#!/bin/bash
# Count test methods in public_site/tests

echo "=== Test Count Summary ==="
echo ""

# Count test methods in each file
echo "Test methods by file:"
echo "--------------------"

for file in $(find public_site/tests -name "test_*.py" -not -name "__pycache__"); do
    count=$(grep -c "def test_" "$file" || echo 0)
    if [ $count -gt 0 ]; then
        echo "$file: $count tests"
    fi
done

echo ""
echo "Total test methods:"
find public_site/tests -name "test_*.py" -exec grep -c "def test_" {} \; | awk '{s+=$1} END {print s}'

echo ""
echo "Test classes:"
find public_site/tests -name "test_*.py" -exec grep -c "class.*Test.*:" {} \; | awk '{s+=$1} END {print s}'
