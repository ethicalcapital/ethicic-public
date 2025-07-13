#!/usr/bin/env python
"""Fast test runner script for development."""

import os
import subprocess
import sys


def main():
    """Run tests with optimized settings."""

    # Set fast test settings
    os.environ["DJANGO_SETTINGS_MODULE"] = "ethicic.test_settings_fast"

    # Default test arguments for speed
    base_args = [
        "pytest",
        "--tb=short",
        "--disable-warnings",
        "--reuse-db",
        "--nomigrations",
        "-x",  # Stop on first failure
        "--maxfail=5",
        "-q",  # Quiet output
    ]

    # Check for arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "unit":
            # Run only unit tests
            base_args.extend(["tests/unit/", "public_site/tests/test_quick.py"])
        elif sys.argv[1] == "quick":
            # Run only quick smoke tests
            base_args.append("public_site/tests/test_quick.py")
        elif sys.argv[1] == "forms":
            # Run only form tests
            base_args.extend(["tests/unit/test_forms.py", "public_site/tests/forms/"])
        elif sys.argv[1] == "parallel":
            # Run with parallel processing
            base_args.extend(["-n", "auto", "tests/unit/"])
        else:
            # Custom test path
            base_args.append(sys.argv[1])
    else:
        # Run unit tests by default
        base_args.extend(["tests/unit/", "public_site/tests/test_quick.py"])

    print(f"Running: {' '.join(base_args)}")
    return subprocess.call(base_args)


if __name__ == "__main__":
    sys.exit(main())
