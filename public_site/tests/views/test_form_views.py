"""
Tests for form submission views in the public site.
"""

import json
from unittest.mock import Mock, patch

from django.test import override_settings
from django.utils import timezone

from public_site.models import SupportTicket
from public_site.tests.test_base import (
    APITestMixin,
    BasePublicSiteTestCase,
    FormTestMixin,
)


@override_settings(
    TESTING=True,
    CONTACT_EMAIL="test@ethicic.com",
    DEFAULT_FROM_EMAIL="noreply@ethicic.com",
)
class ContactFormViewTest(BasePublicSiteTestCase, FormTestMixin):
    """Test contact form submission view."""

    def test_contact_form_submit_success(self):
        """Test successful contact form submission."""
        data = self.create_test_contact_data()

        response = self.submit_form("/contact/submit/", data, follow=False)

        # Should redirect to contact page
        self.assert_redirect(response, "/contact/")

        # Check support ticket was created
        ticket = SupportTicket.objects.first()
        self.assertIsNotNone(ticket)
        self.assertEqual(ticket.email, "test@example.com")
        self.assertEqual(ticket.name, "Test User")
        self.assertIn("general", ticket.subject)
        self.assertEqual(ticket.status, "new")

    def test_contact_form_validation_errors(self):
        """Test contact form with validation errors."""
        data = self.create_test_contact_data()
        data["email"] = "invalid-email"  # Invalid email
        data["message"] = "Too short"  # Too short message

        response = self.submit_form("/contact/submit/", data, follow=False)

        # Should redirect with error
        self.assert_redirect(response, "/contact/")

        # No ticket should be created
        self.assertEqual(SupportTicket.objects.count(), 0)

    def test_contact_form_honeypot_protection(self):
        """Test honeypot spam protection."""
        data = self.create_test_contact_data()
        data["honeypot"] = "spam content"  # Fill honeypot field

        response = self.submit_form("/contact/submit/", data, follow=False)

        # Should redirect but no ticket created
        self.assert_redirect(response, "/contact/")
        self.assertEqual(SupportTicket.objects.count(), 0)

    def test_contact_form_missing_fields(self):
        """Test contact form with missing required fields."""
        data = {
            "email": "test@example.com",
            # Missing name, message, subject
            "human_check": "2",
            "form_start_time": str(timezone.now().timestamp() - 15),
        }

        response = self.submit_form("/contact/submit/", data, follow=False)

        self.assert_redirect(response, "/contact/")
        self.assertEqual(SupportTicket.objects.count(), 0)

    @patch("public_site.views.requests")
    def test_contact_form_api_integration(self, mock_requests):
        """Test contact form attempts to submit to main platform API."""
        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 201
        mock_requests.post.return_value = mock_response

        data = self.create_test_contact_data()

        with self.settings(MAIN_PLATFORM_API_URL="http://api.example.com/"):
            response = self.submit_form("/contact/submit/", data, follow=False)

        # Should attempt API call
        mock_requests.post.assert_called_once()
        call_args = mock_requests.post.call_args
        self.assertIn("contact/submit/", call_args[0][0])

    @patch("public_site.views.send_fallback_email")
    @patch("public_site.views.requests")
    def test_contact_form_fallback_email(self, mock_requests, mock_send_email):
        """Test fallback email when API fails."""
        # Mock failed API response
        mock_requests.post.side_effect = Exception("API Error")

        data = self.create_test_contact_data()

        with self.settings(MAIN_PLATFORM_API_URL="http://api.example.com/"):
            response = self.submit_form("/contact/submit/", data, follow=False)

        # Should call fallback email
        mock_send_email.assert_called_once()

        # Should still create local ticket
        self.assertEqual(SupportTicket.objects.count(), 1)


