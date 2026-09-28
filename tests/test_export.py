"""Tests for export_utils module (TXT, DOCX, and PDF generators)."""

import io
from docx import Document
from ai_core.export_utils import (
    export_to_txt,
    export_to_docx,
    export_to_pdf,
    APP_NAME,
    DISCLAIMER_TEXT,
)

SAMPLE_DOCUMENT = (
    "MUTUAL CONFIDENTIALITY AND NON-DISCLOSURE AGREEMENT\n\n"
    "This Mutual Confidentiality Agreement (the \"Agreement\") is entered into as of October 1, 2026.\n\n"
    "1. DEFINITIONS\n"
    "1.1 \"Confidential Information\" means any proprietary information disclosed by either party.\n\n"
    "2. OBLIGATIONS OF RECEIVING PARTY\n"
    "The Receiving Party agrees to use reasonable care [INSERT DEGREE OF CARE] to maintain confidentiality.\n\n"
    "3. TERM AND TERMINATION\n"
    "This Agreement will expire two (2) years from the Effective Date.\n\n"
    "4. GOVERNING LAW\n"
    "This Agreement shall be governed by the laws of [INSERT GOVERNING STATE].\n\n"
    "SIGNATURES\n"
    "PARTY A:\n"
    "By: _______________________\n"
    "Name: [INSERT NAME]\n"
    "Date: [INSERT DATE]\n\n"
    "PARTY B:\n"
    "By: _______________________\n"
    "Name: [INSERT NAME]\n"
    "Date: [INSERT DATE]\n"
)


def test_export_to_txt():
    """Verify plain text buffer generation, headers, and encoding."""
    buffer = export_to_txt(SAMPLE_DOCUMENT)
    assert isinstance(buffer, io.BytesIO)
    content = buffer.getvalue().decode("utf-8")
    assert APP_NAME in content
    assert DISCLAIMER_TEXT in content
    assert "MUTUAL CONFIDENTIALITY" in content
    assert "SIGNATURES" in content


def test_export_to_docx():
    """Verify DOCX generation, Times New Roman font, and table creation."""
    buffer = export_to_docx(SAMPLE_DOCUMENT, document_title="NDA")
    assert isinstance(buffer, io.BytesIO)
    doc = Document(buffer)

    # Verify paragraphs exist
    assert len(doc.paragraphs) > 5

    # Verify header and footer content
    section = doc.sections[0]
    header_text = section.header.paragraphs[0].text
    footer_text = section.footer.paragraphs[0].text
    assert APP_NAME in header_text
    assert "Draft" in header_text
    assert APP_NAME in footer_text
    assert "Not legal advice" in footer_text

    # Verify table for signatures
    assert len(doc.tables) >= 1
    table = doc.tables[0]
    assert len(table.columns) == 2


def test_export_to_pdf():
    """Verify PDF export produces valid PDF binary structure."""
    buffer = export_to_pdf(SAMPLE_DOCUMENT, document_title="NDA")
    assert isinstance(buffer, io.BytesIO)
    pdf_bytes = buffer.getvalue()

    # Valid PDF starts with %PDF-
    assert pdf_bytes.startswith(b"%PDF-")
    assert len(pdf_bytes) > 2000  # Non-trivial size
