"""
Standalone URL Configuration for Public Site

URL configuration for standalone deployment without garden platform dependencies.
"""

from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from wagtail.admin import urls as wagtailadmin_urls
from wagtail import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls

# Import public site views
from public_site import views

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    path('cms/', include(wagtailadmin_urls)),
    
    # Documents
    path('documents/', include(wagtaildocs_urls)),
    
    # API endpoints
    path('api/v1/contact/', views.contact_api, name='contact_form_api'),
    path('api/v1/newsletter/', views.newsletter_api, name='newsletter_signup_api'),
    path('api/v1/media-items/', views.media_items_api, name='media_items_api'),
    
    # Contact form submissions
    path('contact/submit/', views.contact_form_submit, name='contact_form_submit'),
    path('newsletter/signup/', views.newsletter_signup, name='newsletter_signup'),
    path('onboarding/submit/', views.onboarding_form_submit, name='onboarding_form_submit'),
    
    # Wagtail CMS URLs (should be last)
    path('', include(wagtail_urls)),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Custom error handlers - commented out until implemented
# handler404 = 'public_site.views.custom_404'
# handler500 = 'public_site.views.custom_500'