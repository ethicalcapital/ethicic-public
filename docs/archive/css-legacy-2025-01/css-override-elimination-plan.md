# CSS Override Elimination Plan

## Overview
This plan outlines how to integrate fixes from 22 override CSS files back into the core Garden UI components, eliminating the need for override files.

## Phase 1: Fix Core Theme Issues (Priority: Critical)

### 1.1 Update garden-ui-theme.css
**Override files to eliminate:**
- button-contrast-fixes.css
- z-contact-emergency-fix.css
- z-final-button-contrast-fix.css
- button-on-color-fix.css

**Changes needed:**
```css
/* Replace all hardcoded colors with theme variables */
/* OLD: background-color: white; */
/* NEW: background-color: var(--garden-bg); */

/* Add missing theme variables */
--garden-button-bg: var(--garden-bg);
--garden-button-fg: var(--garden-fg);
--garden-button-border: var(--garden-border);
--garden-input-bg: var(--garden-bg);
--garden-input-fg: var(--garden-fg);
--garden-input-border: var(--garden-border);

/* Add component state variables */
--garden-button-hover-bg: var(--garden-surface);
--garden-button-disabled-opacity: 0.6;
```

### 1.2 Create Component Variants
**New CSS classes to add:**
```css
/* Button variants */
.garden-button--on-color {
  background-color: var(--garden-bg);
  color: var(--garden-accent);
  border-color: var(--garden-bg);
}

.garden-button--header {
  background-color: var(--garden-accent);
  color: var(--garden-bg);
}

.garden-button--secondary {
  background-color: transparent;
  color: var(--garden-fg);
  border-color: var(--garden-border);
}
```

## Phase 2: Fix Layout System (Priority: High)

### 2.1 Update Layout Components
**Override files to eliminate:**
- critical-page-overrides.css
- page-specific-overrides.css
- public-site-layout-fixes.css
- critical-fixes.css

**Changes needed:**
```css
/* Add layout utilities to garden-ui-utilities.css */
.garden-container {
  width: 100%;
  max-width: var(--garden-container-max-width, 1200px);
  margin: 0 auto;
  padding: 0 var(--garden-gutter);
}

.garden-container--narrow {
  --garden-container-max-width: 800px;
}

.garden-container--wide {
  --garden-container-max-width: 1400px;
}

/* Fix panel components */
.garden-panel {
  width: 100%;
  overflow: hidden; /* Prevent content overflow */
}

.garden-panel__content {
  width: 100%;
  box-sizing: border-box;
}
```

## Phase 3: Fix Form Components (Priority: High)

### 3.1 Create garden-forms.css
**Override files to eliminate:**
- contact-page-fixes.css
- form-input-fixes.css

**New component file:**
```css
/* garden-forms.css */
@layer components {
  .garden-form-input {
    background-color: var(--garden-input-bg);
    color: var(--garden-input-fg);
    border: 1px solid var(--garden-input-border);
    padding: var(--space-2) var(--space-3);
    border-radius: var(--radius-sm);
    width: 100%;
    transition: all var(--duration-fast);
  }

  .garden-form-input:focus {
    outline: 2px solid var(--garden-accent);
    outline-offset: 2px;
  }

  /* Dark mode support */
  [data-theme="dark"] .garden-form-input {
    background-color: var(--garden-surface);
    color: var(--garden-fg);
  }
}
```

## Phase 4: Fix Mobile Components (Priority: High)

### 4.1 Update Mobile Navigation
**Override files to eliminate:**
- mobile-menu-override.css

**Changes to garden-header.css:**
```css
/* Mobile-first approach */
.garden-nav {
  display: none;
}

@media (max-width: 768px) {
  .garden-nav--mobile {
    display: block;
    position: fixed;
    top: var(--header-height);
    left: 0;
    right: 0;
    background-color: var(--garden-bg);
    transform: translateX(-100%);
    transition: transform var(--duration-normal);
  }

  .garden-nav--mobile.is-open {
    transform: translateX(0);
  }

  .garden-hamburger {
    display: block;
  }
}

@media (min-width: 769px) {
  .garden-nav {
    display: flex;
  }

  .garden-hamburger {
    display: none;
  }
}
```

## Phase 5: Fix Component-Specific Issues (Priority: Medium)

### 5.1 Update Blog Components
**Override files to eliminate:**
- blog-formatting-fixes.css
- blog-button-fixes.css
- blog-nuclear-button-fix.css

### 5.2 Update Page Components
**Override files to eliminate:**
- faq-page-fixes.css
- about-page-fix.css
- pricing-features-fix.css

## Phase 6: Consolidate Critical CSS (Priority: Medium)

### 6.1 Create garden-critical.css
**Override files to eliminate:**
- critical-fouc-prevention.css

**New approach:**
- Extract truly critical styles
- Load inline in <head>
- Use CSS layers properly

## Implementation Strategy

### Step 1: Create Test Environment
1. Set up staging environment
2. Create visual regression tests
3. Document current behavior

### Step 2: Implement Changes Incrementally
1. Start with Phase 1 (theme fixes)
2. Test each change thoroughly
3. Move to next phase only after validation

### Step 3: Migration Process
1. Update core Garden UI component
2. Test on all affected pages
3. Remove corresponding override file
4. Verify no visual regressions

### Step 4: Clean Up
1. Remove all override files
2. Update CSS loading order
3. Optimize final CSS bundle

## Success Metrics
- Zero override CSS files
- Reduced CSS file size by ~40%
- Improved maintainability
- Consistent styling across all pages
- No visual regressions

## Risk Mitigation
- Keep override files during transition
- Test on all device sizes
- Validate accessibility compliance
- Monitor performance metrics
- Have rollback plan ready
