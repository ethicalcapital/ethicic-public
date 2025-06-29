"""
Temporary homepage view that renders the proper template with hardcoded content
"""
from django.shortcuts import render


def homepage_view(request):
    """Render the homepage with the proper template and hardcoded content"""
    context = {
        'page': {
            'hero_tagline': "We're not like other firms. Good.",
            'hero_title': 'Concentrated ethical portfolios for investors who refuse to compromise',
            'hero_subtitle': '<p>We hand-screen thousands of companies, exclude 57% of the S&P 500*, and build high-conviction portfolios where ethics and excellence converge. Fully transparent. Radically different. Fiduciary always.</p>',
            'excluded_percentage': '57%',
            'since_year': 'SINCE 2021',
            'philosophy_title': 'Ethics Reveal Quality',
            'philosophy_content': '<p>We view ethical screening not as a limitation, but a luxury. Eliminating low-quality companies upfront reveals something profound: the businesses that survive our scrutiny are those woven into the fabric of healthy social systems.</p><p>They grow because communities need them to grow. They succeed through reciprocal value exchange, not extraction. This insight—that ethics reveal quality—creates portfolios radically different from the market at large.</p>',
            'philosophy_highlight': 'When ethics and excellence converge, sustainable investing outcomes follow.',
            'principles_intro': '<p>Our investment approach is built on three foundational pillars that guide every decision we make.</p>',
            'process_principle_1_title': 'Rigorous Research',
            'process_principle_1_content': 'We conduct deep fundamental analysis on every company before inclusion.',
            'process_principle_2_title': 'Ethical Screening',
            'process_principle_2_content': 'Our comprehensive screening process excludes companies that conflict with our values.',
            'process_principle_3_title': 'Active Management',
            'process_principle_3_content': 'We continuously monitor and adjust portfolios based on changing conditions.',
            'practice_principle_1_title': 'Transparency',
            'practice_principle_1_content': 'Full disclosure of holdings and methodology to all clients.',
            'practice_principle_2_title': 'Fiduciary Standard',
            'practice_principle_2_content': 'We are legally bound to act in your best interests at all times.',
            'practice_principle_3_title': 'Alignment',
            'practice_principle_3_content': 'Our interests are aligned with yours through fee structures and shared values.',
            'strategies_intro': '<p>Choose from three distinct approaches, each designed to meet different investment objectives while maintaining our ethical standards.</p>',
            'process_step_1_title': 'Comprehensive Ethical Screening',
            'process_step_1_content': 'We begin where others end. Our multi-factor screening excludes companies involved in fossil fuels, weapons, tobacco, human rights violations, and those failing our governance standards. BDS-compliant and fully transparent.',
            'process_step_2_title': 'Fundamental Analysis',
            'process_step_2_content': 'Beyond exclusions, we seek quality. Every company is evaluated through six lenses: People, Product, Execution, Valuation, Moat, and Risk. We combine traditional analysis with proprietary research tools.',
            'process_step_3_title': 'Portfolio Construction',
            'process_step_3_content': 'From thousands screened to dozens analyzed to 15-25 owned. Each position is sized based on conviction, quality, and risk contribution. The result: high-conviction portfolios you can understand completely.',
            'process_step_4_title': 'Continuous Monitoring and Evolution',
            'process_step_4_content': 'Markets change. Companies evolve. Values clarify. We monitor holdings continuously, engage with clients regularly, and adapt portfolios thoughtfully. Your investments should always align with both your values and goals.',
            'serve_individual_title': 'Individual Investors',
            'serve_individual_content': 'High-net-worth individuals who want their investments to reflect their values.',
            'serve_advisor_title': 'Financial Advisors',
            'serve_advisor_content': 'Fee-only advisors seeking ethical investment solutions for their clients.',
            'serve_institution_title': 'Institutions',
            'serve_institution_content': 'Foundations, endowments, and other institutions with ethical mandates.',
            'cta_title': 'Ready to Get Started?',
            'cta_description': '<p>Schedule a consultation to discuss your investment goals and learn how our ethical approach can work for you.</p>',
            'client_availability_text': 'Currently accepting new clients',
            'disclaimer_text': '<p>Past performance does not guarantee future results. All investments carry risk of loss.</p>',
        }
    }
    
    return render(request, 'public_site/homepage_accessible.html', context)