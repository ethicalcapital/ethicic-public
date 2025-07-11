"""
Default values extracted from PricingPage class in public_site/models.py
These are the hardcoded defaults that need to be preserved before removing them from the model.
"""

PRICING_PAGE_DEFAULTS = {
    # Header section
    "section_header": "TRANSPARENT PRICING FOR EVERY CLIENT TYPE",
    "section_intro": "<p>Simple, transparent pricing based on how you access our services. Individual investors work directly with us at 1.00% annually. Institutional clients accessing through advisers or platforms pay 0.50% annually.</p>",
    
    # Individual Pricing Card
    "individual_badge": "INDIVIDUAL INVESTORS",
    "individual_title": "Direct Client Relationships",
    "individual_subtitle": "For individuals and families",
    "individual_price": "1.00%",
    "individual_price_period": "annually",
    "individual_features": """<ul>
<li>Work directly with Ethical Capital</li>
<li>Personalized portfolio management</li>
<li>Real-time reporting through client portal</li>
<li>Comprehensive reporting</li>
</ul>""",
    "individual_cta_text": "SCHEDULE CONSULTATION",
    "individual_cta_link": "/consultation/",
    
    # Institutional Pricing Card
    "institutional_badge": "INSTITUTIONAL PRICING",
    "institutional_title": "Adviser & Platform Access",
    "institutional_subtitle": "For RIAs, institutions, and platform clients",
    "institutional_price": "0.50%",
    "institutional_price_period": "annually",
    "institutional_features": """<ul>
<li>Access through Schwab, Altruist, or your preferred custodian</li>
<li>Direct access to CIO</li>
<li>SMA implementation</li>
<li>Quarterly performance reporting</li>
</ul>""",
    
    # Fee Details
    "fee_calculation_title": "Fee Calculation",
    "fee_calculation_text": "<p>Fees are calculated quarterly based on average daily balance and debited directly from your account. No hidden costs or transaction fees.</p>",
    "minimum_investment_title": "Minimum Investment",
    "minimum_investment_text": "<p>Direct management minimums vary by strategy. Schwab platform accounts follow standard SMA minimums. Contact us for current requirements.</p>",
    "pricing_rationale_title": "Why Different Pricing?",
    "pricing_rationale_text": "<p>Individual clients (1.00%) receive comprehensive personal service directly from us. Institutional clients (0.50%) access our strategies through their existing adviser relationships or platforms, reflecting economies of scale.</p>",
    
    # Workshop Section
    "workshop_section_header": "EDUCATIONAL WORKSHOPS & SPEAKING ENGAGEMENTS",
    "workshop_intro": "<p>Professional presentations on ethical investing, sustainable finance, and values-aligned wealth management. Topics range from foundational concepts to advanced portfolio construction strategies.</p>",
    "workshop_nonprofit_note": "<p><strong>Note:</strong> We provide complimentary presentations to mission-aligned nonprofit organizations and advocacy groups.</p>",
    "workshop_form_title": "Request a Workshop or Presentation",
    "show_workshop_form": True,
    
    # Additional Services Section
    "services_section_header": "ADDITIONAL SERVICES",
    "services_intro": "<p>Specialized services for institutional clients and platform partners.</p>",
    
    # CTA Section
    "cta_section_header": "LEARN MORE ABOUT US",
    "cta_title": "Explore our approach to ethical investing",
    "cta_description": "<p>Discover how we combine rigorous analysis with ethical principles to build portfolios that reflect your values.</p>",
    
    # Legacy fields (keeping for backward compatibility)
    "intro_text": "<p>Transparent pricing designed to scale with your practice.</p>",
    "enterprise_title": "Enterprise Solutions",
    "contact_cta": "<p>Ready to discuss pricing for your practice? <a href='/contact/'>Contact our team</a> for a personalized quote.</p>",
    
    # Note: The following fields have blank=True but no default value specified:
    # - pricing_description: RichTextField(blank=True)
    # - enterprise_description: RichTextField(blank=True)
    # - additional_services: StreamField(..., blank=True) - this is a StreamField, no default
}

# Fields that are blank=True but have NO default value (will be empty)
BLANK_FIELDS_NO_DEFAULT = [
    "pricing_description",
    "enterprise_description",
    "additional_services",  # StreamField with no default
]

# Summary of all fields with defaults
FIELDS_WITH_DEFAULTS = [
    "section_header",
    "section_intro",
    "individual_badge",
    "individual_title", 
    "individual_subtitle",
    "individual_price",
    "individual_price_period",
    "individual_features",
    "individual_cta_text",
    "individual_cta_link",
    "institutional_badge",
    "institutional_title",
    "institutional_subtitle", 
    "institutional_price",
    "institutional_price_period",
    "institutional_features",
    "fee_calculation_title",
    "fee_calculation_text",
    "minimum_investment_title",
    "minimum_investment_text",
    "pricing_rationale_title",
    "pricing_rationale_text",
    "workshop_section_header",
    "workshop_intro",
    "workshop_nonprofit_note",
    "workshop_form_title",
    "show_workshop_form",
    "services_section_header",
    "services_intro",
    "cta_section_header",
    "cta_title",
    "cta_description",
    "intro_text",
    "enterprise_title",
    "contact_cta",
]

print(f"Total fields with defaults: {len(FIELDS_WITH_DEFAULTS)}")
print(f"Fields with defaults: {', '.join(FIELDS_WITH_DEFAULTS)}")