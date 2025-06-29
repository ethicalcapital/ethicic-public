"""
Standalone URL Configuration for Public Site

URL configuration for standalone deployment without garden platform dependencies.
"""

from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from wagtail.admin import urls as wagtailadmin_urls
from wagtail import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls


def health_check(request):
    """Simple health check endpoint for Kinsta"""
    try:
        # Test database connection
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return JsonResponse({
        'status': 'healthy',
        'service': 'ethicic-public',
        'database': db_status,
        'debug': getattr(settings, 'DEBUG', False)
    })

def simple_test(request):
    """Simple test endpoint that doesn't require database"""
    return JsonResponse({'message': 'Hello from ethicic-public!', 'status': 'ok'})

def favicon_view(request):
    """Simple favicon handler to prevent 500 errors"""
    from django.http import HttpResponse
    return HttpResponse(status=204)  # No content

def debug_homepage(request):
    """Debug homepage bypass for testing"""
    try:
        from wagtail.models import Site
        from public_site.models import HomePage
        
        sites = list(Site.objects.all())
        homepages = list(HomePage.objects.all())
        
        debug_info = {
            'message': 'Debug homepage endpoint',
            'sites_count': len(sites),
            'homepages_count': len(homepages),
            'sites': [{'hostname': s.hostname, 'root_page_title': s.root_page.title if s.root_page else 'None'} for s in sites],
            'homepages': [{'title': h.title, 'live': h.live, 'url': h.url} for h in homepages]
        }
        
        return JsonResponse(debug_info)
    except Exception as e:
        return JsonResponse({'error': str(e), 'type': type(e).__name__})

def debug_static(request):
    """Debug static files configuration"""
    import os
    from django.conf import settings
    
    static_info = {
        'STATIC_URL': settings.STATIC_URL,
        'STATIC_ROOT': str(settings.STATIC_ROOT),
        'STATICFILES_STORAGE': settings.STATICFILES_STORAGE,
        'WHITENOISE_USE_FINDERS': getattr(settings, 'WHITENOISE_USE_FINDERS', None),
        'static_root_exists': os.path.exists(settings.STATIC_ROOT),
        'static_files': []
    }
    
    # Check if static files exist
    if os.path.exists(settings.STATIC_ROOT):
        css_dir = os.path.join(settings.STATIC_ROOT, 'css')
        if os.path.exists(css_dir):
            css_files = os.listdir(css_dir)
            static_info['css_files'] = css_files[:10]  # First 10 files
        
        # Check specific critical files
        critical_files = ['css/garden-ui-theme.css', 'css/critical.css']
        for file_path in critical_files:
            full_path = os.path.join(settings.STATIC_ROOT, file_path)
            static_info['static_files'].append({
                'path': file_path,
                'exists': os.path.exists(full_path),
                'size': os.path.getsize(full_path) if os.path.exists(full_path) else 0
            })
    
    return JsonResponse(static_info)

def serve_css(request, filename):
    """Emergency CSS serving function"""
    import os
    from django.conf import settings
    from django.http import HttpResponse, Http404
    
    # Security: only serve CSS files
    if not filename.endswith('.css'):
        raise Http404("Not a CSS file")
    
    file_path = os.path.join(settings.STATIC_ROOT, 'css', filename)
    
    if not os.path.exists(file_path):
        raise Http404("CSS file not found")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        response = HttpResponse(content, content_type='text/css')
        response['Cache-Control'] = 'max-age=3600'  # 1 hour cache
        return response
    except Exception as e:
        raise Http404(f"Error reading CSS file: {e}")

