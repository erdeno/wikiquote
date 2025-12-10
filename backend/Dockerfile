FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    ffmpeg \
    libsndfile1 \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy application code
COPY backend/ /app/backend/
COPY services/ /app/services/
COPY manage.py /app/

# Create necessary directories and files
RUN mkdir -p /app/backend/staticfiles /root/.cache/huggingface && \
    echo '{}' > /app/speaker_embeddings.json && \
    echo '{}' > /app/tts_preferences.json

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=backend.settings

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/quotes/search/?q=test || exit 1

# Start command (no migrations needed - using Neo4j only)
CMD ["sh", "-c", "python manage.py setup_neo4j && gunicorn backend.wsgi:application --bind 0.0.0.0:8000 --workers 2 --timeout 120 --log-level debug"]
