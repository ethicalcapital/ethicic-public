# Blog CSS Overlap Examples

## Button Style Overlaps

### Example 1: Secondary Button Styles
These selectors appear in multiple files with different rules:

**button-contrast-fixes.css:**
```css
.garden-action.secondary {
    background: transparent !important;
    color: var(--color-primary) !important;
    border: 2px solid var(--color-primary) !important;
}
```

**blog-button-fixes.css:**
```css
.blog-index-page .garden-action.secondary {
    background: transparent !important;
    color: var(--color-primary) !important;
    border: 2px solid var(--color-primary) !important;
}
```

**blog-nuclear-button-fix.css:**
```css
html body .blog-index-page .garden-action.secondary {
    background-color: transparent !important;
    color: var(--color-primary, #6B46C1) !important;
    border: 2px solid var(--color-primary, #6B46C1) !important;
}
```

### Example 2: Panel Header Styles

**core-styles.css:**
```css
.garden-panel__header {
    background: #f5f5f5;
    padding: 1rem;
    border-bottom: 1px solid #e0e0e0;
}
```

**public-site-simple.css:**
```css
.garden-panel__header {
    padding: 16px 20px;
    background: var(--color-surface-variant);
    border-bottom: 1px solid var(--color-border);
}
```

**garden-blog-panels.css:**
```css
.garden-panel .garden-panel-header {
    padding: 1rem 1.5rem;
    background: #f8f8f8;
}
```

**blog-formatting-fixes.css:**
```css
.newsletter-section .garden-panel-header {
    background: var(--color-primary);
    padding: 1rem 1.25rem !important;
}
```

## Specificity Wars Examples

### Nuclear Overrides
The blog-nuclear-button-fix.css uses extremely high specificity:
```css
html body .blog-index-page .article-list-actions a.garden-action.secondary.small:link,
html body .blog-index-page .article-list-actions a.garden-action.secondary.small:visited
```

This overrides simpler selectors like:
```css
.garden-action.secondary
```

## Dark Mode Duplication

Dark mode styles are scattered across multiple files:

**core-styles.css:**
```css
[data-theme="dark"] .garden-panel {
    background: #1a1a1a;
    color: #e0e0e0;
}
```

**button-contrast-fixes.css:**
```css
[data-theme="dark"] .garden-action.secondary {
    color: var(--color-primary-hover) !important;
    border-color: var(--color-primary) !important;
}
```

## Redundant Media Queries

Several files define the same breakpoints with overlapping rules:
- Mobile: max-width: 768px
- Tablet: max-width: 1024px
- Desktop: min-width: 1025px

## Impact Analysis

1. **File Size**: ~30-40% of CSS is redundant or overriding other rules
2. **Performance**: Multiple reflows as cascading rules override each other
3. **Maintenance**: Difficult to track which rule is actually being applied
4. **Debugging**: Developer tools show multiple overridden rules for same element

## Consolidation Benefits

By consolidating these files:
- Reduce total CSS from ~13 files to 6 files
- Eliminate ~40% of redundant code
- Improve page load time by reducing HTTP requests
- Make styling more predictable and maintainable