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

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy application code
COPY backend/ /app/backend/
COPY services/ /app/services/
COPY manage.py /app/

# Create necessary files and directories
RUN touch /app/db.sqlite3 && \
    echo '{}' > /app/speaker_embeddings.json && \
    echo '{}' > /app/tts_preferences.json && \
    mkdir -p /app/backend/media /app/backend/static /app/backend/staticfiles /root/.cache/huggingface

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=backend.settings

EXPOSE 8000

# Test Django can start before running gunicorn
CMD ["sh", "-c", "\
    echo '=== Starting Django Backend ===' && \
    echo 'PYTHONPATH='$PYTHONPATH && \
    echo 'Testing Python imports...' && \
    python -c 'import django; print(\"Django version:\", django.VERSION)' && \
    python -c 'import backend.settings; print(\"Settings loaded\")' && \
    echo 'Running migrations...' && \
    python manage.py migrate --noinput && \
    echo 'Migrations complete!' && \
    echo 'Starting Gunicorn...' && \
    exec gunicorn backend.wsgi:application \
        --bind 0.0.0.0:8000 \
        --workers 2 \
        --timeout 120 \
        --log-level debug \
        --access-logfile - \
        --error-logfile - \
"]
