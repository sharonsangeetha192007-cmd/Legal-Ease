"""LegalEase Streamlit Application.

Alternative frontend interface compatible with Streamlit Community Cloud,
Render, or local standalone deployment. Communicates with the LegalEase
FastAPI backend for document generation and export.
"""

import os
import requests
import streamlit as st

# Configure Streamlit Page
st.set_page_config(
    page_title="LegalEase — AI Legal Document Generator",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# API Endpoint configuration (default to local or environment variable)
API_BASE_URL = os.getenv("LEGALEASE_API_URL", "http://localhost:8000")

# Supported Document Types
DOCUMENT_TYPES = [
    "Non-Disclosure Agreement",
    "Employment Agreement",
    "Freelance/Independent Contractor Agreement",
    "Rental/Lease Agreement",
    "Service Agreement",
    "Partnership Agreement",
    "Sales Agreement",
    "Memorandum of Understanding",
    "Privacy Policy",
    "Terms and Conditions",
    "General Legal Agreement",
]

# Initialize Session State
if "generated_document" not in st.session_state:
    st.session_state["generated_document"] = ""
if "document_type" not in st.session_state:
    st.session_state["document_type"] = "Non-Disclosure Agreement"

# Branding Header
st.title("⚖️ LegalEase")
st.caption("AI-Powered Legal Document Generator — Powered by Google Gemini")

# Legal Disclaimer Notice
st.warning(
    "⚠️ **Legal Notice**: LegalEase generates documents for informational and drafting purposes only. "
    "Generated content is not legal advice and should be reviewed by a qualified legal professional before signing or use."
)

# Sidebar: Health & Settings
with st.sidebar:
    st.header("Service Status")
    try:
        health_resp = requests.get(f"{API_BASE_URL}/api/health", timeout=3)
        if health_resp.status_code == 200:
            st.success("🟢 LegalEase API: Online")
        else:
            st.error(f"🔴 LegalEase API: Status {health_resp.status_code}")
    except Exception:
        st.warning("🟡 Cannot reach FastAPI service. Ensure `uvicorn legalEaseAPI.main:app` is running.")

    st.markdown("---")
    st.subheader("API Configuration")
    api_url_input = st.text_input("Backend API Base URL", value=API_BASE_URL)
    if api_url_input != API_BASE_URL:
        API_BASE_URL = api_url_input

    st.markdown("---")
    st.caption("LegalEase Pro v1.0.0")

# Main Interface: Two Column Layout
col_form, col_editor = st.columns([1, 1], gap="medium")

with col_form:
    st.subheader("1. Document Specifications")
    with st.form(key="document_generation_form"):
        selected_type = st.selectbox(
            "Document Type *",
            options=DOCUMENT_TYPES,
            index=DOCUMENT_TYPES.index(st.session_state["document_type"])
            if st.session_state["document_type"] in DOCUMENT_TYPES
            else 0,
        )

        parties = st.text_area(
            "Contracting Parties & Roles *",
            placeholder="e.g. Acme Corporation, a Delaware corp (Disclosing Party) and John Doe (Receiving Party)",
            height=100,
        )

        dates = st.text_input(
            "Effective Date & Term Duration *",
            placeholder="e.g. October 1, 2026, for a period of 2 years",
        )

        terms = st.text_area(
            "Key Terms, Covenants & Obligations *",
            placeholder="Enter all specific terms, financial arrangements, scope of confidentiality, milestone requirements, governing jurisdiction, and termination rules...",
            height=180,
        )

        generate_submitted = st.form_submit_button(
            "✨ Generate Legal Document", use_container_width=True
        )

    if generate_submitted:
        if not parties.strip():
            st.error("Please specify the contracting parties.")
        elif not dates.strip():
            st.error("Please enter the effective date or term duration.")
        elif not terms.strip():
            st.error("Please specify the key terms and conditions.")
        else:
            with st.spinner("Drafting professional legal document with Gemini AI..."):
                try:
                    payload = {
                        "document_type": selected_type,
                        "parties": parties.strip(),
                        "dates": dates.strip(),
                        "terms": terms.strip(),
                    }
                    response = requests.post(
                        f"{API_BASE_URL}/api/generate", json=payload, timeout=60
                    )
                    if response.status_code == 200:
                        data = response.json()
                        st.session_state["generated_document"] = data.get("document", "")
                        st.session_state["document_type"] = selected_type
                        st.success("Document generated successfully! Review and edit below.")
                    else:
                        error_detail = response.json().get("detail", "Generation failed.")
                        st.error(f"Error ({response.status_code}): {error_detail}")
                except Exception as e:
                    st.error(f"Failed to connect to API: {str(e)}")

with col_editor:
    st.subheader("2. Review, Edit & Export")

    # Editable document area
    edited_doc = st.text_area(
        "Generated Document (Editable)",
        value=st.session_state["generated_document"],
        height=450,
        placeholder="Your generated legal document will appear here for review and inline editing...",
    )

    if edited_doc:
        st.session_state["generated_document"] = edited_doc

        # Metrics
        words = len(edited_doc.split())
        chars = len(edited_doc)
        st.caption(f"📊 **Metrics:** {words:,} words | {chars:,} characters")

        st.markdown("#### Download Document")
        btn_col1, btn_col2, btn_col3 = st.columns(3)

        # 1. Plain Text Download
        with btn_col1:
            st.download_button(
                label="📄 Download TXT",
                data=edited_doc.encode("utf-8"),
                file_name=f"{st.session_state['document_type'].lower().replace(' ', '_')}.txt",
                mime="text/plain",
                use_container_width=True,
            )

        # 2. DOCX Download (Call API export)
        with btn_col2:
            try:
                docx_resp = requests.post(
                    f"{API_BASE_URL}/api/export",
                    json={
                        "document_content": edited_doc,
                        "document_type": st.session_state["document_type"],
                        "format": "docx",
                    },
                    timeout=30,
                )
                if docx_resp.status_code == 200:
                    st.download_button(
                        label="📝 Download DOCX",
                        data=docx_resp.content,
                        file_name=f"{st.session_state['document_type'].lower().replace(' ', '_')}.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        use_container_width=True,
                    )
                else:
                    st.button("DOCX (Service Unavailable)", disabled=True, use_container_width=True)
            except Exception:
                st.button("DOCX (Offline)", disabled=True, use_container_width=True)

        # 3. PDF Download (Call API export)
        with btn_col3:
            try:
                pdf_resp = requests.post(
                    f"{API_BASE_URL}/api/export",
                    json={
                        "document_content": edited_doc,
                        "document_type": st.session_state["document_type"],
                        "format": "pdf",
                    },
                    timeout=30,
                )
                if pdf_resp.status_code == 200:
                    st.download_button(
                        label="📕 Download PDF",
                        data=pdf_resp.content,
                        file_name=f"{st.session_state['document_type'].lower().replace(' ', '_')}.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                    )
                else:
                    st.button("PDF (Service Unavailable)", disabled=True, use_container_width=True)
            except Exception:
                st.button("PDF (Offline)", disabled=True, use_container_width=True)
    else:
        st.info("👈 Fill out the terms and click **Generate Legal Document** to draft your agreement.")
