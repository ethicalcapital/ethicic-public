#!/usr/bin/env python3
"""
Standalone CSS test runner
Can run without Django test framework conflicts
"""

import os
import sys
import unittest

import django

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ethicic.settings")
django.setup()

# Now import and run our CSS tests
from tests.test_css_conflicts import CSSConflictTests, CSSPerformanceTests  # noqa: E402


def run_css_tests():
    """Run CSS conflict prevention tests."""

    print("🧪 Running CSS Conflict Prevention Tests")
    print("=" * 50)

    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add CSS conflict tests
    suite.addTests(loader.loadTestsFromTestCase(CSSConflictTests))
    suite.addTests(loader.loadTestsFromTestCase(CSSPerformanceTests))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Summary
    print("\n" + "=" * 50)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")

    if result.failures:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            msg = traceback.split("AssertionError: ")[-1].split("\n")[0]
            print(f"  - {test}: {msg}")

    if result.errors:
        print("\nERRORS:")
        for test, traceback in result.errors:
            msg = traceback.split("\n")[-2]
            print(f"  - {test}: {msg}")

    success = len(result.failures) == 0 and len(result.errors) == 0

    if success:
        print("\n🎉 All CSS tests passed!")
    else:
        print("\n❌ Some CSS tests failed!")

    return success

if __name__ == "__main__":
    success = run_css_tests()
    sys.exit(0 if success else 1)
