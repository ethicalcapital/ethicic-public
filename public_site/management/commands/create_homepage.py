"""
Simplified command to create homepage after Wagtail is properly initialized
"""
from django.core.management.base import BaseCommand
from wagtail.models import Page, Site

from public_site.models import HomePage


class Command(BaseCommand):
    help = "Create homepage for the site"

    def handle(self, *args, **options):
        # Check if HomePage already exists
        if HomePage.objects.exists():
            self.stdout.write("Homepage already exists")
            return

        # Get the root page
        try:
            root_page = Page.objects.get(id=2)  # Wagtail's default home
        except Page.DoesNotExist:
            try:
                root_page = Page.objects.get(depth=2, slug="home")
            except Page.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR("Could not find root page. Run migrations first.")
                )
                return

        # Delete the default home page and replace with our HomePage
        try:
            # Create our homepage with the same ID to preserve references
            home = HomePage(
                id=root_page.id,
                title="Ethical Capital",
                slug="home",
                hero_title="Welcome to Ethical Capital",
                hero_subtitle="Sustainable investing for a better future",
                path=root_page.path,
                depth=root_page.depth,
                numchild=root_page.numchild,
                url_path=root_page.url_path,
                locale_id=root_page.locale_id,
                content_type=root_page.content_type
            )

            # Delete old page and save new one
            root_page.delete(keep_parents=True)
            home.save()

            self.stdout.write(
                self.style.SUCCESS("Successfully created HomePage")
            )

            # Update the default site
            try:
                site = Site.objects.get(is_default_site=True)
                site.root_page = home
                site.save()
                self.stdout.write("Updated default site")
            except Site.DoesNotExist:
                pass

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Failed to create homepage: {e}")
            )
