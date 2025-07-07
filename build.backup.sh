#!/bin/bash
# Build script for Nixpacks/Kinsta deployment

echo "=== Build Phase Starting ==="
echo "Time: $(date)"
echo "Python version: $(python --version 2>/dev/null || echo 'Not available')"
echo "Current directory: $(pwd)"

# Set build-safe environment variables
export SECRET_KEY="build-phase-key-$(date +%s)"
export USE_SQLITE=true
export DEBUG=false
export ALLOWED_HOSTS="*"
export DJANGO_SETTINGS_MODULE=ethicic.settings_build

echo "🔧 Build environment configured with safe defaults"
echo "   Using settings: $DJANGO_SETTINGS_MODULE"

# Check if we're in a proper Python environment
if command -v python &> /dev/null; then
    echo "✅ Python available"

    # Try to collect static files with build-safe settings
    echo "📁 Attempting to collect static files..."

    # First create static directories to ensure they exist
    mkdir -p static staticfiles

    # Skip collectstatic during build - runtime will handle it
    echo "⏭️  Skipping static files collection during build"
    echo "   Runtime will handle static files with proper environment"

    # Ensure basic static directory structure exists
    mkdir -p staticfiles/css staticfiles/js staticfiles/images
    echo "📁 Created basic static file structure for runtime"

    # Basic Django validation (skip deployment checks in build)
    echo "🔧 Testing Django setup..."
    python manage.py check 2>&1 || {
        echo "⚠️  Django check failed (will retry at runtime)"
    }
else
    echo "⚠️  Python not available during build - deferring all setup to runtime"
fi

# Set up SSL certificates if provided (for runtime use)
echo "=== SSL Certificate Setup ==="
if [ ! -z "$DB_CA_CERT" ] || [ ! -z "$DB_CLIENT_CERT" ]; then
    echo "📜 Setting up SSL certificates for runtime..."

    # Create certs directory
    mkdir -p ./certs

    # Save certificates if provided
    if [ ! -z "$DB_CA_CERT" ]; then
        echo "$DB_CA_CERT" > ./certs/ca-cert.pem
        echo "   ✅ CA certificate saved"
    fi

    if [ ! -z "$DB_CLIENT_CERT" ]; then
        echo "$DB_CLIENT_CERT" > ./certs/client-cert.pem
        echo "   ✅ Client certificate saved"
    fi

    if [ ! -z "$DB_CLIENT_KEY" ]; then
        echo "$DB_CLIENT_KEY" > ./certs/client-key.pem
        echo "   ✅ Client key saved"
    fi

    echo "   📋 Certificates ready for runtime use"
else
    echo "ℹ️  No SSL certificates provided - skipping setup"
fi

echo ""
echo "=== Build Summary ==="
echo "✅ Build completed at $(date)"
echo "Runtime startup will handle:"
echo "1. Database migrations"
echo "2. Static file collection (if failed above)"
echo "3. Site structure setup"
echo "4. Database connection and data import"
