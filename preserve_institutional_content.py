#!/usr/bin/env python
"""
Script to preserve InstitutionalPage content before removing hardcoded defaults.
"""

import os
import sys
import django
from django.conf import settings

# Set up Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ethicic.settings")
django.setup()

from public_site.models import InstitutionalPage

# Dictionary with all InstitutionalPage defaults
INSTITUTIONAL_PAGE_DEFAULTS = {
    # Hero section
    "hero_title": "Institutional Investment Solutions",
    "hero_subtitle": "Scalable ethical investment solutions for institutions, endowments, and pension funds",
    "hero_description": "<p>Custom investment strategies and compliance solutions designed for institutional scale and requirements.</p>",
    
    # Solutions section
    "solutions_title": "Institutional Solutions",
    "solutions_content": "<p>We work with institutions to implement ethical investment strategies at scale.</p>",
    
    # What We Offer section
    "offer_section_title": "WHAT WE OFFER INSTITUTIONS",
    "offer_section_intro": "<p>We provide institutions with proven ethical investment strategies that can be implemented at scale using liquid securities. Our approach focuses on delivering strategies that meet fiduciary standards while achieving alignment with institutional values and stakeholder expectations.</p>",
    
    # Partnership Benefits section
    "benefits_section_title": "WHY INSTITUTIONS CHOOSE US",
    "benefits_section_intro": "<p>Leading institutions partner with us because we deliver proven strategies, transparent methodology, and direct access to decision-makers that institutional fiduciary standards demand.</p>",
    
    # Process Overview section
    "process_section_title": "OUR INSTITUTIONAL APPROACH",
    
    # Scale & Capabilities section
    "scale_section_title": "INSTITUTIONAL SCALE & CAPABILITIES",
    "scale_section_intro": "<p>Our investment strategies and operational infrastructure are designed to support institutional-scale implementations with the rigor and transparency institutional oversight requires.</p>",
    
    # Due Diligence Resources section
    "ddq_section_title": "DUE DILIGENCE RESOURCES",
    "ddq_section_subtitle": "Documentation for Institutional Partners",
    "ddq_section_description": "<p>Comprehensive documentation to support your due diligence process and institutional requirements.</p>",
    
    # CTA section
    "cta_section_title": "READY TO PARTNER?",
    "cta_primary_text": "SCHEDULE INSTITUTIONAL CONSULTATION",
    "cta_primary_url": "https://tidycal.com/ecic/institutional",
    "cta_secondary_text": "SEND A MESSAGE",
    "cta_secondary_url": "/contact/",
    
    # Capabilities section (Legacy)
    "capabilities_title": "Our Capabilities",
    
    # Scale section (Legacy)
    "scale_title": "Institutional Scale",
    "scale_content": "<p>Our technology platform scales to handle institutional portfolio sizes and complexity.</p>",
    
    # CTA section (Legacy)
    "cta_title": "Discuss Your Needs",
    "cta_description": "<p>Contact us to explore how we can support your institutional investment objectives.</p>",
}

def apply_content_to_institutional():
    """Apply the preserved content to existing InstitutionalPage instances."""
    try:
        # Find existing InstitutionalPage instances
        institutional_pages = InstitutionalPage.objects.all()
        
        if not institutional_pages.exists():
            print("No InstitutionalPage instances found.")
            return True
        
        for institutional_page in institutional_pages:
            print(f"Updating InstitutionalPage: {institutional_page.title}")
            updated_fields = []
            
            # Apply defaults to fields that are currently empty
            for field_name, default_value in INSTITUTIONAL_PAGE_DEFAULTS.items():
                if hasattr(institutional_page, field_name):
                    current_value = getattr(institutional_page, field_name)
                    
                    # If field is empty, set it to the preserved content
                    if not current_value:
                        setattr(institutional_page, field_name, default_value)
                        updated_fields.append(field_name)
            
            if updated_fields:
                institutional_page.save()
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
    print("=== INSTITUTIONALPAGE CONTENT PRESERVATION ===")
    print(f"Preserving content for {len(INSTITUTIONAL_PAGE_DEFAULTS)} fields")
    
    success = apply_content_to_institutional()
    if success:
        print("✅ Content preservation completed successfully")
    else:
        print("❌ Content preservation failed")