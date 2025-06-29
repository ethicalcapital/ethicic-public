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
    
    # Run database migrations on startup
    print("📊 Running database migrations...")
    from django.core.management import call_command
    call_command('migrate', verbosity=0, interactive=False)
    print("✅ Database migrations completed")
    
    # Collect static files
    print("📁 Collecting static files...")
    call_command('collectstatic', verbosity=0, interactive=False)
    print("✅ Static files collected")
    
    # Test database connection
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
    print("✅ Database connection successful")
    
    # Auto-setup site structure if this is a fresh deployment
    try:
        from wagtail.models import Site
        from public_site.models import HomePage
        
        # Check if we have a proper homepage configured
        sites = Site.objects.filter(is_default_site=True)
        if not sites.exists():
            print("🏠 No default site found - running auto-setup...")
            from django.core.management import call_command
            call_command('setup_homepage')
            print("✅ Site setup completed automatically")
        else:
            site = sites.first()
            try:
                # Check if root page is a HomePage
                if not isinstance(site.root_page.specific, HomePage):
                    print("🏠 Default site not pointing to HomePage - running auto-setup...")
                    from django.core.management import call_command
                    call_command('setup_homepage')
                    print("✅ Site setup completed automatically")
                else:
                    print("✅ Site already properly configured")
            except Exception:
                # If there's any issue checking the homepage, just run setup
                print("🏠 Issue with current site config - running auto-setup...")
                from django.core.management import call_command
                call_command('setup_homepage')
                print("✅ Site setup completed automatically")
                
    except Exception as setup_error:
        print(f"⚠️  Auto-setup failed (non-critical): {setup_error}")
    
except Exception as e:
    print(f"❌ WSGI startup failed: {e}")
    import traceback
    traceback.print_exc()
    # Re-raise to ensure deployment fails if there's an issue
    raise