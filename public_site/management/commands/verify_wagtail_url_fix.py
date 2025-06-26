"""
Django management command to verify the Wagtail URL structure fix was successful.

This checks that:
1. Site root_page points to the true root (ID 1)
2. Homepage has empty slug and serves at "/"
3. Child pages have proper URLs without /home/ prefix

Usage:
    python manage.py verify_wagtail_url_fix
"""

from django.core.management.base import BaseCommand
from wagtail.models import Page, Site


class Command(BaseCommand):
    help = "Verify Wagtail URL structure fix was successful"

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS("🔍 Verifying Wagtail URL Structure Fix")
        )
        self.stdout.write("=" * 50)

        success = True

        # Check site configuration
        self.stdout.write("📊 Site Configuration:")
        sites = Site.objects.all()
        for site in sites:
            root_page = site.root_page
            if root_page.depth == 1:
                self.stdout.write(
                    f"  ✅ {site.hostname}: Points to true root (ID {root_page.id})"
                )
            else:
                self.stdout.write(
                    f"  ❌ {site.hostname}: Points to wrong page (ID {root_page.id}, depth {root_page.depth})"
                )
                success = False

        # Check homepage configuration
        self.stdout.write("\n🏠 Homepage Configuration:")
        from public_site.models import HomePage

        try:
            homepage = HomePage.objects.get()
            if homepage.slug == '':
                self.stdout.write("  ✅ Homepage slug is empty (correct)")
            else:
                self.stdout.write(f"  ❌ Homepage slug is '{homepage.slug}' (should be empty)")
                success = False

            if homepage.url_path == '/':
                self.stdout.write("  ✅ Homepage URL path is '/' (correct)")
            else:
                self.stdout.write(f"  ❌ Homepage URL path is '{homepage.url_path}' (should be '/')")
                success = False

        except HomePage.DoesNotExist:
            self.stdout.write("  ❌ No HomePage found")
            success = False

        # Check child page URLs
        self.stdout.write("\n📄 Child Page URLs:")
        if 'homepage' in locals():
            child_pages = homepage.get_children().live()[:10]  # Sample of child pages

            for child in child_pages:
                expected_url = f"/{child.slug}/"
                if child.url_path == expected_url:
                    self.stdout.write(f"  ✅ {child.title}: {child.url_path}")
                else:
                    self.stdout.write(f"  ❌ {child.title}: {child.url_path} (expected {expected_url})")
                    success = False

        # Check for any remaining /home/ URLs
        self.stdout.write("\n🔍 Checking for remaining /home/ URLs:")
        pages_with_home = Page.objects.filter(url_path__contains='/home/').live()

        if pages_with_home.exists():
            self.stdout.write(f"  ❌ Found {pages_with_home.count()} pages with /home/ in URL:")
            for page in pages_with_home[:5]:  # Show first 5
                self.stdout.write(f"    - {page.title}: {page.url_path}")
            success = False
        else:
            self.stdout.write("  ✅ No pages found with /home/ in URL")

        # Summary
        self.stdout.write("\n" + "=" * 50)
        if success:
            self.stdout.write(
                self.style.SUCCESS("🎉 All checks passed! Wagtail URL structure is fixed.")
            )
            self.stdout.write("\n📋 What was accomplished:")
            self.stdout.write("✅ Site root page now points to true root (ID 1)")
            self.stdout.write("✅ Homepage serves at root URL (/)")
            self.stdout.write("✅ All child pages serve at proper URLs (/about/, /contact/, etc.)")
            self.stdout.write("✅ No more /home/ prefix in URLs")

            self.stdout.write("\n🚀 Next steps:")
            self.stdout.write("1. Test your site to ensure all URLs work")
            self.stdout.write("2. Set up redirects from old /home/* URLs if needed")
            self.stdout.write("3. Update any hardcoded URLs in templates or documentation")
        else:
            self.stdout.write(
                self.style.ERROR("❌ Some issues found. Please review the output above.")
            )
