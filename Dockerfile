FROM python:3.12-slim

WORKDIR /app

# System dependencies for C-extensions (chromadb)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first (layer cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . .

# Make the startup script executable
RUN chmod +x start.sh

EXPOSE 8000

# start.sh: runs ingest.py on first boot (if chroma_db is missing),
# then launches uvicorn. Runtime env vars (GOOGLE_API_KEY etc.)
# are injected by Render at container start — no build-time secrets needed.
CMD ["./start.sh"]
