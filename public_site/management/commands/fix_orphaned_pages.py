"""
Management command to fix orphaned pages that are causing 404 errors.
Moves pages from being siblings of the homepage to children of the homepage.
"""

from django.core.management.base import BaseCommand

from public_site.models import (
    AboutPage,
    AccessibilityPage,
    FAQIndexPage,
    HomePage,
    NewsletterPage,
    SolutionsPage,
)


class Command(BaseCommand):
    help = "Fix orphaned pages that are siblings instead of children of homepage"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be moved without actually moving pages",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]

        self.stdout.write(self.style.SUCCESS("🔍 Fixing Orphaned Pages"))
        self.stdout.write("=" * 50)

        # Get the homepage (site root)
        try:
            homepage = HomePage.objects.first()
            if not homepage:
                self.stdout.write(self.style.ERROR("❌ No HomePage found!"))
                return

            self.stdout.write(
                f"✅ Found homepage: {homepage.title} (ID: {homepage.id})"
            )
            self.stdout.write(f"   Homepage path: {homepage.path}")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error finding homepage: {e}"))
            return

        # Define pages that should be children of homepage
        pages_to_fix = [
            ("FAQ", FAQIndexPage),
            ("About", AboutPage),
            ("Solutions", SolutionsPage),
            ("Newsletter", NewsletterPage),
            ("Accessibility", AccessibilityPage),
        ]

        moved_pages = []

        for page_name, page_model in pages_to_fix:
            try:
                # Find the page
                page = page_model.objects.first()

                if not page:
                    self.stdout.write(f"⚠️  {page_name} page not found, skipping...")
                    continue

                # Check if it's already a child of homepage
                if page.get_parent() == homepage:
                    self.stdout.write(
                        f"✅ {page_name} page already correctly positioned"
                    )
                    continue

                # Check current position
                current_parent = page.get_parent()
                self.stdout.write(f"\n📄 {page_name} Page Analysis:")
                self.stdout.write(f"   Title: {page.title}")
                self.stdout.write(f"   ID: {page.id}")
                self.stdout.write(f"   Current URL: {page.url}")
                self.stdout.write(f"   Current path: {page.path}")
                self.stdout.write(
                    f"   Current parent: {current_parent.title if current_parent else 'None'}"
                )
                self.stdout.write(f"   Expected parent: {homepage.title}")

                if dry_run:
                    self.stdout.write("   🔄 Would move to be child of homepage")
                else:
                    try:
                        # Move the page to be a child of homepage
                        page.move(homepage, pos="last-child")
                        page.refresh_from_db()

                        self.stdout.write("   ✅ Moved successfully!")
                        self.stdout.write(f"   New path: {page.path}")
                        self.stdout.write(f"   New URL: {page.url}")

                        moved_pages.append((page_name, page.url))

                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f"   ❌ Failed to move: {e}")
                        )

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ Error processing {page_name} page: {e}")
                )

        # Summary
        self.stdout.write("\n" + "=" * 50)
        if dry_run:
            self.stdout.write(
                self.style.WARNING("🔍 DRY RUN COMPLETE - No changes made")
            )
            self.stdout.write("Run without --dry-run to actually move the pages")
        elif moved_pages:
            self.stdout.write(
                self.style.SUCCESS(f"✅ Successfully moved {len(moved_pages)} pages:")
            )
            for page_name, url in moved_pages:
                self.stdout.write(f"   • {page_name}: {url}")
            self.stdout.write(
                "\n📝 These pages should now be accessible at their URLs!"
            )
        else:
            self.stdout.write("ℹ️  No pages needed to be moved")

        # Test URLs
        if not dry_run and moved_pages:
            self.stdout.write("\n🧪 Testing moved pages...")
            from urllib.parse import urljoin

            import requests

            base_url = "https://ethicic.com"

            for page_name, url in moved_pages:
                try:
                    test_url = urljoin(base_url, url)
                    # Use HEAD request to avoid loading full page
                    response = requests.head(test_url, timeout=10)

                    if response.status_code == 200:
                        self.stdout.write(f"   ✅ {page_name}: {test_url} - OK")
                    else:
                        self.stdout.write(
                            f"   ⚠️  {page_name}: {test_url} - HTTP {response.status_code}"
                        )

                except Exception as e:
                    self.stdout.write(f"   ❌ {page_name}: Failed to test - {e}")

        self.stdout.write("\n🎉 Command completed!")
