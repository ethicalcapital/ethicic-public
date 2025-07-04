"""
Build-time settings for Kinsta deployment
Forces SQLite to avoid external database connections during Docker build
"""

# Import only what we need from settings
from .settings import BASE_DIR

# Override database configuration for build phase
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Disable database routers during build
DATABASE_ROUTERS = []

# Ensure we're not in debug mode
DEBUG = False

print("Using build settings - SQLite mode enforced")