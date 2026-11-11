"""rag.retriever: RRF fusion and the retrieve() pipeline, against a fake pool and patched Voyage calls."""

import pytest

from rag import retriever
from rag.retriever import RRF_K, Chunk, _rrf_fuse, retrieve


def chunk(chunk_id, dense_score=0.0, fts_score=0.0):
    return Chunk(
        id=chunk_id, content=f"text {chunk_id}", filename="f.md", drive_file_id="upload:f", chunk_index=0,
        dense_score=dense_score, fts_score=fts_score,
    )  # fmt: skip


def row(chunk_id, score=0.5, category="notes"):
    return {
        "id": chunk_id,
        "content": f"text {chunk_id}",
        "filename": "f.md",
        "drive_file_id": "upload:f",
        "chunk_index": 0,
        "source_category": category,
        "score": score,
    }


def ids(chunks):
    return [c.id for c in chunks]


class TestRrfFuse:
    def test_chunk_in_one_list_scores_reciprocal_of_k_plus_one_based_rank(self):
        result = _rrf_fuse([chunk("a"), chunk("b")], [], limit=10)

        assert result[0].rrf_score == pytest.approx(1 / (RRF_K + 1))
        assert result[1].rrf_score == pytest.approx(1 / (RRF_K + 2))

    def test_chunk_in_both_lists_scores_the_sum_of_both_reciprocals(self):
        dense = [chunk("a"), chunk("b")]
        sparse = [chunk("b"), chunk("c")]

        by_id = {c.id: c for c in _rrf_fuse(dense, sparse, limit=10)}

        assert by_id["a"].rrf_score == pytest.approx(1 / (RRF_K + 1))
        assert by_id["b"].rrf_score == pytest.approx(1 / (RRF_K + 2) + 1 / (RRF_K + 1))
        assert by_id["c"].rrf_score == pytest.approx(1 / (RRF_K + 2))

    def test_results_are_sorted_by_descending_rrf_score(self):
        dense = [chunk("a"), chunk("b")]
        sparse = [chunk("b"), chunk("c")]

        # b = 1/62 + 1/61, a = 1/61, c = 1/62
        assert ids(_rrf_fuse(dense, sparse, limit=10)) == ["b", "a", "c"]

    def test_results_are_cut_to_limit(self):
        dense = [chunk("a"), chunk("b")]
        sparse = [chunk("b"), chunk("c")]

        assert ids(_rrf_fuse(dense, sparse, limit=2)) == ["b", "a"]

    def test_chunk_in_both_lists_keeps_the_sparse_lists_fts_score(self):
        dense = [chunk("b", dense_score=0.9)]
        sparse = [chunk("b", fts_score=0.7)]

        (fused,) = _rrf_fuse(dense, sparse, limit=10)

        assert fused.fts_score == 0.7
        assert fused.dense_score == 0.9

    def test_chunk_only_in_dense_list_keeps_zero_fts_score(self):
        (fused,) = _rrf_fuse([chunk("a", dense_score=0.9)], [chunk("z", fts_score=0.4)], limit=1)

        assert fused.id == "a"
        assert fused.fts_score == 0.0

    def test_empty_inputs_return_empty_list(self):
        assert _rrf_fuse([], [], limit=5) == []


@pytest.fixture
def embed(monkeypatch):
    calls = []

    async def fake_embed_query(text):
        calls.append(text)
        return [0.25, 0.5]

    monkeypatch.setattr(retriever, "embed_query", fake_embed_query)
    return calls


@pytest.fixture
def reranked(monkeypatch):
    """Patches rag.retriever.rerank; `scores` maps chunk id to the rerank_score it assigns."""

    class Recorder:
        def __init__(self):
            self.calls = []
            self.scores = {}

    rec = Recorder()

    async def fake_rerank(query, chunks, top_k):
        rec.calls.append((query, list(chunks), top_k))
        for c in chunks:
            c.rerank_score = rec.scores.get(c.id, 0.0)
        return sorted(chunks, key=lambda c: c.rerank_score, reverse=True)[:top_k]

    monkeypatch.setattr(retriever, "rerank", fake_rerank)
    return rec


@pytest.fixture
def cfg(config, monkeypatch):
    """Config with distinctive, explicit values: hybrid on, rerank off."""
    monkeypatch.setattr(config, "chat_kb_top_k", 3)
    monkeypatch.setattr(config, "rerank_candidates", 7)
    monkeypatch.setattr(config, "chat_kb_similarity_threshold", 0.5)
    monkeypatch.setattr(config, "hnsw_ef_search", 123)
    monkeypatch.setattr(config, "hybrid_sparse_weight", 0.5)
    monkeypatch.setattr(config, "rerank_enabled", False)
    return config


def queue(fake_pool, dense=(), sparse=()):
    fake_pool.conn.responses["fetch"].append(list(dense))
    fake_pool.conn.responses["fetch"].append(list(sparse))


