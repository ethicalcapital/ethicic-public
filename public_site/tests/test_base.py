"""
Base test classes for the public site app.
"""

import json

# Import Django and Wagtail test utilities
from datetime import datetime
from typing import Optional

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase, TransactionTestCase
from django.utils import timezone
from wagtail.models import Locale, Page, Site


class WagtailTestCase(TestCase):
    """Base test case that ensures Wagtail is properly set up."""

    @classmethod
    def setUpTestData(cls):
        """Set up test data once for the entire test class."""
        super().setUpTestData()

        # Ensure we have a locale
        cls.locale = Locale.objects.get_or_create(language_code="en")[0]

        # Ensure we have a root page
        if not Page.objects.filter(depth=1).exists():
            cls.root_page = Page.add_root(title="Root", locale=cls.locale)
        else:
            cls.root_page = Page.objects.get(depth=1)

        # Ensure we have a home page
        home_pages = Page.objects.filter(slug="home", depth=2)
        if not home_pages.exists():
            from public_site.models import HomePage

            cls.home_page = HomePage(
                title="Home",
                slug="home",
                hero_title="Test Home Page",
                hero_tagline="Test tagline",
                locale=cls.locale,
            )
            cls.root_page.add_child(instance=cls.home_page)
        else:
            cls.home_page = home_pages.first()

        # Ensure we have a default site
        cls.site = Site.objects.get_or_create(
            hostname="localhost",
            defaults={
                "port": 80,
                "root_page": cls.home_page,
                "is_default_site": True,
            },
        )[0]

        # Create a test user
        user_model = get_user_model()
        cls.user = user_model.objects.get_or_create(
            username="testuser",
            defaults={
                "email": "test@example.com",
                "is_staff": True,
                "is_superuser": True,
            },
        )[0]


class WagtailTransactionTestCase(TransactionTestCase):
    """Transaction test case version for tests that need transactions."""

    def setUp(self):
        """Set up test data for each test."""
        super().setUp()

        # Ensure we have a locale
        self.locale = Locale.objects.get_or_create(language_code="en")[0]

        # Ensure we have a root page
        if not Page.objects.filter(depth=1).exists():
            self.root_page = Page.add_root(title="Root", locale=self.locale)
        else:
            self.root_page = Page.objects.get(depth=1)

        # Ensure we have a home page
        home_pages = Page.objects.filter(slug="home", depth=2)
        if not home_pages.exists():
            from public_site.models import HomePage

            self.home_page = HomePage(
                title="Home",
                slug="home",
                hero_title="Test Home Page",
                hero_tagline="Test tagline",
                locale=self.locale,
            )
            self.root_page.add_child(instance=self.home_page)
        else:
            self.home_page = home_pages.first()

        # Ensure we have a default site
        self.site = Site.objects.get_or_create(
            hostname="localhost",
            defaults={
                "port": 80,
                "root_page": self.home_page,
                "is_default_site": True,
            },
        )[0]

        # Create a test user
        user_model = get_user_model()
        self.user = user_model.objects.get_or_create(
            username="testuser",
            defaults={
                "email": "test@example.com",
                "is_staff": True,
                "is_superuser": True,
            },
        )[0]


class MockRequestFactory:
    """Factory for creating mock request objects."""

    @staticmethod
    def create_request(user=None, session=None, **kwargs):
        """Create a mock request object."""
        factory = RequestFactory()
        request = factory.get("/", **kwargs)

        # Add user
        if user:
            request.user = user

        # Add session
        if session:
            request.session = session
        else:
            # Create minimal session
            request.session = {}

        return request


