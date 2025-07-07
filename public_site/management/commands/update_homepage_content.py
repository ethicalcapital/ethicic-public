"""
Management command to update HomePage content to match the hardcoded values
This ensures CMS content matches what was in homepage_view.py
"""

from django.core.management.base import BaseCommand

from public_site.models import HomePage


class Command(BaseCommand):
    help = "Update HomePage content in CMS to match hardcoded values (without <strong> tags)"

    def handle(self, *args, **options):
        try:
            # Get the HomePage instance
            homepage = HomePage.objects.first()

            if not homepage:
                self.stdout.write(self.style.ERROR("No HomePage found in database"))
                return

            # Update process step content without <strong> tags
            homepage.process_step_1_content = (
                "We begin where others end. Our multi-factor screening excludes companies "
                "involved in fossil fuels, weapons systems, factory farming, tobacco, gambling, "
                "and those failing our governance standards. This isn't performative—it's "
                "foundational. We cast a wide net, continuously monitoring corporate behavior, "
                "partnerships, and evolving business models. When companies disappoint, we divest. "
                "When emerging risks appear, we investigate."
            )

            homepage.process_step_2_content = (
                "Ethics alone don't make an investment. From the companies that pass our screens, "
                "we identify those with durable competitive advantages. We evaluate business quality "
                "through multiple lenses: market position, financial strength, management integrity, "
                "and growth sustainability. This isn't about finding perfect companies—it's about "
                "understanding which imperfect companies are worth owning and at what price."
            )

            homepage.process_step_3_content = (
                "From thousands screened to hundreds researched to 15-25 owned. We size positions "
                "based on conviction level, business quality, and risk contribution. Concentration "
                "enforces discipline—every holding must earn its place. The result: portfolios where "
                "you understand what you own, why you own it, and how each position contributes to "
                "your long-term objectives."
            )

            homepage.process_step_4_content = (
                "Investing isn't static. We monitor holdings daily, reassess theses quarterly, and "
                "evolve our process continuously. When facts change, we act. When clients raise "
                "concerns, we investigate. When new risks emerge, we adapt. This isn't passive "
                "indexing—it's active stewardship of capital aligned with values that matter."
            )

            # Save the changes
            homepage.save_revision().publish()

            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully updated HomePage "{homepage.title}" content without <strong> tags'
                )
            )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error updating HomePage: {str(e)}"))
