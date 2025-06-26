#!/bin/bash
# Build script for Kinsta deployment

echo "=== Starting build script ==="

# Ensure we're using SQLite for initial setup
export USE_SQLITE=true

echo "Running Django collectstatic..."
python manage.py collectstatic --noinput

echo "Running migrations..."
python manage.py migrate --noinput

# Set up initial site data
echo "Setting up initial site data..."
python manage.py setup_site --hostname="${KINSTA_DOMAIN:-ethicic-public-svoo7.kinsta.app}"

echo "=== Build complete! ==="