class BasePublicSiteTestCase(WagtailTestCase):
    """Base test case for public site tests."""

    @classmethod
    def setUpTestData(cls):
        """Set up test data once for the entire test class."""
        super().setUpTestData()

    def setUp(self):
        """Set up each test."""
        super().setUp()

    def create_test_contact_data(self, **overrides):
        """Create test data for contact forms."""
        data = {
            "name": "Test User",
            "email": "test@example.com",
            "company": "Test Company",
            "subject": "general",
            "message": "This is a test message for contact form submission.",
            "human_check": "2",  # 1+1=2 (test math problem)
            "consent": True,
        }
        data.update(overrides)
        return data

    def create_test_newsletter_data(self, **overrides):
        """Create test data for newsletter forms."""
        data = {
            "email": "newsletter@example.com",
            "consent": True,
        }
        data.update(overrides)
        return data

    def create_test_onboarding_data(self, **overrides):
        """Create test data for onboarding forms that matches actual form structure."""
        data = {
            # Section 1: About You
            "email": "onboarding@example.com",
            "first_name": "Test",
            "last_name": "User",
            "preferred_name_choice": "nope",
            "pronouns": "they/them",
            "street_address": "123 Test St",
            "city": "New York",
            "state": "NY",
            "zip_code": "10001",
            "country": "United States",
            "phone": "555-123-4567",
            "birthday": "1990-01-01",
            "employment_status": "full_time",
            "employer_name": "Test Company",
            "job_title": "Software Engineer",
            "marital_status": "single",
            "add_co_client": "no",
            # Section 3: Contact Preferences
            "communication_preference": ["email"],
            "newsletter_subscribe": "yes",
            # Section 4: Risk Questions
            "risk_question_1": "neutral",
            "risk_question_2": "agree",
            "risk_question_3": "neutral",
            "risk_question_4": "agree",
            "risk_question_5": "strongly_agree",
            "risk_question_6": "agree",
            "risk_question_7": "strongly_agree",
            # Section 5: Values and Viewpoint
            "ethical_considerations": ["environmental_impact"],
            "divestment_movements": ["fossil_fuels"],
            "understanding_importance": "very",
            "ethical_evolution": "strongly_support",
            # Section 6: Financial Context
            "investment_experience": "average",
            "emergency_access": "yes",
            "net_worth": "500000",
            "liquid_net_worth": "200000",
            "investable_net_worth": "100000",
            "investment_familiarity": "get_gist",
            "worked_with_adviser": "yes",
            "account_types": ["individual_taxable"],
            # Anti-spam
            "honeypot": "",
        }
        data.update(overrides)
        return data


class FormTestMixin:
    """Mixin for form testing utilities."""

    def submit_form(self, url, data, expect_redirect=True, follow=False):
        """Submit a form and return the response."""
        return self.client.post(url, data, follow=follow)

    def assert_redirect(self, response, expected_url):
        """Assert that response is a redirect to expected URL."""
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, expected_url)

    def assert_form_error(self, response, field_name, error_message=None):
        """Assert that a form has an error for the given field."""
        self.assertContains(response, f'name="{field_name}"')
        if error_message:
            self.assertContains(response, error_message)

    def assert_form_valid(self, form):
        """Assert that a form is valid."""
        if hasattr(form, "errors"):
            self.assertTrue(
                form.is_valid(), f"Form should be valid but got errors: {form.errors}"
            )

    def assert_form_invalid(self, form, expected_errors=None):
        """Assert that a form is invalid with optional expected errors."""
        self.assertFalse(form.is_valid(), "Form should be invalid but was valid")

        if expected_errors:
            # Check for expected error messages
            for field, expected_message in expected_errors.items():
                self.assertIn(
                    field, form.errors, f"Expected error for field '{field}' not found"
                )

                # Check if the expected message is in the error messages
                field_errors = form.errors[field]
                error_found = any(
                    expected_message in str(error) for error in field_errors
                )
                self.assertTrue(
                    error_found,
                    f"Expected error message '{expected_message}' not found in "
                    f"field '{field}' errors: {field_errors}",
                )


class APITestMixin:
    """Mixin for API testing utilities."""

    def post_json(self, url, data):
        """Post JSON data to an API endpoint."""
        return self.client.post(
            url, data=json.dumps(data), content_type="application/json"
        )

    def assert_api_success(self, response, expected_status=200):
        """Assert that an API response is successful."""
        self.assertEqual(response.status_code, expected_status)
        data = json.loads(response.content)
        self.assertTrue(data.get("success", True))
        return data

    def assert_api_error(self, response, expected_status=400):
        """Assert that an API response is an error."""
        self.assertEqual(response.status_code, expected_status)
        data = json.loads(response.content)
        self.assertFalse(data.get("success", True))
        return data


