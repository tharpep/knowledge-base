import pytest

from rag import chunking
from rag.chunking import chunk_conversation, chunk_markdown, chunk_text

WORDS = " ".join(["word"] * 200)


@pytest.mark.parametrize("blank", ["", "   ", "\n\n\t "])
def test_chunk_text_returns_empty_list_for_blank_text(blank):
    assert chunk_text(blank) == []


@pytest.mark.parametrize("blank", ["", "   ", "\n\n\t "])
def test_chunk_markdown_returns_empty_list_for_blank_text(blank):
    assert chunk_markdown(blank) == []


def test_chunk_text_keeps_short_text_as_one_chunk():
    assert chunk_text("hello world", chunk_size=100, overlap=10) == ["hello world"]


def test_chunk_text_splits_long_text_into_chunks_no_longer_than_chunk_size():
    chunks = chunk_text(WORDS, chunk_size=100, overlap=10)

    assert len(chunks) > 1
    assert all(len(c) <= 100 for c in chunks)


def test_chunk_text_loses_no_words_when_splitting():
    chunks = chunk_text(WORDS, chunk_size=100, overlap=0)

    assert sum(len(c.split()) for c in chunks) == 200


def test_chunk_markdown_pairs_chunk_with_h1_h2_h3_section_title():
    text = "# Top\n\n## Middle\n\n### Bottom\n\nbody text"

    assert chunk_markdown(text) == [("body text", "Top > Middle > Bottom")]


def test_chunk_markdown_title_omits_missing_header_levels():
    text = "# Top\n\n### Bottom\n\nbody text"

    assert chunk_markdown(text) == [("body text", "Top > Bottom")]


def test_chunk_markdown_gives_each_section_its_own_title():
    text = "# One\n\nfirst body\n\n# Two\n\nsecond body"

    assert chunk_markdown(text) == [("first body", "One"), ("second body", "Two")]


def test_chunk_markdown_text_without_headers_has_empty_section_title():
    assert chunk_markdown("just a plain paragraph") == [("just a plain paragraph", "")]


def test_chunk_markdown_sub_splits_long_section_and_repeats_title():
    text = f"# Long\n\n{WORDS}"

    result = chunk_markdown(text, chunk_size=100, overlap=10)

    assert len(result) > 1
    assert {title for _, title in result} == {"Long"}
    assert all(len(chunk) <= 100 for chunk, _ in result)


def test_chunk_markdown_chunks_respect_chunk_size_across_sections():
    text = f"# A\n\n{WORDS}\n\n## B\n\n{WORDS}"

    result = chunk_markdown(text, chunk_size=80, overlap=0)

    assert {title for _, title in result} == {"A", "A > B"}
    assert all(len(chunk) <= 80 for chunk, _ in result)


def test_chunk_conversation_uses_1500_chunk_size_and_150_overlap(monkeypatch):
    seen = {}

    def fake_chunk_text(**kwargs):
        seen.update(kwargs)
        return ["x"]

    monkeypatch.setattr(chunking, "chunk_text", fake_chunk_text)

    assert chunk_conversation("hi") == ["x"]
    assert seen["text"] == "hi"
    assert seen["chunk_size"] == 1500
    assert seen["overlap"] == 150


def test_chunk_conversation_chunks_stay_within_1500_characters():
    text = " ".join(["word"] * 1000)

    chunks = chunk_conversation(text)

    assert len(chunks) > 1
    assert all(len(c) <= 1500 for c in chunks)
