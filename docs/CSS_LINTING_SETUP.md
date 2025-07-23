# CSS Linting Setup - Phase 3: Automate and Enforce Code Quality

## Overview

This document outlines the CSS linting implementation for the Garden UI project, designed to automatically enforce coding conventions, catch errors, and maintain consistency across all 50+ CSS files.

## Stylelint Configuration

### Key Features

- **Extends stylelint-config-standard**: Industry-standard CSS linting rules
- **Garden UI BEM Pattern Enforcement**: Ensures all component classes follow `.garden-block__element--modifier` pattern
- **!important Prohibition**: Flags use of `!important` as an error (violates @layer strategy)
- **Modern CSS Support**: Compatible with `@layer`, CSS nesting, and custom properties
- **Utility Class Support**: Recognizes spacing utilities (`.mt-3`, `.mb-4`, etc.)

### Configuration Details

#### BEM Pattern Enforcement
```javascript
"selector-class-pattern": [
  "^(garden-[a-z]([a-z0-9-]+)?(__[a-z]([a-z0-9-]+)?)?(--[a-z]([a-z0-9-]+)?)?|[a-z]([a-z0-9-]+)?(-[a-z0-9-]+)*|sr-only|visually-hidden)$"
]
```

**Valid Examples:**
- `.garden-panel` (block)
- `.garden-panel__header` (block + element)
- `.garden-panel__header--highlighted` (block + element + modifier)
- `.garden-action--primary` (block + modifier)
- `.mt-3`, `.border-top` (utility classes)
- `.sr-only`, `.visually-hidden` (accessibility classes)

**Invalid Examples:**
- `.panel` (missing garden- prefix)
- `.garden-panel-header` (should use __ for elements)
- `.garden-panel__header-title` (should use -- for modifiers)

#### Modern CSS Support
```javascript
"at-rule-no-unknown": {
  "ignoreAtRules": ["layer", "container", "supports"]
}
```

Supports:
- `@layer` for cascade layers
- `@container` for container queries
- `@supports` for feature queries
- CSS custom properties (`--variable`)

#### Quality Rules
- **No !important**: Prevents specificity wars
- **Max nesting depth**: 3 levels maximum
- **Specificity limits**: 0,4,0 maximum (4 classes max)
- **No vendor prefixes**: Use autoprefixer instead
- **Consistent formatting**: 2-space indentation, double quotes

## NPM Scripts

### Available Commands

```bash
# Basic linting
npm run lint:css              # Check all CSS files
npm run lint:css:fix          # Auto-fix issues where possible
npm run lint:css:report       # Generate JSON report

# Quality workflow
npm run quality               # Run linting + build process
npm run precommit            # Run before commits (lint only)
```

### Integration with Build Process

```bash
# Combined workflow
npm run quality  # Equivalent to:
# 1. npm run lint:css (check for errors)
# 2. npm run build:css (build production files)
```

## Git Hook Integration

### Pre-commit Hook Enhancement

The existing pre-commit hook now includes Stylelint:

```bash
#!/bin/bash
# Existing CSS conflict checks...
# + NEW: Stylelint checks
if npm run lint:css; then
    echo "✅ Stylelint checks passed"
else
    echo "❌ Stylelint checks failed!"
    # Helpful error guidance
    exit 1
fi
```

### Workflow
1. **Developer commits code**
2. **Pre-commit hook runs**:
   - CSS conflict detection
   - Stylelint validation
   - Anti-pattern checks
3. **If any check fails**: Commit rejected with helpful error messages
4. **If all checks pass**: Commit proceeds

## VS Code Integration

### Settings Configuration

The `.vscode/settings.json` file enables:
- **Real-time linting**: Errors shown in editor
- **Auto-fix on save**: Automatically fixes issues when saving
- **Disabled native CSS validation**: Prevents conflicts with Stylelint
- **File associations**: Ensures proper CSS handling

### Editor Experience

- **Red squiggles**: Show linting errors in real-time
- **Quick fixes**: Ctrl+. to see available fixes
- **Auto-formatting**: Fixes spacing, quotes, etc. on save
- **Intellisense**: Validates class names against BEM pattern

## Common Linting Errors and Fixes

### 1. !important Usage
```css
/* ❌ Error */
.garden-button {
  color: red !important;
}

/* ✅ Fixed */
.garden-button {
  color: var(--garden-button-color);
}
```

### 2. Invalid Class Names
```css
/* ❌ Error */
.panel-header {
  background: blue;
}

/* ✅ Fixed */
.garden-panel__header {
  background: var(--garden-panel-header-bg);
}
```

### 3. Hardcoded Colors
```css
/* ❌ Error */
.garden-action {
  background: #3d2970;
}

/* ✅ Fixed */
.garden-action {
  background: var(--garden-action-bg);
}
```

### 4. Excessive Nesting
```css
/* ❌ Error (4 levels deep) */
.garden-panel {
  .garden-panel__header {
    .garden-panel__title {
      .garden-panel__icon {
        color: red;
      }
    }
  }
}

/* ✅ Fixed */
.garden-panel__header-icon {
  color: var(--garden-icon-color);
}
```

## File Exclusions

The linter ignores these directories:
- `node_modules/**/*`
- `staticfiles/**/*` (Django static files)
- `static/css/backup-*/**/*` (Backup directories)
- `static/admin/**/*` (Django admin CSS)
- `dist/**/*` and `build/**/*` (Build artifacts)

## Benefits

### Code Quality
- **Consistent naming**: All classes follow Garden UI BEM pattern
- **No specificity wars**: !important usage blocked
- **Modern CSS**: Supports latest CSS features
- **Maintainable**: Clear component boundaries

### Developer Experience
- **Real-time feedback**: Issues caught while typing
- **Auto-fixes**: Many issues resolved automatically
- **Clear error messages**: Helpful guidance for fixes
- **Git integration**: Prevents bad CSS from being committed

### Team Collaboration
- **Consistent style**: All developers follow same conventions
- **Reduced reviews**: Automated checks catch issues
- **Documentation**: Clear rules and examples
- **Onboarding**: New developers learn conventions quickly

## Troubleshooting

### Common Issues

1. **Plugin not found**: Install missing dependencies
   ```bash
   npm install --save-dev stylelint-selector-bem-pattern
   ```

2. **VS Code not showing errors**: Restart VS Code or install Stylelint extension

3. **Git hook not running**: Check hook permissions
   ```bash
   chmod +x git_hooks/pre-commit
   ```

4. **Build failing**: Check for syntax errors
   ```bash
   npm run lint:css -- --formatter verbose
   ```

### Getting Help

- **View all errors**: `npm run lint:css`
- **Detailed report**: `npm run lint:css:report`
- **Fix auto-fixable issues**: `npm run lint:css:fix`
- **Check specific file**: `npx stylelint static/css/filename.css`

## Future Enhancements

1. **Custom Rules**: Create Garden UI-specific rules
2. **Performance Linting**: Check for CSS performance issues
3. **Accessibility Rules**: Automated a11y checks
4. **Integration Testing**: Validate CSS against components
5. **Documentation Generation**: Auto-generate style guides

This linting setup ensures consistent, maintainable CSS that follows Garden UI conventions while catching errors early in the development process.
