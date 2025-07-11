# Code Quality & Linting Setup

This project uses multiple linting tools to maintain code quality and consistency.

## Tools Configured

### Python - Ruff (Enhanced Security)
- **Tool**: [Ruff](https://github.com/astral-sh/ruff) - Fast Python linter with security focus
- **Rules**: Pycodestyle (E/W), Pyflakes (F), Security (S), Bugbear (B), Complexity (C90), Import sorting (I), Naming (N), PyUpgrade (UP), Pylint (PL), and more
- **Config**: `ruff.toml` with financial-grade security standards
- **Command**: `make lint-python` or `ruff check .`
- **Auto-fix**: `ruff check --fix .`
- **Security**: Includes bandit security checks for vulnerabilities

### CSS - Stylelint (Hardcoded Color Detection)
- **Tool**: [Stylelint](https://stylelint.io/) - CSS linter with Garden UI enforcement
- **Rules**: Standard CSS rules PLUS hardcoded color detection, !important detection, CSS variable enforcement
- **Config**: `.stylelintrc.json` - blocks hardcoded colors, RGB/HSL functions, named colors
- **Command**: `make lint-css` or `stylelint "static/css/**/*.css"`
- **Auto-fix**: `stylelint "static/css/**/*.css" --fix`
- **Theme Exception**: `garden-ui-theme.css` is excluded (it defines the base colors)

### JavaScript - ESLint (Production Standards)
- **Tool**: [ESLint](https://eslint.org/) - JavaScript linter with production-grade rules
- **Rules**: Error prevention, security, complexity limits, no alerts/console (warn), modern JS enforcement
- **Config**: `eslint.config.js` - enhanced for financial software
- **Command**: `make lint-js` or `npx eslint "static/js/**/*.js"`
- **Auto-fix**: `npx eslint "static/js/**/*.js" --fix`
- **Ignore**: `.eslintignore` - excludes libraries and generated files

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
