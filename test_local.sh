#!/bin/bash
# Local test runner that mimics Kinsta deployment exactly

echo "=== Setting up local test environment (Kinsta-style) ==="
echo ""

# Set up environment variables for testing
export USE_SQLITE=true
export SKIP_UBICLOUD=true
export DEBUG=true
export SECRET_KEY="test-secret-key-for-local-testing"
export DJANGO_SETTINGS_MODULE=ethicic.settings

echo "Environment configured:"
echo "- USE_SQLITE: $USE_SQLITE"
echo "- DEBUG: $DEBUG"
echo "- DJANGO_SETTINGS_MODULE: $DJANGO_SETTINGS_MODULE"
echo ""

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

echo "Installing dependencies..."
.venv/bin/pip install -r requirements.txt

echo ""
echo "=== Running migrations (SQLite mode) ==="
.venv/bin/python manage.py migrate --noinput

echo ""
echo "=== Running tests ==="
echo "Running quick smoke test first..."
.venv/bin/python manage.py test public_site.tests.test_quick -v 2

if [ "$1" == "all" ]; then
    echo ""
    echo "Running all tests..."
    .venv/bin/python manage.py test public_site.tests -v 2
elif [ "$1" == "coverage" ]; then
    echo ""
    echo "Running tests with coverage..."
    .venv/bin/pip install coverage
    .venv/bin/coverage run --source='public_site' manage.py test public_site.tests
    .venv/bin/coverage report
    .venv/bin/coverage html
    echo "Coverage report generated in htmlcov/"
elif [ ! -z "$1" ]; then
    echo ""
    echo "Running specific test: $1"
    .venv/bin/python manage.py test public_site.tests.$1 -v 2
else
    echo ""
    echo "Quick test passed! Run with 'all' to run all tests:"
    echo "  ./test_local.sh all"
    echo ""
    echo "Or run specific test modules:"
    echo "  ./test_local.sh models"
    echo "  ./test_local.sh views"
    echo "  ./test_local.sh forms"
    echo "  ./test_local.sh integration"
    echo "  ./test_local.sh test_urls"
    echo ""
    echo "Or run with coverage:"
    echo "  ./test_local.sh coverage"
fi