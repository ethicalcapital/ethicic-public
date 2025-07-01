# Squashed migration for production deployment
# This migration assumes the database already has all the content

from django.db import migrations


class Migration(migrations.Migration):
    """
    This is a squashed migration that replaces all previous migrations.
    It's designed to be marked as already applied (fake) on production
    since the database already contains all the content.
    
    To apply: python manage.py migrate public_site 0001 --fake
    """
    
    initial = True
    
    # Updated dependencies for Wagtail 5.2.6
    dependencies = [
        ("wagtailcore", "0089_log_entry_data_json_null_to_object"),  # Latest Wagtail 5.2 migration
        ("wagtailimages", "0025_alter_image_file_alter_rendition_file"),
        ("wagtaildocs", "0012_uploadeddocument"),
        ("taggit", "0005_auto_20220424_2025"),
    ]
    
    operations = [
        # This migration intentionally has no operations
        # The database schema already exists
        # Run with --fake flag to mark as applied
    ]