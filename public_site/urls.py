"""Public Site URL Configuration
Complete URL routing for Wagtail-based public site with form handling and API endpoints
"""

from django.urls import path, re_path
from django.views.generic import RedirectView

from . import views


app_name = "public_site"

urlpatterns = [
    # ============================================================================
    # FORM SUBMISSION ENDPOINTS
    # ============================================================================
    # Contact form submission
    path("contact/submit/", views.contact_form_submit, name="contact_submit"),
    path("contact/success/", views.contact_success, name="contact_success"),
    # Contact page is handled by Wagtail routing
    # Newsletter signup
    path("newsletter/signup/", views.newsletter_signup, name="newsletter_subscribe"),
    # Onboarding form
    path("onboarding/submit/", views.onboarding_form_submit, name="onboarding_submit"),
    path("onboarding/thank-you/", views.onboarding_thank_you, name="onboarding_thank_you"),
    # Onboarding page is handled by Wagtail routing
    # ============================================================================
    # JSON API ENDPOINTS (for AJAX forms and integrations)
    # ============================================================================
    # Contact form API
    path("api/contact/", views.contact_api, name="api_contact"),
    # Newsletter signup API
    path("api/newsletter/", views.newsletter_api, name="api_newsletter"),
    # Site status and health check API
    path("api/status/", views.site_status_api, name="api_status"),
    # Media items API for infinite scroll
    path("api/media-items/", views.media_items_api, name="api_media_items"),
    # Support categories API removed for standalone deployment
    # ============================================================================
    # GARDEN PLATFORM ACCESS
    # ============================================================================
    # Garden platform redirect - removed for standalone deployment
    # Garden platform overview and access
    path("garden/", views.garden_overview, name="garden_overview"),
    path("api/garden/interest/", views.garden_interest_registration, name="garden_interest_registration"),
    # ============================================================================
    # SEARCH FUNCTIONALITY
    # ============================================================================
    # Site-wide search using Wagtail search
    path("search/", views.site_search, name="search"),
    path("search/live/", views.site_search_live, name="search_live"),
    # HTMX polling endpoints
    path("api/live-stats/", views.live_stats_api, name="api_live_stats"),
    path("api/notifications/count/", views.notifications_count_api, name="api_notifications_count"),
    path("api/notifications/", views.notifications_api, name="api_notifications"),
    path("api/notifications/mark-all-read/", views.mark_notifications_read_api, name="api_notifications_mark_read"),
    # Form validation endpoints
    path("api/validate-email/", views.validate_email_api, name="api_validate_email"),
    # Current Holdings transparency page - temporarily disabled for testing
    # path("holdings/", views.current_holdings, name="current_holdings"),
    # ============================================================================
    # URL REDIRECTS - Ethicic.com to EC1C.com Migration
    # ============================================================================
    # People page redirects to about
    path("people/", RedirectView.as_view(url="/about/", permanent=True), name="redirect_people"),
    # Strategy redirects
    path("how-we-invest/global-opportunities/", RedirectView.as_view(url="/strategies/growth/", permanent=True), name="redirect_growth"),
    path("how-we-invest/impact-income/", RedirectView.as_view(url="/strategies/income/", permanent=True), name="redirect_income"),
    path("how-we-invest/diversifying-allocation/", RedirectView.as_view(url="/strategies/diversification/", permanent=True), name="redirect_diversification"),
    # Process page redirect
    path("our-process/", RedirectView.as_view(url="/process/", permanent=True), name="redirect_process"),
    # Holdings page redirect
    path("what-we-own-and-why/", RedirectView.as_view(url="/strategies/", permanent=True), name="redirect_holdings"),
    # Support redirect
    path("helpandinsight/", RedirectView.as_view(url="/faq/", permanent=True), name="redirect_support"),
    # Legacy support URL redirect
    path("support/", RedirectView.as_view(url="/faq/", permanent=True), name="redirect_support_to_faq"),
    # Legal redirects
    # Redirect old legal URL to new disclosures URL
    path("legal/", RedirectView.as_view(url="/disclosures/", permanent=True), name="redirect_legal_to_disclosures"),
    # ============================================================================
    # UTILITY AND HELPER ENDPOINTS
    # ============================================================================
    # Site navigation helper (for dynamic menus)
    path("api/navigation/", views.get_site_navigation, name="api_navigation"),
    # Footer links helper (for dynamic footers)
    path("api/footer-links/", views.get_footer_links, name="api_footer"),
    # ============================================================================
    # DISCLOSURES PAGE
    # ============================================================================
    # Disclosures page (loads from database or fallback content)
    path("disclosures/", views.disclosures_page, name="disclosures"),
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
