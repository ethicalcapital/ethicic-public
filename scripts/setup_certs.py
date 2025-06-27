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
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ethicic.settings')

def setup_certificates():
    """Create certificate files from environment variables."""
    base_dir = Path(__file__).parent.parent
    certs_dir = base_dir / 'certs'
    
    # Create certs directory if it doesn't exist
    certs_dir.mkdir(exist_ok=True)
    
    # CA Certificate
    ca_cert = os.getenv('DB_CA_CERT')
    if ca_cert:
        ca_cert_path = certs_dir / 'ca-certificate.crt'
        ca_cert_path.write_text(ca_cert)
        os.chmod(ca_cert_path, 0o600)  # Secure permissions
        print(f"✓ Created CA certificate: {ca_cert_path}")
        
        # Set the path environment variable for the app
        os.environ['DB_CA_CERT_PATH'] = str(ca_cert_path)
    
    # Client Certificate
    client_cert = os.getenv('DB_CLIENT_CERT')
    if client_cert:
        client_cert_path = certs_dir / 'client-cert.crt'
        client_cert_path.write_text(client_cert)
        os.chmod(client_cert_path, 0o600)
        print(f"✓ Created client certificate: {client_cert_path}")
    
    # Client Key
    client_key = os.getenv('DB_CLIENT_KEY')
    if client_key:
        client_key_path = certs_dir / 'client-key.key'
        client_key_path.write_text(client_key)
        os.chmod(client_key_path, 0o600)
        print(f"✓ Created client key: {client_key_path}")
    
    # Create a README in certs directory
    readme_path = certs_dir / 'README.md'
    readme_path.write_text("""# SSL Certificates Directory

This directory contains SSL certificates for secure database connections.
These files are generated from environment variables during deployment.

DO NOT commit these files to version control!
""")
    
    print("Certificate setup complete.")

if __name__ == '__main__':
    setup_certificates()