"""
Standalone URL Configuration for Public Site

URL configuration for standalone deployment without garden platform dependencies.
"""

import datetime

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path
from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls

from public_site.homepage_view_cms import homepage_view_cms


def health_check(request):
    """Simple health check endpoint for Kinsta"""
    import os

    # Don't test database on health check to avoid 503s
    response_data = {
        "status": "healthy",
        "service": "ethicic-public",
        "version": "1.0",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }

    # Add storage debug info if requested
    if request.GET.get("debug") == "storage":
        # Test local storage
        storage_test = "UNKNOWN"
        try:
            from django.core.files.base import ContentFile
            from django.core.files.storage import default_storage

            # Test basic file operations
            test_content = "Local storage test file"
            test_file = ContentFile(test_content.encode("utf-8"))
            saved_name = default_storage.save("test_local.txt", test_file)

            # Check if file exists and can be read
            if default_storage.exists(saved_name):
                stored_file = default_storage.open(saved_name)
                content = stored_file.read().decode("utf-8")
                stored_file.close()
                storage_test = f"SUCCESS - Saved and read {len(content)} chars"
            else:
                storage_test = "FAILED - File not found after save"

            # Clean up
            default_storage.delete(saved_name)

        except Exception as e:
            storage_test = f"FAILED: {str(e)}"

        response_data.update(
            {
                "debug_mode": os.getenv("DEBUG", "False"),
                "media_url": getattr(settings, "MEDIA_URL", "NOT_SET"),
                "media_root": getattr(settings, "MEDIA_ROOT", "NOT_SET"),
                "storage_backend": getattr(settings, "STORAGES", {})
                .get("default", {})
                .get("BACKEND", "NOT_SET"),
                "storages_config": "SET"
                if hasattr(settings, "STORAGES")
                else "MISSING",
                "local_storage_test": storage_test,
            }
        )

    # Basic environment check
    if request.GET.get("env") == "check":
        import os

        response_data.update(
            {
                "django_settings_module": os.getenv(
                    "DJANGO_SETTINGS_MODULE", "NOT_SET"
                ),
                "python_path": str(settings.BASE_DIR),
                "installed_apps": len(settings.INSTALLED_APPS),
                "media_root": getattr(settings, "MEDIA_ROOT", "NOT_SET"),
                "wagtail_installed": "wagtail" in settings.INSTALLED_APPS,
                "storages_installed": "storages" in settings.INSTALLED_APPS,
            }
        )
    
    # List media files
    if request.GET.get("list") == "media":
        import os
        try:
            media_root = getattr(settings, "MEDIA_ROOT", "/var/lib/data")
            files = []
            if os.path.exists(media_root):
                for root, dirs, filenames in os.walk(media_root):
                    for filename in filenames:
                        full_path = os.path.join(root, filename)
                        rel_path = os.path.relpath(full_path, media_root)
                        size = os.path.getsize(full_path)
                        files.append({"path": rel_path, "size": size})
            response_data.update({
                "media_root": media_root,
                "files_count": len(files),
                "files": files[:10],  # Show first 10 files
            })
        except Exception as e:
            response_data.update({"media_list_error": str(e)})
    
    # Note: Removed test=media endpoint that was causing 503 errors

    return JsonResponse(response_data)


def simple_test(request):
    """Simple test endpoint that doesn't require database"""
    return JsonResponse({"message": "Hello from ethicic-public!", "status": "ok"})


def debug_image_model(request):
    """Debug Wagtail image model to see what's required"""
    if request.GET.get("test") != "image":
        return JsonResponse({"error": "Add ?test=image to run test"})

    try:
        import io

        from django.core.files.base import ContentFile
        from PIL import Image as PILImage
        from wagtail.images.models import Image

        # Create a test image
        img = PILImage.new("RGB", (100, 100), color="blue")
        img_bytes = io.BytesIO()
        img.save(img_bytes, format="JPEG")
        img_bytes.seek(0)

        # Try to create Wagtail Image model
        test_file = ContentFile(img_bytes.getvalue(), name="debug_test.jpg")

        wagtail_image = Image(
            title="Debug Test Image",
            file=test_file,
        )

        # Try to save and see what validation errors occur
        wagtail_image.full_clean()  # This will raise ValidationError if invalid
        wagtail_image.save()

        result = {
            "status": "SUCCESS",
            "image_id": wagtail_image.id,
            "image_url": wagtail_image.file.url,
            "title": wagtail_image.title,
        }

        # Clean up
        wagtail_image.delete()

        return JsonResponse(result)

    except Exception as e:
        import traceback

        return JsonResponse(
            {"status": "FAILED", "error": str(e), "traceback": traceback.format_exc()}
        )


