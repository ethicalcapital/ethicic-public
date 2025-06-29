"""
Management command to set up the homepage for production deployment.
"""
from django.core.management.base import BaseCommand
from wagtail.models import Site, Page
from public_site.models import HomePage


class Command(BaseCommand):
    help = 'Set up the homepage and site configuration'

    def handle(self, *args, **options):
        """Set up the homepage and site configuration."""
        
        # Get root page
        root = Page.get_first_root_node()
        self.stdout.write(f"Root page: {root.title} (ID: {root.id})")
        
        # Delete any existing sites
        sites_deleted = Site.objects.all().delete()
        self.stdout.write(f"Cleared {sites_deleted[0]} existing sites")
        
        # Check if HomePage already exists
        existing_homepage = HomePage.objects.first()
        
        if existing_homepage:
            homepage = existing_homepage
            self.stdout.write(f"Using existing HomePage: {homepage.title}")
        else:
            # Create new HomePage with all required fields
            homepage = HomePage(
                title='Ethical Capital Investment Collaborative',
                slug='homepage',
                hero_tagline='Ethical Investing',
                hero_title='Where Ethics Drive Investment Excellence',
                hero_subtitle='<p>Professional investment management guided by your values.</p>',
                excluded_percentage='57%',
                since_year='2020',
                philosophy_title='Values-Based Investment Philosophy',
                philosophy_content='<p>We believe that ethical investing delivers superior long-term returns while creating positive impact in the world.</p>',
                philosophy_highlight='Every investment decision reflects your values and drives positive change.',
                cta_title='Ready to Start Your Ethical Investment Journey?',
                cta_description='<p>Schedule a consultation to learn how we can help you invest in line with your values.</p>',
                client_availability_text='Currently accepting new clients',
                disclaimer_text='<p>Investment advisory services provided by Ethical Capital Investment Collaborative.</p>',
                # Process principles content
                principles_intro='<p>Our investment approach is guided by clear principles that ensure every decision aligns with your values while pursuing superior returns.</p>',
                process_principle_1_title='Fiduciary Standard',
                process_principle_1_content='We operate under the highest fiduciary standard, putting your interests first in every decision.',
                process_principle_2_title='Transparent Process',
                process_principle_2_content='Complete transparency in our investment process, from screening to portfolio construction.',
                process_principle_3_title='Continuous Research',
                process_principle_3_content='Ongoing research and analysis to identify opportunities that align with your values.',
                practice_principle_1_title='Values Integration',
                practice_principle_1_content='Deep integration of ethical criteria into every investment decision without compromising returns.',
                practice_principle_2_title='Active Engagement',
                practice_principle_2_content='Active ownership and engagement with companies to drive positive change.',
                practice_principle_3_title='Impact Measurement',
                practice_principle_3_content='Rigorous measurement and reporting of both financial and impact outcomes.',
                # Strategy content
                strategies_intro='<p>We offer three distinct strategies designed to meet different client needs while maintaining our commitment to ethical investing.</p>',
                # Process steps
                process_step_1_title='Discovery & Values Assessment',
                process_step_1_content='We begin by understanding your financial goals, values, and specific ethical preferences through comprehensive discovery.',
                process_step_2_title='Ethical Screening & Research',
                process_step_2_content='Our rigorous research process screens investments against your values while identifying superior risk-adjusted opportunities.',
                process_step_3_title='Portfolio Construction',
                process_step_3_content='We construct concentrated, high-conviction portfolios that reflect your values without compromising on diversification.',
                process_step_4_title='Ongoing Management & Reporting',
                process_step_4_content='Continuous monitoring, rebalancing, and transparent reporting on both financial performance and impact outcomes.',
                # Who we serve
                serve_individual_title='Individual & Family Investors',
                serve_individual_content='Comprehensive investment management for individuals and families who want their investments to reflect their values.',
                serve_advisor_title='Registered Investment Advisors',
                serve_advisor_content='Partnership opportunities for RIAs who want to offer ethical investing solutions to their clients.',
                serve_institution_title='Institutions & Nonprofits',
                serve_institution_content='Custom ethical investment solutions for endowments, foundations, and other institutional investors.'
            )
            
            try:
                # Add to root as child
                root.add_child(instance=homepage)
                homepage.save_revision().publish()
                self.stdout.write(self.style.SUCCESS(f"Created new HomePage: {homepage.title}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error creating homepage: {e}"))
                return
        
        # Create site pointing to homepage
        try:
            site = Site.objects.create(
                hostname='*',  # Accept any hostname
                port=80,
                root_page=homepage,
                is_default_site=True,
                site_name='Ethical Capital'
            )
            
            self.stdout.write(self.style.SUCCESS(f"Site created: {site.hostname}:{site.port} -> {homepage.title}"))
            self.stdout.write(f"Homepage URL: {homepage.url}")
            self.stdout.write(f"Homepage live: {homepage.live}")
            self.stdout.write(f"Homepage content type: {homepage.content_type}")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error creating site: {e}"))