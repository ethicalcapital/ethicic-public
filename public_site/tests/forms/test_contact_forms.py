"""
Tests for contact and communication forms in the public site.
"""

from django.test import TestCase, override_settings
from django.utils import timezone

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
        self.assertEqual(form.cleaned_data['name'], 'Test User')
        self.assertEqual(form.cleaned_data['email'], 'test@example.com')
        self.assertEqual(form.cleaned_data['subject'], 'general')
    
    def test_contact_form_required_fields(self):
        """Test contact form required field validation."""
        form = AccessibleContactForm(data={}, request=self.mock_request)
        
        self.assert_form_invalid(form, {
            'name': 'Please enter your full name',
            'email': 'Please provide your email address',
            'subject': 'Please select a subject',
            'message': 'Please provide a detailed message',
            'human_check': 'Please solve the math problem',
        })
    
    def test_contact_form_email_validation(self):
        """Test email field validation."""
        data = self.create_test_contact_data()
        data['email'] = 'invalid-email'
        
        form = AccessibleContactForm(data=data, request=self.mock_request)
        self.assert_form_invalid(form, {
            'email': 'Please enter a valid email address'
        })
    
    def test_contact_form_message_length(self):
        """Test message length validation."""
        data = self.create_test_contact_data()
        
        # Too short
        data['message'] = 'Short'
        form = AccessibleContactForm(data=data, request=self.mock_request)
        self.assert_form_invalid(form, {
            'message': 'at least 10 characters'
        })
        
        # Too long
        data['message'] = 'x' * 2001
        form = AccessibleContactForm(data=data, request=self.mock_request)
        self.assert_form_invalid(form, {
            'message': 'under 2000 characters'
        })
    
    def test_contact_form_honeypot_fields(self):
        """Test honeypot spam protection fields."""
        data = self.create_test_contact_data()
        
        # Website honeypot filled
        data['website'] = 'http://spam.com'
        form = AccessibleContactForm(data=data, request=self.mock_request)
        self.assert_form_invalid(form, {
            'website': 'unusual activity'
        })
        
        # Honeypot field filled
        data = self.create_test_contact_data()
        data['honeypot'] = 'spam content'
        form = AccessibleContactForm(data=data, request=self.mock_request)
        self.assert_form_invalid(form, {
            'honeypot': 'unusual activity'
        })
    
    def test_contact_form_human_check(self):
        """Test human verification field."""
        data = self.create_test_contact_data()
        
        # In testing mode, any non-empty value is accepted
        data['human_check'] = 'any value'
        form = AccessibleContactForm(data=data, request=self.mock_request)
        self.assert_form_valid(form)
        
        # Empty value should fail
        data['human_check'] = ''
        form = AccessibleContactForm(data=data, request=self.mock_request)
        self.assert_form_invalid(form, {
            'human_check': 'Please solve the math problem'
        })
    
    def test_contact_form_spam_detection(self):
        """Test spam content detection in message."""
        data = self.create_test_contact_data()
        
        # Single spam indicator is okay
        data['message'] = 'Please click here for more information about our services.'
        form = AccessibleContactForm(data=data, request=self.mock_request)
        self.assert_form_valid(form)
        
        # Multiple spam indicators
        data['message'] = 'Click here now! Limited time offer! Make money fast! Buy now!'
        form = AccessibleContactForm(data=data, request=self.mock_request)
        self.assert_form_invalid(form, {
            'message': 'promotional content'
        })
    
    def test_contact_form_excessive_urls(self):
        """Test detection of excessive URLs."""
        data = self.create_test_contact_data()
        
        # Two URLs is okay
        data['message'] = 'Check out http://example1.com and http://example2.com for more info.'
        form = AccessibleContactForm(data=data, request=self.mock_request)
        self.assert_form_valid(form)
        
        # More than two URLs
        data['message'] = 'Visit http://example1.com, http://example2.com, and http://example3.com'
        form = AccessibleContactForm(data=data, request=self.mock_request)
        self.assert_form_invalid(form, {
            'message': 'limit external links'
        })
    
    def test_contact_form_repetition_detection(self):
        """Test detection of excessive word repetition."""
        data = self.create_test_contact_data()
        
        # Excessive repetition
        data['message'] = 'test test test test test test test test test test'
        form = AccessibleContactForm(data=data, request=self.mock_request)
        self.assert_form_invalid(form, {
            'message': 'avoid excessive repetition'
        })
    
    def test_contact_form_layout(self):
        """Test form layout and helper configuration."""
        form = AccessibleContactForm(request=self.mock_request)
        
        # Check form helper attributes
        self.assertEqual(form.helper.form_method, 'post')
        self.assertEqual(form.helper.form_action, '/contact/submit/')
        self.assertEqual(form.helper.form_class, 'accessible-contact-form')
        self.assertEqual(form.helper.form_id, 'contact-form')
        self.assertTrue(form.helper.attrs['novalidate'])
        self.assertEqual(form.helper.attrs['aria-labelledby'], 'contact-form-heading')
    
    def test_contact_form_field_attributes(self):
        """Test form field HTML attributes."""
        form = AccessibleContactForm(request=self.mock_request)
        
        # Check name field
        name_field = form.fields['name']
        self.assertEqual(name_field.widget.attrs['placeholder'], 'e.g., Jane Smith')
        self.assertEqual(name_field.widget.attrs['autocomplete'], 'name')
        self.assertEqual(name_field.widget.attrs['aria-describedby'], 'id_name_help')
        
        # Check email field
        email_field = form.fields['email']
        self.assertEqual(email_field.widget.attrs['autocomplete'], 'email')
        
        # Check human_check field
        human_field = form.fields['human_check']
        self.assertEqual(human_field.widget.attrs['inputmode'], 'numeric')
        self.assertEqual(human_field.widget.attrs['pattern'], '[0-9]*')


