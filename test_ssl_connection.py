#!/usr/bin/env python
"""Test SSL connection to Ubicloud database"""
import os
import sys
import psycopg2
from urllib.parse import urlparse

def test_connection():
    db_url = os.getenv('UBI_DATABASE_URL')
    if not db_url:
        print("ERROR: UBI_DATABASE_URL not set")
        return False
    
    url = urlparse(db_url)
    print(f"Testing connection to: {url.hostname}")
    
    # Test 1: Without SSL
    print("\n1. Testing WITHOUT SSL...")
    try:
        conn = psycopg2.connect(
            host=url.hostname,
            port=url.port or 5432,
            database=url.path[1:],
            user=url.username,
            password=url.password,
            sslmode='disable'
        )
        cur = conn.cursor()
        cur.execute("SELECT current_database(), current_schema()")
        db, schema = cur.fetchone()
        print(f"✅ Success! Connected to database '{db}', schema '{schema}'")
        
        # Check for tables
        cur.execute("""
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        count = cur.fetchone()[0]
        print(f"   Found {count} tables in public schema")
        
        conn.close()
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    # Test 2: With SSL (no cert verification)
    print("\n2. Testing WITH SSL (no cert)...")
    try:
        conn = psycopg2.connect(
            host=url.hostname,
            port=url.port or 5432,
            database=url.path[1:],
            user=url.username,
            password=url.password,
            sslmode='require'
        )
        print("✅ Success! SSL connection works without certificate")
        conn.close()
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    # Test 3: With SSL certificate
    print("\n3. Testing WITH SSL certificate...")
    cert_paths = [
        "/app/config/ssl/ubicloud-root-ca.pem",
        "./config/ssl/ubicloud-root-ca.pem",
        os.path.expanduser("~/config/ssl/ubicloud-root-ca.pem")
    ]
    
    cert_found = False
    for cert_path in cert_paths:
        if os.path.exists(cert_path):
            print(f"   Found certificate at: {cert_path}")
            cert_found = True
            try:
                conn = psycopg2.connect(
                    host=url.hostname,
                    port=url.port or 5432,
                    database=url.path[1:],
                    user=url.username,
                    password=url.password,
                    sslmode='require',
                    sslrootcert=cert_path
                )
                print("✅ Success! SSL with certificate works")
                conn.close()
                return True
            except Exception as e:
                print(f"❌ Failed with cert: {e}")
    
    if not cert_found:
        print("   ⚠️  No SSL certificate found at expected locations")
    
    return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)