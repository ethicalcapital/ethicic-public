#!/bin/bash
# Quick setup script for initial deployment

echo "=== Running initial setup ==="

# Set SQLite mode
export USE_SQLITE=true

# Run migrations
echo "Running migrations..."
python manage.py migrate --noinput

# Set up site
echo "Setting up site data..."
python manage.py setup_site

# Try to import from Ubicloud
echo "Attempting data import from Ubicloud..."
python manage.py import_from_ubicloud || echo "Data import skipped or failed"

echo "=== Setup complete! ==="
echo ""
echo "Admin credentials:"
echo "Username: srvo"
echo "Password: dyzxuc-4muBzy-woqbam"
echo ""
echo "You can now access the admin at: /admin/"