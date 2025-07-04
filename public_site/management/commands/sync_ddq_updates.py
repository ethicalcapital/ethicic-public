"""
Management command to re-sync PRI DDQ content when the main DDQ page is updated.
"""

from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Re-sync PRI DDQ content to FAQ after updates"

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force update all articles even if they exist",
        )

    def handle(self, *args, **options):
        """Re-sync PRI DDQ content."""

        self.stdout.write(self.style.SUCCESS("🔄 Re-syncing PRI DDQ content to FAQ..."))

        # Call the sync command
        call_command("sync_pri_ddq_to_faq")

        self.stdout.write(
            self.style.SUCCESS("✅ PRI DDQ content successfully synced to FAQ!")
        )
        self.stdout.write(
            self.style.SUCCESS("📖 Visit /faq/ to see the updated FAQ entries.")
        )
        self.stdout.write(
            self.style.SUCCESS(
                "🔗 PRI DDQ page at /pri-ddq/ now links to FAQ for easy access."
            )
        )
