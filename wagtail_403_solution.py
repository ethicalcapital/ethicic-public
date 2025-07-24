#!/usr/bin/env python3
"""
WAGTAIL CMS IMAGE UPLOAD 403 ERROR - ROOT CAUSE & SOLUTION

This script explains the root cause of 403 errors when uploading images
through the Wagtail CMS interface and provides the complete solution.
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ethicic.settings')
django.setup()

from django.conf import settings

def explain_issue_and_solution():
    print("🔍 WAGTAIL IMAGE UPLOAD 403 ERROR ANALYSIS")
    print("=" * 60)
    
    print("\n❌ ROOT CAUSE IDENTIFIED:")
    print("   The media directory '/var/lib/data' does not exist!")
    print("   Django/Wagtail cannot create it due to permission restrictions.")
    
    media_root = settings.MEDIA_ROOT
    print(f"\n📁 CURRENT CONFIGURATION:")
    print(f"   MEDIA_ROOT = {media_root}")
    print(f"   Directory exists: {os.path.exists(media_root)}")
    
    if os.path.exists(media_root):
        stat_info = os.stat(media_root)
        print(f"   Permissions: {oct(stat_info.st_mode)[-3:]}")
        print(f"   Owner: {stat_info.st_uid}:{stat_info.st_gid}")
        print(f"   Writable by current process: {os.access(media_root, os.W_OK)}")
    else:
        print("   ❌ Directory does not exist")
    
    print(f"\n🔍 WHY THIS CAUSES 403 ERRORS:")
    print("   1. User uploads image through Wagtail CMS interface")
    print("   2. Wagtail tries to save image to {media_root}/images/")
    print("   3. Directory doesn't exist and can't be created")
    print("   4. File save operation fails with PermissionError")
    print("   5. Django returns HTTP 403 Forbidden instead of 500 error")
    print("   6. User sees generic 403 error with no clear explanation")
    
    print(f"\n✅ COMPLETE SOLUTION:")
    print("   Run these commands as root or with sudo:")
    print(f"   1. sudo mkdir -p {media_root}/images/original_images")
    print(f"   2. sudo mkdir -p {media_root}/documents") 
    print(f"   3. sudo chmod -R 775 {media_root}")
    print(f"   4. sudo chown -R 1000:1000 {media_root}")
    
    print(f"\n🔧 COMMAND EXPLANATION:")
    print("   mkdir -p: Create directories recursively")
    print("   chmod 775: Read/write/execute for owner/group, read/execute for others")
    print("   chown 1000:1000: Set ownership to user 1000 (typical web server user)")
    
    print(f"\n🧪 VERIFICATION STEPS:")
    print("   After running the commands above:")
    print("   1. python test_after_fix.py")
    print("   2. Try uploading an image through /cms/images/")
    print("   3. Check that files appear in the media directory")
    
    print(f"\n🛡️  SECURITY CONSIDERATIONS:")
    print("   ✅ Permissions 775 allow web server to write")
    print("   ✅ Owner 1000:1000 matches typical web server user")
    print("   ✅ Directory structure follows Django/Wagtail conventions")
    
    print(f"\n🏗️  PRODUCTION DEPLOYMENT NOTES:")
    print("   • This fix is required for any deployment (Kinsta, Docker, etc.)")
    print("   • Media directory must be persistent (not ephemeral)")
    print("   • Consider using object storage (S3, R2) for production")
    print("   • Backup strategy should include media files")
    
    print(f"\n🚀 ALTERNATIVE SOLUTIONS:")
    print("   1. Change MEDIA_ROOT to a writable location:")
    print("      MEDIA_ROOT = '/tmp/media'  # Temporary solution")
    print("   2. Use cloud storage (requires additional configuration):")
    print("      STORAGES = {'default': {'BACKEND': 'storages.backends.s3boto3.S3Boto3Storage'}}")
    print("   3. Use Docker volumes (for containerized deployments)")
    
    print(f"\n📋 TESTING CHECKLIST:")
    print("   □ Media directory exists and is writable")
    print("   □ Direct Wagtail Image model creation works")
    print("   □ Image upload through CMS interface works")
    print("   □ Image files appear in media directory")
    print("   □ Image URLs are accessible")
    print("   □ Image renditions can be created")
    
    # Check current status
    print(f"\n📊 CURRENT STATUS:")
    if os.path.exists(media_root):
        if os.access(media_root, os.W_OK):
            print("   ✅ Media directory exists and is writable")
            print("   🎉 Issue likely resolved - test image upload!")
        else:
            print("   ⚠️  Media directory exists but not writable")
            print("   🔧 Run: sudo chmod -R 775 {media_root}")
    else:
        print("   ❌ Media directory missing - run the sudo commands above")

def generate_fix_script():
    """Generate a shell script to fix the issue"""
    media_root = settings.MEDIA_ROOT
    
    script_content = f"""#!/bin/bash
# Fix Wagtail image upload 403 errors by creating media directory

echo "🔧 Fixing Wagtail media directory permissions..."

# Create media directories
echo "📁 Creating media directories..."
mkdir -p {media_root}/images/original_images
mkdir -p {media_root}/documents

# Set permissions
echo "🔐 Setting permissions to 775..."
chmod -R 775 {media_root}

# Set ownership (adjust user/group as needed)
echo "👤 Setting ownership to 1000:1000..."
chown -R 1000:1000 {media_root}

# Verify setup
echo "✅ Verifying setup..."
ls -la {media_root}
ls -la {media_root}/images/

echo "🎉 Media directory setup complete!"
echo "Test image upload at /cms/images/"
"""
    
    with open('/Users/srvo/ethicic-public/fix_media_directory.sh', 'w') as f:
        f.write(script_content)
    
    os.chmod('/Users/srvo/ethicic-public/fix_media_directory.sh', 0o755)
    
    print(f"\n📜 GENERATED FIX SCRIPT:")
    print("   Created: fix_media_directory.sh")
    print("   Usage: sudo ./fix_media_directory.sh")

if __name__ == '__main__':
    explain_issue_and_solution()
    generate_fix_script()
    
    print(f"\n" + "=" * 60)
    print("SUMMARY: Media directory '/var/lib/data' doesn't exist")
    print("SOLUTION: Run 'sudo ./fix_media_directory.sh'")
    print("=" * 60)