def debug_static_file(request, filepath):
    """Debug what's happening with static file requests"""
    import os
    from django.conf import settings
    from django.http import JsonResponse
    
    full_path = os.path.join(settings.STATIC_ROOT, filepath)
    
    debug_info = {
        'requested_path': filepath,
        'full_path': full_path,
        'static_root': str(settings.STATIC_ROOT),
        'file_exists': os.path.exists(full_path),
        'static_root_exists': os.path.exists(settings.STATIC_ROOT),
        'directory_contents': []
    }
    
    if os.path.exists(full_path):
        debug_info['file_size'] = os.path.getsize(full_path)
        if filepath.endswith('.css'):
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()[:200]  # First 200 chars
                debug_info['file_preview'] = content
            except Exception as e:
                debug_info['read_error'] = str(e)
    
    # Check directory contents
    dir_path = os.path.dirname(full_path)
    if os.path.exists(dir_path):
        try:
            debug_info['directory_contents'] = os.listdir(dir_path)[:10]
        except Exception as e:
            debug_info['directory_error'] = str(e)
    
    return JsonResponse(debug_info)

def emergency_homepage(request):
    """Emergency bypass homepage for debugging"""
    from django.http import HttpResponse
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Ethical Capital - Emergency Mode</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .status { background: #e8f5e8; padding: 20px; border-radius: 8px; }
        </style>
    </head>
    <body>
        <div class="status">
            <h1>Ethical Capital Investment Collaborative</h1>
            <p><strong>Status:</strong> Emergency mode - site is operational</p>
            <p><strong>Working endpoints:</strong></p>
            <ul>
                <li><a href="/health/">Health Check</a></li>
                <li><a href="/test/">Simple Test</a></li>
                <li><a href="/debug-homepage/">Debug Info</a></li>
                <li><a href="/cms/">Admin Panel</a></li>
            </ul>
            <p>If you're seeing this, the application is running correctly but Wagtail routing may need configuration.</p>
        </div>
    </body>
    </html>
    """
    return HttpResponse(html)

urlpatterns = [
    # Health check 
    path('health/', health_check, name='health_check'),
    path('test/', simple_test, name='simple_test'),
    path('debug-homepage/', debug_homepage, name='debug_homepage'),
    path('debug-static/', debug_static, name='debug_static'),
    path('debug-file/<path:filepath>', debug_static_file, name='debug_static_file'),
    path('emergency-css/<str:filename>', serve_css, name='serve_css'),
    path('favicon.ico', favicon_view, name='favicon'),
    
    # Admin
    path('admin/', admin.site.urls),
    path('cms/', include(wagtailadmin_urls)),
    
    # Documents
    path('documents/', include(wagtaildocs_urls)),
    
    # Emergency homepage for debugging
    path('emergency/', emergency_homepage, name='emergency_homepage'),
    
    # Include all public_site URLs
    path('', include('public_site.urls')),
    
    # Wagtail CMS URLs - this will handle homepage and all other Wagtail pages
    path('', include(wagtail_urls)),
]

# Serve static and media files
# Custom static file serving with explicit MIME types
def serve_static_with_mimetype(request, path):
    """Serve static files with explicit MIME types"""
    import os
    import mimetypes
    from django.http import HttpResponse, Http404
    from django.conf import settings
    
    # Security check
    if '..' in path or path.startswith('/'):
        raise Http404("Invalid path")
    
    file_path = os.path.join(settings.STATIC_ROOT, path)
    
    if not os.path.exists(file_path) or not os.path.isfile(file_path):
        raise Http404("File not found")
    
    # Determine MIME type
    content_type, _ = mimetypes.guess_type(file_path)
    
    # Force correct MIME types for common file types
    if path.endswith('.css'):
        content_type = 'text/css'
    elif path.endswith('.js'):
        content_type = 'application/javascript'
    elif path.endswith('.json'):
        content_type = 'application/json'
    elif not content_type:
        content_type = 'application/octet-stream'
    
    try:
        if content_type.startswith('text/') or content_type in ['application/javascript', 'application/json']:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        else:
            with open(file_path, 'rb') as f:
                content = f.read()
        
        response = HttpResponse(content, content_type=content_type)
        response['Cache-Control'] = 'max-age=3600'  # 1 hour cache
        return response
    except Exception as e:
        raise Http404(f"Error reading file: {e}")

from django.urls import re_path

# Use custom static file serving
urlpatterns += [
    re_path(r'^static/(?P<path>.*)$', serve_static_with_mimetype, name='static_files'),
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]

# Custom error handlers
handler404 = 'public_site.views.custom_404'
handler500 = 'public_site.views.custom_500'