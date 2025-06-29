"""
WSGI config for ethicic project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os
import sys

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ethicic.settings')

try:
    # Test Django startup
    application = get_wsgi_application()
    print("✅ Django WSGI application created successfully")
    
    # Quick test that basic Django functionality works
    from django.conf import settings
    print(f"✅ Django settings loaded: DEBUG={settings.DEBUG}")
    
    # Test database connection
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
    print("✅ Database connection successful")
    
except Exception as e:
    print(f"❌ WSGI startup failed: {e}")
    import traceback
    traceback.print_exc()
    # Re-raise to ensure deployment fails if there's an issue
    raise