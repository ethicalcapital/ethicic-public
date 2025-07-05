# Generated manually to fix migration state
from django.db import migrations, connection


def check_and_fix_migration_state(apps, schema_editor):
    """Check if fields exist and update migration state accordingly."""
    with connection.cursor() as cursor:
        # Check if the problematic fields already exist
        cursor.execute(
            """
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'public_site_strategypage'
            AND column_name IN ('cash_allocation', 'benchmark_name', 'ytd_benchmark')
        """
        )
        existing_columns = [row[0] for row in cursor.fetchall()]

        if existing_columns:
            print(f"Found existing columns: {existing_columns}")
            # The fields already exist, nothing to do


def reverse_check(apps, schema_editor):
    """Reverse operation - does nothing."""
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("public_site", "0010_update_headshot_url_to_r2"),
    ]

    operations = [
        migrations.RunPython(check_and_fix_migration_state, reverse_check),
    ]
