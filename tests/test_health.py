"""Tests for LegalEase health check and document-types endpoints."""

import pytest
from fastapi.testclient import TestClient
from legalEaseAPI.main import app

client = TestClient(app)


def test_health_check_returns_200():
    """Verify that /api/health responds with 200 OK and expected payload."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "LegalEase" in data["app"]
    assert "timestamp" in data


def test_document_types_returns_list():
    """Verify that /api/document-types returns supported legal document types."""
    response = client.get("/api/document-types")
    assert response.status_code == 200
    data = response.json()
    assert "supported_types" in data
    assert data["total"] >= 10
    names = [t["name"] for t in data["supported_types"]]
    assert "Non-Disclosure Agreement" in names
    assert "Employment Agreement" in names
    assert "Freelance/Independent Contractor Agreement" in names
    assert "Rental/Lease Agreement" in names
    assert "disclaimer" in data