class TestRetrieveDefaults:
    async def test_top_k_defaults_to_config_chat_kb_top_k(self, fake_pool, embed, cfg):
        queue(fake_pool, dense=[row(str(i)) for i in range(5)])

        assert len(await retrieve("q")) == 3

    async def test_explicit_top_k_overrides_config(self, fake_pool, embed, cfg):
        queue(fake_pool, dense=[row(str(i)) for i in range(5)])

        assert len(await retrieve("q", top_k=2)) == 2

    async def test_candidates_default_to_config_rerank_candidates_in_both_queries(self, fake_pool, embed, cfg):
        queue(fake_pool)

        await retrieve("q")

        dense_args, fts_args = (args for method, _, args in fake_pool.conn.calls if method == "fetch")
        assert dense_args[1] == 7
        assert fts_args[1] == 7

    async def test_explicit_candidates_override_config_in_both_queries(self, fake_pool, embed, cfg):
        queue(fake_pool)

        await retrieve("q", candidates=11)

        dense_args, fts_args = (args for method, _, args in fake_pool.conn.calls if method == "fetch")
        assert dense_args[1] == 11
        assert fts_args[1] == 11

    async def test_candidates_cap_dense_results_when_there_are_no_sparse_results(self, fake_pool, embed, cfg):
        queue(fake_pool, dense=[row("a"), row("b"), row("c")])

        assert ids(await retrieve("q", top_k=10, candidates=2)) == ["a", "b"]

    async def test_threshold_defaults_to_config_similarity_threshold(
        self, fake_pool, embed, reranked, cfg, monkeypatch
    ):
        monkeypatch.setattr(cfg, "rerank_enabled", True)
        reranked.scores = {"hi": 0.9, "lo": 0.1}
        queue(fake_pool, dense=[row("hi"), row("lo")])

        assert ids(await retrieve("q")) == ["hi"]

    async def test_explicit_threshold_overrides_config(self, fake_pool, embed, reranked, cfg, monkeypatch):
        monkeypatch.setattr(cfg, "rerank_enabled", True)
        reranked.scores = {"hi": 0.9, "lo": 0.1}
        queue(fake_pool, dense=[row("hi"), row("lo")])

        assert ids(await retrieve("q", threshold=0.05)) == ["hi", "lo"]

    async def test_explicit_zero_threshold_is_not_replaced_by_config_default(
        self, fake_pool, embed, reranked, cfg, monkeypatch
    ):
        monkeypatch.setattr(cfg, "rerank_enabled", True)
        reranked.scores = {"hi": 0.9, "lo": 0.1}
        queue(fake_pool, dense=[row("hi"), row("lo")])

        assert ids(await retrieve("q", threshold=0.0)) == ["hi", "lo"]


class TestRetrieveSearch:
    async def test_query_is_embedded_and_embedding_sent_to_dense_query(self, fake_pool, embed, cfg):
        queue(fake_pool)

        await retrieve("what is x")

        assert embed == ["what is x"]
        method, _, args = fake_pool.conn.calls[2]
        assert method == "fetch"
        assert args[0] == "[0.25,0.5]"

    async def test_fts_query_receives_the_query_text(self, fake_pool, embed, cfg):
        queue(fake_pool)

        await retrieve("what is x")

        fts_args = [args for method, _, args in fake_pool.conn.calls if method == "fetch"][1]
        assert fts_args[0] == "what is x"

    async def test_zero_sparse_weight_issues_no_fts_query(self, fake_pool, embed, cfg, monkeypatch):
        monkeypatch.setattr(cfg, "hybrid_sparse_weight", 0)
        queue(fake_pool, dense=[row("a")])

        await retrieve("q")

        fetches = fake_pool.conn.sql("fetch")
        assert len(fetches) == 1
        assert "plainto_tsquery" not in fetches[0]

    async def test_zero_sparse_weight_passes_dense_results_through_in_order(self, fake_pool, embed, cfg, monkeypatch):
        monkeypatch.setattr(cfg, "hybrid_sparse_weight", 0)
        queue(fake_pool, dense=[row("c"), row("a"), row("b")])

        assert ids(await retrieve("q")) == ["c", "a", "b"]

    async def test_positive_sparse_weight_issues_one_dense_and_one_fts_query(self, fake_pool, embed, cfg):
        queue(fake_pool)

        await retrieve("q")

        fetches = fake_pool.conn.sql("fetch")
        assert len(fetches) == 2
        assert "plainto_tsquery" not in fetches[0]
        assert "plainto_tsquery" in fetches[1]

    async def test_hybrid_results_are_fused_by_rrf(self, fake_pool, embed, cfg):
        queue(fake_pool, dense=[row("a"), row("b")], sparse=[row("b"), row("c")])

        result = await retrieve("q", top_k=10)

        # b = 1/62 + 1/61, a = 1/61, c = 1/62
        assert ids(result) == ["b", "a", "c"]
        assert result[0].rrf_score == pytest.approx(1 / 62 + 1 / 61)

    async def test_hybrid_results_with_empty_fts_keep_dense_order(self, fake_pool, embed, cfg):
        queue(fake_pool, dense=[row("c"), row("a")], sparse=[])

        assert ids(await retrieve("q")) == ["c", "a"]

    async def test_rows_become_chunks_with_selected_columns_and_scores(self, fake_pool, embed, cfg, monkeypatch):
        monkeypatch.setattr(cfg, "hybrid_sparse_weight", 0)
        queue(fake_pool, dense=[row("a", score=0.8, category="notes")])

        (result,) = await retrieve("q")

        assert (result.id, result.content, result.filename, result.drive_file_id) == ("a", "text a", "f.md", "upload:f")
        assert result.source_category == "notes"
        assert result.dense_score == pytest.approx(0.8)

    async def test_categories_reach_both_queries_as_the_third_argument(self, fake_pool, embed, cfg):
        queue(fake_pool)

        await retrieve("q", categories=["notes", "docs"])

        dense_args, fts_args = (args for method, _, args in fake_pool.conn.calls if method == "fetch")
        assert dense_args[2] == ["notes", "docs"]
        assert fts_args[2] == ["notes", "docs"]

    async def test_categories_filter_appears_in_sql_only_when_given(self, fake_pool, embed, cfg):
        queue(fake_pool)
        await retrieve("q", categories=["notes"])
        queue(fake_pool)
        await retrieve("q")

        with_categories, without_categories = fake_pool.conn.sql("fetch")[:2], fake_pool.conn.sql("fetch")[2:]
        assert all("source_category = ANY" in s for s in with_categories)
        assert not any("source_category = ANY" in s for s in without_categories)

    async def test_no_categories_sends_no_category_argument(self, fake_pool, embed, cfg):
        queue(fake_pool)

        await retrieve("q")

        for method, _, args in fake_pool.conn.calls:
            if method == "fetch":
                assert len(args) == 2

    async def test_set_local_hnsw_ef_search_uses_config_value(self, fake_pool, embed, cfg):
        queue(fake_pool)

        await retrieve("q")

        assert "SET LOCAL hnsw.ef_search = 123" in fake_pool.conn.sql("execute")

    async def test_set_local_runs_before_the_dense_query(self, fake_pool, embed, cfg):
        queue(fake_pool)

        await retrieve("q")

        methods = [m for m, _, _ in fake_pool.conn.calls]
        assert methods.index("execute") < methods.index("fetch")


