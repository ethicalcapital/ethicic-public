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
    try:
        # Try fake-initial first to handle existing schemas
        call_command('migrate', fake_initial=True, verbosity=0, interactive=False)
        print("✅ Database migrations completed (fake-initial)")
    except Exception as e:
        print(f"⚠️  Fake-initial failed: {e}")
        try:
            # Fall back to regular migration
            call_command('migrate', verbosity=0, interactive=False)
            print("✅ Database migrations completed (regular)")
        except Exception as e2:
            print(f"⚠️  Migration warnings: {e2}")
            print("   Site will start but may have schema issues")
    
    # Collect static files (essential for CSS/JS serving)
    print("📁 Collecting static files...")
    
    # Ensure staticfiles directory exists
    import os
    import shutil
    staticfiles_root = settings.STATIC_ROOT
    static_source = settings.BASE_DIR / 'static'
    
    print(f"   Static source: {static_source}")
    print(f"   Static root: {staticfiles_root}")
    
    os.makedirs(staticfiles_root, exist_ok=True)
    
    # Manual copy as fallback since collectstatic might be failing
    if os.path.exists(static_source):
        print("📁 Manually copying static files...")
        try:
            # Copy CSS files
            css_source = static_source / 'css'
            css_dest = staticfiles_root / 'css'
            if os.path.exists(css_source):
                os.makedirs(css_dest, exist_ok=True)
                for css_file in os.listdir(css_source):
                    if css_file.endswith('.css'):
                        shutil.copy2(css_source / css_file, css_dest / css_file)
                        print(f"   Copied: {css_file}")
            
            # Copy JS files
            js_source = static_source / 'js'
            js_dest = staticfiles_root / 'js'
            if os.path.exists(js_source):
                os.makedirs(js_dest, exist_ok=True)
                for js_file in os.listdir(js_source):
                    if js_file.endswith('.js'):
                        shutil.copy2(js_source / js_file, js_dest / js_file)
                        print(f"   Copied: {js_file}")
            
            print("✅ Manual static file copy completed")
        except Exception as e:
            print(f"⚠️  Manual copy failed: {e}")
    
    # Now try Django's collectstatic
    try:
        call_command('collectstatic', verbosity=0, interactive=False, clear=False)
        print("✅ Django collectstatic completed")
    except Exception as e:
        print(f"⚠️  Django collectstatic failed: {e}")
    
    # Verify critical CSS files exist
    critical_files = [
        'css/garden-ui-theme.css',
        'css/critical.css',
        'css/critical-fouc-prevention.css'
    ]
    
    missing_files = []
    existing_files = []
    for file_path in critical_files:
        full_path = os.path.join(staticfiles_root, file_path)
        if not os.path.exists(full_path):
            missing_files.append(file_path)
        else:
            size = os.path.getsize(full_path)
            existing_files.append(f"{file_path} ({size} bytes)")
    
    if missing_files:
        print(f"⚠️  Missing critical CSS files: {missing_files}")
    if existing_files:
        print(f"✅ Found CSS files: {existing_files}")
    
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
        
        # Always ensure homepage is properly configured
        print("🏠 Checking homepage configuration...")
        from django.core.management import call_command
        
        try:
            # Check if we have a proper homepage configured
            sites = Site.objects.filter(is_default_site=True)
            homepage_needs_setup = True
            
            if sites.exists():
                site = sites.first()
                try:
                    # Check if root page is a HomePage
                    if isinstance(site.root_page.specific, HomePage):
                        # Check if homepage has content
                        homepage = site.root_page.specific
                        if homepage.title and homepage.title != "Welcome to your new Wagtail site!":
                            print("✅ Homepage already properly configured")
                            homepage_needs_setup = False
                except Exception as e:
                    print(f"⚠️  Error checking homepage: {e}")
            
            if homepage_needs_setup:
                print("🏠 Setting up homepage...")
                call_command('setup_homepage')
                print("✅ Homepage setup completed")
                
        except Exception as setup_error:
            print(f"⚠️  Homepage setup failed: {setup_error}")
            print("   Site will start but may show 404 for homepage")
                
    except Exception as setup_error:
        print(f"⚠️  Auto-setup failed (non-critical): {setup_error}")
    
except Exception as e:
    print(f"❌ WSGI startup failed: {e}")
    import traceback
    traceback.print_exc()
    # Re-raise to ensure deployment fails if there's an issue
    raise