# Safe migration to add philosophy fields to HomePage
from django.db import migrations, models, connection
import wagtail.fields


def safe_add_philosophy_fields(apps, schema_editor):
    """Safely add philosophy fields only if they don't already exist"""
    
    # Get the table structure
    with connection.cursor() as cursor:
        # Check what columns exist in the homepage table
        if 'postgresql' in connection.settings_dict['ENGINE']:
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'public_site_homepage'
            """)
        else:  # SQLite
            cursor.execute("PRAGMA table_info(public_site_homepage)")
            
        existing_columns = set()
        if 'postgresql' in connection.settings_dict['ENGINE']:
            existing_columns = {row[0] for row in cursor.fetchall()}
        else:
            existing_columns = {row[1] for row in cursor.fetchall()}  # SQLite returns name in position 1
    
    # Fields to add with their definitions
    fields_to_add = {
        'philosophy_title': "VARCHAR(200) DEFAULT 'Ethics Reveal Quality'",
        'philosophy_content': "TEXT DEFAULT ''",
        'philosophy_highlight': "VARCHAR(200) DEFAULT ''",
    }
    
    # Add missing columns
    with connection.cursor() as cursor:
        for field_name, field_definition in fields_to_add.items():
            if field_name not in existing_columns:
                print(f"Adding missing philosophy field: {field_name}")
                cursor.execute(f"ALTER TABLE public_site_homepage ADD COLUMN {field_name} {field_definition}")
            else:
                print(f"Philosophy field {field_name} already exists, skipping")


def reverse_safe_add_philosophy_fields(apps, schema_editor):
    """Reverse the migration by removing the fields"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('public_site', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(
            safe_add_philosophy_fields,
            reverse_safe_add_philosophy_fields,
        ),
    ]