"""
Temporary homepage view that renders the proper template with hardcoded content
"""

from django.shortcuts import render


def homepage_view(request):
    """Render the homepage with the proper template and hardcoded content"""
    context = {
        "page": {
            "hero_tagline": "We're not like other firms. Good.",
            "hero_title": "Concentrated ethical portfolios for investors who refuse to compromise",
            "hero_subtitle": "<p>We hand-screen thousands of companies, exclude 57% of the S&P 500*, and build high-conviction portfolios where ethics and excellence converge. Fully transparent. Radically different. Fiduciary always.</p>",
            "excluded_percentage": "57%",
            "since_year": "SINCE 2021",
            "philosophy_title": "Ethics Reveal Quality",
            "philosophy_content": "<p>We view ethical screening not as a limitation, but a luxury. Eliminating low-quality companies upfront reveals something profound: the businesses that survive our scrutiny are those woven into the fabric of healthy social systems.</p><p>They grow because communities need them to grow. They succeed through reciprocal value exchange, not extraction. This insight—that ethics reveal quality—creates portfolios radically different from the market at large.</p>",
            "philosophy_highlight": "When ethics and excellence converge, sustainable investing outcomes follow.",
            "principles_intro": "",
            "process_principle_1_title": "Rigorous Research",
            "process_principle_1_content": "We conduct deep fundamental analysis on every company before inclusion.",
            "process_principle_2_title": "Ethical Screening",
            "process_principle_2_content": "Our comprehensive screening process excludes companies that conflict with our values.",
            "process_principle_3_title": "Active Management",
            "process_principle_3_content": "We continuously monitor and adjust portfolios based on changing conditions.",
            "practice_principle_1_title": "Transparency",
            "practice_principle_1_content": "Full disclosure of holdings and methodology to all clients.",
            "practice_principle_2_title": "Fiduciary Standard",
            "practice_principle_2_content": "We are legally bound to act in your best interests at all times.",
            "practice_principle_3_title": "Alignment",
            "practice_principle_3_content": "Our interests are aligned with yours through fee structures and shared values.",
            "strategies_intro": "<p>Choose from three distinct approaches, each designed to meet different investment objectives while maintaining our ethical standards.</p>",
            "process_step_1_title": "Comprehensive Ethical Screening",
            "process_step_1_content": "<strong>We begin where others end.</strong> Our multi-factor screening excludes companies involved in fossil fuels, weapons systems, factory farming, tobacco, gambling, and those failing our governance standards. This isn't performative—it's foundational. We cast a wide net, continuously monitoring corporate behavior, partnerships, and evolving business models. When companies disappoint, we divest. When emerging risks appear, we investigate.",
            "process_step_2_title": "Fundamental Analysis",
            "process_step_2_content": "<strong>Ethics alone don't make an investment.</strong> From the companies that pass our screens, we identify those with durable competitive advantages. We evaluate business quality through multiple lenses: market position, financial strength, management integrity, and growth sustainability. This isn't about finding perfect companies—it's about understanding which imperfect companies are worth owning and at what price.",
            "process_step_3_title": "Portfolio Construction",
            "process_step_3_content": "<strong>From thousands screened to hundreds researched to 15-25 owned.</strong> We size positions based on conviction level, business quality, and risk contribution. Concentration enforces discipline—every holding must earn its place. The result: portfolios where you understand what you own, why you own it, and how each position contributes to your long-term objectives.",
            "process_step_4_title": "Continuous Monitoring and Evolution",
            "process_step_4_content": "<strong>Investing isn't static.</strong> We monitor holdings daily, reassess theses quarterly, and evolve our process continuously. When facts change, we act. When clients raise concerns, we investigate. When new risks emerge, we adapt. This isn't passive indexing—it's active stewardship of capital aligned with values that matter.",
            "serve_individual_title": "Individual Investors",
            "serve_individual_content": "People who want their investments to reflect their values.",
            "serve_advisor_title": "Financial Advisors",
            "serve_advisor_content": "Fee-only advisors seeking ethical investment solutions for their clients.",
            "serve_institution_title": "Institutions",
            "serve_institution_content": "Foundations, endowments, and other institutions with ethical mandates.",
            "cta_title": "Let's start our journey together.",
            "cta_description": "",
            "client_availability_text": "Currently accepting new clients",
            "disclaimer_text": "<p>Past performance does not guarantee future results. All investments carry risk of loss.</p>",
        }
    }

    return render(request, "public_site/homepage_accessible.html", context)
