#!/usr/bin/env python3
"""
Fix Wagtail site configuration to point to correct homepage.

This command updates the site configuration to point to the actual homepage
instead of the system root page.
"""

from django.core.management.base import BaseCommand
from wagtail.models import Site


class Command(BaseCommand):
    help = "Fix Wagtail site configuration to point to correct homepage"

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS("🔧 Fixing Wagtail Site Configuration")
        )
        self.stdout.write("=" * 50)

        # Find the HomePage
        from public_site.models import HomePage

        try:
            homepage = HomePage.objects.get()
            self.stdout.write(f"🏠 Found HomePage: {homepage.title} (ID: {homepage.id})")
        except HomePage.DoesNotExist:
            self.stdout.write(
                self.style.ERROR("❌ No HomePage found")
            )
            return

        # Update all sites to point to the homepage
        sites = Site.objects.all()

        for site in sites:
            self.stdout.write(f"\n🌐 Updating site: {site.hostname}:{site.port}")
            self.stdout.write(f"    Current root page: {site.root_page.title} (ID: {site.root_page.id})")

            if site.root_page.id != homepage.id:
                site.root_page = homepage
                site.save()
                self.stdout.write(f"    ✅ Updated to point to: {homepage.title} (ID: {homepage.id})")
            else:
                self.stdout.write("    ✅ Already pointing to correct homepage")

        self.stdout.write(
            self.style.SUCCESS(
                f"\n🎉 Site configuration fixed! All sites now point to {homepage.title}"
            )
        )

        self.stdout.write("\n📋 Next Steps:")
        self.stdout.write("1. Test your homepage - it should now show the proper content")
        self.stdout.write("2. Verify all navigation links work correctly")
        self.stdout.write("3. Check that child pages are accessible")
