"""
Django management command to move the HomePage to be a direct child of the root page.

This moves the "Ethical Capital | Investment Advisory" page (currently at depth 2)
to be a direct child of the root page and ensures it serves as the homepage.

Usage:
    python manage.py move_homepage_to_root [--dry-run]
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from wagtail.models import Page


class Command(BaseCommand):
    help = "Move HomePage to be a direct child of root page for proper URL structure"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be changed without making changes",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]

        self.stdout.write(
            self.style.SUCCESS("🏠 Moving HomePage to Root Level")
        )
        self.stdout.write("=" * 50)

        # Get the root page
        try:
            root_page = Page.objects.get(depth=1)
            self.stdout.write(f"📍 Root page: {root_page.title} (ID: {root_page.id})")
        except Page.DoesNotExist:
            self.stdout.write(
                self.style.ERROR("❌ No root page found")
            )
            return

        # Find the HomePage
        from public_site.models import HomePage

        try:
            homepage = HomePage.objects.get()
            self.stdout.write(f"🏠 Found HomePage: {homepage.title} (ID: {homepage.id})")
            self.stdout.write(f"    Current depth: {homepage.depth}")
            self.stdout.write(f"    Current URL path: {homepage.url_path}")
            self.stdout.write(f"    Current parent: {homepage.get_parent().title if homepage.get_parent() else 'None'}")
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

        # Check if HomePage is already at root level
        if homepage.get_parent().id == root_page.id:
            self.stdout.write(
                self.style.SUCCESS("✅ HomePage is already at root level!")
            )
            return

        # Show what would happen
        current_children = homepage.get_children().live()
        self.stdout.write(f"\n📦 HomePage has {current_children.count()} child pages:")
        for child in current_children[:10]:  # Show first 10
            self.stdout.write(f"    - {child.title} ({child.url_path})")
        if current_children.count() > 10:
            self.stdout.write(f"    ... and {current_children.count() - 10} more")

        self.stdout.write("\n🔄 Planned changes:")
        self.stdout.write(f"    Move HomePage '{homepage.title}' to be child of '{root_page.title}'")
        self.stdout.write(f"    HomePage URL will change from {homepage.url_path} to /")
        self.stdout.write("    All child pages will move up one level in the URL structure")

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
            self.style.WARNING("\n⚠️  This will restructure your page hierarchy!")
        )
        confirm = input("Are you sure you want to proceed? (yes/no): ")

        if confirm.lower() != "yes":
            self.stdout.write("Operation cancelled.")
            return

        # Apply the changes
        try:
            with transaction.atomic():
                # Move the homepage to be a child of root
                homepage.move(root_page, pos="last-child")

                # Update the homepage URL path to "/"
                homepage.slug = ""  # Empty slug for homepage
                homepage.save()

                self.stdout.write(
                    self.style.SUCCESS(
                        f"✅ Successfully moved {homepage.title} to root level!"
                    )
                )

                # Refresh and verify
                homepage.refresh_from_db()
                self.stdout.write(f"    New depth: {homepage.depth}")
                self.stdout.write(f"    New URL path: {homepage.url_path}")
                self.stdout.write(f"    New parent: {homepage.get_parent().title}")

                self.stdout.write("\n📋 Next Steps:")
                self.stdout.write("1. Test your homepage at the root URL (/)")
                self.stdout.write("2. Verify all child page URLs work correctly")
                self.stdout.write("3. Remove custom URL redirects in your main urls.py")
                self.stdout.write("4. Update any hardcoded URLs in templates")

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Error moving homepage: {e}")
            )
            raise
