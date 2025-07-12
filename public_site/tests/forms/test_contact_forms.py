"""
Tests for contact and communication forms in the public site.
"""

import os
import sys

# Import our Wagtail test base
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from django.test import TestCase, override_settings

from public_site.forms import (
    AccessibleContactForm,
    AccessibleNewsletterForm,
    AdviserContactForm,
    InstitutionalContactForm,
    OnboardingForm,
)
from public_site.tests.test_base import (
    BasePublicSiteTestCase,
    FormTestMixin,
    MockRequestFactory,
)


@override_settings(TESTING=True)
class AccessibleContactFormTest(BasePublicSiteTestCase, FormTestMixin):
    """Test AccessibleContactForm."""

    def setUp(self):
        super().setUp()
        self.mock_request = MockRequestFactory.create_request()

    def test_contact_form_valid(self):
        """Test valid contact form submission."""
        data = self.create_test_contact_data()

        form = AccessibleContactForm(data=data, request=self.mock_request)
        self.assert_form_valid(form)

        # Check cleaned data
        self.assertEqual(form.cleaned_data["name"], "Test User")
        self.assertEqual(form.cleaned_data["email"], "test@example.com")
        self.assertEqual(form.cleaned_data["subject"], "general")

    def test_contact_form_required_fields(self):
        """Test contact form required field validation."""
        form = AccessibleContactForm(data={}, request=self.mock_request)

        self.assert_form_invalid(
            form,
            {
                "name": "Please enter your full name",
                "email": "Please provide your email address",
                "subject": "Please select a subject",
                "message": "Please provide a detailed message",
                "human_check": "Please solve the math problem",
            },
        )

    def test_contact_form_email_validation(self):
        """Test email field validation."""
        data = self.create_test_contact_data()
        data["email"] = "invalid-email"

        form = AccessibleContactForm(data=data, request=self.mock_request)
        self.assert_form_invalid(form, {"email": "Please enter a valid email address"})

    def test_contact_form_message_length(self):
        """Test message length validation."""
        data = self.create_test_contact_data()

        # Too short
        data["message"] = "Short"
        form = AccessibleContactForm(data=data, request=self.mock_request)
        self.assert_form_invalid(form, {"message": "at least 10 characters"})

        # Too long
        data["message"] = "x" * 2001
        form = AccessibleContactForm(data=data, request=self.mock_request)
        self.assert_form_invalid(form, {"message": "under 2000 characters"})

    def test_contact_form_honeypot_fields(self):
        """Test honeypot spam protection fields."""
        data = self.create_test_contact_data()

        # Website honeypot filled
        data["website"] = "http://spam.com"
        form = AccessibleContactForm(data=data, request=self.mock_request)
        self.assert_form_invalid(form, {"website": "unusual activity"})

        # Honeypot field filled
        data = self.create_test_contact_data()
        data["honeypot"] = "spam content"
        form = AccessibleContactForm(data=data, request=self.mock_request)
        self.assert_form_invalid(form, {"honeypot": "unusual activity"})

    def test_contact_form_human_check(self):
        """Test human verification field."""
        data = self.create_test_contact_data()

        # Correct answer should pass (in testing mode: 1+1=2)
        data["human_check"] = "2"
        form = AccessibleContactForm(data=data, request=self.mock_request)
        self.assert_form_valid(form)

        # Wrong answer should fail
        data["human_check"] = "5"
        form = AccessibleContactForm(data=data, request=self.mock_request)
        self.assert_form_invalid(
            form, {"human_check": "solve the math problem correctly"}
        )

        # Empty value should fail
        data["human_check"] = ""
        form = AccessibleContactForm(data=data, request=self.mock_request)
        self.assert_form_invalid(form, {"human_check": "Please solve the math problem"})

    def test_contact_form_spam_detection(self):
        """Test spam content detection in message."""
        data = self.create_test_contact_data()

        # Single spam indicator is okay
        data["message"] = "Please click here for more information about our services."
        form = AccessibleContactForm(data=data, request=self.mock_request)
        self.assert_form_valid(form)

        # Multiple spam indicators
        data[
            "message"
        ] = "Click here now! Limited time offer! Make money fast! Buy now!"
        form = AccessibleContactForm(data=data, request=self.mock_request)
        self.assert_form_invalid(form, {"message": "promotional content"})

    def test_contact_form_excessive_urls(self):
        """Test detection of excessive URLs."""
        data = self.create_test_contact_data()

        # Two URLs is okay
        data[
            "message"
        ] = "Check out http://example1.com and http://example2.com for more info."
        form = AccessibleContactForm(data=data, request=self.mock_request)
        self.assert_form_valid(form)

        # More than two URLs
        data[
            "message"
        ] = "Visit http://example1.com, http://example2.com, and http://example3.com"
        form = AccessibleContactForm(data=data, request=self.mock_request)
        self.assert_form_invalid(form, {"message": "limit external links"})

    def test_contact_form_repetition_detection(self):
        """Test detection of excessive word repetition."""
        data = self.create_test_contact_data()

        # Excessive repetition
        data["message"] = "test test test test test test test test test test"
        form = AccessibleContactForm(data=data, request=self.mock_request)
        self.assert_form_invalid(form, {"message": "avoid excessive repetition"})

    def test_contact_form_layout(self):
        """Test form layout and helper configuration."""
        form = AccessibleContactForm(request=self.mock_request)

        # Check form helper attributes
        self.assertEqual(form.helper.form_method, "post")
        self.assertEqual(form.helper.form_action, "/contact/submit/")
        self.assertEqual(form.helper.form_class, "accessible-contact-form")
        self.assertEqual(form.helper.form_id, "contact-form")
        self.assertTrue(form.helper.attrs["novalidate"])
        self.assertEqual(form.helper.attrs["aria-labelledby"], "contact-form-heading")

    def test_contact_form_field_attributes(self):
        """Test form field HTML attributes."""
        form = AccessibleContactForm(request=self.mock_request)

        # Check name field
        name_field = form.fields["name"]
        self.assertEqual(name_field.widget.attrs["placeholder"], "e.g., Jane Smith")
        self.assertEqual(name_field.widget.attrs["autocomplete"], "name")
        self.assertEqual(name_field.widget.attrs["aria-describedby"], "id_name_help")

        # Check email field
        email_field = form.fields["email"]
        self.assertEqual(email_field.widget.attrs["autocomplete"], "email")

        # Check human_check field
        human_field = form.fields["human_check"]
        self.assertEqual(human_field.widget.attrs["inputmode"], "numeric")
        self.assertEqual(human_field.widget.attrs["pattern"], "[0-9]*")


