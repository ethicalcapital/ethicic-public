# Inline Style Migration Guide

## Step 2: Migrate Inline Styles to CSS Classes

### Completed Updates

1. **Added comprehensive spacing utilities** to `garden-ui-utilities.css`:
   - Margin utilities: `.mt-0` through `.mt-8`, `.mb-0` through `.mb-8`, `.ml-0` through `.ml-4`, `.mr-0` through `.mr-4`
   - Padding utilities: `.pt-0` through `.pt-8`, `.pb-0` through `.pb-4`
   - Border utilities: `.border-top`, `.border-bottom`, `.border-left`, `.border-right`
   - Visibility utilities: `.hidden`, `.invisible`, `.sr-only`, `.visually-hidden`

2. **Added component layout utilities**:
   - `.garden-nav-divider` - for navigation section dividers
   - `.garden-section-divider` - for general section dividers
   - `.garden-form-section` - for form section spacing

3. **Fixed base template**: Replaced inline style with `.garden-nav-divider` class

### Remaining Inline Styles to Migrate

#### 1. Onboarding Page (`onboarding_page_comprehensive.html`)

**Display toggles for conditional fields:**
```html
<!-- Current -->
<div x-ref="preferredNameField" style="display: none;" class="garden-form-group mt-3">
<div x-ref="pronounsOtherField" style="display: none;" class="garden-form-group mt-3">
<div x-ref="employmentFields" style="display: none;">

<!-- Recommended -->
<div x-ref="preferredNameField" class="garden-form-group mt-3 hidden" :class="{ 'hidden': !showPreferredName }">
<div x-ref="pronounsOtherField" class="garden-form-group mt-3 hidden" :class="{ 'hidden': !showPronounsOther }">
<div x-ref="employmentFields" class="hidden" :class="{ 'hidden': !showEmploymentFields }">
```

**Honeypot field:**
```html
<!-- Current -->
<input type="text" name="honeypot" style="position: absolute; left: -9999px; top: -9999px;" tabindex="-1">

<!-- Recommended -->
<input type="text" name="honeypot" class="visually-hidden" tabindex="-1">
```

**Form sections:**
```html
<!-- Current -->
<div class="garden-form-group" x-show="currentStep === 8" style="margin-bottom: 1rem;">
<section class="garden-panel thank-you-panel" id="thankYouMessage" style="display: none;">

<!-- Recommended -->
<div class="garden-form-group mb-4" x-show="currentStep === 8">
<section class="garden-panel thank-you-panel hidden" id="thankYouMessage">
```

#### 2. Encyclopedia Index (`encyclopedia_index.html`)

**Entry details with inline spacing:**
```html
<!-- Current -->
<div class="entry-details" style="padding-top: var(--space-3, 12px); border-top: 1px solid var(--theme-border); margin-top: var(--space-2, 8px);">
<div style="margin-bottom: var(--space-4, 16px);">
<h4 style="font-size: var(--font-base, 16px); font-weight: var(--font-semibold, 600); margin: 0 0 var(--space-2, 8px) 0; color: var(--theme-on-surface);">

<!-- Recommended -->
<div class="entry-details border-top pt-3 mt-2">
<div class="mb-4">
<h4 class="garden-text-base font-semibold mb-2 text-on-surface">
```

#### 3. Garden Overview (`garden_overview.html`)

**Repository info box:**
```html
<!-- Current -->
<div class="repository-info" style="margin-top: 1.5rem; padding: 1rem; background: var(--color-surface-secondary); border-radius: var(--radius-md); border: 1px solid var(--color-border);">
<p style="margin: 0; color: var(--color-text-secondary);">

<!-- Recommended -->
<div class="repository-info garden-panel mt-6">
<p class="text-secondary mb-0">
```

### Implementation Steps

1. **Create additional utility classes** for text styling:
```css
/* Add to garden-ui-utilities.css */
.text-secondary {
    color: var(--theme-text-secondary);
}

.text-on-surface {
    color: var(--theme-on-surface);
}

.font-semibold {
    font-weight: var(--font-semibold, 600);
}

.garden-text-base {
    font-size: var(--font-base, 16px);
}
```

2. **Update templates** to use utility classes instead of inline styles

3. **Handle dynamic styles** properly with Alpine.js:
   - Use `:class` bindings for conditional visibility
   - Use CSS custom properties for dynamic values
   - Keep JavaScript-driven styles minimal

### Best Practices

- **Spacing**: Use utility classes (`.mt-3`, `.mb-4`, etc.) instead of inline margin/padding
- **Borders**: Use utility classes (`.border-top`, `.border-bottom`) instead of inline borders
- **Display**: Use `.hidden` class with Alpine.js `:class` bindings for conditional visibility
- **Colors**: Use theme variables in CSS classes, not inline styles
- **Typography**: Create utility classes for common text patterns

### Testing

After implementing these changes:
1. Test all form interactions on the onboarding page
2. Verify encyclopedia entries display correctly
3. Check that conditional fields show/hide properly
4. Ensure theme switching works with new utility classes
