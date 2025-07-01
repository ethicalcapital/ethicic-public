#!/bin/bash
# Runtime initialization script - runs when the container starts

echo ""
echo "=========================================="
echo "=== Runtime Initialization Starting ==="
echo "=========================================="
echo "Time: $(date)"
echo "Container ID: $(hostname)"
echo ""

# Check Python environment
echo "=== Python Environment Check ==="
echo "Python executable: $(which python 2>/dev/null || echo 'Not found')"
echo "Python3 executable: $(which python3 2>/dev/null || echo 'Not found')"
echo "Pip executable: $(which pip 2>/dev/null || echo 'Not found')"
echo "Pip3 executable: $(which pip3 2>/dev/null || echo 'Not found')"
echo "UV executable: $(which uv 2>/dev/null || echo 'Not found')"

# Check if dependencies are already available
echo "=== Dependencies Check ==="
echo "Gunicorn: $(which gunicorn 2>/dev/null || echo 'Not found')"
echo "Django: $(python -c 'import django; print(django.__version__)' 2>/dev/null || echo 'Not found')"

# Check Python path and installed packages
echo "=== Python Path Information ==="
python -c "
import sys
print('Python version:', sys.version)
print('Python path:')
for path in sys.path:
    print('  ', path)
print('Installed packages check:')
try:
    import django
    print('  ✅ Django available:', django.__version__)
except ImportError:
    print('  ❌ Django not available')
try:
    import gunicorn
    print('  ✅ Gunicorn available:', gunicorn.__version__)
except ImportError:
    print('  ❌ Gunicorn not available')
" 2>/dev/null || echo "Python not available for diagnostics"

# Try to find gunicorn in various locations
echo "=== Searching for Gunicorn ==="
find /usr -name "gunicorn*" 2>/dev/null | head -5 || echo "No results from /usr search"
find /opt -name "gunicorn*" 2>/dev/null | head -5 || echo "No results from /opt search"
find . -name "gunicorn*" 2>/dev/null | head -5 || echo "No results from current directory search"

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

# Check if we have Kinsta DB_URL first - skip other tests if we do
if [ ! -z "$DB_URL" ]; then
    echo "=== Kinsta Database Detected ==="
    echo "✅ Using Kinsta PostgreSQL - skipping Ubicloud connection tests"
    echo "   Host: $DB_HOST"
    echo "   Database: $DB_DATABASE"
    export SKIP_UBICLOUD=true
else
    # Test database connectivity only if not using Kinsta
    echo "=== Database Connectivity Test ==="
    if command -v python &> /dev/null; then
        python manage.py test_db_connection 2>&1 || {
            echo "⚠️  Database connection test failed (non-fatal)"
            echo "   Will continue with available databases"
        }
    else
        echo "⚠️  Python not available for database test (non-fatal)"
    fi
fi

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

# Run connection diagnostics if available (skip if using Kinsta)
if [ -z "$DB_URL" ] && [ -f "./diagnose_connection.py" ] && [ ! -z "$UBI_DATABASE_URL" ] && command -v python &> /dev/null; then
    echo ""
    echo "=== Running Connection Diagnostics ==="
    python diagnose_connection.py 2>&1 || echo "Diagnostics completed with errors"
fi

# Collect static files if not already done
echo ""
echo "=== Static Files Collection ==="

# Check if key CSS files exist
css_missing=false
if [ -d "staticfiles/css" ]; then
    for css_file in "garden-ui-theme.css" "core-styles.css" "public-site-simple.css"; do
        if [ ! -f "staticfiles/css/$css_file" ]; then
            css_missing=true
            break
        fi
    done
else
    css_missing=true
fi

