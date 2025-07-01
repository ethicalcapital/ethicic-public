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
    
    # Updated dependencies - using the latest available migrations
    dependencies = [
        ("wagtailcore", "0095_query_searchpromotion_querydailyhits"),
        ("wagtailimages", "0027_image_description"),
        ("wagtaildocs", "0014_alter_document_file_size"),
        ("taggit", "0006_rename_taggeditem_content_type_object_id_taggit_tagg_content_8fc721_idx"),
    ]
    
    operations = [
        # This migration intentionally has no operations
        # The database schema already exists
        # Run with --fake flag to mark as applied
    ]