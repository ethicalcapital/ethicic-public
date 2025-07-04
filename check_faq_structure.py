#!/usr/bin/env python
"""Check and fix FAQ structure"""
import os
import sys
import django

# Setup Django
sys.path.append('/Users/srvo/ethicic-public')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ethicic.settings')
django.setup()

from wagtail.models import Page, Site
from public_site.models import FAQIndexPage, HomePage, FAQArticle

def main():
    print("=== FAQ STRUCTURE ANALYSIS ===")
    
    # Get the FAQ Index page
    faq_index = FAQIndexPage.objects.first()
    print(f'FAQ Index: {faq_index.title} (ID: {faq_index.id})')
    print(f'Slug: {faq_index.slug}')
    print(f'Path: {faq_index.path}')
    
    # Get home page
    home_page = HomePage.objects.first()
    if home_page:
        print(f'\nHome page: {home_page.title} (ID: {home_page.id})')
        print(f'Home URL: {home_page.get_url()}')
        
        # Check FAQ parent
        faq_parent = faq_index.get_parent()
        print(f'FAQ parent: {faq_parent.title} (ID: {faq_parent.id})')
        
        if faq_parent.id != home_page.id:
            print("❌ FAQ Index is not under Home page - fixing...")
            faq_index.move(home_page, pos='last-child')
            print("✅ Moved FAQ Index under Home page")
        else:
            print("✅ FAQ Index is under Home page")
    
    # Check site configuration
    site = Site.objects.filter(is_default_site=True).first()
    if site:
        print(f'\nSite root: {site.root_page.title} (ID: {site.root_page.id})')
        print(f'Hostname: {site.hostname}')
        
        # Update site root if needed
        if home_page and site.root_page.id != home_page.id:
            print("❌ Site root is not home page - fixing...")
            site.root_page = home_page
            site.save()
            print("✅ Updated site root to home page")
    
    # Set proper slug for FAQ if needed
    if faq_index.slug != 'faq':
        print(f"❌ FAQ slug is '{faq_index.slug}', should be 'faq' - fixing...")
        faq_index.slug = 'faq'
        faq_index.save()
        print("✅ Updated FAQ slug to 'faq'")
    
    # Test URLs
    print(f'\n=== URL TESTING ===')
    print(f'FAQ Index URL: {faq_index.get_url()}')
    
    # Check specific articles
    target_titles = [
        'What are your fees?',
        'How do you handle market volatility?', 
        'Do you offer tax-loss harvesting?',
        'What makes you different from other ESG funds?'
    ]
    
    print('\n=== TARGET ARTICLES ===')
    for title in target_titles:
        article = FAQArticle.objects.filter(title=title).first()
        if article:
            url = article.get_url()
            print(f'✅ "{title}"')
            print(f'    URL: {url or "No URL"}')
            print(f'    Slug: {article.slug}')
        else:
            print(f'❌ Not found: "{title}"')
    
    print(f'\n✅ FAQ structure verification complete!')
    print(f'Total FAQ articles: {FAQArticle.objects.count()}')
    print(f'Articles under FAQ Index: {FAQArticle.objects.child_of(faq_index).count()}')

if __name__ == '__main__':
    main()