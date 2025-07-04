# Code Quality & Linting Setup

This project uses multiple linting tools to maintain code quality and consistency.

## Tools Configured

### Python - Ruff
- **Tool**: [Ruff](https://github.com/astral-sh/ruff) - Fast Python linter
- **Command**: `make lint-python` or `ruff check .`
- **Auto-fix**: `ruff check --fix .`

### CSS - Stylelint
- **Tool**: [Stylelint](https://stylelint.io/) - CSS linter
- **Config**: `.stylelintrc.json`
- **Command**: `make lint-css` or `stylelint "static/css/**/*.css"`
- **Auto-fix**: `stylelint "static/css/**/*.css" --fix`

### JavaScript - ESLint
- **Tool**: [ESLint](https://eslint.org/) - JavaScript linter
- **Config**: `eslint.config.js`
- **Command**: `make lint-js` or `npx eslint "static/js/**/*.js"`
- **Auto-fix**: `npx eslint "static/js/**/*.js" --fix`
- **Ignore**: `.eslintignore`

### CSS Conflicts - Custom Tool
- **Tool**: Custom CSS monitoring system
- **Command**: `make css-check` or `python css_monitoring.py --check`
- **Purpose**: Prevents CSS variable conflicts and undefined variables

## Quick Commands

```bash
# Run all linting tools
make lint

# Run individual tools
make lint-python
make lint-css
make lint-js

# Auto-fix all issues
make lint-fix

# Check CSS conflicts
make css-check
```

## Pre-commit Hooks

The repository has pre-commit hooks that automatically run all linting tools:

- **Location**: `.git/hooks/pre-commit`
- **Runs**: Ruff, Stylelint, ESLint, CSS conflict checks
- **Behavior**: Blocks commits if any linting errors are found

### What gets checked:
- **Python files**: Ruff linting
- **CSS files**: Stylelint linting + CSS conflict detection
- **JavaScript files**: ESLint linting (only `static/js/` files)

### If linting fails:
The hook will show helpful commands to fix issues:
```bash
# Python issues
ruff check --fix [files]

# CSS issues  
stylelint --fix [files]

# JavaScript issues
npx eslint --fix [files]
```

## File Patterns

### Included in linting:
- **Python**: All `.py` files in the project
- **CSS**: `static/css/**/*.css`
- **JavaScript**: `static/js/**/*.js`

### Excluded from linting:
- `node_modules/`
- `.venv/`
- `staticfiles/`
- `**/coverage/**`
- `**/*min.js`
- Third-party library files

## Benefits

1. **Consistent Code Style**: All code follows the same formatting and style rules
2. **Early Error Detection**: Catch common issues before they reach production
3. **Security**: Prevent common security anti-patterns
4. **CSS Safety**: Prevent CSS conflicts that break the design system
5. **Automated**: Pre-commit hooks ensure all code is checked automatically

## Bypassing (Emergency Only)

In emergency situations, you can bypass pre-commit hooks with:
```bash
git commit --no-verify -m "Emergency commit message"
```

⚠️ **Only use this in true emergencies** - fix linting issues as soon as possible after bypassing.