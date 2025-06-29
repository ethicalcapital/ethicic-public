#!/usr/bin/env python
import os
import sys
import django

# Add the project root to the path
sys.path.insert(0, '/home/ec1c/ethicic-public')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ethicic.settings')
os.environ['USE_SQLITE'] = 'true'
os.environ['DEBUG'] = 'true'  
os.environ['SECRET_KEY'] = 'test-secret-key-for-local-testing'

django.setup()

from public_site.forms import OnboardingForm

# Test data from the test
data = {
    'first_name': 'Test',
    'last_name': 'User',
    'email': 'onboarding@example.com',
    'phone': '555-123-4567',
    'location': 'New York, NY',
    'initial_investment': '50000',
    'monthly_contribution': '1000',
    'time_horizon': '5-10',
    'accredited_investor': True,
    'primary_goal': 'growth',
    'risk_tolerance': 'moderate',
    'investment_experience': 'intermediate',
    'experience_level': 'intermediate',
    'exclusions': ['fossil_fuels', 'weapons'],
    'impact_areas': ['renewable_energy'],
    'referral_source': 'web_search',
    'additional_notes': 'Test notes',
    'consent': True,
    'agree_terms': True,
    'terms_accepted': True,
    'confirm_accuracy': True,
}

print("Testing OnboardingForm with test data...")
form = OnboardingForm(data)
print(f"Form is valid: {form.is_valid()}")
if not form.is_valid():
    print("Form errors:")
    for field, errors in form.errors.items():
        print(f"  {field}: {errors}")