#!/usr/bin/env python
"""
Script to preserve AdvisorPage content before removing hardcoded defaults.
"""

import os
import sys
import django
from django.conf import settings

# Set up Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ethicic.settings")
django.setup()

from public_site.models import AdvisorPage

# Import the defaults
exec(open('/Users/srvo/ethicic-public/advisor_page_defaults.py').read())

def apply_content_to_advisorpage():
    """Apply the preserved content to existing AdvisorPage instances."""
    try:
        # Find existing AdvisorPage instances
        advisor_pages = AdvisorPage.objects.all()
        
        if not advisor_pages.exists():
            print("No AdvisorPage instances found.")
            return True
        
        for advisor_page in advisor_pages:
            print(f"Updating AdvisorPage: {advisor_page.title}")
            updated_fields = []
            
            # Apply defaults to fields that are currently empty
            for field_name, default_value in ADVISOR_PAGE_DEFAULTS.items():
                if hasattr(advisor_page, field_name):
                    current_value = getattr(advisor_page, field_name)
                    
                    # If field is empty, set it to the preserved content
                    if not current_value:
                        setattr(advisor_page, field_name, default_value)
                        updated_fields.append(field_name)
            
            if updated_fields:
                advisor_page.save()
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
    print("=== ADVISORPAGE CONTENT PRESERVATION ===")
    print(f"Preserving content for {len(ADVISOR_PAGE_DEFAULTS)} fields")
    
    success = apply_content_to_advisorpage()
    if success:
        print("✅ Content preservation completed successfully")
    else:
        print("❌ Content preservation failed")