# Generated manually to add NOT NULL constraints to SupportTicket

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("public_site", "0012_accessibilitypage_newsletterpage"),
    ]

    operations = [
        # Add NOT NULL constraints to SupportTicket fields
        migrations.RunSQL(
            sql=[
                # Update any existing NULL values to empty strings first
                "UPDATE public_site_supportticket SET name = '' WHERE name IS NULL;",
                "UPDATE public_site_supportticket SET email = '' WHERE email IS NULL;",
                "UPDATE public_site_supportticket SET subject = '' WHERE subject IS NULL;",
                "UPDATE public_site_supportticket SET message = '' WHERE message IS NULL;",
                # Add NOT NULL constraints
                "ALTER TABLE public_site_supportticket ALTER COLUMN name SET NOT NULL;",
                "ALTER TABLE public_site_supportticket ALTER COLUMN email SET NOT NULL;",
                "ALTER TABLE public_site_supportticket ALTER COLUMN subject SET NOT NULL;",
                "ALTER TABLE public_site_supportticket ALTER COLUMN message SET NOT NULL;",
            ],
            reverse_sql=[
                # Remove NOT NULL constraints
                "ALTER TABLE public_site_supportticket ALTER COLUMN name DROP NOT NULL;",
                "ALTER TABLE public_site_supportticket ALTER COLUMN email DROP NOT NULL;",
                "ALTER TABLE public_site_supportticket ALTER COLUMN subject DROP NOT NULL;",
                "ALTER TABLE public_site_supportticket ALTER COLUMN message DROP NOT NULL;",
            ],
        ),
    ]
