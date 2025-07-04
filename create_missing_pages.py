#!/usr/bin/env python
"""Create missing pages in Wagtail."""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ethicic.settings')
django.setup()

from wagtail.models import Site, Page
from public_site.models_newsletter import NewsletterPage, AccessibilityPage

def create_pages():
    """Create newsletter and accessibility pages."""
    # Get the root page
    root_page = Page.objects.get(id=1)
    
    # Create Newsletter page if it doesn't exist
    if not NewsletterPage.objects.exists():
        print("Creating Newsletter page...")
        newsletter_page = NewsletterPage(
            title="Newsletter",
            slug="newsletter",
            intro_text="<p>Stay updated with the latest insights on ethical investing and portfolio management.</p>",
            benefits_title="Why Subscribe?",
            benefits_text="""<ul>
                <li>Monthly market insights and ethical investing trends</li>
                <li>Research updates and portfolio strategy discussions</li>
                <li>Early access to new features and investment opportunities</li>
                <li>Exclusive content not available on the website</li>
            </ul>""",
            privacy_text="<p>We respect your privacy. Your email will only be used for our newsletter and you can unsubscribe at any time.</p>"
        )
        root_page.add_child(instance=newsletter_page)
        newsletter_page.save_revision().publish()
        print("✓ Newsletter page created")
    else:
        print("Newsletter page already exists")
    
    # Create Accessibility page if it doesn't exist
    if not AccessibilityPage.objects.exists():
        print("Creating Accessibility page...")
        accessibility_page = AccessibilityPage(
            title="Accessibility Statement",
            slug="accessibility",
        )
        root_page.add_child(instance=accessibility_page)
        accessibility_page.save_revision().publish()
        print("✓ Accessibility page created")
    else:
        print("Accessibility page already exists")
    
    # Check if the pages are accessible
    try:
        site = Site.objects.get(is_default_site=True)
        print(f"\nPages created under site: {site.hostname}")
        print(f"Root page: {site.root_page.title}")
        
        # List all pages
        print("\nAll pages:")
        for page in Page.objects.live():
            print(f"  - {page.title} ({page.url_path})")
    except Site.DoesNotExist:
        print("\nNo default site found")

if __name__ == "__main__":
    create_pages()