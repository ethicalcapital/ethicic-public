"""
Django management command to create the missing pages that the homepage links to:
/consultation/, /guide/, /criteria/
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from wagtail.models import Site

from public_site.models import ConsultationPage, CriteriaPage, GuidePage


class Command(BaseCommand):
    help = "Create the missing pages that the homepage links to"

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force recreation of pages even if they exist",
        )

    def handle(self, *args, **options):
        force = options["force"]

        try:
            # Get the site and home page - prefer production site
            site = Site.objects.filter(hostname="www.ec1c.com").first()
            if not site:
                site = Site.objects.filter(is_default_site=True).first()
            home_page = site.root_page

            self.stdout.write(f"Working with site: {site}")
            self.stdout.write(f"Home page: {home_page}")

            with transaction.atomic():
                # Create or update Consultation Page
                self.create_consultation_page(home_page, force)

                # Create or update Guide Page
                self.create_guide_page(home_page, force)

                # Create or update Criteria Page
                self.create_criteria_page(home_page, force)

            self.stdout.write(
                self.style.SUCCESS("Successfully created missing homepage pages!")
            )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error creating pages: {e}"))
            raise

    def create_consultation_page(self, parent, force=False):
        """Create or update the consultation page."""
        slug = "consultation"

        # Check if page already exists
        existing = ConsultationPage.objects.filter(slug=slug).first()
        if existing and not force:
            self.stdout.write(f"Consultation page already exists at: /{slug}/")
            return existing

        if existing and force:
            existing.delete()
            self.stdout.write("Deleted existing consultation page")

        page = ConsultationPage(
            title="Schedule a Consultation",
            slug=slug,
            hero_title="Schedule a Consultation",
            hero_subtitle="Let's discuss how we can help align your investments with your values.",
            introduction="""
            <p>We believe in finding the right fit for both parties. Our consultation process is designed to understand your values, investment goals, and how our approach might align with your needs.</p>

            <p>During our conversation, we'll explore:</p>
            <ul>
                <li>Your current investment situation and goals</li>
                <li>Your ethical concerns and priorities</li>
                <li>How our screening criteria align with your values</li>
                <li>Which of our strategies might be the best fit</li>
                <li>The onboarding process and next steps</li>
            </ul>

            <p>There's no obligation to move forward, and we're happy to answer questions even if we're not the right match for you.</p>
            """,
            contact_email="hello@ec1c.com",
            scheduling_embed_code="",  # Can be filled in later with Calendly embed
        )

        parent.add_child(instance=page)
        page.save_revision().publish()

        self.stdout.write(self.style.SUCCESS(f"Created consultation page at: /{slug}/"))
        return page

    def create_guide_page(self, parent, force=False):
        """Create or update the guide page."""
        slug = "guide"

        # Check if page already exists
        existing = GuidePage.objects.filter(slug=slug).first()
        if existing and not force:
            self.stdout.write(f"Guide page already exists at: /{slug}/")
            return existing

        if existing and force:
            existing.delete()
            self.stdout.write("Deleted existing guide page")

        page = GuidePage(
            title="Investment Guide",
            slug=slug,
            hero_title="Investment Guide",
            hero_subtitle="Comprehensive guide to ethical investing principles and strategies.",
            guide_description="""
            <p>Our investment guide provides a comprehensive overview of our approach to ethical investing, including:</p>

            <h3>What You'll Learn</h3>
            <ul>
                <li><strong>Ethical Screening Process:</strong> How we identify and exclude companies that don't meet our criteria</li>
                <li><strong>Investment Strategies:</strong> Detailed explanation of our Growth, Income, and Diversification strategies</li>
                <li><strong>Research Methodology:</strong> Our six-lens evaluation framework for company analysis</li>
                <li><strong>Portfolio Construction:</strong> How we build concentrated, high-conviction portfolios</li>
                <li><strong>Performance Considerations:</strong> Understanding risk, return, and ethical trade-offs</li>
                <li><strong>Getting Started:</strong> Steps to begin your ethical investing journey</li>
            </ul>

            <p>Whether you're new to ethical investing or looking to refine your approach, this guide provides the foundation you need to make informed decisions.</p>
            """,
            external_guide_url="",  # Can be filled in when guide is ready
        )

        parent.add_child(instance=page)
        page.save_revision().publish()

        self.stdout.write(self.style.SUCCESS(f"Created guide page at: /{slug}/"))
        return page

    def create_criteria_page(self, parent, force=False):
        """Create or update the criteria page."""
        slug = "criteria"

        # Check if page already exists
        existing = CriteriaPage.objects.filter(slug=slug).first()
        if existing and not force:
            self.stdout.write(f"Criteria page already exists at: /{slug}/")
            return existing

        if existing and force:
            existing.delete()
            self.stdout.write("Deleted existing criteria page")

        page = CriteriaPage(
            title="Our Ethical Criteria",
            slug=slug,
            hero_title="Our Ethical Criteria",
            hero_subtitle="Transparent, rigorous screening criteria that guide our investment decisions.",
            criteria_description="""
            <p>We believe in radical transparency when it comes to our ethical screening process. Our criteria are publicly available, regularly updated, and based on extensive research into corporate practices.</p>

            <h3>Our Screening Philosophy</h3>
            <p>We exclude companies involved in activities that cause direct harm to people, animals, or the environment. This isn't about perfect companies—it's about avoiding the worst actors and supporting businesses that align with our values.</p>

            <h3>How We Developed These Criteria</h3>
            <ul>
                <li><strong>Research-Based:</strong> Built on academic research, industry reports, and stakeholder feedback</li>
                <li><strong>Client-Informed:</strong> Refined based on conversations with hundreds of ethical investors</li>
                <li><strong>Continuously Updated:</strong> Regularly revised as new information becomes available</li>
                <li><strong>Transparent Process:</strong> Methodology and reasoning are fully documented</li>
            </ul>

            <p>We exclude approximately 57% of S&P 500 companies based on these criteria, with 40% of our exclusions coming from proprietary research that identifies issues other rating agencies miss.</p>
            """,
            github_criteria_url="https://github.com/ethicalcapital/sage/blob/main/screening_policy.md",
            additional_resources="""
            <h3>Additional Resources</h3>
            <ul>
                <li><a href="/process/">Our Investment Process</a> - How we apply these criteria in practice</li>
                <li><a href="/strategies/">Investment Strategies</a> - How criteria implementation varies by strategy</li>
                <li><a href="https://apartheid-free.org/pledge/" target="_blank">Apartheid Free Pledge</a> - Our commitment to Palestinian human rights</li>
                <li><a href="/consultation/">Schedule a Consultation</a> - Discuss how our criteria align with your values</li>
            </ul>

            <p><strong>Questions about our criteria?</strong> We welcome feedback and questions about our screening process. Your input helps us identify issues we may have missed and continuously improve our approach.</p>
            """,
        )

        parent.add_child(instance=page)
        page.save_revision().publish()

        self.stdout.write(self.style.SUCCESS(f"Created criteria page at: /{slug}/"))
        return page
