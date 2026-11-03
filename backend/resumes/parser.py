"""Bounded, in-memory text extraction. Uploaded originals are never persisted."""
from io import BytesIO
from pathlib import PurePosixPath
from zipfile import ZipFile

import pymupdf
from docx import Document

MAX_UPLOAD_BYTES = 5 * 1024 * 1024
MAX_TEXT_CHARS = 18000
MAX_PAGES = 10


def extract_text(filename: str, content: bytes) -> str:
    if not content or len(content) > MAX_UPLOAD_BYTES:
        raise ValueError("Upload a non-empty PDF or DOCX up to 5 MB.")
    extension = PurePosixPath(filename).suffix.lower()
    try:
        if extension == ".pdf":
            if not content.startswith(b"%PDF-"):
                raise ValueError("The file is not a valid PDF.")
            with pymupdf.open(stream=content, filetype="pdf") as document:
                if document.needs_pass:
                    raise ValueError("Remove the PDF password before uploading.")
                if document.page_count > MAX_PAGES:
                    raise ValueError("Use a resume with no more than 10 pages.")
                parts = []
                for page in document:
                    parts.append(page.get_text(sort=True))
                    if sum(map(len, parts)) > MAX_TEXT_CHARS:
                        raise ValueError("Resume text exceeds 18,000 characters.")
                text = "\n".join(parts)
        elif extension == ".docx":
            with ZipFile(BytesIO(content)) as archive:
                if len(archive.infolist()) > 1000 or sum(
                    item.file_size for item in archive.infolist()
                ) > 20 * 1024 * 1024:
                    raise ValueError("The DOCX expands beyond the supported size.")
                if "word/document.xml" not in archive.namelist():
                    raise ValueError("The file is not a valid DOCX.")
            document = Document(BytesIO(content))
            parts = [paragraph.text for paragraph in document.paragraphs]
            for table in document.tables:
                parts.extend(" | ".join(cell.text for cell in row.cells) for row in table.rows)
            text = "\n".join(parts)
        else:
            raise ValueError("Only PDF and DOCX files are supported.")
    except ValueError:
        raise
    except Exception as exc:
        raise ValueError("Could not read this file. Export a fresh PDF or DOCX.") from exc
    text = text.replace("\x00", "").strip()
    if len(text) < 80:
        raise ValueError("Not enough readable text. Scanned PDFs need OCR; upload a text-based PDF or DOCX.")
    if len(text) > MAX_TEXT_CHARS:
        raise ValueError("Resume text exceeds 18,000 characters.")
    return text
