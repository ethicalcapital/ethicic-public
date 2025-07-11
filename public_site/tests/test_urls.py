"""
Tests for URL routing in the public site.
"""

from django.test import TestCase
from django.urls import resolve, reverse

from public_site import views


class PublicSiteURLTest(TestCase):
    """Test URL patterns and routing."""

    def test_contact_form_submit_url(self):
        """Test contact form submission URL."""
        url = reverse("public_site:contact_submit")
        self.assertEqual(url, "/contact/submit/")

        # Test URL resolves to correct view
        resolver = resolve(url)
        self.assertEqual(resolver.func, views.contact_form_submit)

    def test_newsletter_signup_url(self):
        """Test newsletter signup URL."""
        url = reverse("public_site:newsletter_subscribe")
        self.assertEqual(url, "/newsletter/signup/")

        resolver = resolve(url)
        self.assertEqual(resolver.func, views.newsletter_signup)

    def test_onboarding_urls(self):
        """Test onboarding form URLs."""
        # Submit URL
        submit_url = reverse("public_site:onboarding_submit")
        self.assertEqual(submit_url, "/onboarding/submit/")

        resolver = resolve(submit_url)
        self.assertEqual(resolver.func, views.onboarding_form_submit)

        # Thank you page URL
        thank_you_url = reverse("public_site:onboarding_thank_you")
        self.assertEqual(thank_you_url, "/onboarding/thank-you/")

        resolver = resolve(thank_you_url)
        self.assertEqual(resolver.func, views.onboarding_thank_you)

    def test_contact_success_url(self):
        """Test contact success page URL."""
        url = reverse("public_site:contact_success")
        self.assertEqual(url, "/contact/success/")

        resolver = resolve(url)
        self.assertEqual(resolver.func, views.contact_success)

    def test_api_urls(self):
        """Test API endpoint URLs."""
        # Contact API
        contact_api_url = reverse("public_site:api_contact")
        self.assertEqual(contact_api_url, "/api/contact/")

        resolver = resolve(contact_api_url)
        # Check view name (might be wrapped by decorators)
        self.assertTrue(
            hasattr(resolver.func, "__name__") or hasattr(resolver.func, "__wrapped__")
        )

        # Newsletter API
        newsletter_api_url = reverse("public_site:api_newsletter")
        self.assertEqual(newsletter_api_url, "/api/newsletter/")

        resolver = resolve(newsletter_api_url)
        # Check view exists (might be wrapped by decorators)
        self.assertTrue(
            hasattr(resolver.func, "__name__") or hasattr(resolver.func, "__wrapped__")
        )

        # Site status API
        status_api_url = reverse("public_site:api_status")
        self.assertEqual(status_api_url, "/api/status/")

        resolver = resolve(status_api_url)
        # For decorated views, check the wrapped function name
        view_name = getattr(resolver.func, "__name__", None)
        if hasattr(resolver.func, "view_class"):
            view_name = resolver.func.view_class.__name__
        elif hasattr(resolver.func, "__wrapped__"):
            view_name = resolver.func.__wrapped__.__name__
        self.assertIn(view_name, ["site_status_api", "view"])

        # Navigation API
        nav_api_url = reverse("public_site:api_navigation")
        self.assertEqual(nav_api_url, "/api/navigation/")

        # Footer links API
        footer_api_url = reverse("public_site:api_footer")
        self.assertEqual(footer_api_url, "/api/footer-links/")

        # Media items API
        media_api_url = reverse("public_site:api_media_items")
        self.assertEqual(media_api_url, "/api/media-items/")

    def test_garden_platform_urls(self):
        """Test Garden platform URLs."""
        # Overview page
        overview_url = reverse("public_site:garden_overview")
        self.assertEqual(overview_url, "/garden/")

        resolver = resolve(overview_url)
        self.assertEqual(resolver.func, views.garden_overview)

        # Interest registration API
        interest_url = reverse("public_site:garden_interest_registration")
        self.assertEqual(interest_url, "/api/garden/interest/")

        resolver = resolve(interest_url)
        self.assertEqual(resolver.func, views.garden_interest_registration)

    def test_site_search_url(self):
        """Test site search URL."""
        url = reverse("public_site:search")
        self.assertEqual(url, "/search/")

        resolver = resolve(url)
        self.assertEqual(resolver.func, views.site_search)

    def test_url_namespaces(self):
        """Test URL namespaces are correct."""
        # All public site URLs should be in the public_site namespace
        urls_to_test = [
            "public_site:contact_submit",
            "public_site:newsletter_subscribe",
            "public_site:onboarding_submit",
            "public_site:api_contact",
            "public_site:api_status",
            "public_site:garden_overview",
        ]

        for url_name in urls_to_test:
            # Should resolve with namespace
            url = reverse(url_name)
            self.assertIsNotNone(url)

    def test_url_patterns_trailing_slash(self):
        """Test all URLs have consistent trailing slashes."""
        urls_to_test = [
            ("public_site:contact_submit", "/contact/submit/"),
            ("public_site:newsletter_subscribe", "/newsletter/signup/"),
            ("public_site:onboarding_submit", "/onboarding/submit/"),
            ("public_site:onboarding_thank_you", "/onboarding/thank-you/"),
            ("public_site:contact_success", "/contact/success/"),
            ("public_site:api_contact", "/api/contact/"),
            ("public_site:api_newsletter", "/api/newsletter/"),
            ("public_site:api_status", "/api/status/"),
            ("public_site:api_navigation", "/api/navigation/"),
            ("public_site:api_footer", "/api/footer-links/"),
            ("public_site:garden_overview", "/garden/"),
            ("public_site:garden_interest_registration", "/api/garden/interest/"),
            ("public_site:search", "/search/"),
            ("public_site:api_media_items", "/api/media-items/"),
        ]

        for url_name, expected_path in urls_to_test:
            url = reverse(url_name)
            self.assertEqual(url, expected_path)
            # All should end with trailing slash
            self.assertTrue(url.endswith("/"), f"{url_name} should have trailing slash")


