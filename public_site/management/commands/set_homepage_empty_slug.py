"""
Django management command to set HomePage slug to empty string for root URL.

This directly sets the HomePage slug to empty string so it serves at "/" instead of with a slug.

Usage:
    python manage.py set_homepage_empty_slug [--dry-run]
"""

from django.core.management.base import BaseCommand
from django.db import transaction


class Command(BaseCommand):
    help = "Set HomePage slug to empty string for root URL"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be changed without making changes",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]

        self.stdout.write(
            self.style.SUCCESS("🏠 Setting HomePage to Root URL")
        )
        self.stdout.write("=" * 40)

        # Find the HomePage
        from public_site.models import HomePage

        try:
            homepage = HomePage.objects.get()
            self.stdout.write(f"🏠 Found HomePage: {homepage.title} (ID: {homepage.id})")
            self.stdout.write(f"    Current slug: '{homepage.slug}'")
            self.stdout.write(f"    Current URL path: {homepage.url_path}")
        except HomePage.DoesNotExist:
            self.stdout.write(
                self.style.ERROR("❌ No HomePage found")
            )
            return
        except HomePage.MultipleObjectsReturned:
            self.stdout.write(
                self.style.ERROR("❌ Multiple HomePage instances found")
            )
            return

        # Check if slug is already empty
        if homepage.slug == "":
            self.stdout.write(
                self.style.SUCCESS("✅ Homepage slug is already empty!")
            )
            return

        self.stdout.write(f"🔄 Will set slug from '{homepage.slug}' to '' (empty)")

        if dry_run:
            self.stdout.write(
                self.style.WARNING("\n🔍 DRY RUN - No changes made")
            )
            self.stdout.write(
                "Run without --dry-run to apply these changes."
            )
            return

        # Ask for confirmation
        self.stdout.write(
            self.style.WARNING("\n⚠️  This will change your homepage URL!")
        )
        confirm = input("Are you sure you want to proceed? (yes/no): ")

        if confirm.lower() != "yes":
            self.stdout.write("Operation cancelled.")
            return

        # Apply the changes directly in the database
        try:
            with transaction.atomic():
                from django.db import connection

                with connection.cursor() as cursor:
                    # Update slug to empty string
                    cursor.execute(
                        "UPDATE wagtailcore_page SET slug = '' WHERE id = %s",
                        [homepage.id]
                    )

                    # Update URL path to root
                    cursor.execute(
                        "UPDATE wagtailcore_page SET url_path = '/' WHERE id = %s",
                        [homepage.id]
                    )

                    # Update child page URL paths to remove the old homepage prefix
                    cursor.execute("""
                        UPDATE wagtailcore_page
                        SET url_path = REPLACE(url_path, %s, '/')
                        WHERE path LIKE %s AND id != %s
                    """, [homepage.url_path, f"{homepage.path}%", homepage.id])

                self.stdout.write(
                    self.style.SUCCESS(
                        "✅ Successfully set HomePage to root URL!"
                    )
                )

                # Refresh and verify
                homepage.refresh_from_db()
                self.stdout.write(f"    New slug: '{homepage.slug}'")
                self.stdout.write(f"    New URL path: {homepage.url_path}")

                self.stdout.write("\n📋 Next Steps:")
                self.stdout.write("1. Test your homepage at the root URL (/)")
                self.stdout.write("2. Remove custom URL redirects in your main urls.py")
                self.stdout.write("3. Verify all child page URLs work correctly")

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Error updating homepage: {e}")
            )
            raise
