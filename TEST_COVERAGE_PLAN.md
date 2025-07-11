# Test Coverage Plan for 90% Coverage

## Current Status
- **Current Coverage**: ~16% (17 tests, mostly manual verification)
- **Target Coverage**: 90%
- **Gap**: Need comprehensive test suite with ~150-200 tests

## Test Strategy

### 1. Unit Tests (40% of coverage)
#### Models Tests (`tests/test_models.py`)
- **Page Models** (30 tests)
  - HomePage: field validation, method behavior
  - BlogPost: publishing, tagging, author management
  - FAQArticle: category assignment, ordering
  - StrategyPage: performance calculations, holdings management
  - NewsletterPage & AccessibilityPage: basic CRUD

- **Support Models** (10 tests)
  - SupportTicket: status transitions, priority logic
  - ContactSubmission: form data validation

- **Settings Models** (5 tests)
  - SiteSettings: configuration management
  - NavigationMenuItem: ordering, visibility

#### Forms Tests (`tests/test_forms.py`) - 15 tests
- ContactForm: validation rules, human check
- NewsletterForm: email validation
- OnboardingForm: multi-step validation

#### Utils Tests (`tests/test_utils.py`) - 10 tests
- Helper functions
- Data processing utilities
- Email formatting

### 2. View Tests (30% of coverage)
#### Page View Tests (`tests/test_page_views.py`) - 25 tests
- All Wagtail pages return 200
- Context data correctness
- Template usage
- Authentication requirements

#### API View Tests (`tests/test_api_views.py`) - 20 tests
- Contact API: POST validation, success/error responses
- Newsletter API: subscription handling
- Search API: query handling, results format
- Media API: pagination, HTMX responses

#### Form View Tests (`tests/test_form_views.py`) - 15 tests
- Form submission workflows
- Success/error redirects
- HTMX partial responses

### 3. Integration Tests (15% of coverage)
#### Wagtail Integration (`tests/test_wagtail_integration.py`) - 20 tests
- Page hierarchy
- URL routing
- Publishing workflow
- Site management

#### Database Integration (`tests/test_db_integration.py`) - 10 tests
- Migration testing
- Data integrity
- Foreign key relationships

### 4. Template Tests (10% of coverage)
#### Template Rendering (`tests/test_templates.py`) - 20 tests
- All templates render without errors
- Required context variables
- Inheritance chain
- Partial templates

### 5. URL Tests (5% of coverage)
#### URL Resolution (`tests/test_urls.py`) - 10 tests
- All URLs resolve correctly
- Redirects work as expected
- 404/500 error pages

## Implementation Plan

### Phase 1: Foundation (Week 1)
1. Set up test infrastructure
   - Create test directory structure
   - Configure test settings
   - Set up fixtures and factories
   - Create base test classes

2. Implement model tests
   - Start with simple models
   - Add complex model tests
   - Test model methods and properties

### Phase 2: Views & Forms (Week 2)
1. Implement view tests
   - Test all page views
   - Test API endpoints
   - Test form submissions

2. Add form validation tests
   - Test all form fields
   - Test error conditions
   - Test success paths

### Phase 3: Integration & Templates (Week 3)
1. Add integration tests
   - Wagtail page management
   - Database operations
   - Multi-model workflows

2. Template tests
   - Rendering tests
   - Context tests
   - Error template tests

### Phase 4: Edge Cases & Optimization (Week 4)
1. Add edge case tests
   - Boundary conditions
   - Error scenarios
   - Performance tests

2. Optimize test suite
   - Reduce redundancy
   - Improve speed
   - Add CI/CD integration

## Test Infrastructure Needs

### Testing Libraries
```python
# requirements-dev.txt
pytest==7.4.3
pytest-django==4.7.0
pytest-cov==4.1.0
factory-boy==3.3.0
faker==20.1.0
pytest-xdist==3.5.0  # Parallel execution
```

### Test Settings
```python
# ethicic/test_settings.py
from .settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
CELERY_TASK_ALWAYS_EAGER = True
```

### GitHub Actions CI
```yaml
# .github/workflows/tests.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      - name: Run tests
        run: |
          pytest --cov=public_site --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

## Success Metrics
- Line coverage: ≥90%
- Branch coverage: ≥85%
- All critical paths tested
- Test execution time: <5 minutes
- Zero flaky tests

## Example Test Structure
```python
# tests/test_models.py
import pytest
from django.test import TestCase
from wagtail.test.utils import WagtailPageTests
from public_site.models import HomePage, BlogPost

class TestHomePage(WagtailPageTests):
    def test_can_create_homepage(self):
        self.assertCanCreateAt(Page, HomePage)

    def test_homepage_fields(self):
        home = HomePage(
            title="Test Home",
            hero_title="Test Hero"
        )
        self.assertEqual(home.hero_title, "Test Hero")

class TestBlogPost(TestCase):
    def setUp(self):
        self.blog_index = BlogIndexPage.objects.create(
            title="Blog",
            slug="blog"
        )

    def test_blog_post_creation(self):
        post = BlogPost.objects.create(
            title="Test Post",
            slug="test-post",
            author="Test Author"
        )
        self.assertTrue(post.live)
```

## Maintenance Plan
- Run tests on every commit
- Update tests with new features
- Monthly test coverage review
- Quarterly test optimization
- Annual test strategy review
