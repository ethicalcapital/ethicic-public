#!/bin/bash
set -e

echo "🔧 Kinsta Build Process Starting..."

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Run database migrations
echo "📊 Running database migrations..."
python manage.py migrate --noinput

# Set up complete site structure automatically
echo "🏠 Setting up site structure (homepage, pages, admin)..."
python manage.py setup_homepage

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

echo "✅ Kinsta Build Process Complete!"
echo "🌐 Site ready at root URL with full homepage and essential pages"