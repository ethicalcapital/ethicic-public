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
    # SSL certificate paths for different environments
    ssl_cert_paths = [
        '/app/config/ssl/ubicloud-root-ca.pem',           # Docker/production (Kinsta)
        './config/ssl/ubicloud-root-ca.pem',              # Relative path from app root
        '/home/ec1c/garden/ethicic-public/config/ssl/ubicloud-root-ca.pem',  # Full path
        os.environ.get('SSL_ROOT_CERT'),                  # Environment override
        os.environ.get('DB_CA_CERT_PATH'),                # Alternative env var
        os.environ.get('UBI_DB_CA_CERT_PATH'),            # Ubicloud specific env var
    ]
    
    # Find the first available SSL certificate
    for cert_path in ssl_cert_paths:
        if cert_path and Path(cert_path).exists():
            return str(cert_path)  # Ensure it's a string, not Path object
    
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
    
    # Parse database URL - use dj_database_url for better parsing
    try:
        import dj_database_url
        base_config = dj_database_url.parse(database_url)
        
        print(f"🔍 Configuring database connection to: {base_config['HOST']}")
        print(f"   Port: {base_config['PORT']}")
        print(f"   Database: {base_config['NAME']}")
        
        # Extract connection details from parsed config
        host = base_config['HOST']
        port = base_config['PORT']
        name = base_config['NAME']
        user = base_config['USER']
        password = base_config['PASSWORD']
        
    except ImportError:
        # Fallback to manual parsing
        parsed = urlparse(database_url)
        print(f"🔍 Configuring database connection to: {parsed.hostname}")
        print(f"   Port: {parsed.port or 5432}")
        print(f"   Database: {parsed.path[1:]}")
        
        host = parsed.hostname
        port = parsed.port or 5432
        name = parsed.path[1:]
        user = parsed.username
        password = parsed.password
    
    # SSL options following garden app pattern
    ssl_options = {
        'application_name': 'ethicic_public',
        'connect_timeout': '10',  # Reduce timeout to match garden app
    }
    
    # Configure SSL - try certificate first if available
    ssl_cert_path = get_ssl_cert_path()
    
    if ssl_cert_path:
        # Try full SSL verification with certificate first
        ssl_options['sslmode'] = 'verify-full'
        ssl_options['sslrootcert'] = ssl_cert_path
        print(f"✅ Found SSL certificate, attempting secure connection: {ssl_cert_path}")
    else:
        # Fallback to SSL without certificate verification (still encrypted)
        ssl_options['sslmode'] = 'require'
        print("⚠️  No SSL certificate found - using encrypted connection without verification")
    
    config = {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': name,
        'USER': user,
        'PASSWORD': password,
        'HOST': host,
        'PORT': port,
        'OPTIONS': ssl_options,
        'CONN_MAX_AGE': 600,  # 10 minutes connection pooling
        'CONN_HEALTH_CHECKS': True,  # Enable health checks
    }
    
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