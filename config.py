"""
config.py
Central configuration for the LegalEase application.
Loads environment variables from .env and exposes them as constants.
"""

import os
from dotenv import load_dotenv

# Load variables from a .env file placed at the project root
load_dotenv()

# ---- Gemini / Generative AI settings ----
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-pro")

# ---- Backend settings ----
BACKEND_HOST = os.getenv("BACKEND_HOST", "0.0.0.0")
BACKEND_PORT = int(os.getenv("BACKEND_PORT", "8000"))
BACKEND_URL = os.getenv("BACKEND_URL", f"http://127.0.0.1:{BACKEND_PORT}")

# ---- Frontend / branding settings ----
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH = os.path.join(PROJECT_ROOT, "Image", "Logo.png")
INVERSE_LOGO_PATH = os.path.join(PROJECT_ROOT, "Image", "inverseLogo.png")
APP_TITLE = "LegalEase"
COMPANY_FOOTER = "LegalEase Inc. | contact@legalease.com | All Rights Reserved."

if not GEMINI_API_KEY:
    # We don't raise here so the backend can still start (e.g. for docs/testing),
    # but generation calls will fail with a clear error until the key is set.
    print(
        "[config] WARNING: GEMINI_API_KEY is not set. "
        "Create a .env file (see .env.example) and add your key before generating documents."
    )
