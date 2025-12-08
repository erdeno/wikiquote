# Backend Dockerfile
FROM python:3.10-slim

# Set working directory
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

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ /app/backend/
COPY services/ /app/services/
COPY manage.py /app/
COPY db.sqlite3 /app/
COPY speaker_embeddings.json /app/
COPY tts_preferences.json /app/
COPY pretrained_models/ /app/pretrained_models/

# Create necessary directories
RUN mkdir -p /app/backend/media /app/backend/static

# Set Python path
ENV PYTHONPATH=/app:$PYTHONPATH

# Expose port
EXPOSE 8000

# Run migrations and start server
CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
