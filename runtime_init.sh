#!/bin/bash
# Optimized runtime initialization - parallel operations where possible
set +e  # Don't exit on errors

echo "=== Optimized Runtime Initialization ==="
echo "Time: $(date)"

# Set Django settings
export DJANGO_SETTINGS_MODULE=ethicic.settings

# Quick environment check
echo "Environment: PORT=${PORT:-8080}, DB_URL=${DB_URL:-NOT_SET}"

# Force clear static files cache and regenerate
(
    echo "📁 Force clearing static files cache..."

    # Check if this is a new build or force rebuild is requested
    if [ -f /app/.build_marker ] || [ "$FORCE_STATIC_REBUILD" = "true" ]; then
        echo "🔄 New build detected or force rebuild requested - clearing all static files..."
        rm -rf staticfiles/* 2>/dev/null || true
        find staticfiles -type f -delete 2>/dev/null || true
    fi

    echo "🎨 Building CSS..."
    python manage.py build_css 2>&1 || echo "⚠️  CSS build failed"

    echo "📁 Collecting static files..."
    python manage.py collectstatic --noinput --clear 2>&1 || {
        echo "⚠️  Static collection failed, manual copy..."
        rm -rf staticfiles 2>/dev/null
        cp -r static staticfiles 2>/dev/null
    }

    # Verify critical CSS files are present
    if [ ! -f "staticfiles/css/about-page-v2.css" ]; then
        echo "⚠️  Critical CSS missing, forcing manual copy..."
        cp -r static/* staticfiles/ 2>/dev/null || true
    fi

    echo "✅ Static files ready"
) &
STATIC_PID=$!

# Database operations
if [ ! -z "$DB_URL" ]; then
    echo "📊 Kinsta PostgreSQL detected..."
    python manage.py migrate --noinput 2>&1 || echo "⚠️  Migration warnings"
    python manage.py setup_kinsta 2>&1 || echo "⚠️  Setup warnings"
elif [ ! -z "$UBI_DATABASE_URL" ] && [ -z "$SKIP_UBICLOUD" ]; then
    # Quick connectivity check
    timeout 3 python -c "
import psycopg2, os
from urllib.parse import urlparse
url = urlparse(os.getenv('UBI_DATABASE_URL'))
try:
    conn = psycopg2.connect(
        host=url.hostname, port=url.port or 5432,
        database=url.path[1:], user=url.username,
        password=url.password, connect_timeout=3,
        sslmode='require'
    )
    conn.close()
    exit(0)
except: exit(1)
" 2>&1

    if [ $? -eq 0 ]; then
        echo "✅ Ubicloud connected - hybrid mode"
        python manage.py migrate --noinput 2>&1 || echo "⚠️  Migration warnings"

        # Parallel import and cache sync
        (python manage.py safe_import_from_ubicloud 2>&1 || echo "⚠️  Import skipped") &
        IMPORT_PID=$!
    else
        echo "⚠️  Ubicloud unreachable - standalone mode"
        export USE_SQLITE=true
        unset UBI_DATABASE_URL
        python manage.py migrate --noinput 2>&1
        python manage.py setup_homepage 2>&1
    fi
else
    echo "📍 Standalone mode"
    python manage.py migrate --noinput 2>&1
    python manage.py setup_homepage 2>&1
fi

# Wait for parallel operations
wait $STATIC_PID 2>/dev/null
[ ! -z "$IMPORT_PID" ] && wait $IMPORT_PID 2>/dev/null

echo "✅ Initialization complete"

# Start application
export PORT=${PORT:-8080}
exec "$@"
