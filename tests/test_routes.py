"""HTTP route contracts: auth, search, ingest, delete, read and export."""

import hashlib

import httpx
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.routes.ingest import MAX_UPLOAD_BYTES
from rag.pipeline import EmptyContentError
from rag.query_processor import QueryProcessor
from rag.retriever import Chunk


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def ingested(monkeypatch):
    """Replaces ingest_document; `calls` records each call's arguments."""
    calls = []

    async def fake(file_id, filename, category, content, origin):
        calls.append(
            {"file_id": file_id, "filename": filename, "category": category, "content": content, "origin": origin}
        )
        return {
            "file_id": file_id,
            "filename": filename,
            "category": category,
            "origin": origin,
            "chunk_count": 2,
            "summary": "a summary",
        }

    monkeypatch.setattr("app.routes.ingest.ingest_document", fake)
    return calls


def _ingest_raises(monkeypatch, error):
    async def fake(*args, **kwargs):
        raise error

    monkeypatch.setattr("app.routes.ingest.ingest_document", fake)


def _upload(client, name, data=b"hello", **form):
    return client.post("/v1/kb/ingest/file", files={"file": (name, data, "text/plain")}, data=form)


# --- auth -------------------------------------------------------------------------------------


def test_v1_route_without_key_answers_401_when_api_key_is_set(client, config, fake_pool, monkeypatch):
    monkeypatch.setattr(config, "api_key", "secret")
    assert client.get("/v1/kb/files").status_code == 401


def test_v1_route_with_wrong_key_answers_401(client, config, fake_pool, monkeypatch):
    monkeypatch.setattr(config, "api_key", "secret")
    assert client.get("/v1/kb/files", headers={"X-API-Key": "nope"}).status_code == 401


def test_v1_route_accepts_x_api_key_header(client, config, fake_pool, monkeypatch):
    monkeypatch.setattr(config, "api_key", "secret")
    assert client.get("/v1/kb/files", headers={"X-API-Key": "secret"}).status_code == 200


def test_v1_route_accepts_bearer_token(client, config, fake_pool, monkeypatch):
    monkeypatch.setattr(config, "api_key", "secret")
    assert client.get("/v1/kb/files", headers={"Authorization": "Bearer secret"}).status_code == 200


def test_v1_route_is_open_when_api_key_is_empty(client, config, fake_pool, monkeypatch):
    monkeypatch.setattr(config, "api_key", "")
    assert client.get("/v1/kb/files").status_code == 200


# --- POST /v1/kb/search -----------------------------------------------------------------------


def _chunk(**over):
    fields = {
        "id": "c1",
        "content": "alpha text",
        "filename": "a.md",
        "drive_file_id": "upload:a",
        "chunk_index": 3,
        "source_category": "notes",
        "dense_score": 0.5,
        "rrf_score": 0.25,
        "rerank_score": 0.75,
    }
    fields.update(over)
    return Chunk(**fields)


@pytest.fixture
def retrieved(monkeypatch):
    """Replaces retrieve; `chunks` is what it returns, `calls` the kwargs it received."""
    state = {"chunks": [], "calls": []}

    async def fake(**kwargs):
        state["calls"].append(kwargs)
        return state["chunks"]

    monkeypatch.setattr("app.routes.query.retrieve", fake)
    return state


@pytest.mark.parametrize("query", ["", "   ", "\n\t"])
def test_search_blank_query_answers_400(client, retrieved, query):
    assert client.post("/v1/kb/search", json={"query": query}).status_code == 400
    assert retrieved["calls"] == []


def test_search_maps_chunks_to_results_and_count(client, retrieved):
    retrieved["chunks"] = [_chunk(), _chunk(id="c2", content="beta text", chunk_index=4, rerank_score=0.5)]

    body = client.post("/v1/kb/search", json={"query": "alpha"}).json()

    assert body["count"] == 2
    assert body["results"][0] == {
        "content": "alpha text",
        "filename": "a.md",
        "drive_file_id": "upload:a",
        "chunk_index": 3,
        "source_category": "notes",
        "rerank_score": 0.75,
        "dense_score": 0.5,
        "rrf_score": 0.25,
    }
    assert body["results"][1]["content"] == "beta text"
    assert body["results"][1]["chunk_index"] == 4


