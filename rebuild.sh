#!/bin/bash
# Force rebuild Docker container with no cache and clear volumes

echo "🔄 Force rebuilding Docker container..."
echo "This will clear all cached static files and rebuild from scratch."

# Stop and remove containers
docker-compose down

# Remove the persistent static files volume to clear cache
docker volume rm ethicic-public_static_files 2>/dev/null || true

# Rebuild with no cache
docker-compose build --no-cache

# Start services
docker-compose up -d

echo "✅ Rebuild complete! Static files will be freshly generated."
echo "📊 Check logs with: docker-compose logs -f app"