@override_settings(TESTING=True)
class AccessibleNewsletterFormTest(TestCase, FormTestMixin):
    """Test AccessibleNewsletterForm."""
    
    def test_newsletter_form_valid(self):
        """Test valid newsletter form submission."""
        data = {
            'email': 'newsletter@example.com',
            'consent': True,
            'honeypot': '',
        }
        
        form = AccessibleNewsletterForm(data=data)
        self.assert_form_valid(form)
    
    def test_newsletter_form_email_required(self):
        """Test email is required."""
        form = AccessibleNewsletterForm(data={})
        self.assert_form_invalid(form, {
            'email': 'required'
        })
    
    def test_newsletter_form_consent_optional(self):
        """Test consent is optional in testing."""
        data = {
            'email': 'newsletter@example.com',
            'consent': False,
            'honeypot': '',
        }
        
        form = AccessibleNewsletterForm(data=data)
        self.assert_form_valid(form)
    
    def test_newsletter_form_honeypot(self):
        """Test honeypot protection."""
        data = {
            'email': 'newsletter@example.com',
            'honeypot': 'spam',
        }
        
        form = AccessibleNewsletterForm(data=data)
        self.assert_form_invalid(form, {
            'honeypot': 'unusual activity'
        })
    
    def test_newsletter_form_layout(self):
        """Test newsletter form layout."""
        form = AccessibleNewsletterForm()
        
        self.assertEqual(form.helper.form_action, '/newsletter/signup/')
        self.assertEqual(form.helper.form_class, 'newsletter-form')
        self.assertEqual(form.helper.form_id, 'newsletter-signup')


