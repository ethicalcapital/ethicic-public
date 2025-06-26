#!/bin/bash
# Build script for Kinsta deployment

echo "Running Django collectstatic..."
python manage.py collectstatic --noinput

# Skip migrations during build - run them manually after deployment
echo "Skipping migrations during build phase"
echo "Run 'python manage.py migrate' manually after deployment"

echo "Build complete!"