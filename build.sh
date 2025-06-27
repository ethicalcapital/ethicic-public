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

# Import data from Ubicloud (default behavior, fails gracefully)
echo "Attempting to import data from Ubicloud database..."
python manage.py import_from_ubicloud 2>&1 || {
    echo "⚠️  Data import not available or failed - continuing with empty site"
    echo "   This is normal for initial deployments or when UBI_DATABASE_URL is not set"
}

echo "=== Build complete! ==="