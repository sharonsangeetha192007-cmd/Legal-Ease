"""Gemini AI Document Generator for LegalEase.

Generates structured, professional legal documents using the Google Gemini API.
Adheres strictly to legal safety guidelines and drafting standards.
"""

import os
import logging
from typing import Optional, Dict, Any, List

logger = logging.getLogger("legalease.generator")

# Supported document types and their specific drafting guidance
SUPPORTED_DOCUMENT_TYPES: Dict[str, Dict[str, Any]] = {
    "Non-Disclosure Agreement": {
        "description": "Protects confidential information shared between disclosing and receiving parties.",
        "key_clauses": [
            "Definition of Confidential Information",
            "Exclusions from Confidentiality",
            "Obligations of Receiving Party",
            "Standard of Care",
            "Term and Return of Materials",
            "Remedies for Breach",
        ],
    },
    "Employment Agreement": {
        "description": "Defines rights, responsibilities, compensation, and policies between employer and employee.",
        "key_clauses": [
            "Position and Duties",
            "Compensation and Benefits",
            "Term and At-Will Status (or Fixed Term)",
            "Confidentiality and Proprietary Information",
            "Invention Assignment",
            "Termination Conditions and Severance",
        ],
    },
    "Freelance/Independent Contractor Agreement": {
        "description": "Establishes independent contractor relationship, statement of work, and IP rights.",
        "key_clauses": [
            "Scope of Services and Deliverables",
            "Independent Contractor Status (No Employment/Benefits)",
            "Compensation, Invoicing, and Payment Schedule",
            "Work Made for Hire and Intellectual Property Assignment",
            "Warranties and Indemnification",
            "Termination for Convenience and Cause",
        ],
    },
    "Rental/Lease Agreement": {
        "description": "Governs the rental of residential or commercial property between landlord and tenant.",
        "key_clauses": [
            "Description of Leased Premises",
            "Lease Term and Renewal Options",
            "Rent Amount, Due Date, and Late Fees",
            "Security Deposit and Return Conditions",
            "Use of Property, Maintenance, and Repairs",
            "Default, Eviction, and Surrender of Premises",
        ],
    },
    "Service Agreement": {
        "description": "Defines terms under which a service provider delivers specific services to a client.",
        "key_clauses": [
            "Services Provided and Performance Standards",
            "Fees, Expenses, and Payment Milestones",
            "Client Obligations and Access Requirements",
            "Intellectual Property and Licensing",
            "Limitation of Liability and Disclaimers",
            "Term, Suspension, and Termination",
        ],
    },
    "Partnership Agreement": {
        "description": "Formalizes the partnership terms, ownership shares, profits, and management duties.",
        "key_clauses": [
            "Partnership Purpose and Name",
            "Capital Contributions and Ownership Percentages",
            "Allocation of Profits and Losses",
            "Management Authority and Decision-Making Voting",
            "Withdrawal, Dissolution, and Buy-Sell Provisions",
            "Books, Records, and Accounting",
        ],
    },
    "Sales Agreement": {
        "description": "Documents the sale and transfer of goods or property between seller and buyer.",
        "key_clauses": [
            "Description and Quantity of Goods",
            "Purchase Price and Payment Terms",
            "Delivery Method, Risk of Loss, and Title Transfer",
            "Inspection Period and Acceptance/Rejection",
            "Express and Implied Warranties",
            "Remedies and Limitation of Damages",
        ],
    },
    "Memorandum of Understanding": {
        "description": "Outlines mutual intentions and principles of cooperation between parties.",
        "key_clauses": [
            "Purpose and Mutual Objectives",
            "Roles and Responsibilities of Parties",
            "Non-Binding Statement of Intent (Except Confidentiality)",
            "Financial Arrangements or Resource Commitments",
            "Duration and Review Timeline",
            "Signatures of Authorized Representatives",
        ],
    },
    "Privacy Policy": {
        "description": "Discloses how a website, application, or company collects, uses, and safeguards user data.",
        "key_clauses": [
            "Categories of Personal Information Collected",
            "Methods of Collection (Direct, Cookies, Automated)",
            "Purposes of Processing and Use",
            "Third-Party Sharing and Disclosures",
            "Data Security, Retention, and Storage",
            "User Privacy Rights (Access, Deletion, Opt-Out) and Contact",
        ],
    },
    "Terms and Conditions": {
        "description": "Sets the rules and legal guidelines users must agree to when using a platform or service.",
        "key_clauses": [
            "User Eligibility and Account Registration",
            "Acceptable Use and Prohibited Conduct",
            "Intellectual Property Ownership of Service Content",
            "User-Generated Content License",
            "Disclaimers of Warranty and Limitation of Liability",
            "Account Suspension, Termination, and Governing Law",
        ],
    },
    "General Legal Agreement": {
        "description": "A flexible, comprehensive legal agreement for custom business and personal relationships.",
        "key_clauses": [
            "Recitals and Consideration",
            "Covenants and Obligations",
            "Representations and Warranties",
            "Default and Remedies",
            "Governing Law and Dispute Resolution",
            "Entire Agreement and Amendments",
        ],
    },
}

