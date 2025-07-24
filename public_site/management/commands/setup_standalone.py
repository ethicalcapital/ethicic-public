"""
Setup standalone mode with SQLite database
"""

import os
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from wagtail.models import Page, Site

from public_site.models import HomePage


class Command(BaseCommand):
    help = "Setup standalone SQLite database with basic content"

    def handle(self, *args, **options):
        self.stdout.write("Setting up standalone database...\n")

        # Create superuser
        admin_username = os.getenv("ADMIN_USERNAME", "srvo")
        admin_email = os.getenv("ADMIN_EMAIL", "sloane@ethicic.com")
        admin_password = os.getenv("ADMIN_PASSWORD")
        
        if not admin_password:
            self.stdout.write(
                self.style.ERROR(
                    "ADMIN_PASSWORD environment variable is required for setup. "
                    "Please set it before running this command."
                )
            )
            return
        
        if not User.objects.filter(username=admin_username).exists():
            User.objects.create_superuser(
                username=admin_username,
                email=admin_email,
                password=admin_password,
            )
            self.stdout.write(self.style.SUCCESS(f"✓ Created admin user: {admin_username}"))
        else:
            self.stdout.write(f"Admin user '{admin_username}' already exists")

        # Setup Wagtail site
        try:
            # Get or create root page
            root_page = Page.objects.filter(depth=1).first()
            if not root_page:
                self.stdout.write(self.style.ERROR("No root page found"))
                return

            # Create home page if it doesn't exist
            home_page = HomePage.objects.first()
            if not home_page:
                # Check if there's already a page at the home slug
                existing_home = root_page.get_children().filter(slug="home").first()
                if existing_home and not isinstance(existing_home.specific, HomePage):
                    # Delete the existing non-HomePage at this slug
                    existing_home.delete()
                    self.stdout.write("Removed existing non-HomePage at /home/")

                    # Refresh root page after deletion to fix tree structure
                    root_page.refresh_from_db()

                home_page = HomePage(
                    title="Ethical Capital",
                    slug="home",
                    hero_title="Ethical Capital",
                    hero_subtitle="Mission-driven investment management",
                    hero_tagline="We're not like other firms. Good.",
                    live=True,
                )

                # Use safer method to add child page
                try:
                    home_page = root_page.add_child(instance=home_page)
                    self.stdout.write(self.style.SUCCESS("✓ Created home page"))
                except Exception as e:
                    # Alternative approach if tree is corrupted
                    self.stdout.write(f"Standard add_child failed: {e}")
                    self.stdout.write("Trying alternative creation method...")

                    home_page.path = root_page.get_next_child_path()
                    home_page.depth = root_page.depth + 1
                    home_page.save()
                    self.stdout.write(
                        self.style.SUCCESS("✓ Created home page (alternative method)")
                    )

            else:
                self.stdout.write("Home page already exists")

            # Update site to point to home page
            site = Site.objects.first()
            if site:
                if site.root_page != home_page:
                    site.root_page = home_page
                    site.hostname = "localhost"
                    site.port = 80
                    site.site_name = "Ethical Capital"
                    site.save()
                    self.stdout.write(
                        self.style.SUCCESS("✓ Updated site configuration")
                    )
                else:
                    self.stdout.write("Site already configured correctly")
            else:
                Site.objects.create(
                    hostname="localhost",
                    port=80,
                    root_page=home_page,
                    is_default_site=True,
                    site_name="Ethical Capital",
                )
                self.stdout.write(self.style.SUCCESS("✓ Created site"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error setting up site: {e}"))
            import traceback

            traceback.print_exc()

        self.stdout.write(self.style.SUCCESS("\n✓ Standalone setup complete!"))
        self.stdout.write("You can now access the site and admin at /cms/")