@override_settings(TESTING=True)
class AccessibleNewsletterFormTest(TestCase, FormTestMixin):
    """Test AccessibleNewsletterForm."""

    def test_newsletter_form_valid(self):
        """Test valid newsletter form submission."""
        data = {
            "email": "newsletter@example.com",
            "consent": True,
            "honeypot": "",
        }

        form = AccessibleNewsletterForm(data=data)
        self.assert_form_valid(form)

    def test_newsletter_form_email_required(self):
        """Test email is required."""
        form = AccessibleNewsletterForm(data={})
        self.assert_form_invalid(form, {"email": "required"})

    def test_newsletter_form_consent_optional(self):
        """Test consent is optional in testing."""
        data = {
            "email": "newsletter@example.com",
            "consent": False,
            "honeypot": "",
        }

        form = AccessibleNewsletterForm(data=data)
        self.assert_form_valid(form)

    def test_newsletter_form_honeypot(self):
        """Test honeypot protection."""
        data = {
            "email": "newsletter@example.com",
            "honeypot": "spam",
        }

        form = AccessibleNewsletterForm(data=data)
        self.assert_form_invalid(form, {"honeypot": "unusual activity"})

    def test_newsletter_form_layout(self):
        """Test newsletter form layout."""
        form = AccessibleNewsletterForm()

        self.assertEqual(form.helper.form_action, "/newsletter/signup/")
        self.assertEqual(form.helper.form_class, "newsletter-form")
        self.assertEqual(form.helper.form_id, "newsletter-signup")


