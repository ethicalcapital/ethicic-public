#!/usr/bin/env python3
"""
Standalone test runner for public_site app
Creates a minimal Django environment to run the tests
"""
import os
import sys
import tempfile
from pathlib import Path

# Get the directory containing this script
BASE_DIR = Path(__file__).resolve().parent

# Set up minimal Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_settings')
os.environ['USE_SQLITE'] = 'true'
os.environ['DEBUG'] = 'true'
os.environ['SECRET_KEY'] = 'test-secret-key-for-testing-only'

# Add the project root to Python path
sys.path.insert(0, str(BASE_DIR))

# Create minimal test settings
test_settings_content = f"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

SECRET_KEY = 'test-secret-key-for-testing-only'
DEBUG = True
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    
    # Wagtail core
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
    'crispy_forms',
    'crispy_bootstrap4',
    
    # Our app
    'public_site',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'wagtail.contrib.redirects.middleware.RedirectMiddleware',
]

ROOT_URLCONF = 'public_site.urls'

TEMPLATES = [
    {{
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {{
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        }},
    }},
]

DATABASES = {{
    'default': {{
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }}
}}

USE_TZ = True
STATIC_URL = '/static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Wagtail settings
WAGTAIL_SITE_NAME = 'Test Site'

# Rest framework
REST_FRAMEWORK = {{
    'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.AllowAny'],
}}

# Crispy forms
CRISPY_TEMPLATE_PACK = "bootstrap4"

# Test settings
TESTING = True
CONTACT_EMAIL = 'test@example.com'
DEFAULT_FROM_EMAIL = 'test@example.com'
"""

# Write the test settings to a temporary file
with open(BASE_DIR / 'test_settings.py', 'w') as f:
    f.write(test_settings_content)

try:
    import django
    from django.conf import settings
    from django.test.utils import get_runner
    from django.core.management import execute_from_command_line
    
    django.setup()
    
    # Run migrations to set up test database
    print("Setting up test database...")
    from django.core.management import call_command
    call_command('migrate', verbosity=0, interactive=False)
    
    # Run the tests
    print("🧪 Running public_site tests...")
    
    # Use Django's test runner
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=2, interactive=False, keepdb=False)
    
    # Discover and run tests
    failures = test_runner.run_tests([
        'public_site.tests.integration.test_user_flows.NewsletterSubscriptionFlowTest.test_newsletter_with_existing_contact',
        'public_site.tests.integration.test_user_flows.OnboardingFlowTest.test_complete_onboarding_flow', 
        'public_site.tests.integration.test_user_flows.ErrorHandlingFlowTest.test_rate_limiting_flow',
        'public_site.tests.views.test_form_views.OnboardingFormViewTest.test_onboarding_form_success',
    ])
    
    if failures:
        print(f"❌ {failures} test(s) failed")
        sys.exit(1)
    else:
        print("✅ All specified tests passed!")
        sys.exit(0)
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
finally:
    # Clean up
    test_settings_file = BASE_DIR / 'test_settings.py'
    if test_settings_file.exists():
        test_settings_file.unlink()