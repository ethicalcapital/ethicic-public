#!/bin/bash
# Build script for Kinsta deployment

echo "=== Starting build script ==="

# Show environment info for debugging
echo "Python version: $(python --version)"
echo "Current directory: $(pwd)"
echo "Directory contents:"
ls -la

# Ensure we're using SQLite for initial setup
export USE_SQLITE=true

echo "Running Django collectstatic..."
python manage.py collectstatic --noinput || {
    echo "❌ collectstatic failed"
    exit 1
}

echo "Running migrations..."
# Migrate main database
python manage.py migrate --noinput || {
    echo "❌ migrate failed"
    exit 1
}

# If using hybrid mode, also migrate cache database
if [ ! -z "$UBI_DATABASE_URL" ]; then
    echo "Setting up cache database..."
    python manage.py migrate --database=cache --noinput || echo "Cache database migration skipped"
fi

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

# Import data from Ubicloud (default behavior, fails gracefully)
echo "Attempting to import data from Ubicloud database..."
python manage.py import_from_ubicloud 2>&1 || {
    echo "⚠️  Data import not available or failed - continuing with empty site"
    echo "   This is normal for initial deployments or when UBI_DATABASE_URL is not set"
}

# Sync cache if using hybrid mode
if [ ! -z "$UBI_DATABASE_URL" ]; then
    echo "Syncing data to local cache..."
    python manage.py sync_cache || echo "Cache sync skipped"
fi

echo "=== Build complete! ==="