@override_settings(TESTING=True)
class OnboardingFormTest(TestCase, FormTestMixin):
    """Test OnboardingForm."""
    
    def test_onboarding_form_valid(self):
        """Test valid onboarding form submission."""
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'phone': '+1 555-0123',
            'location': 'San Francisco, CA',
            'primary_goal': 'growth',
            'time_horizon': '10+',
            'exclusions': ['fossil_fuels', 'weapons'],
            'impact_areas': ['renewable_energy'],
            'experience_level': 'intermediate',
            'initial_investment': '50000',
            'monthly_contribution': '1000',
            'risk_tolerance': 'moderate',
            'investment_goals': ['growth'],
            'esg_priorities': ['environmental'],
            'investment_timeline': '3_months',
            'accredited_investor': True,
            'agree_terms': True,
            'terms_accepted': True,
            'confirm_accuracy': True,
            'honeypot': '',
        }
        
        form = OnboardingForm(data=data)
        self.assert_form_valid(form)
    
    def test_onboarding_form_required_fields(self):
        """Test required field validation."""
        form = OnboardingForm(data={})
        
        # Check some key required fields
        self.assertFalse(form.is_valid())
        self.assertIn('first_name', form.errors)
        self.assertIn('last_name', form.errors)
        self.assertIn('email', form.errors)
        self.assertIn('location', form.errors)
        self.assertIn('primary_goal', form.errors)
        self.assertIn('time_horizon', form.errors)
        self.assertIn('experience_level', form.errors)
        self.assertIn('initial_investment', form.errors)
        self.assertIn('risk_tolerance', form.errors)
    
    def test_onboarding_minimum_investment(self):
        """Test minimum investment validation."""
        data = {
            'initial_investment': '10000',  # Below $25,000 minimum
        }
        
        form = OnboardingForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('initial_investment', form.errors)
        self.assertIn('Ensure this value is greater than or equal to 25000', str(form.errors['initial_investment']))
    
    def test_onboarding_accredited_investor_required(self):
        """Test accredited investor requirement."""
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'location': 'San Francisco, CA',
            'primary_goal': 'growth',
            'time_horizon': '10+',
            'experience_level': 'intermediate',
            'initial_investment': '50000',
            'risk_tolerance': 'moderate',
            'accredited_investor': False,  # Not accredited
            'terms_accepted': True,
            'confirm_accuracy': True,
            'honeypot': '',
        }
        
        form = OnboardingForm(data=data)
        self.assert_form_invalid(form, {
            'accredited_investor': 'must be an accredited investor'
        })
    
    def test_onboarding_terms_acceptance(self):
        """Test terms acceptance is required."""
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'location': 'San Francisco, CA',
            'primary_goal': 'growth',
            'time_horizon': '10+',
            'experience_level': 'intermediate',
            'initial_investment': '50000',
            'risk_tolerance': 'moderate',
            'accredited_investor': True,
            'agree_terms': True,
            'terms_accepted': False,  # Terms not accepted
            'confirm_accuracy': True,
            'honeypot': '',
        }
        
        form = OnboardingForm(data=data)
        self.assert_form_invalid(form, {
            'terms_accepted': 'must accept the terms'
        })
    
    def test_onboarding_form_choices(self):
        """Test form choice fields."""
        form = OnboardingForm()
        
        # Check primary goal choices
        goal_choices = [choice[0] for choice in form.fields['primary_goal'].choices]
        self.assertIn('growth', goal_choices)
        self.assertIn('income', goal_choices)
        self.assertIn('balanced', goal_choices)
        self.assertIn('preservation', goal_choices)
        
        # Check time horizon choices
        horizon_choices = [choice[0] for choice in form.fields['time_horizon'].choices]
        self.assertIn('1-3', horizon_choices)
        self.assertIn('10+', horizon_choices)
        
        # Check exclusion choices
        exclusion_choices = [choice[0] for choice in form.fields['exclusions'].choices]
        self.assertIn('fossil_fuels', exclusion_choices)
        self.assertIn('weapons', exclusion_choices)
        self.assertIn('human_rights', exclusion_choices)


