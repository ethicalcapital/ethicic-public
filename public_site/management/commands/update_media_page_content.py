"""Update media page content with more appropriate text."""

from django.core.management.base import BaseCommand

from public_site.models import MediaPage


class Command(BaseCommand):
    help = "Update media page content with EC1C-specific text"

    def handle(self, *args, **options):
        try:
            media_page = MediaPage.objects.live().first()
            if not media_page:
                self.stdout.write(self.style.ERROR("No MediaPage found in the CMS"))
                return

            # Update intro text
            media_page.intro_text = """
            <p>Ethical Capital Investment Collaborative has been featured in leading financial publications
            and media outlets for our innovative approach to values-aligned investing, LGBTQ+ inclusive
            financial planning, and commitment to democratizing investment intelligence.</p>
            """

            # Update press kit description
            media_page.press_kit_title = "Press Resources"
            media_page.press_kit_description = """
            <p><strong>About EC1C:</strong> Ethical Capital Investment Collaborative (EC1C) is a values-driven
            investment management firm specializing in BDS-compliant, fossil fuel free, and socially responsible
            portfolio construction. We serve progressive individuals, families, and institutions seeking to align
            their investments with their values.</p>

            <p><strong>Areas of Expertise:</strong></p>
            <ul>
                <li>BDS-compliant investment strategies</li>
                <li>LGBTQ+ inclusive financial planning</li>
                <li>Fossil fuel free portfolio construction</li>
                <li>Impact measurement and ESG integration</li>
                <li>Accessible investment management for underserved communities</li>
            </ul>

            <p><strong>Media Contact:</strong> For press inquiries, expert commentary, or interview requests,
            please contact our media team through the form below.</p>
            """

            # Save and publish
            media_page.save_revision().publish()

            self.stdout.write(
                self.style.SUCCESS("✅ Successfully updated media page content!")
            )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error updating media page: {e}"))
