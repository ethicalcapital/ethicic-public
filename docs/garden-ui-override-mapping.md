# Garden UI Component Override Mapping

This document maps which override CSS files are fixing issues in which Garden UI components, showing the specific issues being addressed and the CSS selectors/properties being overridden.

## Overview

The codebase contains numerous CSS override files that fix issues in Garden UI components. These overrides are necessary to address:
- Layout and width constraints
- Color contrast and accessibility issues
- Mobile responsiveness
- Dark mode compatibility
- Component visibility and display issues

## 1. Garden UI Theme Component (`garden-ui-theme.css`)

### Override Files Targeting This Component:

#### `button-contrast-fixes.css`
- **Issues Fixed:**
  - Hardcoded white text colors that don't adapt to themes
  - Poor contrast ratios in dark mode
  - Button state visibility issues
- **Specific Overrides:**
  - `.garden-action` color properties
  - `.garden-action.primary` background and color combinations
  - Dark mode button color inversions
  - Removes hardcoded `color: white` declarations

#### `accessibility-contrast-fixes.css`
- **Issues Fixed:**
  - WCAG contrast ratio failures
  - Theme variable misuse
- **Specific Overrides:**
  - Updates color variables to use proper theme tokens
  - Enforces minimum contrast ratios

## 2. Garden Widgets Component (`garden-widgets.css`)

### Override Files Targeting This Component:

#### `page-specific-overrides.css`
- **Issues Fixed:**
  - Widget container width constraints
  - Widget spacing in different page contexts
- **Specific Overrides:**
  - `.garden-widget` max-width properties
  - Widget grid layouts on specific pages

## 3. Garden Blog Components (`garden-blog*.css`)

### Override Files Targeting This Component:

#### `blog-button-fixes.css`
- **Issues Fixed:**
  - Blog button visibility and contrast
  - Newsletter signup button styling
  - Pagination button states
  - Tag and category link styling
- **Specific Overrides:**
  - `.blog-page .garden-action` visibility and colors
  - `.newsletter-signup .garden-action` background and text colors
  - `.pagination .garden-action` states
  - `.tag-link`, `.category-link` hover states

#### `blog-formatting-fixes.css`
- **Issues Fixed:**
  - Blog content width and spacing
  - Article layout consistency
- **Specific Overrides:**
  - `.blog-article` max-width constraints
  - `.article-content` padding and margins

#### `page-specific-overrides.css`
- **Issues Fixed:**
  - Blog page layout width constraints
  - Article grid responsiveness
- **Specific Overrides:**
  - `.blog-post-page .article-*` max-width properties
  - `.blog-index-page .articles-grid` layout

## 4. Garden Panel Component (implicit in Garden UI)

### Override Files Targeting This Component:

#### `critical-page-overrides.css`
- **Issues Fixed:**
  - Panel content width exceeding container
  - Panel padding and spacing inconsistencies
  - Hero panel centering issues
- **Specific Overrides:**
  - `.garden-panel-content` max-width and margin properties
  - `.panel-content` box-sizing and padding
  - `.hero-panel .panel-content` text alignment

#### `page-specific-overrides.css`
- **Issues Fixed:**
  - Page-specific panel width issues
- **Specific Overrides:**
  - Page-specific `.garden-panel-content` constraints

## 5. Garden Header Component (implicit in Garden UI)

### Override Files Targeting This Component:

#### `header-height-fix.css`
- **Issues Fixed:**
  - Excessive header height
  - Navigation item spacing
  - Login dropdown positioning
  - Search input sizing
  - Dark mode text visibility
- **Specific Overrides:**
  - `.garden-header` padding and min-height
  - `.garden-header-content` flex properties
  - `.garden-nav-item` padding and font-size
  - `.garden-login-dropdown` positioning
  - `.garden-search-input` sizing

#### `header-text-fix.css`
- **Issues Fixed:**
  - Header text color in dark mode
  - Navigation link visibility
- **Specific Overrides:**
  - Dark mode color overrides for nav items
  - Text contrast improvements

#### `login-dropdown-fix.css`
- **Issues Fixed:**
  - Login dropdown expansion within header
  - Dropdown positioning issues
- **Specific Overrides:**
  - `.garden-login-dropdown` position and z-index
  - Dropdown animation and display properties

#### `mobile-menu-override.css`
- **Issues Fixed:**
  - Mobile hamburger menu visibility
  - Mobile navigation display
  - Responsive breakpoint issues
- **Specific Overrides:**
  - `.garden-mobile-menu-toggle` display with high specificity
  - `.garden-nav-main` mobile/desktop display states
  - Mobile menu animation and positioning

## 6. Garden Footer Component (implicit in Garden UI)

### Override Files Targeting This Component:

#### `footer-fix.css`
- **Issues Fixed:**
  - Missing base footer class
  - Footer display and layout issues
  - Skip link accessibility
  - Footer grid responsiveness
- **Specific Overrides:**
  - `.garden-footer` base styles
  - `.garden-footer-grid` display properties
  - `.skip-link` accessibility positioning
  - Footer link colors and hover states

## 7. Garden Search Component (implicit in Garden UI)

### Override Files Targeting This Component:

#### `search-fixes.css`
- **Issues Fixed:**
  - Search input interactivity
  - Search results dropdown positioning
  - Search visibility in header
- **Specific Overrides:**
  - `.garden-search-input` pointer-events and user-select
  - `.garden-search-results` positioning and z-index
  - `.garden-search-container` flex properties

#### `search-visibility-ultimate-fix.css`
- **Issues Fixed:**
  - Search component visibility issues
  - Z-index conflicts
- **Specific Overrides:**
  - Forced visibility with `!important` declarations
  - Z-index hierarchy fixes

## 8. Garden Forms Component (implicit in Garden UI)

### Override Files Targeting This Component:

#### `contact-page-fixes.css`
- **Issues Fixed:**
  - Form field styling in contact forms
  - Form layout and spacing
- **Specific Overrides:**
  - Form input and textarea styling
  - Form container width constraints

## Common Patterns Across Overrides

### 1. Width Constraint Pattern
Most override files include fixes for width constraints:
```css
max-width: var(--content-width-normal);
margin-left: auto;
margin-right: auto;
box-sizing: border-box;
```

### 2. Dark Mode Pattern
Many overrides include dark mode specific fixes:
```css
[data-theme="dark"] .component {
    color: var(--color-text-primary);
    background: var(--color-surface);
}
```

### 3. High Specificity Pattern
Several overrides use excessive specificity to override Garden UI:
```css
html body header.garden-header .garden-header-content .specific-element {
    /* overrides */
}
```

### 4. Accessibility Pattern
Multiple files address contrast and visibility:
```css
@media (prefers-contrast: more) {
    /* high contrast overrides */
}
```

## Recommendations

1. **Consolidate Overrides**: Many override files fix similar issues and could be consolidated
2. **Update Garden UI**: The core Garden UI components should be updated to fix these issues at the source
3. **Reduce Specificity**: The need for high-specificity overrides indicates issues with the base component CSS
4. **Create Utility Classes**: Common patterns like width constraints could be utility classes
5. **Theme Integration**: Better integration of theme variables in base components would reduce contrast fix needs
