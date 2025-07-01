# Dockerfile for Kinsta deployment
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Create app directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /app/

# Make scripts executable
RUN chmod +x runtime_init.sh build.sh 2>/dev/null || true

# Run build script
RUN ./build.sh

# Ensure static files are collected during build
RUN python manage.py collectstatic --noinput --clear || echo "Static collection will be retried at runtime"

# Create non-root user
RUN useradd --create-home --shell /bin/bash app && chown -R app:app /app
USER app

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8080/health/', timeout=10)" || exit 1

# Expose port
EXPOSE 8080

# Start with runtime initialization
ENTRYPOINT ["./runtime_init.sh"]
# Use sh -c to allow environment variable expansion
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-8080} --workers 2 --timeout 60 ethicic.wsgi:application"]