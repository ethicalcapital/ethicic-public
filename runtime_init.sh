#!/bin/bash
# Runtime initialization script - runs when the container starts

echo ""
echo "=========================================="
echo "=== Runtime Initialization Starting ==="
echo "=========================================="
echo "Time: $(date)"
echo "Container ID: $(hostname)"
echo ""

# Reset to normal Django settings (not build settings)
export DJANGO_SETTINGS_MODULE=ethicic.settings
echo "Reset DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE"

# Show runtime environment
echo "Runtime Environment:"
echo "- UBI_DATABASE_URL: $([ ! -z "$UBI_DATABASE_URL" ] && echo "SET" || echo "NOT SET")"
echo "- REDIS_URL: $([ ! -z "$REDIS_URL" ] && echo "SET" || echo "NOT SET")"
echo "- USE_SQLITE: $USE_SQLITE"
echo "- SKIP_UBICLOUD: $SKIP_UBICLOUD"
echo ""

# Test database connectivity
echo "=== Database Connectivity Test ==="
python manage.py test_db_connection 2>&1 || {
    echo "⚠️  Database connection test failed (non-fatal)"
    echo "   Will continue with available databases"
}

# Check if we need to sync from Ubicloud
if [ ! -z "$UBI_DATABASE_URL" ] && [ -z "$SKIP_UBICLOUD" ]; then
    echo ""
    echo "=== Checking Ubicloud Connectivity ==="
    
    # Quick connectivity test with timeout
    timeout 5 python -c "
import psycopg2
import os
try:
    from urllib.parse import urlparse
    url = urlparse(os.getenv('UBI_DATABASE_URL'))
    conn = psycopg2.connect(
        host=url.hostname,
        port=url.port or 5432,
        database=url.path[1:],
        user=url.username,
        password=url.password,
        connect_timeout=5
    )
    conn.close()
    print('✅ Ubicloud is reachable')
    exit(0)
except Exception as e:
    print(f'❌ Ubicloud unreachable: {e}')
    exit(1)
" 2>&1
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "=== Hybrid Database Mode ==="
        echo "🔄 Ubicloud database connected - setting up hybrid mode"
        
        # Import data from Ubicloud
        echo ""
        echo "📥 Importing data from Ubicloud..."
        echo "   This may take a few moments..."
        
        start_time=$(date +%s)
        python manage.py import_from_ubicloud 2>&1 || {
            echo "⚠️  Data import failed or skipped"
            echo "   The site will start with empty content"
        }
        end_time=$(date +%s)
        duration=$((end_time - start_time))
        echo "   Import duration: ${duration}s"
        
        # Sync to local cache
        echo ""
        echo "💾 Syncing to local cache..."
        
        start_time=$(date +%s)
        python manage.py sync_cache 2>&1 || {
            echo "⚠️  Cache sync failed or skipped"
            echo "   The site will fetch data directly from Ubicloud"
        }
        end_time=$(date +%s)
        duration=$((end_time - start_time))
        echo "   Sync duration: ${duration}s"
    else
        echo ""
        echo "=== Fallback to Standalone Mode ==="
        echo "⚠️  Cannot reach Ubicloud database"
        echo "📍 Running in standalone mode with local SQLite only"
        
        # Disable Ubicloud for this session
        export USE_SQLITE=true
        unset UBI_DATABASE_URL
    fi
else
    echo ""
    echo "=== Standalone Mode ==="
    echo "📍 Running in standalone mode (no Ubicloud connection)"
    echo "   Using local SQLite database only"
fi

echo ""
echo "=== Runtime Initialization Complete ==="
echo "✅ Ready to start web server at $(date)"
echo ""
echo "Starting application with command: $@"
echo "=========================================="
echo ""

# Start the application
exec "$@"