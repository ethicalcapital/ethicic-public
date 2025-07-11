# Development Workflow Guide

Complete workflow guide for developing with the Ethical Capital CSS system and maintaining conflict-free code.

## 🚀 Quick Start Workflow

### Initial Setup
```bash
# 1. Install git hooks
make install-hooks

# 2. Create CSS baseline
make css-baseline

# 3. Verify everything works
make css-check
make css-test
```

### Daily Development
```bash
# Before starting work
make css-status

# While developing
make css-check    # Quick conflict check

# Before committing
make css-test     # Full test suite
git add .
git commit -m "Your changes"  # Pre-commit hook runs automatically
```

## 🎯 Development Patterns

### Adding New CSS

#### 1. Check Existing Variables First
```bash
# Search theme file for existing variables
grep -i "color" static/css/garden-ui-theme.css
grep -i "spacing" static/css/garden-ui-theme.css
```

#### 2. Use Existing Variables
```css
/* ✅ Good - uses theme variables */
.new-component {
  background: var(--theme-surface);
  color: var(--theme-text-primary);
  padding: var(--space-4);
  border-radius: var(--radius-md);
}

/* ❌ Bad - hardcoded values */
.new-component {
  background: #fafafa;
  color: #1a1a1a;
  padding: 16px;
  border-radius: 6px;
}
```

#### 3. Add New Variables if Needed
```css
/* In garden-ui-theme.css */
:root {
  --new-feature-spacing: var(--space-6);
  --new-feature-color: var(--theme-primary);
}

/* Use in your CSS file */
.new-feature {
  margin: var(--new-feature-spacing);
  border-color: var(--new-feature-color);
}
```

### Template Development

#### Use Garden UI Classes
```html
<!-- ✅ Good - Garden UI classes -->
<form class="garden-form">
  <div class="garden-form-group">
    <label class="form-label">Email</label>
    <input type="email" class="garden-input" required>
  </div>
  <button type="submit" class="garden-action primary">Submit</button>
</form>

<!-- ❌ Bad - deprecated classes -->
<form>
  <div class="form-group">
    <label>Email</label>
    <input type="email" class="form-control" required>
  </div>
  <button type="submit" class="btn btn-primary">Submit</button>
</form>
```

#### Garden UI Component Structure
```html
<!-- Panel pattern -->
<section class="garden-panel">
  <div class="garden-panel-header">
    <h2 class="panel-title">Section Title</h2>
  </div>
  <div class="garden-panel-content">
    <!-- Content here -->
  </div>
</section>
```

## 🔍 Testing & Validation

### Before Every Commit
```bash
# 1. Quick conflict check
make css-check

# 2. Full test suite (if time permits)
make css-test

# 3. Git will run pre-commit hook automatically
git commit -m "Your changes"
```

### After Major CSS Changes
```bash
# 1. Run comprehensive tests
make css-test

# 2. Generate detailed report
make css-report

# 3. Update baseline if changes are intentional
make css-baseline

# 4. Verify no regressions
make css-check
```

### Debugging CSS Issues
```bash
# Check for undefined variables
python css_monitoring.py --report | grep "UNDEFINED"

# Find files with issues
python css_monitoring.py --report | grep "FILES WITH ISSUES"

# Get detailed analysis
make css-report
```

## 🚨 Common Issues & Solutions

### Undefined CSS Variable Error
```
❌ Found undefined variables: --missing-color
```

**Solution:**
```css
/* Add to garden-ui-theme.css */
:root {
  --missing-color: var(--theme-primary);
}
```

### Deprecated Class Usage
```
❌ Found deprecated CSS classes: form-control
```

**Solution:**
```html
<!-- Replace deprecated classes -->
<input class="form-control"> → <input class="garden-input">
<button class="btn btn-primary"> → <button class="garden-action primary">
```

### Pre-commit Hook Failure
```
❌ CSS conflict check failed!
```

**Solution:**
```bash
# 1. See what's wrong
make css-report

# 2. Fix the issues (add variables, update classes)

# 3. Verify fix
make css-check

# 4. Retry commit
git commit -m "Your changes"
```

### CSS File Too Large
```
❌ CSS file too large: theme.css: 250KB
```

**Solution:**
```bash
# Split large files or remove unused styles
# Target: <200KB per file
```

## 📋 Code Review Checklist

