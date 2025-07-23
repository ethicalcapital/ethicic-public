# PostCSS Build Process - Complete Setup

## Overview

This document outlines the complete PostCSS build process for the Garden UI project. The build system combines 64+ CSS files into optimized bundles while respecting CSS layers and maintaining proper cascade order.

## Architecture

### File Structure
```
static/css/
├── dist/                    # Build output directory
│   ├── combined.css         # Raw combined CSS
│   ├── development.css      # Development build (unminified)
│   └── production.css       # Production build (minified)
├── garden-ui-theme.css      # Core theme system
├── garden-ui-utilities.css  # Utility classes
├── garden-forms.css         # Form components
├── core-styles.css          # Base styles
├── layers/                  # Page-specific layers
└── ...                      # Other CSS files
```

### Build Scripts

#### scripts/build-css.js
The main build script that:
- Combines CSS files in correct cascade order
- Wraps output in CSS layers for proper cascade control
- Excludes legacy override files
- Provides detailed build output

#### Key Features
- **Ordered file processing**: Respects CSS cascade hierarchy
- **Layer wrapping**: Wraps combined CSS in `@layer components`
- **Exclusion patterns**: Filters out legacy override files
- **Build reporting**: Shows file order and total size

## NPM Scripts

### Available Commands

```bash
# Development builds (unminified)
npm run build:css:dev       # Build for development
npm run build:css           # Default to development build
npm run build:css:watch     # Watch for changes and rebuild

# Production builds (minified)
npm run build:css:prod      # Build for production
npm run build              # Production build

# Combined workflows
npm run quality            # Lint + production build
npm run dev               # Watch mode for development
```

### Build Process Flow

1. **File Discovery**: Scans `static/css/` for all CSS files
2. **Filtering**: Excludes legacy override files using patterns
3. **Ordering**: Sorts files according to cascade priority
4. **Combining**: Concatenates files with header comments
5. **Layer Wrapping**: Wraps in `@layer components` for cascade control
6. **PostCSS Processing**: Applies transformations and optimizations

## PostCSS Configuration

### Plugins Used

```javascript
// postcss.config.js
module.exports = {
  plugins: [
    // Support for CSS nesting
    require('postcss-nested'),

    // Support for CSS custom properties
    require('postcss-custom-properties')({
      preserve: true // Keep custom properties for runtime theming
    }),

    // Autoprefixer for vendor prefixes
    require('autoprefixer'),

    // CSS optimization (production only)
    require('cssnano')({
      preset: ['default', {
        discardComments: { removeAll: true },
        normalizeWhitespace: false,
        colormin: false,
        minifyFontValues: false,
        // Preserve CSS layers
        discardDuplicates: false,
        mergeRules: false,
        // Don't break CSS custom properties
        reduceIdents: false,
        zindex: false
      }]
    })
  ]
}
```

### Plugin Benefits

1. **postcss-nested**: Enables CSS nesting for better organization
2. **postcss-custom-properties**: Processes CSS variables while preserving them
3. **autoprefixer**: Adds vendor prefixes based on browser support
4. **cssnano**: Optimizes CSS for production (minification, deduplication)

## File Ordering Strategy

### Cascade Priority (High to Low)

1. **Core Garden UI**
   - `garden-ui-theme.css` (theme system)
   - `garden-ui-utilities.css` (utility classes)
   - `garden-forms.css` (form components)
   - `core-styles.css` (base styles)

2. **Component Files**
   - `garden-blog.css`
   - `garden-widgets.css`
   - `garden-data-table.css`

3. **Page-Specific Files**
   - `onboarding-comprehensive.css`
   - `process-page.css`
   - `layers/*.css` (page-specific layers)

4. **Layout and Utilities**
   - `utility-layout.css`
   - `public-site-layout-fixes.css`
   - `public-site-modular.css`

5. **Essential Fixes** (gradually being eliminated)
   - `footer-fix.css`
   - `wcag-contrast-fixes.css`
   - `accessibility-contrast-fixes.css`
   - etc.

### Exclusion Patterns

