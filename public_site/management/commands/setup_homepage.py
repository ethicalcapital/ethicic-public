"""
Management command to set up the complete site structure for production deployment.
"""
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from wagtail.models import Page, Site

from public_site.models import AboutPage, BlogIndexPage, ContactPage, HomePage


class Command(BaseCommand):
    help = "Set up the complete site structure including homepage and essential pages"

    def handle(self, *args, **options):
        """Set up the complete site structure."""

        self.stdout.write(self.style.SUCCESS("Setting up complete site structure..."))

        # Create superuser if none exists
        self.setup_superuser()

        # Get root page
        root = Page.get_first_root_node()
        self.stdout.write(f"Root page: {root.title} (ID: {root.id})")

        # Delete any existing sites to start fresh
        sites_deleted = Site.objects.all().delete()
        self.stdout.write(f"Cleared {sites_deleted[0]} existing sites")

        # Set up homepage
        homepage = self.setup_homepage(root)

        # Set up essential pages
        self.setup_essential_pages(homepage)

        # Configure site
        self.setup_site(homepage)

        self.stdout.write(self.style.SUCCESS("Site setup complete!"))

    def setup_superuser(self):
        """Create superuser if none exists."""
        if not User.objects.filter(is_superuser=True).exists():
            User.objects.create_superuser(
                username="admin",
                email="admin@ethicic.com",
                password="admin123"  # Should be changed in production
            )
            self.stdout.write(self.style.SUCCESS("Created superuser admin/admin123"))
        else:
            self.stdout.write("Superuser already exists")

    def setup_homepage(self, root):
        """Set up the homepage."""

        # Check if HomePage already exists
        existing_homepage = HomePage.objects.first()

        if existing_homepage:
            homepage = existing_homepage
            self.stdout.write(f"Using existing HomePage: {homepage.title}")
        else:
            # Create new HomePage with all required fields
            homepage = HomePage(
                title="Ethical Capital Investment Collaborative",
                slug="homepage",
                hero_tagline="Ethical Investing",
                hero_title="Where Ethics Drive Investment Excellence",
                hero_subtitle="<p>Professional investment management guided by your values.</p>",
                excluded_percentage="57%",
                since_year="2020",
                philosophy_title="Values-Based Investment Philosophy",
                philosophy_content="<p>We believe that ethical investing delivers superior long-term returns while creating positive impact in the world.</p>",
                philosophy_highlight="Every investment decision reflects your values and drives positive change.",
                cta_title="Ready to Start Your Ethical Investment Journey?",
                cta_description="<p>Schedule a consultation to learn how we can help you invest in line with your values.</p>",
                client_availability_text="Currently accepting new clients",
                disclaimer_text="<p>Investment advisory services provided by Ethical Capital Investment Collaborative.</p>",
                # Process principles content
                principles_intro="<p>Our investment approach is guided by clear principles that ensure every decision aligns with your values while pursuing superior returns.</p>",
                process_principle_1_title="Fiduciary Standard",
                process_principle_1_content="We operate under the highest fiduciary standard, putting your interests first in every decision.",
                process_principle_2_title="Transparent Process",
                process_principle_2_content="Complete transparency in our investment process, from screening to portfolio construction.",
                process_principle_3_title="Continuous Research",
                process_principle_3_content="Ongoing research and analysis to identify opportunities that align with your values.",
                practice_principle_1_title="Values Integration",
                practice_principle_1_content="Deep integration of ethical criteria into every investment decision without compromising returns.",
                practice_principle_2_title="Active Engagement",
                practice_principle_2_content="Active ownership and engagement with companies to drive positive change.",
                practice_principle_3_title="Impact Measurement",
                practice_principle_3_content="Rigorous measurement and reporting of both financial and impact outcomes.",
                # Strategy content
                strategies_intro="<p>We offer three distinct strategies designed to meet different client needs while maintaining our commitment to ethical investing.</p>",
                # Process steps
                process_step_1_title="Discovery & Values Assessment",
                process_step_1_content="We begin by understanding your financial goals, values, and specific ethical preferences through comprehensive discovery.",
                process_step_2_title="Ethical Screening & Research",
                process_step_2_content="Our rigorous research process screens investments against your values while identifying superior risk-adjusted opportunities.",
                process_step_3_title="Portfolio Construction",
                process_step_3_content="We construct concentrated, high-conviction portfolios that reflect your values without compromising on diversification.",
                process_step_4_title="Ongoing Management & Reporting",
                process_step_4_content="Continuous monitoring, rebalancing, and transparent reporting on both financial performance and impact outcomes.",
                # Who we serve
                serve_individual_title="Individual & Family Investors",
                serve_individual_content="Comprehensive investment management for individuals and families who want their investments to reflect their values.",
                serve_advisor_title="Registered Investment Advisors",
                serve_advisor_content="Partnership opportunities for RIAs who want to offer ethical investing solutions to their clients.",
                serve_institution_title="Institutions & Nonprofits",
                serve_institution_content="Custom ethical investment solutions for endowments, foundations, and other institutional investors."
            )

            try:
                # Add to root as child
                root.add_child(instance=homepage)
                homepage.save_revision().publish()
                self.stdout.write(self.style.SUCCESS(f"Created new HomePage: {homepage.title}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error creating homepage: {e}"))
                return None

        # Create site pointing to homepage
        try:
            site = Site.objects.create(
                hostname="*",  # Accept any hostname
                port=80,
                root_page=homepage,
                is_default_site=True,
                site_name="Ethical Capital"
            )

            self.stdout.write(self.style.SUCCESS(f"Site created: {site.hostname}:{site.port} -> {homepage.title}"))
            self.stdout.write(f"Homepage URL: {homepage.url}")
            self.stdout.write(f"Homepage live: {homepage.live}")
            self.stdout.write(f"Homepage content type: {homepage.content_type}")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error creating site: {e}"))

        return homepage

    def setup_essential_pages(self, homepage):
        """Create essential pages for the site."""
        self.stdout.write("Creating essential pages...")

        # About page
        try:
            about_page = AboutPage(
                title="About Us",
                slug="about",
                mission_statement="<p>Our mission is to provide ethical investment management.</p>",
                team_intro="<p>Meet our experienced team.</p>",
                company_story="<p>Founded to bridge the gap between values and investing.</p>"
            )
            homepage.add_child(instance=about_page)
            about_page.save_revision().publish()
            self.stdout.write("  ✓ Created About page")
        except Exception as e:
            self.stdout.write(f"  ✗ About page: {e}")

        # Blog index
        try:
            blog_index = BlogIndexPage(
                title="Blog",
                slug="blog",
                intro_text="<p>Insights on ethical investing and market commentary.</p>"
            )
            homepage.add_child(instance=blog_index)
            blog_index.save_revision().publish()
            self.stdout.write("  ✓ Created Blog index")
        except Exception as e:
            self.stdout.write(f"  ✗ Blog index: {e}")

        # Contact page
        try:
            contact_page = ContactPage(
                title="Contact",
                slug="contact",
                intro_text="<p>Get in touch to learn more about our services.</p>",
                show_contact_form=True,
                email="hello@ethicic.com",
                phone="555-123-4567",
                address="<p>123 Investment St<br>Suite 100<br>City, State 12345</p>"
            )
            homepage.add_child(instance=contact_page)
            contact_page.save_revision().publish()
            self.stdout.write("  ✓ Created Contact page")
        except Exception as e:
            self.stdout.write(f"  ✗ Contact page: {e}")

    def setup_site(self, homepage):
        """Configure the site to point to the homepage."""
        try:
            site = Site.objects.create(
                hostname="*",  # Accept any hostname
                port=80,
                root_page=homepage,
                is_default_site=True,
                site_name="Ethical Capital"
            )

            self.stdout.write(self.style.SUCCESS(f"Site created: {site.hostname}:{site.port} -> {homepage.title}"))
            self.stdout.write(f"Homepage URL: {homepage.url}")
            self.stdout.write(f"Homepage live: {homepage.live}")
            self.stdout.write(f"Homepage content type: {homepage.content_type}")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error creating site: {e}"))
