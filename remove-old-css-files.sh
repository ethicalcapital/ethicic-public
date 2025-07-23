#!/bin/bash

# Script to remove old CSS override files that have been integrated into core Garden UI components
# Run this ONLY after testing the updated base template

echo "CSS Override File Removal Script"
echo "================================"
echo "This script will remove CSS files that have been integrated into core Garden UI components."
echo "Make sure you have tested the updated base template before running this!"
echo ""
read -p "Have you tested the new CSS structure? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Please test first, then run this script."
    exit 1
fi

# Create backup directory
backup_dir="static/css/backup-$(date +%Y%m%d-%H%M%S)"
echo "Creating backup directory: $backup_dir"
mkdir -p "$backup_dir"

# List of files to remove
files_to_remove=(
    "static/css/button-contrast-fixes.css"
    "static/css/z-final-button-contrast-fix.css"
    "static/css/button-on-color-fix.css"
    "static/css/header-button-fix.css"
    "static/css/blog-button-fixes.css"
    "static/css/blog-nuclear-button-fix.css"
    "static/css/z-contact-emergency-fix.css"
    "static/css/contact-page-fixes.css"
    "static/css/critical-page-overrides.css"
    "static/css/page-specific-overrides.css"
    "static/css/critical-fixes.css"
    "static/css/mobile-menu-override.css"
    "static/css/blog-formatting-fixes.css"
    "static/css/critical-fouc-prevention.css"
    "static/css/mobile-menu-clean.css"
    "static/css/header-height-fix.css"
    "static/css/page-width-fix.css"
    "static/css/mobile-nav-fix.css"
    "static/css/header-text-fix.css"
    "static/css/strategy-nuclear-fix.css"
    "static/css/strategy-table-contrast-fix.css"
    "static/css/button-alignment-fix.css"
)

# Also check staticfiles directory if it exists
if [ -d "staticfiles/css" ]; then
    echo "Found staticfiles directory, will remove from there too"
    for file in "${files_to_remove[@]}"; do
        staticfile=${file/static/staticfiles}
        if [ -f "$staticfile" ]; then
            files_to_remove+=("$staticfile")
        fi
    done
fi

echo ""
echo "Files to be removed:"
echo "-------------------"
for file in "${files_to_remove[@]}"; do
    if [ -f "$file" ]; then
        echo "✓ $file"
    fi
done

echo ""
read -p "Proceed with removal? (yes/no): " proceed

if [ "$proceed" != "yes" ]; then
    echo "Cancelled."
    exit 0
fi

# Move files to backup directory
echo ""
echo "Moving files to backup directory..."
moved_count=0
for file in "${files_to_remove[@]}"; do
    if [ -f "$file" ]; then
        # Create subdirectory structure in backup
        dir=$(dirname "$file")
        mkdir -p "$backup_dir/$dir"
        mv "$file" "$backup_dir/$file"
        echo "Moved: $file"
        ((moved_count++))
    fi
done

echo ""
echo "Summary:"
echo "--------"
echo "Files moved to backup: $moved_count"
echo "Backup location: $backup_dir"
echo ""
echo "Next steps:"
echo "1. Update your base template to use base_updated.html"
echo "2. Run 'python manage.py collectstatic' if using Django"
echo "3. Clear any CDN caches"
echo "4. Test all pages thoroughly"
echo ""
echo "If you need to restore, all files are in: $backup_dir"
echo ""
echo "Done!"
