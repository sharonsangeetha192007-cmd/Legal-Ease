"""Tests for GeminiDocumentGenerator class and legal drafting prompts."""

import pytest
from unittest.mock import MagicMock, patch
from ai_core.gemini_generator import (
    GeminiDocumentGenerator,
    SUPPORTED_DOCUMENT_TYPES,
)


def test_generator_missing_api_key():
    """Verify ValueError is raised if API key is missing."""
    with patch.dict("os.environ", {}, clear=True):
        gen = GeminiDocumentGenerator(api_key=None)
        with pytest.raises(ValueError, match="Gemini API key is not configured"):
            gen.generate_document(
                document_type="Non-Disclosure Agreement",
                parties="Party A and Party B",
                terms="Terms",
                dates="2026",
            )


def test_generator_validates_input_arguments():
    """Verify ValueError raised when any input is empty."""
    gen = GeminiDocumentGenerator(api_key="mock_key")
    with pytest.raises(ValueError, match="Document type is required"):
        gen.generate_document("", "Parties", "Terms", "2026")

    with pytest.raises(ValueError, match="Parties information is required"):
        gen.generate_document("NDA", "", "Terms", "2026")

    with pytest.raises(ValueError, match="Key terms and conditions are required"):
        gen.generate_document("NDA", "Parties", "", "2026")

    with pytest.raises(ValueError, match="Dates or term duration is required"):
        gen.generate_document("NDA", "Parties", "Terms", "")


def test_generator_prompt_construction():
    """Verify system instructions enforce legal safety and placeholders."""
    gen = GeminiDocumentGenerator(api_key="mock_key")
    sys_prompt = gen._build_system_instruction()
    assert "DRAFTING ROLE ONLY" in sys_prompt
    assert "NO INVENTED FACTS" in sys_prompt
    assert "USE VISIBLE PLACEHOLDERS" in sys_prompt
    assert "[INSERT GOVERNING JURISDICTION]" in sys_prompt

    user_prompt = gen._build_user_prompt(
        document_type="Non-Disclosure Agreement",
        parties="Acme Corp and John Doe",
        terms="Strict 2-year confidentiality",
        dates="October 1, 2026",
    )
    assert "Non-Disclosure Agreement" in user_prompt
    assert "Acme Corp and John Doe" in user_prompt
    assert "Strict 2-year confidentiality" in user_prompt
    assert "October 1, 2026" in user_prompt


def test_generator_successful_call_strips_markdown():
    """Verify model response has surrounding markdown backticks stripped."""
    gen = GeminiDocumentGenerator(api_key="mock_key")

    mock_response = MagicMock()
    mock_response.text = "```markdown\nAGREEMENT TITLE\n\n1. TERMS\nAll good.\n```"

    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = mock_response

    with patch.object(gen, "_get_client", return_value=mock_client):
        doc = gen.generate_document(
            document_type="General Legal Agreement",
            parties="Party A & Party B",
            terms="Sample terms",
            dates="2026",
        )
        assert doc.startswith("AGREEMENT TITLE")
        assert not doc.startswith("```")
        assert not doc.endswith("```")


def test_generator_supported_types():
    """Verify all required legal document types are configured."""
    supported = GeminiDocumentGenerator.get_supported_types()
    assert "Non-Disclosure Agreement" in supported
    assert "Employment Agreement" in supported
    assert "Freelance/Independent Contractor Agreement" in supported
    assert "Rental/Lease Agreement" in supported
    assert "Service Agreement" in supported
    assert "Partnership Agreement" in supported
    assert "Sales Agreement" in supported
    assert "Memorandum of Understanding" in supported
    assert "Privacy Policy" in supported
    assert "Terms and Conditions" in supported
    assert "General Legal Agreement" in supported
