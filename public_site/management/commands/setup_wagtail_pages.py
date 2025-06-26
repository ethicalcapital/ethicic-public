from django.core.management.base import BaseCommand
from wagtail.models import Page, Site

from public_site.models import (
    AboutPage,
    ContactPage,
    HomePage,
    OnboardingPage,
    ProcessPage,
    ResearchPage,
)


class Command(BaseCommand):
    help = "Sets up initial Wagtail pages for the public site"

    def handle(self, *args, **kwargs):
        # Get the root page
        root_page = Page.objects.get(id=1)

        # Delete the default welcome page if it exists
        try:
            welcome_page = Page.objects.get(id=2)
            if welcome_page.title == "Welcome to your new Wagtail site!":
                welcome_page.delete()
                self.stdout.write(self.style.SUCCESS("Deleted default welcome page"))
        except Page.DoesNotExist:
            pass

        # Create HomePage
        homepage = HomePage(
            title="Ethical Capital Investment Collaborative",
            slug="home",
            hero_title="We're not like other firms. Good.",
            hero_subtitle="Turning ethics into peace of mind through disciplined investment research",
            hero_description="<p>Sophisticated investment management that aligns your portfolio with your principles through proprietary research and transparent methodologies.</p>",
            features_title="WHAT MAKES US DIFFERENT",
            cta_title="Ready to find value in your values?",
            cta_description="<p>Join sophisticated investors aligning their portfolios with their principles.</p>",
            cta_button_text="START A CONVERSATION",
            cta_button_url="/contact/",
        )
        root_page.add_child(instance=homepage)
        homepage.save_revision().publish()
        self.stdout.write(self.style.SUCCESS(f"Created HomePage: {homepage.title}"))

        # Update site to point to homepage
        site = Site.objects.get(is_default_site=True)
        site.root_page = homepage
        site.hostname = "ec1c.com"
        site.site_name = "Ethical Capital Investment Collaborative"
        site.save()
        self.stdout.write(self.style.SUCCESS("Updated default site configuration"))

        # Create other pages
        # About Page
        about_page = AboutPage(
            title="About Us",
            slug="about",
            intro_text="<p>Learn about our mission to democratize investment intelligence and compliance technology.</p>",
            body="<p>Founded in 2021, Ethical Capital Investment Collaborative represents a new approach to values-aligned investing.</p>",
            team_title="Our Team",
            team_description="<p>Led by professionals with decades of experience in investment management and technology.</p>",
            values_title="Our Values",
            values_content="<p>Transparency, integrity, and a commitment to helping investors align their portfolios with their principles.</p>",
        )
        homepage.add_child(instance=about_page)
        about_page.save_revision().publish()
        self.stdout.write(self.style.SUCCESS(f"Created AboutPage: {about_page.title}"))

        # Research Page
        research_page = ResearchPage(
            title="Our Research",
            slug="research",
            intro_text="<p>Our research methodology combines proprietary analysis with transparent screening processes.</p>",
            methodology_content="<p>We believe in showing our work. Our research process is designed to be transparent and reproducible.</p>",
            screening_title="Screening Process",
            screening_content="<p>We hand-screen thousands of companies, identifying ethical concerns that third-party ESG ratings often miss.</p>",
            analysis_title="Analysis Framework",
            analysis_content="<p>Our proprietary exclusions reflect deep, original analysis designed to enhance portfolio quality.</p>",
            transparency_title="Radical Transparency",
            transparency_content='<p>We "show the garage" - providing access to our exclusion lists, scoring methodologies, and research processes.</p>',
        )
        homepage.add_child(instance=research_page)
        research_page.save_revision().publish()
        self.stdout.write(
            self.style.SUCCESS(f"Created ResearchPage: {research_page.title}"),
        )

        # Process Page
        process_page = ProcessPage(
            title="Our Process",
            slug="process",
            intro_text="<p>Our investment process combines ethical screening with disciplined portfolio construction.</p>",
            process_overview="<p>A systematic approach to values-aligned investing that doesn't compromise on returns.</p>",
            step1_title="Ethical Screening",
            step1_content="<p>Comprehensive values alignment: BDS-compliant, fossil fuel free, tobacco free, weapons free.</p>",
            step2_title="Proprietary Research",
            step2_content="<p>Hand-screening of companies to identify concerns beyond standard ESG ratings.</p>",
            step3_title="Portfolio Construction",
            step3_content="<p>Disciplined diversification with concentration targets around 2% per holding.</p>",
            step4_title="Ongoing Monitoring",
            step4_content="<p>Continuous research updates and client partnership in identifying new concerns.</p>",
        )
        homepage.add_child(instance=process_page)
        process_page.save_revision().publish()
        self.stdout.write(
            self.style.SUCCESS(f"Created ProcessPage: {process_page.title}"),
        )

        # Contact Page
        contact_page = ContactPage(
            title="Contact Us",
            slug="contact",
            intro_text="<p>Ready to transform your investment research and compliance workflow?</p>",
            contact_description="<p>Let's discuss how we can help align your portfolio with your values.</p>",
            email="contact@ec1c.com",
            show_contact_form=True,
        )
        homepage.add_child(instance=contact_page)
        contact_page.save_revision().publish()
        self.stdout.write(
            self.style.SUCCESS(f"Created ContactPage: {contact_page.title}"),
        )

        # Onboarding Page
        onboarding_page = OnboardingPage(
            title="Get Started",
            slug="start",
            intro_text="<p>Take your first step toward ethical investing or jump in with both feet. Let's find the perfect mix of strategies for your values and needs.</p>",
            form_description="<p>This comprehensive form helps us understand your investment goals, risk tolerance, and ethical priorities to create your personalized portfolio strategy.</p>",
            enable_form=True,
            thank_you_title="Thank You!",
            thank_you_message="<p>We've received your information and will be in touch within 1-2 business days to discuss your personalized investment strategy.</p>",
        )
        homepage.add_child(instance=onboarding_page)
        onboarding_page.save_revision().publish()
        self.stdout.write(
            self.style.SUCCESS(f"Created OnboardingPage: {onboarding_page.title}"),
        )

        self.stdout.write(self.style.SUCCESS("Successfully created all Wagtail pages!"))