@override_settings(TESTING=True)
class NewsletterSignupViewTest(BasePublicSiteTestCase, FormTestMixin):
    """Test newsletter signup view."""

    def test_newsletter_signup_success(self):
        """Test successful newsletter signup."""
        data = self.create_test_newsletter_data()

        response = self.submit_form("/newsletter/signup/", data, follow=False)

        # Should redirect back
        self.assertEqual(response.status_code, 302)

        # Check ticket was created
        ticket = SupportTicket.objects.first()
        self.assertIsNotNone(ticket)
        self.assertEqual(ticket.email, "newsletter@example.com")
        self.assertEqual(ticket.subject, "Newsletter Signup")
        self.assertEqual(ticket.status, "resolved")

    def test_newsletter_signup_invalid_email(self):
        """Test newsletter signup with invalid email."""
        data = {
            "email": "not-an-email",
            "consent": True,
        }

        response = self.submit_form("/newsletter/signup/", data, follow=False)

        # Should redirect back but no ticket created
        self.assertEqual(response.status_code, 302)
        self.assertEqual(SupportTicket.objects.count(), 0)

    def test_newsletter_signup_honeypot(self):
        """Test newsletter honeypot protection."""
        data = self.create_test_newsletter_data()
        data["honeypot"] = "spam"

        response = self.submit_form("/newsletter/signup/", data, follow=False)

        # Should redirect but no ticket
        self.assertEqual(response.status_code, 302)
        self.assertEqual(SupportTicket.objects.count(), 0)

    def test_newsletter_creates_crm_contact(self):
        """Test newsletter signup creates CRM contact when available."""
        # Mock the CRM module import
        mock_contact_class = Mock()
        mock_contact_instance = Mock()
        mock_contact_class.objects.get_or_create.return_value = (
            mock_contact_instance,
            True,
        )

        with patch.dict(
            "sys.modules",
            {
                "crm": Mock(),
                "crm.models": Mock(Contact=mock_contact_class),
                "crm.models.choices": Mock(ContactType=Mock(), ContactStatus=Mock()),
            },
        ):
            data = self.create_test_newsletter_data()
            response = self.submit_form("/newsletter/signup/", data, follow=False)

        # Should create contact
        mock_contact_class.objects.get_or_create.assert_called_once()
        call_kwargs = mock_contact_class.objects.get_or_create.call_args[1]
        self.assertEqual(call_kwargs["email"], "newsletter@example.com")
        self.assertTrue(call_kwargs["defaults"]["opt_in_marketing"])


