"""
frontend/formatters.py

Utility functions that turn raw AI-generated text into:
 - sanitized plain text
 - a branded .docx file (python-docx)
 - a branded .pdf file (fpdf2)
 - a styled HTML preview block (for Streamlit)
"""

import io
import os
import re
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from fpdf import FPDF

from config import LOGO_PATH, COMPANY_FOOTER, APP_TITLE


# --------------------------------------------------------------------------
# Text sanitization
# --------------------------------------------------------------------------
def sanitize_text(text: str) -> str:
    """Removes special/typographic characters that break PDF/DOCX rendering."""
    if not text:
        return ""
    replacements = {
        "\u2018": "'", "\u2019": "'",
        "\u201c": '"', "\u201d": '"',
        "\u2013": "-", "\u2014": "-",
        "\u2026": "...",
        "\u00a0": " ",
    }
    for bad, good in replacements.items():
        text = text.replace(bad, good)
    # Strip any remaining non-latin1 characters (fpdf's classic mode needs latin-1)
    text = text.encode("latin-1", "ignore").decode("latin-1")
    return text.strip()


def _split_terms(terms_line: str):
    """Splits a semicolon-separated terms string into a clean list."""
    parts = [t.strip(" -\u2022") for t in re.split(r"[;\n]", terms_line) if t.strip()]
    return parts


def _extract_title(text: str, fallback: str) -> str:
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("##"):
            return line.lstrip("#").strip()
        if line:
            return line[:80]
    return fallback


# --------------------------------------------------------------------------
# DOCX export
# --------------------------------------------------------------------------
def format_docx(text: str, doc_type: str, terms: str = "") -> bytes:
    """
    Builds a formatted Word document: logo header, Times New Roman body,
    optional terms table, and a footer. Returns raw bytes for download.
    """
    text = sanitize_text(text)
    doc = Document()

    # Default font
    style = doc.styles["Normal"]
    style.font.name = "Times New Roman"
    style.font.size = Pt(11)

    # Logo (centered) if available
    if os.path.exists(LOGO_PATH):
        try:
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run()
            run.add_picture(LOGO_PATH, width=Inches(1.8))
        except Exception:
            pass

    title = _extract_title(text, doc_type)
    title_para = doc.add_heading(title, level=1)
    title_para.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Body: turn each non-empty line into a paragraph; bold numbered section headings
    section_heading_re = re.compile(r"^(\d+\.\s+.+|##.*|\*\*.+\*\*)$")
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("##"):
            continue  # already used as the title
        clean_line = line.strip("*")
        para = doc.add_paragraph()
        run = para.add_run(clean_line)
        if section_heading_re.match(line) or re.match(r"^\d+\.\s+[A-Z]", line):
            run.bold = True
            run.font.size = Pt(12)

    # Terms table
    term_items = _split_terms(terms) if terms else []
    if term_items:
        doc.add_heading("Summary of Terms", level=2)
        table = doc.add_table(rows=1, cols=2)
        table.style = "Light Grid Accent 1"
        hdr = table.rows[0].cells
        hdr[0].text = "#"
        hdr[1].text = "Term"
        for i, term in enumerate(term_items, start=1):
            row = table.add_row().cells
            row[0].text = str(i)
            row[1].text = term

    # Footer
    section = doc.sections[0]
    footer = section.footer
    footer_para = footer.paragraphs[0] if footer.paragraphs else footer.add_paragraph()
    footer_para.text = COMPANY_FOOTER
    footer_para.alignment = WD_ALIGN_PARAGRAPH.CENTER

    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer.getvalue()


# --------------------------------------------------------------------------
# PDF export
# --------------------------------------------------------------------------
class LegalPDF(FPDF):
    def header(self):
        if os.path.exists(LOGO_PATH):
            try:
                self.image(LOGO_PATH, x=(self.w - 40) / 2, y=8, w=40)
                self.set_y(28)
            except Exception:
                self.set_y(10)
        else:
            self.set_y(10)
        self.set_font("Helvetica", "B", 14)
        self.cell(0, 8, APP_TITLE, align="C", ln=True)
        self.ln(2)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, sanitize_text(COMPANY_FOOTER), align="C")


def format_pdf(text: str, doc_type: str, terms: str = "") -> bytes:
    """Builds a branded PDF with header/footer and bullet-style terms."""
    text = sanitize_text(text)
    pdf = LegalPDF()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    title = _extract_title(text, doc_type)
    pdf.set_font("Helvetica", "B", 16)
    pdf.multi_cell(0, 10, sanitize_text(title), align="C")
    pdf.ln(4)

    section_heading_re = re.compile(r"^(\d+\.\s+[A-Za-z]|##|\*\*)")
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("##"):
            continue
        clean_line = line.strip("*")
        if section_heading_re.match(line):
            pdf.set_font("Helvetica", "B", 12)
            pdf.ln(2)
            pdf.multi_cell(0, 7, clean_line)
        else:
            pdf.set_font("Helvetica", "", 11)
            pdf.multi_cell(0, 6, clean_line)

    term_items = _split_terms(terms) if terms else []
    if term_items:
        pdf.ln(4)
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, "Summary of Terms", ln=True)
        pdf.set_font("Helvetica", "", 11)
        for term in term_items:
            pdf.multi_cell(0, 6, f"- {term}")

    # fpdf2 returns a bytearray with dest='S'
    output = pdf.output(dest="S")
    if isinstance(output, str):
        output = output.encode("latin-1")
    return bytes(output)


# --------------------------------------------------------------------------
# HTML preview (for Streamlit)
# --------------------------------------------------------------------------
def format_html_preview(text: str) -> str:
    """Converts raw AI text into a styled HTML block for inline preview."""
    if not text:
        return "<p><em>No content generated yet.</em></p>"

    html_lines = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            html_lines.append("<br>")
            continue
        if line.startswith("##"):
            html_lines.append(f"<h3 style='color:#f5c518;margin-top:0;'>{line.lstrip('#').strip()}</h3>")
        elif re.match(r"^\d+\.\s+", line):
            clean = line.strip("*")
            html_lines.append(f"<p style='font-weight:600;margin-bottom:2px;'>{clean}</p>")
        elif line.startswith(("-", "\u2022")):
            html_lines.append(f"<li>{line.lstrip('-\u2022 ').strip()}</li>")
        else:
            clean = line.replace("**", "")
            html_lines.append(f"<p style='margin:4px 0;'>{clean}</p>")

    return "\n".join(html_lines)
