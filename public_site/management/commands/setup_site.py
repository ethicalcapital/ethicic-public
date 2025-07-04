"""
Management command to set up initial site data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from wagtail.models import Site, Page, Locale
from public_site.models import HomePage


class Command(BaseCommand):
    help = 'Set up initial site data including superuser and homepage'

    def add_arguments(self, parser):
        parser.add_argument(
            '--admin-password',
            type=str,
            default='dyzxuc-4muBzy-woqbam',
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
        if not User.objects.filter(username='srvo').exists():
            User.objects.create_superuser(
                'srvo', 
                'sloane@ethicic.com', 
                options['admin_password']
            )
            self.stdout.write(
                self.style.SUCCESS('Created superuser: srvo')
            )
        else:
            self.stdout.write('Superuser already exists')

        # Ensure default locale exists
        try:
            locale = Locale.objects.get_default()
        except Locale.DoesNotExist:
            # Create default locale
            Locale.objects.create(language_code='en-us')
            locale = Locale.objects.get_default()
            self.stdout.write('Created default locale')

        # Create homepage if it doesn't exist
        if not HomePage.objects.exists():
            try:
                # Get the root page - Wagtail should create this during migrations
                root = Page.objects.filter(depth=1).first()
                
                if not root:
                    # If no root exists, we need to run migrations first
                    self.stdout.write(
                        self.style.ERROR(
                            'No root page found. Please run migrations first: python manage.py migrate'
                        )
                    )
                    return
                
                # Create homepage
                home = HomePage(
                    title='Ethical Capital',
                    slug='home',
                    hero_title='Welcome to Ethical Capital',
                    hero_subtitle='Sustainable investing for a better future',
                    locale=locale
                )
                
                # Save without adding as child first to get an ID
                home.save()
                
                # Now add as child
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
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Failed to create homepage: {e}')
                )
                self.stdout.write('Site setup will continue without homepage')
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