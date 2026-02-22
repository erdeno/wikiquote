FROM python:3.10-slim

WORKDIR /app

# Install system dependencies (added libpq-dev for PostgreSQL)
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    ffmpeg \
    libsndfile1 \
    git \
    curl \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip==23.3.1 setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt gunicorn

# Copy application code
COPY backend/ /app/backend/
COPY services/ /app/services/
COPY manage.py /app/

# Create necessary files and directories (removed db.sqlite3 creation)
RUN echo '{}' > /app/speaker_embeddings.json && \
    echo '{}' > /app/tts_preferences.json && \
    mkdir -p /app/backend/media /app/backend/static /app/backend/staticfiles /root/.cache/huggingface

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=backend.settings

# Expose port
EXPOSE 8000

# Start without setup_neo4j command (constraints created automatically on first use)
CMD ["gunicorn", "backend.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "120", "--log-level", "debug"]
