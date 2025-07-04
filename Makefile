# Makefile for CSS conflict management and testing

.PHONY: css-check css-test css-baseline css-report css-fix install-hooks test-all

# CSS Conflict Management
css-check:
	@echo "🔍 Checking CSS conflicts..."
	@python css_monitoring.py --check

css-test:
	@echo "🧪 Running CSS conflict tests..."
	@python -m pytest tests/test_css_conflicts.py -v

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

help:
	@echo "CSS Conflict Management Commands:"
	@echo "  css-check      - Check for CSS conflicts against baseline"
	@echo "  css-test       - Run comprehensive CSS test suite"
	@echo "  css-baseline   - Create new baseline snapshot"
	@echo "  css-report     - Generate detailed CSS analysis report"
	@echo "  css-fix        - Attempt automatic fixes"
	@echo "  install-hooks  - Install git pre-commit hooks"
	@echo "  test-all       - Run all CSS tests and checks"
	@echo "  dev-setup      - Setup development environment"
	@echo "  css-status     - Quick CSS status check"