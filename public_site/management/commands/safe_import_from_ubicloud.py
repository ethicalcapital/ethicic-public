"""
Safe import command that checks column existence before importing
"""

from django.core.management.base import BaseCommand
from django.db import connections, transaction
from wagtail.models import Page

from public_site.models import HomePage, MediaItem, SupportTicket


class Command(BaseCommand):
    help = "Safely import public site data from Ubicloud database with column checking"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Check what tables and columns exist without importing",
        )

    def handle(self, *args, **options):
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("Safe Data Import from Ubicloud")
        self.stdout.write("=" * 60)

        # Check if Ubicloud database is configured
        if "ubicloud" not in connections:
            self.stdout.write(
                self.style.WARNING("\n⚠️  UBI_DATABASE_URL not configured")
            )
            return

        # Test connection
        try:
            with connections["ubicloud"].cursor() as cursor:
                cursor.execute("SELECT version()")
                cursor.fetchone()[0]  # Test connection
                self.stdout.write(
                    self.style.SUCCESS("✅ Connected to Ubicloud database")
                )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"\n❌ Connection failed: {e}"))
            return

        # Check what tables and columns exist
        table_schemas = self._check_table_schemas()

        if options["dry_run"]:
            self._print_schema_info(table_schemas)
            return

        # Import data safely
        with transaction.atomic():
            self._safe_import_pages(table_schemas)
            self._safe_import_media(table_schemas)
            self._safe_import_tickets(table_schemas)

        self.stdout.write(self.style.SUCCESS("✅ Safe import completed!"))

    def _check_table_schemas(self):
        """Check what tables and columns exist in Ubicloud"""
        schemas = {}

        with connections["ubicloud"].cursor() as cursor:
            # Get list of tables
            cursor.execute(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name LIKE 'public_site_%'
            """
            )
            tables = [row[0] for row in cursor.fetchall()]

            # For each table, get its columns
            for table in tables:
                cursor.execute(
                    """
                    SELECT column_name, data_type
                    FROM information_schema.columns
                    WHERE table_name = %s
                    ORDER BY ordinal_position
                """,
                    [table],
                )

                schemas[table] = {row[0]: row[1] for row in cursor.fetchall()}

        return schemas

    def _print_schema_info(self, schemas):
        """Print information about available tables and columns"""
        self.stdout.write("\n📋 Available Tables and Columns:")

        for table, columns in schemas.items():
            self.stdout.write(f"\n🗃️  {table}:")
            for col_name, col_type in columns.items():
                self.stdout.write(f"    • {col_name} ({col_type})")

        self.stdout.write("\n")

    def _safe_import_pages(self, schemas):
        """Safely import pages based on available columns"""
        homepage_table = "public_site_homepage"

        if homepage_table not in schemas:
            self.stdout.write("⚠️  No homepage table found, skipping page import")
            return

        self.stdout.write("Importing pages...")

        try:
            with connections["ubicloud"].cursor() as cursor:
                # Build dynamic query based on available columns
                homepage_cols = schemas[homepage_table]

                # Map expected fields to available columns
                select_fields = []
                if "title" in homepage_cols:
                    select_fields.append("title")
                if "slug" in homepage_cols:
                    select_fields.append("slug")
                if "hero_title" in homepage_cols:
                    select_fields.append("hero_title")
                if "hero_subtitle" in homepage_cols:
                    select_fields.append("hero_subtitle")
                if "body" in homepage_cols:
                    select_fields.append("body")

                if select_fields:
                    query = f"SELECT {', '.join(select_fields)} FROM {homepage_table}"
                    if "live" in homepage_cols:
                        query += " WHERE live = true"
                    query += " LIMIT 1"

                    cursor.execute(query)
                    home_data = cursor.fetchone()

                    if home_data and not HomePage.objects.exists():
                        # Create homepage with available data
                        field_map = {
                            field: home_data[i] for i, field in enumerate(select_fields)
                        }

                        root = Page.objects.get(id=1)
                        home = HomePage(
                            title=field_map.get("title", "Ethical Capital"),
                            slug=field_map.get("slug", "home"),
                            hero_title=field_map.get("hero_title", ""),
                            hero_subtitle=field_map.get("hero_subtitle", ""),
                            body=field_map.get("body", ""),
                        )
                        root.add_child(instance=home)

                        self.stdout.write(
                            self.style.SUCCESS(
                                "✓ Imported HomePage with available fields"
                            )
                        )

        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Page import failed: {e}"))

    def _safe_import_media(self, schemas):
        """Safely import media items"""
        table = "public_site_mediaitem"

        if table not in schemas:
            self.stdout.write("⚠️  No media item table found, skipping")
            return

        # Check required columns exist
        required_cols = ["title"]  # Minimum required
        available_cols = schemas[table]

        if not all(col in available_cols for col in required_cols):
            self.stdout.write("⚠️  Media table missing required columns, skipping")
            return

        self.stdout.write("Importing media items...")

        try:
            with connections["ubicloud"].cursor() as cursor:
                # Use only available columns
                select_cols = []
                for col in ["title", "publication", "date", "excerpt", "featured"]:
                    if col in available_cols:
                        select_cols.append(col)

                if select_cols:
                    query = f"SELECT {', '.join(select_cols)} FROM {table} ORDER BY "
                    if "date" in available_cols:
                        query += "date DESC"
                    else:
                        query += "1"

                    cursor.execute(query)
                    items = cursor.fetchall()

                    imported = 0
                    for item_data in items:
                        field_map = {
                            col: item_data[i] for i, col in enumerate(select_cols)
                        }

                        # Only create if we have enough data
                        if field_map.get("title"):
                            MediaItem.objects.get_or_create(
                                title=field_map["title"],
                                defaults={
                                    "publication": field_map.get("publication", ""),
                                    "date": field_map.get("date"),
                                    "excerpt": field_map.get("excerpt", ""),
                                    "featured": field_map.get("featured", False),
                                },
                            )
                            imported += 1

                    self.stdout.write(
                        self.style.SUCCESS(f"✓ Imported {imported} media items")
                    )

        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Media import failed: {e}"))

    def _safe_import_tickets(self, schemas):
        """Safely import support tickets"""
        table = "public_site_supportticket"

        if table not in schemas:
            self.stdout.write("⚠️  No support ticket table found, skipping")
            return

        # Check required columns
        required_cols = ["name", "email", "subject", "message"]
        available_cols = schemas[table]

        missing_cols = [col for col in required_cols if col not in available_cols]
        if missing_cols:
            self.stdout.write(
                f"⚠️  Support ticket table missing columns: {missing_cols}, skipping"
            )
            return

        self.stdout.write("Importing support tickets...")

        try:
            with connections["ubicloud"].cursor() as cursor:
                # Use available columns
                select_cols = []
                for col in [
                    "name",
                    "email",
                    "subject",
                    "message",
                    "status",
                    "priority",
                    "created_at",
                ]:
                    if col in available_cols:
                        select_cols.append(col)

                query = f"SELECT {', '.join(select_cols)} FROM {table}"
                if "created_at" in available_cols:
                    query += " ORDER BY created_at DESC"

                cursor.execute(query)
                tickets = cursor.fetchall()

                imported = 0
                for ticket_data in tickets:
                    field_map = {
                        col: ticket_data[i] for i, col in enumerate(select_cols)
                    }

                    SupportTicket.objects.get_or_create(
                        email=field_map["email"],
                        subject=field_map["subject"],
                        defaults={
                            "name": field_map["name"],
                            "message": field_map["message"],
                            "status": field_map.get("status", "open"),
                            "priority": field_map.get("priority", "medium"),
                            "created_at": field_map.get("created_at"),
                        },
                    )
                    imported += 1

                self.stdout.write(
                    self.style.SUCCESS(f"✓ Imported {imported} support tickets")
                )

        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Support ticket import failed: {e}"))
