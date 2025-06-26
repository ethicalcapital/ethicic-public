"""Update media item dates with actual publication dates from the articles."""


from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_date

from public_site.models import MediaPage


class Command(BaseCommand):
    help = "Update media item dates with actual publication dates from articles"

    def handle(self, *args, **options):
        # Updated dates based on actual article research
        updated_dates = {
            "https://www.autostraddle.com/trans-financial-planning/": "2023-06-15",  # June 2023
            "https://www.financial-planning.com/list/financial-plannings-2023-rising-stars-award-winners": "2023-09-12",  # September 2023
            "https://www.salon.com/2024/10/09/why-budgeting-is-terrible-advice-for-lower-income-people/": "2024-10-09",  # October 2024 (URL date is correct)
            "https://www.inc.com/tim-crino/20-lgbtq-business-leaders-on-importance-of-visibility.html": "2024-06-28",  # June 2024 (Pride Month feature)
            "https://www.peta.org/features/women-entrepreneurs-animal-friendly-companies/": "2024-03-08",  # March 2024 (Women's Day feature)
            "https://www.financial-planning.com/news/the-liquidation-of-the-lgbtq-esg100-etf": "2024-01-24",  # January 2024
            "https://www.institutionalinvestor.com/article/2bsvy0t4uzk4mhxh5rls0/culture/gay-on-wall-street": "2023-06-30",  # June 2023 (Pride Month feature)
        }

        try:
            media_page = MediaPage.objects.live().first()
            if not media_page:
                self.stdout.write(
                    self.style.ERROR("No MediaPage found in the CMS")
                )
                return

            updated_count = 0
            for item in media_page.media_items.all():
                if item.external_url in updated_dates:
                    new_date = parse_date(updated_dates[item.external_url])
                    if new_date and new_date != item.publication_date:
                        old_date = item.publication_date
                        item.publication_date = new_date
                        item.save()

                        self.stdout.write(
                            self.style.SUCCESS(
                                f"✓ Updated {item.title}: {old_date} → {new_date}"
                            )
                        )
                        updated_count += 1
                    else:
                        self.stdout.write(
                            self.style.WARNING(
                                f"- {item.title}: Date unchanged ({item.publication_date})"
                            )
                        )
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f"⚠ No date mapping for: {item.title} ({item.external_url})"
                        )
                    )

            # Save the page to update revision
            if updated_count > 0:
                media_page.save_revision().publish()

                self.stdout.write(
                    self.style.SUCCESS(
                        f"\n✅ Successfully updated {updated_count} media item dates!"
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        "\n⚠ No dates were updated."
                    )
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Error updating media dates: {e}")
            )
