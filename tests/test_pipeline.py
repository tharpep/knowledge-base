"""Tests for rag.pipeline: contextualization, summary fallback, and the ingest_document flow."""

import json

import pytest

from rag import pipeline
from rag.pipeline import (
    SUMMARY_UNAVAILABLE,
    EmptyContentError,
    contextualize_chunk,
    generate_summary,
    ingest_document,
)


def returning(value):
    def fake(*_args, **_kwargs):
        return value

    return fake


def forbidden(message):
    def fake(*_args, **_kwargs):
        pytest.fail(message)

    return fake


class FakeGateway:
    summary = "A short summary."

    def chat(self, prompt):
        return self.summary


class RaisingGateway:
    def chat(self, prompt):
        msg = "gateway down"
        raise RuntimeError(msg)


@pytest.fixture
def embed_calls(monkeypatch):
    """Batches passed to embed_documents; each chunk gets the one-dimensional embedding [1.0]."""
    calls: list[list[str]] = []

    async def fake_embed(batch):
        calls.append(list(batch))
        return [[1.0] for _ in batch]

    monkeypatch.setattr(pipeline, "embed_documents", fake_embed)
    return calls


@pytest.fixture(autouse=True)
def gateway(monkeypatch):
    monkeypatch.setattr(pipeline, "AIGateway", FakeGateway)


@pytest.fixture
def txn_log(fake_pool):
    """Wrap conn.transaction so entering and leaving it are recorded in conn.calls."""
    conn = fake_pool.conn

    class Recorder:
        async def __aenter__(self):
            conn.calls.append(("txn", "enter", ()))

        async def __aexit__(self, *exc):
            conn.calls.append(("txn", "exit", ()))
            return False

    conn.transaction = Recorder
    return conn


def test_contextualize_chunk_with_summary_and_section_orders_parts():
    result = contextualize_chunk("body", "notes.md", "About cats", "Intro")
    assert result == "From 'notes.md' (About cats) [Intro]: body"


def test_contextualize_chunk_without_section_omits_brackets():
    assert contextualize_chunk("body", "notes.txt", "About cats") == "From 'notes.txt' (About cats): body"


def test_contextualize_chunk_with_unavailable_summary_omits_parentheses():
    result = contextualize_chunk("body", "notes.md", SUMMARY_UNAVAILABLE, "Intro")
    assert result == "From 'notes.md' [Intro]: body"


def test_contextualize_chunk_with_unavailable_summary_and_no_section_is_filename_only():
    assert contextualize_chunk("body", "a.txt", SUMMARY_UNAVAILABLE) == "From 'a.txt': body"


def test_generate_summary_returns_gateway_reply():
    assert generate_summary("some text", FakeGateway()) == "A short summary."


def test_generate_summary_returns_unavailable_marker_when_gateway_raises():
    assert generate_summary("some text", RaisingGateway()) == SUMMARY_UNAVAILABLE


@pytest.mark.parametrize("content", ["", "   ", "\n\t \n"])
async def test_ingest_document_raises_empty_content_error_for_blank_content(fake_pool, embed_calls, content):
    with pytest.raises(EmptyContentError):
        await ingest_document("upload:1", "a.txt", None, content, "upload")
    assert fake_pool.conn.calls == []
    assert embed_calls == []


async def test_ingest_document_markdown_stores_section_title_in_metadata(fake_pool, embed_calls, monkeypatch):
    monkeypatch.setattr(pipeline, "chunk_markdown", returning([("alpha", "Intro"), ("beta", "Intro > Setup")]))
    monkeypatch.setattr(pipeline, "chunk_text", forbidden("chunk_text used for markdown"))

    await ingest_document("upload:1", "guide.md", "docs", "# Intro\nalpha", "upload")

    (rows,) = [args[0] for method, _, args in fake_pool.conn.calls if method == "executemany"]
    assert [json.loads(row[6]) for row in rows] == [{"section_title": "Intro"}, {"section_title": "Intro > Setup"}]


async def test_ingest_document_dot_markdown_extension_uses_markdown_chunker(fake_pool, embed_calls, monkeypatch):
    monkeypatch.setattr(pipeline, "chunk_markdown", returning([("alpha", "Intro")]))
    monkeypatch.setattr(pipeline, "chunk_text", forbidden("chunk_text used for markdown"))

    await ingest_document("upload:1", "guide.markdown", None, "# Intro\nalpha", "upload")

    (rows,) = [args[0] for method, _, args in fake_pool.conn.calls if method == "executemany"]
    assert json.loads(rows[0][6]) == {"section_title": "Intro"}


async def test_ingest_document_non_markdown_uses_text_chunker_with_empty_metadata(fake_pool, embed_calls, monkeypatch):
    monkeypatch.setattr(pipeline, "chunk_text", returning(["one", "two"]))
    monkeypatch.setattr(pipeline, "chunk_markdown", forbidden("chunk_markdown used for txt"))

    await ingest_document("upload:1", "notes.txt", None, "one two", "upload")

    (rows,) = [args[0] for method, _, args in fake_pool.conn.calls if method == "executemany"]
    assert [json.loads(row[6]) for row in rows] == [{}, {}]


