"""Public Site URL Configuration
Complete URL routing for Wagtail-based public site with form handling and API endpoints
"""

from django.urls import path, include
from django.views.generic import RedirectView

from .views import (
    contact_form_submit, contact_success, newsletter_signup,
    test_clean_nav, test_form, onboarding_form_submit, onboarding_thank_you,
    contact_api, newsletter_api, site_status_api, media_items_api,
    garden_overview, garden_interest_registration,
    site_search, site_search_live, live_stats_api, notifications_count_api,
    notifications_api, mark_notifications_read_api, validate_email_api,
    theme_api, check_submission_status, get_site_navigation, get_footer_links,
    disclosures_page
)

app_name = "public_site"

urlpatterns = [
    # ============================================================================
    # FORM SUBMISSION ENDPOINTS
    # ============================================================================
    # Contact form submission
    path("contact/submit/", contact_form_submit, name="contact_submit"),
    path("contact/success/", contact_success, name="contact_success"),
    # Contact page is handled by Wagtail routing
    # Newsletter signup
    path("newsletter/signup/", newsletter_signup, name="newsletter_subscribe"),
    # Test clean navigation
    path("test-clean-nav/", test_clean_nav, name="test_clean_nav"),
    # Test form inputs
    path("test-form/", test_form, name="test_form"),
    # Onboarding form
    path("onboarding/submit/", onboarding_form_submit, name="onboarding_submit"),
    path(
        "onboarding/thank-you/", onboarding_thank_you, name="onboarding_thank_you"
    ),
    # Onboarding page is handled by Wagtail routing
    # ============================================================================
    # JSON API ENDPOINTS (for AJAX forms and integrations)
    # ============================================================================
    # Contact form API
    path("api/contact/", contact_api, name="api_contact"),
    # Newsletter signup API
    path("api/newsletter/", newsletter_api, name="api_newsletter"),
    # Site status and health check API
    path("api/status/", site_status_api, name="api_status"),
    # Media items API for infinite scroll
    path("api/media-items/", media_items_api, name="api_media_items"),
    # Support categories API removed for standalone deployment
    # ============================================================================
    # GARDEN PLATFORM ACCESS
    # ============================================================================
    # Garden platform redirect - removed for standalone deployment
    # Garden platform overview and access
    path("garden/", garden_overview, name="garden_overview"),
    path(
        "api/garden/interest/",
        garden_interest_registration,
        name="garden_interest_registration",
    ),
    # ============================================================================
    # SEARCH FUNCTIONALITY
    # ============================================================================
    # Site-wide search using Wagtail search
    path("search/", site_search, name="search"),
    path("search/live/", site_search_live, name="search_live"),
    # HTMX polling endpoints
    path("api/live-stats/", live_stats_api, name="api_live_stats"),
    path(
        "api/notifications/count/",
        notifications_count_api,
        name="api_notifications_count",
    ),
    path("api/notifications/", notifications_api, name="api_notifications"),
    path(
        "api/notifications/mark-all-read/",
        mark_notifications_read_api,
        name="api_notifications_mark_read",
    ),
    # Form validation endpoints
    path("api/validate-email/", validate_email_api, name="api_validate_email"),
    # Theme preference API
    path("api/theme/set/", theme_api, name="api_theme"),
    # Form submission status checking
    path(
        "api/submission-status/<str:submission_id>/",
        check_submission_status,
        name="api_submission_status",
    ),
    # Current Holdings transparency page - temporarily disabled for testing
    # path("holdings/", current_holdings, name="current_holdings"),
    # Note: Media files are served by Django/WhiteNoise and configured in main urls.py
    # ============================================================================
    # URL REDIRECTS - Ethicic.com to EC1C.com Migration
    # ============================================================================
    # People page redirects to about
    path(
        "people/",
        RedirectView.as_view(url="/about/", permanent=True),
        name="redirect_people",
    ),
    # Strategy redirects
    path(
        "how-we-invest/global-opportunities/",
        RedirectView.as_view(url="/strategies/growth/", permanent=True),
        name="redirect_growth",
    ),
    path(
        "how-we-invest/impact-income/",
        RedirectView.as_view(url="/strategies/income/", permanent=True),
        name="redirect_income",
    ),
    path(
        "how-we-invest/diversifying-allocation/",
        RedirectView.as_view(url="/strategies/diversification/", permanent=True),
        name="redirect_diversification",
    ),
    # Process page redirect
    path(
        "our-process/",
        RedirectView.as_view(url="/process/", permanent=True),
        name="redirect_process",
    ),
    # Holdings page redirect
    path(
        "what-we-own-and-why/",
        RedirectView.as_view(url="/strategies/", permanent=True),
        name="redirect_holdings",
    ),
    # Support redirect
    path(
        "helpandinsight/",
        RedirectView.as_view(url="/faq/", permanent=True),
        name="redirect_support",
    ),
    # Legacy support URL redirect
    path(
        "support/",
        RedirectView.as_view(url="/faq/", permanent=True),
        name="redirect_support_to_faq",
    ),
    # Ethical Capital FAQ redirects (fix for 404s on /ethical-capital/faq/* URLs)
    path(
        "ethical-capital/faq/",
        RedirectView.as_view(url="/faq/", permanent=True),
        name="redirect_ethical_capital_faq_index",
    ),
    path(
        "ethical-capital/faq/<path:slug>/",
        RedirectView.as_view(url="/faq/%(slug)s/", permanent=True),
        name="redirect_ethical_capital_faq_articles",
    ),
    # Legal redirects
    # Redirect old legal URL to new disclosures URL
    path(
        "legal/",
        RedirectView.as_view(url="/disclosures/", permanent=True),
        name="redirect_legal_to_disclosures",
    ),
    # ============================================================================
    # BROKEN LINKS FIX REDIRECTS - July 2025
    # ============================================================================
    # Form ADV to SEC document
    path(
        "disclosures/form-adv/",
        RedirectView.as_view(
            url="https://reports.adviserinfo.sec.gov/reports/ADV/316032/PDF/316032.pdf",
            permanent=True,
        ),
        name="redirect_form_adv",
    ),
    # Research page to blog
    path(
        "research/",
        RedirectView.as_view(url="/blog/", permanent=True),
        name="redirect_research_to_blog",
    ),
    # Process screening to main process
    path(
        "our-process/screening/",
        RedirectView.as_view(url="/process/", permanent=True),
        name="redirect_screening",
    ),
    # Reach out to contact
    path(
        "reach-out/",
        RedirectView.as_view(url="/contact/", permanent=True),
        name="redirect_reach_out",
    ),
    # Fix strategies typo
    path(
        "strategies/global-opportunitites/",
        RedirectView.as_view(url="/strategies/growth/", permanent=True),
        name="redirect_strategies_typo",
    ),
    # Blog post slug redirects
    path(
        "blog/what-does-inflation-mean-to-you/",
        RedirectView.as_view(
            url="/blog/the-progressive-view-of-inflation/", permanent=True
        ),
        name="redirect_inflation_blog",
    ),
    path(
        "blog/what-should-you-expect-when-youre-investing/",
        RedirectView.as_view(
            url="/blog/stock-market-performance-what-should-you-expect/", permanent=True
        ),
        name="redirect_investing_expectations_blog",
    ),
    # Charitable giving resources - redirect to correct blog post
    path(
        "charitable-giving-resources/",
        RedirectView.as_view(url="/blog/charitable-giving-resources/", permanent=True),
        name="redirect_charitable_giving",
    ),
    # Privacy and Terms redirects to disclosures page
    path(
        "privacy-policy/",
        RedirectView.as_view(url="/disclosures/", permanent=True),
        name="redirect_privacy_to_disclosures",
    ),
    path(
        "terms-of-service/",
        RedirectView.as_view(url="/disclosures/", permanent=True),
        name="redirect_terms_to_disclosures",
    ),
    # ============================================================================
    # UTILITY AND HELPER ENDPOINTS
    # ============================================================================
    # Site navigation helper (for dynamic menus)
    path("api/navigation/", get_site_navigation, name="api_navigation"),
    # Footer links helper (for dynamic footers)
    path("api/footer-links/", get_footer_links, name="api_footer"),
    # ============================================================================
    # DISCLOSURES PAGE
    # ============================================================================
    # Disclosures page (loads from database or fallback content)
    path("disclosures/", disclosures_page, name="disclosures"),
    # ============================================================================
    # AI-POWERED CONTENT ANALYSIS ENDPOINTS
    # ============================================================================
    # AI analysis API for blog content creation (admin only)
    # Note: AI APIs are handled by the main garden web container
    # path("admin/", include("public_site.urls_ai")),
    # ============================================================================
    # NOTE: Most public site page URLs are handled by Wagtail's routing system
    # ============================================================================
    #
    # The following page types are automatically routed by Wagtail:
    # - HomePage (/)
    # - AboutPage (/about/)
    # - PricingPage (/pricing/)
    # - ContactPage (/contact/)
    # - BlogIndexPage (/blog/)
    # - BlogPost (/blog/post-slug/)
    # - FAQPage (/faq/ or /support/)
    # - LegalPage (/legal/privacy/, /legal/terms/, etc.)
    # - MediaPage (/media/)
    # - ResearchPage (/research/)
    # - ProcessPage (/process/)
    # - CompliancePage (/compliance/*)
    # - OnboardingPage (/onboarding/)
    # - StrategyPage (/strategies/*)
    # - FAQIndexPage (/faq/)
    # - FAQArticle (/faq/article-slug/)
    # - ContactFormPage (/contact-form/)
    # - EncyclopediaIndexPage (/encyclopedia/) [commented out in models]
    # - EncyclopediaEntry (/encyclopedia/term/) [commented out in models]
    #
    # These are defined in the main dewey_django/urls.py as:
    # re_path(r'', include(wagtail_urls))  # Wagtail catch-all (must be last)
]
