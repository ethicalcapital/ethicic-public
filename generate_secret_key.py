#!/usr/bin/env python
"""Generate a secure Django SECRET_KEY for production use"""

import secrets
import string


def generate_secret_key(length=50):
    """Generate a secure random string for Django SECRET_KEY"""
    characters = string.ascii_letters + string.digits + "!@#$%^&*(-_=+)"
    return "".join(secrets.choice(characters) for _ in range(length))

if __name__ == "__main__":
    print("\n=== Django SECRET_KEY Generator ===\n")
    print("Generated SECRET_KEY (copy this for Kinsta):\n")
    print(generate_secret_key())
    print("\nIMPORTANT: Keep this key secret and never commit it to git!")
    print("Add it to Kinsta's environment variables as SECRET_KEY\n")
