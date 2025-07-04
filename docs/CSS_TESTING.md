# CSS Testing Infrastructure

Comprehensive testing system for CSS conflict prevention and quality assurance.

## 🧪 Test Suite Overview

### Core Test Files
- **`tests/test_css_conflicts.py`** - Django-based CSS conflict tests
- **`run_css_tests.py`** - Standalone test runner  
- **`css_monitoring.py`** - Monitoring and baseline system

### Test Categories

#### 1. CSS Conflict Tests (`CSSConflictTests`)
```python
# Key tests in the suite:
test_no_undefined_css_variables()     # Ensures all CSS variables are defined
test_conflicting_files_removed()     # Verifies problematic files are removed
test_garden_ui_consistency()         # Validates Garden UI class usage
test_critical_pages_load()          # Tests page loading performance
test_theme_variables_coverage()     # Ensures essential variables exist
test_css_file_count_reasonable()    # Monitors file count for conflicts
test_no_hardcoded_colors()         # Prevents hardcoded color usage
```

#### 2. Performance Tests (`CSSPerformanceTests`)
```python
test_css_file_sizes_reasonable()    # Monitors file size limits (200KB max)
test_theme_loading_performance()    # Ensures fast theme loading (<0.1s)
```

## 🚀 Running Tests

### Quick Commands
```bash
# Run all CSS tests
make css-test

# Check for conflicts only  
make css-check

# Generate detailed report
make css-report

# Standalone test runner
python run_css_tests.py
```

### CI/CD Integration
```bash
# For continuous integration
make ci-css-check
```

## 📊 Test Results & Metrics

### Current Status
- **Tests**: 10 total (CSSConflictTests: 8, CSSPerformanceTests: 2)
- **Success Rate**: 100% (10/10 passing)
- **Coverage**: 44 CSS files, 300+ variables monitored
- **Performance**: All tests complete in ~21 seconds

### Monitored Metrics
- Undefined CSS variables (Target: 0)
- CSS file count (Range: 10-50 files)
- File sizes (Limit: 200KB per file)
- Garden UI adoption rate
- Theme loading performance

## 🔍 Test Details

### Undefined Variable Detection
```python
# Algorithm:
1. Extract all defined variables from garden-ui-theme.css
2. Scan all CSS files for var() usage
3. Flag any used variables not in defined set
4. Report files and specific undefined variables
```

### Garden UI Consistency Check  
```python
# Checks for deprecated classes:
- form-control → garden-input
- btn-primary → garden-action primary  
- form-input → garden-input
```

### Performance Monitoring
```python
# File size limits:
- Individual CSS files: <200KB
- Theme loading time: <0.1 seconds
- Total CSS files: 10-50 reasonable range
```

## 📋 Test Configuration

### Test Settings
```python
# In tests/test_css_conflicts.py
CSS_DIR = "static/css"
THEME_FILE = "garden-ui-theme.css"
MAX_FILE_SIZE = 200 * 1024  # 200KB
MAX_LOAD_TIME = 0.1  # 100ms
```

### Exclusions & Special Cases
```python
# Files excluded from hardcoded color checks:
THEME_FILES = ["garden-ui-theme.css", "core-styles.css"]

# Deprecated classes monitored:
DEPRECATED_CLASSES = ["form-control", "form-input", "btn-primary"]

# Essential variables that must exist:
REQUIRED_VARIABLES = [
    "--theme-primary", "--theme-background", "--garden-accent"
]
```

## 🛠 Test Development

### Adding New Tests
```python
def test_new_css_feature(self):
    """Test description."""
    # 1. Setup test data
    css_files = self._get_css_files()
    
    # 2. Run checks
    issues = self._check_feature(css_files)
    
    # 3. Assert expectations
    self.assertEqual(len(issues), 0, f"Found issues: {issues}")
```

### Test Utilities
```python
# Helper methods available:
self._get_defined_variables()  # Get theme variables
self._analyze_file()          # Analyze single CSS file
self.css_dir                  # CSS directory path
self.theme_file              # Theme file path
```

## 🚨 Troubleshooting Tests

### Common Test Failures

#### Undefined Variables
```
❌ Found 5 undefined variables in 2 files:
  - about-page.css: ['--missing-var']
```
**Fix**: Add missing variables to `garden-ui-theme.css`

#### Deprecated Classes  
```
❌ Found deprecated CSS classes in templates:
  - contact_form.html: ['form-control']
```
**Fix**: Replace with Garden UI classes in templates

#### Performance Issues
```
❌ CSS file too large: theme.css: 250KB
```
**Fix**: Optimize CSS file or split into smaller files

### Test Environment Issues
```bash
# Django settings not configured
export DJANGO_SETTINGS_MODULE=ethicic.settings

# Database connection issues  
python manage.py check

# Missing test dependencies
pip install pytest django
```

## 📈 Continuous Improvement

### Metrics Tracking
The test suite tracks these metrics over time:
- Undefined variable count (trend toward 0)
- File count stability (10-50 range)
- Test execution time (keep under 30s)
- Garden UI adoption rate (trend toward 100%)

### Future Enhancements
- Visual regression testing with screenshots
- CSS validation and linting integration
- Performance budget enforcement
- Automated CSS optimization suggestions

## 🎯 Best Practices

### For Developers
1. **Run tests before committing**: `make css-test`
2. **Check status regularly**: `make css-check`  
3. **Add tests for new features**: Follow existing patterns
4. **Monitor performance**: Keep files under 200KB

### For CI/CD
1. **Run on every PR**: Include in GitHub Actions
2. **Block failing builds**: Don't merge with CSS issues
3. **Generate reports**: Store test artifacts
4. **Track metrics**: Monitor trends over time

---

This testing infrastructure ensures robust CSS quality and prevents regressions as the codebase evolves.