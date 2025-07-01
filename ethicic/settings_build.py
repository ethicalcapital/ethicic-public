"""
Minimal settings for build phase - avoids database connections
"""
from .settings import *

# Override database to use SQLite for build phase
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Disable all external connections during build
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Ensure we have a SECRET_KEY for build
SECRET_KEY = os.getenv('SECRET_KEY', 'build-phase-temporary-key')

# Disable debug for build
DEBUG = False

# Allow all hosts during build
ALLOWED_HOSTS = ['*']

# Ensure static files settings are correct
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Use simple static files storage for build
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'