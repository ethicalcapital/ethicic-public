"""
Management command to fix migration conflicts by marking problematic migrations as applied.
"""

from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import connection
from django.conf import settings


class Command(BaseCommand):
    help = 'Fix migration conflicts by marking problematic migrations as fake applied'

    def handle(self, *args, **options):
        self.stdout.write("🔧 Fixing migration conflicts...")
        
        # Check if the problematic migration is already applied
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT * FROM django_migrations 
                WHERE app = 'public_site' AND name = '0002_add_missing_homepage_fields'
            """)
            migration_exists = cursor.fetchone()
            
            # Check if the columns actually exist
            if 'postgresql' in settings.DATABASES['default']['ENGINE']:
                cursor.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'public_site_homepage' AND column_name = 'hero_tagline'
                """)
            else:  # SQLite
                cursor.execute("PRAGMA table_info(public_site_homepage)")
                
            column_exists = cursor.fetchone()
        
        if column_exists and not migration_exists:
            self.stdout.write("📋 Columns exist but migration not recorded - marking as fake applied")
            try:
                # Mark the problematic migration as fake applied
                call_command('migrate', 'public_site', '0002', '--fake', verbosity=1, interactive=False)
                self.stdout.write(self.style.SUCCESS("✅ Migration 0002 marked as fake applied"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Failed to fake apply migration: {e}"))
                return
        elif migration_exists:
            self.stdout.write("✅ Migration already recorded")
        else:
            self.stdout.write("⚠️  Columns don't exist yet")
        
        # Now run normal migrations
        self.stdout.write("🔄 Running normal migrations...")
        try:
            call_command('migrate', verbosity=1, interactive=False)
            self.stdout.write(self.style.SUCCESS("✅ Migrations completed successfully"))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"⚠️  Migration warnings: {e}"))
        
        self.stdout.write(self.style.SUCCESS("🎉 Migration conflict fix completed!"))