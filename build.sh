#!/bin/bash
# Build script for Kinsta deployment

echo "=== Starting build script ==="

# Show environment info for debugging
echo "Python version: $(python --version)"
echo "Current directory: $(pwd)"
echo "Directory contents:"
ls -la

# IMPORTANT: During build phase, we can't connect to external databases
# Force SQLite mode for the build process
echo "Build phase detected - using SQLite for initial setup"
export USE_SQLITE=true
export SKIP_UBICLOUD=true

# Set up SSL certificates if provided (for runtime use)
if [ ! -z "$DB_CA_CERT" ] || [ ! -z "$DB_CLIENT_CERT" ]; then
    echo "Setting up SSL certificates for runtime..."
    python scripts/setup_certs.py || echo "Certificate setup skipped"
fi

echo "Running Django collectstatic..."
python manage.py collectstatic --noinput || {
    echo "❌ collectstatic failed"
    exit 1
}

echo "Running migrations..."
# During build, we're in SQLite mode
python manage.py migrate --noinput || {
    echo "❌ migrate failed"
    exit 1
}

# Create superuser (don't fail if it already exists)
echo "Creating superuser..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='srvo').exists():
    User.objects.create_superuser('srvo', 'sloane@ethicic.com', 'dyzxuc-4muBzy-woqbam')
    print('Created superuser: srvo')
else:
    print('Superuser already exists')
"

# Create homepage (don't fail if it fails)
echo "Creating homepage..."
python manage.py create_homepage || echo "Homepage creation skipped or failed"

# Update site configuration
echo "Configuring site..."
python manage.py shell -c "
from wagtail.models import Site
from public_site.models import HomePage

# Get homepage if it exists
home = HomePage.objects.first()
if home:
    # Update or create site
    site, created = Site.objects.get_or_create(
        is_default_site=True,
        defaults={
            'hostname': '${KINSTA_DOMAIN:-ethicic-public-svoo7.kinsta.app}',
            'root_page': home
        }
    )
    if not created:
        site.hostname = '${KINSTA_DOMAIN:-ethicic-public-svoo7.kinsta.app}'
        site.root_page = home
        site.save()
    print(f'Site configured: {site.hostname}')
else:
    print('No homepage found, skipping site configuration')
"

# Skip data import during build phase
echo "Build phase - skipping data import (will run at runtime)"

echo "=== Build complete! ==="