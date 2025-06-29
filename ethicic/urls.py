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

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Custom error handlers
handler404 = 'public_site.views.custom_404'
handler500 = 'public_site.views.custom_500'