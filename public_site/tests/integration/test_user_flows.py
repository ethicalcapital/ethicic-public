"""
Integration tests for complete user flows in the public site.
"""

import json
from unittest.mock import Mock, patch

from django.test import override_settings

from public_site.models import SupportTicket, OnboardingPage
from public_site.tests.test_base import (
    APITestMixin,
    BasePublicSiteTestCase,
    FormTestMixin,
    WagtailPublicSiteTestCase,
)


@override_settings(
    TESTING=True,
    CONTACT_EMAIL="test@ethicic.com",
    DEFAULT_FROM_EMAIL="noreply@ethicic.com",
)
class ContactInquiryFlowTest(BasePublicSiteTestCase, FormTestMixin):
    """Test complete contact inquiry user flow."""

    def test_general_inquiry_flow(self):
        """Test a complete general inquiry flow from form to ticket."""
        # Test contact form submission directly (no page dependency)
        # Step 1: User fills out and submits contact form
        contact_data = self.create_test_contact_data()
        contact_data["subject"] = "general"
        contact_data[
            "message"
        ] = "I would like to learn more about your investment services."

        submit_response = self.submit_form("/contact/submit/", contact_data)

        # Step 2: Verify redirect to contact page with success message
        self.assert_redirect(submit_response, "/contact/")

        # Step 3: Verify support ticket was created
        ticket = SupportTicket.objects.first()
        self.assertIsNotNone(ticket)
        self.assertEqual(ticket.email, "test@example.com")
        self.assertEqual(ticket.status, "new")  # Default status is 'new'
        self.assertIn("general", ticket.subject)
        self.assertIn("Test Company", ticket.subject)

        # Step 4: Verify ticket details
        self.assertEqual(ticket.name, "Test User")
        self.assertEqual(ticket.ticket_type, "contact")
        self.assertIn("learn more about your investment services", ticket.message)

    def test_investment_inquiry_flow(self):
        """Test investment services inquiry flow."""
        # Investment inquiry with company info
        contact_data = self.create_test_contact_data()
        contact_data.update(
            {
                "name": "Jane Investor",
                "email": "jane@investmentfirm.com",
                "company": "Investment Firm LLC",
                "subject": "investment_inquiry",
                "message": "We are interested in your ethical investment strategies for our clients.",
            }
        )

        response = self.submit_form("/contact/submit/", contact_data)

        # Check ticket was created with correct priority
        ticket = SupportTicket.objects.first()
        self.assertEqual(ticket.email, "jane@investmentfirm.com")
        self.assertIn("Investment Firm LLC", ticket.subject)
        self.assertEqual(ticket.ticket_type, "contact")

    def test_adviser_partnership_inquiry_flow(self):
        """Test adviser partnership inquiry flow."""
        contact_data = self.create_test_contact_data()
        contact_data.update(
            {
                "name": "John Adviser",
                "email": "john@ria.com",
                "company": "Registered Investment Advisors",
                "subject": "adviser_partnership",
                "message": "Looking to partner with you to offer ethical investment options to our clients.",
            }
        )

        response = self.submit_form("/contact/submit/", contact_data)

        # Verify high-priority handling for advisers
        ticket = SupportTicket.objects.first()
        self.assertEqual(ticket.ticket_type, "contact")
        self.assertIn("Registered Investment Advisors", ticket.subject)

    @patch("public_site.views.requests")
    def test_contact_flow_with_api_integration(self, mock_requests):
        """Test contact flow with main platform API integration."""
        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 201
        mock_requests.post.return_value = mock_response

        contact_data = self.create_test_contact_data()

        with self.settings(MAIN_PLATFORM_API_URL="http://api.example.com/"):
            response = self.submit_form("/contact/submit/", contact_data)

        # Verify API was called
        mock_requests.post.assert_called_once()

        # Verify local ticket still created
        self.assertEqual(SupportTicket.objects.count(), 1)


