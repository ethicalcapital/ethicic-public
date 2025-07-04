from datetime import date

from django.core.management.base import BaseCommand
from wagtail.models import Page

from public_site.models import MediaItem, MediaPage


class Command(BaseCommand):
    help = "Create Media page with sample content"

    def handle(self, *args, **options):
        # Get the root page
        root_page = Page.objects.filter(depth=2).first()
        if not root_page:
            self.stdout.write(self.style.ERROR("No root page found"))
            return

        # Check if media page already exists
        media_page = MediaPage.objects.filter(slug="media").first()

        if media_page:
            self.stdout.write(self.style.WARNING(f"Media page already exists at: {media_page.url}"))
            return

        # Create media page
        media_page = MediaPage(
            title="Media & Press",
            slug="media",
            intro_text="<p>Media coverage, press releases, and news about Ethical Capital's mission to transform investing through ethical screening and sustainable practices.</p>",
            press_kit_title="Press Kit & Resources",
            press_kit_description="<p>For journalists and media professionals, we offer comprehensive resources about Ethical Capital, including our mission, investment philosophy, and impact data. Contact us for high-resolution images, logos, and additional materials.</p>",
        )

        root_page.add_child(instance=media_page)
        media_page.save_revision().publish()

        self.stdout.write(self.style.SUCCESS(f"Created Media page: {media_page.title}"))

        # Add sample media items
        sample_items = [
            {
                "title": "Ethical Capital: Pioneering Sustainable Investment Strategies",
                "description": "<p>An in-depth look at how Ethical Capital is reshaping the investment landscape by excluding companies involved in preventable harms while delivering competitive returns.</p>",
                "publication": "Sustainable Finance Weekly",
                "publication_date": date(2024, 11, 15),
                "external_url": "https://example.com/ethical-capital-profile",
                "featured": True,
            },
            {
                "title": "The Rise of Values-Based Investing: A Conversation with Sloane Ortel",
                "description": "<p>Ethical Capital's Chief Investment Officer discusses the growing demand for investment strategies that align with personal values and the firm's unique approach to ethical screening.</p>",
                "publication": "Investment Advisor Magazine",
                "publication_date": date(2024, 10, 28),
                "external_url": "https://example.com/sloane-ortel-interview",
                "featured": False,
            },
            {
                "title": "Study: Ethical Investing Can Match or Beat Traditional Returns",
                "description": "<p>New research featuring Ethical Capital's performance data challenges the myth that ethical constraints necessarily lead to lower investment returns.</p>",
                "publication": "Financial Times",
                "publication_date": date(2024, 9, 12),
                "external_url": "https://example.com/ethical-investing-study",
                "featured": False,
            },
            {
                "title": "How One Firm Excludes 57% of the S&P 500—and Still Outperforms",
                "description": "<p>A deep dive into Ethical Capital's screening methodology and how their concentrated portfolio approach has delivered results for conscious investors.</p>",
                "publication": "Bloomberg Markets",
                "publication_date": date(2024, 8, 5),
                "external_url": "https://example.com/ethical-capital-methodology",
                "featured": True,
            },
            {
                "title": "The Future of Fiduciary Duty: Ethics as a Core Investment Principle",
                "description": "<p>Industry leaders, including Ethical Capital, are redefining what it means to act in clients' best interests by incorporating ethical considerations into fiduciary responsibilities.</p>",
                "publication": "Institutional Investor",
                "publication_date": date(2024, 7, 22),
                "external_url": "https://example.com/fiduciary-ethics",
                "featured": False,
            },
            {
                "title": "Ethical Capital Launches Open-Source Investment Screening Framework",
                "description": "<p>In a move toward greater transparency, Ethical Capital has made its complete screening methodology available on GitHub, inviting collaboration from the investment community.</p>",
                "publication": "TechCrunch",
                "publication_date": date(2024, 6, 10),
                "external_url": "https://github.com/ethicalcapital/sage",
                "featured": True,
            },
        ]

        for item_data in sample_items:
            MediaItem.objects.create(page=media_page, **item_data)

        self.stdout.write(self.style.SUCCESS(f"Added {len(sample_items)} media items"))
        self.stdout.write(self.style.SUCCESS(f"Media page available at: {media_page.url}"))
