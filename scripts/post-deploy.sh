#!/bin/bash
set -e

echo "🚀 Running post-deployment setup..."

# Run database migrations
echo "📊 Running database migrations..."
python manage.py migrate --noinput

# Set up complete site structure (homepage, essential pages, superuser)
echo "🏠 Setting up site structure..."
python manage.py setup_homepage

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

echo "✅ Post-deployment setup complete!"
