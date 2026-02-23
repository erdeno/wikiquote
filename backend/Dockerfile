FROM python:3.10-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc g++ ffmpeg libsndfile1 git curl libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy ONLY the dependency files first (better caching)
COPY pyproject.toml uv.lock ./

# We set the environment variable right before the command
# --no-install-project is optional but often faster if you copy code later
ENV UV_SYSTEM_PYTHON=1
RUN uv sync --frozen --no-cache

# Copy application code
COPY backend/ /app/backend/
COPY services/ /app/services/
COPY manage.py /app/

# Setup directories
RUN echo '{}' > /app/speaker_embeddings.json && \
    echo '{}' > /app/tts_preferences.json && \
    mkdir -p /app/backend/media /app/backend/static /app/backend/staticfiles /root/.cache/huggingface

# Add the virtual environment's bin folder to the PATH 
# so 'gunicorn' and 'python' commands find the uv-installed versions.
ENV PATH="/app/.venv/bin:$PATH"

# Copy application code
COPY . .

ENV PYTHONPATH=/app PYTHONUNBUFFERED=1 DJANGO_SETTINGS_MODULE=backend.settings
EXPOSE 8000

CMD ["/app/.venv/bin/gunicorn", "backend.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "120"]