@override_settings(TESTING=True)
class AdviserContactFormTest(TestCase, FormTestMixin):
    """Test AdviserContactForm."""
    
    def test_adviser_form_valid(self):
        """Test valid adviser contact form."""
        data = {
            'name': 'Jane Adviser',
            'email': 'jane@ria.com',
            'company': 'Test RIA LLC',
            'role': 'Chief Investment Officer',
            'assets_under_management': '50m_100m',
            'custodian': 'Schwab',
            'inquiry_type': 'partnership',
            'message': 'Interested in partnering for ethical investment strategies.',
        }
        
        form = AdviserContactForm(data=data)
        self.assert_form_valid(form)
    
    def test_adviser_form_required_fields(self):
        """Test adviser form required fields."""
        form = AdviserContactForm(data={})
        
        self.assert_form_invalid(form)
        self.assertIn('name', form.errors)
        self.assertIn('email', form.errors)
        self.assertIn('company', form.errors)
        self.assertIn('role', form.errors)
        self.assertIn('inquiry_type', form.errors)
        self.assertIn('message', form.errors)
        
        # Optional fields should not be in errors
        self.assertNotIn('assets_under_management', form.errors)
        self.assertNotIn('custodian', form.errors)
    
    def test_adviser_form_message_validation(self):
        """Test message length validation."""
        data = {
            'name': 'Test',
            'email': 'test@ria.com',
            'company': 'Test RIA',
            'role': 'Adviser',
            'inquiry_type': 'general',
            'message': 'Short',  # Too short
        }
        
        form = AdviserContactForm(data=data)
        self.assert_form_invalid(form, {
            'message': 'at least 10'
        })
    
    def test_adviser_form_choices(self):
        """Test adviser form choice fields."""
        form = AdviserContactForm()
        
        # Check AUM choices
        aum_choices = [choice[0] for choice in form.fields['assets_under_management'].choices]
        self.assertIn('under_10m', aum_choices)
        self.assertIn('over_1b', aum_choices)
        
        # Check inquiry type choices
        inquiry_choices = [choice[0] for choice in form.fields['inquiry_type'].choices]
        self.assertIn('partnership', inquiry_choices)
        self.assertIn('strategies', inquiry_choices)
        self.assertIn('compliance', inquiry_choices)


@override_settings(TESTING=True)
class InstitutionalContactFormTest(TestCase, FormTestMixin):
    """Test InstitutionalContactForm."""
    
    def test_institutional_form_valid(self):
        """Test valid institutional contact form."""
        data = {
            'name': 'John Smith',
            'email': 'john@university.edu',
            'organization': 'Test University Endowment',
            'role': 'Chief Investment Officer',
            'institution_type': 'endowment',
            'investment_capacity': '250m_500m',
            'inquiry_type': 'strategies',
            'message': 'Exploring ethical investment options for our endowment.',
        }
        
        form = InstitutionalContactForm(data=data)
        self.assert_form_valid(form)
    
    def test_institutional_form_required_fields(self):
        """Test institutional form required fields."""
        form = InstitutionalContactForm(data={})
        
        self.assert_form_invalid(form)
        self.assertIn('name', form.errors)
        self.assertIn('email', form.errors)
        self.assertIn('organization', form.errors)
        self.assertIn('role', form.errors)
        self.assertIn('institution_type', form.errors)
        self.assertIn('inquiry_type', form.errors)
        self.assertIn('message', form.errors)
        
        # Investment capacity is optional
        self.assertNotIn('investment_capacity', form.errors)
    
    def test_institutional_form_choices(self):
        """Test institutional form choice fields."""
        form = InstitutionalContactForm()
        
        # Check institution type choices
        type_choices = [choice[0] for choice in form.fields['institution_type'].choices]
        self.assertIn('endowment', type_choices)
        self.assertIn('foundation', type_choices)
        self.assertIn('pension', type_choices)
        self.assertIn('university', type_choices)
        self.assertIn('family_office', type_choices)
        
        # Check investment capacity choices
        capacity_choices = [choice[0] for choice in form.fields['investment_capacity'].choices]
        self.assertIn('under_50m', capacity_choices)
        self.assertIn('over_1b', capacity_choices)
    
    def test_institutional_form_layout(self):
        """Test institutional form layout configuration."""
        form = InstitutionalContactForm()
        
        self.assertEqual(form.helper.form_action, '/contact/submit/')
        self.assertEqual(form.helper.form_class, 'institutional-contact-form')
        self.assertEqual(form.helper.form_id, 'institutional-contact-form')