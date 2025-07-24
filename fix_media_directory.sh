#!/bin/bash
# Fix Wagtail image upload 403 errors by creating media directory

echo "🔧 Fixing Wagtail media directory permissions..."

# Create media directories
echo "📁 Creating media directories..."
mkdir -p /var/lib/data/images/original_images
mkdir -p /var/lib/data/documents

# Set permissions
echo "🔐 Setting permissions to 775..."
chmod -R 775 /var/lib/data

# Set ownership (adjust user/group as needed)
echo "👤 Setting ownership to 1000:1000..."
chown -R 1000:1000 /var/lib/data

# Verify setup
echo "✅ Verifying setup..."
ls -la /var/lib/data
ls -la /var/lib/data/images/

echo "🎉 Media directory setup complete!"
echo "Test image upload at /cms/images/"
