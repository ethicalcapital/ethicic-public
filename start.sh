#!/bin/bash
# Simple start script for Nixpacks
set -e

echo "🚀 Starting application..."

# Ensure PORT is set (Kinsta provides this)
if [ -z "$PORT" ]; then
    echo "⚠️  PORT not set, defaulting to 8080"
    export PORT=8080
fi

echo "📍 PORT is set to: $PORT"
echo "📍 Environment check:"
echo "   - PATH: $PATH"
echo "   - PWD: $(pwd)"
echo "   - USER: $(whoami 2>/dev/null || echo 'unknown')"

# Ensure runtime init script is executable
chmod +x runtime_init.sh 2>/dev/null || true

# Check if gunicorn is available
if command -v gunicorn &> /dev/null; then
    echo "✅ Gunicorn found at: $(which gunicorn)"
    # Start with runtime initialization - use explicit port
    exec ./runtime_init.sh gunicorn --bind 0.0.0.0:${PORT} --workers 2 --timeout 60 --access-logfile - --error-logfile - ethicic.wsgi:application
else
    echo "⚠️  Gunicorn not found, trying with runtime init fallback"
    exec ./runtime_init.sh
fi
