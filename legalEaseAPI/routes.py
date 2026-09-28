"""API routes for LegalEase.

Exposes endpoints for document generation, document export, health checks,
and supported document types metadata.
"""

import re
import urllib.parse
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field, field_validator

from ai_core.gemini_generator import (
    GeminiDocumentGenerator,
    SUPPORTED_DOCUMENT_TYPES,
    LEGAL_DISCLAIMER_TEXT,
)
from ai_core.export_utils import export_to_txt, export_to_docx, export_to_pdf

router = APIRouter(prefix="/api", tags=["LegalEase"])


# =====================================================================
# Request & Response Schemas
# =====================================================================

class DocumentRequest(BaseModel):
    """Input payload for generating a legal document."""
    document_type: str = Field(
        ...,
        min_length=3,
        max_length=150,
        description="Type of legal document (e.g., Non-Disclosure Agreement)",
        examples=["Non-Disclosure Agreement"]
    )
    parties: str = Field(
        ...,
        min_length=3,
        max_length=1500,
        description="Names and roles of the contracting parties",
        examples=["Acme Corp (Disclosing Party) and John Doe (Receiving Party)"]
    )
    terms: str = Field(
        ...,
        min_length=5,
        max_length=10000,
        description="Key terms, covenants, consideration, and obligations",
        examples=["2-year confidentiality period, standard exclusions, mutual return of documents."]
    )
    dates: str = Field(
        ...,
        min_length=2,
        max_length=300,
        description="Effective date, duration, or milestone dates",
        examples=["October 1, 2026 for a period of 2 years"]
    )

    @field_validator("document_type", "parties", "terms", "dates")
    @classmethod
    def check_not_empty_or_whitespace(cls, v: str, info) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError(f"Field '{info.field_name}' must not be empty or whitespace only.")
        return stripped


class DocumentResponse(BaseModel):
    """Response payload containing generated legal document."""
    success: bool = True
    document: str
    document_type: str
    disclaimer: str = LEGAL_DISCLAIMER_TEXT


class ExportRequest(BaseModel):
    """Payload to export an edited document to TXT, DOCX, or PDF."""
    document_content: str = Field(
        ...,
        min_length=10,
        max_length=300000,
        description="Document text content to export"
    )
    document_type: Optional[str] = Field(
        default="Legal Document",
        max_length=150,
        description="Document title/type for headers and file naming"
    )
    format: str = Field(
        ...,
        pattern=r"^(txt|docx|pdf)$",
        description="Desired export file format (txt, docx, pdf)"
    )

    @field_validator("document_content")
    @classmethod
    def check_content_not_empty(cls, v: str) -> str:
        stripped = v.strip()
        if len(stripped) < 10:
            raise ValueError("Document content is too short to export.")
        return stripped


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "ok"
    app: str = "LegalEase API"
    timestamp: str


# =====================================================================
# API Endpoints
# =====================================================================

@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check endpoint",
    description="Returns the operational status of the LegalEase API service."
)
async def health_check():
    """Health check endpoint for deployment monitoring and verification."""
    return HealthResponse(
        status="ok",
        app="LegalEase API",
        timestamp=datetime.now(timezone.utc).isoformat()
    )


@router.get(
    "/document-types",
    summary="List supported document types",
    description="Returns all supported legal document types and their recommended clauses."
)
async def list_document_types() -> Dict[str, Any]:
    """Retrieve supported document types and metadata."""
    types_list = [
        {
            "name": name,
            "description": info["description"],
            "key_clauses": info["key_clauses"],
        }
        for name, info in SUPPORTED_DOCUMENT_TYPES.items()
    ]
    return {
        "supported_types": types_list,
        "total": len(types_list),
        "disclaimer": LEGAL_DISCLAIMER_TEXT,
    }


@router.post(
    "/generate",
    response_model=DocumentResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate a legal document",
    description="Generates a structured, professional legal document using Google Gemini."
)
async def generate_document(request: DocumentRequest):
    """Generate a legal document based on user inputs."""
    try:
        generator = GeminiDocumentGenerator()
        generated_text = generator.generate_document(
            document_type=request.document_type,
            parties=request.parties,
            terms=request.terms,
            dates=request.dates,
        )
        return DocumentResponse(
            success=True,
            document=generated_text,
            document_type=request.document_type,
            disclaimer=LEGAL_DISCLAIMER_TEXT,
        )
    except ValueError as ve:
        # Client validation or configuration errors
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except RuntimeError as re_err:
        # Upstream Gemini or service errors
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(re_err)
        )
    except Exception as e:
        # Unexpected server errors (masked for security)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="We couldn't generate the document right now. Please check your inputs and try again."
        )


def _safe_filename(name: str, ext: str) -> str:
    """Create a sanitized, URL-safe download filename."""
    clean = re.sub(r'[^a-zA-Z0-9_-]', '_', name.strip().lower())
    clean = re.sub(r'_+', '_', clean).strip('_')
    if not clean:
        clean = "legal_document"
    return f"{clean}.{ext}"


@router.post(
    "/export",
    summary="Export legal document",
    description="Exports document text to TXT, DOCX, or PDF with LegalEase formatting and branding."
)
async def export_document(request: ExportRequest):
    """Export document content as an in-memory downloadable file."""
    doc_type = request.document_type or "Legal Document"
    fmt = request.format.lower()

    try:
        if fmt == "txt":
            buffer = export_to_txt(request.document_content)
            media_type = "text/plain; charset=utf-8"
            filename = _safe_filename(doc_type, "txt")
        elif fmt == "docx":
            buffer = export_to_docx(request.document_content, document_title=doc_type)
            media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            filename = _safe_filename(doc_type, "docx")
        elif fmt == "pdf":
            buffer = export_to_pdf(request.document_content, document_title=doc_type)
            media_type = "application/pdf"
            filename = _safe_filename(doc_type, "pdf")
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported format '{fmt}'. Choose from: txt, docx, pdf."
            )

        # RFC 5987 / 6266 safe header encoding
        encoded_filename = urllib.parse.quote(filename)
        headers = {
            "Content-Disposition": f'attachment; filename="{filename}"; filename*=UTF-8\'\'{encoded_filename}'
        }

        return StreamingResponse(
            buffer,
            media_type=media_type,
            headers=headers
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate {fmt.upper()} export: {str(e)}"
        )


@router.post("/export/txt", summary="Export to TXT")
async def export_txt(request: ExportRequest):
    """Convenience endpoint to export as plain text."""
    request.format = "txt"
    return await export_document(request)


@router.post("/export/docx", summary="Export to DOCX")
async def export_docx(request: ExportRequest):
    """Convenience endpoint to export as DOCX."""
    request.format = "docx"
    return await export_document(request)


@router.post("/export/pdf", summary="Export to PDF")
async def export_pdf(request: ExportRequest):
    """Convenience endpoint to export as PDF."""
    request.format = "pdf"
    return await export_document(request)
