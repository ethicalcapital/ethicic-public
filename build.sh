#!/bin/bash
# Simple build script for Kinsta deployment - Python setup happens at runtime

echo "=== Starting build script at $(date) ==="
echo "Build environment information:"
echo "- Current directory: $(pwd)"
echo "- Memory available: $(free -h | grep Mem | awk '{print $7}' 2>/dev/null || echo 'Unknown')"
echo "- Disk space: $(df -h . | tail -1 | awk '{print $4}' 2>/dev/null || echo 'Unknown') available"

echo ""
echo "Environment variables (sanitized):"
echo "- UBI_DATABASE_URL: $([ ! -z "$UBI_DATABASE_URL" ] && echo "SET" || echo "NOT SET")"
echo "- DEBUG: $DEBUG"
echo "- KINSTA_DOMAIN: $KINSTA_DOMAIN"

echo ""
echo "Directory contents:"
ls -la

echo ""
echo "=== Build Configuration ==="
echo "✅ Simple build - Python setup deferred to runtime"
echo "   Reason: Python/Django commands handled by WSGI startup"
echo "   All database operations, static files, and site setup will run when Django starts"

echo ""
echo "=== SSL Certificate Setup ==="
# Set up SSL certificates if provided (for runtime use) 
if [ ! -z "$DB_CA_CERT" ] || [ ! -z "$DB_CLIENT_CERT" ]; then
    echo "📜 Setting up SSL certificates for runtime..."
    
    # Create certs directory
    mkdir -p /app/certs
    
    # Save certificates if provided
    if [ ! -z "$DB_CA_CERT" ]; then
        echo "$DB_CA_CERT" > /app/certs/ca-cert.pem
        echo "   ✅ CA certificate saved"
    fi
    
    if [ ! -z "$DB_CLIENT_CERT" ]; then
        echo "$DB_CLIENT_CERT" > /app/certs/client-cert.pem
        echo "   ✅ Client certificate saved"
    fi
    
    if [ ! -z "$DB_CLIENT_KEY" ]; then
        echo "$DB_CLIENT_KEY" > /app/certs/client-key.pem
        echo "   ✅ Client key saved"
    fi
    
    echo "   📋 Certificates ready for runtime use"
else
    echo "ℹ️  No SSL certificates provided - skipping setup"
fi

echo ""
echo "=== Build Summary ==="
echo "✅ Build completed successfully at $(date)"
echo ""
echo "Django startup will handle:"
echo "1. Database migrations"
echo "2. Static file collection"
echo "3. Site structure setup (homepage, pages, admin)"
echo "4. Database connection and data import"
echo ""
echo "=== End of build script ==="