def test_search_without_results_answers_count_zero(client, retrieved):
    body = client.post("/v1/kb/search", json={"query": "alpha"}).json()

    assert body["results"] == []
    assert body["count"] == 0


def test_search_without_expansion_has_no_expanded_query(client, retrieved):
    body = client.post("/v1/kb/search", json={"query": "  alpha  "}).json()

    assert retrieved["calls"][0]["query"] == "alpha"
    assert body["query"] == "  alpha  "
    assert body["expanded_query"] is None


def test_search_with_expansion_retrieves_expanded_query_and_echoes_original(client, retrieved, monkeypatch):
    seen = []

    def fake_expand(self, query, model=None):
        seen.append(query)
        return "alpha beta gamma"

    monkeypatch.setattr(QueryProcessor, "expand", fake_expand)

    body = client.post("/v1/kb/search", json={"query": "alpha", "expand_query": True}).json()

    assert seen == ["alpha"]
    assert retrieved["calls"][0]["query"] == "alpha beta gamma"
    assert body["query"] == "alpha"
    assert body["expanded_query"] == "alpha beta gamma"


# --- POST /v1/kb/ingest/file ------------------------------------------------------------------


@pytest.mark.parametrize("name", ["tool.exe", "image.png", "archive.zip", "noextension"])
def test_ingest_file_rejects_other_extensions_with_415(client, ingested, name):
    assert _upload(client, name).status_code == 415
    assert ingested == []


@pytest.mark.parametrize("name", ["a.pdf", "a.docx", "a.md", "a.markdown", "a.txt", "a.csv", "A.TXT"])
def test_ingest_file_accepts_allowed_extensions(client, ingested, name):
    assert _upload(client, name).status_code == 201


def test_ingest_file_rejects_body_over_max_upload_bytes_with_413(client, ingested):
    assert _upload(client, "big.txt", b"a" * (MAX_UPLOAD_BYTES + 1)).status_code == 413
    assert ingested == []


def test_ingest_file_accepts_body_of_exactly_max_upload_bytes(client, ingested):
    assert _upload(client, "big.txt", b"a" * MAX_UPLOAD_BYTES).status_code == 201


def test_ingest_file_maps_names_differing_only_in_case_to_one_file_id(client, ingested):
    _upload(client, "Notes.MD")
    _upload(client, "notes.md")

    expected = "upload:" + hashlib.sha256(b"notes.md").hexdigest()[:32]
    assert [c["file_id"] for c in ingested] == [expected, expected]


def test_ingest_file_passes_decoded_text_category_and_origin(client, ingested):
    response = _upload(client, "Notes.MD", "héllo".encode(), category="journal")

    assert response.status_code == 201
    assert ingested[0]["filename"] == "Notes.MD"
    assert ingested[0]["content"] == "héllo"
    assert ingested[0]["category"] == "journal"
    assert ingested[0]["origin"] == "upload"
    assert response.json()["chunk_count"] == 2


def test_ingest_file_empty_content_answers_422(client, monkeypatch):
    _ingest_raises(monkeypatch, EmptyContentError("no text"))

    response = _upload(client, "empty.txt", b"")

    assert response.status_code == 422
    assert "no text" in response.json()["detail"]


# --- POST /v1/kb/ingest/text ------------------------------------------------------------------


def test_ingest_text_with_source_id_uses_text_prefixed_file_id(client, ingested):
    response = client.post("/v1/kb/ingest/text", json={"title": "T", "content": "body", "source_id": "journal-2026-10"})

    assert response.status_code == 201
    assert response.json()["file_id"] == "text:journal-2026-10"
    assert ingested[0]["file_id"] == "text:journal-2026-10"


def test_ingest_text_without_source_id_generates_distinct_text_file_ids(client, ingested):
    client.post("/v1/kb/ingest/text", json={"title": "T", "content": "body"})
    client.post("/v1/kb/ingest/text", json={"title": "T", "content": "body"})

    first, second = (c["file_id"] for c in ingested)
    assert first.startswith("text:")
    assert second.startswith("text:")
    assert first != second


