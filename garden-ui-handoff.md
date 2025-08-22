# Garden UI Shared Design Token Integration Guide

## For the Garden Financial Platform Team

This document provides instructions for integrating the new shared design token system into the Garden Financial Platform.

## What's Been Created

We've extracted core design tokens from the Ethicic Public Site into a shared layer that both sites can use:

1. **`/static/css/shared/garden-brand-tokens.css`**
   - Core brand colors (purple, teal, grays)
   - Spacing scale (4px to 128px)
   - Typography tokens (fonts, sizes, weights)
   - Border radius, shadows, and transitions

2. **`/static/css/shared/garden-component-base.css`**
   - `.garden-action` - Base button component
   - `.garden-panel` - Base card/container component
   - `.garden-input` - Base form input component

## Integration Steps for Garden Platform

### 1. Copy the Shared Files

Copy these files to your Garden platform:
```bash
# From ethicic-public repository
cp static/css/shared/garden-brand-tokens.css [GARDEN_PATH]/static/css/shared/
cp static/css/shared/garden-component-base.css [GARDEN_PATH]/static/css/shared/
cp static/css/shared/README.md [GARDEN_PATH]/static/css/shared/
```

### 2. Import in Your Base Template

Add these imports to your main template or CSS file:
```html
<!-- In your base template -->
<link rel="stylesheet" href="{% static 'css/shared/garden-brand-tokens.css' %}?v=1" />
<link rel="stylesheet" href="{% static 'css/shared/garden-component-base.css' %}?v=1" />
```

Or in your main CSS file:
```css
@import url('shared/garden-brand-tokens.css');
@import url('shared/garden-component-base.css');
```

### 3. Use the Design Tokens

Replace hardcoded values with design tokens:

**Before:**
```css
.my-button {
  background-color: #581c87;
  padding: 8px 16px;
  font-family: Outfit, sans-serif;
}
```

**After:**
```css
.my-button {
  background-color: var(--garden-brand-purple);
  padding: var(--garden-space-2) var(--garden-space-4);
  font-family: var(--garden-brand-font-sans);
}
```

### 4. Extend Base Components

Use the shared component classes as a foundation:

```html
<!-- Use directly -->
<button class="garden-action primary">Save Changes</button>

<!-- Or extend with custom classes -->
<button class="garden-action secondary dashboard-action">Export Data</button>
```

```css
/* Custom extensions */
.dashboard-action {
  /* Inherits all garden-action styles */
  /* Add dashboard-specific styles */
  min-width: 120px;
}
```

## Token Reference

### Primary Colors
- `--garden-brand-purple`: #581c87
- `--garden-brand-purple-hover`: #6b46c1
- `--garden-brand-teal`: #14b8a6
- `--garden-brand-teal-hover`: #0d9488

### Grays (Dark to Light)
- `--garden-brand-gray-900`: #111827
- `--garden-brand-gray-800`: #1f2937
- `--garden-brand-gray-700`: #374151
- `--garden-brand-gray-600`: #4b5563
- `--garden-brand-gray-500`: #6b7280
- `--garden-brand-gray-400`: #9ca3af
- `--garden-brand-gray-300`: #d1d5db
- `--garden-brand-gray-200`: #e5e7eb
- `--garden-brand-gray-100`: #f3f4f6
- `--garden-brand-gray-50`: #f9fafb

### Spacing Scale
- `--garden-space-1`: 4px
- `--garden-space-2`: 8px
- `--garden-space-3`: 12px
- `--garden-space-4`: 16px
- `--garden-space-6`: 24px
- `--garden-space-8`: 32px
- (and more up to space-32)

### Typography
- `--garden-brand-font-sans`: Outfit font stack
- `--garden-brand-font-heading`: Bebas Neue font stack
- `--garden-brand-text-[xs-5xl]`: Font size scale

## Best Practices

1. **Don't modify the shared files** - These should remain identical between both platforms
2. **Use semantic extensions** - Create platform-specific classes that extend the base components
3. **Maintain dark mode support** - Test all customizations in both light and dark modes
4. **Version your imports** - Use cache-busting query parameters (?v=1, ?v=2, etc.)

## Example Implementation

```css
/* garden-platform-overrides.css */

/* Extend the base button for Garden-specific needs */
.garden-action.data-action {
  /* Uses shared tokens */
  background-color: var(--garden-brand-teal);
  font-size: var(--garden-brand-text-xs);
  
  /* Garden-specific additions */
  text-transform: none;
  letter-spacing: normal;
}

/* Create compound components */
.data-panel {
  /* Extend garden-panel */
  @extend .garden-panel;
  
  /* Add data visualization specific styles */
  overflow-x: auto;
  min-height: 400px;
}

/* Platform-specific theme */
.garden-platform-theme {
  /* Override specific tokens for Garden context */
  --garden-brand-purple: #6b46c1; /* Lighter purple for data viz */
}
```

## Benefits

1. **Visual Consistency**: Both sites share the same core brand identity
2. **Independent Evolution**: Each site can still develop unique features
3. **Maintainability**: Update brand colors in one place
4. **Performance**: Shared tokens are lightweight and cached
5. **Flexibility**: Easy to extend without breaking changes

## Questions or Issues?

The shared token system is designed to be additive only. If you need additional tokens or components that should be shared, please coordinate with the Ethicic Public Site team to add them to the shared layer.

## Next Steps

1. Review the current Garden platform styles
2. Identify which hardcoded values can use shared tokens
3. Test the integration in a development environment
4. Gradually migrate to the shared token system
5. Document any platform-specific extensions

The goal is a consistent visual language while maintaining the flexibility for each platform to address its unique needs.