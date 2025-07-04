"""Base test class that properly sets up Wagtail for testing."""
from django.test import TestCase, TransactionTestCase
from wagtail.models import Page, Site, Locale
from django.contrib.auth import get_user_model


class WagtailTestCase(TestCase):
    """Base test case that ensures Wagtail is properly set up."""
    
    @classmethod
    def setUpTestData(cls):
        """Set up test data once for the entire test class."""
        super().setUpTestData()
        
        # Ensure we have a locale
        cls.locale = Locale.objects.get_or_create(language_code='en')[0]
        
        # Ensure we have a root page
        if not Page.objects.filter(depth=1).exists():
            cls.root_page = Page.add_root(
                title='Root',
                locale=cls.locale
            )
        else:
            cls.root_page = Page.objects.get(depth=1)
        
        # Ensure we have a home page
        home_pages = Page.objects.filter(slug='home', depth=2)
        if not home_pages.exists():
            from public_site.models import HomePage
            cls.home_page = HomePage(
                title='Home',
                slug='home',
                hero_title='Test Home Page',
                hero_tagline='Test tagline',
                locale=cls.locale
            )
            cls.root_page.add_child(instance=cls.home_page)
        else:
            cls.home_page = home_pages.first()
        
        # Ensure we have a default site
        cls.site = Site.objects.get_or_create(
            hostname='localhost',
            defaults={
                'port': 80,
                'root_page': cls.home_page,
                'is_default_site': True,
            }
        )[0]
        
        # Create a test user
        User = get_user_model()
        cls.user = User.objects.get_or_create(
            username='testuser',
            defaults={
                'email': 'test@example.com',
                'is_staff': True,
                'is_superuser': True,
            }
        )[0]


class WagtailTransactionTestCase(TransactionTestCase):
    """Transaction test case version for tests that need transactions."""
    
    def setUp(self):
        """Set up test data for each test."""
        super().setUp()
        
        # Ensure we have a locale
        self.locale = Locale.objects.get_or_create(language_code='en')[0]
        
        # Ensure we have a root page
        if not Page.objects.filter(depth=1).exists():
            self.root_page = Page.add_root(
                title='Root',
                locale=self.locale
            )
        else:
            self.root_page = Page.objects.get(depth=1)
        
        # Ensure we have a home page
        home_pages = Page.objects.filter(slug='home', depth=2)
        if not home_pages.exists():
            from public_site.models import HomePage
            self.home_page = HomePage(
                title='Home',
                slug='home',
                hero_title='Test Home Page',
                hero_tagline='Test tagline',
                locale=self.locale
            )
            self.root_page.add_child(instance=self.home_page)
        else:
            self.home_page = home_pages.first()
        
        # Ensure we have a default site
        self.site = Site.objects.get_or_create(
            hostname='localhost',
            defaults={
                'port': 80,
                'root_page': self.home_page,
                'is_default_site': True,
            }
        )[0]
        
        # Create a test user
        User = get_user_model()
        self.user = User.objects.get_or_create(
            username='testuser',
            defaults={
                'email': 'test@example.com',
                'is_staff': True,
                'is_superuser': True,
            }
        )[0]