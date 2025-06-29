#!/bin/bash
# Run all public site tests

echo "🧪 Running Public Site Test Suite..."
echo "===================================="

# Set test environment
export DJANGO_SETTINGS_MODULE=config.settings.test
export TESTING=true

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to run tests and check result
run_test_module() {
    local module=$1
    local description=$2
    
    echo -e "\n${YELLOW}Testing ${description}...${NC}"
    
    if docker exec garden-platform python manage.py test ${module} --verbosity=2; then
        echo -e "${GREEN}✓ ${description} tests passed${NC}"
        return 0
    else
        echo -e "${RED}✗ ${description} tests failed${NC}"
        return 1
    fi
}

# Track overall result
FAILED=0

# Run different test modules
run_test_module "public_site.tests.models" "Models" || FAILED=1
run_test_module "public_site.tests.forms" "Forms" || FAILED=1
run_test_module "public_site.tests.views" "Views" || FAILED=1
run_test_module "public_site.tests.test_urls" "URL Routing" || FAILED=1
run_test_module "public_site.tests.integration" "Integration Flows" || FAILED=1

echo -e "\n===================================="

# Run all tests together with coverage
echo -e "\n${YELLOW}Running full test suite with coverage...${NC}"

if docker exec garden-platform coverage run --source='public_site' manage.py test public_site.tests --verbosity=2; then
    echo -e "${GREEN}✓ All tests passed${NC}"
    
    # Generate coverage report
    echo -e "\n${YELLOW}Coverage Report:${NC}"
    docker exec garden-platform coverage report -m
    
    # Generate HTML coverage report
    docker exec garden-platform coverage html
    echo -e "${GREEN}HTML coverage report generated in htmlcov/${NC}"
else
    echo -e "${RED}✗ Some tests failed${NC}"
    FAILED=1
fi

# Summary
echo -e "\n===================================="
if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ All test suites passed successfully!${NC}"
    exit 0
else
    echo -e "${RED}❌ Some test suites failed. Please check the output above.${NC}"
    exit 1
fi