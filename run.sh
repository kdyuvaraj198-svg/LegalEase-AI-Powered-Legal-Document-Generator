#!/usr/bin/env bash
# Convenience script: starts the FastAPI backend, waits for it to come up,
# then launches the Streamlit frontend. Press Ctrl+C to stop both.

set -e

echo "Starting FastAPI backend on http://127.0.0.1:8000 ..."
uvicorn legalEaseAPI.main:app --reload --port 8000 &
BACKEND_PID=$!

# Give the backend a moment to boot
sleep 3

echo "Starting Streamlit frontend on http://127.0.0.1:8501 ..."
streamlit run frontend/app.py

# When Streamlit exits, also stop the backend
kill $BACKEND_PID 2>/dev/null || true
