"""
Test R2 storage connectivity and configuration
"""

import os
import tempfile
from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage


class Command(BaseCommand):
    help = 'Test R2 storage configuration and connectivity'

    def handle(self, *args, **options):
        self.stdout.write("🔍 Testing R2 storage configuration...")
        
        # Check settings
        self.stdout.write("📋 Current storage settings:")
        if hasattr(settings, 'STORAGES'):
            storage_config = settings.STORAGES.get('default', {})
            self.stdout.write(f"  Storage Backend: {storage_config.get('BACKEND', 'Not set')}")
            self.stdout.write(f"  Storage Options: {list(storage_config.get('OPTIONS', {}).keys())}")
        else:
            self.stdout.write("  ❌ STORAGES not configured")
            
        self.stdout.write(f"  MEDIA_URL: {settings.MEDIA_URL}")
        
        # Check environment variables
        self.stdout.write("🔐 R2 credentials:")
        access_key = os.getenv('R2_ACCESS_KEY_ID')
        secret_key = os.getenv('R2_SECRET_ACCESS_KEY')
        self.stdout.write(f"  R2_ACCESS_KEY_ID: {'✅ Set' if access_key else '❌ Missing'}")
        self.stdout.write(f"  R2_SECRET_ACCESS_KEY: {'✅ Set' if secret_key else '❌ Missing'}")
        
        # Test storage connection
        try:
            self.stdout.write("📁 Testing file operations...")
            
            # Create a test file
            test_content = "This is a test file for R2 storage"
            test_file = ContentFile(test_content.encode('utf-8'))
            
            # Save the file
            file_name = "test_r2_connection.txt"
            saved_name = default_storage.save(file_name, test_file)
            self.stdout.write(f"✅ File saved as: {saved_name}")
            
            # Check if file exists
            if default_storage.exists(saved_name):
                self.stdout.write("✅ File exists in storage")
                
                # Get file URL
                file_url = default_storage.url(saved_name)
                self.stdout.write(f"🔗 File URL: {file_url}")
                
                # Try to read the file back
                stored_file = default_storage.open(saved_name)
                content = stored_file.read().decode('utf-8')
                if content == test_content:
                    self.stdout.write("✅ File content matches")
                else:
                    self.stdout.write("❌ File content mismatch")
                stored_file.close()
                
                # Clean up
                default_storage.delete(saved_name)
                self.stdout.write("🗑️ Test file cleaned up")
                
            else:
                self.stdout.write("❌ File not found in storage after save")
                
        except Exception as e:
            self.stdout.write(f"❌ Storage test failed: {str(e)}")
            import traceback
            self.stdout.write(f"Full error: {traceback.format_exc()}")
            
        self.stdout.write("✅ R2 storage test complete")