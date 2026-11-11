import io

import openpyxl
import pytest
from docx import Document

from rag.loader import parse_content

XLSX_MIME = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


def _docx_bytes(paragraphs):
    doc = Document()
    for p in paragraphs:
        doc.add_paragraph(p)
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


def _xlsx_bytes(sheets):
    wb = openpyxl.Workbook()
    wb.remove(wb.active)
    for name, rows in sheets.items():
        ws = wb.create_sheet(name)
        for row in rows:
            ws.append(row)
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


@pytest.mark.parametrize("mime", ["text/plain", "text/markdown", "text/csv"])
def test_parse_content_decodes_text_by_mime(mime):
    assert parse_content("héllo".encode(), mime, "blob") == "héllo"


@pytest.mark.parametrize("filename", ["a.txt", "a.md", "a.markdown", "a.csv", "A.TXT"])
def test_parse_content_decodes_text_by_extension_when_mime_is_generic(filename):
    assert parse_content(b"plain body", "application/octet-stream", filename) == "plain body"


def test_parse_content_returns_csv_text_unchanged():
    assert parse_content(b"a,b\n1,2\n", "text/csv", "data.csv") == "a,b\n1,2\n"


def test_parse_content_returns_markdown_text_unchanged():
    assert parse_content(b"# Title\n\nbody", "text/markdown", "n.md") == "# Title\n\nbody"


def test_parse_content_joins_docx_paragraphs_with_blank_lines():
    data = _docx_bytes(["first", "second"])

    assert parse_content(data, DOCX_MIME, "d.docx") == "first\n\nsecond"


def test_parse_content_docx_detected_by_extension():
    data = _docx_bytes(["only"])

    assert parse_content(data, "application/octet-stream", "d.docx") == "only"


def test_parse_content_docx_skips_blank_paragraphs():
    data = _docx_bytes(["first", "   ", "", "second"])

    assert parse_content(data, DOCX_MIME, "d.docx") == "first\n\nsecond"


def test_parse_content_xlsx_heads_sheet_with_equals_name_and_tab_joins_cells():
    data = _xlsx_bytes({"Sales": [["a", "b"], [1, 2]]})

    assert parse_content(data, XLSX_MIME, "s.xlsx") == "=== Sales ===\na\tb\n1\t2"


def test_parse_content_xlsx_detected_by_extension():
    data = _xlsx_bytes({"S": [["x"]]})

    assert parse_content(data, "application/octet-stream", "s.xlsx") == "=== S ===\nx"


def test_parse_content_xlsx_skips_empty_rows():
    data = _xlsx_bytes({"S": [["a"], [None, None], ["b"]]})

    assert parse_content(data, XLSX_MIME, "s.xlsx") == "=== S ===\na\nb"


def test_parse_content_xlsx_renders_empty_cell_in_a_row_as_empty_string():
    data = _xlsx_bytes({"S": [["a", None, "c"]]})

    assert parse_content(data, XLSX_MIME, "s.xlsx") == "=== S ===\na\t\tc"


def test_parse_content_xlsx_separates_sheets_with_blank_line():
    data = _xlsx_bytes({"One": [["a"]], "Two": [["b"]]})

    assert parse_content(data, XLSX_MIME, "s.xlsx") == "=== One ===\na\n\n=== Two ===\nb"


def test_parse_content_xlsx_omits_sheet_with_no_rows():
    data = _xlsx_bytes({"Empty": [], "Full": [["a"]]})

    assert parse_content(data, XLSX_MIME, "s.xlsx") == "=== Full ===\na"


def test_parse_content_unknown_type_decodes_utf8():
    assert parse_content("héllo".encode(), "application/x-weird", "file.bin") == "héllo"


def test_parse_content_unknown_type_replaces_invalid_utf8_bytes():
    assert parse_content(b"ok\xffend", "application/x-weird", "file.bin") == "ok�end"
