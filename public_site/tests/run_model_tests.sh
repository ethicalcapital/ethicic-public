#!/bin/bash
"""
Script to run all model-related tests.
Usage: ./run_model_tests.sh [options]
"""

# Set up environment
export DJANGO_SETTINGS_MODULE=ethicic.test_settings

echo "🧪 Running Model Tests..."
echo "========================="

# Run model tests with coverage
echo "📊 Running with coverage analysis..."

uv run python -m pytest \
    public_site/tests/test_models_updated.py \
    public_site/tests/test_database_optimizations.py \
    public_site/tests/models/test_page_models.py \
    public_site/tests/test_models_comprehensive.py \
    -v \
    --tb=short \
    --durations=10 \
    --cov=public_site.models \
    --cov-report=term-missing \
    --cov-report=html:htmlcov/models \
    "$@"

echo ""
echo "✅ Model tests completed!"
echo "📈 Coverage report available in htmlcov/models/"

# Optional: Run specific test categories
if [ "$1" = "--constraints" ]; then
    echo ""
    echo "🔒 Running constraint-specific tests..."
    uv run python -m pytest \
        public_site/tests/test_database_optimizations.py::DatabaseConstraintValidationTestCase \
        -v
fi

if [ "$1" = "--performance" ]; then
    echo ""
    echo "⚡ Running performance tests..."
    uv run python -m pytest \
        public_site/tests/test_database_optimizations.py::IndexPerformanceTestCase \
        public_site/tests/test_models_updated.py::PerformanceTestCase \
        -v
fi

if [ "$1" = "--quick" ]; then
    echo ""
    echo "🚀 Running quick model tests..."
    uv run python -m pytest \
        public_site/tests/test_models_updated.py::QueryOptimizationTestCase \
        public_site/tests/test_models_updated.py::PRIDDQPageTestCase \
        -v
fi
