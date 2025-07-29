"""
Debug media file storage and permissions
"""

import os

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Debug media file storage configuration"

    def handle(self, *args, **options):
        self.stdout.write("🔍 Debugging media file storage...")

        # Check settings
        self.stdout.write(f"MEDIA_ROOT: {settings.MEDIA_ROOT}")
        self.stdout.write(f"MEDIA_URL: {settings.MEDIA_URL}")

        # Check if directory exists
        if os.path.exists(settings.MEDIA_ROOT):
            self.stdout.write("✅ MEDIA_ROOT directory exists")

            # Check permissions
            import stat

            mode = oct(stat.S_IMODE(os.stat(settings.MEDIA_ROOT).st_mode))
            self.stdout.write(f"Directory permissions: {mode}")

            # Check if writable
            if os.access(settings.MEDIA_ROOT, os.W_OK):
                self.stdout.write("✅ MEDIA_ROOT is writable")
            else:
                self.stdout.write("❌ MEDIA_ROOT is not writable")

            # List contents
            contents = os.listdir(settings.MEDIA_ROOT)
            self.stdout.write(f"MEDIA_ROOT contents: {contents}")

            # Check images subdirectory
            images_dir = os.path.join(settings.MEDIA_ROOT, "images")
            if os.path.exists(images_dir):
                self.stdout.write("✅ images/ subdirectory exists")
                image_contents = os.listdir(images_dir)
                self.stdout.write(f"images/ contents: {image_contents}")

                if os.access(images_dir, os.W_OK):
                    self.stdout.write("✅ images/ directory is writable")
                else:
                    self.stdout.write("❌ images/ directory is not writable")
            else:
                self.stdout.write("❌ images/ subdirectory does not exist")

        else:
            self.stdout.write("❌ MEDIA_ROOT directory does not exist")

        # Test file creation
        test_file = os.path.join(settings.MEDIA_ROOT, "test_write.txt")
        try:
            with open(test_file, "w") as f:
                f.write("test")
            self.stdout.write("✅ Can write test file")
            os.remove(test_file)
            self.stdout.write("✅ Can delete test file")
        except Exception as e:
            self.stdout.write(f"❌ Cannot write test file: {e}")
