"""
Management command to fix database migration issues.
"""

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = "Fix database migration issues by detecting and resolving conflicts"

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force reset of problematic migrations",
        )

    def handle(self, *args, **options):
        self.stdout.write("🔧 Fixing database issues...")

        # Check what tables exist
        with connection.cursor() as cursor:
            if "sqlite" in settings.DATABASES["default"]["ENGINE"]:
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            else:
                cursor.execute(
                    "SELECT tablename FROM pg_tables WHERE schemaname='public'"
                )

            existing_tables = [row[0] for row in cursor.fetchall()]

        self.stdout.write(f"Found {len(existing_tables)} existing tables")

        # Check for critical Wagtail tables
        wagtail_tables = [
            table for table in existing_tables if table.startswith("wagtail")
        ]
        public_site_tables = [
            table for table in existing_tables if table.startswith("public_site")
        ]

        self.stdout.write(f"Wagtail tables: {len(wagtail_tables)}")
        self.stdout.write(f"Public site tables: {len(public_site_tables)}")

        if not wagtail_tables:
            self.stdout.write("⚠️  No Wagtail tables found - running full migration")
            try:
                call_command("migrate", verbosity=1, interactive=False)
                self.stdout.write(self.style.SUCCESS("✅ Full migration completed"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Migration failed: {e}"))
                return
        else:
            self.stdout.write("📋 Wagtail tables exist - checking for conflicts")

            # Try to fake apply migrations that might be causing conflicts
            if options["force"]:
                self.stdout.write(
                    "🔄 Force mode: marking conflicting migrations as applied"
                )
                try:
                    # Mark public_site migrations as fake applied if they exist
                    call_command(
                        "migrate",
                        "public_site",
                        "--fake",
                        verbosity=1,
                        interactive=False,
                    )
                    self.stdout.write("✅ Public site migrations marked as applied")
                except Exception as e:
                    self.stdout.write(f"⚠️  Could not fake apply public_site: {e}")

            # Try regular migration now
            try:
                call_command("migrate", verbosity=1, interactive=False)
                self.stdout.write(self.style.SUCCESS("✅ Migration completed"))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"⚠️  Migration warnings: {e}"))

        # Set up site structure
        self.stdout.write("🏠 Setting up site structure...")
        try:
            call_command("setup_homepage")
            self.stdout.write(self.style.SUCCESS("✅ Site setup completed"))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"⚠️  Site setup warnings: {e}"))

        self.stdout.write(self.style.SUCCESS("🎉 Database fix completed!"))