Files automatically excluded from builds:
```javascript
excludePatterns: [
  'dist/**',           // Build output
  'backup-*/**',       // Backup directories
  'archived/**',       // Archived files
  'z-*.css',          // Emergency fixes
  '*-nuclear-*.css',   // Nuclear overrides
  '*-emergency-*.css', // Emergency overrides
  // ... other legacy patterns
]
```

## CSS Layers Integration

### Layer Structure
```css
@layer reset, base, components, utilities, overrides;

@layer components {
  /* All combined CSS goes here */
}
```

### Benefits
- **Cascade Control**: Explicit layer ordering prevents specificity wars
- **Maintainability**: Clear separation of concerns
- **Future-Proof**: Supports CSS layers natively
- **Override Safety**: Utility classes always win over components

## Build Outputs

### Development Build (`development.css`)
- **Unminified**: Human-readable format
- **Comments preserved**: File headers and documentation
- **Source maps**: Easy debugging
- **File size**: ~616KB

### Production Build (`production.css`)
- **Minified**: Optimized for size
- **Comments removed**: No documentation comments
- **Vendor prefixes**: Added automatically
- **File size**: ~773KB (includes autoprefixer additions)

## File Watching

### Development Workflow
```bash
npm run dev  # Starts file watcher
```

The watcher:
- Monitors all CSS files in `static/css/`
- Rebuilds automatically on changes
- Provides instant feedback
- Maintains development-friendly output

## Integration with Django

### Template Integration
```html
<!-- Development -->
<link rel="stylesheet" href="{% static 'css/dist/development.css' %}">

<!-- Production -->
<link rel="stylesheet" href="{% static 'css/dist/production.css' %}">
```

### Static Files Collection
```bash
# After building CSS
python manage.py collectstatic
```

## Performance Optimization

### Build Performance
- **Parallel processing**: Files processed efficiently
- **Caching**: Only rebuilds when source files change
- **Incremental builds**: Watch mode for development

### Runtime Performance
- **Single HTTP request**: All CSS in one file
- **Optimized cascade**: CSS layers prevent specificity issues
- **Minified output**: Reduced file size for production
- **Vendor prefixes**: Automated browser compatibility

## Troubleshooting

### Common Issues

1. **Build fails with "file not found"**
   - Check file paths in `orderedFiles` configuration
   - Ensure files exist in `static/css/`

2. **CSS not applying correctly**
   - Verify layer order in combined output
   - Check for specificity conflicts

3. **Watch mode not working**
   - Ensure `chokidar-cli` is installed
   - Check file permissions

4. **Large file sizes**
   - Review included files in build output
   - Consider splitting into multiple bundles

### Debug Commands
```bash
# Check build output
npm run build:css:dev

# View file order
node scripts/build-css.js

# Check PostCSS processing
postcss static/css/dist/combined.css --verbose
```

## Future Enhancements

### Planned Features
1. **Bundle splitting**: Separate critical CSS from non-critical
2. **Purge CSS**: Remove unused styles
3. **Source maps**: Better debugging support
4. **Tree shaking**: Remove unused CSS variables
5. **Performance budgets**: File size limits

### Migration Strategy
1. **Gradual override removal**: Eliminate legacy files
2. **Layer optimization**: Better layer organization
3. **Component bundling**: Group related components
4. **Critical CSS**: Inline critical styles

## Benefits Achieved

### Developer Experience
- **Automated builds**: No manual CSS concatenation
- **Watch mode**: Instant feedback during development
- **Clear ordering**: Predictable cascade behavior
- **Legacy handling**: Gradual migration path

### Performance
- **Reduced HTTP requests**: Single CSS file
- **Optimized delivery**: Minified production builds
- **Better caching**: Consolidated assets
- **Faster rendering**: Optimized CSS structure

### Maintainability
- **Organized structure**: Clear file hierarchy
- **Automated optimization**: No manual minification
- **Consistent processing**: Same build process everywhere
- **Version control**: Build outputs tracked

This PostCSS build process provides a solid foundation for managing CSS at scale while maintaining performance and developer experience.
