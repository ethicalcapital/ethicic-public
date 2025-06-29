# Public Site Test Suite

Comprehensive test coverage for the Ethical Capital public website.

## Test Structure

```
public_site/tests/
├── __init__.py
├── test_base.py          # Base test classes and utilities
├── models/               # Model tests
│   └── test_page_models.py
├── views/                # View tests
│   └── test_form_views.py
├── forms/                # Form tests
│   └── test_contact_forms.py
├── integration/          # Integration tests
│   └── test_user_flows.py
├── test_urls.py          # URL routing tests
└── run_tests.sh          # Test runner script
```

## Running Tests

### Run All Tests
```bash
# Using the test runner script
./public_site/tests/run_tests.sh

# Or directly with Django
docker exec garden-platform python manage.py test public_site.tests
```

### Run Specific Test Modules
```bash
# Model tests only
docker exec garden-platform python manage.py test public_site.tests.models

# Form tests only
docker exec garden-platform python manage.py test public_site.tests.forms

# View tests only
docker exec garden-platform python manage.py test public_site.tests.views

# Integration tests only
docker exec garden-platform python manage.py test public_site.tests.integration

# URL tests only
docker exec garden-platform python manage.py test public_site.tests.test_urls
```

### Run with Coverage
```bash
# Run with coverage report
docker exec garden-platform coverage run --source='public_site' manage.py test public_site.tests
docker exec garden-platform coverage report -m

# Generate HTML coverage report
docker exec garden-platform coverage html
```

## Test Categories

### Model Tests (`models/`)
- **Page Models**: Tests for all Wagtail page models (HomePage, BlogPost, etc.)
- **Support Models**: Tests for SupportTicket and related models
- **Validation**: Field validation, model methods, and meta options

### Form Tests (`forms/`)
- **Contact Forms**: AccessibleContactForm validation and spam protection
- **Newsletter Form**: Newsletter signup form tests
- **Onboarding Form**: Comprehensive onboarding form validation
- **Specialized Forms**: Adviser and Institutional contact forms

### View Tests (`views/`)
- **Form Submissions**: Contact, newsletter, and onboarding submission views
- **API Endpoints**: REST API endpoint tests
- **Garden Platform**: Garden overview and interest registration
- **Error Handling**: 404, 500, and validation error handling

### URL Tests (`test_urls.py`)
- **URL Patterns**: Verify all URLs resolve correctly
- **URL Names**: Test reverse URL lookups
- **Access Control**: Test public vs authenticated access
- **Parameters**: Query parameter handling

### Integration Tests (`integration/`)
- **User Flows**: Complete end-to-end user journeys
- **Contact Flow**: From form submission to ticket creation
- **Newsletter Flow**: Subscription process
- **Onboarding Flow**: Client onboarding journey
- **API Integration**: External API usage flows
- **Error Scenarios**: Spam detection, rate limiting, etc.

## Test Utilities

### Base Test Classes

#### `BasePublicSiteTestCase`
- Common setup for public site tests
- Test data creation helpers
- Form assertion utilities

#### `WagtailPublicSiteTestCase`
- Wagtail-specific test setup
- Page creation helpers
- Site structure utilities

#### `APITestMixin`
- JSON request/response helpers
- API assertion utilities

#### `FormTestMixin`
- Form submission helpers
- Validation assertion utilities

### Test Data Helpers

```python
# Create test contact form data
contact_data = self.create_test_contact_data()

# Create test onboarding data
onboarding_data = self.create_test_onboarding_data()

# Create test newsletter data
newsletter_data = self.create_test_newsletter_data()
```

### Mock Objects

```python
# Create mock request
from public_site.tests.test_base import MockRequestFactory
mock_request = MockRequestFactory.create_request(
    ip_address='127.0.0.1',
    user_agent='Test Browser'
)
```

## Writing New Tests

### Model Test Example
```python
class MyModelTest(WagtailPublicSiteTestCase):
    def test_model_creation(self):
        page = MyPage(title="Test", slug="test")
        self.home_page.add_child(instance=page)
        self.assertEqual(page.title, "Test")
```

### Form Test Example
```python
class MyFormTest(BasePublicSiteTestCase, FormTestMixin):
    def test_form_valid(self):
        data = {'field': 'value'}
        form = MyForm(data=data)
        self.assert_form_valid(form)
```

### View Test Example
```python
class MyViewTest(BasePublicSiteTestCase):
    def test_view_response(self):
        response = self.client.get('/my-url/')
        self.assertEqual(response.status_code, 200)
```

### Integration Test Example
```python
class MyFlowTest(BasePublicSiteTestCase):
    def test_user_flow(self):
        # Step 1: User action
        response = self.client.get('/start/')
        
        # Step 2: Submit form
        data = {'field': 'value'}
        response = self.submit_form('/submit/', data)
        
        # Step 3: Verify outcome
        self.assert_redirect(response, '/success/')
```

## Test Settings

Tests use `TESTING=True` setting to:
- Simplify spam protection validation
- Disable rate limiting
- Use test email backends
- Enable debug mode

## Continuous Integration

The test suite is designed to run in CI/CD pipelines:

```yaml
# Example GitHub Actions
- name: Run Tests
  run: |
    docker compose up -d
    docker exec garden-platform python manage.py test public_site.tests
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all app dependencies are installed
2. **Database Errors**: Tests use transactions, ensure test DB is configured
3. **Wagtail Errors**: Some tests require Wagtail site structure setup
4. **Cache Issues**: Tests clear cache in setUp/tearDown

### Debug Mode

Run tests with higher verbosity:
```bash
docker exec garden-platform python manage.py test public_site.tests --verbosity=3
```

### Specific Test
```bash
docker exec garden-platform python manage.py test public_site.tests.models.test_page_models.HomePageTest.test_homepage_creation
```

## Coverage Goals

- **Target**: 90%+ code coverage
- **Critical Areas**: 
  - Form validation
  - View logic
  - API endpoints
  - User flows

## Contributing

When adding new features:
1. Write tests first (TDD)
2. Ensure all tests pass
3. Maintain or improve coverage
4. Update test documentation