"""
Debug Wagtail images and renditions
"""

import os

from django.conf import settings
from django.core.management.base import BaseCommand
from wagtail.images.models import Image


class Command(BaseCommand):
    help = "Debug Wagtail images and check file system"

    def handle(self, *args, **options):
        self.stdout.write("🖼️ Debugging Wagtail images...")

        # Check media settings
        self.stdout.write(f"📁 Media root: {settings.MEDIA_ROOT}")
        self.stdout.write(f"🔗 Media URL: {settings.MEDIA_URL}")

        # Check if media root exists and is writable
        if os.path.exists(settings.MEDIA_ROOT):
            self.stdout.write("✅ Media root exists")
            if os.access(settings.MEDIA_ROOT, os.W_OK):
                self.stdout.write("✅ Media root is writable")
            else:
                self.stdout.write("❌ Media root is not writable")
        else:
            self.stdout.write("❌ Media root does not exist")

        # List actual files
        if os.path.exists(settings.MEDIA_ROOT):
            self.stdout.write("\n📂 Files in media root:")
            for root, _dirs, files in os.walk(settings.MEDIA_ROOT):
                level = root.replace(settings.MEDIA_ROOT, "").count(os.sep)
                indent = " " * 2 * level
                self.stdout.write(f"{indent}{os.path.basename(root)}/")
                subindent = " " * 2 * (level + 1)
                for file in files:
                    file_path = os.path.join(root, file)
                    size = os.path.getsize(file_path)
                    self.stdout.write(f"{subindent}{file} ({size} bytes)")

        # Check Wagtail images in database
        images = Image.objects.all().order_by("-created_at")[:5]
        self.stdout.write(f"\n🖼️ Recent Wagtail images ({len(images)}):")

        for img in images:
            self.stdout.write(f"  ID: {img.id} | Title: {img.title}")
            self.stdout.write(f"    File: {img.file.name if img.file else 'NO FILE'}")

            if img.file:
                file_path = img.file.path
                self.stdout.write(f"    Path: {file_path}")

                if os.path.exists(file_path):
                    size = os.path.getsize(file_path)
                    self.stdout.write(f"    ✅ File exists ({size} bytes)")
                else:
                    self.stdout.write("    ❌ File missing from disk")

                # Check renditions
                renditions = img.renditions.all()[:3]
                self.stdout.write(
                    f"    📐 Renditions: {len(renditions)} total, showing first 3:"
                )

                for rendition in renditions:
                    rend_path = rendition.file.path if rendition.file else "NO FILE"
                    if rendition.file and os.path.exists(rend_path):
                        size = os.path.getsize(rend_path)
                        self.stdout.write(
                            f"      ✅ {rendition.filter_spec}: {rend_path} ({size} bytes)"
                        )
                    else:
                        self.stdout.write(
                            f"      ❌ {rendition.filter_spec}: MISSING - {rend_path}"
                        )

            self.stdout.write("")

        self.stdout.write("✅ Image debug complete!")
