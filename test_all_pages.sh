#!/bin/bash

# Comprehensive pa11y accessibility testing script for all ethicic.com pages
# Based on sitemap URLs extracted from https://ethicic.com/sitemap.xml

echo "🔍 Starting comprehensive accessibility audit of ethicic.com"
echo "Testing all pages from sitemap..."
echo ""

# Counter variables
total_pages=0
pages_with_errors=0
total_errors=0
search_form_errors=0
other_errors=0

# Results file
results_file="/tmp/ethicic_accessibility_results.txt"
echo "Comprehensive Accessibility Audit Results - $(date)" > "$results_file"
echo "=========================================" >> "$results_file"
echo "" >> "$results_file"

# Base URL
base_url="https://ethicic.com"

# Read URLs from file and test each one
while IFS= read -r url_path; do
    # Skip empty lines
    if [[ -z "$url_path" ]]; then 
        continue
    fi
    
    # Remove leading/trailing whitespace and line numbers
    url_path=$(echo "$url_path" | sed 's/^[[:space:]]*[0-9]*→//' | sed 's/^[[:space:]]*//' | sed 's/[[:space:]]*$//')
    
    # Skip if still empty after cleaning
    if [[ -z "$url_path" ]]; then 
        continue
    fi
    
    # Build full URL
    full_url="${base_url}${url_path}"
    
    total_pages=$((total_pages + 1))
    
    echo "Testing [$total_pages]: $full_url"
    
    # Run pa11y and capture output
    pa11y_output=$(pa11y "$full_url" 2>&1)
    pa11y_exit_code=$?
    
    # Count errors in this page
    page_error_count=$(echo "$pa11y_output" | grep -c "• Error:")
    
    if [[ $page_error_count -gt 0 ]]; then
        pages_with_errors=$((pages_with_errors + 1))
        total_errors=$((total_errors + page_error_count))
        
        # Check if it's just the search form error
        search_form_count=$(echo "$pa11y_output" | grep -c "This form does not contain a submit button")
        search_form_errors=$((search_form_errors + search_form_count))
        
        page_other_errors=$((page_error_count - search_form_count))
        other_errors=$((other_errors + page_other_errors))
        
        echo "  ❌ $page_error_count error(s) found"
        
        # Log detailed results for pages with non-search-form errors
        if [[ $page_other_errors -gt 0 ]]; then
            echo "" >> "$results_file"
            echo "🚨 PRIORITY: $full_url - $page_other_errors unique error(s)" >> "$results_file"
            echo "$pa11y_output" >> "$results_file"
            echo "" >> "$results_file"
        fi
    else
        echo "  ✅ No errors found"
    fi
    
    # Add small delay to be respectful to the server
    sleep 0.5
    
done < /tmp/ethicic_urls.txt

# Final summary
echo ""
echo "🎯 ACCESSIBILITY AUDIT SUMMARY"
echo "=============================="
echo "Pages tested: $total_pages"
echo "Pages with errors: $pages_with_errors"
echo "Total errors found: $total_errors"
echo "Search form errors: $search_form_errors (known fix pending deployment)"
echo "Other unique errors: $other_errors"
echo ""

if [[ $other_errors -eq 0 ]]; then
    echo "🎉 EXCELLENT: Only known search form issue found across all pages!"
    echo "   Once the search button fix is deployed, the site will be fully accessible."
else
    echo "⚠️  $other_errors unique accessibility issues found that need attention."
    echo "   Check $results_file for detailed error reports."
fi

# Write summary to results file
echo "" >> "$results_file"
echo "FINAL SUMMARY" >> "$results_file"
echo "=============" >> "$results_file"
echo "Pages tested: $total_pages" >> "$results_file"
echo "Pages with errors: $pages_with_errors" >> "$results_file"
echo "Total errors: $total_errors" >> "$results_file"
echo "Search form errors: $search_form_errors" >> "$results_file"
echo "Other unique errors: $other_errors" >> "$results_file"

echo ""
echo "Detailed results saved to: $results_file"