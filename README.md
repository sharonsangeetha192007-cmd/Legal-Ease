# ⚖️ LegalEase: AI-Powered Legal Document Generator

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Google Gemini](https://img.shields.io/badge/Google%20Gemini-3.8%20%2F%202.5-4285F4.svg?logo=google&logoColor=white)](https://ai.google.dev)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB.svg?logo=python&logoColor=white)](https://python.org)
[![Vercel Ready](https://img.shields.io/badge/Deployment-Vercel%20Serverless-black.svg?logo=vercel&logoColor=white)](https://vercel.com)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

**LegalEase** is a production-grade legal document generation platform powered by Google Gemini. It enables attorneys, founders, freelancers, and businesses to draft meticulously structured legal contracts, perform real-time in-browser edits, and export finalized agreements directly to **TXT**, **DOCX (Microsoft Word)**, and **PDF** formats.

---

## 📑 Table of Contents

1. [Project Overview](#-project-overview)
2. [Key Features](#-key-features)
3. [System Architecture](#-system-architecture)
4. [Project Structure](#-project-structure)
5. [Prerequisites](#-prerequisites)
6. [Installation & Setup](#-installation--setup)
7. [Environment Configuration](#-environment-configuration)
8. [Local Development](#-local-development)
9. [API Documentation](#-api-documentation)
10. [Frontend Usage & Workflow](#-frontend-usage--workflow)
11. [Document Export Engine](#-document-export-engine)
12. [Automated Testing](#-automated-testing)
13. [Vercel Production Deployment](#-vercel-production-deployment)
14. [Streamlit Deployment (Optional)](#-streamlit-deployment-optional)
15. [Security & Compliance](#-security--compliance)
16. [Legal Disclaimer](#-legal-disclaimer)
17. [Troubleshooting Guide](#-troubleshooting-guide)

---

## 🌟 Project Overview

Traditional contract drafting is either prohibitively expensive or relies on rigid, static boilerplate forms that do not reflect unique commercial terms. **LegalEase** bridges this divide by uniting:
- **Google Gemini API** for context-aware, structured legal synthesis.
- **FastAPI** for an asynchronous, high-throughput backend with strict Pydantic validation.
- **In-Memory Document Formatting** with `python-docx` and `fpdf2`, ensuring zero disk writes in serverless execution environments.
- **Dual Frontend Architecture**: A high-performance, responsive HTML5/CSS3/JavaScript UI for Vercel, paired with an optional Streamlit application for rapid internal experimentation.

---

## ✨ Key Features

- **11 Standardized Legal Document Categories**:
  - Non-Disclosure Agreements (NDA)
  - Employment Agreements
  - Freelance / Independent Contractor Agreements
  - Commercial & Residential Rental / Lease Agreements
  - Master Service Agreements (MSA)
  - Partnership Agreements
  - Sales & Purchase Agreements
  - Memorandums of Understanding (MOU)
  - Privacy Policies (GDPR / CCPA compliant structures)
  - Terms of Service / Terms & Conditions
  - General Legal Agreements
- **Strict Legal Guardrails & Ethics**:
  - Zero hallucination rules for statutory codes or case citations.
  - Prominent uppercase bracketed placeholders (e.g., `[INSERT GOVERNING STATE]`, `[INSERT EFFECTIVE DATE]`).
  - Strict advisory disclaimers on all outputs and exported files.
- **Interactive In-Browser Document Editor**:
  - Full inline editing before document commitment.
  - Live word and character metrics.
  - One-click clipboard copying.
  - Instant regeneration controls.
- **Multi-Format In-Memory Export**:
  - **Plain Text (`.txt`)**: UTF-8 formatted with header disclaimers.
  - **Word (`.docx`)**: Times New Roman 11pt, 1-inch margins, multi-level numbering, header/footer branding, and two-column signature tables.
  - **PDF (`.pdf`)**: A4 format, page numbers (`Page X of Y`), running headers, and clean typography.
- **1-Click Sample Presets**: Quickly populate complete examples for NDAs, Contractor Agreements, Leases, and Employment Contracts.

---

## 🏛 System Architecture

LegalEase follows a serverless-native decoupled architecture:

```
                    ┌─────────────────────────────────────────┐
                    │              LegalEase UI               │
                    │   HTML5 / CSS3 / ES6+ Responsive SPA    │
                    │   (Served Statically / Vercel Edge)     │
                    └────────────────────┬────────────────────┘
                                         │
                                         │ HTTPS / REST JSON
                                         ▼
                    ┌─────────────────────────────────────────┐
                    │         FastAPI REST Backend            │
                    │         (Vercel Serverless /            │
                    │          api/index.py Entry)            │
                    └──────────┬───────────────────┬──────────┘
                               │                   │
                     Generates │                   │ Exports In-Memory
                     Document  │                   │ (TXT / DOCX / PDF)
                               ▼                   ▼
                    ┌────────────────────┐ ┌──────────────────┐
                    │  Google Gemini AI  │ │ ai_core/export   │
                    │   (google-genai)   │ │  python-docx &   │
                    │ gemini-2.5-flash   │ │      fpdf2       │
                    └────────────────────┘ └──────────────────┘
```

> **Why Not Deploy Streamlit on Vercel?**  
> Streamlit requires an active Python WebSocket connection and persistent memory space. Vercel Serverless executes short-lived ephemeral HTTP functions. LegalEase provides the production SPA for Vercel and keeps the Streamlit app (`frontend/app.py`) for local runs or Streamlit Community Cloud / Render.

---

## 📁 Project Structure

```
legalease/
├── api/
│   └── index.py               # Vercel serverless entrypoint importing FastAPI
├── ai_core/
│   ├── __init__.py            # AI core module exports
│   ├── gemini_generator.py    # GeminiDocumentGenerator class & drafting prompts
│   └── export_utils.py        # In-memory TXT, DOCX, and PDF generators
├── legalEaseAPI/
│   ├── __init__.py            # API module exports
│   ├── main.py                # FastAPI app, CORS, static mounting, error handling
│   └── routes.py              # Endpoints: /generate, /export, /health, /document-types
├── frontend/
│   ├── index.html             # Production responsive web interface
│   ├── style.css              # Custom legal-tech theme styling
│   ├── app.js                 # Frontend state, API client, blob downloads
│   └── app.py                 # Alternative Streamlit frontend application
├── public/
│   ├── logo.svg               # Scalable vector logo (Scales of Justice & Document)
│   └── logo.png               # High-resolution raster branding asset
├── tests/
│   ├── __init__.py
│   ├── test_health.py         # Healthcheck & document types endpoint tests
│   ├── test_routes.py         # Route validation, mock generation, export tests
│   ├── test_generator.py      # Prompt construction & API key tests
│   └── test_export.py         # In-memory TXT, DOCX, and PDF tests
├── .env.example               # Template environment configuration
├── .gitignore                 # Excludes .env, virtualenvs, bytecode, caches
├── requirements.txt           # Python dependencies pinned for production
├── vercel.json                # Vercel serverless routing & rewrites
├── package.json               # NPM scripts for developer workflows
└── README.md                  # Comprehensive platform documentation
```

---

## 📋 Prerequisites

Before setting up LegalEase locally or in production, ensure you have:
1. **Python 3.10+** (Tested on Python 3.10, 3.11, 3.12, 3.13).
2. **Google Gemini API Key**: Obtain a free API key from [Google AI Studio](https://aistudio.google.com/).

---

## 🚀 Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/legalease.git
cd legalease
```

### 2. Create and Activate a Virtual Environment

**On Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**On macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 🔑 Environment Configuration

Create a local `.env` file by copying the example template:

```bash
cp .env.example .env
```

Open `.env` and insert your Gemini API key:
```ini
# Required: Google Gemini API Key
GEMINI_API_KEY=AIzaSyYourGeminiApiKeyHere

# Optional: Gemini Model Selection (defaults to gemini-2.5-flash)
GEMINI_MODEL=gemini-2.5-flash

# Optional: CORS Allowed Origins (defaults to * in development)
ALLOWED_ORIGINS=*

# Optional: Streamlit API base URL (used when running frontend/app.py)
LEGALEASE_API_URL=http://localhost:8000
```

> ⚠️ **Security Warning**: Never commit your `.env` file to version control. The `.gitignore` is pre-configured to prevent `.env` commits.

---

## 💻 Local Development

### Running the FastAPI Backend & Production Web UI

Start the Uvicorn server:
```bash
uvicorn legalEaseAPI.main:app --reload --port 8000
```

Once running:
- **Web Application UI**: Open [http://localhost:8000](http://localhost:8000) in your browser.
- **Interactive Swagger Docs**: Open [http://localhost:8000/api/docs](http://localhost:8000/api/docs).
- **Redoc Documentation**: Open [http://localhost:8000/api/redoc](http://localhost:8000/api/redoc).
- **Health Check Endpoint**: [http://localhost:8000/api/health](http://localhost:8000/api/health).

### Running the Streamlit Frontend (Optional)

In a separate terminal window with your virtual environment activated:
```bash
streamlit run frontend/app.py
```
This launches the Streamlit interface at [http://localhost:8501](http://localhost:8501).

---

## 🔌 API Documentation

### 1. Health Verification
- **Endpoint**: `GET /api/health`
- **Description**: Verifies service status and returns timestamp.
- **Response `200 OK`**:
```json
{
  "status": "ok",
  "app": "LegalEase API",
  "timestamp": "2026-09-28T14:15:00.000000+00:00"
}
```

### 2. Supported Document Types
- **Endpoint**: `GET /api/document-types`
- **Description**: Returns all 11 supported document types and standard clauses.

### 3. Generate Legal Document
- **Endpoint**: `POST /api/generate`
- **Request Body**:
```json
{
  "document_type": "Non-Disclosure Agreement",
  "parties": "Acme Corp (Disclosing Party) and Global Tech LLC (Receiving Party)",
  "terms": "Mutual confidentiality for 2 years. Standard exclusions. Return or destroy records upon notice.",
  "dates": "October 1, 2026"
}
```
- **Response `200 OK`**:
```json
{
  "success": true,
  "document": "MUTUAL NON-DISCLOSURE AGREEMENT\n\nThis Mutual Non-Disclosure Agreement...",
  "document_type": "Non-Disclosure Agreement",
  "disclaimer": "LegalEase generates documents for informational and drafting purposes only..."
}
```

### 4. Export Document
- **Endpoint**: `POST /api/export`
- **Request Body**:
```json
{
  "document_content": "MUTUAL NON-DISCLOSURE AGREEMENT\n\n1. DEFINITIONS...",
  "document_type": "Non-Disclosure Agreement",
  "format": "docx"
}
```
- **Response**: Binary stream with `Content-Disposition: attachment; filename="non_disclosure_agreement.docx"`.
- **Supported Formats**: `txt`, `docx`, `pdf`.

---

## 🖥 Frontend Usage & Workflow

1. **Select Document Type**: Choose from 11 contract types in the dropdown.
2. **Use Quick Presets (Optional)**: Click the **Sample Preset** selector to instantly populate complete, realistic commercial terms.
3. **Customize Parties & Dates**: Input corporate names, jurisdictions of incorporation, and effective dates.
4. **Define Terms & Covenants**: Specify deliverables, IP ownership, liability caps, warranties, and milestones.
5. **Generate**: Click **Generate Legal Document**. The Gemini AI constructs a comprehensive agreement adhering to legal drafting standards.
6. **Review & In-Place Editing**: Inspect the generated text inside the editor. Adjust clauses, replace placeholders (e.g. `[INSERT STATE]`), or add custom riders.
7. **Export**: Click **TXT**, **DOCX**, or **PDF** to download your finalized document directly to your device.

---

## 📄 Document Export Engine

LegalEase provides institutional-grade formatting without third-party external conversion APIs or disk-bound operations:

| Feature | TXT Export | DOCX Export (`python-docx`) | PDF Export (`fpdf2`) |
| :--- | :--- | :--- | :--- |
| **Typography** | Plain Text UTF-8 | Times New Roman (11pt / 15pt Title) | Helvetica / Times |
| **Page Layout** | Continuous | Letter (8.5" x 11"), 1-inch margins | A4, 20mm margins |
| **Headers/Footers** | Top/Bottom text rules | Running header + disclaimer footer | Running header + dynamic page numbers |
| **Signature Block** | ASCII text lines | Formatted 2-column table | Dual-column block |
| **Memory Model** | `io.BytesIO` buffer | `io.BytesIO` buffer | `io.BytesIO` buffer |
| **Serverless Safe** | ✅ 100% In-Memory | ✅ 100% In-Memory | ✅ 100% In-Memory |

---

## 🧪 Automated Testing

LegalEase includes a full test suite built with `pytest` and `httpx`. Gemini API calls are mocked to ensure instant, deterministic test execution without consuming API quota:

```bash
# Run all tests with verbose output
pytest tests/ -v
```

### Test Coverage Highlights:
- `tests/test_health.py`: Healthcheck endpoint and document types metadata.
- `tests/test_routes.py`: Pydantic validation (empty strings, whitespace-only, field length limits), successful generation, 503 error bubbling, and export endpoints.
- `tests/test_generator.py`: Prompt synthesis, missing API key exceptions, Markdown backtick stripping, and legal disclaimer preservation.
- `tests/test_export.py`: Binary integrity, byte headers, table structures, and UTF-8 encoding for TXT, DOCX, and PDF generators.

---

## ☁️ Vercel Production Deployment

LegalEase is configured for 1-click deployment to Vercel via `@vercel/python` and static asset routing.

### Step 1: Push Code to GitHub
```bash
git init
git add .
git commit -m "feat: initial commit of LegalEase"
git branch -M main
git remote add origin https://github.com/your-username/legalease.git
git push -u origin main
```

### Step 2: Import Project into Vercel
1. Log into your [Vercel Dashboard](https://vercel.com).
2. Click **Add New...** -> **Project**.
3. Select your `legalease` repository from GitHub.
4. Keep the Framework Preset as **Other**.

### Step 3: Add Environment Variables
Under **Environment Variables**, configure:
- `GEMINI_API_KEY`: Your Google Gemini API Key from Google AI Studio.
- `GEMINI_MODEL`: `gemini-2.5-flash` (or `gemini-3.8-flash`).

### Step 4: Deploy
Click **Deploy**. Vercel will:
1. Build the Python serverless function for `api/index.py`.
2. Host the frontend assets from `frontend/` and `public/` at the global edge.
3. Automatically route `/api/*` to the FastAPI backend and `/` to `frontend/index.html`.

---

## 🎈 Streamlit Deployment (Optional)

To deploy the Streamlit frontend independently to **Streamlit Community Cloud**:
1. Connect your repository to [share.streamlit.io](https://share.streamlit.io).
2. Set the main file path to: `frontend/app.py`.
3. In Streamlit App Settings -> **Secrets**, add:
   ```toml
   LEGALEASE_API_URL = "https://your-legalease-fastapi-domain.vercel.app"
   ```
4. Deploy the application.

---

## 🛡️ Security & Compliance

- **No Credential Exposure**: `GEMINI_API_KEY` is strictly accessed on the backend server and is never passed to frontend browser JavaScript.
- **Ephemerality**: LegalEase does not persistently store generated legal documents in any database. Content resides in memory for the duration of the HTTP request.
- **Sanitized Headers**: Download filenames are sanitized to prevent header injection or directory traversal attacks.
- **Stack Trace Shielding**: Global FastAPI exception handlers intercept uncaught exceptions and return friendly error objects rather than leaking server execution paths.
- **Strict Input Validation**: Request payloads are bound by minimum and maximum character limits to guard against buffer exhaustion attacks.

---

## ⚖️ Legal Disclaimer

> **IMPORTANT NOTICE**:  
> LegalEase generates documents for informational, educational, and drafting purposes only. Generated documents do not constitute legal advice, nor does the use of LegalEase establish an attorney-client relationship. Laws vary significantly across jurisdictions, states, and countries. Always review generated legal documents with licensed legal counsel prior to execution or reliance.

---

## 🔍 Troubleshooting Guide

| Issue | Cause | Solution |
| :--- | :--- | :--- |
| **API Status shows "API Offline"** | FastAPI server not running on localhost:8000 | Run `uvicorn legalEaseAPI.main:app --reload` and check terminal logs. |
| **400 Bad Request: "Gemini API key is not configured"** | Missing `GEMINI_API_KEY` in environment | Create `.env` from `.env.example` and set a valid API key. |
| **503 Service Unavailable: "rate limit exceeded"** | Google Gemini quota limit reached | Wait 60 seconds or switch to a paid tier key in Google AI Studio. |
| **PDF export fails on rare symbols** | Character outside Latin-1 encoding | Handled automatically by `_sanitize_pdf_text` in `export_utils.py`. |
| **CORS errors in browser console** | Accessing API from unauthorized origin | Update `ALLOWED_ORIGINS` in `.env` to include your origin or `*`. |

---

<p align="center">
  <sub>Crafted with precision for legal professionals, startups, and developers worldwide.</sub>
</p>
