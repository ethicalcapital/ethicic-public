"""Populate media page with real media mentions."""

from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_date

from public_site.models import MediaItem, MediaPage


class Command(BaseCommand):
    help = "Populate media page with real media mentions of EC1C"

    def handle(self, *args, **options):
        # Media mentions data
        media_mentions = [
            {
                "title": "Trans Financial Planning",
                "description": "In-depth coverage of financial planning for the transgender community, featuring insights from EC1C on creating inclusive investment strategies.",
                "publication": "Autostraddle",
                "publication_date": "2023-01-15",
                "external_url": "https://www.autostraddle.com/trans-financial-planning/",
            },
            {
                "title": "Financial Planning's 2023 Rising Stars Award Winners",
                "description": "EC1C recognized among Financial Planning's Rising Stars for innovative approaches to ethical investment management and client service.",
                "publication": "Financial Planning",
                "publication_date": "2023-06-01",
                "external_url": "https://www.financial-planning.com/list/financial-plannings-2023-rising-stars-award-winners",
            },
            {
                "title": "Why Budgeting is Terrible Advice for Lower-Income People",
                "description": "Featured commentary on systemic financial inequality and the need for accessible investment strategies beyond traditional budgeting advice.",
                "publication": "Salon",
                "publication_date": "2024-10-09",
                "external_url": "https://www.salon.com/2024/10/09/why-budgeting-is-terrible-advice-for-lower-income-people/",
            },
            {
                "title": "20 LGBTQ Business Leaders on Importance of Visibility",
                "description": "EC1C leadership featured among prominent LGBTQ business leaders discussing the importance of visibility in financial services.",
                "publication": "Inc.",
                "publication_date": "2023-08-15",
                "external_url": "https://www.inc.com/tim-crino/20-lgbtq-business-leaders-on-importance-of-visibility.html",
            },
            {
                "title": "Women Entrepreneurs Behind Animal-Friendly Companies",
                "description": "PETA highlights EC1C's commitment to cruelty-free investing and ethical portfolio construction.",
                "publication": "PETA",
                "publication_date": "2023-03-20",
                "external_url": "https://www.peta.org/features/women-entrepreneurs-animal-friendly-companies/",
            },
            {
                "title": "The Liquidation of the LGBTQ+ ESG100 ETF",
                "description": "Expert analysis on the challenges facing ESG investing and EC1C's approach to authentic values-aligned investment management.",
                "publication": "Financial Planning",
                "publication_date": "2023-11-15",
                "external_url": "https://www.financial-planning.com/news/the-liquidation-of-the-lgbtq-esg100-etf",
            },
            {
                "title": "Gay on Wall Street",
                "description": "Institutional Investor profiles EC1C's work in creating inclusive investment strategies and challenging traditional Wall Street culture.",
                "publication": "Institutional Investor",
                "publication_date": "2023-05-10",
                "external_url": "https://www.institutionalinvestor.com/article/2bsvy0t4uzk4mhxh5rls0/culture/gay-on-wall-street",
            },
        ]

        # Find the media page
        try:
            media_page = MediaPage.objects.live().first()
            if not media_page:
                self.stdout.write(
                    self.style.ERROR("No MediaPage found in the CMS")
                )
                return
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Error finding MediaPage: {e}")
            )
            return

        # Clear existing media items
        media_page.media_items.all().delete()
        self.stdout.write(
            self.style.WARNING("Cleared existing media items")
        )

        # Add new media items
        for idx, item_data in enumerate(media_mentions):
            try:
                # Parse the date if provided
                pub_date = None
                if item_data.get("publication_date"):
                    pub_date = parse_date(item_data["publication_date"])

                # Create the media item
                media_item = MediaItem(
                    page=media_page,
                    title=item_data["title"],
                    description=f"<p>{item_data['description']}</p>",
                    publication=item_data["publication"],
                    publication_date=pub_date,
                    external_url=item_data["external_url"],
                    sort_order=idx,
                )
                media_item.save()

                self.stdout.write(
                    self.style.SUCCESS(
                        f"✓ Added: {item_data['title']} ({item_data['publication']})"
                    )
                )

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f"✗ Failed to add {item_data['title']}: {e}"
                    )
                )

        # Save the page to update revision
        media_page.save_revision().publish()

        self.stdout.write(
            self.style.SUCCESS(
                f"\n✅ Successfully populated {len(media_mentions)} media items!"
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                "Visit /media/ to see the updates"
            )
        )
