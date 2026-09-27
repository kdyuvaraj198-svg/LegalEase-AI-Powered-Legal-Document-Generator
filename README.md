# LegalEase — AI-Powered Legal Document Generator

Generates employment contracts, NDAs, lease agreements, and other legal
documents from simple inputs (document type, parties, terms, effective date)
using Google's Gemini model. Export as `.txt`, `.docx`, or `.pdf`.

**Stack:** FastAPI (backend) + Streamlit (frontend) + Google Generative AI (Gemini)

```
LegalEase/
├── ai_core/
│   └── gemini_generator.py     # Gemini prompt building + API calls
├── legalEaseAPI/
│   ├── main.py                 # FastAPI app entrypoint
│   └── routes.py               # /generate and /health endpoints
├── frontend/
│   ├── app.py                  # Streamlit UI
│   └── formatters.py           # sanitize / docx / pdf / html-preview helpers
├── Image/
│   ├── Logo.png                # used in UI header + docx/pdf branding
│   └── inverseLogo.png
├── config.py                   # loads .env, shared constants
├── requirements.txt
├── .env.example                # copy to .env and add your API key
└── run.sh                      # starts backend + frontend together
```

---

## 1. Prerequisites

- **Python 3.11 or 3.12** (recommended). Avoid Python 3.13/3.14 for now —
  they're very new, and some dependencies here (Pillow, pydantic-core, etc.)
  don't yet ship pre-built Windows wheels for them, which causes pip to try
  compiling from source and fail. Check your version with:
  ```bash
  python --version
  ```
  If you have multiple Python versions installed on Windows, target 3.12
  specifically when creating the venv:
  ```powershell
  py -3.12 -m venv venv
  ```
  If you don't have 3.11/3.12 installed, grab it from
  https://www.python.org/downloads/ (during install, check "Add python.exe to PATH").
- A free Gemini API key: https://aistudio.google.com/app/apikey
- VS Code (recommended) with the Python extension

---

## 2. VS Code Setup

1. Open the `LegalEase` folder in VS Code (`File > Open Folder...`).
2. Open a terminal in VS Code (`` Ctrl+` `` / `` Cmd+` ``).
3. Create and activate a virtual environment (use Python 3.11/3.12 — see
   Prerequisites above if you have multiple versions installed):

   **Windows (PowerShell):**
   ```powershell
   py -3.12 -m venv venv
   venv\Scripts\activate
   ```

   **macOS / Linux:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
   In VS Code, when prompted, select this `venv` as the Python interpreter
   (`Ctrl+Shift+P` → "Python: Select Interpreter").

4. Upgrade pip first, then install dependencies. This matters on Windows —
   an outdated pip can fail to find pre-built wheels for packages like
   `pydantic-core` or `Pillow` and try to compile them from source instead
   (which needs Rust + Visual Studio C++ Build Tools and usually fails):
   ```bash
   python -m pip install --upgrade pip setuptools wheel
   pip install -r requirements.txt
   ```

5. Create your `.env` file:
   ```bash
   cp .env.example .env      # macOS/Linux
   copy .env.example .env    # Windows
   ```
   Open `.env` and paste your real key:
   ```
   GEMINI_API_KEY=AIza...your_real_key...
   ```

---

## 3. Running the App

You need **two terminals** (or use the provided script) since the backend
and frontend are separate processes.

### Option A — one command (macOS/Linux)
```bash
./run.sh
```

### Option B — two terminals (works everywhere)

**Terminal 1 — Backend (FastAPI):**
```bash
uvicorn legalEaseAPI.main:app --reload --port 8000
```
You should see `Application startup complete.` and it will serve at
`http://127.0.0.1:8000`.

**Terminal 2 — Frontend (Streamlit):**
```bash
streamlit run frontend/app.py
```
This opens the UI automatically at `http://localhost:8501`.

---

## 4. Testing the Application

1. **Backend health check** — with the backend running, open
   `http://127.0.0.1:8000/docs` in a browser. You'll see interactive
   Swagger docs for `/generate` and `/health`. Try `/health` — it should
   return `{"status": "ok"}`.

2. **End-to-end test via the UI:**
   - Document Type: `Freelance Work Contract`
   - Parties Involved: `Jane Doe (Service Provider), TechNova Inc. (Client)`
   - Terms & Conditions: `Payment within 7 days of invoice; Confidentiality must be maintained; Either party may terminate with 15 days notice`
   - Effective Date: `April 15, 2025`
   - Click **Generate Document** → a formatted contract appears in the preview.
   - Click **Click to Edit Document** to tweak the text inline.
   - Download as **.TXT**, **.DOCX**, and **.PDF** and confirm each opens
     correctly, with the logo and footer present in the Word/PDF files.

3. **Direct API test (optional, via curl):**
   ```bash
   curl -X POST http://127.0.0.1:8000/generate \
     -H "Content-Type: application/json" \
     -d '{"document_type":"NDA","parties":"Alice, Bob","terms":"Confidentiality for 2 years","dates":"Jan 1, 2026"}'
   ```

---

## 5. Troubleshooting

| Problem | Fix |
|---|---|
| `Could not reach the backend API` in Streamlit | Make sure the FastAPI server (Terminal 1) is running on port 8000 before generating. |
| `GEMINI_API_KEY is not configured` | Check your `.env` file exists at the project root and has a valid key, then restart the backend. |
| PDF/DOCX missing the logo | Confirm `Image/Logo.png` exists — replace it with your own branding image any time (keep the filename `Logo.png`). |
| `ModuleNotFoundError` | Make sure your virtual environment is activated and `pip install -r requirements.txt` completed without errors. |
| `RequiredDependencyException`, `zlib`, or "does not support Python 3.14 / 3.13 and does not provide prebuilt Windows binaries" while installing Pillow | You're on too new a Python version. Install Python 3.12 from python.org, then recreate the venv with `py -3.12 -m venv venv` (delete the old `venv` folder first) and reinstall requirements. |
| `error: failed-wheel-build-for-install` / mentions of `maturin`, `cargo`, or "Visual Studio" while installing `pydantic-core` or `Pillow` | Your pip is trying to compile a package from source instead of downloading a pre-built wheel. Run `python -m pip install --upgrade pip setuptools wheel`, delete the `venv` folder, recreate it, and reinstall with `pip install -r requirements.txt`. This is almost always fixed by the pip upgrade alone — no need to install Rust or Visual Studio C++ Build Tools. |

---

## 6. Notes on the AI Model

The code defaults to `gemini-1.5-pro` (set via `GEMINI_MODEL` in `.env`).
If that model isn't available on your API key/tier, switch to a currently
available Gemini model name (check https://ai.google.dev/gemini-api/docs/models
for the latest list) and update `GEMINI_MODEL` in `.env` — no code changes needed.
