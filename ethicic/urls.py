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

urlpatterns = [
    # Health check (must be first)
    path('health/', health_check, name='health_check'),
    path('test/', simple_test, name='simple_test'),
    path('favicon.ico', favicon_view, name='favicon'),
    
    # Admin
    path('admin/', admin.site.urls),
    path('cms/', include(wagtailadmin_urls)),
    
    # Documents
    path('documents/', include(wagtaildocs_urls)),
    
    # Include all public_site URLs
    path('', include('public_site.urls')),
    
    # Wagtail CMS URLs (should be last)
    path('', include(wagtail_urls)),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Custom error handlers
handler404 = 'public_site.views.custom_404'
handler500 = 'public_site.views.custom_500'