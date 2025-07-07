# Multi-stage Dockerfile for faster builds
FROM python:3.11-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy only dependency files first
WORKDIR /app
COPY pyproject.toml requirements.txt ./

# Install dependencies with uv (10-100x faster than pip)
RUN uv venv && \
    . .venv/bin/activate && \
    uv pip install -r requirements.txt

# Production stage
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8080
ENV PATH="/app/.venv/bin:$PATH"

# Install only runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy application code
COPY . /app/

# Make scripts executable
RUN chmod +x runtime_init.sh build.sh 2>/dev/null || true

# Create static directories
RUN mkdir -p staticfiles/css staticfiles/js staticfiles/images

# Create non-root user
RUN useradd --create-home --shell /bin/bash app && chown -R app:app /app
USER app

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8080/health/', timeout=10)" || exit 1

EXPOSE 8080

ENTRYPOINT ["./runtime_init.sh"]
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-8080} --workers 2 --timeout 60 --access-logfile - --error-logfile - ethicic.wsgi:application"]