LEGAL_DISCLAIMER_TEXT = (
    "LegalEase generates documents for informational and drafting purposes only. "
    "Generated content is not legal advice and should be reviewed by a qualified "
    "legal professional before signing or use."
)


class GeminiDocumentGenerator:
    """Reusable generator for professional legal documents using Google Gemini."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """Initialize the Gemini document generator.

        Args:
            api_key: Optional Gemini API key. Defaults to GEMINI_API_KEY environment variable.
            model: Optional model name. Defaults to GEMINI_MODEL env var or 'gemini-2.5-flash'.
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model = model or os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        self._client = None

    def _get_client(self):
        """Lazy-load the Gemini Client using google-genai SDK."""
        if not self.api_key:
            raise ValueError(
                "Gemini API key is not configured. Please set the GEMINI_API_KEY "
                "environment variable or provide it to the generator."
            )
        if self._client is None:
            try:
                from google import genai
                self._client = genai.Client(api_key=self.api_key)
            except ImportError:
                raise RuntimeError(
                    "The 'google-genai' package is required. "
                    "Please install it using 'pip install google-genai'."
                )
        return self._client

    @staticmethod
    def get_supported_types() -> List[str]:
        """Return the list of supported legal document types."""
        return list(SUPPORTED_DOCUMENT_TYPES.keys())

    @staticmethod
    def get_type_details(document_type: str) -> Dict[str, Any]:
        """Return details and key clauses for a document type."""
        return SUPPORTED_DOCUMENT_TYPES.get(
            document_type,
            SUPPORTED_DOCUMENT_TYPES["General Legal Agreement"]
        )

    def _build_system_instruction(self) -> str:
        """Construct the system prompt enforcing legal drafting standards and ethics."""
        return (
            "You are LegalEase AI, an expert legal drafting assistant specialized in drafting "
            "comprehensive, precise, and professionally structured legal agreements and documents.\n\n"
            "CRITICAL DRAFTING RULES & LEGAL SAFETY:\n"
            "1. DRAFTING ROLE ONLY: You draft documents for informational and drafting purposes only. "
            "Never claim or imply that the document is legally binding or valid in all jurisdictions without review.\n"
            "2. NO INVENTED FACTS OR CITATIONS: Never invent case citations, fictitious statutory references, "
            "or factual data not provided by the user.\n"
            "3. USE VISIBLE PLACEHOLDERS: Whenever a critical piece of information is omitted or unknown "
            "(such as party addresses, governing state/jurisdiction, specific monetary figures, or notification emails), "
            "clearly denote it in uppercase brackets, e.g.: [INSERT GOVERNING JURISDICTION], [INSERT PARTY A ADDRESS], "
            "[INSERT EFFECTIVE DATE], [INSERT NOTICE EMAIL].\n"
            "4. PROFESSIONAL STRUCTURE: Organize the document using standard legal hierarchy:\n"
            "   - Formal Document Title (in ALL CAPS)\n"
            "   - Preamble and Recitals (Whereas clauses, if applicable)\n"
            "   - Clear Definitions (where appropriate)\n"
            "   - Numbered, Titled Sections (e.g., 1. DEFINITIONS, 2. SCOPE OF SERVICES, 3. PAYMENT TERMS)\n"
            "   - Sub-clauses (1.1, 1.2, etc.) for readability and precision\n"
            "   - Standard Protective Covenants: Representations & Warranties, Term & Termination, "
            "Confidentiality, Dispute Resolution (Mediation/Arbitration/Litigation), Governing Law, "
            "Severability, Entire Agreement, and Notices.\n"
            "   - Formal Signature Block with lines for Signatures, Printed Names, Titles, and Dates for each party.\n"
            "5. TONE & CLARITY: Maintain an objective, formal, balanced, and authoritative legal tone. "
            "Do not include commentary, conversational remarks, preamble chit-chat, or markdown conversational wrappers. "
            "Output the document text directly."
        )

    def _build_user_prompt(
        self,
        document_type: str,
        parties: str,
        terms: str,
        dates: str
    ) -> str:
        """Construct the prompt containing document specifics and custom terms."""
        type_info = self.get_type_details(document_type)
        key_clauses_list = "\n- ".join(type_info.get("key_clauses", []))

        prompt = (
            f"Draft a complete, professional, ready-to-customize {document_type}.\n\n"
            f"PARTIES INVOLVED:\n{parties.strip()}\n\n"
            f"EFFECTIVE DATE / TIMELINE:\n{dates.strip()}\n\n"
            f"KEY TERMS, CONDITIONS, & REQUIREMENTS:\n{terms.strip()}\n\n"
            f"RECOMMENDED CLAUSES TO INCLUDE FOR THIS DOCUMENT TYPE:\n- {key_clauses_list}\n\n"
            f"INSTRUCTIONS:\n"
            f"- Fully incorporate all specific requirements, obligations, and terms stated above.\n"
            f"- Use numbered clauses (1., 1.1, 2., etc.).\n"
            f"- Insert clearly marked placeholders [INSERT ...] for any missing operational or legal details.\n"
            f"- Provide a complete, professional signature block at the end.\n"
            f"- Output ONLY the final legal document text with no introductory or concluding chat remarks."
        )
        return prompt

    def generate_document(
        self,
        document_type: str,
        parties: str,
        terms: str,
        dates: str
    ) -> str:
        """Generate a complete legal document using Gemini.

        Args:
            document_type: The type of legal document to generate.
            parties: Names and roles of the parties.
            terms: The key terms, clauses, and conditions.
            dates: The effective date or term duration.

        Returns:
            The generated legal document text.

        Raises:
            ValueError: If input validation fails or API key is missing.
            RuntimeError: If the Gemini API call fails.
        """
        # Validate inputs
        if not document_type or not document_type.strip():
            raise ValueError("Document type is required.")
        if not parties or not parties.strip():
            raise ValueError("Parties information is required.")
        if not terms or not terms.strip():
            raise ValueError("Key terms and conditions are required.")
        if not dates or not dates.strip():
            raise ValueError("Dates or term duration is required.")

        client = self._get_client()
        system_instruction = self._build_system_instruction()
        user_prompt = self._build_user_prompt(
            document_type=document_type,
            parties=parties,
            terms=terms,
            dates=dates,
        )

        logger.info(f"Generating '{document_type}' using model '{self.model}'")

        # Candidate models to try in sequence for maximum resilience
        candidate_models = [self.model]
        for m in ["gemini-3.8-flash", "gemma-4-26b-a4b-it", "gemma-4-31b-it", "gemini-3.5-flash-lite"]:
            if m not in candidate_models:
                candidate_models.append(m)

        last_error = None

        for model_candidate in candidate_models:
            try:
                logger.info(f"Attempting document generation with model '{model_candidate}'")
                response = client.models.generate_content(
                    model=model_candidate,
                    contents=user_prompt,
                    config={
                        "system_instruction": system_instruction,
                        "temperature": 0.2,  # Low temperature for formal, deterministic legal drafting
                        "max_output_tokens": 8192,
                    }
                )

                if response and response.text and response.text.strip():
                    document_text = response.text.strip()
                    # Clean any leading/trailing markdown code blocks if the model wrapped it
                    if document_text.startswith("```markdown"):
                        document_text = document_text[len("```markdown"):].strip()
                    elif document_text.startswith("```"):
                        document_text = document_text[len("```"):].strip()
                    if document_text.endswith("```"):
                        document_text = document_text[:-3].strip()

                    return document_text

            except Exception as e:
                err_msg = str(e)
                logger.warning(f"Model '{model_candidate}' attempt failed: {err_msg}")
                last_error = e
                # If invalid key, fail immediately without trying remaining models
                if "API_KEY_INVALID" in err_msg or "invalid api key" in err_msg.lower():
                    raise ValueError("The provided Gemini API key is invalid. Please check your credentials.")
                continue

        # If all candidates failed, surface a clean error
        err_str = str(last_error) if last_error else "Unknown error"
        if "RESOURCE_EXHAUSTED" in err_str or "rate limit" in err_str.lower():
            raise RuntimeError("Gemini API rate limit exceeded. Please wait a moment and try again.")
        raise RuntimeError(f"Failed to generate legal document: {err_str}")
