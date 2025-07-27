# CSS Architecture Documentation - 2025 Rational System

## Overview

The CSS architecture has been fundamentally restructured from scattered "fix" files to a rational, consolidated system. This document provides comprehensive guidance for all future CSS work.

## Architecture Principles

### 1. **Garden UI First**
- **ALWAYS** use Garden UI theme variables (`var(--color-primary)`, `var(--space-4)`, etc.)
- **NEVER** use hardcoded colors, sizes, or values
- Reference: `static/css/garden-ui-theme.css` (7.5K lines, 300+ variables)

### 2. **CSS Layers Architecture**
```css
@layer base {
  /* Foundation styles, resets, typography */
}

@layer components {
  /* Garden UI components, widgets */
}

@layer accessibility {
  /* WCAG AA compliance, contrast fixes */
}

@layer theme-modes {
  /* Light/dark mode specific styles */
}

@layer utilities {
  /* Helper classes, emergency fixes */
}
```

### 3. **No Specificity Wars**
- Use logical selector specificity, avoid `!important`
- Leverage CSS Layers for cascade management
- Target classes, not IDs (`#main-content` → `.main-content`)

## Consolidated System Architecture

### Current Structure (65% Consolidation Complete)

#### 1. **Layout System**
- **`garden-layout-clean.css`** - Navigation, header, mobile layouts
- **`garden-layout-system.css`** - Homepage, containers, responsive grid
- **Replaces**: header-height-fix.css, page-width-fix.css, mobile-nav-fix.css, responsive-breakpoints-fix.css, fix-white-line.css, public-site-layout-fixes.css, critical-fixes.css

#### 2. **Button System**
- **`garden-buttons-enhanced.css`** - Complete button system with accessibility
- **Replaces**: button-alignment-fix.css, button-contrast-fixes.css, button-on-color-fix.css, header-button-fix.css, cta-button-fixes.css, blog-button-fixes.css

#### 3. **Accessibility System**
- **`garden-accessibility-clean.css`** - WCAG compliance, contrast, tables
- **Replaces**: accessibility-contrast-fixes.css, wcag-contrast-fixes.css, table-contrast-accessibility-fix.css, strategy-table-contrast-fix.css

#### 4. **Forms & Interactive System**
- **`garden-forms-clean.css`** - Forms, dropdowns, interactive elements
- **Replaces**: contact-page-fixes.css, login-dropdown-fix.css, blog-formatting-fixes.css

## Development Workflow

### For New CSS Work

1. **Identify the functional area**: Layout, Buttons, Accessibility, Forms, or Pages
2. **Edit the appropriate consolidated file**:
   - Layout issues → `garden-layout-clean.css` or `garden-layout-system.css`
   - Button issues → `garden-buttons-enhanced.css`
   - Accessibility/contrast → `garden-accessibility-clean.css`
   - Forms/dropdowns → `garden-forms-clean.css`
3. **Use proper CSS Layer**: Add styles to correct `@layer` section
4. **Use Garden UI variables**: Never hardcode values
5. **Test responsively**: Ensure mobile/tablet/desktop compatibility

### For Existing "Fix" Files

**DO NOT** create new fix files. Instead:
1. Identify which consolidated system the fix belongs to
2. Add the fix to the appropriate consolidated file
3. Use proper CSS Layers and Garden UI variables
4. Delete the old fix file after testing

## Template Integration

### Current Template Loading
Templates should load consolidated CSS files:
```html
<!-- Load consolidated systems -->
<link rel="stylesheet" href="{% static 'css/garden-layout-clean.css' %}">
<link rel="stylesheet" href="{% static 'css/garden-layout-system.css' %}">
<link rel="stylesheet" href="{% static 'css/garden-buttons-enhanced.css' %}">
<link rel="stylesheet" href="{% static 'css/garden-accessibility-clean.css' %}">
<link rel="stylesheet" href="{% static 'css/garden-forms-clean.css' %}">
```

### Legacy Template Cleanup
Remove references to old fix files:
- ❌ `header-height-fix.css`, `button-contrast-fixes.css`, etc.
- ✅ Use consolidated files only

## Garden UI Variable Reference

### Colors
```css
/* Primary brand colors */
--color-primary: #3d2970;
--color-primary-hover: #2d1f5a;
--color-on-primary: #ffffff;

/* Surface colors */
--color-surface: var(--theme-surface);
--color-surface-variant: var(--theme-surface-variant);
--color-surface-hover: var(--theme-surface-hover);

/* Text colors */
--color-text-primary: var(--theme-text-primary);
--color-text-secondary: var(--theme-text-secondary);

/* Semantic colors */
--color-success: #16a34a;
--color-error: #dc2626;
--color-warning: #ca8a04;
```

### Spacing
```css
--space-1: 0.25rem;   /* 4px */
--space-2: 0.5rem;    /* 8px */
--space-3: 0.75rem;   /* 12px */
--space-4: 1rem;      /* 16px */
--space-6: 1.5rem;    /* 24px */
--space-8: 2rem;      /* 32px */
--space-12: 3rem;     /* 48px */
--space-16: 4rem;     /* 64px */
```

