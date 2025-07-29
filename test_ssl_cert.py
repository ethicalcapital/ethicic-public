#!/usr/bin/env python
"""
Test SSL certificate loading and database connection
"""

import os
import sys
from pathlib import Path

# Add the project to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Set Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ethicic.settings")

# Test SSL certificate discovery
print("=== Testing SSL Certificate Discovery ===")
print(f"Current working directory: {os.getcwd()}")
print(f"Script location: {Path(__file__).parent}")

# Check certificate locations
cert_locations = [
    "/app/config/ssl/ubicloud-root-ca.pem",
    "./config/ssl/ubicloud-root-ca.pem",
    str(Path(__file__).parent / "config" / "ssl" / "ubicloud-root-ca.pem"),
]

for cert_path in cert_locations:
    exists = Path(cert_path).exists()
    print(f"  {cert_path}: {'✅ EXISTS' if exists else '❌ NOT FOUND'}")
    if exists:
        # Verify it's readable
        try:
            with open(cert_path) as f:
                content = f.read()
                if content.startswith("-----BEGIN CERTIFICATE-----"):
                    print(f"    → Valid certificate file ({len(content)} bytes)")
                else:
                    print("    → Invalid certificate format")
        except Exception as e:
            print(f"    → Error reading: {e}")

# Test database configuration
print("\n=== Testing Database Configuration ===")
try:
    from ethicic.database_config import get_database_config, get_ssl_cert_path

    ssl_cert = get_ssl_cert_path()
    print(f"SSL certificate path found: {ssl_cert}")

    if os.getenv("UBI_DATABASE_URL"):
        config = get_database_config()
        if config:
            print(f"Database host: {config['HOST']}")
            print(f"Database port: {config['PORT']}")
            print(f"SSL options: {config['OPTIONS']}")
    else:
        print("No UBI_DATABASE_URL set")

except Exception as e:
    print(f"Error loading database config: {e}")
    import traceback

    traceback.print_exc()

# Test raw psycopg2 connection
print("\n=== Testing Raw psycopg2 Connection ===")
if os.getenv("UBI_DATABASE_URL"):
    try:
        from urllib.parse import urlparse

        import psycopg2

        url = urlparse(os.getenv("UBI_DATABASE_URL"))

        # Find SSL certificate
        ssl_cert = None
        for cert_path in cert_locations:
            if Path(cert_path).exists():
                ssl_cert = cert_path
                break

        conn_params = {
            "host": url.hostname,
            "port": url.port or 5432,
            "database": url.path[1:],
            "user": url.username,
            "password": url.password,
            "connect_timeout": 5,
            "sslmode": "require",
        }

        if ssl_cert:
            conn_params["sslrootcert"] = ssl_cert
            print(f"Using SSL certificate: {ssl_cert}")
        else:
            print("No SSL certificate found")

        print(f"Connecting to: {url.hostname}:{url.port or 5432}")
        conn = psycopg2.connect(**conn_params)
        print("✅ Connection successful!")

        # Test SSL
        cur = conn.cursor()
        cur.execute("SELECT ssl_is_used()")
        ssl_used = cur.fetchone()[0]
        print(f"SSL in use: {ssl_used}")

        conn.close()

    except Exception as e:
        print(f"❌ Connection failed: {e}")
        import traceback

        traceback.print_exc()
