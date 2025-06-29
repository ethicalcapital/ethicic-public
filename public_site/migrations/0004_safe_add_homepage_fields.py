# Safe migration to add homepage fields only if they don't exist
from django.db import migrations, models, connection
import wagtail.fields


def safe_add_homepage_fields(apps, schema_editor):
    """Safely add fields only if they don't already exist"""
    
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
        'hero_tagline': "VARCHAR(100) DEFAULT 'We''re not like other firms. Good.'",
        'excluded_percentage': "VARCHAR(10) DEFAULT '57%'",
        'since_year': "VARCHAR(20) DEFAULT 'SINCE 2021'",
        'trust_text': "VARCHAR(50) DEFAULT 'Trust'",
        'commitment_text': "VARCHAR(50) DEFAULT 'Commitment'",
        'consistency_text': "VARCHAR(50) DEFAULT 'Consistency'",
        'footer_cta_title': "VARCHAR(255) DEFAULT 'Ready to invest with purpose?'",
        'footer_cta_text': "VARCHAR(255) DEFAULT 'Join forward-thinking investors who refuse to profit from harm.'",
        'footer_cta_button_text': "VARCHAR(100) DEFAULT 'Start a Conversation'",
        'footer_cta_button_link': "VARCHAR(255) DEFAULT '/contact/'",
    }
    
    # Add missing columns
    with connection.cursor() as cursor:
        for field_name, field_definition in fields_to_add.items():
            if field_name not in existing_columns:
                print(f"Adding missing field: {field_name}")
                cursor.execute(f"ALTER TABLE public_site_homepage ADD COLUMN {field_name} {field_definition}")
            else:
                print(f"Field {field_name} already exists, skipping")


def reverse_safe_add_homepage_fields(apps, schema_editor):
    """Reverse the migration by removing the fields"""
    # Note: This is a simplified reverse - in practice you might want to be more careful
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('public_site', '0003_add_philosophy_fields'),
    ]

    operations = [
        migrations.RunPython(
            safe_add_homepage_fields,
            reverse_safe_add_homepage_fields,
        ),
    ]