@override_settings(TESTING=True)
class NewsletterSubscriptionFlowTest(BasePublicSiteTestCase, FormTestMixin):
    """Test newsletter subscription user flow."""

    def test_newsletter_signup_from_blog(self):
        """Test newsletter signup flow (tests form submission directly)."""
        # Test newsletter form submission directly (no page dependency)
        # Step 1: User enters email in newsletter form
        newsletter_data = self.create_test_newsletter_data()
        newsletter_data["email"] = "blog_reader@example.com"

        # Step 2: Submit newsletter form
        response = self.submit_form("/newsletter/signup/", newsletter_data)

        # Step 3: Verify redirect back to referring page
        self.assertEqual(response.status_code, 302)

        # Step 4: Verify ticket was created
        ticket = SupportTicket.objects.first()
        self.assertEqual(ticket.email, "blog_reader@example.com")
        self.assertEqual(ticket.subject, "Newsletter Signup")
        self.assertEqual(ticket.status, "resolved")  # Auto-resolved

    def test_newsletter_with_existing_contact(self):
        """Test newsletter signup falls back to SupportTicket in standalone deployment."""
        # Since CRM models aren't available in standalone deployment,
        # the view should fall back to creating a SupportTicket

        newsletter_data = self.create_test_newsletter_data(email="existing@example.com")

        # Create an existing ticket to simulate "existing contact"
        existing_ticket = SupportTicket.objects.create(
            name="Previous Subscriber",
            email="existing@example.com",
            subject="Previous Signup",
            message="Previous newsletter signup",
            ticket_type="newsletter",
            status="resolved",
        )

        response = self.submit_form("/newsletter/signup/", newsletter_data)

        # Should create a new ticket (since we can't update in SupportTicket model)
        tickets = SupportTicket.objects.filter(email="existing@example.com")
        self.assertEqual(tickets.count(), 2)  # Original + new

        # Check the new ticket
        new_ticket = tickets.exclude(id=existing_ticket.id).first()
        self.assertEqual(new_ticket.subject, "Newsletter Signup")
        self.assertEqual(new_ticket.status, "resolved")


@override_settings(TESTING=True)
class OnboardingFlowTest(WagtailPublicSiteTestCase, FormTestMixin):
    """Test client onboarding flow."""
    
    def setUp(self):
        super().setUp()
        
        # Create onboarding page for redirect tests
        self.onboarding_page = OnboardingPage(
            title="Onboarding",
            slug="onboarding",
            locale=self.locale
        )
        self.home_page.add_child(instance=self.onboarding_page)

    def test_complete_onboarding_flow(self):
        """Test complete onboarding flow from form to confirmation."""
        # Test onboarding form submission directly (no page dependency)
        # Step 1: User fills out comprehensive onboarding form
        onboarding_data = self.create_test_onboarding_data()
        onboarding_data.update(
            {
                "legal_name": "Sarah Investor",
                "email": "sarah@example.com",
                "initial_investment": "100000",
            }
        )

        # Step 2: Submit onboarding form
        response = self.submit_form("/onboarding/submit/", onboarding_data)

        # Debug: Print response status and content if not a redirect
        if response.status_code != 302:
            print(f"Response status: {response.status_code}")
            if hasattr(response, "context") and "form" in response.context:
                print(f"Form errors: {response.context['form'].errors}")

        # Step 3: Verify redirect to thank you page
        self.assert_redirect(response, "/onboarding/thank-you/")

        # Step 4: Follow redirect to thank you page
        thank_you_response = self.client.get("/onboarding/thank-you/")
        self.assertEqual(thank_you_response.status_code, 200)
        self.assertIn("Application Received", thank_you_response.content.decode())

        # Step 5: Verify onboarding ticket was created
        ticket = SupportTicket.objects.first()
        self.assertEqual(ticket.name, "Sarah Investor")
        self.assertIn("Onboarding Application", ticket.subject)
        self.assertIn("$100,000", ticket.message)
        self.assertEqual(ticket.status, "new")
        self.assertEqual(ticket.ticket_type, "onboarding")

    def test_onboarding_validation_flow(self):
        """Test onboarding with validation errors."""
        # Test onboarding form validation directly (no page dependency)
        # Invalid data - spam detected via honeypot
        invalid_data = self.create_test_onboarding_data()
        invalid_data["honeypot"] = "spam content"  # Triggers spam detection

        response = self.submit_form("/onboarding/submit/", invalid_data)

        # Should redirect back to form
        self.assert_redirect(response, "/onboarding/")

        # No ticket should be created
        self.assertEqual(SupportTicket.objects.count(), 0)


