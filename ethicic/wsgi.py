"""
WSGI config for ethicic project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ethicic.settings')

# Initialize Django
application = get_wsgi_application()

# Run essential setup on first startup
try:
    from django.core.management import call_command
    from django.db import connection
    from django.conf import settings
    import os
    
    # Ensure static files are collected
    print("📁 Ensuring static files are available...")
    try:
        # Check if staticfiles directory exists and has content
        static_root = settings.STATIC_ROOT
        if not os.path.exists(static_root) or not os.listdir(static_root):
            print("   Collecting static files...")
            call_command('collectstatic', verbosity=0, interactive=False, clear=False)
            print("✅ Static files collected")
        else:
            print("✅ Static files already available")
    except Exception as e:
        print(f"⚠️  Static file collection failed: {e}")
    
    # Quick check if basic tables exist
    with connection.cursor() as cursor:
        try:
            cursor.execute("SELECT COUNT(*) FROM wagtailcore_site")
            print("✅ Wagtail tables exist")
        except Exception:
            print("🔧 Setting up database...")
            try:
                # Try migrations
                call_command('migrate', verbosity=0, interactive=False)
                print("✅ Migrations completed")
                
                # Set up homepage
                call_command('setup_homepage')
                print("✅ Homepage setup completed")
            except Exception as e:
                print(f"⚠️  Setup warnings: {e}")
                print("   Site will start but may need manual setup")
                
except Exception as e:
    print(f"⚠️  WSGI setup warnings: {e}")
    print("   Site starting without automatic setup")