"""
legalEaseAPI/routes.py

Defines the /generate endpoint that accepts document details from the
Streamlit frontend and returns AI-generated legal text.
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ai_core.gemini_generator import GeminiDocumentGenerator

router = APIRouter()
gemini_generator = GeminiDocumentGenerator()


class DocumentRequest(BaseModel):
    document_type: str = Field(..., min_length=1, example="Freelance Work Contract")
    parties: str = Field(..., min_length=1, example="Jane Doe (Service Provider), TechNova Inc. (Client)")
    terms: str = Field(
        ...,
        min_length=1,
        example="Payment within 30 days; Confidentiality must be maintained; Either party may terminate with 15 days notice",
    )
    dates: str = Field(..., min_length=1, example="April 15, 2025")


class DocumentResponse(BaseModel):
    document: str


@router.post("/generate", response_model=DocumentResponse)
def generate_legal_document(request: DocumentRequest):
    """
    Accepts document details and returns the AI-generated legal document text.
    """
    try:
        response = gemini_generator.generate_document(
            request.document_type,
            request.parties,
            request.terms,
            request.dates,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc))
    except Exception as exc:  # unexpected errors
        raise HTTPException(status_code=500, detail=f"Unexpected error: {exc}")

    return {"document": response}


@router.get("/health")
def health_check():
    """Simple health check endpoint used to verify the backend is running."""
    return {"status": "ok"}
