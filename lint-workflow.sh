#!/bin/bash

# CSS Linting Workflow Script
# Helps manage the gradual migration to clean CSS

set -e

echo "🔍 CSS Linting Workflow"
echo "======================="

# Function to show help
show_help() {
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  check     - Run linting on all files"
    echo "  fix       - Auto-fix issues where possible"
    echo "  report    - Generate detailed report"
    echo "  clean     - Check only clean files (no legacy issues)"
    echo "  migrate   - Interactive migration helper"
    echo "  help      - Show this help message"
    echo ""
}

# Function to check specific files
check_files() {
    echo "🔍 Checking CSS files for issues..."
    npm run lint:css 2>&1 | tee lint-output.txt

    # Count issues
    error_count=$(grep -c "✖" lint-output.txt || echo "0")
    warning_count=$(grep -c "⚠" lint-output.txt || echo "0")

    echo ""
    echo "Summary:"
    echo "  Errors: $error_count"
    echo "  Warnings: $warning_count"

    if [ "$error_count" -gt 0 ]; then
        echo ""
        echo "💡 To fix auto-fixable issues: npm run lint:css:fix"
        echo "💡 To see detailed report: ./lint-workflow.sh report"
        return 1
    fi

    return 0
}

# Function to auto-fix issues
fix_issues() {
    echo "🔧 Auto-fixing CSS issues..."
    npm run lint:css:fix
    echo "✅ Auto-fix complete!"
    echo ""
    echo "🔍 Checking remaining issues..."
    npm run lint:css
}

# Function to generate report
generate_report() {
    echo "📊 Generating detailed lint report..."
    npm run lint:css:report

    if [ -f "lint-report.json" ]; then
        echo "✅ Report generated: lint-report.json"

        # Show summary
        echo ""
        echo "📋 Issue Summary:"
        echo "=================="

        # Count issues by type (requires jq)
        if command -v jq &> /dev/null; then
            echo "By rule:"
            jq -r '.[] | .warnings[]? | .rule' lint-report.json | sort | uniq -c | sort -nr
        else
            echo "Install jq for detailed breakdown"
        fi
    else
        echo "❌ Failed to generate report"
    fi
}

# Function to check only clean files
check_clean() {
    echo "🧹 Checking only clean files..."

    # List of clean files (no legacy issues)
    clean_files=(
        "static/css/garden-ui-utilities.css"
        "static/css/garden-forms.css"
        "static/css/garden-critical.css"
    )

    for file in "${clean_files[@]}"; do
        if [ -f "$file" ]; then
            echo "Checking: $file"
            npx stylelint "$file" || true
        fi
    done
}

# Function for interactive migration
migrate_interactive() {
    echo "🚀 Interactive CSS Migration Helper"
    echo "=================================="

    echo ""
    echo "This will help you migrate CSS files to comply with linting rules."
    echo ""

    read -p "Choose a file to migrate (or press Enter for all): " file_choice

    if [ -n "$file_choice" ]; then
        if [ -f "$file_choice" ]; then
            echo "Processing: $file_choice"
            npx stylelint "$file_choice" --fix
            echo "✅ Auto-fixes applied"
            echo ""
            echo "Remaining issues:"
            npx stylelint "$file_choice" || true
        else
            echo "❌ File not found: $file_choice"
        fi
    else
        echo "Processing all files..."
        npm run lint:css:fix
    fi
}

# Parse command line arguments
case "${1:-help}" in
    check)
        check_files
        ;;
    fix)
        fix_issues
        ;;
    report)
        generate_report
        ;;
    clean)
        check_clean
        ;;
    migrate)
        migrate_interactive
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo "❌ Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