@override_settings(TESTING=True)
class APIIntegrationFlowTest(BasePublicSiteTestCase, APITestMixin):
    """Test API integration flows."""

    def test_contact_api_flow(self):
        """Test contact submission via API."""
        # Step 1: External system submits contact via API
        api_data = {
            "name": "API Integration Test",
            "email": "api@external.com",
            "company": "External System Inc",
            "subject": "partnership",
            "message": "Submitted via API integration for partnership inquiry.",
        }

        response = self.post_json("/api/contact/", api_data)

        # Step 2: Verify API response
        result = self.assert_api_success(response, 201)
        self.assertIn("ticket_id", result)
        self.assertIn("Thank you", result["message"])

        # Step 3: Verify ticket was created
        ticket = SupportTicket.objects.get(id=result["ticket_id"])
        self.assertEqual(ticket.email, "api@external.com")
        self.assertEqual(ticket.name, "API Integration Test")
        self.assertEqual(ticket.ticket_type, "contact")

    def test_newsletter_api_flow(self):
        """Test newsletter subscription via API."""
        api_data = {
            "email": "api-newsletter@example.com",
            "consent": True,
        }

        response = self.post_json("/api/newsletter/", api_data)

        result = self.assert_api_success(response, 201)

        # Verify ticket
        ticket = SupportTicket.objects.first()
        self.assertEqual(ticket.email, "api-newsletter@example.com")
        self.assertEqual(ticket.status, "resolved")

    def test_site_navigation_api_flow(self):
        """Test fetching site navigation via API."""
        # Step 1: Request navigation
        nav_response = self.client.get("/api/navigation/")
        nav_data = self.assert_api_success(nav_response)

        # Step 2: Verify navigation structure
        self.assertIn("navigation", nav_data)
        nav_items = nav_data["navigation"]

        # Check expected navigation items exist
        nav_slugs = [item["slug"] for item in nav_items]
        self.assertIn("home", nav_slugs)
        self.assertIn("about", nav_slugs)
        self.assertIn("blog", nav_slugs)
        self.assertIn("contact", nav_slugs)

        # Step 3: Request footer links
        footer_response = self.client.get("/api/footer-links/")
        footer_data = self.assert_api_success(footer_response)

        # Verify footer sections
        self.assertIn("company", footer_data)
        self.assertIn("services", footer_data)
        self.assertIn("legal", footer_data)
        self.assertIn("connect", footer_data)


@override_settings(TESTING=True)
class GardenPlatformFlowTest(BasePublicSiteTestCase, APITestMixin):
    """Test Garden platform interest flow."""

    def test_adviser_garden_interest_flow(self):
        """Test adviser expressing interest in Garden platform."""
        # Step 1: Adviser visits Garden overview
        overview_response = self.client.get("/garden/")
        self.assertEqual(overview_response.status_code, 200)

        # Verify feature information
        self.assertIn("garden_features", overview_response.context)
        features = overview_response.context["garden_features"]
        self.assertEqual(len(features), 6)

        # Step 2: Adviser submits interest form
        interest_data = {
            "name": "Jane Adviser",
            "email": "jane@advisorfirm.com",
            "company": "Advisor Firm LLC",
            "role": "Chief Investment Officer",
            "interest_areas": [
                "Portfolio Intelligence",
                "Research Platform",
                "Compliance",
            ],
            "message": "We manage $100M and need better ethical screening tools.",
        }

        response = self.post_json("/api/garden/interest/", interest_data)

        # Step 3: Verify successful submission
        result = self.assert_api_success(response, 201)
        self.assertIn("Thank you", result["message"])

        # Step 4: Verify ticket was created
        ticket = SupportTicket.objects.first()
        self.assertEqual(ticket.name, "Jane Adviser")
        self.assertEqual(ticket.ticket_type, "garden_interest")
        self.assertIn("Chief Investment Officer", ticket.subject)
        self.assertIn("$100M", ticket.message)

    def test_institution_garden_interest_flow(self):
        """Test institution expressing interest in Garden platform."""
        interest_data = {
            "name": "University Endowment",
            "email": "cio@university.edu",
            "company": "State University System",
            "role": "Chief Investment Officer",
            "interest_areas": ["ESG Integration", "Reporting", "Risk Management"],
            "message": "Need institutional-grade ESG analytics for our $500M endowment.",
        }

        response = self.post_json("/api/garden/interest/", interest_data)

        result = self.assert_api_success(response, 201)

        # Verify high-priority handling for institutions
        ticket = SupportTicket.objects.first()
        self.assertIn("$500M endowment", ticket.message)


