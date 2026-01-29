# OPAL Orchestrator Backend Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directories
RUN mkdir -p /app/data/db /app/data/pdfs /app/data/chroma

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8000

# Set default workers (can be overridden at runtime)
ENV WEB_WORKERS=4

# Create entrypoint script for variable substitution
RUN echo '#!/bin/sh\nuvicorn app.main:app \\\n  --host 0.0.0.0 \\\n  --port 8000 \\\n  --workers ${WEB_WORKERS:-4} \\\n  --loop uvloop \\\n  --http httptools \\\n  --access-log' > /entrypoint.sh && chmod +x /entrypoint.sh

# Run the application with proper concurrency settings
ENTRYPOINT ["/entrypoint.sh"]
