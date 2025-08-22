"""
Test R2 storage configuration and URL generation.
"""

from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.files.storage import default_storage
from wagtail.images.models import Image


class Command(BaseCommand):
    help = "Test R2 storage configuration"

    def handle(self, *args, **options):
        self.stdout.write("\n=== R2 Storage Configuration Test ===\n")
        
        # Check configuration
        self.stdout.write(f"USE_R2: {getattr(settings, 'USE_R2', False)}")
        self.stdout.write(f"MEDIA_URL: {settings.MEDIA_URL}")
        
        if hasattr(settings, 'AWS_S3_ENDPOINT_URL'):
            self.stdout.write(f"AWS_S3_ENDPOINT_URL: {settings.AWS_S3_ENDPOINT_URL}")
            self.stdout.write(f"AWS_STORAGE_BUCKET_NAME: {settings.AWS_STORAGE_BUCKET_NAME}")
            self.stdout.write(f"R2_PUBLIC_URL: {getattr(settings, 'R2_PUBLIC_URL', 'Not set')}")
        
        # Check storage backend
        self.stdout.write(f"\nDefault storage backend: {default_storage.__class__.__name__}")
        
        # Test with an actual image
        images = Image.objects.all()[:1]
        if images:
            image = images[0]
            self.stdout.write(f"\nTesting with image: {image.title}")
            self.stdout.write(f"File name: {image.file.name}")
            self.stdout.write(f"File URL: {image.file.url}")
            
            # Test rendition
            try:
                rendition = image.get_rendition('width-400')
                self.stdout.write(f"Rendition URL: {rendition.url}")
                self.stdout.write(f"Full rendition URL: {rendition.file.url}")
            except Exception as e:
                self.stdout.write(f"Error creating rendition: {e}")
        
        # Show what URL pattern we're expecting
        self.stdout.write("\n=== Expected URL Patterns ===")
        self.stdout.write("For R2 public access, URLs should be one of:")
        self.stdout.write("1. https://{account-id}.r2.cloudflarestorage.com/{bucket}/{key}")
        self.stdout.write("2. https://pub-{hash}.r2.dev/{key}")
        self.stdout.write("3. Custom domain if configured")
        
        self.stdout.write("\n=== End Test ===\n")