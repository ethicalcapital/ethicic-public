# Onboarding Form Tests

This directory contains comprehensive tests for the OnboardingForm functionality. The tests are organized into multiple files to cover different aspects of the form.

## Test Files

### 1. `test_onboarding_form_comprehensive.py`

The main comprehensive test file containing:

- **OnboardingFormComprehensiveTest**: Detailed unit tests for the OnboardingForm class
- **OnboardingFormViewTest**: Tests for the onboarding form view functionality
- **OnboardingFormHTMXTest**: Tests for HTMX-specific behavior

### 2. `test_contact_forms.py`

Contains basic onboarding form tests alongside other contact form tests:

- **OnboardingFormTest**: Basic form validation tests

### 3. `../integration/test_onboarding_form_integration.py`

Integration tests covering:

- **OnboardingFormIntegrationTest**: End-to-end form processing tests
- **OnboardingFormPerformanceTest**: Performance and load testing

## Test Coverage

### Form Field Testing

- ✅ All form fields and their validation
- ✅ Required field validation
- ✅ Field-specific validation (email, phone, date formats)
- ✅ Field attribute testing (CSS classes, autocomplete, etc.)
- ✅ Choice field validation
- ✅ Multiple choice field handling

### Conditional Field Testing

- ✅ Co-client section shows/hides based on selection
- ✅ Co-client required fields validation
- ✅ Co-client address sharing logic
- ✅ "Other" field requirements (pronouns, preferred name, etc.)
- ✅ Employment status conditional fields
- ✅ Co-client employment conditional fields

### Form Submission Testing

- ✅ Successful form submission
- ✅ Validation error handling
- ✅ Spam protection (honeypot)
- ✅ Email normalization
- ✅ Comprehensive data capture in support tickets

### HTMX Testing

- ✅ HTMX vs regular POST handling
- ✅ HTMX success responses
- ✅ HTMX error handling
- ✅ HTMX server error responses

### Integration Testing

- ✅ Complete onboarding flow (regular POST)
- ✅ Complete onboarding flow (HTMX)
- ✅ Co-client flow integration
- ✅ Multi-step form navigation
- ✅ Error state preservation
- ✅ Concurrent submission handling
- ✅ Performance testing

### Edge Cases

- ✅ Unicode characters in form fields
- ✅ Special characters in text fields
- ✅ Long text field validation
- ✅ Multiple communication preferences
- ✅ Form field order independence
- ✅ Session independence

## Running the Tests

### Run All Onboarding Form Tests

```bash
python manage.py test public_site.tests.forms.test_onboarding_form_comprehensive --settings=ethicic.test_settings_fast
```

### Run Basic Onboarding Tests

```bash
python manage.py test public_site.tests.forms.test_contact_forms.OnboardingFormTest --settings=ethicic.test_settings_fast
```

### Run Integration Tests

```bash
python manage.py test public_site.tests.integration.test_onboarding_form_integration --settings=ethicic.test_settings_fast
```

### Run View Tests

```bash
python manage.py test public_site.tests.views.test_form_views.OnboardingFormViewTest --settings=ethicic.test_settings_fast
```

### Run Specific Test Classes

```bash
# Comprehensive form tests
python manage.py test public_site.tests.forms.test_onboarding_form_comprehensive.OnboardingFormComprehensiveTest --settings=ethicic.test_settings_fast

# HTMX-specific tests
python manage.py test public_site.tests.forms.test_onboarding_form_comprehensive.OnboardingFormHTMXTest --settings=ethicic.test_settings_fast

# Performance tests
python manage.py test public_site.tests.integration.test_onboarding_form_integration.OnboardingFormPerformanceTest --settings=ethicic.test_settings_fast
```

### Run Individual Tests

```bash
# Test co-client conditional behavior
python manage.py test public_site.tests.forms.test_onboarding_form_comprehensive.OnboardingFormComprehensiveTest.test_co_client_conditional_fields_required_when_yes --settings=ethicic.test_settings_fast

# Test HTMX success response
python manage.py test public_site.tests.forms.test_onboarding_form_comprehensive.OnboardingFormHTMXTest.test_onboarding_form_htmx_success --settings=ethicic.test_settings_fast

# Test complete integration flow
python manage.py test public_site.tests.integration.test_onboarding_form_integration.OnboardingFormIntegrationTest.test_complete_onboarding_flow_regular_post --settings=ethicic.test_settings_fast
```

## Test Data Helpers

The tests use several helper methods to create test data:

### `create_complete_onboarding_data()`

Creates a complete set of valid form data with all fields filled.

### `create_co_client_data()`

Creates test data including co-client information.

### `create_minimal_valid_data()`

Creates the minimum required data for a valid form submission.

### `create_basic_onboarding_data()`

Creates basic test data for simple validation tests.

## Test Scenarios Covered

### 1. Valid Form Submissions

- Complete form with all fields
- Minimal required fields only
- Form with co-client information
- Form with "other" field selections
- Form with multiple choice selections

### 2. Validation Scenarios

- Missing required fields
- Invalid field formats (email, phone, date)
- Conditional field validation
- Choice field validation
- Text field length validation

### 3. Conditional Logic

- Co-client section appears when "yes" is selected
- Co-client fields become required
- Co-client address sharing logic
- Employment status conditional fields
- "Other" field requirements

### 4. Security Features

- Honeypot spam protection
- Form field sanitization
- Email normalization

### 5. User Experience

- HTMX vs regular POST handling
- Error message display
- Success response handling
- Multi-step form navigation

### 6. Performance

- Form validation speed
- Form processing time
- Database query optimization

## Maintenance

When adding new fields to the OnboardingForm:

1. Update the test data helper methods
2. Add specific validation tests for new fields
3. Update conditional logic tests if the field affects other fields
4. Add integration tests for the new field's behavior
5. Update this documentation

## Test Quality Standards

All tests should:

- Have descriptive names explaining what they test
- Include docstrings explaining the test purpose
- Use appropriate assertion methods
- Clean up after themselves
- Be independent of other tests
- Cover both success and failure scenarios

## Coverage Goals

The onboarding form tests aim for:

- 100% line coverage of the OnboardingForm class
- 100% branch coverage of conditional logic
- Coverage of all form fields and their validation
- Coverage of all view scenarios (regular POST, HTMX, errors)
- Coverage of all integration scenarios
