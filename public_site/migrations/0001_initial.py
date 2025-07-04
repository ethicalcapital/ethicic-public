# Simple migration for production deployment
# This migration assumes the database already has all the content

from django.db import migrations


class Migration(migrations.Migration):
    """
    This is a simplified migration that just establishes the initial migration
    without creating any tables. It's designed to be used with --fake flag
    on production databases that already have the schema.

    To apply: python manage.py migrate public_site 0001_initial_simple --fake
    """

    initial = True

    dependencies = [
        ("taggit", "0005_auto_20220424_2025"),
        ("wagtailcore", "0089_log_entry_data_json_null_to_object"),
        ("wagtaildocs", "0012_uploadeddocument"),
        ("wagtailimages", "0025_alter_image_file_alter_rendition_file"),
    ]

    operations = [
        # No operations - the database schema already exists
        # This migration is just to mark the app as migrated
    ]