async def test_ingest_document_stores_contextualized_chunks_in_markdown_path(fake_pool, embed_calls, monkeypatch):
    monkeypatch.setattr(pipeline, "chunk_markdown", returning([("alpha", "Intro"), ("beta", "Setup")]))

    await ingest_document("upload:1", "guide.md", None, "# Intro\nalpha", "upload")

    (rows,) = [args[0] for method, _, args in fake_pool.conn.calls if method == "executemany"]
    assert [row[0] for row in rows] == [
        "From 'guide.md' (A short summary.) [Intro]: alpha",
        "From 'guide.md' (A short summary.) [Setup]: beta",
    ]
    assert embed_calls == [[row[0] for row in rows]]


async def test_ingest_document_stores_contextualized_chunks_in_text_path(fake_pool, embed_calls, monkeypatch):
    monkeypatch.setattr(pipeline, "chunk_text", returning(["one", "two"]))

    await ingest_document("upload:1", "notes.txt", None, "one two", "upload")

    (rows,) = [args[0] for method, _, args in fake_pool.conn.calls if method == "executemany"]
    assert [row[0] for row in rows] == [
        "From 'notes.txt' (A short summary.): one",
        "From 'notes.txt' (A short summary.): two",
    ]


async def test_ingest_document_stores_chunks_without_summary_part_when_summary_unavailable(
    fake_pool, embed_calls, monkeypatch
):
    monkeypatch.setattr(pipeline, "AIGateway", RaisingGateway)
    monkeypatch.setattr(pipeline, "chunk_text", returning(["one"]))

    result = await ingest_document("upload:1", "notes.txt", None, "one", "upload")

    (rows,) = [args[0] for method, _, args in fake_pool.conn.calls if method == "executemany"]
    assert rows[0][0] == "From 'notes.txt': one"
    assert result["summary"] == SUMMARY_UNAVAILABLE


async def test_ingest_document_embeds_200_chunks_in_batches_of_96_96_and_8(fake_pool, embed_calls, monkeypatch):
    monkeypatch.setattr(pipeline, "chunk_text", returning([f"c{i}" for i in range(200)]))

    result = await ingest_document("upload:1", "notes.txt", None, "x", "upload")

    assert [len(batch) for batch in embed_calls] == [96, 96, 8]
    embedded = [c for batch in embed_calls for c in batch]
    assert embedded == [f"From 'notes.txt' (A short summary.): c{i}" for i in range(200)]
    assert result["chunk_count"] == 200


async def test_ingest_document_deletes_existing_chunks_then_inserts_in_one_transaction(
    txn_log, embed_calls, monkeypatch
):
    monkeypatch.setattr(pipeline, "chunk_text", returning(["one", "two"]))

    await ingest_document("upload:42", "notes.txt", None, "one two", "upload")

    steps = [(method, sql.strip().split()[0]) for method, sql, _ in txn_log.calls]
    assert steps[:5] == [
        ("txn", "enter"),
        ("execute", "DELETE"),
        ("executemany", "INSERT"),
        ("txn", "exit"),
        ("execute", "INSERT"),
    ]
    delete = txn_log.calls[1]
    assert "kb_chunks" in delete[1]
    assert delete[2] == ("upload:42",)
    assert [method for method, _, _ in txn_log.calls].count("txn") == 2


async def test_ingest_document_upserts_kb_source_with_count_summary_content_and_origin(
    fake_pool, embed_calls, monkeypatch
):
    monkeypatch.setattr(pipeline, "chunk_text", returning(["one", "two", "three"]))

    await ingest_document("text:abc", "pasted.txt", "notes", "the raw content", "text")

    (upsert,) = [args for method, sql, args in fake_pool.conn.calls if method == "execute" and "kb_sources" in sql]
    assert upsert == ("text:abc", "pasted.txt", "notes", 3, "A short summary.", "the raw content", "text")


async def test_ingest_document_returns_chunk_count_and_summary(fake_pool, embed_calls, monkeypatch):
    monkeypatch.setattr(pipeline, "chunk_text", returning(["one", "two"]))

    result = await ingest_document("url:9", "page.txt", "web", "one two", "url")

    assert result == {
        "file_id": "url:9",
        "filename": "page.txt",
        "category": "web",
        "origin": "url",
        "chunk_count": 2,
        "summary": "A short summary.",
    }


async def test_ingest_document_raises_when_chunker_produces_no_chunks(fake_pool, embed_calls, monkeypatch):
    monkeypatch.setattr(pipeline, "chunk_text", returning([]))

    with pytest.raises(EmptyContentError):
        await ingest_document("upload:1", "notes.txt", None, "some text", "upload")
    assert fake_pool.conn.calls == []
