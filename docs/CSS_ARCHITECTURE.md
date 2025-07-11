# CSS Architecture Guide

Comprehensive guide to the Ethical Capital CSS architecture, theme system, and design patterns.

## 🏗 Architecture Overview

### Design System Philosophy
The CSS architecture follows a **Garden UI design system** with these core principles:
- **Single source of truth** for all design tokens
- **CSS variables** for all colors, spacing, and typography
- **Semantic naming** that reflects purpose, not appearance
- **WCAG AAA accessibility** compliance (7:1 contrast ratios)
- **Light/dark mode** support throughout

### File Organization
```
static/css/
├── garden-ui-theme.css          # 🎨 Core theme variables & design tokens
├── high-contrast-mode.css       # ♿ Accessibility enhancements
├── core-styles.css             # 🏗 Base styles & resets
├── public-site-simple.css      # 🌐 Public site specific styles
├── button-contrast-fixes.css   # 🔘 Button theming
└── layers/                     # 📁 Page-specific styles
    ├── 16-homepage.css
    ├── 30-strategy-page.css
    └── ...
```

## 🎨 Theme System

### Core Theme File: `garden-ui-theme.css`
This is the **single source of truth** for all design tokens. Contains 300+ CSS variables.

#### Theme Structure
```css
:root {
  /* 🎯 Core Colors */
  --garden-accent: #3d2970;           /* Primary purple */
  --theme-primary: var(--garden-accent);
  --theme-background: #ffffff;
  --theme-surface: #fafafa;

  /* 📝 Typography */
  --font-sans: 'Inter', system-ui, sans-serif;
  --font-base: 16px;                  /* Minimum accessible size */
  --font-lg: 20px;

  /* 📏 Spacing */
  --space-1: 4px;
  --space-4: 16px;
  --space-8: 32px;

  /* 🔵 Border Radius */
  --radius-sm: 4px;
  --radius-md: 6px;
  --radius-lg: 8px;
}
```

### Light/Dark Mode Support
```css
/* Light mode (default) */
[data-theme="light"] {
  --theme-background: #ffffff;
  --theme-text-primary: #1a1a1a;
  --theme-border: #e5e7eb;
}

/* Dark mode */
[data-theme="dark"] {
  --theme-background: #0a0a0a;
  --theme-text-primary: #f0f0f0;
  --theme-border: #374151;
}
```

### Compatibility Layer
For legacy CSS files, compatibility variables map old names to new system:
```css
/* Legacy compatibility */
--color-primary: var(--theme-primary);
--color-surface-secondary: var(--theme-surface-variant);
--text-lg: var(--font-lg);
```

## 🧩 Component Architecture

### Garden UI Components
All UI components use the `garden-*` class naming convention:

#### Panels
```css
.garden-panel {
  background: var(--theme-surface);
  border: 1px solid var(--theme-border);
  border-radius: var(--radius-sm);
  padding: var(--space-4);
}

.garden-panel-header {
  background: var(--theme-surface-variant);
  border-bottom: 1px solid var(--theme-border);
  padding: var(--space-3) var(--space-4);
  font-weight: var(--font-semibold);
}
```

#### Actions (Buttons)
```css
.garden-action {
  padding: var(--space-2) var(--space-4);
  border-radius: var(--radius-md);
  font-family: var(--font-ui);
  transition: all 0.2s ease;
}

.garden-action.primary {
  background: var(--theme-primary);
  color: var(--theme-on-primary);
}

.garden-action.secondary {
  background: var(--theme-surface-variant);
  color: var(--theme-text-primary);
}
```

#### Form Elements
```css
.garden-input {
  padding: var(--space-3);
  border: 1px solid var(--theme-border);
  border-radius: var(--radius-md);
  background: var(--theme-surface);
  color: var(--theme-text-primary);
}

.garden-input:focus {
  border-color: var(--theme-primary);
  box-shadow: var(--shadow-primary-focus);
}
```

## 🎯 Design Tokens

### Color System
```css
/* Primary Colors */
--garden-accent: #3d2970;              /* Main brand purple */
--theme-primary: var(--garden-accent);
--theme-primary-hover: #4c3b8a;
--theme-primary-alpha: rgba(61, 41, 112, 0.1);

/* Semantic Colors */
--theme-success: #10b981;
--theme-warning: #f59e0b;
--theme-error: #ef4444;
--theme-info: #3b82f6;

/* Surface Colors */
--theme-background: #ffffff;           /* Page background */
--theme-surface: #fafafa;             /* Card/panel background */
--theme-surface-variant: #f3f4f6;     /* Secondary surfaces */

/* Text Colors */
--theme-text-primary: #1a1a1a;        /* Main text */
--theme-text-secondary: #6b7280;      /* Muted text */
--theme-text-tertiary: #9ca3af;       /* Disabled text */
```