def favicon_view(request):
    """Simple favicon handler to prevent 500 errors"""
    from django.http import HttpResponse

    return HttpResponse(status=204)  # No content


def carbon_txt_view(request):
    """Serve carbon.txt file for sustainability transparency"""
    import os

    from django.conf import settings
    from django.http import Http404, HttpResponse

    carbon_txt_path = os.path.join(settings.BASE_DIR, "static", "carbon.txt")

    if os.path.exists(carbon_txt_path):
        try:
            with open(carbon_txt_path, encoding="utf-8") as f:
                content = f.read()

            response = HttpResponse(content, content_type="text/plain")
            response["Cache-Control"] = "max-age=86400"  # 24 hour cache
            return response
        except Exception as e:
            raise Http404(f"Error reading carbon.txt: {e}")
    else:
        raise Http404("carbon.txt file not found")


def llms_txt_view(request):
    """Serve llms.txt file for AI/LLM consumption"""
    import os

    from django.conf import settings
    from django.http import Http404, HttpResponse

    llms_txt_path = os.path.join(settings.BASE_DIR, "static", "llms.txt")

    if os.path.exists(llms_txt_path):
        try:
            with open(llms_txt_path, encoding="utf-8") as f:
                content = f.read()

            response = HttpResponse(content, content_type="text/plain; charset=utf-8")
            response["Cache-Control"] = "max-age=86400"  # 24 hour cache
            return response
        except Exception as e:
            raise Http404(f"Error reading llms.txt: {e}")
    else:
        raise Http404("llms.txt file not found")


def robots_txt_view(request):
    """Serve robots.txt file for search engine crawlers"""
    import os

    from django.conf import settings
    from django.http import Http404, HttpResponse

    robots_txt_path = os.path.join(settings.BASE_DIR, "static", "robots.txt")

    if os.path.exists(robots_txt_path):
        try:
            with open(robots_txt_path, encoding="utf-8") as f:
                content = f.read()

            response = HttpResponse(content, content_type="text/plain")
            response["Cache-Control"] = "max-age=86400"  # 24 hour cache
            return response
        except Exception as e:
            raise Http404(f"Error reading robots.txt: {e}")
    else:
        raise Http404("robots.txt file not found")


def serve_media_file(request, filepath):
    """Serve media files directly in production"""
    import os
    import mimetypes
    from django.http import FileResponse, Http404
    from django.conf import settings
    
    # Build the full file path
    media_root = getattr(settings, 'MEDIA_ROOT', '/var/lib/data')
    full_path = os.path.join(media_root, filepath)
    
    # Security check: ensure the path is within media root
    if not os.path.commonpath([media_root, full_path]).startswith(media_root):
        raise Http404("File not found")
    
    # Check if file exists
    if not os.path.exists(full_path) or not os.path.isfile(full_path):
        raise Http404(f"File not found: {filepath}")
    
    # Determine content type
    content_type, _ = mimetypes.guess_type(full_path)
    if not content_type:
        content_type = 'application/octet-stream'
    
    # Serve the file
    try:
        response = FileResponse(
            open(full_path, 'rb'),
            content_type=content_type
        )
        response['Cache-Control'] = 'public, max-age=31536000'  # 1 year cache
        return response
    except Exception as e:
        raise Http404(f"Error serving file: {e}")


def debug_homepage(request):
    """Debug homepage bypass for testing"""
    try:
        from wagtail.models import Site

        from public_site.models import HomePage

        sites = list(Site.objects.all())
        homepages = list(HomePage.objects.all())

        debug_info = {
            "message": "Debug homepage endpoint",
            "sites_count": len(sites),
            "homepages_count": len(homepages),
            "sites": [
                {
                    "hostname": s.hostname,
                    "root_page_title": s.root_page.title if s.root_page else "None",
                }
                for s in sites
            ],
            "homepages": [
                {"title": h.title, "live": h.live, "url": h.url} for h in homepages
            ],
        }

        return JsonResponse(debug_info)
    except Exception as e:
        return JsonResponse({"error": str(e), "type": type(e).__name__})


