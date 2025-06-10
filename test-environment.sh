#!/bin/bash
# Test script to validate the test environment setup

echo "🧪 Testing Python Test Environment Setup"
echo "========================================"

echo "1. Running pytest tests..."
python -m pytest tests/ -v
TEST_RESULT=$?

echo ""
echo "2. Running flake8 linting..."
flake8 . --max-line-length=88
LINT_RESULT=$?

echo ""
echo "3. Checking black formatting..."
black --check --diff .
FORMAT_RESULT=$?

echo ""
echo "4. Running coverage report..."
python -m pytest tests/ --cov=. --cov-report=term-missing

echo ""
echo "========================================"
echo "📊 Results Summary:"
echo "Tests: $([ $TEST_RESULT -eq 0 ] && echo "✅ PASS" || echo "❌ FAIL")"
echo "Linting: $([ $LINT_RESULT -eq 0 ] && echo "✅ PASS" || echo "❌ FAIL")"
echo "Formatting: $([ $FORMAT_RESULT -eq 0 ] && echo "✅ PASS" || echo "❌ FAIL")"

if [ $TEST_RESULT -eq 0 ] && [ $LINT_RESULT -eq 0 ] && [ $FORMAT_RESULT -eq 0 ]; then
    echo "🎉 All checks passed!"
    exit 0
else
    echo "❌ Some checks failed!"
    exit 1
fi