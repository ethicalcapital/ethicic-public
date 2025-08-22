"""
Management command to diagnose featured image issues.
"""

from django.core.management.base import BaseCommand
from django.conf import settings
from wagtail.images.models import Image
from public_site.models import BlogPost


class Command(BaseCommand):
    help = "Check featured images and diagnose display issues"

    def handle(self, *args, **options):
        self.stdout.write("\n=== Featured Image Diagnostics ===\n")

        # Check settings
        self.stdout.write(f"MEDIA_URL: {settings.MEDIA_URL}")
        self.stdout.write(f"MEDIA_ROOT: {settings.MEDIA_ROOT}")
        self.stdout.write(f"DEBUG: {settings.DEBUG}")

        # Check if any images exist
        image_count = Image.objects.count()
        self.stdout.write(f"\nTotal images in database: {image_count}")

        if image_count > 0:
            # Check a sample image
            sample_image = Image.objects.first()
            self.stdout.write("\nSample image:")
            self.stdout.write(f"  - ID: {sample_image.id}")
            self.stdout.write(f"  - Title: {sample_image.title}")
            self.stdout.write(f"  - File: {sample_image.file}")
            self.stdout.write(f"  - File URL: {sample_image.file.url}")

            # Check if file exists
            try:
                self.stdout.write(
                    f"  - File exists: {sample_image.file.storage.exists(sample_image.file.name)}"
                )
                self.stdout.write(f"  - File path: {sample_image.file.path}")
            except Exception as e:
                self.stdout.write(f"  - Error checking file: {e}")

        # Check blog posts with featured images
        posts_with_images = BlogPost.objects.filter(featured_image__isnull=False)
        self.stdout.write(
            f"\nBlog posts with featured images: {posts_with_images.count()}"
        )

        for post in posts_with_images[:3]:  # Check first 3
            self.stdout.write(f"\nPost: {post.title}")
            self.stdout.write(f"  - Featured image ID: {post.featured_image.id}")
            self.stdout.write(f"  - Image URL: {post.featured_image.file.url}")

            # Test renditions
            try:
                rendition = post.featured_image.get_rendition("width-400")
                self.stdout.write(f"  - Rendition URL: {rendition.url}")
                self.stdout.write(
                    f"  - Rendition file exists: {rendition.file.storage.exists(rendition.file.name)}"
                )
            except Exception as e:
                self.stdout.write(f"  - Error creating rendition: {e}")

        self.stdout.write("\n=== End Diagnostics ===\n")
