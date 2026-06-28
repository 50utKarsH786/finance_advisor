#!/bin/bash
set -e

# ── Startup Script for Render Free Tier ──────────────────────────────────────
# Render free tier has no persistent disk, so we run ingest.py on first boot.
# The container filesystem persists between requests (not serverless),
# so ingest only re-runs when Render redeploys the container.
# ─────────────────────────────────────────────────────────────────────────────

CHROMA_DIR="${CHROMA_DIR:-chroma_db}"

if [ ! -d "$CHROMA_DIR" ] || [ -z "$(ls -A $CHROMA_DIR 2>/dev/null)" ]; then
    echo "========================================="
    echo " ChromaDB not found. Running ingest.py..."
    echo "========================================="
    python ingest.py
    echo "========================================="
    echo " Ingest complete. Starting API server..."
    echo "========================================="
else
    echo "ChromaDB found at '$CHROMA_DIR'. Skipping ingest."
fi

# Start the FastAPI server
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
