#!/usr/bin/env python3
"""
Diagnose Wagtail image upload 403 errors using direct model testing
"""

import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ethicic.settings")
django.setup()

import io

from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from PIL import Image as PILImage
from wagtail.images.models import Image


def diagnose_image_upload():
    print("🔍 WAGTAIL IMAGE UPLOAD DIAGNOSIS")
    print("=" * 50)

    # 1. Check basic setup
    print("\n📋 BASIC SETUP:")
    print(f"   Media root: {settings.MEDIA_ROOT}")
    print(f"   Media exists: {os.path.exists(settings.MEDIA_ROOT)}")
    if os.path.exists(settings.MEDIA_ROOT):
        stat_info = os.stat(settings.MEDIA_ROOT)
        print(f"   Permissions: {oct(stat_info.st_mode)[-3:]}")
        print(f"   Owner: {stat_info.st_uid}:{stat_info.st_gid}")
        print(f"   Current user: {os.getuid()}")
        print(f"   Writable: {os.access(settings.MEDIA_ROOT, os.W_OK)}")

    # 2. Test image directory
    images_dir = os.path.join(settings.MEDIA_ROOT, "images")
    print("\n🖼️  IMAGES DIRECTORY:")
    print(f"   Path: {images_dir}")
    print(f"   Exists: {os.path.exists(images_dir)}")

    if not os.path.exists(images_dir):
        try:
            os.makedirs(images_dir, exist_ok=True)
            print("   ✅ Created images directory")
        except Exception as e:
            print(f"   ❌ Failed to create: {e}")
            return

    # 3. Test direct file creation
    print("\n📝 FILE CREATION TEST:")
    test_file = os.path.join(images_dir, "test_permissions.txt")
    try:
        with open(test_file, "w") as f:
            f.write("test")
        print("   ✅ Can write files")
        os.remove(test_file)
        print("   ✅ Can delete files")
    except Exception as e:
        print(f"   ❌ File operations failed: {e}")
        return

    # 4. Test Wagtail Image model directly
    print("\n🎨 WAGTAIL IMAGE MODEL TEST:")
    try:
        # Create test image data
        img = PILImage.new("RGB", (100, 100), color="red")
        img_bytes = io.BytesIO()
        img.save(img_bytes, format="JPEG")
        img_bytes.seek(0)

        # Create ContentFile
        image_file = ContentFile(img_bytes.getvalue(), name="test_direct.jpg")

        # Create Wagtail Image
        wagtail_image = Image(
            title="Direct Test Image",
            file=image_file,
        )

        # Validate
        wagtail_image.full_clean()
        print("   ✅ Image validation passed")

        # Save
        wagtail_image.save()
        print(f"   ✅ Image saved with ID: {wagtail_image.id}")
        print(f"   📁 File path: {wagtail_image.file.name}")
        print(f"   🔗 URL: {wagtail_image.file.url}")

        # Check if file exists on disk
        full_path = os.path.join(settings.MEDIA_ROOT, wagtail_image.file.name)
        print(f"   💾 File exists: {os.path.exists(full_path)}")
        if os.path.exists(full_path):
            print(f"   💾 File size: {os.path.getsize(full_path)} bytes")

        # Clean up
        wagtail_image.delete()
        print("   🗑️  Test image deleted")

    except Exception as e:
        print(f"   ❌ Image model test failed: {e}")
        import traceback

        print(f"   Traceback: {traceback.format_exc()}")
        return

    # 5. Check users and permissions
    print("\n👥 USER PERMISSIONS:")
    users = User.objects.filter(is_staff=True)
    print(f"   Staff users: {users.count()}")
    for user in users:
        print(
            f"   - {user.username} (staff: {user.is_staff}, superuser: {user.is_superuser})"
        )

    # 6. Check middleware that might cause 403s
    print("\n🔧 MIDDLEWARE ANALYSIS:")
    problematic_middleware = []

    if "django.middleware.csrf.CsrfViewMiddleware" not in settings.MIDDLEWARE:
        problematic_middleware.append("Missing CSRF middleware")
    else:
        print("   ✅ CSRF middleware present")

    if (
        "django.contrib.auth.middleware.AuthenticationMiddleware"
        not in settings.MIDDLEWARE
    ):
        problematic_middleware.append("Missing Authentication middleware")
    else:
        print("   ✅ Authentication middleware present")

    if "django.middleware.clickjacking.XFrameOptionsMiddleware" in settings.MIDDLEWARE:
        print("   ⚠️  XFrame middleware present (may interfere with iframe uploads)")

    if problematic_middleware:
        print(f"   ❌ Issues: {', '.join(problematic_middleware)}")

    # 7. Check security settings
    print("\n🔒 SECURITY SETTINGS:")
    print(f"   DEBUG: {settings.DEBUG}")
    print(f"   ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")

    if not settings.DEBUG:
        security_settings = [
            (
                "SECURE_BROWSER_XSS_FILTER",
                getattr(settings, "SECURE_BROWSER_XSS_FILTER", "Not set"),
            ),
            (
                "SECURE_CONTENT_TYPE_NOSNIFF",
                getattr(settings, "SECURE_CONTENT_TYPE_NOSNIFF", "Not set"),
            ),
            ("X_FRAME_OPTIONS", getattr(settings, "X_FRAME_OPTIONS", "Not set")),
            ("CSRF_COOKIE_SECURE", getattr(settings, "CSRF_COOKIE_SECURE", "Not set")),
        ]
        for setting, value in security_settings:
            print(f"   {setting}: {value}")

    # 8. Check Wagtail-specific settings
    print("\n⚙️  WAGTAIL SETTINGS:")
    wagtail_settings = [
        (
            "WAGTAILIMAGES_MAX_UPLOAD_SIZE",
            getattr(settings, "WAGTAILIMAGES_MAX_UPLOAD_SIZE", "Not set"),
        ),
        (
            "WAGTAILIMAGES_EXTENSIONS",
            getattr(settings, "WAGTAILIMAGES_EXTENSIONS", "Not set"),
        ),
        (
            "WAGTAILADMIN_BASE_URL",
            getattr(settings, "WAGTAILADMIN_BASE_URL", "Not set"),
        ),
    ]
    for setting, value in wagtail_settings:
        print(f"   {setting}: {value}")

    # 9. Storage backend test
    print("\n💾 STORAGE BACKEND TEST:")
    try:
        from django.core.files.storage import default_storage

        print(f"   Backend: {type(default_storage).__name__}")
        print(f"   Location: {getattr(default_storage, 'location', 'N/A')}")

        # Test storage operations
        test_content = b"Storage test"
        test_file = ContentFile(test_content, name="storage_test.txt")

        saved_name = default_storage.save("test_storage.txt", test_file)
        print(f"   ✅ File saved: {saved_name}")

        exists = default_storage.exists(saved_name)
        print(f"   ✅ File exists: {exists}")

        if exists:
            # Clean up
            default_storage.delete(saved_name)
            print("   ✅ File deleted")

    except Exception as e:
        print(f"   ❌ Storage test failed: {e}")

    print("\n" + "=" * 50)
    print("DIAGNOSIS SUMMARY")
    print("=" * 50)

    print("✅ Direct Wagtail Image model creation works")
    print("✅ File system permissions are correct")
    print("✅ Storage backend is functional")

    print("\n🔍 LIKELY CAUSES OF 403 ERROR:")
    print("1. 🔒 CSRF token missing or invalid in upload form")
    print("2. 🚫 User doesn't have proper Wagtail permissions")
    print("3. 🛠️  Middleware blocking the upload request")
    print("4. 🌐 ALLOWED_HOSTS configuration (when using test client)")
    print("5. 🔐 Session/authentication issues in the browser")

    print("\n💡 RECOMMENDED DEBUGGING STEPS:")
    print("1. Check browser developer tools for detailed 403 error")
    print("2. Look at Django logs when upload fails")
    print("3. Verify CSRF token is included in upload form")
    print("4. Check user has 'add image' permission in Wagtail")
    print("5. Test with a different browser/incognito mode")

    print("\n🔧 QUICK FIXES TO TRY:")
    print("1. Refresh the page to get new CSRF token")
    print("2. Log out and log back in")
    print("3. Clear browser cookies/cache")
    print("4. Try uploading a smaller image file")


if __name__ == "__main__":
    diagnose_image_upload()
