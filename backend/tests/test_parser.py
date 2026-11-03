from io import BytesIO

import pymupdf
import pytest
from docx import Document

from resumes.parser import MAX_UPLOAD_BYTES, extract_text
from conftest import RESUME_TEXT


def test_docx_extracts_paragraphs_and_tables(resume_bytes):
    assert "Built Python APIs" in extract_text("resume.docx", resume_bytes)
    document = Document(BytesIO(resume_bytes))
    document.add_table(rows=1, cols=1).cell(0, 0).text = "Docker workshop"
    stream = BytesIO()
    document.save(stream)
    assert "Docker workshop" in extract_text("resume.docx", stream.getvalue())


def test_pdf_extracts_text():
    with pymupdf.open() as document:
        page = document.new_page()
        page.insert_text((50, 50), RESUME_TEXT)
        content = document.tobytes()
    assert "Built Python APIs" in extract_text("resume.pdf", content)


@pytest.mark.parametrize("filename,content", [
    ("resume.exe", b"not a document"), ("resume.pdf", b"not a pdf"),
    ("resume.docx", b"not a zip"), ("resume.pdf", b""),
    ("resume.pdf", b"x" * (MAX_UPLOAD_BYTES + 1)),
])
def test_invalid_uploads_rejected(filename, content):
    with pytest.raises(ValueError):
        extract_text(filename, content)


def test_blank_and_long_pdf_rejected():
    with pymupdf.open() as document:
        document.new_page()
        with pytest.raises(ValueError, match="readable text"):
            extract_text("resume.pdf", document.tobytes())
        for _ in range(10):
            document.new_page()
        with pytest.raises(ValueError, match="10 pages"):
            extract_text("resume.pdf", document.tobytes())
