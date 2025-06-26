"""
Django management command to fix the HomePage slug to serve at root URL.

This changes the HomePage slug from "home" to empty string so it serves at "/" instead of "/home/".

Usage:
    python manage.py fix_homepage_slug [--dry-run]
"""

from django.core.management.base import BaseCommand
from django.db import transaction


class Command(BaseCommand):
    help = "Fix HomePage slug to serve at root URL (/) instead of /home/"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be changed without making changes",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]

        self.stdout.write(
            self.style.SUCCESS("🔧 Fixing HomePage Slug")
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

        # Check if slug is already correct
        if homepage.slug in {'', 'home'}:

            if homepage.slug == '':
                self.stdout.write(
                    self.style.SUCCESS("✅ Homepage slug is already empty (correct for root URL)")
                )

                # But check if URL path is still wrong
                if homepage.url_path != '/':
                    self.stdout.write(
                        f"⚠️  But URL path is '{homepage.url_path}' instead of '/'"
                    )
                    self.stdout.write("    This will be fixed by changing the slug.")
                else:
                    self.stdout.write("✅ Homepage is already configured correctly!")
                    return
            else:
                self.stdout.write(f"🔄 Will change slug from '{homepage.slug}' to '' (empty)")
                self.stdout.write(f"    URL will change from {homepage.url_path} to /")
        else:
            self.stdout.write(
                self.style.WARNING(f"⚠️  Unexpected slug: '{homepage.slug}'")
            )
            self.stdout.write("    Will change to '' (empty) for root URL")

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

        if confirm.lower() != 'yes':
            self.stdout.write("Operation cancelled.")
            return

        # Apply the changes
        try:
            with transaction.atomic():
                old_slug = homepage.slug
                old_url_path = homepage.url_path

                # Set empty slug for root URL
                homepage.slug = ''
                homepage.save()

                # Refresh to get updated URL path
                homepage.refresh_from_db()

                self.stdout.write(
                    self.style.SUCCESS(
                        "✅ Successfully updated HomePage slug!"
                    )
                )
                self.stdout.write(f"    Changed slug from '{old_slug}' to '{homepage.slug}'")
                self.stdout.write(f"    URL path changed from {old_url_path} to {homepage.url_path}")

                self.stdout.write("\n📋 Next Steps:")
                self.stdout.write("1. Test your homepage at the root URL (/)")
                self.stdout.write("2. Remove custom URL redirects in your main urls.py")
                self.stdout.write("3. Verify all child page URLs work correctly")
                self.stdout.write("4. Set up redirects from /home/ to / if needed for bookmarks")

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Error updating homepage slug: {e}")
            )
            raise
