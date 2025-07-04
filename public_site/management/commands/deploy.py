"""
Management command for deployment setup.
This should be run after deployment to set up the database and static files.
"""

from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Run deployment setup: migrations, collectstatic, and site setup"

    def handle(self, *args, **options):
        self.stdout.write("🚀 Starting deployment setup...")

        # 1. Run migrations
        self.stdout.write("📊 Running database migrations...")
        try:
            call_command("migrate", verbosity=1, interactive=False)
            self.stdout.write(self.style.SUCCESS("✅ Database migrations completed"))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"⚠️  Migration warnings: {e}"))

        # 2. Collect static files
        self.stdout.write("📁 Collecting static files...")
        try:
            call_command("collectstatic", verbosity=1, interactive=False, clear=True)
            self.stdout.write(self.style.SUCCESS("✅ Static files collected"))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"⚠️  Static collection warnings: {e}"))

        # 3. Set up homepage
        self.stdout.write("🏠 Setting up site structure...")
        try:
            call_command("setup_homepage")
            self.stdout.write(self.style.SUCCESS("✅ Site setup completed"))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"⚠️  Site setup warnings: {e}"))

        self.stdout.write(self.style.SUCCESS("🎉 Deployment setup completed!"))
