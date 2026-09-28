"""Main entrypoint for LegalEase FastAPI application.

Configures CORS, registers API routers, sets up global error handling,
and serves the frontend web interface with comprehensive fallbacks for both
local development and Vercel serverless execution.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse, Response
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
    docs_url="/docs",
    openapi_url="/openapi.json"
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
# Register API Routes (Both with /api prefix and root for Vercel rewrites)
# =====================================================================
app.include_router(api_router, prefix="/api")
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
# Static File & UI Serving (Robust against Vercel serverless bundling)
# =====================================================================
BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"
PUBLIC_DIR = BASE_DIR / "public"

# Mount static directories if they exist
if PUBLIC_DIR.is_dir():
    app.mount("/public", StaticFiles(directory=str(PUBLIC_DIR)), name="public")

if FRONTEND_DIR.is_dir():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")


def _find_file(*candidates):
    """Search for a file across multiple candidate directories."""
    for c in candidates:
        if c and Path(c).is_file():
            return Path(c)
    return None


@app.get("/", include_in_schema=False)
@app.get("/index.html", include_in_schema=False)
async def serve_index():
    target = _find_file(
        BASE_DIR / "index.html",
        FRONTEND_DIR / "index.html",
        PUBLIC_DIR / "index.html",
        Path.cwd() / "index.html",
        Path.cwd() / "frontend" / "index.html",
    )
    if target:
        return FileResponse(str(target), media_type="text/html")
    return HTMLResponse("<h1>LegalEase</h1><p>Document Generator is running.</p>")


@app.get("/style.css", include_in_schema=False)
@app.get("/static/style.css", include_in_schema=False)
@app.get("/public/style.css", include_in_schema=False)
async def serve_css():
    target = _find_file(
        BASE_DIR / "style.css",
        FRONTEND_DIR / "style.css",
        PUBLIC_DIR / "style.css",
        Path.cwd() / "style.css",
        Path.cwd() / "frontend" / "style.css",
    )
    if target:
        return FileResponse(str(target), media_type="text/css")
    return Response(content="", media_type="text/css")


@app.get("/app.js", include_in_schema=False)
@app.get("/static/app.js", include_in_schema=False)
@app.get("/public/app.js", include_in_schema=False)
async def serve_js():
    target = _find_file(
        BASE_DIR / "app.js",
        FRONTEND_DIR / "app.js",
        PUBLIC_DIR / "app.js",
        Path.cwd() / "app.js",
        Path.cwd() / "frontend" / "app.js",
    )
    if target:
        return FileResponse(str(target), media_type="application/javascript")
    return Response(content="", media_type="application/javascript")


@app.get("/logo.svg", include_in_schema=False)
@app.get("/public/logo.svg", include_in_schema=False)
async def serve_logo_svg():
    target = _find_file(
        BASE_DIR / "logo.svg",
        PUBLIC_DIR / "logo.svg",
        Path.cwd() / "public" / "logo.svg",
    )
    if target:
        return FileResponse(str(target), media_type="image/svg+xml")
    return Response(content="", media_type="image/svg+xml")