### Typography Scale
```css
/* Font Families */
--font-sans: 'Inter', 'Source Sans Pro', system-ui, sans-serif;
--font-body: var(--font-sans);
--font-heading: var(--font-sans);

/* Font Sizes */
--font-xs: 12px;
--font-sm: 14px;
--font-base: 16px;    /* Minimum accessible body text */
--font-md: 18px;
--font-lg: 20px;
--font-xl: 24px;
--font-2xl: 30px;
--font-3xl: 36px;

/* Font Weights */
--font-light: 300;
--font-normal: 400;
--font-medium: 500;
--font-semibold: 600;
--font-bold: 700;
```

### Spacing System
```css
/* Base-4 Spacing Scale */
--space-1: 4px;      /* 0.25rem */
--space-2: 8px;      /* 0.5rem */
--space-3: 12px;     /* 0.75rem */
--space-4: 16px;     /* 1rem */
--space-5: 20px;     /* 1.25rem */
--space-6: 24px;     /* 1.5rem */
--space-8: 32px;     /* 2rem */
--space-10: 40px;    /* 2.5rem */
--space-12: 48px;    /* 3rem */
--space-16: 64px;    /* 4rem */
--space-20: 80px;    /* 5rem */
--space-24: 96px;    /* 6rem */
```

### Border Radius
```css
--radius-sm: 4px;    /* Small elements */
--radius-md: 6px;    /* Default buttons, inputs */
--radius-lg: 8px;    /* Cards, panels */
--radius-xl: 12px;   /* Large containers */
--radius-full: 50%;  /* Circular elements */
```

## ♿ Accessibility

### Color Contrast Standards
All colors meet **WCAG AAA** standards (7:1 contrast ratio):
```css
/* High contrast mode overrides */
@media (prefers-contrast: high) {
  :root {
    --theme-primary: #2D1B69;      /* Enhanced contrast */
    --theme-text-primary: #000000;  /* Pure black text */
  }
}
```

### Focus Management
```css
/* Visible focus indicators */
.garden-action:focus,
.garden-input:focus {
  outline: 2px solid var(--theme-primary);
  outline-offset: 2px;
}

/* Focus within containers */
.garden-panel:focus-within {
  box-shadow: var(--shadow-primary-focus);
}
```

### Reduced Motion Support
```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

## 📱 Responsive Design

### Breakpoint System
```css
/* Mobile first approach */
@media (min-width: 640px) {  /* sm */
  .garden-container { max-width: 640px; }
}

@media (min-width: 768px) {  /* md */
  .garden-container { max-width: 768px; }
}

@media (min-width: 1024px) { /* lg */
  .garden-container { max-width: 1024px; }
}

@media (min-width: 1280px) { /* xl */
  .garden-container { max-width: 1280px; }
}
```

### Container System
```css
.garden-container {
  width: 100%;
  margin: 0 auto;
  padding: 0 var(--space-4);
}

.garden-grid {
  display: grid;
  gap: var(--space-4);
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
}
```

## 🚀 Performance Optimizations

### CSS Loading Strategy
```html
<!-- Critical CSS loads first -->
<link rel="stylesheet" href="garden-ui-theme.css">
<link rel="stylesheet" href="core-styles.css">

<!-- Page-specific CSS loads conditionally -->
{% if page.slug == 'about' %}
<link rel="stylesheet" href="about-page.css">
{% endif %}
```

### CSS Layers
```css
/* Explicit cascade control */
@layer reset, tokens, themes, base, components, utilities;

@layer tokens {
  /* CSS variables defined here */
}

@layer base {
  /* Base element styles */
}

@layer components {
  /* Garden UI components */
}
```

### File Size Monitoring
- Individual CSS files: **<200KB** limit
- Total CSS payload: **<500KB** target
- Theme file: **~50KB** (300+ variables)

## 🔄 Migration Patterns

### Adding New Variables
```css
/* 1. Add to theme file */
:root {
  --new-feature-color: #your-color;
}

/* 2. Use in components */
.new-component {
  background: var(--new-feature-color);
}

/* 3. Add dark mode variant */
[data-theme="dark"] {
  --new-feature-color: #dark-variant;
}
```

### Deprecating Variables
```css
/* 1. Mark as deprecated */
--old-variable: var(--new-variable); /* @deprecated Use --new-variable */

/* 2. Update usage gradually */
/* 3. Remove after migration complete */
```

## 📊 Monitoring & Maintenance

### Automated Checks
- **Undefined variables**: Prevented by tests
- **File sizes**: Monitored automatically
- **Color contrast**: Validated in CI
- **Garden UI adoption**: Tracked over time

### Maintenance Commands
```bash
make css-check      # Verify no conflicts
make css-test       # Full test suite
make css-baseline   # Update baseline
make css-report     # Detailed analysis
```

---

This architecture ensures scalable, maintainable, and accessible CSS that grows with the platform while maintaining consistency and performance.
