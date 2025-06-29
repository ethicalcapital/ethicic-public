#!/bin/bash
# Simple start script for Nixpacks
set -e

echo "🚀 Starting application..."

# Ensure runtime init script is executable
chmod +x runtime_init.sh 2>/dev/null || true

# Start with runtime initialization
exec ./runtime_init.sh gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 60 ethicic.wsgi:application