#!/bin/bash
# Build script for Kinsta deployment

echo "=== Starting build script at $(date) ==="
echo "Build environment information:"
echo "- Python version: $(python --version)"
echo "- Current directory: $(pwd)"
echo "- Memory available: $(free -h | grep Mem | awk '{print $7}')"
echo "- Disk space: $(df -h . | tail -1 | awk '{print $4}' ) available"

echo ""
echo "Environment variables (sanitized):"
echo "- UBI_DATABASE_URL: $([ ! -z "$UBI_DATABASE_URL" ] && echo "SET" || echo "NOT SET")"
echo "- DB_CA_CERT: $([ ! -z "$DB_CA_CERT" ] && echo "SET ($(echo "$DB_CA_CERT" | wc -l) lines)" || echo "NOT SET")"
echo "- REDIS_URL: $([ ! -z "$REDIS_URL" ] && echo "SET" || echo "NOT SET")"
echo "- DEBUG: $DEBUG"
echo "- KINSTA_DOMAIN: $KINSTA_DOMAIN"

echo ""
echo "Directory contents:"
ls -la

# IMPORTANT: During build phase, we can't connect to external databases
# Force SQLite mode for the build process
echo ""
echo "=== Build Configuration ==="
echo "⚠️  Build phase detected - forcing SQLite mode"
echo "   Reason: Cannot connect to external databases during Docker build"
export USE_SQLITE=true
export SKIP_UBICLOUD=true

# Set up SSL certificates if provided (for runtime use)
if [ ! -z "$DB_CA_CERT" ] || [ ! -z "$DB_CLIENT_CERT" ]; then
    echo ""
    echo "=== SSL Certificate Setup ==="
    echo "📜 Setting up SSL certificates for runtime..."
    python scripts/setup_certs.py 2>&1 || {
        echo "⚠️  Certificate setup failed (non-fatal)"
        echo "   Error details above"
    }
else
    echo ""
    echo "=== SSL Certificate Setup ==="
    echo "ℹ️  No SSL certificates provided - skipping setup"
fi

echo ""
echo "=== Static Files Collection ==="
echo "📁 Running Django collectstatic..."
echo "   Target: $(python -c "from pathlib import Path; import os; print(Path(os.environ.get('STATIC_ROOT', 'staticfiles')).resolve())")"
python manage.py collectstatic --noinput 2>&1 || {
    echo "❌ ERROR: collectstatic failed"
    echo "   Check the error output above"
    exit 1
}
echo "✅ Static files collected successfully"

echo ""
echo "=== Database Migrations ==="
echo "🗄️  Running migrations (SQLite mode)..."
echo "   Database: $(python -c "from pathlib import Path; print(Path('db.sqlite3').resolve())")"
python manage.py migrate --noinput 2>&1 || {
    echo "❌ ERROR: migrate failed"
    echo "   Check the error output above"
    exit 1
}
echo "✅ Migrations completed successfully"

echo ""
echo "=== User Setup ==="
echo "👤 Creating superuser..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
try:
    if not User.objects.filter(username='srvo').exists():
        User.objects.create_superuser('srvo', 'sloane@ethicic.com', 'dyzxuc-4muBzy-woqbam')
        print('✅ Created superuser: srvo')
    else:
        print('ℹ️  Superuser already exists')
except Exception as e:
    print(f'⚠️  Superuser creation failed: {e}')
" 2>&1

echo ""
echo "=== Homepage Setup ==="
echo "🏠 Creating homepage..."
python manage.py create_homepage 2>&1 || {
    echo "⚠️  Homepage creation failed (non-fatal)"
    echo "   This can be set up later via admin"
}

echo ""
echo "=== Site Configuration ==="
echo "🌐 Configuring site settings..."
echo "   Hostname: ${KINSTA_DOMAIN:-ethicic-public-svoo7.kinsta.app}"
python manage.py shell -c "
from wagtail.models import Site
from public_site.models import HomePage

try:
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
        print(f'✅ Site configured: {site.hostname}')
    else:
        print('⚠️  No homepage found, skipping site configuration')
except Exception as e:
    print(f'⚠️  Site configuration failed: {e}')
" 2>&1

echo ""
echo "=== Data Import Status ==="
echo "⏳ Build phase - deferring data import to runtime"
echo "   Reason: External database connections not available during build"

echo ""
echo "=== Build Summary ==="
echo "✅ Build completed successfully at $(date)"
echo ""
echo "Next steps at runtime:"
echo "1. Connect to Ubicloud database (if configured)"
echo "2. Import existing data"
echo "3. Sync to local cache"
echo "4. Start web server"
echo ""
echo "=== End of build script ==="