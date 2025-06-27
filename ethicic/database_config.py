"""
Centralized database configuration module for ethicic-public
Based on garden app's database configuration approach
"""

import os
from pathlib import Path
from urllib.parse import urlparse

def get_ssl_cert_path():
    """
    Find SSL certificate following garden app's pattern
    Checks multiple locations in order of preference
    """
    base_dir = Path(__file__).resolve().parent.parent
    
    cert_locations = [
        # Environment variable override
        os.getenv('SSL_ROOT_CERT'),
        os.getenv('DB_CA_CERT_PATH'),
        # Production Docker path
        '/app/config/ssl/ubicloud-root-ca.pem',
        # Local development path
        base_dir / 'config' / 'ssl' / 'ubicloud-root-ca.pem',
        # Garden shared certificate
        base_dir.parent / 'config' / 'ssl' / 'ubicloud-root-ca.pem',
        # Fallback certs directory
        base_dir / 'certs' / 'ca-certificate.crt',
    ]
    
    for cert_path in cert_locations:
        if cert_path and Path(cert_path).exists():
            return str(cert_path)
    
    return None


def get_database_config(database_url=None):
    """
    Generate database configuration with SSL and optimization settings
    Following garden app's configuration pattern
    """
    if not database_url:
        database_url = os.getenv('UBI_DATABASE_URL') or os.getenv('DATABASE_URL')
    
    if not database_url:
        return None
    
    # Parse database URL
    parsed = urlparse(database_url)
    
    config = {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': parsed.path[1:],  # Remove leading slash
        'USER': parsed.username,
        'PASSWORD': parsed.password,
        'HOST': parsed.hostname,
        'PORT': parsed.port or 5432,
        'CONN_MAX_AGE': 600,  # 10 minutes connection pooling
        'CONN_HEALTH_CHECKS': True,  # Enable health checks
        'OPTIONS': {
            'application_name': 'ethicic_public',
            'sslmode': 'require',
            'connect_timeout': '30',
            'options': '-c search_path=public,pg_catalog -c statement_timeout=60s',
        }
    }
    
    # Add SSL certificate if available
    ssl_cert = get_ssl_cert_path()
    if ssl_cert:
        config['OPTIONS']['sslrootcert'] = ssl_cert
        print(f"✅ Using SSL certificate: {ssl_cert}")
    else:
        print("⚠️  No SSL certificate found - connection will use sslmode=require without cert validation")
    
    return config


def validate_database_config():
    """
    Validate that required database configuration is present
    Similar to garden app's validation
    """
    errors = []
    
    # Check for database URL
    if not os.getenv('UBI_DATABASE_URL') and not os.getenv('DATABASE_URL'):
        errors.append("No database URL configured (UBI_DATABASE_URL or DATABASE_URL)")
    
    # Check for SSL certificate
    if not get_ssl_cert_path():
        errors.append("No SSL certificate found for secure database connection")
    
    # Validate environment
    required_vars = ['SECRET_KEY']
    for var in required_vars:
        if not os.getenv(var):
            errors.append(f"Required environment variable {var} not set")
    
    return errors


def get_cache_database_config():
    """
    Get configuration for local SQLite cache database
    """
    base_dir = Path(__file__).resolve().parent.parent
    
    return {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': base_dir / 'cache.sqlite3',
    }