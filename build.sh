#!/bin/bash
# Build script for Kinsta deployment

echo "Running Django collectstatic..."
python manage.py collectstatic --noinput

echo "Running Django migrations..."
python manage.py migrate --noinput

echo "Build complete!"