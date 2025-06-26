"""
Management command to set up initial site data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from wagtail.models import Site, Page
from public_site.models import HomePage


class Command(BaseCommand):
    help = 'Set up initial site data including superuser and homepage'

    def add_arguments(self, parser):
        parser.add_argument(
            '--admin-password',
            type=str,
            default='ethicic2024!',
            help='Password for the admin user'
        )
        parser.add_argument(
            '--hostname',
            type=str,
            default='ethicic-public-svoo7.kinsta.app',
            help='Hostname for the site'
        )

    def handle(self, *args, **options):
        User = get_user_model()
        
        # Create superuser if it doesn't exist
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                'admin', 
                'admin@ethicic.com', 
                options['admin_password']
            )
            self.stdout.write(
                self.style.SUCCESS('Created superuser: admin')
            )
        else:
            self.stdout.write('Superuser already exists')

        # Create homepage if it doesn't exist
        if not HomePage.objects.exists():
            # Get the root page
            root = Page.objects.get(id=1)
            
            # Create homepage
            home = HomePage(
                title='Ethical Capital',
                slug='home',
                hero_title='Welcome to Ethical Capital',
                hero_subtitle='Sustainable investing for a better future'
            )
            root.add_child(instance=home)
            
            # Set up the site
            Site.objects.all().delete()  # Remove any existing sites
            Site.objects.create(
                hostname=options['hostname'],
                root_page=home,
                is_default_site=True
            )
            self.stdout.write(
                self.style.SUCCESS('Created homepage and site configuration')
            )
        else:
            self.stdout.write('Homepage already exists')
            
            # Update site hostname if needed
            site = Site.objects.first()
            if site and site.hostname != options['hostname']:
                site.hostname = options['hostname']
                site.save()
                self.stdout.write(
                    self.style.SUCCESS(f'Updated site hostname to {options["hostname"]}')
                )

        self.stdout.write(
            self.style.SUCCESS('Site setup complete!')
        )