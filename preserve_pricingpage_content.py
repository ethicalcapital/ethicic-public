#!/usr/bin/env python
"""
Script to preserve PricingPage content before removing hardcoded defaults.
"""

import os
import sys
import django
from django.conf import settings

# Set up Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ethicic.settings")
django.setup()

from public_site.models import PricingPage

# Import the defaults
exec(open('/Users/srvo/ethicic-public/pricing_page_defaults.py').read())

def apply_content_to_pricingpage():
    """Apply the preserved content to existing PricingPage instances."""
    try:
        # Find existing PricingPage instances
        pricing_pages = PricingPage.objects.all()
        
        if not pricing_pages.exists():
            print("No PricingPage instances found.")
            return True
        
        for pricing_page in pricing_pages:
            print(f"Updating PricingPage: {pricing_page.title}")
            updated_fields = []
            
            # Apply defaults to fields that are currently empty
            for field_name, default_value in PRICING_PAGE_DEFAULTS.items():
                if hasattr(pricing_page, field_name):
                    current_value = getattr(pricing_page, field_name)
                    
                    # If field is empty, set it to the preserved content
                    if not current_value:
                        setattr(pricing_page, field_name, default_value)
                        updated_fields.append(field_name)
            
            if updated_fields:
                pricing_page.save()
                print(f"Updated {len(updated_fields)} fields: {updated_fields[:5]}...")
            else:
                print("No fields needed updating - content already exists")
                
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    print("=== PRICINGPAGE CONTENT PRESERVATION ===")
    print(f"Preserving content for {len(PRICING_PAGE_DEFAULTS)} fields")
    
    success = apply_content_to_pricingpage()
    if success:
        print("✅ Content preservation completed successfully")
    else:
        print("❌ Content preservation failed")