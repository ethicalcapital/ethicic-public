"""
Management command to create the Accessibility Statement page in Wagtail.
"""

from django.core.management.base import BaseCommand

from public_site.models import LegalPage


class Command(BaseCommand):
    help = "Create the Accessibility Statement page"

    def handle(self, *args, **options):
        # Get the root page (usually the home page)
        try:
            from public_site.models import HomePage
            home_page = HomePage.objects.first()
            if not home_page:
                self.stdout.write(
                    self.style.ERROR("No HomePage found. Please create a HomePage first.")
                )
                return
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Error finding HomePage: {e}")
            )
            return

        # Check if accessibility statement already exists
        existing_page = LegalPage.objects.filter(title="Accessibility Statement").first()
        if existing_page:
            self.stdout.write(
                self.style.WARNING(f"Accessibility Statement page already exists at: {existing_page.get_url()}")
            )
            return

        # Create the accessibility statement page
        accessibility_page = LegalPage(
            title="Accessibility Statement",
            slug="accessibility",
            intro_text="<p>Our commitment to ensuring digital accessibility for people with disabilities.</p>",
            content=self._get_accessibility_content(),
            show_in_menus=True,
        )

        # Add as child of home page
        try:
            home_page.add_child(instance=accessibility_page)
            accessibility_page.save_revision().publish()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully created Accessibility Statement page at: {accessibility_page.get_url()}"
                )
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Error creating accessibility page: {e}")
            )

    def _get_accessibility_content(self):
        """Return the accessibility statement content."""
        return """
        <h2>Our Commitment to Accessibility</h2>
        <p>Ethical Capital is committed to ensuring digital accessibility for people with disabilities. We are continually improving the user experience for everyone and applying the relevant accessibility standards to ensure we provide equal access to all of our users.</p>

        <h2>Accessibility Standards</h2>
        <p>We aim to conform to the Web Content Accessibility Guidelines (WCAG) 2.1 Level AA standards. These guidelines explain how to make web content more accessible for people with disabilities, and user-friendly for everyone.</p>

        <h2>Current Accessibility Features</h2>
        <ul>
            <li><strong>Keyboard Navigation:</strong> All interactive elements can be accessed using keyboard navigation</li>
            <li><strong>Screen Reader Support:</strong> Proper semantic HTML and ARIA labels for assistive technologies</li>
            <li><strong>Color Contrast:</strong> Text and background colors meet WCAG AA contrast requirements</li>
            <li><strong>Responsive Design:</strong> Content adapts to different screen sizes and zoom levels up to 200%</li>
            <li><strong>Alternative Text:</strong> Descriptive alt text for all meaningful images</li>
            <li><strong>Focus Indicators:</strong> Clear visual focus indicators for keyboard users</li>
            <li><strong>Skip Navigation:</strong> Skip links allow users to bypass repetitive navigation</li>
            <li><strong>Form Labels:</strong> All form inputs have associated labels for screen readers</li>
            <li><strong>Heading Structure:</strong> Proper heading hierarchy for logical content structure</li>
            <li><strong>Error Messages:</strong> Clear, descriptive error messages for form validation</li>
        </ul>

        <h2>Accessibility Testing</h2>
        <p>We regularly test our website using:</p>
        <ul>
            <li>Automated accessibility testing tools</li>
            <li>Manual keyboard navigation testing</li>
            <li>Screen reader testing with NVDA, JAWS, and VoiceOver</li>
            <li>Color contrast analysis tools</li>
            <li>Mobile accessibility testing</li>
        </ul>

        <h2>Known Limitations</h2>
        <p>We are aware of some accessibility limitations and are actively working to address them:</p>
        <ul>
            <li>Some complex financial charts may have limited screen reader accessibility - we provide alternative data tables where possible</li>
            <li>Third-party embedded content may not fully meet our accessibility standards - we work with vendors to improve this</li>
            <li>Some legacy content is being updated to meet current accessibility standards</li>
        </ul>

        <h2>Ongoing Improvements</h2>
        <p>We are committed to continual improvement and regularly:</p>
        <ul>
            <li>Conduct accessibility audits of new features</li>
            <li>Train our development team on accessibility best practices</li>
            <li>Update our design system to include accessibility requirements</li>
            <li>Review and test content with assistive technologies</li>
            <li>Incorporate user feedback to improve accessibility</li>
        </ul>

        <h2>Feedback and Contact Information</h2>
        <p>We welcome your feedback on the accessibility of our website. If you encounter any accessibility barriers or have suggestions for improvement, please contact us:</p>
        
        <p><strong>Email:</strong> <a href="mailto:hello@ethicic.com">hello@ethicic.com</a></p>
        <p><strong>Phone:</strong> <a href="tel:+1-801-123-4567">+1 (801) 123-4567</a></p>

        <p>We aim to respond to accessibility feedback within 2 business days and will work with you to provide the information or functionality you need in an accessible format.</p>

        <h2>Alternative Formats</h2>
        <p>If you need this accessibility statement in an alternative format, please contact us using the information above. We can provide this information in:</p>
        <ul>
            <li>Large print</li>
            <li>High contrast format</li>
            <li>Plain text email</li>
            <li>Audio format</li>
        </ul>

        <h2>Third-Party Content</h2>
        <p>Some content on our website is provided by third parties. We work with our partners to ensure their content meets accessibility standards, but we may not have full control over their accessibility features. If you encounter issues with third-party content, please contact us and we will work to resolve the issue.</p>

        <div style="margin-top: 2rem; padding: 1rem; background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 4px;">
            <p><strong>Last Updated:</strong> December 2024</p>
            <p><strong>Next Review:</strong> June 2025</p>
            <p><em>This statement will be reviewed and updated every six months to reflect our ongoing accessibility improvements.</em></p>
        </div>
        """