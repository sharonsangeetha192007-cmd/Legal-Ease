"""Vercel Serverless entrypoint for LegalEase FastAPI backend."""

from legalEaseAPI.main import app

# Export app for ASGI serverless runtime
__all__ = ["app"]