def test_ingest_text_passes_title_content_category_and_origin(client, ingested):
    client.post("/v1/kb/ingest/text", json={"title": "My title", "content": "body", "category": "ideas"})

    assert ingested[0]["filename"] == "My title"
    assert ingested[0]["content"] == "body"
    assert ingested[0]["category"] == "ideas"
    assert ingested[0]["origin"] == "text"


@pytest.mark.parametrize("source_id", ["a/b", "-lead", "has space", ""])
def test_ingest_text_rejects_source_id_that_is_not_a_url_safe_id(client, ingested, source_id):
    response = client.post("/v1/kb/ingest/text", json={"title": "T", "content": "body", "source_id": source_id})

    assert response.status_code == 422
    assert ingested == []


def test_ingest_text_empty_content_error_becomes_422(client, monkeypatch):
    _ingest_raises(monkeypatch, EmptyContentError("nothing to embed"))

    response = client.post("/v1/kb/ingest/text", json={"title": "T", "content": " "})

    assert response.status_code == 422
    assert response.json()["detail"] == "nothing to embed"


def test_ingest_text_other_pipeline_error_becomes_500(client, monkeypatch):
    _ingest_raises(monkeypatch, RuntimeError("boom"))

    assert client.post("/v1/kb/ingest/text", json={"title": "T", "content": "body"}).status_code == 500


# --- POST /v1/kb/ingest/url -------------------------------------------------------------------


class _FakeResponse:
    def __init__(self, status_code, payload=None, text=""):
        self.status_code = status_code
        self._payload = payload
        self.text = text

    def json(self):
        return self._payload


@pytest.fixture
def gateway_reply(monkeypatch):
    """Patches httpx.AsyncClient; set `reply["response"]`, read the request from `reply["posts"]`."""
    reply = {"response": None, "posts": []}

    class FakeAsyncClient:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *exc):
            return False

        async def post(self, url, json=None, headers=None):
            reply["posts"].append({"url": url, "json": json})
            return reply["response"]

    monkeypatch.setattr(httpx, "AsyncClient", FakeAsyncClient)
    return reply


def test_ingest_url_non_200_gateway_reply_answers_502(client, ingested, gateway_reply):
    gateway_reply["response"] = _FakeResponse(500, text="upstream down")

    response = client.post("/v1/kb/ingest/url", json={"url": "https://example.com/a"})

    assert response.status_code == 502
    assert "upstream down" in response.json()["detail"]
    assert ingested == []


@pytest.mark.parametrize(
    "payload",
    [{}, {"results": []}, {"results": [{}]}, {"results": [{"raw_content": ""}]}],
)
def test_ingest_url_with_nothing_extracted_answers_422(client, ingested, gateway_reply, payload):
    gateway_reply["response"] = _FakeResponse(200, payload)

    response = client.post("/v1/kb/ingest/url", json={"url": "https://example.com/a"})

    assert response.status_code == 422
    assert ingested == []


def test_ingest_url_ingests_extracted_text_under_url_hash_file_id(client, ingested, gateway_reply):
    url = "https://example.com/a"
    gateway_reply["response"] = _FakeResponse(200, {"results": [{"raw_content": "page text"}]})

    response = client.post("/v1/kb/ingest/url", json={"url": url, "category": "web"})

    assert response.status_code == 201
    assert gateway_reply["posts"][0]["url"].endswith("/search/web/fetch")
    assert gateway_reply["posts"][0]["json"] == {"url": url}
    assert ingested[0] == {
        "file_id": "url:" + hashlib.sha256(url.encode()).hexdigest(),
        "filename": url,
        "category": "web",
        "content": "page text",
        "origin": "url",
    }


# --- DELETE /v1/kb/files/{id} -----------------------------------------------------------------


def test_delete_file_answers_404_when_both_deletes_report_zero_rows(client, fake_pool):
    fake_pool.conn.responses["execute"].extend(["DELETE 0", "DELETE 0"])

    assert client.delete("/v1/kb/files/upload:missing").status_code == 404