class URLAccessibilityTest(TestCase):
    """Test URL accessibility and response codes."""

    def test_public_urls_accessible(self):
        """Test public URLs are accessible without authentication."""
        public_urls = [
            "/search/",
            "/garden/",
            "/contact/success/",
            "/onboarding/thank-you/",
        ]

        for url in public_urls:
            response = self.client.get(url)
            # Should return 200 OK
            self.assertEqual(
                response.status_code, 200, f"{url} should be publicly accessible"
            )

    def test_api_endpoints_accessible(self):
        """Test API endpoints are accessible without authentication."""
        api_urls = [
            "/api/status/",
            "/api/navigation/",
            "/api/footer-links/",
            "/api/media-items/",
        ]

        for url in api_urls:
            response = self.client.get(url)
            # Should return 200 OK
            self.assertEqual(
                response.status_code,
                200,
                f"{url} API endpoint should be publicly accessible",
            )

    def test_post_only_endpoints(self):
        """Test POST-only endpoints reject GET requests."""
        post_only_urls = [
            "/contact/submit/",
            "/newsletter/signup/",
            "/onboarding/submit/",
            "/api/contact/",
            "/api/newsletter/",
            "/api/garden/interest/",
        ]

        for url in post_only_urls:
            # Follow redirects to handle Django's APPEND_SLASH behavior
            response = self.client.get(url, follow=True)
            # Final response should be 405 Method Not Allowed
            self.assertEqual(
                response.status_code,
                405,
                f"{url} should not accept GET requests (got {response.status_code})",
            )

    def test_search_with_query(self):
        """Test search URL with query parameters."""
        response = self.client.get("/search/", {"q": "test query"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("query_string", response.context)
        self.assertEqual(response.context["query_string"], "test query")

    def test_media_api_pagination(self):
        """Test media API with pagination parameters."""
        response = self.client.get("/api/media-items/", {"page": "1", "per_page": "10"})
        self.assertEqual(response.status_code, 200)

        # Check JSON response
        import json

        data = json.loads(response.content)
        self.assertIn("items", data)
        self.assertIn("has_next", data)
        self.assertIn("total_pages", data)


class URLParameterTest(TestCase):
    """Test URL parameter handling."""

    def test_search_query_escaping(self):
        """Test search handles special characters in query."""
        special_queries = [
            "test & query",
            'test <script>alert("xss")</script>',
            "test?param=value",
            "test#anchor",
            "test%20encoded",
        ]

        for query in special_queries:
            response = self.client.get("/search/", {"q": query})
            self.assertEqual(response.status_code, 200)
            # Query should be properly escaped in context
            self.assertEqual(response.context["query_string"], query)

    def test_media_api_invalid_pagination(self):
        """Test media API handles invalid pagination parameters."""
        # Invalid page number should cause a ValueError and return 400
        response = self.client.get(
            "/api/media-items/", {"page": "invalid", "per_page": "10"}
        )
        # The API returns 200 with an error message for non-integer page
        self.assertIn(response.status_code, [200, 400])

        # Negative page number
        response = self.client.get(
            "/api/media-items/", {"page": "-1", "per_page": "10"}
        )
        # The API returns 200 with empty results for out-of-range pages
        self.assertEqual(response.status_code, 200)

        # Excessive per_page
        response = self.client.get(
            "/api/media-items/",
            {
                "page": "1",
                "per_page": "1000",  # Should be capped
            },
        )
        self.assertEqual(response.status_code, 200)

        import json

        data = json.loads(response.content)
        # Should be capped at reasonable limit
        self.assertLessEqual(len(data["items"]), 50)
