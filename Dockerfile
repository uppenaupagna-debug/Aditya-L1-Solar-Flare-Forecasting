# Production container for Aditya-L1 Mission Flight Operations API
FROM python:3.11-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency specifications and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code and create data directories
COPY src/ ./src/
RUN mkdir -p /app/data/processed

EXPOSE 8008

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8008}/health || exit 1

CMD ["sh", "-c", "uvicorn src.api.server:app --host 0.0.0.0 --port ${PORT:-8008}"]
