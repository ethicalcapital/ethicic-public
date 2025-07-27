# CSS Architecture Overview

**Current as of: July 27, 2025**
**Version: 2.0 (Rational Architecture)**

## Quick Start

### For CSS Changes
1. **Identify functional area**: Layout, Buttons, Accessibility, Forms
2. **Edit appropriate file**:
   - Layout → `garden-layout-clean.css` or `garden-layout-system.css`
   - Buttons → `garden-buttons-enhanced.css`
   - Accessibility → `garden-accessibility-clean.css`
   - Forms → `garden-forms-clean.css`
3. **Use Garden UI variables**: `var(--color-primary)`, `var(--space-4)`, etc.
4. **Never use**: Hardcoded colors, new "fix" files, `!important`

### Documentation
- **Complete Reference**: [`CSS_ARCHITECTURE_CURRENT.md`](./CSS_ARCHITECTURE_CURRENT.md)
- **Implementation Plan**: [`../css-consolidation-plan.md`](../css-consolidation-plan.md)

## Current Architecture (65% Consolidated)

### Consolidated Systems ✅
| File | Purpose | Replaces |
|------|---------|----------|
| `garden-layout-clean.css` | Navigation, header, mobile | 7+ fix files |
| `garden-layout-system.css` | Homepage, containers, grid | 7+ fix files |
| `garden-buttons-enhanced.css` | All button components | 6+ fix files |
| `garden-accessibility-clean.css` | WCAG, contrast, tables | 4+ fix files |
| `garden-forms-clean.css` | Forms, dropdowns, interactive | 3+ fix files |

### Key Principles
- **Garden UI First**: All variables from `garden-ui-theme.css`
- **CSS Layers**: Proper cascade management (`@layer base`, `@layer components`, etc.)
- **No Specificity Wars**: Logical selectors, avoid `!important`
- **Accessibility Built-in**: WCAG AA compliance standard

### What's Left (35%)
- Page-specific layouts (about, FAQ, pricing)
- Content & typography fixes
- Search & interactive components

## Performance Impact
- **HTTP Requests**: 65% reduction (20+ files → 5 files)
- **Maintainability**: Logical organization by function
- **CSS Size**: Consolidated without bloat
- **Developer Experience**: Clear patterns, no guesswork

## Quick Reference

### Common Variables
```css
/* Colors */
--color-primary: #3d2970;
--color-surface: var(--theme-surface);
--color-text-primary: var(--theme-text-primary);

/* Spacing */
--space-4: 1rem;    /* 16px */
--space-6: 1.5rem;  /* 24px */
--space-8: 2rem;    /* 32px */

/* Typography */
--font-base: 1rem;
--font-lg: 1.125rem;
--font-semibold: 600;
```

### CSS Layers
```css
@layer base { /* Foundation */ }
@layer components { /* Garden UI */ }
@layer accessibility { /* WCAG fixes */ }
@layer theme-modes { /* Light/dark */ }
@layer utilities { /* Helpers */ }
```

## Related Documentation
- [`CSS_ARCHITECTURE_CURRENT.md`](./CSS_ARCHITECTURE_CURRENT.md) - Complete technical reference
- [`CSS_LINTING_SETUP.md`](./CSS_LINTING_SETUP.md) - Stylelint configuration
- [`CSS_TESTING.md`](./CSS_TESTING.md) - Testing procedures
- [`POSTCSS_BUILD_PROCESS.md`](./POSTCSS_BUILD_PROCESS.md) - Build system
- [`../css-consolidation-plan.md`](../css-consolidation-plan.md) - Implementation roadmap

## Support
- **Stylelint Issues**: Check [`CSS_LINTING_SETUP.md`](./CSS_LINTING_SETUP.md)
- **Garden UI Variables**: Reference `static/css/garden-ui-theme.css`
- **Architecture Questions**: See [`CSS_ARCHITECTURE_CURRENT.md`](./CSS_ARCHITECTURE_CURRENT.md)