class TestRetrieveRerank:
    async def test_rerank_disabled_cuts_fused_results_to_top_k_without_calling_rerank(
        self, fake_pool, embed, reranked, cfg
    ):
        queue(fake_pool, dense=[row("a"), row("b"), row("c")])

        assert ids(await retrieve("q", top_k=2)) == ["a", "b"]
        assert reranked.calls == []

    async def test_rerank_enabled_calls_rerank_with_query_fused_chunks_and_top_k(
        self, fake_pool, embed, reranked, cfg, monkeypatch
    ):
        monkeypatch.setattr(cfg, "rerank_enabled", True)
        queue(fake_pool, dense=[row("a"), row("b")], sparse=[row("b")])

        await retrieve("my query", top_k=2, threshold=0)

        ((query, chunks, top_k),) = reranked.calls
        assert query == "my query"
        assert ids(chunks) == ["b", "a"]
        assert top_k == 2

    async def test_rerank_enabled_returns_reranked_order(self, fake_pool, embed, reranked, cfg, monkeypatch):
        monkeypatch.setattr(cfg, "rerank_enabled", True)
        reranked.scores = {"a": 0.2, "b": 0.9, "c": 0.6}
        queue(fake_pool, dense=[row("a"), row("b"), row("c")])

        assert ids(await retrieve("q", top_k=2, threshold=0.1)) == ["b", "c"]

    async def test_threshold_keeps_chunks_whose_rerank_score_equals_it(
        self, fake_pool, embed, reranked, cfg, monkeypatch
    ):
        monkeypatch.setattr(cfg, "rerank_enabled", True)
        reranked.scores = {"edge": 0.5, "below": 0.49}
        queue(fake_pool, dense=[row("edge"), row("below")])

        assert ids(await retrieve("q", threshold=0.5)) == ["edge"]

    async def test_threshold_filters_every_chunk_below_it_to_an_empty_list(
        self, fake_pool, embed, reranked, cfg, monkeypatch
    ):
        monkeypatch.setattr(cfg, "rerank_enabled", True)
        reranked.scores = {"a": 0.1, "b": 0.2}
        queue(fake_pool, dense=[row("a"), row("b")])

        assert await retrieve("q", threshold=0.5) == []

    async def test_threshold_does_not_filter_when_rerank_is_disabled(self, fake_pool, embed, reranked, cfg):
        queue(fake_pool, dense=[row("a"), row("b")])

        result = await retrieve("q", threshold=0.9)

        assert ids(result) == ["a", "b"]
        assert all(c.rerank_score == 0.0 for c in result)

    async def test_no_candidates_returns_empty_list_without_calling_rerank(
        self, fake_pool, embed, reranked, cfg, monkeypatch
    ):
        monkeypatch.setattr(cfg, "rerank_enabled", True)
        queue(fake_pool)

        assert await retrieve("q") == []
        assert reranked.calls == []

    async def test_no_candidates_with_rerank_disabled_returns_empty_list(self, fake_pool, embed, reranked, cfg):
        queue(fake_pool)

        assert await retrieve("q") == []
