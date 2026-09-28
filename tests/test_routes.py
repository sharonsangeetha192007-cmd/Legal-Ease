"""Tests for LegalEase API route validation, document generation, and export endpoints."""

from unittest.mock import patch
import pytest
from fastapi.testclient import TestClient
from legalEaseAPI.main import app

client = TestClient(app)


def test_generate_document_success():
    """Verify successful generation when Gemini returns valid content."""
    mock_doc = (
        "MUTUAL NON-DISCLOSURE AGREEMENT\n\n"
        "This Agreement is entered into as of October 1, 2026.\n\n"
        "1. DEFINITIONS\n"
        "1.1 Confidential Information means all proprietary technical information.\n\n"
        "2. OBLIGATIONS\n"
        "Receiving party shall protect confidential information.\n\n"
        "SIGNATURES\n"
        "PARTY A: __________________\n"
        "PARTY B: __________________\n"
    )

    with patch("legalEaseAPI.routes.GeminiDocumentGenerator.generate_document", return_value=mock_doc):
        response = client.post(
            "/api/generate",
            json={
                "document_type": "Non-Disclosure Agreement",
                "parties": "Acme Inc. and Cyber Dyne LLC",
                "terms": "Strict confidentiality for 2 years. Standard exclusions.",
                "dates": "October 1, 2026",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "MUTUAL NON-DISCLOSURE AGREEMENT" in data["document"]
        assert data["document_type"] == "Non-Disclosure Agreement"
        assert "disclaimer" in data


def test_generate_missing_required_fields():
    """Verify validation error when required fields are missing."""
    response = client.post(
        "/api/generate",
        json={"document_type": "Non-Disclosure Agreement"},
    )
    assert response.status_code == 422  # Unprocessable Entity (Pydantic validation)


def test_generate_empty_or_whitespace_fields():
    """Verify rejection when fields are blank or whitespace only."""
    response = client.post(
        "/api/generate",
        json={
            "document_type": "   ",
            "parties": "Acme Inc.",
            "terms": "Valid terms here",
            "dates": "2026",
        },
    )
    assert response.status_code == 422


def test_generate_handles_upstream_gemini_error():
    """Verify friendly error returned when Gemini generation fails."""
    with patch(
        "legalEaseAPI.routes.GeminiDocumentGenerator.generate_document",
        side_effect=RuntimeError("Gemini API rate limit exceeded. Please wait a moment and try again."),
    ):
        response = client.post(
            "/api/generate",
            json={
                "document_type": "Non-Disclosure Agreement",
                "parties": "Acme Inc. and Beta LLC",
                "terms": "Confidentiality terms",
                "dates": "2026",
            },
        )
        assert response.status_code == 503
        data = response.json()
        assert "rate limit" in data["detail"]


def test_export_txt_success():
    """Verify plain text document export."""
    response = client.post(
        "/api/export",
        json={
            "document_content": "AGREEMENT TITLE\n\n1. SCOPE\nThis is a test legal agreement.\n\nSIGNATURES",
            "document_type": "Test Agreement",
            "format": "txt",
        },
    )
    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]
    assert "LegalEase" in response.text


def test_export_docx_success():
    """Verify Word DOCX document export returns valid bytes."""
    response = client.post(
        "/api/export",
        json={
            "document_content": "SERVICES AGREEMENT\n\n1. SCOPE\nContractor shall perform services.\n\nSIGNATURES",
            "document_type": "Services Agreement",
            "format": "docx",
        },
    )
    assert response.status_code == 200
    assert "application/vnd.openxmlformats" in response.headers["content-type"]
    assert len(response.content) > 1000  # DOCX zip archive header


def test_export_pdf_success():
    """Verify PDF document export returns valid PDF binary bytes."""
    response = client.post(
        "/api/export",
        json={
            "document_content": "EMPLOYMENT AGREEMENT\n\n1. POSITION\nSoftware Engineer.\n\nSIGNATURES",
            "document_type": "Employment Agreement",
            "format": "pdf",
        },
    )
    assert response.status_code == 200
    assert "application/pdf" in response.headers["content-type"]
    assert response.content.startswith(b"%PDF-")


def test_export_invalid_format():
    """Verify validation error for unsupported export format."""
    response = client.post(
        "/api/export",
        json={
            "document_content": "Valid legal text content here for test.",
            "document_type": "Test",
            "format": "exe",
        },
    )
    assert response.status_code == 422
