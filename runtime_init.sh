#!/bin/bash
# Runtime initialization script - runs when the container starts

echo "=== Runtime initialization ==="

# Check if we need to sync from Ubicloud
if [ ! -z "$UBI_DATABASE_URL" ] && [ -z "$SKIP_UBICLOUD" ]; then
    echo "Ubicloud database configured - setting up hybrid mode"
    
    # Import data from Ubicloud
    echo "Importing data from Ubicloud..."
    python manage.py import_from_ubicloud || echo "Data import skipped"
    
    # Sync to local cache
    echo "Syncing to local cache..."
    python manage.py sync_cache || echo "Cache sync skipped"
else
    echo "Running in standalone mode"
fi

echo "=== Runtime initialization complete ==="

# Start the application
exec "$@"