@pytest.mark.parametrize("deleted", [("DELETE 4", "DELETE 1"), ("DELETE 0", "DELETE 1"), ("DELETE 3", "DELETE 0")])
def test_delete_file_answers_204_when_either_delete_removed_rows(client, fake_pool, deleted):
    fake_pool.conn.responses["execute"].extend(deleted)

    assert client.delete("/v1/kb/files/upload:abc").status_code == 204


def test_delete_file_deletes_chunks_and_source_row_by_id(client, fake_pool):
    fake_pool.conn.responses["execute"].extend(["DELETE 2", "DELETE 1"])

    client.delete("/v1/kb/files/upload:abc")

    calls = [(sql, args) for method, sql, args in fake_pool.conn.calls if method == "execute"]
    assert "kb_chunks" in calls[0][0]
    assert "kb_sources" in calls[1][0]
    assert calls[0][1] == ("upload:abc",)
    assert calls[1][1] == ("upload:abc",)


# --- GET /v1/kb/sources/{id}/content and /export ----------------------------------------------


def test_source_content_answers_404_for_missing_source(client, fake_pool):
    assert client.get("/v1/kb/sources/text:nope/content").status_code == 404


def test_source_content_returns_metadata_and_raw_text(client, fake_pool):
    fake_pool.conn.responses["fetchrow"].append(
        {"file_id": "text:a", "filename": "A", "category": "notes", "origin": "text", "raw_content": "full text"}
    )

    assert client.get("/v1/kb/sources/text:a/content").json() == {
        "file_id": "text:a",
        "filename": "A",
        "category": "notes",
        "origin": "text",
        "content": "full text",
    }


def test_source_content_null_raw_text_becomes_empty_string(client, fake_pool):
    fake_pool.conn.responses["fetchrow"].append(
        {"file_id": "text:a", "filename": "A", "category": None, "origin": "text", "raw_content": None}
    )

    assert client.get("/v1/kb/sources/text:a/content").json()["content"] == ""


def test_source_export_answers_404_for_missing_source(client, fake_pool):
    assert client.get("/v1/kb/sources/text:nope/export").status_code == 404


def _export(client, fake_pool, filename, raw="body text", **params):
    fake_pool.conn.responses["fetchrow"].append({"filename": filename, "raw_content": raw})
    return client.get("/v1/kb/sources/text:a/export", params=params)


def test_source_export_defaults_to_markdown(client, fake_pool):
    response = _export(client, fake_pool, "Notes")

    assert response.headers["content-type"] == "text/markdown; charset=utf-8"
    assert response.headers["content-disposition"] == 'attachment; filename="Notes.md"'
    assert response.text == "body text"


def test_source_export_txt_format_is_plain_text(client, fake_pool):
    response = _export(client, fake_pool, "Notes", format="txt")

    assert response.headers["content-type"] == "text/plain; charset=utf-8"
    assert response.headers["content-disposition"] == 'attachment; filename="Notes.txt"'


def test_source_export_replaces_unsafe_runs_with_one_underscore(client, fake_pool):
    response = _export(client, fake_pool, "https://example.com/a b?x=1")

    assert response.headers["content-disposition"] == 'attachment; filename="a_b_x_1.md"'


def test_source_export_strips_edge_dots_and_underscores(client, fake_pool):
    response = _export(client, fake_pool, '"final"')

    assert response.headers["content-disposition"] == 'attachment; filename="final.md"'


def test_source_export_drops_the_original_extension(client, fake_pool):
    response = _export(client, fake_pool, "report.pdf")

    assert response.headers["content-disposition"] == 'attachment; filename="report.md"'


def test_source_export_falls_back_to_source_when_nothing_safe_remains(client, fake_pool):
    response = _export(client, fake_pool, "???")

    assert response.headers["content-disposition"] == 'attachment; filename="source.md"'


def test_source_export_truncates_stem_to_100_characters(client, fake_pool):
    response = _export(client, fake_pool, "a" * 150)

    assert response.headers["content-disposition"] == f'attachment; filename="{"a" * 100}.md"'


def test_source_export_null_raw_text_is_empty_body(client, fake_pool):
    assert _export(client, fake_pool, "Notes", raw=None).text == ""