def debug_static(request):
    """Debug static files configuration"""
    import os

    from django.conf import settings

    static_info = {
        "STATIC_URL": settings.STATIC_URL,
        "STATIC_ROOT": str(settings.STATIC_ROOT),
        "STATICFILES_STORAGE": settings.STATICFILES_STORAGE,
        "STATICFILES_DIRS": [str(d) for d in settings.STATICFILES_DIRS],
        "WHITENOISE_USE_FINDERS": getattr(settings, "WHITENOISE_USE_FINDERS", None),
        "WHITENOISE_AUTOREFRESH": getattr(settings, "WHITENOISE_AUTOREFRESH", None),
        "static_root_exists": os.path.exists(settings.STATIC_ROOT),
        "static_dirs_exist": [
            {"dir": str(d), "exists": os.path.exists(d)}
            for d in settings.STATICFILES_DIRS
        ],
        "middleware_installed": "whitenoise.middleware.WhiteNoiseMiddleware"
        in settings.MIDDLEWARE,
        "static_files": [],
    }

    # Check if static files exist
    if os.path.exists(settings.STATIC_ROOT):
        css_dir = os.path.join(settings.STATIC_ROOT, "css")
        if os.path.exists(css_dir):
            css_files = os.listdir(css_dir)
            static_info["css_files"] = css_files[:10]  # First 10 files

        # Check specific critical files
        critical_files = [
            "css/garden-ui-theme.css",
            "css/core-styles.css",
            "css/public-site-simple.css",
        ]
        for file_path in critical_files:
            full_path = os.path.join(settings.STATIC_ROOT, file_path)
            static_info["static_files"].append(
                {
                    "path": file_path,
                    "exists": os.path.exists(full_path),
                    "size": os.path.getsize(full_path)
                    if os.path.exists(full_path)
                    else 0,
                }
            )

    # Also check source static directory
    static_info["source_static_files"] = []
    if settings.STATICFILES_DIRS:
        source_dir = settings.STATICFILES_DIRS[0]
        if os.path.exists(source_dir):
            css_dir = os.path.join(source_dir, "css")
            if os.path.exists(css_dir):
                for file_name in [
                    "garden-ui-theme.css",
                    "core-styles.css",
                    "public-site-simple.css",
                ]:
                    full_path = os.path.join(css_dir, file_name)
                    static_info["source_static_files"].append(
                        {
                            "path": f"css/{file_name}",
                            "exists": os.path.exists(full_path),
                            "size": os.path.getsize(full_path)
                            if os.path.exists(full_path)
                            else 0,
                        }
                    )

    return JsonResponse(static_info)


def serve_css(request, filename):
    """Emergency CSS serving function"""
    import os

    from django.conf import settings
    from django.http import Http404, HttpResponse

    # Security: only serve CSS files
    if not filename.endswith(".css"):
        raise Http404("Not a CSS file")

    file_path = os.path.join(settings.STATIC_ROOT, "css", filename)

    if not os.path.exists(file_path):
        raise Http404("CSS file not found")

    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        response = HttpResponse(content, content_type="text/css")
        response["Cache-Control"] = "max-age=3600"  # 1 hour cache
        return response
    except Exception as e:
        raise Http404(f"Error reading CSS file: {e}")


def serve_manifest(request):
    """Serve manifest.json with correct content type"""
    import json
    import os

    from django.conf import settings
    from django.http import Http404, JsonResponse

    manifest_path = os.path.join(settings.STATIC_ROOT, "manifest.json")
    if not os.path.exists(manifest_path):
        # Try static directory if staticfiles not collected
        manifest_path = os.path.join(settings.BASE_DIR, "static", "manifest.json")

    if os.path.exists(manifest_path):
        try:
            with open(manifest_path, encoding="utf-8") as f:
                manifest_data = json.load(f)
            response = JsonResponse(manifest_data)
            response["Cache-Control"] = "max-age=3600"
            return response
        except Exception as e:
            raise Http404(f"Error reading manifest: {e}")
    else:
        raise Http404("Manifest file not found")


