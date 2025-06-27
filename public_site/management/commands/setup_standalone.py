"""
Setup standalone mode with SQLite database
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from wagtail.models import Site, Page
from public_site.models import HomePage


class Command(BaseCommand):
    help = 'Setup standalone SQLite database with basic content'

    def handle(self, *args, **options):
        self.stdout.write('Setting up standalone database...\n')
        
        # Create superuser
        if not User.objects.filter(username='srvo').exists():
            User.objects.create_superuser(
                username='srvo',
                email='sloane@ethicic.com',
                password='dyzxuc-4muBzy-woqbam'
            )
            self.stdout.write(self.style.SUCCESS('✓ Created admin user: srvo'))
        else:
            self.stdout.write('Admin user already exists')
        
        # Setup Wagtail site
        try:
            # Get or create root page
            root_page = Page.objects.filter(depth=1).first()
            if not root_page:
                self.stdout.write(self.style.ERROR('No root page found'))
                return
            
            # Create home page if it doesn't exist
            home_page = HomePage.objects.first()
            if not home_page:
                home_page = HomePage(
                    title='Ethical Capital',
                    slug='home',
                    hero_title='Ethical Capital',
                    hero_subtitle='Mission-driven investment management',
                    live=True,
                )
                root_page.add_child(instance=home_page)
                self.stdout.write(self.style.SUCCESS('✓ Created home page'))
            
            # Update site to point to home page
            site = Site.objects.first()
            if site:
                site.root_page = home_page
                site.hostname = 'localhost'
                site.port = 80
                site.site_name = 'Ethical Capital'
                site.save()
                self.stdout.write(self.style.SUCCESS('✓ Updated site configuration'))
            else:
                Site.objects.create(
                    hostname='localhost',
                    port=80,
                    root_page=home_page,
                    is_default_site=True,
                    site_name='Ethical Capital'
                )
                self.stdout.write(self.style.SUCCESS('✓ Created site'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error setting up site: {e}'))
        
        self.stdout.write(self.style.SUCCESS('\n✓ Standalone setup complete!'))
        self.stdout.write('You can now access the site and admin at /cms/')