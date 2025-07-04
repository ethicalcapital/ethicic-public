#!/usr/bin/env python
"""
Management command to create initial page structure with imported content
"""

from django.core.management.base import BaseCommand
from wagtail.models import Page, Site

from public_site.models import AboutPage, ContactPage, HomePage


class Command(BaseCommand):
    help = "Create initial page structure"

    def handle(self, *args, **options):
        # Get the root page
        root = Page.objects.filter(depth=1).first()
        if not root:
            self.stdout.write(self.style.ERROR("No root page found!"))
            return

        # Delete the default homepage if it exists
        default_home = Page.objects.filter(
            title="Welcome to your new Wagtail site!"
        ).first()
        if default_home:
            default_home.delete()
            self.stdout.write("✓ Removed default homepage")

        # Create HomePage
        home = HomePage.objects.filter(slug="home").first()
        if not home:
            home = HomePage(
                title="Ethical Capital",
                slug="home",
                hero_title="Concentrated ethical portfolios for investors who refuse to compromise",
                hero_subtitle="<p>We hand-screen thousands of companies, exclude 57% of the S&P 500*, and build high-conviction portfolios where ethics and excellence converge. Fully transparent. Radically different. Fiduciary always.</p>",
                hero_tagline="We're not like other firms. Good.",
                excluded_percentage="57%",
                since_year="2021",
            )
            root.add_child(instance=home)
            self.stdout.write("✓ Created HomePage")

            # Publish the page
            home.save_revision().publish()

            # Set as the site root
            site = Site.objects.first()
            if site:
                site.root_page = home
                site.save()
                self.stdout.write("✓ Set HomePage as site root")
        else:
            self.stdout.write("✓ HomePage already exists")

        # Refresh home page instance
        home = HomePage.objects.get(slug="home")

        # Create About page
        about = AboutPage.objects.filter(slug="about").first()
        if not about:
            about = AboutPage(
                title="About",
                slug="about",
                headshot_alt_text="Sloane Ortel, Chief Investment Officer & Founder",
                philosophy_quote="<p>I believe that investing should reflect our values, not compromise them.</p>",
                philosophy_quote_link="/blog/",
                philosophy_quote_link_text="Read more about our philosophy →",
            )
            home.add_child(instance=about)
            about.save_revision().publish()
            self.stdout.write("✓ Created AboutPage")
        else:
            self.stdout.write("✓ AboutPage already exists")

        # Create Contact page
        contact = ContactPage.objects.filter(slug="contact").first()
        if not contact:
            contact = ContactPage(
                title="Contact",
                slug="contact",
                intro_text="<p>Ready to transform your investment research and compliance workflow?</p>",
                phone="+1 (555) 123-4567",
                email="hello@ethicic.com",
                address="90 N 400 E, Provo, UT, 84606",
                show_contact_form=True,
            )
            home.add_child(instance=contact)
            contact.save_revision().publish()
            self.stdout.write("✓ Created ContactPage")
        else:
            self.stdout.write("✓ ContactPage already exists")

        # Show final page structure
        self.stdout.write("\n📄 Final Page Structure:")
        for page in Page.objects.all():
            indent = "  " * (page.depth - 1)
            self.stdout.write(f"{indent}- {page.title} ({page.slug})")

        self.stdout.write(
            self.style.SUCCESS("\n✅ Page structure created successfully!")
        )
