#!/usr/bin/env python
"""
Set up SSL certificates from environment variables
This runs during build to prepare certificates for database connections
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ethicic.settings")


def setup_certificates():
    """Create certificate files from environment variables."""
    base_dir = Path(__file__).parent.parent

    # Use config/ssl directory to match what the app expects
    ssl_dir = base_dir / "config" / "ssl"

    print("SSL Certificate Setup")
    print("=" * 50)
    print(f"Base directory: {base_dir}")
    print(f"SSL directory: {ssl_dir}")

    # Create config/ssl directory if it doesn't exist
    ssl_dir.mkdir(parents=True, exist_ok=True)
    print("✓ Created/verified SSL directory")

    cert_count = 0

    # CA Certificate - save as ubicloud-root-ca.pem to match expected filename
    ca_cert = os.getenv("DB_CA_CERT")
    if ca_cert:
        print("\nProcessing CA certificate...")
        ca_cert_path = ssl_dir / "ubicloud-root-ca.pem"
        ca_cert_path.write_text(ca_cert)
        os.chmod(ca_cert_path, 0o600)  # Secure permissions

        # Verify certificate
        lines = ca_cert.strip().split("\n")
        print(f"  ✓ Created: {ca_cert_path}")
        print(f"  ✓ Size: {len(ca_cert)} bytes")
        print(f"  ✓ Lines: {len(lines)}")
        print("  ✓ Permissions: 0600 (read/write owner only)")

        # Set the path environment variable for the app
        os.environ["DB_CA_CERT_PATH"] = str(ca_cert_path)
        os.environ["SSL_ROOT_CERT"] = str(ca_cert_path)
        print("  ✓ Set DB_CA_CERT_PATH and SSL_ROOT_CERT environment variables")
        cert_count += 1
    else:
        print("\n  ℹ️  No CA certificate provided")

    # Client Certificate
    client_cert = os.getenv("DB_CLIENT_CERT")
    if client_cert:
        print("\nProcessing client certificate...")
        client_cert_path = ssl_dir / "client-cert.crt"
        client_cert_path.write_text(client_cert)
        os.chmod(client_cert_path, 0o600)
        print(f"  ✓ Created: {client_cert_path}")
        print(f"  ✓ Size: {len(client_cert)} bytes")
        print("  ✓ Permissions: 0600")
        cert_count += 1
    else:
        print("\n  ℹ️  No client certificate provided")

    # Client Key
    client_key = os.getenv("DB_CLIENT_KEY")
    if client_key:
        print("\nProcessing client key...")
        client_key_path = ssl_dir / "client-key.key"
        client_key_path.write_text(client_key)
        os.chmod(client_key_path, 0o600)
        print(f"  ✓ Created: {client_key_path}")
        print(f"  ✓ Size: {len(client_key)} bytes")
        print("  ✓ Permissions: 0600")
        cert_count += 1
    else:
        print("\n  ℹ️  No client key provided")

    # Create a README in ssl directory
    readme_path = ssl_dir / "README.md"
    readme_path.write_text("""# SSL Certificates Directory

This directory contains SSL certificates for secure database connections.
These files are generated from environment variables during deployment.

DO NOT commit these files to version control!
""")
    print(f"\n✓ Created README: {readme_path}")

    print("\n" + "=" * 50)
    print(f"Certificate setup complete: {cert_count} certificates processed")
    print("=" * 50)


if __name__ == "__main__":
    setup_certificates()
