from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from wagtail.models import Page, Site

from public_site.models import (
    AboutPage,
    BlogIndexPage,
    CompliancePage,
    ContactPage,
    FAQPage,
    HomePage,
    LegalPage,
    MediaPage,
    PricingPage,
)

User = get_user_model()


class Command(BaseCommand):
    help = "Set up initial Wagtail site structure with all required pages"

    def handle(self, *args, **options):
        try:
            # Get or create the site
            site = Site.objects.get(is_default_site=True)

            self.stdout.write(f"Setting up Wagtail site: {site.hostname}")

            # Check if HomePage already exists
            if HomePage.objects.filter(slug="home").exists():
                self.stdout.write(
                    self.style.WARNING("Wagtail site already set up. Skipping."),
                )
                return

            # Get the existing welcome page to replace it
            try:
                welcome_page = Page.objects.get(slug="home")
                parent_page = welcome_page.get_parent()
                welcome_page.delete()
            except Page.DoesNotExist:
                # If no welcome page, use root
                parent_page = site.root_page

            # Create HomePage as the site's home page
            home_page = HomePage(
                title="Garden Platform - Investment Intelligence & Compliance",
                slug="home",
                hero_title="Garden Platform",
                hero_subtitle="Advanced Investment Intelligence & Compliance Platform",
                hero_description="<p>Streamline your investment research, compliance monitoring, and portfolio management with our comprehensive platform designed for modern financial advisory practices.</p>",
                features_title="Platform Features",
                features_content="""
<h3>Investment Intelligence</h3>
<p>Real-time market monitoring, research workflow automation, and portfolio analytics.</p>

<h3>Compliance Management</h3>
<p>Automated compliance tracking, deadline monitoring, and regulatory reporting.</p>

<h3>Client Management</h3>
<p>Comprehensive CRM with client communications and document management.</p>

<h3>Media Monitoring</h3>
<p>Track news, social media, and market sentiment across all your holdings.</p>
                """,
                cta_title="Ready to Get Started?",
                cta_description="<p>Join leading financial advisors who trust Garden Platform for their investment intelligence needs.</p>",
                cta_button_text="Contact Us",
                cta_button_url="/contact/",
            )

            parent_page.add_child(instance=home_page)

            # Update the site to point to our new homepage
            site.root_page = home_page
            site.save()

            self.stdout.write(
                self.style.SUCCESS(f"Created HomePage: {home_page.title}"),
            )

            # Create About page
            about_page = AboutPage(
                title="About Us - Our Story",
                slug="about",
                intro_text="<p>Learn about our mission to democratize investment intelligence and compliance technology.</p>",
                body="""
<h2>Our Mission</h2>
<p>Garden Platform was built to solve the complexity challenge facing modern financial advisors. We believe that powerful investment intelligence and compliance tools shouldn't be limited to large institutions.</p>

<h2>Our Approach</h2>
<p>We combine cutting-edge technology with deep financial industry expertise to create tools that actually work for advisors in their daily practice.</p>

<h2>Why Garden?</h2>
<p>Named after the library classification system, our platform brings the same systematic organization and accessibility to financial intelligence that libraries brought to information.</p>
                """,
                team_title="Our Team",
                team_description="<p>A diverse team of technologists, financial professionals, and compliance experts working together to build the future of advisory technology.</p>",
                values_title="Our Values",
                values_content="""
<ul>
<li><strong>Transparency:</strong> Clear pricing, open communication, and honest relationships</li>
<li><strong>Quality:</strong> We build tools that advisors actually want to use every day</li>
<li><strong>Innovation:</strong> Constantly pushing the boundaries of what's possible in fintech</li>
<li><strong>Compliance:</strong> Security and regulatory adherence built into everything we do</li>
</ul>
                """,
            )
            home_page.add_child(instance=about_page)
            self.stdout.write(
                self.style.SUCCESS(f"Created AboutPage: {about_page.title}"),
            )

            # Create Pricing page
            pricing_page = PricingPage(
                title="Pricing & Fees",
                slug="pricing",
                intro_text="<p>Transparent pricing designed to scale with your practice.</p>",
                pricing_description="""
<h2>Platform Pricing</h2>
<p>Our pricing is designed to be simple, transparent, and scalable. Whether you're a solo advisor or a large RIA, we have a solution that fits your needs.</p>

<h3>Professional Plan</h3>
<ul>
<li>Complete investment intelligence platform</li>
<li>Compliance monitoring and reporting</li>
<li>Client management and CRM</li>
<li>Real-time media monitoring</li>
<li>API access and integrations</li>
</ul>

<h3>Enterprise Plan</h3>
<ul>
<li>Everything in Professional</li>
<li>Custom compliance workflows</li>
<li>Advanced analytics and reporting</li>
<li>Dedicated support team</li>
<li>Custom integrations</li>
</ul>
                """,
                enterprise_title="Enterprise Solutions",
                enterprise_description="<p>Large RIAs and institutions can benefit from our enterprise-grade solutions with custom compliance workflows, advanced analytics, and dedicated support.</p>",
                contact_cta="<p>Ready to discuss pricing for your practice? <a href='/contact/'>Contact our team</a> for a personalized quote and demo.</p>",
            )
            home_page.add_child(instance=pricing_page)
            self.stdout.write(
                self.style.SUCCESS(f"Created PricingPage: {pricing_page.title}"),
            )

            # Create Contact page
            contact_page = ContactPage(
                title="Contact Us - Get Started",
                slug="contact",
                intro_text="<p>Ready to transform your investment research and compliance workflow?</p>",
                contact_description="""
<h2>Get Started Today</h2>
<p>Our team is ready to help you streamline your practice with the Garden Platform. Whether you're looking for a demo, have questions about pricing, or want to discuss custom solutions, we're here to help.</p>

<h3>What to Expect</h3>
<ul>
<li>Personalized demo of the platform</li>
<li>Discussion of your specific needs</li>
<li>Custom pricing and implementation plan</li>
<li>Ongoing support and training</li>
</ul>
                """,
                email="contact@ec1c.com",
                phone="",
                address="",
                show_contact_form=True,
            )
            home_page.add_child(instance=contact_page)
            self.stdout.write(
                self.style.SUCCESS(f"Created ContactPage: {contact_page.title}"),
            )

            # Create Blog index page
            blog_index = BlogIndexPage(
                title="Blog - Insights & Updates",
                slug="blog",
                intro="<p>Insights, updates, and thought leadership on investment intelligence and compliance.</p>",
            )
            home_page.add_child(instance=blog_index)
            self.stdout.write(
                self.style.SUCCESS(f"Created BlogIndexPage: {blog_index.title}"),
            )

            # Create FAQ page
            faq_page = FAQPage(
                title="FAQ & Support",
                slug="faq",
                intro_text="<p>Frequently asked questions about the Garden Platform.</p>",
            )
            home_page.add_child(instance=faq_page)
            self.stdout.write(self.style.SUCCESS(f"Created FAQPage: {faq_page.title}"))

            # Create Media/Press page
            media_page = MediaPage(
                title="Media & Press",
                slug="media",
                intro_text="<p>Media coverage, press releases, and company news.</p>",
                press_kit_title="Press Kit",
                press_kit_description="<p>Download our press kit for logos, company information, and executive bios.</p>",
            )
            home_page.add_child(instance=media_page)
            self.stdout.write(
                self.style.SUCCESS(f"Created MediaPage: {media_page.title}"),
            )

            # Create Legal pages
            privacy_page = LegalPage(
                title="Privacy Policy",
                slug="privacy",
                intro_text="<p>Our commitment to protecting your privacy and data.</p>",
                content="""
<h2>Privacy Policy</h2>
<p>At Garden Platform, we take your privacy seriously. This policy outlines how we collect, use, and protect your information.</p>

<h3>Information We Collect</h3>
<p>We collect information you provide directly to us, such as when you create an account, use our services, or contact us for support.</p>

<h3>How We Use Your Information</h3>
<p>We use the information we collect to provide, maintain, and improve our services, process transactions, and communicate with you.</p>

<h3>Information Sharing</h3>
<p>We do not sell, trade, or otherwise transfer your personal information to third parties without your consent, except as described in this policy.</p>

<h3>Data Security</h3>
<p>We implement appropriate security measures to protect your personal information against unauthorized access, alteration, disclosure, or destruction.</p>
                """,
            )
            home_page.add_child(instance=privacy_page)
            self.stdout.write(
                self.style.SUCCESS(f"Created Privacy Policy: {privacy_page.title}"),
            )

            terms_page = LegalPage(
                title="Terms of Service",
                slug="terms",
                intro_text="<p>Terms and conditions for using the Garden Platform.</p>",
                content="""
<h2>Terms of Service</h2>
<p>These terms govern your use of the Garden Platform and any related services.</p>

<h3>Acceptance of Terms</h3>
<p>By accessing and using our platform, you accept and agree to be bound by these terms.</p>

<h3>Use of Service</h3>
<p>You may use our service for lawful purposes only. You agree not to use the service in any way that violates applicable laws or regulations.</p>

<h3>Account Responsibility</h3>
<p>You are responsible for safeguarding your account credentials and all activities that occur under your account.</p>

<h3>Limitation of Liability</h3>
<p>To the fullest extent permitted by law, Garden Platform shall not be liable for any indirect, incidental, special, consequential, or punitive damages.</p>
                """,
            )
            home_page.add_child(instance=terms_page)
            self.stdout.write(
                self.style.SUCCESS(f"Created Terms of Service: {terms_page.title}"),
            )

            # Create Form ADV page
            form_adv_page = CompliancePage(
                title="Form ADV",
                slug="form-adv",
                intro_text="<p>Our Form ADV disclosure document as required by the SEC.</p>",
                content="""
<h2>Form ADV - Investment Adviser Registration</h2>
<p>This Form ADV gives you information about EC1C and our advisory services.</p>

<h3>Advisory Business</h3>
<p>EC1C provides investment advisory services through our Garden Platform technology.</p>

<h3>Fees and Compensation</h3>
<p>Our fees are based on a percentage of assets under management or fixed subscription fees for platform access.</p>

<h3>Conflicts of Interest</h3>
<p>We maintain policies and procedures to identify and address potential conflicts of interest.</p>

<h3>Additional Information</h3>
<p>For the complete Form ADV, please contact us directly or download the full document from our compliance section.</p>
                """,
                document_type="form_adv",
                version="2024.1",
            )
            home_page.add_child(instance=form_adv_page)
            self.stdout.write(
                self.style.SUCCESS(f"Created Form ADV: {form_adv_page.title}"),
            )

            # Create Exclusion Lists page
            exclusions_page = CompliancePage(
                title="Exclusion Lists",
                slug="exclusions",
                intro_text="<p>Investment exclusion criteria and screening methodologies.</p>",
                content="""
<h2>Investment Exclusion Lists</h2>
<p>Our platform includes comprehensive screening for various exclusion criteria to support ESG and ethical investing requirements.</p>

<h3>ESG Exclusions</h3>
<ul>
<li>Tobacco companies</li>
<li>Weapons manufacturers</li>
<li>Fossil fuel companies (optional)</li>
<li>Companies with poor labor practices</li>
</ul>

<h3>Regulatory Exclusions</h3>
<ul>
<li>Sanctioned entities</li>
<li>Companies under regulatory investigation</li>
<li>Fraudulent or delinquent issuers</li>
</ul>

<h3>Custom Exclusions</h3>
<p>Clients can create custom exclusion lists based on their specific values and requirements.</p>

<h3>Screening Process</h3>
<p>Our automated screening process updates daily to ensure compliance with all applicable exclusion criteria.</p>
                """,
                document_type="exclusion_list",
                version="2024.1",
            )
            home_page.add_child(instance=exclusions_page)
            self.stdout.write(
                self.style.SUCCESS(f"Created Exclusion Lists: {exclusions_page.title}"),
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f"\n✅ Wagtail site setup complete!\n"
                    f"🏠 Homepage: {home_page.get_full_url()}\n"
                    f"🛠️  CMS Admin: /cms-admin/\n"
                    f"📱 Platform: /platform/\n"
                    f"📋 Created {Page.objects.filter(depth__gt=1).count()} pages total",
                ),
            )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error setting up Wagtail site: {e!s}"))
            raise