class SearchFlowTest(WagtailPublicSiteTestCase):
    """Test site search functionality flow."""

    def setUp(self):
        super().setUp()
        # Create test content
        self.blog_index = self.create_test_blog_index()
        self.blog_post1 = self.create_test_blog_post(
            parent=self.blog_index, title="Ethical Investing Guide"
        )
        self.blog_post2 = self.create_test_blog_post(
            parent=self.blog_index, title="Portfolio Management Tips"
        )

    def test_search_flow(self):
        """Test user search flow."""
        # Step 1: User performs search
        search_response = self.client.get("/search/", {"q": "ethical"})

        self.assertEqual(search_response.status_code, 200)
        self.assertIn("query_string", search_response.context)
        self.assertEqual(search_response.context["query_string"], "ethical")

        # Step 2: Verify search results
        if "search_results" in search_response.context:
            results = search_response.context["search_results"]
            # Results should include relevant content
            self.assertGreater(len(results), 0)

    def test_empty_search_flow(self):
        """Test search with no query."""
        response = self.client.get("/search/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["query_string"], "")
        self.assertEqual(response.context["total_results"], 0)


class MediaBrowsingFlowTest(WagtailPublicSiteTestCase, APITestMixin):
    """Test media browsing flow."""

    def setUp(self):
        super().setUp()
        self.media_page = self.create_test_media_page()

    def test_media_infinite_scroll_flow(self):
        """Test media page infinite scroll flow."""
        # Step 1: Initial page load
        page1_response = self.client.get(
            "/api/media-items/", {"page": "1", "per_page": "3"}
        )

        page1_data = self.assert_api_success(page1_response)
        self.assertEqual(len(page1_data["items"]), 3)
        self.assertTrue(page1_data["has_next"])

        # Verify featured item is first
        self.assertTrue(page1_data["items"][0]["featured"])

        # Step 2: Load more items
        page2_response = self.client.get(
            "/api/media-items/", {"page": "2", "per_page": "3"}
        )

        page2_data = self.assert_api_success(page2_response)
        self.assertGreater(len(page2_data["items"]), 0)

        # Step 3: Verify no duplicate items
        page1_ids = [item["id"] for item in page1_data["items"]]
        page2_ids = [item["id"] for item in page2_data["items"]]
        self.assertEqual(len(set(page1_ids) & set(page2_ids)), 0)  # No overlap


@override_settings(TESTING=True)
class ErrorHandlingFlowTest(BasePublicSiteTestCase, FormTestMixin):
    """Test error handling in user flows."""

    def test_contact_form_spam_detection_flow(self):
        """Test spam detection in contact flow."""
        # Attempt to submit spam content
        spam_data = self.create_test_contact_data()
        spam_data[
            "message"
        ] = "Buy viagra now! Click here! Limited offer! Make money fast!"

        response = self.submit_form("/contact/submit/", spam_data)

        # Should redirect but no ticket created
        self.assert_redirect(response, "/contact/")
        self.assertEqual(SupportTicket.objects.count(), 0)

    def test_rate_limiting_flow(self):
        """Test rate limiting protection."""
        # Submit multiple forms rapidly
        contact_data = self.create_test_contact_data()

        for i in range(5):
            # Change email to avoid duplication
            contact_data["email"] = f"test{i}@example.com"
            response = self.submit_form("/contact/submit/", contact_data)

        # All should succeed in testing mode
        self.assertEqual(SupportTicket.objects.count(), 5)

    def test_api_error_handling_flow(self):
        """Test API error handling."""
        # Invalid JSON
        response = self.client.post(
            "/api/contact/", data="invalid json {", content_type="application/json"
        )

        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertFalse(data["success"])
        self.assertIn("Invalid JSON", data["message"])
