"""
frontend/app.py

Streamlit UI for LegalEase. Collects document details, calls the FastAPI
backend to generate the document via Gemini, and lets the user preview,
edit, and download it as .txt / .docx / .pdf.

Run with:  streamlit run frontend/app.py
(Make sure the FastAPI backend is already running on BACKEND_URL.)
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import streamlit as st

from config import BACKEND_URL, LOGO_PATH, APP_TITLE
from frontend.formatters import sanitize_text, format_docx, format_pdf, format_html_preview

st.set_page_config(page_title=APP_TITLE, page_icon="\u2696\ufe0f", layout="centered")

# ---- Header / Logo ----
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, use_container_width=True)
    else:
        st.markdown(f"<h1 style='text-align:center;'>{APP_TITLE}</h1>", unsafe_allow_html=True)

st.markdown(
    "<h4 style='text-align:center;color:#9aa0a6;'>AI Legal Document Generator</h4>",
    unsafe_allow_html=True,
)
st.divider()

# ---- Session state defaults ----
if "generated_text" not in st.session_state:
    st.session_state.generated_text = ""
if "show_edit" not in st.session_state:
    st.session_state.show_edit = False
if "last_terms" not in st.session_state:
    st.session_state.last_terms = ""
if "last_doc_type" not in st.session_state:
    st.session_state.last_doc_type = ""

# ---- Input form ----
document_type = st.text_input(
    "Document Type (Ex: Agreement, Contract, NDA)",
    placeholder="Freelance Work Contract",
)
parties = st.text_area(
    "Parties Involved",
    placeholder="Jane Doe (Service Provider), TechNova Inc. (Client)",
    height=80,
)
terms = st.text_area(
    "Terms & Conditions (Use semicolons for bullet points)",
    placeholder="Payment within 30 days of invoice; Confidentiality must be maintained; Either party may terminate with 15 days notice",
    height=110,
)
dates = st.text_input("Effective Date", placeholder="April 15, 2025")

generate_clicked = st.button("Generate Document", type="primary")

# ---- Generate ----
if generate_clicked:
    if not (document_type and parties and terms and dates):
        st.warning("Please fill in all fields before generating the document.")
    else:
        with st.spinner("Generating your legal document with Gemini..."):
            try:
                response = requests.post(
                    f"{BACKEND_URL}/generate",
                    json={
                        "document_type": document_type,
                        "parties": parties,
                        "terms": terms,
                        "dates": dates,
                    },
                    timeout=60,
                )
                if response.status_code == 200:
                    st.session_state.generated_text = sanitize_text(response.json()["document"])
                    st.session_state.last_terms = terms
                    st.session_state.last_doc_type = document_type
                    st.session_state.show_edit = False
                    st.success("Document Generated Successfully!")
                else:
                    detail = response.json().get("detail", response.text)
                    st.error(f"Backend error ({response.status_code}): {detail}")
            except requests.exceptions.ConnectionError:
                st.error(
                    "Could not reach the backend API. Make sure it's running "
                    f"at {BACKEND_URL} (see the README's 'Running the App' section)."
                )
            except requests.exceptions.Timeout:
                st.error("The request timed out. Please try again.")

# ---- Preview / Edit / Download ----
if st.session_state.generated_text:
    st.markdown(
        f"""
        <div style='background-color:#111418;border:1px solid #2a2f36;
                    border-radius:8px;padding:20px;max-height:420px;
                    overflow-y:auto;color:#e6e6e6;'>
            {format_html_preview(st.session_state.generated_text)}
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("\u270f\ufe0f Click to Edit Document"):
        st.session_state.show_edit = not st.session_state.show_edit

    if st.session_state.show_edit:
        edited_text = st.text_area(
            "Edit Document Below:",
            st.session_state.generated_text,
            height=300,
        )
        st.session_state.generated_text = edited_text

    st.divider()
    st.subheader("Download")

    file_stub = (st.session_state.last_doc_type or document_type or "legal_document")
    file_stub = file_stub.strip().lower().replace(" ", "_") or "legal_document"

    dl_col1, dl_col2, dl_col3 = st.columns(3)
    with dl_col1:
        st.download_button(
            "\U0001F4C4 Download as .TXT",
            data=st.session_state.generated_text,
            file_name=f"{file_stub}.txt",
            mime="text/plain",
        )
    with dl_col2:
        st.download_button(
            "\U0001F4DD Download as .DOCX",
            data=format_docx(
                st.session_state.generated_text,
                st.session_state.last_doc_type or document_type,
                st.session_state.last_terms or terms,
            ),
            file_name=f"{file_stub}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
    with dl_col3:
        st.download_button(
            "\U0001F4C4 Download as .PDF",
            data=format_pdf(
                st.session_state.generated_text,
                st.session_state.last_doc_type or document_type,
                st.session_state.last_terms or terms,
            ),
            file_name=f"{file_stub}.pdf",
            mime="application/pdf",
        )
else:
    st.info("Fill in the details above and click 'Generate Document' to start.")
