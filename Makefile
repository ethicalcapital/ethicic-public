# Makefile for CSS conflict management and testing

.PHONY: css-check css-test css-baseline css-report css-fix install-hooks test-all lint lint-python lint-css lint-js lint-fix

# CSS Conflict Management
css-check:
	@echo "🔍 Checking CSS conflicts..."
	@python css_monitoring.py --check

css-test:
	@echo "🧪 Running CSS conflict tests..."
	@python run_css_tests.py

css-baseline:
	@echo "📸 Creating CSS baseline..."
	@python css_monitoring.py --create-baseline

css-report:
	@echo "📊 Generating CSS report..."
	@python css_monitoring.py --report

css-fix:
	@echo "🔧 Attempting auto-fix..."
	@python css_monitoring.py --auto-fix

# Git Hooks
install-hooks:
	@echo "🔗 Installing git hooks..."
	@cp git_hooks/pre-commit .git/hooks/pre-commit
	@chmod +x .git/hooks/pre-commit
	@echo "✅ Pre-commit hook installed"

# Combined testing
test-all: css-test css-check
	@echo "✅ All CSS tests passed!"

# Development helpers
dev-setup: install-hooks css-baseline
	@echo "🚀 Development environment setup complete"

# Quick status check
css-status:
	@python css_monitoring.py

# Continuous integration target
ci-css-check: css-test css-check
	@echo "✅ CI CSS checks passed"

# Code Quality & Linting
lint: lint-python lint-css lint-js css-check
	@echo "✅ All linting checks passed!"

lint-python:
	@echo "🐍 Running Ruff on Python files..."
	@ruff check .

lint-css:
	@echo "🎨 Running Stylelint on CSS files..."
	@stylelint "static/css/**/*.css"

lint-js:
	@echo "📜 Running ESLint on JavaScript files..."
	@npx eslint "static/js/**/*.js" --ignore-pattern "node_modules/" --ignore-pattern "staticfiles/" --ignore-pattern ".venv/" --ignore-pattern "**/*min.js" --ignore-pattern "**/coverage/**"

lint-fix:
	@echo "🔧 Auto-fixing linting issues..."
	@ruff check --fix . || true
	@stylelint "static/css/**/*.css" --fix || true
	@npx eslint "static/js/**/*.js" --fix --ignore-pattern "node_modules/" --ignore-pattern "staticfiles/" --ignore-pattern ".venv/" --ignore-pattern "**/*min.js" --ignore-pattern "**/coverage/**" || true
	@echo "✅ Auto-fix complete!"

help:
	@echo "🛠️  Ethical Capital Development Commands"
	@echo ""
	@echo "Code Quality:"
	@echo "  lint           - Run all linting tools (ruff, stylelint, eslint, css-check)"
	@echo "  lint-python    - Run ruff on Python files"
	@echo "  lint-css       - Run stylelint on CSS files"
	@echo "  lint-js        - Run ESLint on JavaScript files"
	@echo "  lint-fix       - Auto-fix all linting issues"
	@echo ""
	@echo "CSS Conflict Management:"
	@echo "  css-check      - Check for CSS conflicts against baseline"
	@echo "  css-test       - Run comprehensive CSS test suite"
	@echo "  css-baseline   - Create new baseline snapshot"
	@echo "  css-report     - Generate detailed CSS analysis report"
	@echo "  css-fix        - Attempt automatic fixes"
	@echo ""
	@echo "Development:"
	@echo "  install-hooks  - Install git pre-commit hooks"
	@echo "  test-all       - Run all CSS tests and checks"
	@echo "  dev-setup      - Setup development environment"
	@echo "  css-status     - Quick CSS status check"