@override_settings(TESTING=True)
class OnboardingFormViewTest(BasePublicSiteTestCase, FormTestMixin):
    """Test onboarding form submission view."""

    def create_test_onboarding_data(self):
        """Create test data for onboarding form that matches actual form structure."""
        return {
            # Section 1: About You
            "email": "test@example.com",
            "legal_name": "John Doe",
            "preferred_name_choice": "nope",
            "pronouns": "he/him",
            "mailing_address": "123 Main St, San Francisco, CA 94102",
            "phone": "+1 555-0123",
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

    def test_onboarding_form_success(self):
        """Test successful onboarding form submission."""
        data = self.create_test_onboarding_data()

        response = self.submit_form("/onboarding/submit/", data, follow=False)

        # Should redirect to thank you page
        self.assert_redirect(response, "/onboarding/thank-you/")

        # Check ticket was created
        ticket = SupportTicket.objects.first()
        self.assertIsNotNone(ticket)
        self.assertEqual(ticket.name, "John Doe")
        self.assertEqual(ticket.email, "test@example.com")
        self.assertEqual(ticket.ticket_type, "onboarding")
        self.assertEqual(ticket.status, "new")
        self.assertIn("Onboarding Application", ticket.subject)

    def test_onboarding_form_validation(self):
        """Test onboarding form validation."""
        data = self.create_test_onboarding_data()
        data["email"] = "invalid-email"  # Invalid email

        response = self.submit_form("/onboarding/submit/", data, follow=False)

        # Should redirect back with errors
        self.assert_redirect(response, "/onboarding/")
        self.assertEqual(SupportTicket.objects.count(), 0)

    def test_onboarding_form_with_co_client(self):
        """Test onboarding form submission with co-client."""
        data = self.create_test_onboarding_data()
        data.update({
            "add_co_client": "yes",
            "co_client_legal_name": "Jane Doe",
            "co_client_call_them": "that",
            "co_client_email": "jane@example.com",
            "co_client_pronouns": "she/her",
            "co_client_phone": "+1 555-0456",
            "co_client_birthday": "1992-05-15",
            "co_client_employment_status": "part_time",
            "co_client_employer_name": "Freelance Design",
            "co_client_share_address": "yes",
        })

        response = self.submit_form("/onboarding/submit/", data, follow=False)

        # Should redirect to thank you page
        self.assert_redirect(response, "/onboarding/thank-you/")

        # Check ticket includes co-client information
        ticket = SupportTicket.objects.first()
        self.assertIsNotNone(ticket)
        self.assertIn("Co-Client Information", ticket.message)
        self.assertIn("Jane Doe", ticket.message)

    def test_onboarding_form_honeypot_protection(self):
        """Test onboarding form honeypot protection."""
        data = self.create_test_onboarding_data()
        data["honeypot"] = "spam content"

        response = self.submit_form("/onboarding/submit/", data, follow=False)

        # Should redirect back
        self.assert_redirect(response, "/onboarding/")
        self.assertEqual(SupportTicket.objects.count(), 0)

    def test_onboarding_form_htmx_request(self):
        """Test onboarding form HTMX request handling."""
        data = self.create_test_onboarding_data()

        response = self.client.post(
            "/onboarding/submit/",
            data,
            HTTP_HX_REQUEST="true"
        )

        # Should return template response instead of redirect
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Thank you for your application!")

    def test_onboarding_thank_you_page(self):
        """Test onboarding thank you page."""
        response = self.client.get("/onboarding/thank-you/")

        self.assertEqual(response.status_code, 200)
        # Check that the page loads without errors
        self.assertContains(response, "Thank")


@override_settings(TESTING=True)
class ContactAPIViewTest(BasePublicSiteTestCase, APITestMixin):
    """Test contact form API endpoint."""

    def test_contact_api_success(self):
        """Test successful API contact submission."""
        data = {
            "name": "API Test User",
            "email": "api@example.com",
            "company": "API Company",
            "subject": "general",
            "message": "This is a test message from the API endpoint.",
        }

        response = self.post_json("/api/contact/", data)

        result = self.assert_api_success(response, 201)
        self.assertIn("ticket_id", result)

        # Check ticket was created
        ticket = SupportTicket.objects.get(id=result["ticket_id"])
        self.assertEqual(ticket.email, "api@example.com")
        self.assertEqual(ticket.name, "API Test User")

    def test_contact_api_validation(self):
        """Test API contact form validation."""
        data = {
            "name": "Test",
            "email": "invalid",  # Invalid email
            "message": "Short",  # Too short
        }

        response = self.post_json("/api/contact/", data)

        result = self.assert_api_error(response, 400)
        self.assertIn("errors", result)
        self.assertIn("email", result["errors"])

    def test_contact_api_invalid_json(self):
        """Test API with invalid JSON."""
        response = self.client.post(
            "/api/contact/", data="invalid json", content_type="application/json"
        )

        self.assertEqual(response.status_code, 400)
        result = json.loads(response.content)
        self.assertFalse(result["success"])

    def test_contact_api_spam_protection(self):
        """Test API spam protection is handled."""
        data = {
            "name": "Test User",
            "email": "test@example.com",
            "subject": "general",
            "message": "Valid message with sufficient length for testing.",
            # Note: human_check is auto-added for API
        }

        response = self.post_json("/api/contact/", data)

        # Should succeed (API adds default human_check)
        self.assert_api_success(response, 201)


@override_settings(TESTING=True)
class NewsletterAPIViewTest(BasePublicSiteTestCase, APITestMixin):
    """Test newsletter API endpoint."""

    def test_newsletter_api_success(self):
        """Test successful newsletter API signup."""
        data = {
            "email": "newsletter-api@example.com",
            "consent": True,
        }

        response = self.post_json("/api/newsletter/", data)

        result = self.assert_api_success(response, 201)

        # Check ticket was created
        ticket = SupportTicket.objects.first()
        self.assertEqual(ticket.email, "newsletter-api@example.com")
        self.assertEqual(ticket.status, "resolved")

    def test_newsletter_api_invalid_email(self):
        """Test newsletter API with invalid email."""
        data = {
            "email": "not-an-email",
            "consent": True,
        }

        response = self.post_json("/api/newsletter/", data)

        result = self.assert_api_error(response, 400)
        self.assertIn("errors", result)
        self.assertIn("email", result["errors"])


@override_settings(TESTING=True)
class SiteStatusAPITest(BasePublicSiteTestCase, APITestMixin):
    """Test site status API endpoint."""

    def test_site_status_healthy(self):
        """Test site status returns healthy."""
        response = self.client.get("/api/status/")

        result = self.assert_api_success(response)
        self.assertEqual(result["status"], "healthy")
        self.assertEqual(result["database"], "connected")
        self.assertIn("support_tickets", result)
        self.assertIn("timestamp", result)

    def test_site_status_with_tickets(self):
        """Test site status includes ticket counts."""
        # Create some tickets
        SupportTicket.objects.create(
            name="Test User",
            email="test@example.com",
            subject="Test",
            message="Test message",
            status="open",
        )
        SupportTicket.objects.create(
            name="Test2 User2",
            email="test2@example.com",
            subject="Test2",
            message="Test message 2",
            status="resolved",
        )

        response = self.client.get("/api/status/")

        result = self.assert_api_success(response)
        self.assertEqual(result["support_tickets"]["total"], 2)
        self.assertEqual(result["support_tickets"]["open"], 1)
        self.assertEqual(result["support_tickets"]["resolved"], 1)


@override_settings(TESTING=True)
class NavigationAPITest(BasePublicSiteTestCase, APITestMixin):
    """Test navigation API endpoints."""

    def test_get_site_navigation(self):
        """Test site navigation API."""
        response = self.client.get("/api/navigation/")

        result = self.assert_api_success(response)
        self.assertIn("navigation", result)

        # Check navigation items
        nav_items = result["navigation"]
        self.assertIsInstance(nav_items, list)
        self.assertGreater(len(nav_items), 0)

        # Check navigation structure
        for item in nav_items:
            self.assertIn("title", item)
            self.assertIn("url", item)
            self.assertIn("slug", item)

    def test_get_footer_links(self):
        """Test footer links API."""
        response = self.client.get("/api/footer-links/")

        result = self.assert_api_success(response)

        # Check footer sections
        self.assertIn("company", result)
        self.assertIn("services", result)
        self.assertIn("legal", result)
        self.assertIn("connect", result)

        # Check link structure
        for section, links in result.items():
            self.assertIsInstance(links, list)
            for link in links:
                self.assertIn("title", link)
                self.assertIn("url", link)


@override_settings(TESTING=True)
class GardenPlatformViewTest(BasePublicSiteTestCase, APITestMixin):
    """Test Garden platform views."""

    def test_garden_overview_page(self):
        """Test Garden platform overview page."""
        response = self.client.get("/garden/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("garden_features", response.context)
        self.assertIn("platform_login_url", response.context)

        # Check features
        features = response.context["garden_features"]
        self.assertEqual(len(features), 6)

        # Check feature structure
        for feature in features:
            self.assertIn("title", feature)
            self.assertIn("icon", feature)
            self.assertIn("description", feature)
            self.assertIn("highlights", feature)
            self.assertEqual(len(feature["highlights"]), 5)

    def test_garden_interest_registration_success(self):
        """Test Garden platform interest registration."""
        data = {
            "name": "Test Adviser",
            "email": "adviser@ria.com",
            "company": "Test RIA",
            "role": "Chief Investment Officer",
            "interest_areas": ["research", "compliance"],
            "message": "Interested in learning more about Garden platform.",
        }

        response = self.post_json("/api/garden/interest/", data)

        result = self.assert_api_success(response, 201)

        # Check ticket was created
        ticket = SupportTicket.objects.first()
        self.assertEqual(ticket.name, "Test Adviser")
        self.assertEqual(ticket.ticket_type, "garden_interest")
        self.assertIn("Chief Investment Officer", ticket.subject)

    def test_garden_interest_validation(self):
        """Test Garden interest form validation."""
        data = {
            "name": "",  # Missing name
            "email": "invalid",  # Invalid email
        }

        response = self.post_json("/api/garden/interest/", data)

        result = self.assert_api_error(response, 400)
        self.assertIn("error", result)


@override_settings(TESTING=True)
class MediaItemsAPITest(BasePublicSiteTestCase, APITestMixin):
    """Test media items API endpoint."""

    def setUp(self):
        super().setUp()
        # Create test media items
        # Get root page
        from wagtail.models import Page

        from public_site.models import MediaPage

        try:
            root = Page.objects.get(depth=1)
        except Page.DoesNotExist:
            self.skipTest("No Wagtail root page - skipping media items test")

        # Create media page properly as a child of root
        self.media_page = MediaPage(
            title="Media",
            slug="media",
        )
        root.add_child(instance=self.media_page)

        # Create media items
        for i in range(10):
            from public_site.models import MediaItem

            MediaItem.objects.create(
                page=self.media_page,
                title=f"Media Item {i+1}",
                description=f"<p>Description {i+1}</p>",
                publication=f"Publication {i+1}",
                publication_date=timezone.now().date() - timezone.timedelta(days=i),
                external_url=f"https://example.com/article-{i+1}",
                featured=(i == 0),
                sort_order=i,
            )

    def test_media_items_pagination(self):
        """Test media items API pagination."""
        response = self.client.get("/api/media-items/?page=1&per_page=5")

        result = self.assert_api_success(response)
        self.assertEqual(len(result["items"]), 5)
        self.assertTrue(result["has_next"])
        self.assertEqual(result["total_pages"], 2)
        self.assertEqual(result["current_page"], 1)
        self.assertEqual(result["total_items"], 10)

    def test_media_items_featured_first(self):
        """Test media items returns featured items first."""
        response = self.client.get("/api/media-items/?page=1&per_page=10")

        result = self.assert_api_success(response)
        # First item should be featured
        self.assertTrue(result["items"][0]["featured"])

    def test_media_items_invalid_page(self):
        """Test media items with invalid page number."""
        response = self.client.get("/api/media-items/?page=100&per_page=5")

        result = self.assert_api_success(response)
        self.assertEqual(len(result["items"]), 0)
        self.assertFalse(result["has_next"])
