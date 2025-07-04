#!/bin/bash
# Check favicon files status

echo "Checking favicon files in /Users/srvo/ethicic-public/static/"
echo "=================================================="

# List of required favicon files
files=(
    "favicon.ico"
    "favicon-16x16.png"
    "favicon-32x32.png"
    "favicon.svg"
    "apple-touch-icon.png"
    "android-chrome-192x192.png"
    "android-chrome-512x512.png"
    "manifest.json"
    "browserconfig.xml"
    "images/og-default.png"
    "images/og-default.svg"
    "images/twitter-card.png"
    "images/twitter-card.svg"
)

# Check each file
for file in "${files[@]}"; do
    if [ -f "/Users/srvo/ethicic-public/static/$file" ]; then
        echo "✅ $file - EXISTS"
    else
        echo "❌ $file - MISSING"
    fi
done

echo ""
echo "Generator Tools:"
echo "----------------"
echo "📄 favicon-generator.html - Creates PNG favicons from SVG"
echo "📄 social-media-generator.html - Creates social media images"
