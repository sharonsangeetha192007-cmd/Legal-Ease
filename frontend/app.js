/**
 * LegalEase — AI-Powered Legal Document Generator
 * Frontend Application Logic
 */

document.addEventListener("DOMContentLoaded", () => {
  // DOM Elements - Form
  const documentForm = document.getElementById("documentForm");
  const documentTypeSelect = document.getElementById("documentType");
  const partiesTextarea = document.getElementById("parties");
  const datesInput = document.getElementById("dates");
  const datePickerHelper = document.getElementById("datePickerHelper");
  const termsTextarea = document.getElementById("terms");
  const generateBtn = document.getElementById("generateBtn");
  const btnText = generateBtn.querySelector(".btn-text");
  const btnLoading = generateBtn.querySelector(".btn-loading");
  const samplePresetSelect = document.getElementById("samplePreset");
  const partiesCharCount = document.getElementById("partiesCharCount");
  const termsCharCount = document.getElementById("termsCharCount");
  const typeHint = document.getElementById("typeHint");

  // DOM Elements - Editor
  const editorDocumentTitle = document.getElementById("editorDocumentTitle");
  const emptyState = document.getElementById("emptyState");
  const loadingState = document.getElementById("loadingState");
  const documentEditor = document.getElementById("documentEditor");
  const wordCountBadge = document.getElementById("wordCountBadge");
  const charCountBadge = document.getElementById("charCountBadge");
  const copyBtn = document.getElementById("copyBtn");
  const regenerateBtn = document.getElementById("regenerateBtn");
  const clearEditorBtn = document.getElementById("clearEditorBtn");
  const exportTxtBtn = document.getElementById("exportTxtBtn");
  const exportDocxBtn = document.getElementById("exportDocxBtn");
  const exportPdfBtn = document.getElementById("exportPdfBtn");

  // Health Badge
  const apiStatusBadge = document.getElementById("apiStatusBadge");
  const toastContainer = document.getElementById("toastContainer");

  // State
  let currentDocumentType = "";
  let lastGeneratedPayload = null;

  // Sample Presets for instantaneous 1-click test
  const SAMPLE_PRESETS = {
    nda: {
      type: "Non-Disclosure Agreement",
      parties: "Alpha Genesis Technologies Inc., a Delaware corporation (Disclosing Party), and Horizon Software Systems LLC, a California limited liability company (Receiving Party).",
      dates: "November 1, 2026, for a confidential term of 3 years",
      terms: "Disclosing Party will share proprietary source code, architectural blueprints, AI model training datasets, and customer pipeline data in connection with exploring a potential joint venture. Receiving Party covenants to preserve strict confidentiality, use reasonable degree of care, restrict access strictly to designated engineers with a need to know, not reverse-engineer, and promptly destroy or return all materials upon written request.",
    },
    contractor: {
      type: "Freelance/Independent Contractor Agreement",
      parties: "Vanguard Media Group LLC (Client) and Jane Doe, d/b/a Doe Creative Studio (Contractor).",
      dates: "Effective October 15, 2026 until completion of milestone deliverables or December 31, 2026",
      terms: "Contractor to design and deliver full brand identity package, UI design system in Figma, and marketing collateral. Total fixed compensation is $18,500 payable in three milestone installments (30% deposit, 40% on draft delivery, 30% upon final acceptance). Contractor retains independent contractor status. All work product shall constitute work-made-for-hire with complete IP assignment to Client upon final payment. Either party may terminate with 14 days written notice.",
    },
    lease: {
      type: "Rental/Lease Agreement",
      parties: "Highland Real Estate Holdings LP (Landlord) and Nexus Analytics Inc. (Tenant).",
      dates: "January 1, 2027 through December 31, 2029 (36-month term)",
      terms: "Lease of commercial office Suite 400 at 500 Financial Plaza, San Francisco, CA. Base monthly rent of $12,500 payable on the 1st of each month. Security deposit of $25,000 held in escrow. Permitted use: commercial tech office and administration. Landlord responsible for structural maintenance and HVAC; Tenant responsible for utilities and interior upkeep. No subletting without prior written consent.",
    },
    employment: {
      type: "Employment Agreement",
      parties: "Quantum Dynamics Corp. (Employer) and Marcus Sterling (Employee).",
      dates: "Starting November 1, 2026, full-time employment",
      terms: "Position: Principal Systems Architect reporting to the VP of Engineering. Annual base salary of $210,000 paid bi-weekly, plus eligibility for annual 20% performance bonus and standard healthcare, 401(k) matching, and 20 days paid PTO. At-will employment relationship. Mandatory proprietary information and inventions assignment agreement. Post-termination non-solicitation of employees and customers for 12 months.",
    },
  };

  // 1. Initial Health Check
  async function checkHealth() {
    try {
      const res = await fetch("/api/health");
      if (res.ok) {
        apiStatusBadge.classList.add("online");
        apiStatusBadge.classList.remove("offline");
        apiStatusBadge.querySelector(".status-label").textContent = "API Ready";
      } else {
        throw new Error("Unhealthy response");
      }
    } catch (err) {
      apiStatusBadge.classList.remove("online");
      apiStatusBadge.classList.add("offline");
      apiStatusBadge.querySelector(".status-label").textContent = "API Offline";
    }
  }
  checkHealth();

  // 2. Character Counters
  partiesTextarea.addEventListener("input", () => {
    partiesCharCount.textContent = `${partiesTextarea.value.length} / 1500`;
  });

  termsTextarea.addEventListener("input", () => {
    termsCharCount.textContent = `${termsTextarea.value.length} / 10000`;
  });

  // 3. Date Picker Sync
  datePickerHelper.addEventListener("change", (e) => {
    if (e.target.value) {
      const selected = new Date(e.target.value);
      const formatted = selected.toLocaleDateString("en-US", {
        year: "numeric",
        month: "long",
        day: "numeric",
      });
      datesInput.value = formatted;
    }
  });

  // 4. Sample Preset Selector
  samplePresetSelect.addEventListener("change", (e) => {
    const key = e.target.value;
    if (!key || !SAMPLE_PRESETS[key]) return;

    const data = SAMPLE_PRESETS[key];
    documentTypeSelect.value = data.type;
    partiesTextarea.value = data.parties;
    datesInput.value = data.dates;
    termsTextarea.value = data.terms;

    // Trigger input events to update counters
    partiesTextarea.dispatchEvent(new Event("input"));
    termsTextarea.dispatchEvent(new Event("input"));

    showToast(`Loaded sample preset for ${data.type}`, "info");
  });

  // 5. Update Metrics (Word count and character count)
  function updateEditorMetrics() {
    const text = documentEditor.value;
    const words = text.trim() ? text.trim().split(/\s+/).length : 0;
    const chars = text.length;

    wordCountBadge.textContent = `${words.toLocaleString()} words`;
    charCountBadge.textContent = `${chars.toLocaleString()} chars`;
  }

  documentEditor.addEventListener("input", updateEditorMetrics);

  // 6. UI State Management
  function setGenerating(isGenerating) {
    if (isGenerating) {
      generateBtn.disabled = true;
      regenerateBtn.disabled = true;
      btnText.classList.add("hidden");
      btnLoading.classList.remove("hidden");
      emptyState.classList.add("hidden");
      documentEditor.classList.add("hidden");
      loadingState.classList.remove("hidden");
    } else {
      generateBtn.disabled = false;
      regenerateBtn.disabled = false;
      btnText.classList.remove("hidden");
      btnLoading.classList.add("hidden");
      loadingState.classList.add("hidden");
    }
  }

  function setDocumentContent(content, docType) {
    currentDocumentType = docType || "Legal Document";
    editorDocumentTitle.textContent = currentDocumentType;
    documentEditor.value = content;
    emptyState.classList.add("hidden");
    loadingState.classList.add("hidden");
    documentEditor.classList.remove("hidden");
    updateEditorMetrics();
  }

  // 7. Generate Document Submission
  documentForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const docType = documentTypeSelect.value;
    const parties = partiesTextarea.value.trim();
    const dates = datesInput.value.trim();
    const terms = termsTextarea.value.trim();

    // Validation
    if (!docType) {
      showToast("Please select a document type.", "error");
      documentTypeSelect.focus();
      return;
    }
    if (!parties) {
      showToast("Please specify the contracting parties.", "error");
      partiesTextarea.focus();
      return;
    }
    if (!dates) {
      showToast("Please enter an effective date or duration.", "error");
      datesInput.focus();
      return;
    }
    if (!terms) {
      showToast("Please provide the key terms and conditions.", "error");
      termsTextarea.focus();
      return;
    }

    const payload = {
      document_type: docType,
      parties: parties,
      dates: dates,
      terms: terms,
    };

    lastGeneratedPayload = payload;
    setGenerating(true);

    try {
      const response = await fetch("/api/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Failed to generate legal document.");
      }

      setDocumentContent(data.document, data.document_type);
      showToast("Document generated successfully. Please review and edit before using.", "success");

      // Smooth scroll to editor on smaller screens
      if (window.innerWidth < 1080) {
        documentEditor.scrollIntoView({ behavior: "smooth" });
      }
    } catch (err) {
      showToast(err.message || "We couldn't generate the document right now. Please check your inputs and try again.", "error");
      if (!documentEditor.value) {
        emptyState.classList.remove("hidden");
      } else {
        documentEditor.classList.remove("hidden");
      }
    } finally {
      setGenerating(false);
    }
  });

  // 8. Regenerate Button
  regenerateBtn.addEventListener("click", () => {
    if (!lastGeneratedPayload) {
      showToast("Please fill in the form and click Generate first.", "info");
      return;
    }
    // Re-trigger submit
    documentForm.dispatchEvent(new Event("submit"));
  });

  // 9. Clear Editor Button
  clearEditorBtn.addEventListener("click", () => {
    if (confirm("Are you sure you want to clear the editor?")) {
      documentEditor.value = "";
      updateEditorMetrics();
      documentEditor.classList.add("hidden");
      emptyState.classList.remove("hidden");
      showToast("Editor cleared.", "info");
    }
  });

  // 10. Copy to Clipboard
  copyBtn.addEventListener("click", async () => {
    const text = documentEditor.value;
    if (!text.trim()) {
      showToast("No document content to copy.", "error");
      return;
    }
    try {
      await navigator.clipboard.writeText(text);
      showToast("Legal document copied to clipboard.", "success");
    } catch (err) {
      // Fallback
      documentEditor.select();
      document.execCommand("copy");
      showToast("Legal document copied to clipboard.", "success");
    }
  });

  // 11. Document Export Handler (TXT, DOCX, PDF)
  async function handleExport(format) {
    const content = documentEditor.value.trim();
    if (!content) {
      showToast("No document content to export. Please generate or enter a document first.", "error");
      return;
    }

    const docType = currentDocumentType || documentTypeSelect.value || "Legal Document";

    showToast(`Preparing ${format.toUpperCase()} export...`, "info");

    try {
      const response = await fetch("/api/export", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          document_content: content,
          document_type: docType,
          format: format,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Failed to export as ${format.toUpperCase()}.`);
      }

      // Download file blob
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.style.display = "none";
      a.href = url;

      // Extract filename from Content-Disposition header if available
      const disposition = response.headers.get("Content-Disposition");
      let filename = `${docType.toLowerCase().replace(/[^a-z0-9_-]/g, "_")}.${format}`;
      if (disposition && disposition.indexOf("filename=") !== -1) {
        const matches = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/.exec(disposition);
        if (matches != null && matches[1]) {
          filename = matches[1].replace(/['"]/g, "");
        }
      }

      a.download = filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      showToast(`Downloaded ${filename} successfully!`, "success");
    } catch (err) {
      showToast(err.message || `Export failed for ${format.toUpperCase()}.`, "error");
    }
  }

  exportTxtBtn.addEventListener("click", () => handleExport("txt"));
  exportDocxBtn.addEventListener("click", () => handleExport("docx"));
  exportPdfBtn.addEventListener("click", () => handleExport("pdf"));

  // 12. Toast Notification Function
  function showToast(message, type = "info") {
    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;

    let icon = "";
    if (type === "success") {
      icon = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>`;
    } else if (type === "error") {
      icon = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#ef4444" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>`;
    } else {
      icon = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#d97706" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>`;
    }

    toast.innerHTML = `
      ${icon}
      <span class="toast-message">${message}</span>
    `;

    toastContainer.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = "0";
      toast.style.transform = "translateY(10px)";
      setTimeout(() => toast.remove(), 250);
    }, 4500);
  }
});