if [ ! -d "staticfiles" ] || [ -z "$(ls -A staticfiles 2>/dev/null)" ] || [ "$css_missing" = true ]; then
    echo "📁 Static files missing or incomplete - collecting now..."
    
    # First check if source files exist
    echo "   Checking source static files..."
    if [ -d "static/css" ]; then
        echo "   ✅ Source static/css directory found"
        ls -la static/css/*.css 2>/dev/null | head -5 || echo "   ⚠️ No CSS files in source directory"
    else
        echo "   ❌ Source static/css directory missing!"
    fi
    
    # Clear and recollect
    python manage.py collectstatic --noinput --clear 2>&1 || {
        echo "⚠️  Static files collection failed"
        echo "   Site may have styling issues"
        
        # Try copying manually as fallback
        if [ -d "static" ] && [ ! -d "staticfiles" ]; then
            echo "   Attempting manual copy as fallback..."
            cp -r static staticfiles 2>/dev/null && echo "   ✅ Manual copy completed" || echo "   ❌ Manual copy failed"
        fi
    }
else
    echo "✅ Static files already collected"
fi

# Always verify key files
echo "   Verifying key CSS files:"
ls -la staticfiles/css/garden-ui-theme.css 2>/dev/null && echo "   ✅ garden-ui-theme.css found" || echo "   ❌ garden-ui-theme.css missing"
ls -la staticfiles/css/core-styles.css 2>/dev/null && echo "   ✅ core-styles.css found" || echo "   ❌ core-styles.css missing"
ls -la staticfiles/css/public-site-simple.css 2>/dev/null && echo "   ✅ public-site-simple.css found" || echo "   ❌ public-site-simple.css missing"

# Process based on database configuration
if [ ! -z "$DB_URL" ]; then
    echo ""
    echo "=== Using Kinsta PostgreSQL Database ==="
    echo "📊 Running database migrations on Kinsta PostgreSQL..."
    # First, fake the initial migration since DB already has content
    python manage.py migrate public_site 0001 --fake --noinput 2>&1 || {
        echo "   ⚠️  Initial migration fake completed with warnings"
    }
    # Then run any other migrations normally
    python manage.py migrate --noinput 2>&1 || {
        echo "   ⚠️  Migration completed with warnings"
    }
    
    # Set up initial data
    echo ""
    echo "🔧 Setting up initial Kinsta data..."
    python manage.py setup_kinsta 2>&1 || {
        echo "   ⚠️  Setup completed with warnings"
    }
    
# Otherwise check if we need to sync from Ubicloud
elif [ ! -z "$UBI_DATABASE_URL" ] && [ -z "$SKIP_UBICLOUD" ]; then
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
        'sslmode': 'require'  # Use SSL but don't verify certificate
    }
    
    # Try with certificate first if available
    ssl_cert = os.getenv('SSL_ROOT_CERT')
    if not ssl_cert:
        # Check other possible locations
        for path in ['/app/config/ssl/ubicloud-root-ca.pem', './config/ssl/ubicloud-root-ca.pem']:
            if os.path.exists(path):
                ssl_cert = path
                break
    
    connection_successful = False
    
    # First attempt: Try with SSL certificate if available
    if ssl_cert and os.path.exists(ssl_cert):
        try:
            conn_params['sslrootcert'] = ssl_cert
            conn_params['sslmode'] = 'verify-full'
            print(f'   Attempting connection with SSL certificate: {ssl_cert}')
            test_conn = psycopg2.connect(**conn_params)
            test_conn.close()
            print('   ✅ SSL certificate connection successful')
            connection_successful = True
        except Exception as e:
            print(f'   ⚠️  SSL certificate connection failed: {e}')
            # Remove certificate for fallback attempt
            conn_params.pop('sslrootcert', None)
            conn_params['sslmode'] = 'require'
    
    # Second attempt: Try without certificate verification
    if not connection_successful:
        print('   Attempting connection with SSL but no certificate verification...')
    
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
        
        # Run migrations to ensure schema is up to date
        echo ""
        echo "📊 Running database migrations..."
        
        # Check if this is a fresh database or has existing schema
        echo "   Checking database state..."
        
        # Try to check if wagtailcore_site table exists
        python -c "
from django.db import connection
try:
    with connection.cursor() as cursor:
        cursor.execute(\"SELECT COUNT(*) FROM wagtailcore_site\")
        print('Database has existing Wagtail schema')
        exit(0)
except Exception:
    print('Database appears to be fresh or incomplete')
    exit(1)
" 2>/dev/null

        if [ $? -eq 0 ]; then
            echo "   Using fake-initial for existing schema..."
            python manage.py migrate --fake-initial --noinput 2>&1 || {
                echo "   ⚠️  Fake-initial failed, trying regular migration..."
                python manage.py migrate --noinput 2>&1 || {
                    echo "   ⚠️  Migration completed with warnings"
                }
            }
        else
            echo "   Running full migration for fresh database..."
            python manage.py migrate --noinput 2>&1 || {
                echo "   ⚠️  Migration completed with warnings"
            }
        fi
        
        # Import data from Ubicloud
        echo ""
        echo "📥 Importing data from Ubicloud..."
        echo "   This may take a few moments..."
        
        start_time=$(date +%s)
        python manage.py safe_import_from_ubicloud 2>&1 || {
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
        
        # For standalone mode, always run full migrations since it's likely a fresh SQLite database
        echo "   Running full migrations for standalone mode..."
        python manage.py migrate --noinput 2>&1 || echo "   Migration completed with warnings"
        
        # Ensure homepage is set up
        echo "🏠 Setting up homepage..."
        python manage.py setup_homepage 2>&1 || echo "   Homepage setup completed with warnings"
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

# Check if we have arguments (command to execute)
if [ $# -eq 0 ]; then
    echo "⚠️  No command provided, starting Django development server"
    PORT=${PORT:-8080}
    echo "🚀 Starting Django development server on 0.0.0.0:$PORT"
    exec python manage.py runserver 0.0.0.0:$PORT
fi

# Check if the command contains gunicorn and if gunicorn is available
if [[ "$*" == *"gunicorn"* ]]; then
    if ! command -v gunicorn &> /dev/null; then
        echo "⚠️  Gunicorn not found, falling back to Django development server"
        echo "   This is not ideal for production but will allow the site to start"
        
        # Extract port from environment or default
        PORT=${PORT:-8080}
        
        # Start Django development server instead
        echo "🚀 Starting Django development server on 0.0.0.0:$PORT"
        exec python manage.py runserver 0.0.0.0:$PORT
    else
        echo "✅ Gunicorn is available, proceeding with gunicorn startup"
    fi
fi

# Ensure PORT is available in the environment for gunicorn
export PORT=${PORT:-8080}
echo "📍 Final PORT check: $PORT"
echo "📍 Command to execute: $@"

# Test port binding before starting
echo "📍 Testing port binding capability..."
python -c "
import socket
port = int('$PORT')
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    sock.bind(('0.0.0.0', port))
    print(f'✅ Port {port} is available for binding')
    sock.close()
except Exception as e:
    print(f'❌ Cannot bind to port {port}: {e}')
    exit(1)
"

if [ $? -ne 0 ]; then
    echo "⚠️  Port binding test failed, trying Django development server instead"
    exec python manage.py runserver 0.0.0.0:$PORT
fi

# Start the application with exec to preserve environment
exec "$@"