def debug_static_file(request, filepath):
    """Serve static files with proper MIME types"""
    import mimetypes
    import os

    from django.conf import settings
    from django.http import Http404, HttpResponse

    # For CSS and other static files, serve them directly
    full_path = os.path.join(settings.STATIC_ROOT, filepath)

    # Special handling for missing static files - return appropriate empty content instead of 404
    if not os.path.exists(full_path):
        if filepath.endswith(".css"):
            response = HttpResponse(
                "/* CSS file not found - serving empty CSS to prevent MIME type errors */",
                content_type="text/css",
            )
            response["Cache-Control"] = "max-age=60"  # Short cache for missing files
            return response
        if filepath.endswith(".js"):
            response = HttpResponse(
                "// JS file not found", content_type="application/javascript"
            )
            response["Cache-Control"] = "max-age=60"
            return response
        if filepath.endswith((".png", ".jpg", ".jpeg", ".gif", ".ico")):
            # Return a 1x1 transparent pixel for missing images
            from base64 import b64decode

            pixel = b64decode(
                "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
            )
            response = HttpResponse(pixel, content_type="image/png")
            response["Cache-Control"] = "max-age=60"
            return response
        if filepath.endswith(".json"):
            response = HttpResponse("{}", content_type="application/json")
            response["Cache-Control"] = "max-age=60"
            return response

    if not os.path.exists(full_path):
        raise Http404(f"Static file not found: {filepath}")

    # Get MIME type
    content_type, _ = mimetypes.guess_type(full_path)
    if not content_type:
        # Default MIME types for common extensions
        if filepath.endswith(".css"):
            content_type = "text/css"
        elif filepath.endswith(".js"):
            content_type = "application/javascript"
        elif filepath.endswith(".png"):
            content_type = "image/png"
        elif filepath.endswith((".jpg", ".jpeg")):
            content_type = "image/jpeg"
        elif filepath.endswith(".svg"):
            content_type = "image/svg+xml"
        else:
            content_type = "application/octet-stream"

    try:
        # For text files, read as text
        if content_type.startswith("text/") or content_type in [
            "application/javascript",
            "image/svg+xml",
        ]:
            with open(full_path, encoding="utf-8") as f:
                content = f.read()
        else:
            # For binary files, read as binary
            with open(full_path, "rb") as f:
                content = f.read()

        response = HttpResponse(content, content_type=content_type)
        response["Cache-Control"] = "max-age=3600"  # 1 hour cache
        return response

    except Exception as e:
        raise Http404(f"Error reading static file: {e}")


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
    # Let WhiteNoise handle static files - don't intercept them
    # path('static/<path:filepath>', debug_static_file, name='debug_static_serve'),
    # Manifest.json disabled due to serving issues
    # path('manifest.json', serve_manifest, name='serve_manifest'),
    # path('static/manifest.json', serve_manifest, name='serve_manifest_static'),
    # Homepage - MUST be first
    path("", homepage_view_cms, name="homepage"),
    # Health check
    path("health/", health_check, name="health_check"),
    path("test/", simple_test, name="simple_test"),
    path("debug-image/", debug_image_model, name="debug_image"),
    path("debug-homepage/", debug_homepage, name="debug_homepage"),
    path("debug-static/", debug_static, name="debug_static"),
    path("debug-file/<path:filepath>", debug_static_file, name="debug_static_file"),
    path("emergency-css/<str:filename>", serve_css, name="serve_css"),
    path("favicon.ico", favicon_view, name="favicon"),
    # Direct media serving for production
    path("media/<path:filepath>", serve_media_file, name="serve_media"),
    # Sustainability transparency
    path("carbon.txt", carbon_txt_view, name="carbon_txt"),
    # AI/LLM information file
    path("llms.txt", llms_txt_view, name="llms_txt"),
    # Search engine crawler instructions
    path("robots.txt", robots_txt_view, name="robots_txt"),
    # Admin
    path("admin/", admin.site.urls),
    path("cms/", include(wagtailadmin_urls)),
    # Documents
    path("documents/", include(wagtaildocs_urls)),
    # Emergency homepage for debugging
    path("emergency/", emergency_homepage, name="emergency_homepage"),
    # Include all public_site URLs
    path("", include("public_site.urls")),
    # Wagtail CMS URLs - this will handle other Wagtail pages
    path("", include(wagtail_urls)),
]

# Serve static and media files
# In production, WhiteNoise middleware handles static files
# Only add Django's static serving in DEBUG mode
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Media files need to be served in both DEBUG and production
# IMPORTANT: This must be BEFORE Wagtail URLs to prevent conflicts
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Custom error handlers
handler404 = "public_site.views.custom_404"
handler500 = "public_site.views.custom_500"
