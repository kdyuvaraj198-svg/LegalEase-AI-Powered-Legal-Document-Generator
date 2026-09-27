"""
legalEaseAPI/main.py

Entry point for the LegalEase FastAPI backend.
Run directly with: python -m legalEaseAPI.main
or via uvicorn:      uvicorn legalEaseAPI.main:app --reload
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from legalEaseAPI.routes import router

app = FastAPI(
    title="LegalEase - AI Legal Document Generator",
    description="Backend API that generates legal documents using Google's Gemini model.",
    version="1.0.0",
)

# Allow the Streamlit frontend (running on a different port) to call this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the /generate and /health routes
app.include_router(router)


@app.get("/")
def home():
    return {"message": "Welcome to LegalEase AI Legal Document Generator API"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("legalEaseAPI.main:app", host="0.0.0.0", port=8000, reload=True)
