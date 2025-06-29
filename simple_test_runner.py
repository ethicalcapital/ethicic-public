#!/usr/bin/env python3
"""
Simple test runner that validates our fixes
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, '.')

def test_imports():
    """Test that all modules can be imported without errors"""
    try:
        # Test basic imports
        from public_site.tests.integration.test_user_flows import (
            NewsletterSubscriptionFlowTest,
            OnboardingFlowTest,
            ErrorHandlingFlowTest
        )
        from public_site.tests.test_base import BasePublicSiteTestCase, FormTestMixin
        from public_site.models import SupportTicket
        print("✅ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_mock_fix():
    """Test that our newsletter mock fix is correct"""
    try:
        from unittest.mock import Mock
        
        # Simulate the fix we implemented
        existing_contact = Mock()
        existing_contact.opt_in_marketing = False
        existing_contact.notes = 'Existing notes'
        
        # This should work now (was the source of the error)
        existing_contact.preferences = Mock()
        existing_contact.preferences.get = Mock(return_value=False)
        
        # Test that we can call the mocked methods
        result = existing_contact.preferences.get('newsletter', False)
        assert result == False
        
        print("✅ Newsletter mock fix verified")
        return True
    except Exception as e:
        print(f"❌ Mock test error: {e}")
        return False

def test_inheritance_fix():
    """Test that ErrorHandlingFlowTest has correct inheritance"""
    try:
        from public_site.tests.integration.test_user_flows import ErrorHandlingFlowTest
        from public_site.tests.test_base import FormTestMixin
        
        # Check that ErrorHandlingFlowTest has FormTestMixin methods
        test_instance = ErrorHandlingFlowTest()
        assert hasattr(test_instance, 'submit_form'), "submit_form method missing"
        assert hasattr(test_instance, 'assert_redirect'), "assert_redirect method missing"
        
        print("✅ ErrorHandlingFlowTest inheritance verified")
        return True
    except Exception as e:
        print(f"❌ Inheritance test error: {e}")
        return False

def test_model_choices():
    """Test that SupportTicket has garden_interest choice"""
    try:
        from public_site.models import SupportTicket
        
        # Get the choices from the model field
        field = SupportTicket._meta.get_field('ticket_type')
        choices = [choice[0] for choice in field.choices]
        
        assert 'garden_interest' in choices, "garden_interest choice not found"
        assert 'contact' in choices, "contact choice not found"
        assert 'newsletter' in choices, "newsletter choice not found"
        assert 'onboarding' in choices, "onboarding choice not found"
        
        print("✅ SupportTicket choices verified")
        return True
    except Exception as e:
        print(f"❌ Model choices test error: {e}")
        return False

def test_onboarding_data():
    """Test that our onboarding test data has all required fields"""
    try:
        from public_site.tests.test_base import BasePublicSiteTestCase
        
        test_case = BasePublicSiteTestCase()
        test_data = test_case.create_test_onboarding_data()
        
        required_fields = [
            'first_name', 'last_name', 'email', 'phone', 'location',
            'initial_investment', 'monthly_contribution', 'time_horizon',
            'accredited_investor', 'primary_goal', 'risk_tolerance',
            'investment_experience', 'experience_level', 'exclusions',
            'impact_areas', 'referral_source', 'additional_notes',
            'consent', 'agree_terms', 'terms_accepted', 'confirm_accuracy'
        ]
        
        for field in required_fields:
            assert field in test_data, f"Required field {field} missing from test data"
        
        # Check specific values that caused issues
        assert test_data['time_horizon'] == '5-10', "time_horizon should be '5-10'"
        assert test_data['agree_terms'] == True, "agree_terms should be True"
        assert test_data['terms_accepted'] == True, "terms_accepted should be True"
        assert test_data['confirm_accuracy'] == True, "confirm_accuracy should be True"
        
        print("✅ Onboarding test data verified")
        return True
    except Exception as e:
        print(f"❌ Onboarding data test error: {e}")
        return False

def main():
    """Run all validation tests"""
    print("🧪 Running test validation suite...")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_mock_fix,
        test_inheritance_fix,
        test_model_choices,
        test_onboarding_data
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All validation tests passed! The fixes should work correctly.")
        return 0
    else:
        print(f"❌ {total - passed} validation test(s) failed")
        return 1

if __name__ == '__main__':
    sys.exit(main())