"""
ai_core/gemini_generator.py

Wraps the Google Generative AI (Gemini) SDK and turns structured user
input (document type, parties, terms, dates) into a complete, well
formatted legal document as plain text (Markdown-ish headings).
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import google.generativeai as genai
from config import GEMINI_API_KEY, GEMINI_MODEL


class GeminiDocumentGenerator:
    """Generates legal documents using Google's Gemini model."""

    def __init__(self, api_key: str = None, model_name: str = None):
        self.api_key = api_key or GEMINI_API_KEY
        self.model_name = model_name or GEMINI_MODEL
        self._configured = False
        self.model = None

        if self.api_key:
            self._configure()

    def _configure(self):
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(self.model_name)
        self._configured = True

    def _build_prompt(self, document_type: str, parties: str, terms: str, dates: str) -> str:
        return (
            f"You are an expert contract lawyer. Generate a comprehensive, "
            f"professionally formatted legal document titled '{document_type}'.\n\n"
            f"Involved Parties: {parties}\n"
            f"Effective Date: {dates}\n"
            f"Terms and Conditions to incorporate: {terms}\n\n"
            "Requirements:\n"
            "- Use a clear document title as a level-2 markdown heading (## Title).\n"
            "- Include an opening recital paragraph naming the parties and the effective date.\n"
            "- Organize the body into numbered sections with bold section headings "
            "(e.g. '1. Services', '2. Term and Termination', '3. Payment', "
            "'4. Confidentiality', '5. Governing Law', etc.) appropriate to the document type.\n"
            "- Weave the given terms and conditions into the relevant sections.\n"
            "- End with a signature block for each party.\n"
            "- Use formal legal language, but keep placeholders like [State] or [Address] "
            "in brackets when information wasn't provided.\n"
            "- Do not include any commentary outside of the document itself."
        )

    def generate_document(self, document_type: str, parties: str, terms: str, dates: str) -> str:
        """
        Calls the Gemini model to generate the legal document text.
        Raises a RuntimeError with a friendly message on failure.
        """
        if not self.api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is not configured. Add it to your .env file and restart the server."
            )
        if not self._configured:
            self._configure()

        prompt = self._build_prompt(document_type, parties, terms, dates)

        try:
            response = self.model.generate_content(prompt)
        except Exception as exc:  # network / auth / quota errors
            raise RuntimeError(f"Gemini API call failed: {exc}") from exc

        text = getattr(response, "text", None)
        if not text:
            # Some responses (e.g. blocked by safety filters) have no .text
            raise RuntimeError(
                "Gemini returned an empty response. Try rephrasing the terms or document type."
            )
        return text.strip()
