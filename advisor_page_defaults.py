"""
AdvisorPage Default Values Dictionary
=====================================

This dictionary contains all default values from the AdvisorPage class fields.
Use this for content preservation when removing hardcoded defaults from the model.

Generated from: /Users/srvo/ethicic-public/public_site/models.py
Class: AdvisorPage (lines 3860-4165)
"""

ADVISOR_PAGE_DEFAULTS = {
    # Hero section
    "hero_title": "Partner with Ethical Capital",
    "hero_subtitle": "Deep research expertise and proven strategies to help you serve clients with complex values and sophisticated needs",
    "hero_description": "<p>As investment advisers ourselves, we understand the challenges of serving clients who want their portfolios to align with their principles. We provide the specialized research, proven strategies, and easy access you need to deliver exceptional outcomes.</p>",
    
    # Services section
    "services_title": "Advisory Services",
    "services_content": "<p>We provide investment advisers with specialized expertise in niche and ethical investing, rigorous analytical processes, effective client communication support, operational assistance, and educational resources to help you serve clients with complex needs and values.</p>",
    
    # What We Offer section
    "offer_section_title": "WHAT WE OFFER ADVISERS",
    "offer_section_intro": "<p>We provide investment advisers with institutional-grade research capabilities and proven strategies to confidently serve clients who prioritize ethical investing, without compromising on performance or professionalism.</p>",
    
    # Partnership Benefits section
    "benefits_section_title": "WHY ADVISERS CHOOSE US",
    "benefits_section_intro": "<p>Leading investment advisers partner with us because we deliver the institutional-grade expertise and transparency their sophisticated clients demand.</p>",
    
    # Process Overview section
    "process_section_title": "OUR COLLABORATIVE APPROACH",
    
    # Due Diligence Resources section
    "ddq_section_title": "DUE DILIGENCE RESOURCES",
    "ddq_section_subtitle": "Documentation for Investment Advisers",
    "ddq_section_description": "<p>Comprehensive documentation to support your due diligence process and adviser requirements.</p>",
    
    # CTA section
    "cta_section_title": "READY TO PARTNER?",
    "cta_primary_text": "SCHEDULE A CONSULTATION",
    "cta_primary_url": "https://tidycal.com/ecic/adviser",
    "cta_secondary_text": "SEND A MESSAGE",
    "cta_secondary_url": "/contact/",
    
    # Benefits section (Legacy)
    "benefits_title": "Why Partner With Us",
    "benefits_content": "<h4>Expertise in Niche and Ethical Investing</h4><p>Deep knowledge and specialized focus on sustainable and ethical investing. Our in-house ethical screening goes beyond standard third-party data, offering rigorous transparency that distinguishes us from conventional options.</p><h4>Rigorous Analytical Process</h4><p>Systematic approach to investment analysis with proprietary screening of thousands of companies using our 'Tick' rating system, ensuring strategies are both ethically aligned and financially sound.</p><h4>Effective Client Communication</h4><p>High closing rates with prospective clients through clear communication of complex financial concepts and personal engagement, helping manage the emotional aspects of investing.</p><h4>Operational Support</h4><p>Experience with platforms like Altruist and Schwab, streamlining account opening, transfers, and SMA implementation for busy advisers.</p><h4>Educational Partnership</h4><p>Trusted thought partner providing consulting, ad-hoc analysis, and insights to help you navigate challenging client scenarios and develop expertise in ethical investing.</p>",
    
    # Technology section
    "technology_title": "Technology Platform",
    "technology_content": "<p>Access our comprehensive platform for portfolio construction, compliance monitoring, and client reporting.</p>",
    
    # Legacy CTA section
    "cta_title": "Ready to Partner?",
    "cta_description": "<p>Join leading investment advisers who trust our multi-faceted approach to help them serve a broader range of clients with complex needs and values more effectively.</p>",
}

# Field types for reference
FIELD_TYPES = {
    # CharField fields
    "hero_title": "CharField",
    "hero_subtitle": "CharField", 
    "services_title": "CharField",
    "offer_section_title": "CharField",
    "benefits_section_title": "CharField",
    "process_section_title": "CharField",
    "ddq_section_title": "CharField",
    "ddq_section_subtitle": "CharField",
    "cta_section_title": "CharField",
    "cta_primary_text": "CharField",
    "cta_secondary_text": "CharField",
    "cta_secondary_url": "CharField",
    "benefits_title": "CharField",
    "technology_title": "CharField",
    "cta_title": "CharField",
    
    # URLField
    "cta_primary_url": "URLField",
    
    # RichTextField fields
    "hero_description": "RichTextField",
    "services_content": "RichTextField",
    "offer_section_intro": "RichTextField",
    "benefits_section_intro": "RichTextField",
    "ddq_section_description": "RichTextField",
    "benefits_content": "RichTextField",
    "technology_content": "RichTextField",
    "cta_description": "RichTextField",
    
    # StreamField fields (no defaults specified)
    "services_offered": "StreamField",
    "partnership_benefits": "StreamField",
    "process_steps": "StreamField",
    "resource_categories": "StreamField",
}

# Summary information
TOTAL_FIELDS_WITH_DEFAULTS = len(ADVISOR_PAGE_DEFAULTS)
RICHTEXT_FIELDS_WITH_DEFAULTS = len([k for k, v in FIELD_TYPES.items() if k in ADVISOR_PAGE_DEFAULTS and v == "RichTextField"])
CHARFIELD_FIELDS_WITH_DEFAULTS = len([k for k, v in FIELD_TYPES.items() if k in ADVISOR_PAGE_DEFAULTS and v == "CharField"])
URLFIELD_FIELDS_WITH_DEFAULTS = len([k for k, v in FIELD_TYPES.items() if k in ADVISOR_PAGE_DEFAULTS and v == "URLField"])

print(f"Total fields with defaults: {TOTAL_FIELDS_WITH_DEFAULTS}")
print(f"RichTextField fields with defaults: {RICHTEXT_FIELDS_WITH_DEFAULTS}")
print(f"CharField fields with defaults: {CHARFIELD_FIELDS_WITH_DEFAULTS}")
print(f"URLField fields with defaults: {URLFIELD_FIELDS_WITH_DEFAULTS}")
print(f"StreamField fields (no defaults): {len([k for k, v in FIELD_TYPES.items() if v == 'StreamField'])}")