### For CSS Changes
- [ ] Uses CSS variables instead of hardcoded values
- [ ] No undefined variables (run `make css-check`)
- [ ] File size reasonable (<200KB)
- [ ] Follows Garden UI naming conventions
- [ ] Includes dark mode variants if applicable
- [ ] Accessibility contrast requirements met

### For Template Changes
- [ ] Uses Garden UI classes (`garden-*`)
- [ ] No deprecated classes (`form-control`, `btn-*`)
- [ ] Proper semantic HTML structure
- [ ] ARIA attributes where needed
- [ ] Works in light and dark modes

### For New Features
- [ ] CSS tests pass (`make css-test`)
- [ ] No conflicts detected (`make css-check`)
- [ ] Documentation updated if needed
- [ ] Git hooks working properly

## 🔄 Git Workflow Integration

### Pre-commit Hook Behavior
The installed git hook automatically:
1. **Checks for CSS regressions** against baseline
2. **Validates no undefined variables**
3. **Prevents deprecated class usage**
4. **Warns about excessive hardcoded colors**
5. **Blocks commit if conflicts found**

### Hook Override (Emergency Only)
```bash
# Skip hooks in emergency (use sparingly!)
git commit --no-verify -m "Emergency fix"

# Then immediately fix the issues
make css-check
# Fix problems
git add .
git commit -m "Fix CSS conflicts"
```

### CI/CD Integration
GitHub Actions automatically:
- Runs CSS tests on every push/PR
- Checks template consistency
- Monitors Garden UI adoption
- Generates reports for failures

## 📈 Performance Considerations

### CSS Loading Optimization
```html
<!-- Load critical CSS first -->
<link rel="stylesheet" href="garden-ui-theme.css">
<link rel="stylesheet" href="core-styles.css">

<!-- Conditionally load page-specific CSS -->
{% if page.slug == 'strategies' %}
<link rel="stylesheet" href="strategy-page.css">
{% endif %}
```

### File Size Monitoring
- Keep individual CSS files under **200KB**
- Monitor total CSS payload (**<500KB** target)
- Use CSS layers for cascade control
- Remove unused styles regularly

### Runtime Performance
```css
/* Use efficient selectors */
.garden-panel { } /* ✅ Good */
div.panel.garden { } /* ❌ Bad - too specific */

/* Minimize repaints */
.garden-action {
  transform: translateY(0); /* ✅ GPU accelerated */
  top: 0; /* ❌ Causes layout shifts */
}
```

## 🛠 Tools & Commands Reference

### Essential Commands
```bash
make css-check      # Quick conflict verification
make css-test       # Full test suite (10 tests)
make css-baseline   # Create/update baseline snapshot
make css-report     # Detailed analysis report
make css-status     # Quick status overview
make install-hooks  # Install git pre-commit hooks
```

### Monitoring Scripts
```bash
python css_monitoring.py                    # Quick status
python css_monitoring.py --check           # Check against baseline
python css_monitoring.py --report          # Detailed report
python css_monitoring.py --create-baseline # Create new baseline
```

### Test Runners
```bash
python run_css_tests.py    # Standalone test runner
make ci-css-check          # CI/CD test command
```

## 📚 Learning Resources

### Key Documentation
- [CSS_MAINTENANCE_GUIDE.md](CSS_MAINTENANCE_GUIDE.md) - Complete maintenance system
- [CSS_ARCHITECTURE.md](CSS_ARCHITECTURE.md) - Architecture and design patterns
- [CSS_TESTING.md](CSS_TESTING.md) - Testing infrastructure details

### Garden UI Patterns
- **Panels**: `garden-panel`, `garden-panel-header`, `garden-panel-content`
- **Actions**: `garden-action primary/secondary`, `garden-dropdown`
- **Forms**: `garden-form`, `garden-input`, `garden-form-group`
- **Layout**: `garden-container`, `garden-grid`

### CSS Variable Usage
```css
/* Colors */
var(--theme-primary)
var(--theme-surface)
var(--theme-text-primary)

/* Spacing */
var(--space-4)
var(--space-8)

/* Typography */
var(--font-base)
var(--font-semibold)

/* Borders */
var(--radius-md)
var(--theme-border)
```

---

Following this workflow ensures consistent, conflict-free CSS development that scales with the platform and maintains high quality standards.
