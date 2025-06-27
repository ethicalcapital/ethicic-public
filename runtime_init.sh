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
echo "- PORT: ${PORT:-NOT SET}"
echo "- All environment variables containing PORT:"
env | grep -i port || echo "  None found"
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

# Check SSL certificate availability
echo "=== SSL Certificate Check ==="
if [ -f "/app/config/ssl/ubicloud-root-ca.pem" ]; then
    echo "✅ SSL certificate found at /app/config/ssl/ubicloud-root-ca.pem"
    export SSL_ROOT_CERT="/app/config/ssl/ubicloud-root-ca.pem"
    # Verify certificate is readable
    head -n 1 /app/config/ssl/ubicloud-root-ca.pem | grep -q "BEGIN CERTIFICATE" && echo "   Certificate format verified" || echo "   ⚠️ Certificate format issue"
    ls -la /app/config/ssl/ubicloud-root-ca.pem
elif [ -f "./config/ssl/ubicloud-root-ca.pem" ]; then
    echo "✅ SSL certificate found at ./config/ssl/ubicloud-root-ca.pem"
    export SSL_ROOT_CERT="./config/ssl/ubicloud-root-ca.pem"
    # Verify certificate is readable
    head -n 1 ./config/ssl/ubicloud-root-ca.pem | grep -q "BEGIN CERTIFICATE" && echo "   Certificate format verified" || echo "   ⚠️ Certificate format issue"
    ls -la ./config/ssl/ubicloud-root-ca.pem
else
    echo "⚠️  No SSL certificate found - connection will use sslmode=require without cert validation"
    echo "   Checking directory contents:"
    ls -la /app/config/ssl/ 2>/dev/null || echo "   /app/config/ssl/ not found"
    ls -la ./config/ssl/ 2>/dev/null || echo "   ./config/ssl/ not found"
fi

# Run connection diagnostics if available
if [ -f "./diagnose_connection.py" ] && [ ! -z "$UBI_DATABASE_URL" ]; then
    echo ""
    echo "=== Running Connection Diagnostics ==="
    python diagnose_connection.py 2>&1 || echo "Diagnostics completed with errors"
fi

# Check if we need to sync from Ubicloud
if [ ! -z "$UBI_DATABASE_URL" ] && [ -z "$SKIP_UBICLOUD" ]; then
    echo ""
    echo "=== Checking Ubicloud Connectivity ==="
    
    # Quick connectivity test with timeout
    timeout 5 python -c "
import psycopg2
import os
import sys
try:
    from urllib.parse import urlparse
    url = urlparse(os.getenv('UBI_DATABASE_URL'))
    
    # Connection parameters
    conn_params = {
        'host': url.hostname,
        'port': url.port or 5432,
        'database': url.path[1:],
        'user': url.username,
        'password': url.password,
        'connect_timeout': 5,
        'sslmode': 'require'
    }
    
    # Add SSL certificate if available
    ssl_cert = os.getenv('SSL_ROOT_CERT')
    if ssl_cert and os.path.exists(ssl_cert):
        conn_params['sslrootcert'] = ssl_cert
        print(f'   Using SSL certificate: {ssl_cert}')
    
    conn = psycopg2.connect(**conn_params)
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
        
        # Setup standalone database if needed
        echo ""
        echo "🔧 Setting up standalone database..."
        python manage.py migrate --noinput 2>&1 || echo "   Migration completed with warnings"
        python manage.py setup_standalone 2>&1 || echo "   Standalone setup completed with warnings"
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
echo "Starting application with: $@"
echo "=========================================="
echo ""

# Ensure PORT is set (Kinsta should provide this)
if [ -z "$PORT" ]; then
    echo "⚠️  WARNING: PORT environment variable not set, defaulting to 8080"
    export PORT=8080
fi

echo "📍 PORT is set to: $PORT"
echo "📍 Gunicorn will automatically bind to 0.0.0.0:$PORT"
echo ""

# Show the actual command being executed
echo "Executing: $@"
echo ""

# Start the application with exec to preserve environment
exec "$@"