### Typography
```css
--font-xs: 0.75rem;   /* 12px */
--font-sm: 0.875rem;  /* 14px */
--font-base: 1rem;    /* 16px */
--font-lg: 1.125rem;  /* 18px */
--font-xl: 1.25rem;   /* 20px */
--font-2xl: 1.5rem;   /* 24px */
--font-3xl: 1.875rem; /* 30px */
--font-4xl: 2.25rem;  /* 36px */

--font-normal: 400;
--font-medium: 500;
--font-semibold: 600;
--font-bold: 700;
```

### Breakpoints
```css
/* Mobile first approach */
@media (width >= 768px) { /* Tablet */ }
@media (width >= 1024px) { /* Desktop */ }
@media (width >= 1280px) { /* Large desktop */ }
```

## Accessibility Requirements

### WCAG AA Compliance
- **Contrast ratios**: 4.5:1 minimum for normal text, 3:1 for large text
- **Touch targets**: 44px minimum for interactive elements
- **Focus states**: 2px outline with adequate contrast
- **Color independence**: Never rely on color alone for meaning

### Implementation
```css
/* Good: Uses accessible variables */
.garden-action {
  background: var(--color-primary);
  color: var(--color-on-primary);
  min-height: 44px; /* WCAG touch target */
}

.garden-action:focus-visible {
  outline: 2px solid var(--color-focus);
  outline-offset: 2px;
}
```

## Performance Guidelines

### CSS Loading Strategy
1. **Critical CSS**: Inline essential styles in `<head>`
2. **Component CSS**: Load consolidated files as needed
3. **Page-specific CSS**: Only load for specific pages
4. **Avoid CSS-in-JS**: Use CSS files for better caching

### File Size Targets
- Individual files: < 50KB compressed
- Total CSS payload: < 200KB compressed
- Consolidation reduces HTTP requests by ~65%

## Quality Standards

### Stylelint Compliance
- **No hardcoded colors**: Use Garden UI variables
- **Specificity limits**: Avoid high-specificity selectors
- **Selector patterns**: Use logical, maintainable selectors
- **Color formats**: Use hex shorthand (#fff not #ffffff)

### Code Organization
```css
/* ===== SECTION HEADERS ===== */

/* Component description */
.component-name {
  /* Layout */
  display: flex;

  /* Appearance */
  background: var(--color-surface);

  /* Typography */
  font-size: var(--font-base);

  /* Spacing */
  padding: var(--space-4);

  /* Interaction */
  cursor: pointer;
  transition: all var(--duration-fast) var(--ease-out);
}
```

## Migration Path

### Remaining Work (Phase 2B)
1. **Page-Specific Layouts** → `garden-pages-clean.css`
   - about-page-fix.css, faq-page-fixes.css, pricing-features-fix.css
2. **Content & Typography** → `garden-content-clean.css`
   - blog-post-garden-ui-fix.css, fix-formatting-issues.css
3. **Search & Interactive** → `garden-interactive-clean.css`
   - search-fixes.css, search-visibility-ultimate-fix.css

### Target: 78% Total Reduction
- **Current**: 20+ files → 5 systems (65% reduction)
- **Final**: 32+ files → 7 systems (78% reduction)

## Common Patterns

### Responsive Design
```css
/* Mobile first */
.component {
  padding: var(--space-4);
}

/* Tablet */
@media (width >= 768px) {
  .component {
    padding: var(--space-6);
  }
}

/* Desktop */
@media (width >= 1024px) {
  .component {
    padding: var(--space-8);
  }
}
```

### Theme Support
```css
/* Base styles */
.component {
  background: var(--color-surface);
  color: var(--color-text-primary);
}

/* Dark mode specific (if needed) */
[data-theme="dark"] .component {
  border-color: var(--color-border);
}
```

### Interactive States
```css
.interactive-element {
  transition: all var(--duration-fast) var(--ease-out);
}

.interactive-element:hover {
  background: var(--color-surface-hover);
  transform: translateY(-1px);
}

.interactive-element:focus-visible {
  outline: 2px solid var(--color-focus);
  outline-offset: 2px;
}

.interactive-element:active {
  transform: translateY(0);
}
```

## Troubleshooting

### Common Issues

#### Specificity Conflicts
**Problem**: Styles not applying due to specificity wars
**Solution**: Use CSS Layers, avoid `!important`
```css
/* Wrong */
.component {
  color: red !important;
}

/* Right */
@layer components {
  .component {
    color: var(--color-error);
  }
}
```

#### Theme Variable Issues
**Problem**: Colors not updating with theme changes
**Solution**: Use proper theme variables
```css
/* Wrong */
.component {
  background: #ffffff;
}

/* Right */
.component {
  background: var(--color-surface);
}
```

#### Mobile Layout Issues
**Problem**: Layout breaking on mobile
**Solution**: Use mobile-first responsive design
```css
/* Wrong - desktop first */
@media (max-width: 767px) {
  .component { /* mobile styles */ }
}

/* Right - mobile first */
.component { /* mobile styles */ }

@media (width >= 768px) {
  .component { /* desktop styles */ }
}
```

## Future Development

### Upcoming Features
- **CSS Container Queries**: For component-based responsive design
- **CSS Cascade Layers**: Enhanced with more granular layers
- **CSS Custom Properties**: Dynamic theme variable generation
- **Performance Optimization**: Critical CSS extraction automation

### Maintenance Schedule
- **Weekly**: Stylelint compliance check
- **Monthly**: Consolidated file size audit
- **Quarterly**: Architecture review and optimization

---

**Last Updated**: January 27, 2025
**Version**: 2.0 (Rational Architecture)
**Next Review**: April 2025
