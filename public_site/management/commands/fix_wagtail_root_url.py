"""
Django management command to fix Wagtail site root page URL structure.

This command changes the site root page from the current "home" page to the true root page,
which will make all child page URLs appear at the root level instead of under /home/.

Usage:
    python manage.py fix_wagtail_root_url [--dry-run]
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from wagtail.models import Page, Site


class Command(BaseCommand):
    help = "Fix Wagtail site root page URL structure to remove /home/ prefix"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be changed without making changes",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]

        self.stdout.write(
            self.style.SUCCESS("🔧 Wagtail Root URL Structure Fix")
        )
        self.stdout.write("=" * 50)

        # Get current site configuration
        sites = Site.objects.all()

        if not sites.exists():
            self.stdout.write(
                self.style.ERROR("❌ No sites found in database")
            )
            return

        # Check current root pages
        self.stdout.write("📊 Current Site Configuration:")
        for site in sites:
            root_page = site.root_page
            self.stdout.write(
                f"  Site: {site.hostname} (ID: {site.id})"
            )
            self.stdout.write(
                f"    Root Page: {root_page.title} (ID: {root_page.id})"
            )
            self.stdout.write(
                f"    Root URL Path: {root_page.url_path}"
            )
            self.stdout.write(
                f"    Root Slug: {root_page.slug}"
            )

        # Find the actual root page (depth=1)
        try:
            true_root = Page.objects.get(depth=1)
            self.stdout.write("\n🎯 Found True Root Page:")
            self.stdout.write(f"    Title: {true_root.title}")
            self.stdout.write(f"    ID: {true_root.id}")
            self.stdout.write(f"    URL Path: {true_root.url_path}")
            self.stdout.write(f"    Slug: {true_root.slug}")
        except Page.DoesNotExist:
            self.stdout.write(
                self.style.ERROR("❌ No root page found at depth=1")
            )
            return
        except Page.MultipleObjectsReturned:
            self.stdout.write(
                self.style.ERROR("❌ Multiple root pages found at depth=1")
            )
            return

        # Check if any sites need fixing
        sites_to_fix = sites.exclude(root_page_id=true_root.id)

        if not sites_to_fix.exists():
            self.stdout.write(
                self.style.SUCCESS("✅ All sites already point to the correct root page!")
            )
            return

        self.stdout.write("\n🔄 Sites that need fixing:")
        for site in sites_to_fix:
            self.stdout.write(
                f"  {site.hostname} -> Change root from ID {site.root_page_id} to ID {true_root.id}"
            )

        # Show what child pages will be affected
        current_home_pages = Page.objects.filter(
            id__in=sites_to_fix.values_list('root_page_id', flat=True)
        )

        for home_page in current_home_pages:
            child_pages = home_page.get_children().live()
            if child_pages.exists():
                self.stdout.write(f"\n📄 Child pages under '{home_page.title}' that will move to root level:")
                for child in child_pages:
                    old_url = child.url_path
                    # Calculate what the new URL would be
                    new_url = old_url.replace(home_page.url_path, '/')
                    if new_url.startswith('//'):
                        new_url = new_url[1:]  # Remove double slash
                    self.stdout.write(f"    {child.title}: {old_url} → {new_url}")

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
            self.style.WARNING("\n⚠️  This will change your site's URL structure!")
        )
        confirm = input("Are you sure you want to proceed? (yes/no): ")

        if confirm.lower() != 'yes':
            self.stdout.write("Operation cancelled.")
            return

        # Apply the changes
        try:
            with transaction.atomic():
                updated_count = 0
                for site in sites_to_fix:
                    old_root_id = site.root_page_id
                    site.root_page = true_root
                    site.save()
                    updated_count += 1

                    self.stdout.write(
                        f"✅ Updated {site.hostname}: root page changed from ID {old_root_id} to ID {true_root.id}"
                    )

                self.stdout.write(
                    self.style.SUCCESS(
                        f"\n🎉 Successfully updated {updated_count} site(s)!"
                    )
                )

                self.stdout.write("\n📋 Next Steps:")
                self.stdout.write("1. Test your site URLs to ensure they work correctly")
                self.stdout.write("2. Remove any custom URL redirects that are no longer needed")
                self.stdout.write("3. Update any hardcoded URLs in your templates or code")
                self.stdout.write("4. Consider setting up redirects for any bookmarked /home/ URLs")

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Error updating sites: {e}")
            )
            raise
