"""
Standalone Django Settings for Public Site Deployment

This settings file is designed for standalone deployment of the public site
without dependencies on the main garden platform.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    # During build phase, use a temporary key
    import uuid
    SECRET_KEY = f"build-phase-key-{uuid.uuid4().hex}"
    print("⚠️  Using temporary SECRET_KEY for build phase")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '*').split(',')
# Add Kinsta temporary domain support
if os.getenv('KINSTA_DOMAIN'):
    ALLOWED_HOSTS.append(os.getenv('KINSTA_DOMAIN'))
    ALLOWED_HOSTS.append(f"*.{os.getenv('KINSTA_DOMAIN')}")
    
# Temporary: Allow all hosts if not specified
if ALLOWED_HOSTS == ['*']:
    ALLOWED_HOSTS = ['*']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    
    # Wagtail dependencies
    'wagtail.contrib.forms',
    'wagtail.contrib.redirects',
    'wagtail.embeds',
    'wagtail.sites',
    'wagtail.users',
    'wagtail.snippets',
    'wagtail.documents',
    'wagtail.images',
    'wagtail.search',
    'wagtail.admin',
    'wagtail',
    
    'modelcluster',
    'taggit',
    'rest_framework',
    
    # Third party apps
    'crispy_forms',
    'crispy_bootstrap4',
    
    # Local apps
    'public_site',
]

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap4"
CRISPY_TEMPLATE_PACK = "bootstrap4"

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # For static files in production
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'wagtail.contrib.redirects.middleware.RedirectMiddleware',
]

ROOT_URLCONF = 'ethicic.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'ethicic.wsgi.application'

# Database Configuration
# Hybrid approach: Ubicloud as primary, local SQLite as cache
DATABASE_URL = os.getenv('DATABASE_URL')
UBI_DATABASE_URL = os.getenv('UBI_DATABASE_URL')

# Configure databases based on environment
# IMPORTANT: Check USE_SQLITE first for build phase
if os.getenv('USE_SQLITE', 'False').lower() == 'true':
    # Build phase or development - use SQLite only
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
elif UBI_DATABASE_URL:
    # Production mode: Try Ubicloud, fallback to SQLite
    from .database_config import get_database_config, get_cache_database_config
    
    # Test if we can connect to Ubicloud first
    def test_database_connection(config):
        """Test database connection without hanging the startup"""
        try:
            import psycopg2
            import socket
            
            # Quick socket test first (1 second timeout)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((config['HOST'], int(config['PORT'])))
            sock.close()
            
            if result != 0:
                return False
                
            # Quick database connection test
            conn = psycopg2.connect(
                host=config['HOST'],
                port=config['PORT'],
                database=config['NAME'],
                user=config['USER'],
                password=config['PASSWORD'],
                connect_timeout=3,
                sslmode='require'
            )
            conn.close()
            return True
        except Exception as e:
            print(f"⚠️  Database connection test failed: {e}")
            return False
    
    # Get Ubicloud configuration
    ubicloud_config = get_database_config(UBI_DATABASE_URL)
    
    if ubicloud_config and test_database_connection(ubicloud_config):
        print("✅ Ubicloud database connection successful")
        DATABASES = {
            # Ubicloud as primary database with SSL
            'default': ubicloud_config,
            'ubicloud': ubicloud_config.copy(),
            
            # Local SQLite cache for frequently accessed data
            'cache': get_cache_database_config()
        }
        
        # Use database router for hybrid approach
        DATABASE_ROUTERS = ['public_site.db_router.HybridDatabaseRouter']
    else:
        # Fallback to SQLite if Ubicloud is unavailable
        print("⚠️  Ubicloud database unavailable, using SQLite fallback")
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': BASE_DIR / 'db.sqlite3',
            }
        }
    
elif DATABASE_URL and DATABASE_URL != 'sqlite':
    # Kinsta database only (fallback)
    import dj_database_url
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL, conn_max_age=600)
    }
    
else:
    # Manual PostgreSQL configuration
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('DB_NAME', 'public_site'),
            'USER': os.getenv('DB_USER', 'postgres'),
            'PASSWORD': os.getenv('DB_PASSWORD', 'password'),
            'HOST': os.getenv('DB_HOST', 'localhost'),
            'PORT': os.getenv('DB_PORT', '5432'),
            'OPTIONS': {
                'sslmode': os.getenv('DB_SSLMODE', 'prefer'),
                'sslcert': os.getenv('DB_SSLCERT', ''),
                'sslkey': os.getenv('DB_SSLKEY', ''),
                'sslrootcert': os.getenv('DB_SSLROOTCERT', ''),
            } if any([
                os.getenv('DB_SSLMODE'),
                os.getenv('DB_SSLCERT'),
                os.getenv('DB_SSLKEY'),
                os.getenv('DB_SSLROOTCERT')
            ]) else {}
        }
    }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# WhiteNoise settings for static file serving
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = DEBUG

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Wagtail settings
WAGTAIL_SITE_NAME = 'Ethical Capital'
WAGTAILADMIN_BASE_URL = os.getenv('WAGTAILADMIN_BASE_URL', 'https://ethicic.com')

# Email configuration
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = os.getenv('EMAIL_HOST', '')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True').lower() == 'true'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'noreply@ethicic.com')

# Contact form email
CONTACT_EMAIL = os.getenv('CONTACT_EMAIL', 'hello@ethicic.com')

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
}

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'public_site.log',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'public_site': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# Security settings for production
if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_REDIRECT_EXEMPT = []
    # Disable SSL redirect - handled by Kinsta load balancer
    # SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    X_FRAME_OPTIONS = 'DENY'

# Cache configuration - Use Redis for query/session caching
REDIS_URL = os.getenv('REDIS_URL')

if REDIS_URL:
    # Production: Use Redis for caching
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': REDIS_URL,
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                'PARSER_CLASS': 'redis.connection.HiredisParser',
                'CONNECTION_POOL_KWARGS': {
                    'max_connections': 50,
                    'retry_on_timeout': True,
                },
                'PICKLE_VERSION': -1,
            }
        },
        # Separate cache for sessions
        'session': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': REDIS_URL,
            'KEY_PREFIX': 'session',
            'TIMEOUT': 86400,  # 24 hours
        }
    }
    
    # Use Redis for sessions
    SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
    SESSION_CACHE_ALIAS = 'session'
    
else:
    # Development: Use local memory cache
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake',
        }
    }

# Cache middleware settings
CACHE_MIDDLEWARE_ALIAS = 'default'
CACHE_MIDDLEWARE_SECONDS = 300  # 5 minutes
CACHE_MIDDLEWARE_KEY_PREFIX = 'ethicic'