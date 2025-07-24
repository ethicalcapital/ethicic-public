#!/usr/bin/env python3
"""
Fix media directory permissions for Wagtail image uploads
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ethicic.settings')
django.setup()

from django.conf import settings

def fix_media_permissions():
    print("🔧 FIXING MEDIA DIRECTORY PERMISSIONS")
    print("=" * 50)
    
    media_root = settings.MEDIA_ROOT
    print(f"📁 Target media root: {media_root}")
    
    # Check if we're running as root or have sudo access
    current_user = os.getuid()
    print(f"🔍 Current user ID: {current_user}")
    
    if current_user == 0:
        print("✅ Running as root - can create directories")
    else:
        print("⚠️  Not running as root - may need sudo")
    
    # Try to create the media directory structure
    directories_to_create = [
        media_root,
        os.path.join(media_root, 'images'),
        os.path.join(media_root, 'images', 'original_images'),
        os.path.join(media_root, 'documents'),
    ]
    
    for directory in directories_to_create:
        print(f"\n📁 Creating: {directory}")
        try:
            if not os.path.exists(directory):
                os.makedirs(directory, mode=0o775, exist_ok=True)
                print(f"   ✅ Created successfully")
                
                # Set permissions
                os.chmod(directory, 0o775)
                print(f"   ✅ Set permissions to 775")
                
                # Try to set ownership (requires root)
                if current_user == 0:
                    # Set ownership to user 1000 (typical web server user)
                    try:
                        os.chown(directory, 1000, 1000)
                        print(f"   ✅ Set ownership to 1000:1000")
                    except Exception as e:
                        print(f"   ⚠️  Could not set ownership: {e}")
            else:
                print(f"   ✅ Already exists")
                
                # Check and fix permissions
                stat_info = os.stat(directory)
                current_perms = oct(stat_info.st_mode)[-3:]
                print(f"   📋 Current permissions: {current_perms}")
                
                if current_perms != '775':
                    os.chmod(directory, 0o775)
                    print(f"   ✅ Fixed permissions to 775")
                
        except PermissionError as e:
            print(f"   ❌ Permission denied: {e}")
            print(f"   💡 Try running with sudo: sudo python {__file__}")
        except Exception as e:
            print(f"   ❌ Failed: {e}")
    
    # Test file creation
    print(f"\n🧪 TESTING FILE OPERATIONS:")
    test_file = os.path.join(media_root, 'images', 'test_write.txt')
    try:
        with open(test_file, 'w') as f:
            f.write('test content')
        print("   ✅ Can write files")
        
        with open(test_file, 'r') as f:
            content = f.read()
        print("   ✅ Can read files")
        
        os.remove(test_file)
        print("   ✅ Can delete files")
        
        print(f"\n🎉 MEDIA DIRECTORY SETUP COMPLETE!")
        print(f"✅ Wagtail image uploads should now work")
        
    except Exception as e:
        print(f"   ❌ File operations still failing: {e}")
        print(f"\n🔧 MANUAL STEPS NEEDED:")
        print(f"Run these commands as root:")
        print(f"  sudo mkdir -p {media_root}/images/original_images")
        print(f"  sudo mkdir -p {media_root}/documents")
        print(f"  sudo chmod -R 775 {media_root}")
        print(f"  sudo chown -R 1000:1000 {media_root}")

if __name__ == '__main__':
    fix_media_permissions()