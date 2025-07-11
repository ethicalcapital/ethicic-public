#!/bin/bash
set -e

echo "🔧 Kinsta Build Process Starting..."

# Check if we're in Python environment or need to use uv
if command -v uv &> /dev/null; then
    echo "📦 Installing dependencies with uv..."
    uv sync
    PYTHON_CMD="uv run python"
elif command -v pip &> /dev/null; then
    echo "📦 Installing dependencies with pip..."
    pip install -r requirements.txt
    PYTHON_CMD="python"
else
    echo "❌ Neither uv nor pip found. Build cannot continue."
    exit 1
fi

# Run database migrations
echo "📊 Running database migrations..."
$PYTHON_CMD manage.py migrate --noinput

# Set up complete site structure automatically
echo "🏠 Setting up site structure (homepage, pages, admin)..."
$PYTHON_CMD manage.py setup_homepage

# Collect static files
echo "📁 Collecting static files..."
$PYTHON_CMD manage.py collectstatic --noinput

echo "✅ Kinsta Build Process Complete!"
echo "🌐 Site ready at root URL with full homepage and essential pages"
