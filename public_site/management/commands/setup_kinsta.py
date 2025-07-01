from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth import get_user_model
from wagtail.models import Site, Page
from public_site.models import HomePage

User = get_user_model()

class Command(BaseCommand):
    help = 'Set up initial data for Kinsta deployment'

    def handle(self, *args, **options):
        self.stdout.write('Setting up Kinsta deployment...')
        
        with transaction.atomic():
            # Create superuser if none exists
            if not User.objects.filter(is_superuser=True).exists():
                self.stdout.write('Creating superuser...')
                User.objects.create_superuser(
                    username='admin',
                    email='admin@ethicic.com',
                    password='ChangeThisPassword123!'
                )
                self.stdout.write(self.style.SUCCESS('✅ Superuser created (username: admin)'))
                self.stdout.write(self.style.WARNING('⚠️  CHANGE THE PASSWORD IMMEDIATELY!'))
            
            # Ensure we have a root page
            if not Page.objects.filter(pk=1).exists():
                self.stdout.write('Creating root page...')
                root_page = Page.objects.create(
                    title="Root",
                    slug="root",
                    content_type_id=1,
                    path="0001",
                    depth=1,
                    numchild=0,
                    url_path="/",
                )
                root_page.save()
                self.stdout.write(self.style.SUCCESS('✅ Root page created'))
            else:
                root_page = Page.objects.get(pk=1)
            
            # Create HomePage if it doesn't exist
            if not HomePage.objects.exists():
                self.stdout.write('Creating HomePage...')
                home = HomePage(
                    title="Ethical Capital Investment Collaborative",
                    slug="home",
                    live=True,
                )
                root_page.add_child(instance=home)
                home.save_revision().publish()
                self.stdout.write(self.style.SUCCESS('✅ HomePage created'))
            else:
                home = HomePage.objects.first()
            
            # Set up the site
            if not Site.objects.exists():
                self.stdout.write('Creating Site...')
                Site.objects.create(
                    hostname='ethical-capital-public-frezv.kinsta.app',
                    port=443,
                    is_default_site=True,
                    root_page=home,
                )
                self.stdout.write(self.style.SUCCESS('✅ Site created'))
            else:
                # Update existing site
                site = Site.objects.first()
                site.root_page = home
                site.save()
                self.stdout.write(self.style.SUCCESS('✅ Site updated'))
        
        self.stdout.write(self.style.SUCCESS('\n✅ Kinsta setup complete!'))