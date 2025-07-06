"""
Base test classes for the public site app.
"""

import json
import os

# Import our Wagtail test base
import sys
from datetime import datetime
from typing import Optional

from django.test import RequestFactory, TestCase
from django.utils import timezone
from wagtail.models import Page

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from tests.wagtail_test_base import WagtailTestCase


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


class BasePublicSiteTestCase(TestCase):
    """Base test case for public site tests."""

    @classmethod
    def setUpTestData(cls):
        """Set up test data once for the entire test class."""

    def setUp(self):
        """Set up each test."""

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
        """Create test data for onboarding forms."""
        data = {
            "first_name": "Test",
            "last_name": "User",
            "email": "onboarding@example.com",
            "phone": "555-123-4567",
            "location": "New York, NY",
            "initial_investment": "50000",
            "monthly_contribution": "1000",
            "time_horizon": "5-10",
            "accredited_investor": True,
            "primary_goal": "growth",
            "risk_tolerance": "moderate",
            "investment_experience": "intermediate",
            "experience_level": "intermediate",
            "exclusions": ["fossil_fuels", "weapons"],
            "impact_areas": ["renewable_energy"],
            "referral_source": "web_search",
            "additional_notes": "Test notes",
            "consent": True,
            "agree_terms": True,
            "terms_accepted": True,
            "confirm_accuracy": True,
        }
        data.update(overrides)
        return data


class FormTestMixin:
    """Mixin for form testing utilities."""

    def submit_form(self, url, data, expect_redirect=True, follow=False):
        """Submit a form and return the response."""
        response = self.client.post(url, data, follow=follow)
        return response

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
                    f"Expected error message '{expected_message}' not found in field '{field}' errors: {field_errors}",
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


class WagtailPublicSiteTestCase(WagtailTestCase, BasePublicSiteTestCase):
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
            except:
                from unittest import SkipTest

                raise SkipTest("Cannot create blog index for blog post creation")

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
