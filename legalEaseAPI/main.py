"""Main entrypoint for LegalEase FastAPI application.

Configures CORS, registers API routers, sets up global error handling,
and optionally serves the frontend for seamless local development.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from legalEaseAPI.routes import router as api_router
from ai_core.gemini_generator import LEGAL_DISCLAIMER_TEXT

# Load environment variables from .env if present
load_dotenv()

app = FastAPI(
    title="LegalEase: AI-Powered Legal Document Generator",
    description=(
        "Production-ready AI Legal Drafting platform powered by Google Gemini. "
        "Generates structured legal documents, facilitates in-browser edits, "
        "and exports to TXT, DOCX, and PDF.\n\n"
        f"LEGAL DISCLAIMER: {LEGAL_DISCLAIMER_TEXT}"
    ),
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# =====================================================================
# CORS Configuration
# =====================================================================
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS if ALLOWED_ORIGINS != ["*"] else ["*"],
    allow_credentials=True if ALLOWED_ORIGINS != ["*"] else False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================================================
# API Routes
# =====================================================================
app.include_router(api_router)


# =====================================================================
# Global Exception Handler (Never leak stack traces)
# =====================================================================
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Fallback handler to prevent raw stack traces from reaching clients."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An unexpected server error occurred. Please verify your inputs and try again.",
            "type": "server_error"
        }
    )


# =====================================================================
# Static Frontend Serving for Local Development
# =====================================================================
BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"
PUBLIC_DIR = BASE_DIR / "public"

# Mount /public if it exists
if PUBLIC_DIR.is_dir():
    app.mount("/public", StaticFiles(directory=str(PUBLIC_DIR)), name="public")

# Serve frontend static assets and index.html
if FRONTEND_DIR.is_dir():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

    @app.get("/", include_in_schema=False)
    async def serve_index():
        index_file = FRONTEND_DIR / "index.html"
        if index_file.is_file():
            return FileResponse(str(index_file))
        return JSONResponse({"message": "LegalEase API is running. Access /api/docs for documentation."})
