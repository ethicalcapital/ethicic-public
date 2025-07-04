#!/usr/bin/env python
"""
Diagnose Ubicloud connection issues
"""
import os
import socket
import ssl
from urllib.parse import urlparse

print("=== Connection Diagnostics ===")

# Get database URL
db_url = os.getenv('UBI_DATABASE_URL')
if not db_url:
    print("❌ UBI_DATABASE_URL not set")
    exit(1)

# Parse URL
parsed = urlparse(db_url)
host = parsed.hostname
port = parsed.port or 5432

print(f"Target: {host}:{port}")

# Test DNS resolution
try:
    ip = socket.gethostbyname(host)
    print(f"✅ DNS resolved to: {ip}")
except Exception as e:
    print(f"❌ DNS resolution failed: {e}")
    exit(1)

# Test TCP connection
print("\n=== TCP Connection Test ===")
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)
    result = sock.connect_ex((host, port))
    if result == 0:
        print(f"✅ TCP connection to {host}:{port} successful")
    else:
        print(f"❌ TCP connection failed with error code: {result}")
    sock.close()
except Exception as e:
    print(f"❌ TCP connection error: {e}")

# Test SSL connection
print("\n=== SSL Connection Test ===")
try:
    # Create SSL context
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    
    # Try to connect with SSL
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)
    
    ssl_sock = context.wrap_socket(sock, server_hostname=host)
    ssl_sock.connect((host, port))
    
    print("✅ SSL connection established")
    print(f"   SSL Version: {ssl_sock.version()}")
    print(f"   Cipher: {ssl_sock.cipher()}")
    
    # Try to send PostgreSQL startup message
    # This is a simplified version - just to see if we get a response
    ssl_sock.send(b'\x00\x00\x00\x08\x04\xd2\x16\x2f')
    response = ssl_sock.recv(1)
    if response:
        print(f"✅ PostgreSQL responded (got {len(response)} bytes)")
    
    ssl_sock.close()
except ssl.SSLError as e:
    print(f"❌ SSL error: {e}")
except socket.timeout:
    print("❌ Connection timeout")
except Exception as e:
    print(f"❌ Connection error: {e}")

# Get current public IP (useful for whitelisting)
print("\n=== Current Public IP ===")
try:
    import urllib.request
    public_ip = urllib.request.urlopen('https://api.ipify.org').read().decode('utf-8')
    print(f"Current public IP: {public_ip}")
    print("\n📌 To whitelist this IP in Ubicloud, run:")
    print(f"   ubi pg dewey-db add-firewall-rule {public_ip}/32")
    print("\nNote: Kinsta may use multiple IPs. Contact their support for the full range.")
except Exception as e:
    print(f"Could not determine public IP: {e}")

# Test PostgreSQL-specific connection
print("\n=== PostgreSQL SSL Handshake Test ===")
if os.getenv('UBI_DATABASE_URL'):
    try:
        import psycopg2
        print("Attempting psycopg2 connection with SSL...")
        
        # Try with minimal SSL first
        conn_string = os.getenv('UBI_DATABASE_URL').replace('postgresql://', 'postgresql://')
        conn_string += '?sslmode=require&connect_timeout=5'
        
        print(f"Connection string: {conn_string.split('@')[1]}")  # Hide credentials
        
        conn = psycopg2.connect(conn_string)
        print("✅ Connection successful!")
        conn.close()
        
    except psycopg2.OperationalError as e:
        error_msg = str(e)
        if "server closed the connection unexpectedly" in error_msg:
            print("❌ Server closed connection - likely needs IP whitelisting")
        elif "SSL connection has been closed unexpectedly" in error_msg:
            print("❌ SSL handshake failed - certificate or protocol mismatch")
        else:
            print(f"❌ Connection failed: {error_msg}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")