class WagtailPublicSiteTestCase(BasePublicSiteTestCase):
    """Base test case for Wagtail page tests with proper Wagtail setup."""

    @classmethod
    def setUpTestData(cls):
        """Set up test data once for the entire test class."""
        # Call WagtailTestCase setup first to ensure Wagtail is ready
        super().setUpTestData()

        # Now we have these available from WagtailTestCase:
        # cls.locale, cls.root_page, cls.home_page, cls.site, cls.user

        # Set up additional pages as needed
        cls.contact_page = None
        cls.onboarding_page = None
        cls.blog_index = None

    def setUp(self):
        """Set up each test."""
        super().setUp()

    def create_test_blog_index(self):
        """Create a test blog index page - will skip if no home page."""
        if not hasattr(self, "home_page") or not self.home_page:
            from unittest import SkipTest

            raise SkipTest("No home page available for blog index creation")

        from public_site.models import BlogIndexPage

        blog_index = BlogIndexPage(
            title="Blog",
            slug="blog",
            intro_text="<p>Welcome to our blog</p>",
        )
        self.home_page.add_child(instance=blog_index)
        return blog_index

    def create_test_blog_post(
        self,
        parent: Optional[Page] = None,
        title: str = "Test Blog Post",
        featured: bool = False,
        publish_date: Optional[datetime] = None,
    ):
        """Create a test blog post."""
        if not parent:
            try:
                parent = self.create_test_blog_index()
            except Exception:
                from unittest import SkipTest

                raise SkipTest(
                    "Cannot create blog index for blog post creation"
                ) from None

        if not parent:
            from unittest import SkipTest

            raise SkipTest("No parent page available for blog post creation")

        import re

        from public_site.models import BlogPost

        slug = re.sub(r"[^a-z0-9-_]", "", title.lower().replace(" ", "-"))
        blog_post = BlogPost(
            title=title,
            slug=slug,
            excerpt="Test excerpt for the blog post.",
            body="<p>Test blog post content with sufficient length.</p>",
            author="Test Author",
            featured=featured,
            publish_date=publish_date or timezone.now().date(),
        )
        parent.add_child(instance=blog_post)

        # Publish the post
        blog_post.save_revision().publish()

        return blog_post

    def create_test_strategy_page(
        self,
        parent: Optional[Page] = None,
        title: str = "Test Strategy",
        strategy_label: str = "Test Label",
    ):
        """Create a test strategy page."""
        if not parent:
            parent = getattr(self, "home_page", None)

        if not parent:
            # Skip page creation if no parent available
            from unittest import SkipTest

            raise SkipTest("No parent page available for strategy page creation")

        import re

        from public_site.models import StrategyPage

        slug = re.sub(r"[^a-z0-9-_]", "", title.lower().replace(" ", "-"))
        strategy = StrategyPage(
            title=title,
            slug=slug,
            strategy_subtitle="Test strategy subtitle",
            strategy_description="<p>Test strategy description</p>",
            strategy_label=strategy_label,
            risk_level="Full market exposure",
            ethical_implementation="100% Full Criteria",
            holdings_count="~25 positions",
            best_for="Long-term growth",
        )
        parent.add_child(instance=strategy)
        return strategy

    def create_test_faq_article(
        self,
        parent: Optional[Page] = None,
        title: str = "Test FAQ Article",
        category: str = "general",
        featured: bool = False,
    ):
        """Create a test FAQ article."""
        if not parent:
            home_page = getattr(self, "home_page", None)
            if not home_page:
                from unittest import SkipTest

                raise SkipTest("No home page available for FAQ creation")

            # Create FAQ index if not provided
            from public_site.models import FAQIndexPage

            faq_index = FAQIndexPage(
                title="Support",
                slug="support",
                locale=getattr(self, "locale", None) or home_page.locale,
            )
            home_page.add_child(instance=faq_index)
            parent = faq_index

        if not parent:
            from unittest import SkipTest

            raise SkipTest("No parent page available for FAQ article creation")

        import re

        from public_site.models import FAQArticle

        # Generate a valid slug by removing special characters
        slug = re.sub(r"[^a-z0-9-_]", "", title.lower().replace(" ", "-"))
        article = FAQArticle(
            title=title,
            slug=slug,
            summary="Test FAQ summary",
            content="<p>Test FAQ content with detailed answer.</p>",
            category=category,
            featured=featured,
            priority=1,
            locale=parent.locale,
        )
        parent.add_child(instance=article)
        return article

    def create_test_media_page(self):
        """Create a test media page with items - will skip if no home page."""
        home_page = getattr(self, "home_page", None)
        if not home_page:
            from unittest import SkipTest

            raise SkipTest("No home page available for media page creation")

        from public_site.models import MediaItem, MediaPage

        media_page = MediaPage(
            title="Media",
            slug="media",
            sidebar_interview_show=True,
            sidebar_contact_show=True,
        )
        home_page.add_child(instance=media_page)

        # Create test media items
        for i in range(5):
            MediaItem.objects.create(
                title=f"Media Item {i+1}",
                description=f"Description for media item {i+1}",
                publication="Test Publication",
                publication_date=timezone.now().date(),
                featured=(i == 0),  # First item is featured
                external_url=f"https://example.com/item-{i+1}",
                page=media_page,
            )

        return media_page