@override_settings(TESTING=True)
class OnboardingFormTest(TestCase, FormTestMixin):
    """Test OnboardingForm - basic tests (comprehensive tests in separate file)."""

    def create_basic_onboarding_data(self):
        """Create basic test data for onboarding form."""
        return {
            # Section 1: About You
            "email": "test@example.com",
            "first_name": "John",
            "middle_names": "Michael",
            "last_name": "Doe",
            "preferred_name_choice": "nope",
            "pronouns": "he/him",
            "street_address": "123 Main St",
            "street_address_2": "Apt 4B",
            "city": "San Francisco",
            "state": "CA",
            "zip_code": "94102",
            "country": "United States",
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

    def test_onboarding_form_valid(self):
        """Test valid onboarding form submission."""
        data = self.create_basic_onboarding_data()
        form = OnboardingForm(data=data)
        self.assert_form_valid(form)

    def test_onboarding_form_required_fields(self):
        """Test required field validation."""
        form = OnboardingForm(data={})

        # Check some key required fields
        self.assertFalse(form.is_valid())
        self.assertIn("first_name", form.errors)
        self.assertIn("last_name", form.errors)
        self.assertIn("email", form.errors)
        self.assertIn("street_address", form.errors)
        self.assertIn("city", form.errors)
        self.assertIn("pronouns", form.errors)
        self.assertIn("employment_status", form.errors)

    def test_onboarding_form_honeypot_protection(self):
        """Test honeypot spam protection."""
        data = self.create_basic_onboarding_data()
        data["honeypot"] = "spam content"

        form = OnboardingForm(data=data)
        self.assert_form_invalid(form)
        self.assertIn("unusual activity", str(form.errors))

    def test_onboarding_form_email_normalization(self):
        """Test email normalization."""
        data = self.create_basic_onboarding_data()
        data["email"] = "TEST@EXAMPLE.COM"

        form = OnboardingForm(data=data)
        self.assert_form_valid(form)
        self.assertEqual(form.cleaned_data["email"], "test@example.com")

    def test_onboarding_form_co_client_conditional(self):
        """Test co-client conditional field behavior."""
        data = self.create_basic_onboarding_data()
        data["add_co_client"] = "yes"
        # Don't provide co-client fields

        form = OnboardingForm(data=data)
        self.assert_form_invalid(form)
        self.assertIn("co_client_first_name", form.errors)
        self.assertIn("co_client_last_name", form.errors)
        self.assertIn("co_client_email", form.errors)

    def test_onboarding_form_choice_fields(self):
        """Test form choice field validation."""
        form = OnboardingForm()

        # Check pronoun choices
        pronoun_choices = [choice[0] for choice in form.fields["pronouns"].choices]
        self.assertIn("he/him", pronoun_choices)
        self.assertIn("she/her", pronoun_choices)
        self.assertIn("they/them", pronoun_choices)
        self.assertIn("other", pronoun_choices)

        # Check employment status choices
        employment_choices = [
            choice[0] for choice in form.fields["employment_status"].choices
        ]
        self.assertIn("full_time", employment_choices)
        self.assertIn("part_time", employment_choices)
        self.assertIn("self_employed", employment_choices)
        self.assertIn("retired", employment_choices)

        # Check ethical considerations choices
        ethical_choices = [
            choice[0] for choice in form.fields["ethical_considerations"].choices
        ]
        self.assertIn("environmental_impact", ethical_choices)
        self.assertIn("human_rights", ethical_choices)
        self.assertIn("animal_welfare", ethical_choices)

    def test_onboarding_form_po_box_validation(self):
        """Test that PO Boxes are rejected in street address."""
        data = self.create_basic_onboarding_data()

        # Test various PO Box formats
        po_box_addresses = [
            "P.O. Box 123",
            "PO Box 456",
            "P O BOX 789",
            "POBOX 321",
            "Box 654",
            "PMB 987",
        ]

        for po_address in po_box_addresses:
            with self.subTest(address=po_address):
                data["street_address"] = po_address
                form = OnboardingForm(data=data)
                self.assertFalse(form.is_valid())
                self.assertIn("street_address", form.errors)
                error_text = str(form.errors["street_address"])
                self.assertTrue(
                    "unable to use P.O. boxes" in error_text,
                    f"Expected PO Box error message in: {error_text}"
                )

    def test_onboarding_form_valid_street_address(self):
        """Test that valid street addresses are accepted."""
        data = self.create_basic_onboarding_data()

        valid_addresses = [
            "123 Main Street",
            "456 Oak Avenue Apt 2B",
            "789 First Street Unit 5",
            "321 Elm Drive",
        ]

        for valid_address in valid_addresses:
            with self.subTest(address=valid_address):
                data["street_address"] = valid_address
                form = OnboardingForm(data=data)
                self.assertTrue(
                    form.is_valid(),
                    f"Form should be valid for address: {valid_address}",
                )

    def test_onboarding_form_name_assembly(self):
        """Test that names are properly assembled from components."""
        data = self.create_basic_onboarding_data()
        form = OnboardingForm(data=data)
        self.assertTrue(form.is_valid())

        # The view will assemble the name as "John Michael Doe"
        # We can't test the view logic directly in form tests,
        # but we ensure all name components are present
        self.assertEqual(form.cleaned_data["first_name"], "John")
        self.assertEqual(form.cleaned_data["middle_names"], "Michael")
        self.assertEqual(form.cleaned_data["last_name"], "Doe")


@override_settings(TESTING=True)
class AdviserContactFormTest(TestCase, FormTestMixin):
    """Test AdviserContactForm."""

    def test_adviser_form_valid(self):
        """Test valid adviser contact form."""
        data = {
            "name": "Jane Adviser",
            "email": "jane@ria.com",
            "company": "Test RIA LLC",
            "role": "Chief Investment Officer",
            "assets_under_management": "50m_100m",
            "custodian": "Schwab",
            "inquiry_type": "partnership",
            "message": "Interested in partnering for ethical investment strategies.",
        }

        form = AdviserContactForm(data=data)
        self.assert_form_valid(form)

    def test_adviser_form_required_fields(self):
        """Test adviser form required fields."""
        form = AdviserContactForm(data={})

        self.assert_form_invalid(form)
        self.assertIn("name", form.errors)
        self.assertIn("email", form.errors)
        self.assertIn("company", form.errors)
        self.assertIn("role", form.errors)
        self.assertIn("inquiry_type", form.errors)
        self.assertIn("message", form.errors)

        # Optional fields should not be in errors
        self.assertNotIn("assets_under_management", form.errors)
        self.assertNotIn("custodian", form.errors)

    def test_adviser_form_message_validation(self):
        """Test message length validation."""
        data = {
            "name": "Test",
            "email": "test@ria.com",
            "company": "Test RIA",
            "role": "Adviser",
            "inquiry_type": "general",
            "message": "Short",  # Too short
        }

        form = AdviserContactForm(data=data)
        self.assert_form_invalid(form, {"message": "at least 10"})

    def test_adviser_form_choices(self):
        """Test adviser form choice fields."""
        form = AdviserContactForm()

        # Check AUM choices
        aum_choices = [
            choice[0] for choice in form.fields["assets_under_management"].choices
        ]
        self.assertIn("under_10m", aum_choices)
        self.assertIn("over_1b", aum_choices)

        # Check inquiry type choices
        inquiry_choices = [choice[0] for choice in form.fields["inquiry_type"].choices]
        self.assertIn("partnership", inquiry_choices)
        self.assertIn("strategies", inquiry_choices)
        self.assertIn("compliance", inquiry_choices)


@override_settings(TESTING=True)
class InstitutionalContactFormTest(TestCase, FormTestMixin):
    """Test InstitutionalContactForm."""

    def test_institutional_form_valid(self):
        """Test valid institutional contact form."""
        data = {
            "name": "John Smith",
            "email": "john@university.edu",
            "organization": "Test University Endowment",
            "role": "Chief Investment Officer",
            "institution_type": "endowment",
            "investment_capacity": "250m_500m",
            "inquiry_type": "strategies",
            "message": "Exploring ethical investment options for our endowment.",
        }

        form = InstitutionalContactForm(data=data)
        self.assert_form_valid(form)

    def test_institutional_form_required_fields(self):
        """Test institutional form required fields."""
        form = InstitutionalContactForm(data={})

        self.assert_form_invalid(form)
        self.assertIn("name", form.errors)
        self.assertIn("email", form.errors)
        self.assertIn("organization", form.errors)
        self.assertIn("role", form.errors)
        self.assertIn("institution_type", form.errors)
        self.assertIn("inquiry_type", form.errors)
        self.assertIn("message", form.errors)

        # Investment capacity is optional
        self.assertNotIn("investment_capacity", form.errors)

    def test_institutional_form_choices(self):
        """Test institutional form choice fields."""
        form = InstitutionalContactForm()

        # Check institution type choices
        type_choices = [choice[0] for choice in form.fields["institution_type"].choices]
        self.assertIn("endowment", type_choices)
        self.assertIn("foundation", type_choices)
        self.assertIn("pension", type_choices)
        self.assertIn("university", type_choices)
        self.assertIn("family_office", type_choices)

        # Check investment capacity choices
        capacity_choices = [
            choice[0] for choice in form.fields["investment_capacity"].choices
        ]
        self.assertIn("under_50m", capacity_choices)
        self.assertIn("over_1b", capacity_choices)

    def test_institutional_form_layout(self):
        """Test institutional form layout configuration."""
        form = InstitutionalContactForm()

        self.assertEqual(form.helper.form_action, "/contact/submit/")
        self.assertEqual(form.helper.form_class, "institutional-contact-form")
        self.assertEqual(form.helper.form_id, "institutional-contact-form")
