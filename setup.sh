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

echo "=== Setup complete! ==="
echo ""
echo "Admin credentials:"
echo "Username: admin"
echo "Password: ethicic2024!"
echo ""
echo "You can now access the admin at: /admin/"