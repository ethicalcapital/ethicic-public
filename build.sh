#!/bin/bash
# Build script for Nixpacks/Kinsta deployment

echo "=== Build Phase Starting ==="
echo "Time: $(date)"
echo "Python version: $(python --version 2>/dev/null || echo 'Not available')"
echo "Current directory: $(pwd)"

# Check if we're in a proper Python environment
if command -v python &> /dev/null; then
    echo "✅ Python available"
    
    # Try to collect static files (may fail without database)
    echo "📁 Attempting to collect static files..."
    python manage.py collectstatic --noinput --clear 2>&1 || {
        echo "⚠️  Static files collection failed (will retry at runtime)"
    }
    
    # Check if we can run basic Django commands
    echo "🔧 Testing Django setup..."
    python manage.py check --deploy 2>&1 || {
        echo "⚠️  Django check failed (normal for build phase)"
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