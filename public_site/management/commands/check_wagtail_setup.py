from django.contrib.auth.models import Permission
from django.core.management.base import BaseCommand
from wagtail.models import Page, Site

from public_site.models import AboutPage, ContactPage, HomePage, ResearchPage


class Command(BaseCommand):
    help = 'Check Wagtail page setup and permissions'

    def handle(self, *args, **options):
        self.stdout.write("=== Wagtail Page Tree ===")

        # Get the root page
        try:
            root_page = Page.objects.get(id=1)
            self.stdout.write(f"Root Page: {root_page.title} (ID: {root_page.id})")
        except Page.DoesNotExist:
            self.stdout.write(self.style.ERROR("No root page found!"))
            return

        # Get all pages
        all_pages = Page.objects.all()
        self.stdout.write(f"\nTotal pages in database: {all_pages.count()}")

        # Show page tree
        self.stdout.write("\nPage Tree:")
        for page in all_pages:
            indent = "  " * (page.depth - 1)
            specific_class = page.specific_class
            page_type = specific_class.__name__ if specific_class else "Unknown"
            status = "LIVE" if page.live else "DRAFT"
            self.stdout.write(f"{indent}- {page.title} (ID: {page.id}, Type: {page_type}, Status: {status})")

        # Check sites
        self.stdout.write("\n=== Wagtail Sites ===")
        sites = Site.objects.all()
        for site in sites:
            self.stdout.write(f"Site: {site.hostname} (Root Page: {site.root_page.title})")

        # Check page permissions
        self.stdout.write("\n=== Page Permissions ===")
        page_permissions = Permission.objects.filter(
            content_type__app_label='wagtailcore',
            content_type__model='page'
        )
        for perm in page_permissions:
            self.stdout.write(f"- {perm.codename}: {perm.name}")

        # Check specific page models
        self.stdout.write("\n=== Public Site Page Models ===")
        page_models = [HomePage, AboutPage, ContactPage, ResearchPage]
        for model in page_models:
            count = model.objects.count()
            self.stdout.write(f"- {model.__name__}: {count} instances")
            if count > 0:
                for page in model.objects.all():
                    self.stdout.write(f"  - {page.title} (ID: {page.id}, Live: {page.live}, URL: {page.url})")

        # Check for common issues
        self.stdout.write("\n=== Common Issues Check ===")

        # Check if public_site pages are under the right parent
        public_pages = Page.objects.filter(content_type__app_label='public_site')
        if not public_pages.exists():
            self.stdout.write(self.style.WARNING("No public_site pages found in database!"))

        # Check for orphaned pages
        orphaned = Page.objects.filter(depth=1).exclude(id=1)
        if orphaned.exists():
            self.stdout.write(self.style.WARNING(f"Found {orphaned.count()} orphaned pages at root level"))

        # Check page editability
        self.stdout.write("\n=== Page Editability Check ===")
        for page in public_pages[:5]:  # Check first 5 pages
            specific_page = page.specific
            has_content_panels = hasattr(specific_page, 'content_panels')
            self.stdout.write(f"- {specific_page.title}: Has content_panels: {has_content_panels}")
            if has_content_panels:
                panel_count = len(specific_page.content_panels)
                self.stdout.write(f"  Panel count: {panel_count}")
