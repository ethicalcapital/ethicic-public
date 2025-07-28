from typing import ClassVar

from django.core.paginator import Paginator
from django.db import models
from django.utils import timezone
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from taggit.models import TaggedItemBase
from wagtail import blocks
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.contrib.routable_page.models import RoutablePageMixin, path
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.contrib.table_block.blocks import TableBlock
from wagtail.fields import RichTextField, StreamField
from wagtail.images.blocks import ImageChooserBlock
from wagtail.models import Orderable, Page
from wagtail.search import index

# Import StreamField blocks
# Import models from other modules
from .models_newsletter import AccessibilityPage, NewsletterPage  # noqa: F401

# ============================================================================
# PAGE MODELS
# ============================================================================
# These are Wagtail Page models that represent different page types on the site


class SafeUrlMixin:
    """
    Mixin class that provides safe URL generation methods for Wagtail pages.
    Handles cases where standard URL methods might return None.
    """

    def get_safe_url(self, request=None, fallback_url="#"):
        """
        Generate a safe URL for this page, handling None values gracefully.

        Args:
            request: Django request object (optional)
            fallback_url: URL to use if page URL cannot be determined

        Returns:
            str: A valid URL or the fallback URL
        """
        # Try multiple method to get a valid URL
        url = None

        # Method 1: Try the standard url property
        try:
            url = self.url
            if url and url != "None" and url.strip():
                return url
        except (AttributeError, Exception):
            pass

        # Method 2: Try get_url() method
        try:
            url = self.get_url(request=request)
            if url and url != "None" and url.strip():
                return url
        except (AttributeError, Exception):
            pass

        # Method 3: Try get_full_url() method
        try:
            url = self.get_full_url(request=request)
            if url and url != "None" and url.strip():
                return url
        except (AttributeError, Exception):
            pass

        # Method 4: Construct URL from url_path if available
        try:
            if hasattr(self, "url_path") and self.url_path:
                url_path = self.url_path.strip()
                if url_path and url_path != "/":
                    # Remove any leading duplicate slashes and ensure single leading slash
                    url_path = "/" + url_path.lstrip("/")
                    if url_path != "None" and url_path != "/None":
                        return url_path
        except (AttributeError, Exception):
            pass

        # Method 5: If all else fails, try to construct from slug
        try:
            if hasattr(self, "slug") and self.slug:
                slug = self.slug.strip()
                if slug and slug != "None":
                    # For most pages, we can construct the URL as /slug/
                    constructed_url = f"/{slug}/"
                    return constructed_url
        except (AttributeError, Exception):
            pass

        # Last resort: return fallback URL
        return fallback_url

    def get_safe_absolute_url(self, request=None, fallback_url="#"):
        """
        Generate a safe absolute URL for this page.

        Args:
            request: Django request object (optional)
            fallback_url: URL to use if page URL cannot be determined

        Returns:
            str: A valid absolute URL or the fallback URL
        """
        # Get the relative URL first
        relative_url = self.get_safe_url(request=request, fallback_url=None)

        if not relative_url or relative_url == "#":
            return fallback_url

        # If it's already absolute, return it
        if relative_url.startswith("http"):
            return relative_url

        # Construct absolute URL
        try:
            if request:
                # Use request to build absolute URL
                scheme = "https" if request.is_secure() else "http"
                host = request.get_host()
                return f"{scheme}://{host}{relative_url}"
        except (AttributeError, Exception):
            pass

        # Fallback to site domain if available
        try:
            if hasattr(self, "get_site"):
                site = self.get_site()
                if site and hasattr(site, "root_url"):
                    return f"{site.root_url.rstrip('/')}{relative_url}"
        except (AttributeError, Exception):
            pass

        return fallback_url


class HomePage(SafeUrlMixin, Page):
    """Homepage model for Ethical Capital Investment Collaborative."""

    template = "public_site/homepage_tailwind.html"

    # Hero Section - Main banner content
    hero_tagline = models.CharField(
        max_length=100,
        blank=True,
    )
    hero_title = models.CharField(
        max_length=300,
        blank=True,
        help_text="Main homepage headline",
    )
    hero_subtitle = RichTextField(
        blank=True,
        help_text="Hero description text",
    )

    # Hero Stats
    excluded_percentage = models.CharField(
        max_length=10,
        blank=True,
        help_text="Percentage of S&P 500 excluded",
    )
    since_year = models.CharField(
        max_length=20,
        blank=True,
        help_text="Year established or founding info",
    )

    # Investment Philosophy Section
    philosophy_title = models.CharField(
        max_length=200,
        blank=True,
    )
    philosophy_content = RichTextField(
        blank=True,
        help_text="Investment philosophy description",
    )
    philosophy_highlight = models.CharField(
        max_length=300,
        blank=True,
        help_text="Key philosophy statement",
    )

    # Section Headers - CMS Manageable
    philosophy_section_header = models.CharField(
        max_length=100,
        blank=True,
        help_text="Section header for investment philosophy",
    )
    principles_section_header = models.CharField(
        max_length=100,
        blank=True,
        help_text="Section header for principles",
    )
    strategies_section_header = models.CharField(
        max_length=100,
        blank=True,
        help_text="Section header for strategies",
    )
    process_section_header = models.CharField(
        max_length=100,
        blank=True,
        help_text="Section header for process",
    )
    serve_section_header = models.CharField(
        max_length=100,
        blank=True,
        help_text="Section header for who we serve",
    )
    cta_section_header = models.CharField(
        max_length=100,
        blank=True,
        help_text="Section header for call to action",
    )

    # Principles Section
    principles_intro = RichTextField(
        blank=True,
    )

    # Process Principles
    process_principle_1_title = models.CharField(max_length=100, blank=True)
    process_principle_1_content = models.TextField(
        blank=True,
    )

    process_principle_2_title = models.CharField(max_length=100, blank=True)
    process_principle_2_content = models.TextField(
        blank=True,
    )

    process_principle_3_title = models.CharField(max_length=100, blank=True)
    process_principle_3_content = models.TextField(
        blank=True,
    )

    # Practice Principles
    practice_principle_1_title = models.CharField(max_length=100, blank=True)
    practice_principle_1_content = models.TextField(
        blank=True,
    )

    practice_principle_2_title = models.CharField(max_length=100, blank=True)
    practice_principle_2_content = models.TextField(
        blank=True,
    )

    practice_principle_3_title = models.CharField(max_length=100, blank=True)
    practice_principle_3_content = models.TextField(
        blank=True,
    )

    # Strategies Section
    strategies_intro = RichTextField(
        blank=True,
    )

    # Process Section
    process_title = models.CharField(max_length=200, blank=True)

    process_step_1_title = models.CharField(max_length=100, blank=True)
    process_step_1_content = models.TextField(
        blank=True,
    )

    process_step_2_title = models.CharField(max_length=100, blank=True)
    process_step_2_content = models.TextField(
        blank=True,
    )

    process_step_3_title = models.CharField(max_length=100, blank=True)
    process_step_3_content = models.TextField(
        blank=True,
    )

    process_step_4_title = models.CharField(max_length=100, blank=True)
    process_step_4_content = models.TextField(
        blank=True,
    )

    # Who We Serve Section
    serve_individual_title = models.CharField(max_length=100, blank=True)
    serve_individual_content = models.TextField(
        blank=True,
    )

    serve_advisor_title = models.CharField(max_length=100, blank=True)
    serve_advisor_content = models.TextField(
        blank=True,
    )

    serve_institution_title = models.CharField(max_length=100, blank=True)
    serve_institution_content = models.TextField(
        blank=True,
    )

    # CTA Section
    cta_title = models.CharField(
        max_length=200,
        blank=True,
    )
    cta_description = RichTextField(
        blank=True,
    )

    # CTA Info Items
    minimum_investment_text = models.CharField(max_length=100, blank=True)
    client_availability_text = models.CharField(max_length=100, blank=True)

    # Footer/Disclaimer Content
    disclaimer_text = RichTextField(
        blank=True,
        help_text="Legal disclaimer and footnotes",
    )

    # Strategy Cards - Growth Strategy
    strategy_1_name = models.CharField(
        max_length=100,
        blank=True,
        help_text="Name of the first strategy",
    )
    strategy_1_subtitle = models.CharField(
        max_length=100,
        blank=True,
        help_text="Subtitle for first strategy",
    )
    strategy_1_focus = models.CharField(
        max_length=100,
        blank=True,
        help_text="Focus value for growth strategy",
    )
    strategy_1_screening = models.CharField(
        max_length=100,
        blank=True,
        help_text="Screening value for growth strategy",
    )
    strategy_1_management = models.CharField(
        max_length=100,
        blank=True,
        help_text="Management value for growth strategy",
    )
    strategy_1_ownership = models.CharField(
        max_length=100,
        blank=True,
        help_text="Ownership value for growth strategy",
    )
    strategy_1_description = models.TextField(
        blank=True,
        help_text="Description for growth strategy",
    )
    strategy_1_link = models.CharField(
        max_length=200,
        blank=True,
        help_text="Link URL for growth strategy",
    )
    strategy_1_link_text = models.CharField(
        max_length=100,
        blank=True,
        help_text="Link text for growth strategy",
    )

    # Strategy Cards - Income Strategy
    strategy_2_name = models.CharField(
        max_length=100,
        blank=True,
        help_text="Name of the second strategy",
    )
    strategy_2_subtitle = models.CharField(
        max_length=100,
        blank=True,
        help_text="Subtitle for second strategy",
    )
    strategy_2_focus = models.CharField(
        max_length=100,
        blank=True,
        help_text="Focus value for income strategy",
    )
    strategy_2_screening = models.CharField(
        max_length=100,
        blank=True,
        help_text="Screening value for income strategy",
    )
    strategy_2_management = models.CharField(
        max_length=100,
        blank=True,
        help_text="Management value for income strategy",
    )
    strategy_2_ownership = models.CharField(
        max_length=100,
        blank=True,
        help_text="Ownership value for income strategy",
    )
    strategy_2_description = models.TextField(
        blank=True,
        help_text="Description for income strategy",
    )
    strategy_2_link = models.CharField(
        max_length=200,
        blank=True,
        help_text="Link URL for income strategy",
    )
    strategy_2_link_text = models.CharField(
        max_length=100,
        blank=True,
        help_text="Link text for income strategy",
    )

    # Strategy Cards - Diversification Strategy
    strategy_3_name = models.CharField(
        max_length=100,
        blank=True,
        help_text="Name of the third strategy",
    )
    strategy_3_subtitle = models.CharField(
        max_length=100,
        blank=True,
        help_text="Subtitle for third strategy",
    )
    strategy_3_focus = models.CharField(
        max_length=100,
        blank=True,
        help_text="Focus value for diversification strategy",
    )
    strategy_3_screening = models.CharField(
        max_length=100,
        blank=True,
        help_text="Screening value for diversification strategy",
    )
    strategy_3_management = models.CharField(
        max_length=100,
        blank=True,
        help_text="Management value for diversification strategy",
    )
    strategy_3_ownership = models.CharField(
        max_length=100,
        blank=True,
        help_text="Ownership value for diversification strategy",
    )
    strategy_3_description = models.TextField(
        blank=True,
        help_text="Description for diversification strategy",
    )
    strategy_3_link = models.CharField(
        max_length=200,
        blank=True,
        help_text="Link URL for diversification strategy",
    )
    strategy_3_link_text = models.CharField(
        max_length=100,
        blank=True,
        help_text="Link text for diversification strategy",
    )

    # Strategy Table Labels
    strategy_label_focus = models.CharField(
        max_length=50,
        blank=True,
        help_text="Label for strategy focus row",
    )
    strategy_label_screening = models.CharField(
        max_length=50,
        blank=True,
        help_text="Label for strategy screening row",
    )
    strategy_label_management = models.CharField(
        max_length=50,
        blank=True,
        help_text="Label for strategy management row",
    )
    strategy_label_ownership = models.CharField(
        max_length=50,
        blank=True,
        help_text="Label for strategy ownership row",
    )

    # Hero CTA Links
    hero_cta_1_link = models.CharField(
        max_length=200,
        blank=True,
        help_text="First hero CTA link URL",
    )
    hero_cta_1_text = models.CharField(
        max_length=100,
        blank=True,
        help_text="First hero CTA link text",
    )
    hero_cta_2_link = models.CharField(
        max_length=200,
        blank=True,
        help_text="Second hero CTA link URL",
    )
    hero_cta_2_text = models.CharField(
        max_length=100,
        blank=True,
        help_text="Second hero CTA link text",
    )

    # Who We Serve Links
    serve_individual_link = models.CharField(
        max_length=200,
        blank=True,
        help_text="Individual investors link URL",
    )
    serve_individual_link_text = models.CharField(
        max_length=100,
        blank=True,
        help_text="Individual investors link text",
    )
    serve_advisor_link = models.CharField(
        max_length=200,
        blank=True,
        help_text="Financial advisors link URL",
    )
    serve_advisor_link_text = models.CharField(
        max_length=100,
        blank=True,
        help_text="Financial advisors link text",
    )
    serve_institution_link = models.CharField(
        max_length=200,
        blank=True,
        help_text="Institutions link URL",
    )
    serve_institution_link_text = models.CharField(
        max_length=100,
        blank=True,
        help_text="Institutions link text",
    )

    # Process Section Link
    process_section_link = models.CharField(
        max_length=200,
        blank=True,
        help_text="Process section link URL",
    )
    process_section_link_text = models.CharField(
        max_length=100,
        blank=True,
        help_text="Process section link text",
    )

    # Bottom CTA Links
    cta_button_1_link = models.CharField(
        max_length=200,
        blank=True,
        help_text="Bottom CTA first button link URL",
    )
    cta_button_1_text = models.CharField(
        max_length=100,
        blank=True,
        help_text="Bottom CTA first button text",
    )
    cta_button_2_link = models.CharField(
        max_length=200,
        blank=True,
        help_text="Bottom CTA second button link URL",
    )
    cta_button_2_text = models.CharField(
        max_length=100,
        blank=True,
        help_text="Bottom CTA second button text",
    )

    # Miscellaneous Fields
    hero_stats_date = models.CharField(
        max_length=50,
        blank=True,
        help_text="Date text for hero statistics",
    )
    process_subsection_header = models.CharField(
        max_length=50,
        blank=True,
        help_text="Process subsection header in principles",
    )
    practice_subsection_header = models.CharField(
        max_length=50,
        blank=True,
        help_text="Practice subsection header in principles",
    )
    accepting_clients_icon = models.CharField(
        max_length=10,
        blank=True,
        help_text="Icon for accepting clients indicator",
    )
    content_panels: ClassVar[list] = [
        *Page.content_panels,
        MultiFieldPanel(
            [
                FieldPanel("hero_tagline"),
                FieldPanel("hero_title"),
                FieldPanel("hero_subtitle"),
                FieldPanel("excluded_percentage"),
                FieldPanel("since_year"),
            ],
            heading="Hero Section",
        ),
        MultiFieldPanel(
            [
                FieldPanel("philosophy_section_header"),
                FieldPanel("philosophy_title"),
                FieldPanel("philosophy_content"),
                FieldPanel("philosophy_highlight"),
            ],
            heading="Investment Philosophy",
        ),
        MultiFieldPanel(
            [FieldPanel("principles_section_header"), FieldPanel("principles_intro")],
            heading="Principles Introduction",
        ),
        MultiFieldPanel(
            [
                FieldPanel("process_principle_1_title"),
                FieldPanel("process_principle_1_content"),
                FieldPanel("process_principle_2_title"),
                FieldPanel("process_principle_2_content"),
                FieldPanel("process_principle_3_title"),
                FieldPanel("process_principle_3_content"),
            ],
            heading="Process Principles",
        ),
        MultiFieldPanel(
            [
                FieldPanel("practice_principle_1_title"),
                FieldPanel("practice_principle_1_content"),
                FieldPanel("practice_principle_2_title"),
                FieldPanel("practice_principle_2_content"),
                FieldPanel("practice_principle_3_title"),
                FieldPanel("practice_principle_3_content"),
            ],
            heading="Practice Principles",
        ),
        MultiFieldPanel(
            [FieldPanel("strategies_section_header"), FieldPanel("strategies_intro")],
            heading="Strategies Introduction",
        ),
        MultiFieldPanel(
            [
                FieldPanel("process_section_header"),
                FieldPanel("process_title"),
                FieldPanel("process_step_1_title"),
                FieldPanel("process_step_1_content"),
                FieldPanel("process_step_2_title"),
                FieldPanel("process_step_2_content"),
                FieldPanel("process_step_3_title"),
                FieldPanel("process_step_3_content"),
                FieldPanel("process_step_4_title"),
                FieldPanel("process_step_4_content"),
            ],
            heading="Process Steps",
        ),
        MultiFieldPanel(
            [
                FieldPanel("serve_section_header"),
                FieldPanel("serve_individual_title"),
                FieldPanel("serve_individual_content"),
                FieldPanel("serve_advisor_title"),
                FieldPanel("serve_advisor_content"),
                FieldPanel("serve_institution_title"),
                FieldPanel("serve_institution_content"),
            ],
            heading="Who We Serve",
        ),
        MultiFieldPanel(
            [
                FieldPanel("cta_section_header"),
                FieldPanel("cta_title"),
                FieldPanel("cta_description"),
                FieldPanel("minimum_investment_text"),
                FieldPanel("client_availability_text"),
            ],
            heading="Call to Action",
        ),
        MultiFieldPanel([FieldPanel("disclaimer_text")], heading="Footer & Disclaimer"),
        MultiFieldPanel(
            [
                FieldPanel("hero_cta_1_link"),
                FieldPanel("hero_cta_1_text"),
                FieldPanel("hero_cta_2_link"),
                FieldPanel("hero_cta_2_text"),
                FieldPanel("hero_stats_date"),
            ],
            heading="Hero Section Links & Settings",
        ),
        MultiFieldPanel(
            [
                FieldPanel("process_subsection_header"),
                FieldPanel("practice_subsection_header"),
            ],
            heading="Principles Subsection Headers",
        ),
        MultiFieldPanel(
            [
                FieldPanel("strategy_label_focus"),
                FieldPanel("strategy_label_screening"),
                FieldPanel("strategy_label_management"),
                FieldPanel("strategy_label_ownership"),
            ],
            heading="Strategy Table Labels",
        ),
        MultiFieldPanel(
            [
                FieldPanel("strategy_1_name"),
                FieldPanel("strategy_1_subtitle"),
                FieldPanel("strategy_1_focus"),
                FieldPanel("strategy_1_screening"),
                FieldPanel("strategy_1_management"),
                FieldPanel("strategy_1_ownership"),
                FieldPanel("strategy_1_description"),
                FieldPanel("strategy_1_link"),
                FieldPanel("strategy_1_link_text"),
            ],
            heading="Strategy 1 - Growth",
        ),
        MultiFieldPanel(
            [
                FieldPanel("strategy_2_name"),
                FieldPanel("strategy_2_subtitle"),
                FieldPanel("strategy_2_focus"),
                FieldPanel("strategy_2_screening"),
                FieldPanel("strategy_2_management"),
                FieldPanel("strategy_2_ownership"),
                FieldPanel("strategy_2_description"),
                FieldPanel("strategy_2_link"),
                FieldPanel("strategy_2_link_text"),
            ],
            heading="Strategy 2 - Income",
        ),
        MultiFieldPanel(
            [
                FieldPanel("strategy_3_name"),
                FieldPanel("strategy_3_subtitle"),
                FieldPanel("strategy_3_focus"),
                FieldPanel("strategy_3_screening"),
                FieldPanel("strategy_3_management"),
                FieldPanel("strategy_3_ownership"),
                FieldPanel("strategy_3_description"),
                FieldPanel("strategy_3_link"),
                FieldPanel("strategy_3_link_text"),
            ],
            heading="Strategy 3 - Diversification",
        ),
        MultiFieldPanel(
            [
                FieldPanel("serve_individual_link"),
                FieldPanel("serve_individual_link_text"),
                FieldPanel("serve_advisor_link"),
                FieldPanel("serve_advisor_link_text"),
                FieldPanel("serve_institution_link"),
                FieldPanel("serve_institution_link_text"),
            ],
            heading="Who We Serve Links",
        ),
        MultiFieldPanel(
            [
                FieldPanel("process_section_link"),
                FieldPanel("process_section_link_text"),
            ],
            heading="Process Section Link",
        ),
        MultiFieldPanel(
            [
                FieldPanel("cta_button_1_link"),
                FieldPanel("cta_button_1_text"),
                FieldPanel("cta_button_2_link"),
                FieldPanel("cta_button_2_text"),
                FieldPanel("accepting_clients_icon"),
            ],
            heading="Bottom CTA Settings",
        ),
    ]

    # Wagtail admin panel configurations
    promote_panels = Page.promote_panels
    settings_panels = Page.settings_panels

    # Search fields for Wagtail search functionality
    search_fields = Page.search_fields + [
        index.SearchField("hero_title"),
        index.SearchField("hero_subtitle"),
        index.SearchField("philosophy_content"),
        index.SearchField("philosophy_highlight"),
    ]

    # Define allowed subpage types - exclude BlogPost to enforce proper hierarchy
    subpage_types = [
        "public_site.AboutPage",
        "public_site.PricingPage",
        "public_site.ContactPage",
        "public_site.BlogIndexPage",  # Blog posts must go under BlogIndexPage
        "public_site.FAQPage",
        "public_site.FAQIndexPage",  # FAQ articles index
        "public_site.StrategyPage",
        "public_site.StrategyListPage",
        "public_site.MediaPage",
        "public_site.PRIDDQPage",
        "public_site.EncyclopediaIndexPage",
        "public_site.LegalPage",
    ]

    class Meta:
        verbose_name = "Homepage"
        verbose_name_plural = "Homepages"


class AboutPage(SafeUrlMixin, Page):
    """About/Our Story page."""

    template = "public_site/about_page.html"

    # Hero section
    headshot_image = models.URLField(
        blank=True,
        help_text="URL to headshot image",
    )
    headshot_alt_text = models.CharField(
        max_length=200,
        blank=True,
        help_text="Alt text for headshot image",
    )
    philosophy_quote = RichTextField(
        blank=True,
        help_text="Philosophy quote in the hero section",
    )
    philosophy_quote_link = models.CharField(
        max_length=500,
        blank=True,
        help_text="Link for the philosophy quote attribution (can be relative or absolute URL)",
    )
    philosophy_quote_link_text = models.CharField(
        max_length=200,
        blank=True,
        help_text="Text for the philosophy quote link",
    )

    # Identity section
    name = models.CharField(
        max_length=200,
        blank=True,
        help_text="Name and pronouns",
    )
    professional_title = models.CharField(
        max_length=200,
        blank=True,
        help_text="Professional title",
    )

    # Social links
    linkedin_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    bluesky_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    tiktok_url = models.URLField(blank=True)
    calendar_url = models.URLField(blank=True)
    sec_info_url = models.URLField(blank=True)

    # Professional background section
    professional_background_title = models.CharField(
        max_length=200,
        blank=True,
        help_text="Title for professional background section",
    )
    professional_background_content = RichTextField(
        blank=True,
        help_text="Professional background content",
    )

    # External roles section
    external_roles_title = models.CharField(
        max_length=200,
        blank=True,
        help_text="Title for external roles section",
    )
    external_roles_content = RichTextField(
        blank=True,
        help_text="External roles and leadership content",
    )

    # Speaking & writing section
    speaking_writing_title = models.CharField(
        max_length=200,
        blank=True,
        help_text="Title for speaking & writing section",
    )
    speaking_writing_content = RichTextField(
        blank=True,
        help_text="Speaking & writing content",
    )
    speaking_cta_text = RichTextField(
        blank=True,
        help_text="Call-to-action text for speaking section",
    )
    speaking_contact_note = RichTextField(
        blank=True,
        help_text="Contact note for speaking section",
    )
    calendar_link = models.URLField(
        blank=True,
        help_text="Calendar booking link",
    )
    calendar_link_text = models.CharField(
        max_length=200,
        blank=True,
        help_text="Text for calendar link",
    )
    email_link = models.EmailField(blank=True, help_text="Contact email address")
    email_link_text = models.CharField(
        max_length=200,
        blank=True,
        help_text="Text for email link",
    )

    # Personal interests section
    personal_interests_title = models.CharField(
        max_length=200,
        blank=True,
        help_text="Title for personal interests section",
    )
    personal_interests_content = RichTextField(
        blank=True,
        help_text="Personal interests content",
    )

    # Timeline experience data
    experience_timeline = StreamField(
        [
            (
                "timeline_item",
                blocks.StructBlock(
                    [
                        (
                            "year",
                            blocks.CharBlock(
                                max_length=20,
                                help_text="Year or year range (e.g., 2007-8)",
                            ),
                        ),
                        (
                            "company",
                            blocks.CharBlock(
                                max_length=200, help_text="Company or organization name"
                            ),
                        ),
                        (
                            "description",
                            blocks.CharBlock(
                                max_length=500,
                                required=False,
                                help_text="Optional description",
                            ),
                        ),
                    ]
                ),
            )
        ],
        blank=True,
        use_json_field=True,
        help_text="Experience timeline items",
    )

    # Hobbies/interests with icons
    hobbies = StreamField(
        [
            (
                "hobby",
                blocks.StructBlock(
                    [
                        (
                            "icon",
                            blocks.CharBlock(
                                max_length=10, help_text="Emoji icon for the hobby"
                            ),
                        ),
                        ("title", blocks.CharBlock(max_length=100)),
                        ("description", blocks.TextBlock()),
                    ]
                ),
            )
        ],
        blank=True,
        use_json_field=True,
        help_text="Personal hobbies and interests",
    )

    # Featured writing posts
    featured_posts = StreamField(
        [
            (
                "featured_post",
                blocks.StructBlock(
                    [
                        ("title", blocks.CharBlock(max_length=100)),
                        ("description", blocks.TextBlock()),
                        (
                            "url",
                            blocks.CharBlock(
                                max_length=200, help_text="Link to the post"
                            ),
                        ),
                    ]
                ),
            )
        ],
        blank=True,
        use_json_field=True,
        help_text="Featured writing posts",
    )

    # Three-panel content for new layout
    # What I Do Now panel
    current_role_content = RichTextField(
        blank=True,
        help_text="Current role description for What I Do Now panel",
    )
    philosophy_content = RichTextField(
        blank=True,
        help_text="Philosophy description for What I Do Now panel",
    )
    client_focus_content = RichTextField(
        blank=True,
        help_text="Client focus description for What I Do Now panel",
    )

    # Featured posts section
    featured_post_1_title = models.CharField(max_length=200, blank=True)
    featured_post_1_description = models.CharField(
        max_length=300,
        blank=True,
    )
    featured_post_1_url = models.CharField(max_length=500, blank=True)

    featured_post_2_title = models.CharField(max_length=200, blank=True)
    featured_post_2_description = models.CharField(max_length=300, blank=True)
    featured_post_2_url = models.CharField(
        max_length=500,
        blank=True,
    )

    featured_post_3_title = models.CharField(max_length=200, blank=True)
    featured_post_3_description = models.CharField(max_length=300, blank=True)
    featured_post_3_url = models.CharField(max_length=500, blank=True)

    featured_post_4_title = models.CharField(
        max_length=200,
        blank=True,
    )
    featured_post_4_description = models.CharField(max_length=300, blank=True)
    featured_post_4_url = models.CharField(
        max_length=500,
        blank=True,
    )

    # Speaking topics
    speaking_topics = RichTextField(
        blank=True,
        help_text="Topics covered in speaking engagements",
    )

    # Speaker bio download
    speaker_bio_url = models.URLField(
        blank=True,
        help_text="URL to speaker bio PDF",
    )

    content_panels: ClassVar[list] = [
        *Page.content_panels,
        MultiFieldPanel(
            [
                FieldPanel("headshot_image"),
                FieldPanel("headshot_alt_text"),
                FieldPanel("philosophy_quote"),
                FieldPanel("philosophy_quote_link"),
                FieldPanel("philosophy_quote_link_text"),
            ],
            heading="Hero Section",
        ),
        MultiFieldPanel(
            [
                FieldPanel("name"),
                FieldPanel("professional_title"),
            ],
            heading="Identity",
        ),
        MultiFieldPanel(
            [
                FieldPanel("linkedin_url"),
                FieldPanel("twitter_url"),
                FieldPanel("bluesky_url"),
                FieldPanel("instagram_url"),
                FieldPanel("tiktok_url"),
                FieldPanel("calendar_url"),
                FieldPanel("sec_info_url"),
            ],
            heading="Social Links",
        ),
        MultiFieldPanel(
            [
                FieldPanel("current_role_content"),
                FieldPanel("philosophy_content"),
                FieldPanel("client_focus_content"),
            ],
            heading="What I Do Now Panel",
        ),
        MultiFieldPanel(
            [
                FieldPanel("professional_background_title"),
                FieldPanel("professional_background_content"),
            ],
            heading="Professional Background",
        ),
        MultiFieldPanel(
            [
                FieldPanel("external_roles_title"),
                FieldPanel("external_roles_content"),
            ],
            heading="External Roles",
        ),
        FieldPanel("experience_timeline"),
        FieldPanel("hobbies"),
        MultiFieldPanel(
            [
                FieldPanel("featured_post_1_title"),
                FieldPanel("featured_post_1_description"),
                FieldPanel("featured_post_1_url"),
                FieldPanel("featured_post_2_title"),
                FieldPanel("featured_post_2_description"),
                FieldPanel("featured_post_2_url"),
                FieldPanel("featured_post_3_title"),
                FieldPanel("featured_post_3_description"),
                FieldPanel("featured_post_3_url"),
                FieldPanel("featured_post_4_title"),
                FieldPanel("featured_post_4_description"),
                FieldPanel("featured_post_4_url"),
            ],
            heading="Featured Posts (Legacy)",
        ),
        FieldPanel("featured_posts"),
        MultiFieldPanel(
            [
                FieldPanel("speaking_writing_title"),
                FieldPanel("speaking_writing_content"),
                FieldPanel("speaking_topics"),
                FieldPanel("speaker_bio_url"),
                FieldPanel("speaking_cta_text"),
                FieldPanel("speaking_contact_note"),
                FieldPanel("calendar_link"),
                FieldPanel("calendar_link_text"),
                FieldPanel("email_link"),
                FieldPanel("email_link_text"),
            ],
            heading="Speaking & Writing",
        ),
        MultiFieldPanel(
            [
                FieldPanel("personal_interests_title"),
                FieldPanel("personal_interests_content"),
            ],
            heading="Personal Interests",
        ),
    ]

    # Wagtail admin panel configurations
    promote_panels = Page.promote_panels
    settings_panels = Page.settings_panels

    # Search fields for Wagtail search functionality
    search_fields = Page.search_fields + [
        index.SearchField("name"),
        index.SearchField("title"),
        index.SearchField("philosophy_quote"),
        index.SearchField("current_role_content"),
        index.SearchField("philosophy_content"),
        index.SearchField("professional_background_content"),
    ]

    class Meta:
        verbose_name = "About Page"


class PricingPage(SafeUrlMixin, Page):
    """Pricing/Fees page."""

    template = "public_site/pricing_page.html"

    # Header section
    section_header = models.CharField(
        max_length=200,
        blank=True,
        help_text="Main pricing section header",
    )
    section_intro = RichTextField(
        blank=True,
        help_text="Introduction text for pricing section",
    )

    # Individual Pricing Card
    individual_badge = models.CharField(max_length=100, blank=True)
    individual_title = models.CharField(max_length=200, blank=True)
    individual_subtitle = models.CharField(max_length=200, blank=True)
    individual_price = models.CharField(max_length=20, blank=True)
    individual_price_period = models.CharField(max_length=50, blank=True)
    individual_features = RichTextField(
        blank=True,
        help_text="Features for individual pricing tier",
    )
    individual_cta_text = models.CharField(max_length=100, blank=True)
    individual_cta_link = models.CharField(max_length=200, blank=True)

    # Institutional Pricing Card
    institutional_badge = models.CharField(max_length=100, blank=True)
    institutional_title = models.CharField(max_length=200, blank=True)
    institutional_subtitle = models.CharField(
        max_length=200,
        blank=True,
    )
    institutional_price = models.CharField(max_length=20, blank=True)
    institutional_price_period = models.CharField(max_length=50, blank=True)
    institutional_features = RichTextField(
        blank=True,
        help_text="Features for institutional pricing tier",
    )

    # Fee Details
    fee_calculation_title = models.CharField(max_length=100, blank=True)
    fee_calculation_text = RichTextField(
        blank=True,
    )
    minimum_investment_title = models.CharField(max_length=100, blank=True)
    minimum_investment_text = RichTextField(
        blank=True,
    )
    pricing_rationale_title = models.CharField(max_length=100, blank=True)
    pricing_rationale_text = RichTextField(
        blank=True,
    )

    # Workshop Section
    workshop_section_header = models.CharField(
        max_length=200,
        blank=True,
    )
    workshop_intro = RichTextField(
        blank=True,
    )
    workshop_nonprofit_note = RichTextField(
        blank=True,
    )
    workshop_form_title = models.CharField(max_length=200, blank=True)
    show_workshop_form = models.BooleanField(
        default=False, blank=True, help_text="Show the workshop request form"
    )

    # Additional Services Section
    services_section_header = models.CharField(max_length=200, blank=True)
    services_intro = RichTextField(
        blank=True,
    )

    # Service Cards (as StreamField for flexibility)
    additional_services = StreamField(
        [
            (
                "service",
                blocks.StructBlock(
                    [
                        ("title", blocks.CharBlock(max_length=200)),
                        ("description", blocks.TextBlock()),
                        ("fee_text", blocks.CharBlock(max_length=100, required=False)),
                        ("cta_text", blocks.CharBlock(max_length=50)),
                        ("cta_link", blocks.CharBlock(max_length=200)),
                    ]
                ),
            )
        ],
        blank=True,
        use_json_field=True,
    )

    # CTA Section
    cta_section_header = models.CharField(max_length=200, blank=True)
    cta_title = models.CharField(max_length=200, blank=True)
    cta_description = RichTextField(
        blank=True,
    )

    # Legacy fields (keeping for backward compatibility)
    intro_text = RichTextField(
        blank=True,
    )
    pricing_description = RichTextField(blank=True)
    enterprise_title = models.CharField(
        max_length=200,
        blank=True,
    )
    enterprise_description = RichTextField(blank=True)
    contact_cta = RichTextField(
        blank=True,
    )

    content_panels: ClassVar[list] = [
        *Page.content_panels,
        MultiFieldPanel(
            [
                FieldPanel("section_header"),
                FieldPanel("section_intro"),
            ],
            heading="Main Pricing Section",
        ),
        MultiFieldPanel(
            [
                FieldPanel("individual_badge"),
                FieldPanel("individual_title"),
                FieldPanel("individual_subtitle"),
                FieldPanel("individual_price"),
                FieldPanel("individual_price_period"),
                FieldPanel("individual_features"),
                FieldPanel("individual_cta_text"),
                FieldPanel("individual_cta_link"),
            ],
            heading="Individual Pricing",
        ),
        MultiFieldPanel(
            [
                FieldPanel("institutional_badge"),
                FieldPanel("institutional_title"),
                FieldPanel("institutional_subtitle"),
                FieldPanel("institutional_price"),
                FieldPanel("institutional_price_period"),
                FieldPanel("institutional_features"),
            ],
            heading="Institutional Pricing",
        ),
        MultiFieldPanel(
            [
                FieldPanel("fee_calculation_title"),
                FieldPanel("fee_calculation_text"),
                FieldPanel("minimum_investment_title"),
                FieldPanel("minimum_investment_text"),
                FieldPanel("pricing_rationale_title"),
                FieldPanel("pricing_rationale_text"),
            ],
            heading="Fee Details",
        ),
        MultiFieldPanel(
            [
                FieldPanel("workshop_section_header"),
                FieldPanel("workshop_intro"),
                FieldPanel("workshop_nonprofit_note"),
                FieldPanel("workshop_form_title"),
                FieldPanel("show_workshop_form"),
            ],
            heading="Workshop Section",
        ),
        MultiFieldPanel(
            [
                FieldPanel("services_section_header"),
                FieldPanel("services_intro"),
                FieldPanel("additional_services"),
            ],
            heading="Additional Services",
        ),
        MultiFieldPanel(
            [
                FieldPanel("cta_section_header"),
                FieldPanel("cta_title"),
                FieldPanel("cta_description"),
            ],
            heading="Call to Action",
        ),
        MultiFieldPanel(
            [
                FieldPanel("intro_text"),
                FieldPanel("pricing_description"),
                FieldPanel("enterprise_title"),
                FieldPanel("enterprise_description"),
                FieldPanel("contact_cta"),
            ],
            heading="Legacy Fields (Deprecated)",
            classname="collapsed",  # Start collapsed since these are legacy
        ),
    ]

    # Wagtail admin panel configurations
    promote_panels = Page.promote_panels
    settings_panels = Page.settings_panels

    # Search fields for Wagtail search functionality
    search_fields = Page.search_fields + [
        index.SearchField("intro_text"),
        index.SearchField("pricing_description"),
        index.SearchField("enterprise_title"),
        index.SearchField("enterprise_description"),
    ]

    class Meta:
        verbose_name = "Pricing Page"


class ContactPage(SafeUrlMixin, RoutablePageMixin, Page):
    """Contact/Get Started page with accessible form."""

    template = "public_site/contact_form_tailwind.html"

    @path("")
    def contact_page_view(self, request):
        """Default contact page view with form handling."""
        if request.method == "POST" and self.show_contact_form:
            from .forms import AccessibleContactForm

            form = AccessibleContactForm(request.POST)

            if form.is_valid():
                # Process the form data
                self._process_contact_form(form.cleaned_data, request)

                from django.contrib import messages

                messages.success(
                    request,
                    "Thank you for your message! We will get back to you within 24 hours.",
                )

                # Redirect to prevent re-submission
                from django.shortcuts import redirect

                return redirect(request.path)

        return self.render(request)

    intro_text = RichTextField(
        blank=True,
    )
    contact_description = RichTextField(blank=True)

    # Contact information
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = RichTextField(blank=True)

    # Form settings
    show_contact_form = models.BooleanField(
        default=True,
        help_text="Show the contact form on this page",
    )

    content_panels: ClassVar[list] = [
        *Page.content_panels,
        FieldPanel("intro_text"),
        FieldPanel("contact_description"),
        MultiFieldPanel(
            [FieldPanel("email"), FieldPanel("phone"), FieldPanel("address")],
            heading="Contact Information",
        ),
        FieldPanel("show_contact_form"),
    ]

    # Wagtail admin panel configurations
    promote_panels = Page.promote_panels
    settings_panels = Page.settings_panels

    # Search fields for Wagtail search functionality
    search_fields = Page.search_fields + [
        index.SearchField("intro_text"),
        index.SearchField("contact_description"),
    ]

    def get_context(self, request):
        """Add contact form to page context."""
        from django.contrib import messages

        from .forms import AccessibleContactForm

        context = super().get_context(request)

        if self.show_contact_form:
            # Handle form submission
            if request.method == "POST":
                form = AccessibleContactForm(request.POST, request=request)

                # Check rate limiting first
                if form._check_rate_limiting(request):
                    messages.error(
                        request,
                        "Too many submissions from your location. Please try again later or contact us directly.",
                    )
                    form = AccessibleContactForm(request=request)  # Fresh form
                elif form.is_valid():
                    # Process form submission
                    success = self._process_contact_form(form.cleaned_data, request)

                    if success:
                        messages.success(
                            request,
                            "Thank you for your message! We will get back to you within 24 hours.",
                        )
                        # Redirect to prevent re-submission
                        from django.shortcuts import redirect

                        return redirect(request.path)
                    messages.error(
                        request,
                        "We encountered an issue sending your message. Please try again or contact us directly.",
                    )
            else:
                form = AccessibleContactForm(request=request)

            context["contact_form"] = form

        return context

    def _process_contact_form(self, form_data, request):
        """Process the submitted contact form data."""
        import logging

        from django.conf import settings
        from django.core.mail import send_mail
        from django.template.loader import render_to_string
        from django.utils import timezone
        from django.utils.html import strip_tags

        logger = logging.getLogger(__name__)

        try:
            # Log the submission
            logger.info(
                f"Contact form submission from {form_data['email']}: {form_data['subject']}",
                extra={
                    "user_email": form_data["email"],
                    "subject": form_data["subject"],
                    "ip_address": self._get_client_ip(request),
                    "user_agent": request.META.get("HTTP_USER_AGENT", "")[:200],
                },
            )

            # Prepare email content
            context = {
                "form_data": form_data,
                "request": request,
                "ip_address": self._get_client_ip(request),
                "user_agent": request.META.get("HTTP_USER_AGENT", "")[:200],
                "timestamp": timezone.now(),
            }

            # Render email templates
            html_message = render_to_string(
                "public_site/emails/contact_form_notification.html", context
            )
            plain_message = strip_tags(html_message)

            # Send notification email to your team
            send_mail(
                subject=f"Contact Form: {form_data.get('subject', 'General Inquiry')} - {form_data['name']}",
                message=plain_message,
                html_message=html_message,
                from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "hello@ethicic.com"),
                recipient_list=["hello@ethicic.com"],
                fail_silently=False,
            )

            # Send auto-reply to the user
            auto_reply_context = {
                "name": form_data["name"],
                "subject": form_data.get("subject", "General Inquiry"),
            }

            auto_reply_html = render_to_string(
                "public_site/emails/contact_form_auto_reply.html", auto_reply_context
            )
            auto_reply_plain = strip_tags(auto_reply_html)

            send_mail(
                subject="Thank you for contacting Ethical Capital",
                message=auto_reply_plain,
                html_message=auto_reply_html,
                from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "hello@ethicic.com"),
                recipient_list=[form_data["email"]],
                fail_silently=True,  # Don't fail if auto-reply fails
            )

            # Try to create a CRM contact if CRM is available
            try:
                self._create_crm_contact(form_data, request)
            except Exception as e:
                logger.warning(f"Failed to create CRM contact: {e}")

            return True

        except Exception as e:
            logger.error(f"Failed to process contact form: {e}", exc_info=True)
            return False

    def _get_client_ip(self, request):
        """Get the client's IP address."""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0].strip()
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip

    def _create_crm_contact(self, form_data, request):
        """Create a contact in the CRM system."""
        try:
            from crm.models import Contact

            # Check if contact already exists
            existing_contact = Contact.objects.filter(email=form_data["email"]).first()

            if existing_contact:
                # Update existing contact with new information
                if form_data.get("company"):
                    existing_contact.company = form_data["company"]
                existing_contact.save()
                return existing_contact
            # Create new contact
            return Contact.objects.create(
                name=form_data["name"],
                email=form_data["email"],
                company=form_data.get("company", ""),
                source="Website Contact Form",
                notes=f"Subject: {form_data.get('subject', 'General Inquiry')}\n\nMessage: {form_data['message'][:500]}",
            )

        except ImportError:
            # CRM app not available
            pass
        except Exception:
            raise

    class Meta:
        verbose_name = "Contact Page"


# ============================================================================
# ORDERABLE & RELATED MODELS
# ============================================================================
# These are supporting models for pages - tags, items, components, etc.


class BlogTag(TaggedItemBase):
    """Tag model for blog posts."""

    content_object = ParentalKey(
        "BlogPost",
        related_name="tagged_items",
        on_delete=models.CASCADE,
    )


class BlogIndexPage(SafeUrlMixin, RoutablePageMixin, Page):
    """Blog index page with pagination and filtering."""

    template = "public_site/blog_index_tailwind.html"

    intro_text = RichTextField(
        blank=True,
    )

    description = RichTextField(
        blank=True,
    )

    # Custom page display title
    display_title = models.CharField(
        max_length=255,
        blank=True,
        help_text="Optional custom title to display on the page (if blank, uses the page title)",
    )

    # Featured research section
    featured_title = models.CharField(
        max_length=200,
        blank=True,
    )
    featured_description = RichTextField(
        blank=True,
    )

    content_panels: ClassVar[list] = [
        *Page.content_panels,
        FieldPanel("display_title"),
        FieldPanel("intro_text"),
        FieldPanel("description"),
        MultiFieldPanel(
            [FieldPanel("featured_title"), FieldPanel("featured_description")],
            heading="Featured Research Section",
        ),
    ]

    # Wagtail admin panel configurations
    promote_panels = Page.promote_panels
    settings_panels = Page.settings_panels

    # Search fields for Wagtail search functionality
    search_fields = Page.search_fields + [
        index.SearchField("display_title"),
        index.SearchField("intro_text"),
        index.SearchField("description"),
    ]

    # Restrict to only allow BlogPost children
    subpage_types = ["public_site.BlogPost"]

    def get_posts(self):
        """Get all published blog posts."""
        return (
            BlogPost.objects.child_of(self)
            .live()
            .public()
            .select_related("owner")
            .prefetch_related("tags")
            .order_by("-first_published_at")
        )

    def get_popular_posts(self, limit=5):
        """Get popular blog posts based on reading time and recent publication."""
        from django.db.models import Case, F, IntegerField, When

        # Simple popularity algorithm: prioritize posts with longer reading time
        # (indicating substantial content) and more recent publication dates
        return (
            self.get_posts()
            .annotate(
                popularity_score=Case(
                    When(reading_time__isnull=True, then=0),
                    default=F("reading_time"),
                    output_field=IntegerField(),
                )
            )
            .order_by("-first_published_at", "-popularity_score")[:limit]
        )

    def get_all_authors(self):
        """Get all unique authors with post counts."""
        from django.db.models import Count

        # Get unique authors with their post counts
        authors = (
            self.get_posts()
            .values("author")
            .annotate(post_count=Count("id"))
            .filter(author__isnull=False, author__gt="")
            .order_by("author")
        )

        # Convert to a list with slug-friendly author names
        author_list = []
        for author_data in authors:
            author_name = author_data["author"]
            author_slug = author_name.lower().replace(" ", "-")
            author_list.append(
                {
                    "name": author_name,
                    "slug": author_slug,
                    "post_count": author_data["post_count"],
                }
            )

        return author_list

    def get_featured_posts(self):
        """Get featured blog posts."""
        return self.get_posts().filter(featured=True)[:3]

    def get_recent_posts(self):
        """Get recent blog posts."""
        return self.get_posts()[:6]

    def get_posts_by_tag(self, tag_name):
        """Get posts filtered by tag."""
        return self.get_posts().filter(tags__name=tag_name)

    def get_all_tags(self):
        """Get all tags used in posts."""
        try:
            from django.contrib.contenttypes.models import ContentType
            from taggit.models import Tag

            # Get ContentType for BlogPost
            blog_post_ct = ContentType.objects.get_for_model(BlogPost)

            return Tag.objects.filter(
                taggit_taggeditem_items__content_type=blog_post_ct
            ).distinct()
        except Exception:
            # Return empty queryset if there's any issue
            from taggit.models import Tag

            return Tag.objects.none()

    @path("")
    def post_list(self, request):
        """Default research listing."""
        posts = self.get_posts()
        featured_posts = self.get_featured_posts()
        recent_posts = self.get_recent_posts()
        all_tags = self.get_all_tags()

        # Handle search and filtering
        search_query = request.GET.get("search", "")
        tag_filter = request.GET.get("tag", "")

        if search_query:
            posts = posts.search(search_query)

        if tag_filter:
            posts = posts.filter(tags__name=tag_filter)

        paginator = Paginator(posts, 12)  # 12 posts per page
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        # Handle HTMX requests for infinite scroll
        is_htmx = request.headers.get("HX-Request") == "true"

        if is_htmx and page_number and int(page_number) > 1:
            # Return only the article list for infinite scroll
            from django.template.loader import render_to_string

            html = render_to_string(
                "public_site/partials/blog_articles.html",
                {
                    "posts": page_obj,
                    "has_next": page_obj.has_next(),
                    "next_page_num": page_obj.next_page_number()
                    if page_obj.has_next()
                    else None,
                },
                request=request,
            )
            from django.http import HttpResponse

            return HttpResponse(html)

        return self.render(
            request,
            context_overrides={
                "posts": page_obj,
                "featured_posts": featured_posts,
                "recent_posts": recent_posts,
                "all_tags": all_tags,
                "all_authors": self.get_all_authors(),
                "search_query": search_query,
                "tag_filter": tag_filter,
                "paginator": paginator,
            },
        )

    @path("tag/<str:tag>/")
    def post_by_tag(self, request, tag):
        """Filter posts by tag."""
        posts = self.get_posts().filter(tags__name=tag)
        paginator = Paginator(posts, 10)

        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        return self.render(
            request,
            context_overrides={
                "posts": page_obj,
                "tag": tag,
                "paginator": paginator,
            },
        )

    @path("author/<str:author_slug>/")
    def post_by_author(self, request, author_slug):
        """Filter posts by author."""
        # Convert slug back to author name (replace hyphens with spaces, title case)
        author_name = author_slug.replace("-", " ").title()
        posts = self.get_posts().filter(author__iexact=author_name)
        paginator = Paginator(posts, 10)

        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        return self.render(
            request,
            context_overrides={
                "posts": page_obj,
                "author": author_name,
                "author_slug": author_slug,
                "paginator": paginator,
            },
        )

    def get_context(self, request):
        """Add custom display title and other context to the template."""
        context = super().get_context(request)

        # Add custom display title
        context["display_title"] = self.display_title or self.title

        # Add popular posts for sidebar
        context["popular_posts"] = self.get_popular_posts(limit=5)

        return context

    class Meta:
        verbose_name = "Blog Index Page"


class BlogPost(SafeUrlMixin, Page):
    """Individual blog post with rich StreamField content."""

    excerpt = models.CharField(
        max_length=300,
        blank=True,
        help_text="Brief description of the post for listings and SEO",
    )

    # New StreamField for rich content with AI-powered blocks
    content = StreamField(
        [
            (
                "rich_text",
                blocks.RichTextBlock(
                    features=[
                        "h2",
                        "h3",
                        "h4",
                        "bold",
                        "italic",
                        "link",
                        "ol",
                        "ul",
                        "document-link",
                    ],
                    help_text="Rich text content with basic formatting",
                ),
            ),
            (
                "key_statistic",
                blocks.StructBlock(
                    [
                        (
                            "value",
                            blocks.CharBlock(
                                max_length=50, help_text="The statistic value"
                            ),
                        ),
                        (
                            "label",
                            blocks.CharBlock(
                                max_length=100, help_text="Statistic label"
                            ),
                        ),
                        (
                            "description",
                            blocks.TextBlock(
                                required=False, help_text="Optional description"
                            ),
                        ),
                        (
                            "ai_confidence",
                            blocks.DecimalBlock(
                                default=0.0,
                                max_digits=3,
                                decimal_places=2,
                                required=False,
                            ),
                        ),
                        ("ai_context", blocks.TextBlock(required=False)),
                        (
                            "significance_level",
                            blocks.ChoiceBlock(
                                choices=[
                                    ("high", "High Significance"),
                                    ("medium", "Medium Significance"),
                                    ("low", "Low Significance"),
                                ],
                                default="medium",
                                required=False,
                            ),
                        ),
                        (
                            "statistic_category",
                            blocks.ChoiceBlock(
                                choices=[
                                    ("performance", "Performance/Returns"),
                                    ("valuation", "Valuation Metrics"),
                                    ("risk", "Risk Metrics"),
                                    ("allocation", "Portfolio Allocation"),
                                    ("fundamental", "Fundamental Analysis"),
                                    ("market", "Market Data"),
                                ],
                                default="performance",
                                required=False,
                            ),
                        ),
                        (
                            "visualization_type",
                            blocks.ChoiceBlock(
                                choices=[
                                    ("bar", "Bar Chart"),
                                    (
                                        "performance_comparison",
                                        "Performance Comparison",
                                    ),
                                    ("allocation_pie", "Allocation Pie Chart"),
                                    ("trend_line", "Trend Line"),
                                    ("gauge", "Gauge/Meter"),
                                    ("callout", "Highlighted Callout"),
                                ],
                                default="callout",
                                required=False,
                            ),
                        ),
                        (
                            "time_period",
                            blocks.ChoiceBlock(
                                choices=[
                                    ("daily", "Daily"),
                                    ("weekly", "Weekly"),
                                    ("monthly", "Monthly"),
                                    ("quarterly", "Quarterly"),
                                    ("annual", "Annual"),
                                    ("ytd", "Year-to-Date"),
                                    ("since_inception", "Since Inception"),
                                    ("custom", "Custom Period"),
                                ],
                                required=False,
                            ),
                        ),
                        (
                            "chart_title",
                            blocks.CharBlock(max_length=100, required=False),
                        ),
                        ("chart_config", blocks.TextBlock(required=False)),
                        (
                            "related_entities",
                            blocks.ListBlock(
                                blocks.CharBlock(max_length=100), required=False
                            ),
                        ),
                    ],
                    template="public_site/blocks/key_statistic.html",
                    icon="success",
                    label="Key Statistic",
                ),
            ),
            (
                "table",
                blocks.StructBlock(
                    [
                        (
                            "caption",
                            blocks.CharBlock(
                                required=False, help_text="Table title or caption"
                            ),
                        ),
                        (
                            "description",
                            blocks.RichTextBlock(
                                required=False,
                                help_text="Optional description or context",
                            ),
                        ),
                        (
                            "table",
                            TableBlock(
                                help_text="Add table data - first row will be used as headers"
                            ),
                        ),
                        (
                            "source",
                            blocks.CharBlock(
                                required=False, help_text="Data source attribution"
                            ),
                        ),
                    ],
                    template="public_site/blocks/table_block.html",
                    icon="table",
                    label="Data Table",
                ),
            ),
            ("image", ImageChooserBlock()),
            (
                "callout",
                blocks.StructBlock(
                    [
                        (
                            "type",
                            blocks.ChoiceBlock(
                                choices=[
                                    ("info", "Info"),
                                    ("warning", "Warning"),
                                    ("success", "Success"),
                                    ("error", "Error"),
                                ]
                            ),
                        ),
                        ("title", blocks.CharBlock(required=False)),
                        ("content", blocks.RichTextBlock()),
                    ],
                    icon="help",
                ),
            ),
            (
                "quote",
                blocks.StructBlock(
                    [
                        ("quote", blocks.TextBlock()),
                        ("author", blocks.CharBlock(required=False)),
                        ("source", blocks.CharBlock(required=False)),
                    ],
                    icon="openquote",
                ),
            ),
        ],
        blank=True,
        use_json_field=True,
        help_text="Rich content with AI-enhanced statistics, charts, and analysis blocks",
    )

    # Keep old body field for backwards compatibility during migration
    body = RichTextField(
        blank=True,
        help_text="Legacy rich text field (use Content field above for new posts)",
    )

    # Featured image for social sharing and blog listings (exists from WordPress migration)
    featured_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Featured image for social sharing and blog listings",
    )

    tags = ClusterTaggableManager(through=BlogTag, blank=True)

    # Meta information
    author = models.CharField(max_length=100, blank=True)
    publish_date = models.DateField(
        blank=True,
        null=True,
        help_text="Leave blank for today's date",
    )
    featured = models.BooleanField(
        default=False,
        help_text="Feature this post on the homepage",
    )
    # Reading time estimation (restored to fix validation errors)
    reading_time = models.IntegerField(
        blank=True, null=True, help_text="Estimated reading time in minutes"
    )

    # Content update tracking
    updated_at = models.DateTimeField(
        auto_now=True, help_text="Automatically updated when the content is modified"
    )

    def calculate_reading_time(self):
        """Calculate reading time based on content word count."""
        from math import ceil

        # Average reading speed (words per minute)
        words_per_minute = 200
        word_count = 0

        # Count words in excerpt
        if self.excerpt:
            word_count += len(self.excerpt.split())

        # Count words in StreamField content
        if self.content:
            word_count += self._count_streamfield_words()

        # Count words in legacy body field (for backwards compatibility)
        if self.body:
            from django.utils.html import strip_tags

            body_text = strip_tags(str(self.body))
            word_count += len(body_text.split())

        # Calculate reading time (minimum 1 minute)
        reading_time = ceil(word_count / words_per_minute) if word_count > 0 else 1
        return max(reading_time, 1)

    def _count_streamfield_words(self):
        """Helper method to count words in StreamField content."""
        word_count = 0
        for block in self.content:
            block_text = self._extract_block_text(block)
            if block_text:
                word_count += len(block_text.split())
        return word_count

    def _extract_block_text(self, block):
        """Extract text content from a StreamField block."""
        from django.utils.html import strip_tags

        if block.block_type == "rich_text":
            return strip_tags(str(block.value))

        if block.block_type in [
            "key_statistic",
            "callout",
            "quote",
            "table",
        ] and hasattr(block.value, "values"):
            return " ".join(
                str(value) for value in block.value.values() if isinstance(value, str)
            )

        return ""

    def save(self, *args, **kwargs):
        """Override save to auto-calculate reading time."""
        # Auto-calculate reading time if not manually set
        if not self.reading_time:
            self.reading_time = self.calculate_reading_time()

        super().save(*args, **kwargs)

    content_panels: ClassVar[list] = [
        *Page.content_panels,
        MultiFieldPanel(
            [FieldPanel("excerpt"), FieldPanel("featured_image")],
            heading="Post Overview",
            help_text="Basic post information and featured image for social sharing",
        ),
        MultiFieldPanel(
            [FieldPanel("content")],
            heading="Main Content",
            help_text="Use this StreamField for rich content with images, videos, quotes, and other blocks",
        ),
        MultiFieldPanel(
            [FieldPanel("body")],
            heading="Legacy Content (Deprecated)",
            help_text="Old rich text field - use Main Content above for new posts",
            classname="collapsed",
        ),
        MultiFieldPanel(
            [
                FieldPanel("tags"),
                FieldPanel("author"),
                FieldPanel("publish_date"),
                FieldPanel("featured"),
                FieldPanel("reading_time"),
            ],
            heading="Post Metadata",
            help_text="Author, publishing details, and categorization",
        ),
    ]

    # Wagtail admin panel configurations
    promote_panels = Page.promote_panels
    settings_panels = Page.settings_panels

    search_fields = Page.search_fields + [
        index.SearchField("excerpt"),
        index.SearchField("content"),
        index.SearchField("body"),  # Keep for backwards compatibility
        index.FilterField("author"),
        index.FilterField("publish_date"),
        index.FilterField("featured"),
    ]

    # Restrict to only allow BlogIndexPage as parent
    parent_page_types = ["public_site.BlogIndexPage"]

    # Use the Tailwind template with typography plugin
    template = "public_site/blog_post_tailwind.html"

    class Meta:
        verbose_name = "BlogPost"


class FAQPage(SafeUrlMixin, Page):
    """FAQ/Support page."""

    intro_text = RichTextField(
        blank=True,
    )

    # Empty State
    empty_state_title = models.CharField(
        max_length=200,
        blank=True,
    )
    empty_state_message = RichTextField(
        blank=True,
    )
    empty_state_button_text = models.CharField(
        max_length=100,
        blank=True,
    )
    empty_state_button_url = models.CharField(
        max_length=200,
        blank=True,
    )

    content_panels: ClassVar[list] = [
        *Page.content_panels,
        FieldPanel("intro_text"),
        InlinePanel("faq_items", label="FAQ Items"),
        MultiFieldPanel(
            [
                FieldPanel("empty_state_title"),
                FieldPanel("empty_state_message"),
                FieldPanel("empty_state_button_text"),
                FieldPanel("empty_state_button_url"),
            ],
            heading="Empty State",
        ),
    ]

    # Wagtail admin panel configurations
    promote_panels = Page.promote_panels
    settings_panels = Page.settings_panels

    # Search fields for Wagtail search functionality
    search_fields = Page.search_fields + [
        index.SearchField("intro_text"),
    ]

    class Meta:
        verbose_name = "FAQ Page"


class FAQItem(Orderable):
    """Individual FAQ item."""

    page = ParentalKey(FAQPage, on_delete=models.CASCADE, related_name="faq_items")
    question = models.CharField(max_length=300)
    answer = RichTextField()

    panels: ClassVar[list] = [
        FieldPanel("question"),
        FieldPanel("answer"),
    ]

    def __str__(self):
        return self.question


class LegalPage(SafeUrlMixin, Page):
    """Legal pages for disclosures, privacy policy, etc."""

    template = "public_site/legal_page.html"

    intro_text = RichTextField(blank=True)
    content = RichTextField()

    # Legal metadata
    effective_date = models.DateField(
        blank=True,
        null=True,
        help_text="When this legal document takes effect",
    )
    updated_at = models.DateField(auto_now=True)

    content_panels: ClassVar[list] = [
        *Page.content_panels,
        FieldPanel("intro_text"),
        FieldPanel("content"),
        MultiFieldPanel(
            [FieldPanel("effective_date"), FieldPanel("updated_at", read_only=True)],
            heading="Legal Information",
        ),
    ]

    # Wagtail admin panel configurations
    promote_panels = Page.promote_panels
    settings_panels = Page.settings_panels

    # Search fields for Wagtail search functionality
    search_fields = Page.search_fields + [
        index.SearchField("intro_text"),
        index.SearchField("content"),
    ]

    class Meta:
        verbose_name = "Legal Page"


class MediaPage(SafeUrlMixin, Page):
    """Media/Press page."""

    template = "public_site/media_page.html"

    intro_text = RichTextField(
        blank=True,
        help_text="Introduction text that appears at the top of the media page",
    )

    # Press kit information
    press_kit_title = models.CharField(
        max_length=200,
        blank=True,
        help_text="Title for the press kit section",
    )
    press_kit_description = RichTextField(
        blank=True,
        help_text="Description and information about available press materials",
    )

    # Empty State
    empty_state_title = models.CharField(
        max_length=200,
        blank=True,
    )
    empty_state_message = RichTextField(
        blank=True,
    )

    # Sidebar - Schedule Interview
    sidebar_interview_show = models.BooleanField(
        blank=True,
        help_text="Show schedule interview sidebar section",
    )
    sidebar_interview_title = models.CharField(
        max_length=200,
        blank=True,
    )
    sidebar_interview_description = RichTextField(
        blank=True,
    )
    sidebar_interview_button_text = models.CharField(
        max_length=100,
        blank=True,
    )
    sidebar_interview_button_url = models.URLField(
        blank=True,
    )

    # Sidebar - Media Contact
    sidebar_contact_show = models.BooleanField(
        blank=True,
        help_text="Show media contact sidebar section",
    )
    sidebar_contact_title = models.CharField(
        max_length=200,
        blank=True,
    )
    sidebar_contact_description = RichTextField(
        blank=True,
    )
    sidebar_contact_button_text = models.CharField(
        max_length=100,
        blank=True,
    )
    sidebar_contact_button_url = models.CharField(
        max_length=200,
        blank=True,
    )

    content_panels: ClassVar[list] = [
        *Page.content_panels,
        FieldPanel("intro_text"),
        MultiFieldPanel(
            [FieldPanel("press_kit_title"), FieldPanel("press_kit_description")],
            heading="Press Kit",
        ),
        MultiFieldPanel(
            [
                FieldPanel("empty_state_title"),
                FieldPanel("empty_state_message"),
            ],
            heading="Empty State",
        ),
        MultiFieldPanel(
            [
                FieldPanel("sidebar_interview_show"),
                FieldPanel("sidebar_interview_title"),
                FieldPanel("sidebar_interview_description"),
                FieldPanel("sidebar_interview_button_text"),
                FieldPanel("sidebar_interview_button_url"),
            ],
            heading="Sidebar - Schedule Interview",
        ),
        MultiFieldPanel(
            [
                FieldPanel("sidebar_contact_show"),
                FieldPanel("sidebar_contact_title"),
                FieldPanel("sidebar_contact_description"),
                FieldPanel("sidebar_contact_button_text"),
                FieldPanel("sidebar_contact_button_url"),
            ],
            heading="Sidebar - Media Contact",
        ),
    ]

    # Wagtail admin panel configurations
    promote_panels = Page.promote_panels
    settings_panels = Page.settings_panels

    # Search fields for Wagtail search functionality
    search_fields = Page.search_fields + [
        index.SearchField("intro_text"),
        index.SearchField("press_kit_title"),
        index.SearchField("press_kit_description"),
    ]

    class Meta:
        verbose_name = "Media Page"


class MediaItem(Orderable):
    """Individual media/press item."""

    page = ParentalKey(
        MediaPage,
        on_delete=models.CASCADE,
        related_name="media_items",
        null=True,
        blank=True,
    )
    title = models.CharField(max_length=300)
    description = RichTextField(blank=True)
    publication = models.CharField(
        max_length=200,
        blank=True,
        help_text="Publication name",
    )
    publication_date = models.DateField(blank=True, null=True)
    external_url = models.URLField(
        blank=True,
        help_text="Link to external article/coverage",
    )
    featured = models.BooleanField(
        default=False, help_text="Feature this media item at the top"
    )

    panels: ClassVar[list] = [
        FieldPanel("title"),
        FieldPanel("description"),
        FieldPanel("publication"),
        FieldPanel("publication_date"),
        FieldPanel("external_url"),
        FieldPanel("featured"),
    ]

    def __str__(self):
        return self.title

    class Meta:
        ordering: ClassVar[list] = [
            "-featured",
            "-publication_date",
        ]  # Featured first, then most recent


class ResearchPage(SafeUrlMixin, RoutablePageMixin, Page):
    """Research index page with blog posts and categories."""

    template = "public_site/research_page.html"

    intro_text = RichTextField(
        blank=True,
    )

    description = RichTextField(
        blank=True,
    )

    # Featured research section
    featured_title = models.CharField(
        max_length=200,
        blank=True,
    )
    featured_description = RichTextField(
        blank=True,
    )

    content_panels: ClassVar[list] = [
        *Page.content_panels,
        FieldPanel("intro_text"),
        FieldPanel("description"),
        MultiFieldPanel(
            [FieldPanel("featured_title"), FieldPanel("featured_description")],
            heading="Featured Research Section",
        ),
    ]

    # Wagtail admin panel configurations
    promote_panels = Page.promote_panels
    settings_panels = Page.settings_panels

    # Search fields for Wagtail search functionality
    search_fields = Page.search_fields + [
        index.SearchField("intro_text"),
        index.SearchField("description"),
    ]

    def get_posts(self):
        """Get all published blog posts for research."""
        site = self.get_site()
        if site and site.root_page:
            return (
                BlogPost.objects.descendant_of(site.root_page)
                .live()
                .public()
                .select_related("owner")
                .prefetch_related("tags__tag")
                .order_by("-first_published_at")
            )
        # Fallback for test environments or when site is not set
        return (
            BlogPost.objects.live()
            .public()
            .select_related("owner")
            .prefetch_related("tags")
            .order_by("-first_published_at")
        )

    def get_featured_posts(self):
        """Get featured blog posts."""
        return self.get_posts().filter(featured=True)[:3]

    def get_recent_posts(self):
        """Get recent blog posts."""
        return self.get_posts()[:6]

    def get_posts_by_tag(self, tag_name):
        """Get posts filtered by tag."""
        return self.get_posts().filter(tags__name=tag_name)

    def get_all_tags(self):
        """Get all tags used in posts."""
        try:
            from django.contrib.contenttypes.models import ContentType
            from taggit.models import Tag

            # Get ContentType for BlogPost
            blog_post_ct = ContentType.objects.get_for_model(BlogPost)

            return Tag.objects.filter(
                taggit_taggeditem_items__content_type=blog_post_ct
            ).distinct()
        except Exception:
            # Return empty queryset if there's any issue
            from taggit.models import Tag

            return Tag.objects.none()

    @path("")
    def post_list(self, request):
        """Default research listing."""
        posts = self.get_posts()
        featured_posts = self.get_featured_posts()
        recent_posts = self.get_recent_posts()
        all_tags = self.get_all_tags()

        # Handle search and filtering
        search_query = request.GET.get("search", "")
        tag_filter = request.GET.get("tag", "")

        if search_query:
            posts = posts.search(search_query)

        if tag_filter:
            posts = posts.filter(tags__name=tag_filter)

        paginator = Paginator(posts, 12)  # 12 posts per page
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        return self.render(
            request,
            context_overrides={
                "posts": page_obj,
                "featured_posts": featured_posts,
                "recent_posts": recent_posts,
                "all_tags": all_tags,
                "all_authors": self.get_all_authors(),
                "search_query": search_query,
                "tag_filter": tag_filter,
                "paginator": paginator,
            },
        )

    @path("tag/<str:tag>/")
    def post_by_tag(self, request, tag):
        """Filter posts by tag."""
        posts = self.get_posts().filter(tags__name=tag)
        paginator = Paginator(posts, 12)

        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        return self.render(
            request,
            context_overrides={
                "posts": page_obj,
                "tag": tag,
                "paginator": paginator,
            },
        )

    class Meta:
        verbose_name = "Research Page"


class ProcessPage(SafeUrlMixin, Page):
    """Investment process and workflow page."""

    intro_text = RichTextField(
        blank=True,
    )
    process_overview = RichTextField(
        blank=True,
    )

    # Process steps
    step1_title = models.CharField(
        max_length=200,
        blank=True,
    )
    step1_content = RichTextField(
        blank=True,
    )

    step2_title = models.CharField(
        max_length=200,
        blank=True,
    )
    step2_content = RichTextField(
        blank=True,
    )

    step3_title = models.CharField(
        max_length=200,
        blank=True,
    )
    step3_content = RichTextField(
        blank=True,
    )

    step4_title = models.CharField(
        max_length=200,
        blank=True,
    )
    step4_content = RichTextField(
        blank=True,
    )

    # Main sections
    section_header = models.CharField(
        max_length=200,
        blank=True,
    )

    # Screening step title (used in step 1)
    screening_title = models.CharField(
        max_length=200,
        blank=True,
    )
    screening_description = RichTextField(
        blank=True,
    )

    # Product-based exclusions section
    product_exclusions_title = models.CharField(
        max_length=200,
        blank=True,
    )
    product_exclusions_subtitle = RichTextField(
        blank=True,
    )

    # Conduct-based exclusions section
    conduct_exclusions_title = models.CharField(
        max_length=200,
        blank=True,
    )
    conduct_exclusions_subtitle = RichTextField(
        blank=True,
    )

    # Methodology section
    methodology_title = models.CharField(
        max_length=200,
        blank=True,
    )
    methodology_content = RichTextField(
        blank=True,
    )

    # Statistics
    exclusion_percentage = models.CharField(
        max_length=10,
        blank=True,
        help_text="Percentage of S&P 500 excluded",
    )
    exclusion_date = models.CharField(
        max_length=50,
        blank=True,
        help_text="Date of exclusion percentage calculation",
    )

    # Exclusion categories (as StreamField for flexibility)
    product_exclusions = StreamField(
        [
            (
                "exclusion_category",
                blocks.StructBlock(
                    [
                        ("title", blocks.CharBlock(max_length=200)),
                        ("items", blocks.ListBlock(blocks.CharBlock())),
                    ]
                ),
            )
        ],
        blank=True,
        use_json_field=True,
    )

    conduct_exclusions = StreamField(
        [
            (
                "exclusion_category",
                blocks.StructBlock(
                    [
                        ("title", blocks.CharBlock(max_length=200)),
                        ("items", blocks.ListBlock(blocks.CharBlock())),
                    ]
                ),
            )
        ],
        blank=True,
        use_json_field=True,
    )

    # Guiding principles section
    principles_title = models.CharField(
        max_length=200,
        blank=True,
    )
    principles_content = RichTextField(
        blank=True,
    )

    # CTA section
    cta_title = models.CharField(
        max_length=200,
        blank=True,
    )
    cta_description = RichTextField(
        blank=True,
    )

    content_panels: ClassVar[list] = [
        *Page.content_panels,
        FieldPanel("section_header"),
        FieldPanel("intro_text"),
        FieldPanel("process_overview"),
        MultiFieldPanel(
            [FieldPanel("step1_title"), FieldPanel("step1_content")], heading="Step 1"
        ),
        MultiFieldPanel(
            [FieldPanel("step2_title"), FieldPanel("step2_content")], heading="Step 2"
        ),
        MultiFieldPanel(
            [FieldPanel("step3_title"), FieldPanel("step3_content")], heading="Step 3"
        ),
        MultiFieldPanel(
            [FieldPanel("step4_title"), FieldPanel("step4_content")], heading="Step 4"
        ),
        MultiFieldPanel(
            [
                FieldPanel("screening_title"),
                FieldPanel("screening_description"),
            ],
            heading="Screening Section (Step 1 Expanded)",
        ),
        MultiFieldPanel(
            [
                FieldPanel("product_exclusions_title"),
                FieldPanel("product_exclusions_subtitle"),
                FieldPanel("product_exclusions"),
            ],
            heading="Product-Based Exclusions",
        ),
        MultiFieldPanel(
            [
                FieldPanel("conduct_exclusions_title"),
                FieldPanel("conduct_exclusions_subtitle"),
                FieldPanel("conduct_exclusions"),
            ],
            heading="Conduct-Based Exclusions",
        ),
        MultiFieldPanel(
            [
                FieldPanel("methodology_title"),
                FieldPanel("methodology_content"),
                FieldPanel("exclusion_percentage"),
                FieldPanel("exclusion_date"),
            ],
            heading="Methodology Section",
        ),
        MultiFieldPanel(
            [
                FieldPanel("principles_title"),
                FieldPanel("principles_content"),
            ],
            heading="Guiding Principles",
        ),
        MultiFieldPanel(
            [
                FieldPanel("cta_title"),
                FieldPanel("cta_description"),
            ],
            heading="Call to Action",
        ),
    ]

    # Wagtail admin panel configurations
    promote_panels = Page.promote_panels
    settings_panels = Page.settings_panels

    # Search fields for Wagtail search functionality
    search_fields = Page.search_fields + [
        index.SearchField("intro_text"),
        index.SearchField("process_overview"),
        index.SearchField("step1_title"),
        index.SearchField("step1_content"),
    ]

    class Meta:
        verbose_name = "Process Page"


class CompliancePage(SafeUrlMixin, Page):
    """Compliance-specific pages (Form ADV, exclusion lists, etc.)."""

    intro_text = RichTextField(blank=True)
    content = RichTextField()

    # Compliance metadata
    document_type = models.CharField(
        max_length=100,
        blank=True,
        choices=[
            ("form_adv", "Form ADV"),
            ("exclusion_list", "Exclusion List"),
            ("compliance_policy", "Compliance Policy"),
            ("disclosure", "Disclosure Document"),
        ],
    )
    effective_date = models.DateField(blank=True, null=True)
    version = models.CharField(max_length=20, blank=True, help_text="Document version")

    content_panels: ClassVar[list] = [
        *Page.content_panels,
        FieldPanel("intro_text"),
        FieldPanel("content"),
        MultiFieldPanel(
            [
                FieldPanel("document_type"),
                FieldPanel("effective_date"),
                FieldPanel("version"),
            ],
            heading="Compliance Information",
        ),
    ]

    # Wagtail admin panel configurations
    promote_panels = Page.promote_panels
    settings_panels = Page.settings_panels

    # Search fields for Wagtail search functionality
    search_fields = Page.search_fields + [
        index.SearchField("intro_text"),
        index.SearchField("content"),
    ]

    class Meta:
        verbose_name = "Compliance Page"


class OnboardingPage(SafeUrlMixin, Page):
    """Client onboarding form page."""

    intro_text = RichTextField(
        blank=True,
    )
    form_description = RichTextField(
        blank=True,
    )

    # Form configuration
    enable_form = models.BooleanField(
        default=True,
        help_text="Enable the onboarding form on this page",
    )

    # Thank you message
    thank_you_title = models.CharField(max_length=200, blank=True)
    thank_you_message = RichTextField(
        blank=True,
    )

    content_panels: ClassVar[list] = [
        *Page.content_panels,
        FieldPanel("intro_text"),
        FieldPanel("form_description"),
        FieldPanel("enable_form"),
        MultiFieldPanel(
            [FieldPanel("thank_you_title"), FieldPanel("thank_you_message")],
            heading="Thank You Message",
        ),
    ]

    # Wagtail admin panel configurations
    promote_panels = Page.promote_panels
    settings_panels = Page.settings_panels

    # Search fields for Wagtail search functionality
    search_fields = Page.search_fields + [
        index.SearchField("intro_text"),
        index.SearchField("form_description"),
        index.SearchField("thank_you_title"),
        index.SearchField("thank_you_message"),
    ]

    # Override the template to use the comprehensive version
    template = "public_site/onboarding_page_comprehensive.html"

    class Meta:
        verbose_name = "Onboarding Page"


# Strategy Page Related Models


class StrategyRiskMetric(models.Model):
    """Risk and quality metrics for a strategy"""

    page = ParentalKey(
        "StrategyPage", on_delete=models.CASCADE, related_name="risk_metrics"
    )

    standard_deviation = models.CharField(
        max_length=20, blank=True, help_text="e.g., 16.2%"
    )
    sharpe_ratio = models.CharField(max_length=20, blank=True, help_text="e.g., 0.78")
    max_drawdown = models.CharField(max_length=20, blank=True, help_text="e.g., -22.1%")
    beta = models.CharField(max_length=20, blank=True, help_text="e.g., 0.94")

    panels = [
        FieldPanel("standard_deviation"),
        FieldPanel("sharpe_ratio"),
        FieldPanel("max_drawdown"),
        FieldPanel("beta"),
    ]


class StrategyGeographicAllocation(Orderable):
    """Geographic allocation for a strategy"""

    page = ParentalKey(
        "StrategyPage", on_delete=models.CASCADE, related_name="geographic_allocations"
    )

    region = models.CharField(
        max_length=100, help_text="e.g., United States, International"
    )
    allocation_percent = models.CharField(max_length=20, help_text="e.g., 78.0%")
    benchmark_percent = models.CharField(max_length=20, help_text="e.g., 62.0%")
    difference_percent = models.CharField(max_length=20, help_text="e.g., +16.0%")

    panels = [
        FieldPanel("region"),
        FieldPanel("allocation_percent"),
        FieldPanel("benchmark_percent"),
        FieldPanel("difference_percent"),
    ]


class StrategySectorPosition(Orderable):
    """Sector overweights/exclusions for a strategy"""

    page = ParentalKey(
        "StrategyPage", on_delete=models.CASCADE, related_name="sector_positions"
    )

    POSITION_TYPE_CHOICES = [
        ("overweight", "Overweight"),
        ("exclusion", "Exclusion"),
    ]

    position_type = models.CharField(max_length=20, choices=POSITION_TYPE_CHOICES)
    sector_name = models.CharField(max_length=100)
    note = models.TextField(blank=True, help_text="Additional notes about this sector")

    panels = [
        FieldPanel("position_type"),
        FieldPanel("sector_name"),
        FieldPanel("note"),
    ]


class StrategyHolding(Orderable):
    """Top holdings for a strategy"""

    page = ParentalKey(
        "StrategyPage", on_delete=models.CASCADE, related_name="holdings"
    )

    company_name = models.CharField(max_length=200)
    ticker_symbol = models.CharField(max_length=20)
    weight_percent = models.CharField(max_length=20, help_text="e.g., ~8.4%")
    vertical = models.CharField(
        max_length=100, help_text="e.g., Lending, Real Estate, Innovation"
    )
    investment_thesis = models.TextField()
    key_metrics = models.TextField(
        help_text="e.g., 40%+ annual revenue growth, AI market leader"
    )

    panels = [
        FieldPanel("company_name"),
        FieldPanel("ticker_symbol"),
        FieldPanel("weight_percent"),
        FieldPanel("vertical"),
        FieldPanel("investment_thesis"),
        FieldPanel("key_metrics"),
    ]


class StrategyVerticalAllocation(Orderable):
    """Vertical allocation breakdown for a strategy"""

    page = ParentalKey(
        "StrategyPage", on_delete=models.CASCADE, related_name="vertical_allocations"
    )

    vertical_name = models.CharField(max_length=100)
    weight_percent = models.CharField(max_length=20)
    dividend_yield = models.CharField(max_length=20)
    pe_ratio = models.CharField(max_length=20)
    revenue_cagr = models.CharField(max_length=20)
    fcf_market_cap = models.CharField(max_length=20)
    is_total_row = models.BooleanField(
        default=False, help_text="Check for portfolio total row"
    )
    is_benchmark_row = models.BooleanField(
        default=False, help_text="Check for benchmark comparison row"
    )

    panels = [
        FieldPanel("vertical_name"),
        FieldPanel("weight_percent"),
        FieldPanel("dividend_yield"),
        FieldPanel("pe_ratio"),
        FieldPanel("revenue_cagr"),
        FieldPanel("fcf_market_cap"),
        FieldPanel("is_total_row"),
        FieldPanel("is_benchmark_row"),
    ]


class StrategyDocument(Orderable):
    """Documents related to a strategy"""

    page = ParentalKey(
        "StrategyPage", on_delete=models.CASCADE, related_name="documents"
    )

    DOCUMENT_CATEGORY_CHOICES = [
        ("performance", "Performance Reports"),
        ("strategy", "Strategy Information"),
        ("regulatory", "Regulatory Disclosures"),
    ]

    category = models.CharField(max_length=20, choices=DOCUMENT_CATEGORY_CHOICES)
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=300)
    icon = models.CharField(
        max_length=10, default="📄", help_text="Emoji icon for document"
    )
    document_url = models.URLField(
        blank=True, help_text="Link to document if available"
    )
    requires_request = models.BooleanField(
        default=True, help_text="Document requires request"
    )

    panels = [
        FieldPanel("category"),
        FieldPanel("title"),
        FieldPanel("description"),
        FieldPanel("icon"),
        FieldPanel("document_url"),
        FieldPanel("requires_request"),
    ]


class StrategyPage(SafeUrlMixin, Page):
    """Investment strategy detail page with performance data and portfolio information."""

    template = "public_site/strategy_page_editable.html"

    # Strategy overview
    strategy_subtitle = models.CharField(
        max_length=300,
        blank=True,
        help_text="Brief description shown in header",
    )
    strategy_description = RichTextField(
        blank=True,
        help_text="Main strategy description",
    )

    # Strategy characteristics
    strategy_label = models.CharField(
        max_length=100,
        blank=True,
        help_text="Label shown on strategy card (e.g., 'Our Flagship')",
    )
    risk_level = models.CharField(
        max_length=100,
        blank=True,
    )
    ethical_implementation = models.CharField(
        max_length=100,
        blank=True,
    )
    holdings_count = models.CharField(
        max_length=50,
        blank=True,
    )
    best_for = models.CharField(max_length=100, blank=True)
    cash_allocation = models.CharField(max_length=20, blank=True)

    # Benchmark information
    benchmark_name = models.CharField(
        max_length=50,
        blank=True,
        help_text="e.g., ACWI, AGG/PFF, S&P 500",
    )

    # Performance data (enhanced with benchmark)
    ytd_return = models.CharField(max_length=20, blank=True)
    ytd_benchmark = models.CharField(max_length=20, blank=True)
    ytd_difference = models.CharField(max_length=20, blank=True)

    one_year_return = models.CharField(max_length=20, blank=True)
    one_year_benchmark = models.CharField(max_length=20, blank=True)
    one_year_difference = models.CharField(max_length=20, blank=True)

    three_year_return = models.CharField(max_length=20, blank=True)
    three_year_benchmark = models.CharField(max_length=20, blank=True)
    three_year_difference = models.CharField(max_length=20, blank=True)

    since_inception_return = models.CharField(
        max_length=20,
        blank=True,
    )
    since_inception_benchmark = models.CharField(max_length=20, blank=True)
    since_inception_difference = models.CharField(max_length=20, blank=True)
    inception_date = models.DateField(
        blank=True,
        null=True,
        help_text="Strategy inception date",
    )

    # Portfolio information
    portfolio_content = RichTextField(
        blank=True,
        help_text="Portfolio composition and holdings information",
    )

    # Sector positioning notes
    overweights_note = models.CharField(max_length=300, blank=True)
    exclusions_note = models.CharField(max_length=300, blank=True)
    healthcare_exclusion_note = models.TextField(
        blank=True,
    )

    # Commentary section
    commentary_title = models.CharField(
        max_length=200,
        blank=True,
    )
    commentary_content = RichTextField(
        blank=True,
        help_text="Current market commentary and strategy insights",
    )

    # Process section
    process_title = models.CharField(max_length=200, blank=True)
    process_content = RichTextField(
        blank=True,
        help_text="Detailed process explanation for this strategy",
    )

    # Documents section
    documents_title = models.CharField(
        max_length=200,
        blank=True,
    )
    documents_content = RichTextField(
        blank=True,
        help_text="Links to relevant documents and disclosures",
    )

    # Performance disclaimer
    performance_disclaimer = RichTextField(
        blank=True,
    )

    # Monthly performance data - new automated system
    monthly_returns = models.JSONField(
        default=dict,
        blank=True,
        help_text="Historical monthly returns data {year: {month: {strategy: %, benchmark: %}}}",
    )
    performance_last_updated = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When performance data was last updated",
    )
    latest_month_return = models.CharField(
        max_length=20,
        blank=True,
        help_text="Enter latest month return (e.g., '5.51%') - will auto-update all calculations",
    )
    latest_month_benchmark = models.CharField(
        max_length=20,
        blank=True,
        help_text="Enter latest month benchmark return (e.g., '4.64%')",
    )
    latest_month_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date of the latest monthly data (e.g., June 30, 2025)",
    )

    content_panels: ClassVar[list] = [
        *Page.content_panels,
        # Strategy Overview
        MultiFieldPanel(
            [
                FieldPanel("strategy_subtitle"),
                FieldPanel("strategy_description"),
                FieldPanel("strategy_label"),
            ],
            heading="Strategy Overview",
        ),
        # Strategy Characteristics
        MultiFieldPanel(
            [
                FieldPanel("risk_level"),
                FieldPanel("ethical_implementation"),
                FieldPanel("holdings_count"),
                FieldPanel("best_for"),
                FieldPanel("cash_allocation"),
                FieldPanel("benchmark_name"),
            ],
            heading="Strategy Characteristics",
        ),
        # Performance Data - Monthly Update System
        MultiFieldPanel(
            [
                FieldPanel("latest_month_return"),
                FieldPanel("latest_month_benchmark"),
                FieldPanel("latest_month_date"),
                FieldPanel("performance_last_updated", read_only=True),
            ],
            heading="📊 Performance Update - Enter New Month",
            help_text="Enter the latest month's performance data. All other metrics will auto-calculate when saved.",
        ),
        # Performance Data - Auto-Calculated
        MultiFieldPanel(
            [
                FieldPanel("ytd_return", read_only=True),
                FieldPanel("ytd_benchmark", read_only=True),
                FieldPanel("ytd_difference", read_only=True),
                FieldPanel("one_year_return", read_only=True),
                FieldPanel("one_year_benchmark", read_only=True),
                FieldPanel("one_year_difference", read_only=True),
                FieldPanel("three_year_return", read_only=True),
                FieldPanel("three_year_benchmark", read_only=True),
                FieldPanel("three_year_difference", read_only=True),
                FieldPanel("since_inception_return", read_only=True),
                FieldPanel("since_inception_benchmark", read_only=True),
                FieldPanel("since_inception_difference", read_only=True),
                FieldPanel("inception_date"),
            ],
            heading="📈 Calculated Performance Data (Auto-Updated)",
            classname="collapsed",
        ),
        # Risk Metrics
        InlinePanel("risk_metrics", max_num=1, heading="Risk & Quality Metrics"),
        # Geographic Allocation
        InlinePanel("geographic_allocations", heading="Geographic Composition"),
        # Sector Positioning
        MultiFieldPanel(
            [
                FieldPanel("overweights_note"),
                FieldPanel("exclusions_note"),
                FieldPanel("healthcare_exclusion_note"),
            ],
            heading="Sector Positioning Notes",
        ),
        InlinePanel("sector_positions", heading="Sector Positions"),
        # Holdings
        MultiFieldPanel(
            [
                FieldPanel("portfolio_content"),
            ],
            heading="Portfolio Information",
        ),
        InlinePanel("holdings", heading="Top Holdings"),
        # Vertical Allocation
        InlinePanel("vertical_allocations", heading="Vertical Allocation"),
        # Commentary & Process
        MultiFieldPanel(
            [
                FieldPanel("commentary_title"),
                FieldPanel("commentary_content"),
            ],
            heading="Commentary",
        ),
        MultiFieldPanel(
            [
                FieldPanel("process_title"),
                FieldPanel("process_content"),
            ],
            heading="Process",
        ),
        # Documents
        MultiFieldPanel(
            [
                FieldPanel("documents_title"),
                FieldPanel("documents_content"),
            ],
            heading="Documents Section",
        ),
        InlinePanel("documents", heading="Strategy Documents"),
        # Disclaimers
        MultiFieldPanel(
            [
                FieldPanel("performance_disclaimer"),
            ],
            heading="Disclaimers",
        ),
    ]

    # Wagtail admin panel configurations
    promote_panels = Page.promote_panels
    settings_panels = Page.settings_panels

    # Search fields for Wagtail search functionality
    search_fields = Page.search_fields + [
        index.SearchField("strategy_subtitle"),
        index.SearchField("strategy_description"),
    ]

    def save(self, *args, **kwargs):
        """Override save to auto-calculate performance when monthly data is updated."""
        # Check if we have new monthly performance data to process
        if (
            self.latest_month_return
            and self.latest_month_benchmark
            and self.latest_month_date
        ):
            # Update monthly_returns with new data
            year_str = str(self.latest_month_date.year)
            month_name = self.latest_month_date.strftime("%b")

            if not self.monthly_returns:
                self.monthly_returns = {}

            if year_str not in self.monthly_returns:
                self.monthly_returns[year_str] = {}

            self.monthly_returns[year_str][month_name] = {
                "strategy": self.latest_month_return,
                "benchmark": self.latest_month_benchmark,
            }

            # Update performance calculations
            self._update_calculated_performance()

            # Clear the input fields after processing
            self.latest_month_return = ""
            self.latest_month_benchmark = ""
            self.latest_month_date = None

            # Update timestamp
            self.performance_last_updated = timezone.now()

        super().save(*args, **kwargs)

    def _update_calculated_performance(self):
        """Update all calculated performance fields from monthly_returns data."""
        try:
            from .utils.performance_calculator import (
                update_performance_from_monthly_data,
            )

            update_performance_from_monthly_data(self, self.monthly_returns)
        except ImportError:
            # Fallback if utility is not available
            pass

    class Meta:
        verbose_name = "Strategy Page"


class StrategyListPage(SafeUrlMixin, Page):
    """Strategies listing page that displays all available investment strategies."""

    template = "public_site/strategy_list_tailwind.html"

    intro_text = RichTextField(
        blank=True,
    )
    description = RichTextField(
        blank=True,
    )

    # Strategy comparison section
    comparison_title = models.CharField(
        max_length=200,
        blank=True,
    )
    comparison_description = RichTextField(
        blank=True,
    )

    # Resources Section
    resources_section_title = models.CharField(
        max_length=200,
        blank=True,
    )
    resources_section_subtitle = models.CharField(
        max_length=200,
        blank=True,
    )
    resources_section_description = RichTextField(
        blank=True,
    )
    resources = StreamField(
        [
            (
                "resource_category",
                blocks.StructBlock(
                    [
                        ("title", blocks.CharBlock(max_length=100)),
                        ("description", blocks.TextBlock()),
                        (
                            "links",
                            blocks.ListBlock(
                                blocks.StructBlock(
                                    [
                                        ("text", blocks.CharBlock(max_length=100)),
                                        ("url", blocks.CharBlock(max_length=200)),
                                    ]
                                )
                            ),
                        ),
                    ]
                ),
            )
        ],
        blank=True,
        use_json_field=True,
        help_text="Resource categories with links",
    )

    # CTA Section
    cta_section_title = models.CharField(
        max_length=200,
        blank=True,
    )
    cta_title = models.CharField(
        max_length=200,
        blank=True,
    )
    cta_description = RichTextField(
        blank=True,
    )
    cta_buttons = StreamField(
        [
            (
                "cta_button",
                blocks.StructBlock(
                    [
                        ("text", blocks.CharBlock(max_length=100)),
                        ("url", blocks.CharBlock(max_length=200)),
                        (
                            "style",
                            blocks.ChoiceBlock(
                                choices=[
                                    ("primary", "Primary"),
                                    ("secondary", "Secondary"),
                                ],
                                default="primary",
                            ),
                        ),
                    ]
                ),
            )
        ],
        blank=True,
        use_json_field=True,
        help_text="Call to action buttons",
    )

    content_panels: ClassVar[list] = [
        *Page.content_panels,
        FieldPanel("intro_text"),
        FieldPanel("description"),
        MultiFieldPanel(
            [FieldPanel("comparison_title"), FieldPanel("comparison_description")],
            heading="Strategy Comparison Section",
        ),
        MultiFieldPanel(
            [
                FieldPanel("resources_section_title"),
                FieldPanel("resources_section_subtitle"),
                FieldPanel("resources_section_description"),
                FieldPanel("resources"),
            ],
            heading="Resources Section",
        ),
        MultiFieldPanel(
            [
                FieldPanel("cta_section_title"),
                FieldPanel("cta_title"),
                FieldPanel("cta_description"),
                FieldPanel("cta_buttons"),
            ],
            heading="Call to Action Section",
        ),
    ]

    # Wagtail admin panel configurations
    promote_panels = Page.promote_panels
    settings_panels = Page.settings_panels

    # Search fields for Wagtail search functionality
    search_fields = Page.search_fields + [
        index.SearchField("intro_text"),
        index.SearchField("description"),
        index.SearchField("comparison_title"),
        index.SearchField("comparison_description"),
    ]

    def get_strategies(self):
        """Get all published strategy pages, with flagship strategy first."""
        strategies = StrategyPage.objects.live().public()

        # Order by flagship strategy first (based on strategy_label)
        # Then alphabetically by title
        flagship_strategies = strategies.filter(
            strategy_label__icontains="flagship"
        ).order_by("title")
        other_strategies = strategies.exclude(
            strategy_label__icontains="flagship"
        ).order_by("title")

        # Combine the lists with flagship first
        return list(flagship_strategies) + list(other_strategies)

    def get_context(self, request):
        """Add strategies to template context."""
        context = super().get_context(request)
        context["strategies"] = self.get_strategies()
        return context

    class Meta:
        verbose_name = "Strategy List Page"


# Support System Models


class FAQIndexPage(SafeUrlMixin, RoutablePageMixin, Page):
    """FAQ index page with categories and search."""

    template = "public_site/faq_index_tailwind.html"

    intro_text = RichTextField(
        blank=True,
    )
    description = RichTextField(
        blank=True,
    )

    # Contact information
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(
        max_length=20,
        blank=True,
    )
    contact_address = models.CharField(
        max_length=300,
        blank=True,
    )
    meeting_link = models.URLField(blank=True)

    content_panels: ClassVar[list] = [
        *Page.content_panels,
        FieldPanel("intro_text"),
        FieldPanel("description"),
        MultiFieldPanel(
            [
                FieldPanel("contact_email"),
                FieldPanel("contact_phone"),
                FieldPanel("contact_address"),
                FieldPanel("meeting_link"),
            ],
            heading="Contact Information",
        ),
    ]

    # Wagtail admin panel configurations
    promote_panels = Page.promote_panels
    settings_panels = Page.settings_panels

    # Search fields for Wagtail search functionality
    search_fields = Page.search_fields + [
        index.SearchField("intro_text"),
        index.SearchField("description"),
    ]

    def get_articles(self):
        """Get all published FAQ articles."""
        return (
            FAQArticle.objects.child_of(self)
            .live()
            .public()
            .order_by("category", "title")
        )

    def get_articles_by_category(self, category):
        """Get articles by category."""
        return self.get_articles().filter(category=category)

    def get_categories(self):
        """Get all categories that have articles."""
        articles = self.get_articles()
        categories = set()
        for article in articles:
            if article.category:
                categories.add(article.category)
        return sorted(categories)

    @path("")
    def index_view(self, request):
        """Default support listing."""
        articles = self.get_articles()
        categories = self.get_categories()

        # Group articles by category
        articles_by_category = {}
        for category in categories:
            articles_by_category[category] = self.get_articles_by_category(category)

        return self.render(
            request,
            context_overrides={
                "articles": articles,
                "categories": categories,
                "articles_by_category": articles_by_category,
            },
        )

    @path("search/")
    def search_view(self, request):
        """Search support articles."""
        query = request.GET.get("q", "")
        articles = self.get_articles()

        if query:
            articles = articles.search(query)

        return self.render(
            request,
            context_overrides={
                "articles": articles,
                "search_query": query,
            },
        )

    class Meta:
        verbose_name = "FAQ Index Page"


class FAQArticle(SafeUrlMixin, Page):
    """Individual FAQ article."""

    template = "public_site/faq_page_tailwind.html"

    # Article content
    summary = models.TextField(
        max_length=500,
        blank=True,
        help_text="Brief summary shown on index page (max 500 characters)",
    )
    content = RichTextField(help_text="Detailed article content")

    # Classification
    category = models.CharField(
        max_length=100,
        blank=True,
        choices=[
            ("account", "Account Management & Setup"),
            ("investment", "Investment Philosophy & Options"),
            ("planning", "Financial Planning & Education"),
            ("company", "Company Information"),
            ("help", "Help & Insight"),
            ("altruist", "Altruist Platform"),
            ("general", "General Questions"),
            ("ethical_capital", "Ethical Capital Philosophy"),
            ("how_we_invest", "How We Invest"),
            ("investing_101", "Investing 101"),
            ("big_questions", "Big Questions"),
            ("investment_approach", "Investment Approach & Philosophy"),
            ("esg_integration", "ESG Integration & Analysis"),
            ("stewardship", "Stewardship & Engagement"),
            ("reporting", "Reporting & Verification"),
        ],
    )

    # Article metadata
    priority = models.IntegerField(default=0, help_text="Higher numbers appear first")
    featured = models.BooleanField(default=False, help_text="Feature this article")
    related_articles = models.CharField(
        max_length=500,
        blank=True,
        help_text="Comma-separated list of related article titles",
    )

    # SEO and search
    keywords = models.CharField(
        max_length=300,
        blank=True,
        help_text="Keywords for search and SEO",
    )

    content_panels: ClassVar[list] = [
        *Page.content_panels,
        FieldPanel("summary"),
        FieldPanel("content"),
        MultiFieldPanel(
            [FieldPanel("category"), FieldPanel("priority"), FieldPanel("featured")],
            heading="Classification",
        ),
        MultiFieldPanel(
            [FieldPanel("related_articles"), FieldPanel("keywords")],
            heading="SEO & Related Content",
        ),
    ]

    # Wagtail admin panel configurations
    promote_panels = Page.promote_panels
    settings_panels = Page.settings_panels

    search_fields: ClassVar[list] = [
        *Page.search_fields,
        index.SearchField("summary"),
        index.SearchField("content"),
        index.SearchField("keywords"),
        index.FilterField("category"),
        index.FilterField("featured"),
    ]

    def get_related_articles_list(self):
        """Get related articles based on related_articles field."""
        if not self.related_articles:
            return FAQArticle.objects.none()

        related_titles = [title.strip() for title in self.related_articles.split(",")]
        return FAQArticle.objects.filter(
            live=True,
            title__in=related_titles,
        ).exclude(id=self.id)

    class Meta:
        verbose_name = "FAQ Article"
        ordering: ClassVar[list] = ["-priority", "title"]


class ContactFormPage(SafeUrlMixin, Page):
    """Contact form page for support inquiries."""

    template = "public_site/contact_form_tailwind.html"

    intro_text = RichTextField(
        blank=True,
    )
    form_description = RichTextField(
        blank=True,
    )

    # Thank you message
    thank_you_title = models.CharField(max_length=200, blank=True)
    thank_you_message = RichTextField(
        blank=True,
    )

    # Form settings
    enable_form = models.BooleanField(blank=True)
    require_phone = models.BooleanField(
        blank=True,
        help_text="Require phone number field",
    )

    # Contact Information
    contact_section_title = models.CharField(
        max_length=200,
        blank=True,
    )
    contact_email = models.EmailField(
        blank=True,
        help_text="Primary contact email address",
    )
    contact_phone = models.CharField(
        max_length=20,
        blank=True,
        help_text="Primary contact phone number",
    )
    contact_address = models.CharField(
        max_length=200,
        blank=True,
        help_text="Business address",
    )
    business_hours = models.CharField(
        max_length=200,
        blank=True,
        help_text="Business hours",
    )

    # Consultation Sidebar
    show_consultation_sidebar = models.BooleanField(
        blank=True,
        help_text="Show consultation scheduling sidebar",
    )
    consultation_sidebar_title = models.CharField(
        max_length=200,
        blank=True,
    )
    consultation_sidebar_description = RichTextField(
        blank=True,
    )
    consultation_sidebar_button_text = models.CharField(
        max_length=100,
        blank=True,
    )
    consultation_sidebar_button_url = models.CharField(
        max_length=200,
        blank=True,
    )

    content_panels: ClassVar[list] = [
        *Page.content_panels,
        FieldPanel("intro_text"),
        FieldPanel("form_description"),
        MultiFieldPanel(
            [FieldPanel("thank_you_title"), FieldPanel("thank_you_message")],
            heading="Thank You Message",
        ),
        MultiFieldPanel(
            [FieldPanel("enable_form"), FieldPanel("require_phone")],
            heading="Form Settings",
        ),
        MultiFieldPanel(
            [
                FieldPanel("contact_section_title"),
                FieldPanel("contact_email"),
                FieldPanel("contact_phone"),
                FieldPanel("contact_address"),
                FieldPanel("business_hours"),
            ],
            heading="Contact Information",
        ),
        MultiFieldPanel(
            [
                FieldPanel("show_consultation_sidebar"),
                FieldPanel("consultation_sidebar_title"),
                FieldPanel("consultation_sidebar_description"),
                FieldPanel("consultation_sidebar_button_text"),
                FieldPanel("consultation_sidebar_button_url"),
            ],
            heading="Consultation Sidebar",
        ),
    ]

    # Wagtail admin panel configurations
    promote_panels = Page.promote_panels
    settings_panels = Page.settings_panels

    # Search fields for Wagtail search functionality
    search_fields = Page.search_fields + [
        index.SearchField("intro_text"),
        index.SearchField("form_description"),
        index.SearchField("thank_you_title"),
        index.SearchField("thank_you_message"),
    ]

    class Meta:
        verbose_name = "Contact Form Page"


class AdvisorPage(SafeUrlMixin, Page):
    """Investment Adviser services page."""

    template = "public_site/adviser_page.html"

    # Hero section
    hero_title = models.CharField(
        max_length=200,
        blank=True,
    )
    hero_subtitle = models.CharField(
        max_length=300,
        blank=True,
    )
    hero_description = RichTextField(
        blank=True,
    )

    # Services section
    services_title = models.CharField(
        max_length=200,
        blank=True,
    )
    services_content = RichTextField(
        blank=True,
    )

    # What We Offer section
    offer_section_title = models.CharField(
        max_length=200,
        blank=True,
    )
    offer_section_intro = RichTextField(
        blank=True,
    )
    services_offered = StreamField(
        [
            (
                "service",
                blocks.StructBlock(
                    [
                        ("title", blocks.CharBlock(max_length=100)),
                        ("description", blocks.RichTextBlock()),
                    ]
                ),
            )
        ],
        blank=True,
        use_json_field=True,
        help_text="Services offered to advisers",
    )

    # Partnership Benefits section
    benefits_section_title = models.CharField(
        max_length=200,
        blank=True,
    )
    benefits_section_intro = RichTextField(
        blank=True,
    )
    partnership_benefits = StreamField(
        [
            (
                "benefit",
                blocks.StructBlock(
                    [
                        ("title", blocks.CharBlock(max_length=100)),
                        ("description", blocks.RichTextBlock()),
                    ]
                ),
            )
        ],
        blank=True,
        use_json_field=True,
        help_text="Partnership benefits for advisers",
    )

    # Process Overview section
    process_section_title = models.CharField(
        max_length=200,
        blank=True,
    )
    process_steps = StreamField(
        [
            (
                "process_step",
                blocks.StructBlock(
                    [
                        ("step_number", blocks.IntegerBlock(min_value=1)),
                        ("title", blocks.CharBlock(max_length=100)),
                        ("description", blocks.TextBlock()),
                    ]
                ),
            )
        ],
        blank=True,
        use_json_field=True,
        help_text="Process steps for adviser collaboration",
    )

    # Due Diligence Resources section
    ddq_section_title = models.CharField(
        max_length=200,
        blank=True,
    )
    ddq_section_subtitle = models.CharField(
        max_length=200,
        blank=True,
    )
    ddq_section_description = RichTextField(
        blank=True,
    )
    resource_categories = StreamField(
        [
            (
                "resource_category",
                blocks.StructBlock(
                    [
                        ("title", blocks.CharBlock(max_length=100)),
                        (
                            "resources",
                            blocks.ListBlock(
                                blocks.StructBlock(
                                    [
                                        (
                                            "icon",
                                            blocks.CharBlock(
                                                max_length=10, help_text="Emoji icon"
                                            ),
                                        ),
                                        ("title", blocks.CharBlock(max_length=100)),
                                        (
                                            "description",
                                            blocks.CharBlock(max_length=200),
                                        ),
                                        ("url", blocks.CharBlock(max_length=200)),
                                    ]
                                )
                            ),
                        ),
                    ]
                ),
            )
        ],
        blank=True,
        use_json_field=True,
        help_text="Resource categories with links",
    )

    # CTA section
    cta_section_title = models.CharField(
        max_length=200,
        blank=True,
    )
    cta_primary_text = models.CharField(
        max_length=100,
        blank=True,
    )
    cta_primary_url = models.URLField(
        blank=True,
    )
    cta_secondary_text = models.CharField(
        max_length=100,
        blank=True,
    )
    cta_secondary_url = models.CharField(
        max_length=200,
        blank=True,
    )

    # Benefits section
    benefits_title = models.CharField(
        max_length=200,
        blank=True,
    )
    benefits_content = RichTextField(
        blank=True,
    )

    # Technology section
    technology_title = models.CharField(
        max_length=200,
        blank=True,
    )
    technology_content = RichTextField(
        blank=True,
    )

    # CTA section
    cta_title = models.CharField(
        max_length=200,
        blank=True,
    )
    cta_description = RichTextField(
        blank=True,
    )

    content_panels: ClassVar[list] = [
        *Page.content_panels,
        MultiFieldPanel(
            [
                FieldPanel("hero_title"),
                FieldPanel("hero_subtitle"),
                FieldPanel("hero_description"),
            ],
            heading="Hero Section",
        ),
        MultiFieldPanel(
            [FieldPanel("services_title"), FieldPanel("services_content")],
            heading="Services Section",
        ),
        MultiFieldPanel(
            [
                FieldPanel("offer_section_title"),
                FieldPanel("offer_section_intro"),
                FieldPanel("services_offered"),
            ],
            heading="What We Offer Section",
        ),
        MultiFieldPanel(
            [FieldPanel("benefits_title"), FieldPanel("benefits_content")],
            heading="Benefits Section (Legacy)",
        ),
        MultiFieldPanel(
            [
                FieldPanel("benefits_section_title"),
                FieldPanel("benefits_section_intro"),
                FieldPanel("partnership_benefits"),
            ],
            heading="Partnership Benefits Section",
        ),
        MultiFieldPanel(
            [
                FieldPanel("process_section_title"),
                FieldPanel("process_steps"),
            ],
            heading="Process Overview Section",
        ),
        MultiFieldPanel(
            [
                FieldPanel("ddq_section_title"),
                FieldPanel("ddq_section_subtitle"),
                FieldPanel("ddq_section_description"),
                FieldPanel("resource_categories"),
            ],
            heading="Due Diligence Resources Section",
        ),
        MultiFieldPanel(
            [FieldPanel("technology_title"), FieldPanel("technology_content")],
            heading="Technology Section",
        ),
        MultiFieldPanel(
            [
                FieldPanel("cta_section_title"),
                FieldPanel("cta_primary_text"),
                FieldPanel("cta_primary_url"),
                FieldPanel("cta_secondary_text"),
                FieldPanel("cta_secondary_url"),
            ],
            heading="Call to Action Section",
        ),
        MultiFieldPanel(
            [FieldPanel("cta_title"), FieldPanel("cta_description")],
            heading="Legacy CTA (Deprecated)",
            classname="collapsed",
        ),
    ]

    # Wagtail admin panel configurations
    promote_panels = Page.promote_panels
    settings_panels = Page.settings_panels

    # Search fields for Wagtail search functionality
    search_fields = Page.search_fields + [
        index.SearchField("hero_title"),
        index.SearchField("hero_subtitle"),
        index.SearchField("hero_description"),
    ]

    class Meta:
        verbose_name = "Adviser Page"


class InstitutionalPage(SafeUrlMixin, Page):
    """Institutional services page."""

    template = "public_site/institutional_page.html"

    # Hero section
    hero_title = models.CharField(
        max_length=200,
        blank=True,
    )
    hero_subtitle = models.CharField(
        max_length=300,
        blank=True,
    )
    hero_description = RichTextField(
        blank=True,
    )

    # Solutions section
    solutions_title = models.CharField(
        max_length=200,
        blank=True,
    )
    solutions_content = RichTextField(
        blank=True,
    )

    # What We Offer section
    offer_section_title = models.CharField(
        max_length=200,
        blank=True,
    )
    offer_section_intro = RichTextField(
        blank=True,
    )
    services = StreamField(
        [
            (
                "service",
                blocks.StructBlock(
                    [
                        ("title", blocks.CharBlock(max_length=100)),
                        ("description", blocks.RichTextBlock()),
                    ]
                ),
            )
        ],
        blank=True,
        use_json_field=True,
        help_text="Services offered to institutions",
    )

    # Partnership Benefits section
    benefits_section_title = models.CharField(
        max_length=200,
        blank=True,
    )
    benefits_section_intro = RichTextField(
        blank=True,
    )
    benefits = StreamField(
        [
            (
                "benefit",
                blocks.StructBlock(
                    [
                        ("title", blocks.CharBlock(max_length=100)),
                        ("description", blocks.RichTextBlock()),
                    ]
                ),
            )
        ],
        blank=True,
        use_json_field=True,
        help_text="Partnership benefits for institutions",
    )

    # Process Overview section
    process_section_title = models.CharField(
        max_length=200,
        blank=True,
    )
    process_steps = StreamField(
        [
            (
                "process_step",
                blocks.StructBlock(
                    [
                        ("step_number", blocks.IntegerBlock(min_value=1)),
                        ("title", blocks.CharBlock(max_length=100)),
                        ("description", blocks.TextBlock()),
                    ]
                ),
            )
        ],
        blank=True,
        use_json_field=True,
        help_text="Process steps for institutional collaboration",
    )

    # Scale & Capabilities section
    scale_section_title = models.CharField(
        max_length=200,
        blank=True,
    )
    scale_section_intro = RichTextField(
        blank=True,
    )
    scale_metrics = StreamField(
        [
            (
                "metric",
                blocks.StructBlock(
                    [
                        ("value", blocks.CharBlock(max_length=20)),
                        ("label", blocks.CharBlock(max_length=20)),
                        ("description", blocks.TextBlock()),
                    ]
                ),
            )
        ],
        blank=True,
        use_json_field=True,
        help_text="Scale and capability metrics",
    )

    # Due Diligence Resources section
    ddq_section_title = models.CharField(
        max_length=200,
        blank=True,
    )
    ddq_section_subtitle = models.CharField(
        max_length=200,
        blank=True,
    )
    ddq_section_description = RichTextField(
        blank=True,
    )
    resource_categories = StreamField(
        [
            (
                "resource_category",
                blocks.StructBlock(
                    [
                        ("title", blocks.CharBlock(max_length=100)),
                        (
                            "resources",
                            blocks.ListBlock(
                                blocks.StructBlock(
                                    [
                                        (
                                            "icon",
                                            blocks.CharBlock(
                                                max_length=10, help_text="Emoji icon"
                                            ),
                                        ),
                                        ("title", blocks.CharBlock(max_length=100)),
                                        (
                                            "description",
                                            blocks.CharBlock(max_length=200),
                                        ),
                                        ("url", blocks.CharBlock(max_length=200)),
                                    ]
                                )
                            ),
                        ),
                    ]
                ),
            )
        ],
        blank=True,
        use_json_field=True,
        help_text="Resource categories with links",
    )

    # CTA section updates
    cta_section_title = models.CharField(
        max_length=200,
        blank=True,
    )
    cta_primary_text = models.CharField(
        max_length=100,
        blank=True,
    )
    cta_primary_url = models.URLField(
        blank=True,
    )
    cta_secondary_text = models.CharField(
        max_length=100,
        blank=True,
    )
    cta_secondary_url = models.CharField(
        max_length=200,
        blank=True,
    )

    # Capabilities section
    capabilities_title = models.CharField(
        max_length=200,
        blank=True,
    )
    capabilities_content = RichTextField(blank=True)

    # Scale section
    scale_title = models.CharField(
        max_length=200,
        blank=True,
    )
    scale_content = RichTextField(
        blank=True,
    )

    # CTA section
    cta_title = models.CharField(
        max_length=200,
        blank=True,
    )
    cta_description = RichTextField(
        blank=True,
    )

    content_panels: ClassVar[list] = [
        *Page.content_panels,
        MultiFieldPanel(
            [
                FieldPanel("hero_title"),
                FieldPanel("hero_subtitle"),
                FieldPanel("hero_description"),
            ],
            heading="Hero Section",
        ),
        MultiFieldPanel(
            [
                FieldPanel("offer_section_title"),
                FieldPanel("offer_section_intro"),
                FieldPanel("services"),
            ],
            heading="What We Offer Section",
        ),
        MultiFieldPanel(
            [
                FieldPanel("benefits_section_title"),
                FieldPanel("benefits_section_intro"),
                FieldPanel("benefits"),
            ],
            heading="Partnership Benefits Section",
        ),
        MultiFieldPanel(
            [
                FieldPanel("process_section_title"),
                FieldPanel("process_steps"),
            ],
            heading="Process Overview Section",
        ),
        MultiFieldPanel(
            [
                FieldPanel("scale_section_title"),
                FieldPanel("scale_section_intro"),
                FieldPanel("scale_metrics"),
            ],
            heading="Scale & Capabilities Section",
        ),
        MultiFieldPanel(
            [
                FieldPanel("ddq_section_title"),
                FieldPanel("ddq_section_subtitle"),
                FieldPanel("ddq_section_description"),
                FieldPanel("resource_categories"),
            ],
            heading="Due Diligence Resources Section",
        ),
        MultiFieldPanel(
            [
                FieldPanel("cta_section_title"),
                FieldPanel("cta_title"),
                FieldPanel("cta_description"),
                FieldPanel("cta_primary_text"),
                FieldPanel("cta_primary_url"),
                FieldPanel("cta_secondary_text"),
                FieldPanel("cta_secondary_url"),
            ],
            heading="Call to Action Section",
        ),
        MultiFieldPanel(
            [FieldPanel("solutions_title"), FieldPanel("solutions_content")],
            heading="Solutions Section (Legacy)",
        ),
        MultiFieldPanel(
            [FieldPanel("capabilities_title"), FieldPanel("capabilities_content")],
            heading="Capabilities Section (Legacy)",
        ),
        MultiFieldPanel(
            [FieldPanel("scale_title"), FieldPanel("scale_content")],
            heading="Scale Section (Legacy)",
        ),
    ]

    # Wagtail admin panel configurations
    promote_panels = Page.promote_panels
    settings_panels = Page.settings_panels

    # Search fields for Wagtail search functionality
    search_fields = Page.search_fields + [
        index.SearchField("hero_title"),
        index.SearchField("hero_subtitle"),
        index.SearchField("hero_description"),
    ]

    class Meta:
        verbose_name = "Institutional Page"


class SupportTicket(models.Model):
    """Support ticket/contact form submission."""

    # Contact information
    name = models.CharField(max_length=255, null=False, blank=False)
    email = models.EmailField(null=False, blank=False)
    company = models.CharField(max_length=255, blank=True, null=True)

    # Ticket type
    ticket_type = models.CharField(
        max_length=20,
        default="contact",
        choices=[
            ("contact", "Contact Form"),
            ("newsletter", "Newsletter Signup"),
            ("onboarding", "Onboarding Request"),
            ("garden_interest", "Garden Platform Interest"),
        ],
    )

    # Inquiry details
    subject = models.CharField(max_length=255, null=False, blank=False)
    message = models.TextField(null=False, blank=False)

    # Status and priority
    status = models.CharField(
        max_length=20,
        default="new",
        choices=[
            ("new", "New"),
            ("in_progress", "In Progress"),
            ("resolved", "Resolved"),
            ("closed", "Closed"),
        ],
    )
    priority = models.CharField(
        max_length=10,
        default="medium",
        choices=[
            ("low", "Low"),
            ("medium", "Medium"),
            ("high", "High"),
            ("urgent", "Urgent"),
        ],
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(blank=True, null=True)

    # Internal notes
    notes = models.TextField(
        blank=True,
        help_text="Internal notes about this ticket",
    )

    # External tracking
    external_reference = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="External submission ID for tracking secure API submissions",
    )

    class Meta:
        verbose_name = "Support Ticket"
        verbose_name_plural = "Support Tickets"
        ordering = ["-created_at"]

    def __str__(self):
        return f"#{self.id} - {self.subject or 'General Inquiry'} - {self.email}"


class EncyclopediaIndexPage(SafeUrlMixin, RoutablePageMixin, Page):
    """Investment Encyclopedia index page with alphabetical navigation."""

    template = "public_site/encyclopedia_index.html"

    intro_text = RichTextField(
        blank=True,
    )
    description = RichTextField(
        blank=True,
    )

    content_panels: ClassVar[list] = [
        *Page.content_panels,
        FieldPanel("intro_text"),
        FieldPanel("description"),
    ]

    # Wagtail admin panel configurations
    promote_panels = Page.promote_panels
    settings_panels = Page.settings_panels

    # Search fields for Wagtail search functionality
    search_fields = Page.search_fields + [
        index.SearchField("intro_text"),
        index.SearchField("description"),
    ]

    def get_entries(self):
        """Get all published encyclopedia entries."""
        return (
            EncyclopediaEntry.objects.child_of(self).live().public().order_by("title")
        )

    def get_entries_by_letter(self, letter):
        """Get entries that start with a specific letter."""
        return self.get_entries().filter(title__istartswith=letter)

    def get_available_letters(self):
        """Get all letters that have entries."""
        entries = self.get_entries()
        letters = set()
        for entry in entries:
            if entry.title:
                letters.add(entry.title[0].upper())
        return sorted(letters)

    @path("")
    def index_view(self, request):
        """Default encyclopedia listing."""
        entries = self.get_entries()
        letters = self.get_available_letters()

        return self.render(
            request,
            context_overrides={
                "entries": entries,
                "available_letters": letters,
                "selected_letter": None,
            },
        )

    @path("<str:letter>/")
    def entries_by_letter(self, request, letter):
        """Filter entries by first letter."""
        letter = letter.upper()
        entries = self.get_entries_by_letter(letter)
        available_letters = self.get_available_letters()

        return self.render(
            request,
            context_overrides={
                "entries": entries,
                "available_letters": available_letters,
                "selected_letter": letter,
            },
        )

    class Meta:
        verbose_name = "Encyclopedia Index Page"


class EncyclopediaEntry(SafeUrlMixin, Page):
    """Individual encyclopedia entry."""

    template = "public_site/encyclopedia_entry.html"

    # Entry content
    summary = models.TextField(
        max_length=500,
        help_text="Brief summary shown on index page (max 500 characters)",
    )
    detailed_content = RichTextField(help_text="Detailed explanation of the term")

    # Classification
    category = models.CharField(
        max_length=100,
        blank=True,
        choices=[
            ("risk", "Risk Management"),
            ("strategy", "Investment Strategy"),
            ("instruments", "Financial Instruments"),
            ("analysis", "Analysis & Research"),
            ("ethics", "Ethical Investing"),
            ("markets", "Markets & Trading"),
            ("regulation", "Regulation & Compliance"),
            ("general", "General Finance"),
        ],
    )

    # SEO and metadata
    related_terms = models.CharField(
        max_length=500, blank=True, help_text="Comma-separated list of related terms"
    )
    difficulty_level = models.CharField(
        max_length=20,
        blank=True,
        choices=[
            ("beginner", "Beginner"),
            ("intermediate", "Intermediate"),
            ("advanced", "Advanced"),
        ],
    )

    # Content organization
    examples = RichTextField(blank=True, help_text="Examples and use cases")
    further_reading = RichTextField(
        blank=True, help_text="Links to additional resources"
    )

    content_panels: ClassVar[list] = [
        *Page.content_panels,
        FieldPanel("summary"),
        FieldPanel("detailed_content"),
        MultiFieldPanel(
            [
                FieldPanel("category"),
                FieldPanel("difficulty_level"),
                FieldPanel("related_terms"),
            ],
            heading="Classification",
        ),
        MultiFieldPanel(
            [FieldPanel("examples"), FieldPanel("further_reading")],
            heading="Additional Content",
        ),
    ]

    # Wagtail admin panel configurations
    promote_panels = Page.promote_panels
    settings_panels = Page.settings_panels

    search_fields: ClassVar[list] = [
        *Page.search_fields,
        index.SearchField("summary"),
        index.SearchField("detailed_content"),
        index.SearchField("related_terms"),
        index.FilterField("category"),
        index.FilterField("difficulty_level"),
    ]

    def get_related_entries(self):
        """Get entries related to this one based on related_terms."""
        if not self.related_terms:
            return EncyclopediaEntry.objects.none()

        related_terms = [term.strip().lower() for term in self.related_terms.split(",")]
        return EncyclopediaEntry.objects.filter(
            live=True, title__iregex=r"\b(?:" + "|".join(related_terms) + r")\b"
        ).exclude(id=self.id)[:5]

    class Meta:
        verbose_name = "Encyclopedia Entry"


class ConsultationPage(SafeUrlMixin, Page):
    """Consultation scheduling page."""

    template = "public_site/consultation_page.html"

    # Hero content
    hero_title = models.CharField(max_length=200, blank=True, help_text="Main headline")
    hero_subtitle = models.TextField(
        max_length=500,
        blank=True,
        help_text="Subtitle text below the main headline",
    )

    # Main content
    introduction = RichTextField(
        blank=True, help_text="Introduction text explaining the consultation process"
    )

    # Contact information
    contact_email = models.EmailField(
        blank=True,
        help_text="Contact email for consultations",
    )

    # Scheduling widget (optional - can be embedded)
    scheduling_embed_code = models.TextField(
        blank=True,
        help_text="Optional: Embed code for scheduling widget (Calendly, etc.)",
    )

    # Schedule Section
    schedule_section_title = models.CharField(
        max_length=200,
        blank=True,
    )
    schedule_intro_text = RichTextField(
        blank=True,
    )

    # Consultation Types
    consultation_types = StreamField(
        [
            (
                "consultation_type",
                blocks.StructBlock(
                    [
                        (
                            "icon",
                            blocks.CharBlock(max_length=10, help_text="Emoji icon"),
                        ),
                        ("title", blocks.CharBlock(max_length=100)),
                        ("description", blocks.TextBlock()),
                        (
                            "button_text",
                            blocks.CharBlock(max_length=50, default="Schedule Call"),
                        ),
                        ("button_url", blocks.URLBlock()),
                    ]
                ),
            )
        ],
        blank=True,
        use_json_field=True,
        help_text="Different consultation types available",
    )

    # Alternative Contact
    alternative_contact_text = RichTextField(
        blank=True,
    )

    # Expectations Section
    expectations_section_title = models.CharField(
        max_length=200,
        blank=True,
    )
    expectations = StreamField(
        [
            (
                "expectation",
                blocks.StructBlock(
                    [
                        ("title", blocks.CharBlock(max_length=100)),
                        ("description", blocks.TextBlock()),
                    ]
                ),
            )
        ],
        blank=True,
        use_json_field=True,
        help_text="What to expect during consultation",
    )

    # Disclaimer
    disclaimer_title = models.CharField(
        max_length=200,
        blank=True,
    )
    disclaimer_text = RichTextField(
        blank=True,
    )

    content_panels: ClassVar[list] = [
        *Page.content_panels,
        MultiFieldPanel(
            [FieldPanel("hero_title"), FieldPanel("hero_subtitle")],
            heading="Hero Section",
        ),
        FieldPanel("introduction"),
        MultiFieldPanel(
            [
                FieldPanel("schedule_section_title"),
                FieldPanel("schedule_intro_text"),
                FieldPanel("consultation_types"),
                FieldPanel("alternative_contact_text"),
            ],
            heading="Schedule Section",
        ),
        MultiFieldPanel(
            [
                FieldPanel("expectations_section_title"),
                FieldPanel("expectations"),
            ],
            heading="Expectations Section",
        ),
        MultiFieldPanel(
            [
                FieldPanel("disclaimer_title"),
                FieldPanel("disclaimer_text"),
            ],
            heading="Disclaimer Section",
        ),
        MultiFieldPanel(
            [FieldPanel("contact_email"), FieldPanel("scheduling_embed_code")],
            heading="Contact & Scheduling (Legacy)",
        ),
    ]

    # Wagtail admin panel configurations
    promote_panels = Page.promote_panels
    settings_panels = Page.settings_panels

    # Search fields for Wagtail search functionality
    search_fields = Page.search_fields + [
        index.SearchField("hero_title"),
        index.SearchField("hero_subtitle"),
    ]

    class Meta:
        verbose_name = "Consultation Page"


class GuidePage(SafeUrlMixin, Page):
    """Investment guide download page."""

    template = "public_site/guide_page.html"

    # Hero content
    hero_title = models.CharField(max_length=200, blank=True, help_text="Main headline")
    hero_subtitle = models.TextField(
        max_length=500,
        blank=True,
        help_text="Subtitle text below the main headline",
    )

    # Guide content
    guide_description = RichTextField(
        blank=True, help_text="Description of what's included in the guide"
    )

    # Download link
    guide_document = models.ForeignKey(
        "wagtaildocs.Document",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="PDF or other document to download",
    )

    # Alternative external link
    external_guide_url = models.URLField(
        blank=True,
        help_text="Alternative: External URL for guide (if not using document upload)",
    )

    # Section Headers
    description_section_header = models.CharField(
        max_length=200,
        blank=True,
    )
    download_section_header = models.CharField(
        max_length=200,
        blank=True,
    )
    resources_section_header = models.CharField(
        max_length=200,
        blank=True,
    )
    newsletter_section_header = models.CharField(
        max_length=200,
        blank=True,
    )

    # Additional Resources
    resources = StreamField(
        [
            (
                "resource",
                blocks.StructBlock(
                    [
                        ("title", blocks.CharBlock(max_length=100)),
                        ("description", blocks.TextBlock()),
                        (
                            "button_text",
                            blocks.CharBlock(max_length=50, default="Learn More"),
                        ),
                        ("button_url", blocks.CharBlock(max_length=200)),
                    ]
                ),
            )
        ],
        blank=True,
        use_json_field=True,
        help_text="Additional resource links",
    )

    # Newsletter Settings
    newsletter_description = RichTextField(
        blank=True,
    )

    content_panels: ClassVar[list] = [
        *Page.content_panels,
        MultiFieldPanel(
            [FieldPanel("hero_title"), FieldPanel("hero_subtitle")],
            heading="Hero Section",
        ),
        MultiFieldPanel(
            [
                FieldPanel("description_section_header"),
                FieldPanel("guide_description"),
            ],
            heading="Guide Description",
        ),
        MultiFieldPanel(
            [
                FieldPanel("download_section_header"),
                FieldPanel("guide_document"),
                FieldPanel("external_guide_url"),
            ],
            heading="Guide Download",
        ),
        MultiFieldPanel(
            [
                FieldPanel("resources_section_header"),
                FieldPanel("resources"),
            ],
            heading="Additional Resources",
        ),
        MultiFieldPanel(
            [
                FieldPanel("newsletter_section_header"),
                FieldPanel("newsletter_description"),
            ],
            heading="Newsletter Section",
        ),
    ]

    # Wagtail admin panel configurations
    promote_panels = Page.promote_panels
    settings_panels = Page.settings_panels

    # Search fields for Wagtail search functionality
    search_fields = Page.search_fields + [
        index.SearchField("hero_title"),
        index.SearchField("hero_subtitle"),
    ]

    class Meta:
        verbose_name = "Guide Page"


class ExclusionCategory(Orderable):
    """Exclusion category for criteria page."""

    page = ParentalKey(
        "CriteriaPage", on_delete=models.CASCADE, related_name="exclusion_categories"
    )

    icon = models.CharField(
        max_length=10, default="🚫", help_text="Emoji icon for category"
    )
    title = models.CharField(max_length=100, help_text="Category title")
    description = models.TextField(
        help_text="Description of what is excluded in this category"
    )

    panels = [
        FieldPanel("icon"),
        FieldPanel("title"),
        FieldPanel("description"),
    ]


class CriteriaPage(SafeUrlMixin, Page):
    """Ethical criteria page - links to GitHub."""

    template = "public_site/criteria_page_editable.html"

    # Hero content
    hero_title = models.CharField(max_length=200, blank=True, help_text="Main headline")
    hero_subtitle = models.TextField(
        max_length=500,
        blank=True,
        help_text="Subtitle text below the main headline",
    )

    # Content
    criteria_description = RichTextField(
        blank=True, help_text="Description of the criteria and screening process"
    )

    # GitHub link section
    transparency_section_title = models.CharField(
        max_length=200,
        blank=True,
        help_text="Title for transparency section",
    )
    transparency_description = RichTextField(
        blank=True,
        help_text="Description of transparency approach",
    )
    transparency_benefits = models.TextField(
        blank=True,
        help_text="Benefits of transparency, one per line",
    )
    github_criteria_url = models.URLField(
        blank=True,
        help_text="URL to GitHub screening policy",
    )

    # Exclusions section
    exclusions_section_title = models.CharField(
        max_length=200,
        blank=True,
        help_text="Title for exclusions section",
    )
    exclusions_note = RichTextField(
        blank=True,
        help_text="Note about exclusions",
    )

    # Additional resources
    additional_resources = RichTextField(
        blank=True, help_text="Links to additional resources and documentation"
    )

    content_panels: ClassVar[list] = [
        *Page.content_panels,
        MultiFieldPanel(
            [FieldPanel("hero_title"), FieldPanel("hero_subtitle")],
            heading="Hero Section",
        ),
        FieldPanel("criteria_description"),
        MultiFieldPanel(
            [
                FieldPanel("transparency_section_title"),
                FieldPanel("transparency_description"),
                FieldPanel("transparency_benefits"),
                FieldPanel("github_criteria_url"),
            ],
            heading="Transparency Section",
        ),
        MultiFieldPanel(
            [
                FieldPanel("exclusions_section_title"),
                InlinePanel("exclusion_categories", label="Exclusion Categories"),
                FieldPanel("exclusions_note"),
            ],
            heading="Exclusions Section",
        ),
        FieldPanel("additional_resources"),
    ]

    # Wagtail admin panel configurations
    promote_panels = Page.promote_panels
    settings_panels = Page.settings_panels

    # Search fields for Wagtail search functionality
    search_fields = Page.search_fields + [
        index.SearchField("hero_title"),
        index.SearchField("hero_subtitle"),
    ]

    class Meta:
        verbose_name = "Criteria Page"


class StrategyCard(Orderable):
    """Strategy card for solutions page."""

    page = ParentalKey(
        "SolutionsPage", on_delete=models.CASCADE, related_name="strategy_cards"
    )

    icon = models.CharField(
        max_length=10, default="🚀", help_text="Emoji icon for strategy"
    )
    title = models.CharField(max_length=100, help_text="Strategy title")
    description = models.TextField(help_text="Brief description of the strategy")
    features = models.TextField(help_text="Strategy features, one per line")
    url = models.CharField(max_length=200, help_text="URL to strategy page")

    panels = [
        FieldPanel("icon"),
        FieldPanel("title"),
        FieldPanel("description"),
        FieldPanel("features"),
        FieldPanel("url"),
    ]


class SolutionsPage(SafeUrlMixin, Page):
    """Solutions page showcasing services for individuals, institutions, and advisers."""

    template = "public_site/solutions_page_editable.html"

    # Hero content
    hero_title = models.CharField(max_length=200, blank=True, help_text="Main headline")
    hero_subtitle = models.TextField(
        max_length=500,
        blank=True,
        help_text="Subtitle text below the main headline",
    )
    hero_description = RichTextField(
        blank=True,
        help_text="Hero section description",
    )

    # Strategies section
    strategies_section_title = models.CharField(
        max_length=200,
        blank=True,
        help_text="Title for strategies section",
    )
    strategies_intro = models.TextField(
        blank=True,
        help_text="Introduction text for strategies section",
    )

    # Individuals section
    individuals_title = models.CharField(max_length=200, blank=True)
    individuals_content = RichTextField(
        blank=True,
    )

    # Institutions section
    institutions_title = models.CharField(max_length=200, blank=True)
    institutions_content = RichTextField(
        blank=True,
    )

    # Advisors section
    advisors_title = models.CharField(max_length=200, blank=True)
    advisors_content = RichTextField(
        blank=True,
    )

    # Call to action
    cta_title = models.CharField(max_length=200, blank=True)
    cta_description = RichTextField(
        blank=True,
    )

    content_panels: ClassVar[list] = [
        *Page.content_panels,
        MultiFieldPanel(
            [
                FieldPanel("hero_title"),
                FieldPanel("hero_subtitle"),
                FieldPanel("hero_description"),
            ],
            heading="Hero Section",
        ),
        MultiFieldPanel(
            [
                FieldPanel("strategies_section_title"),
                FieldPanel("strategies_intro"),
                InlinePanel("strategy_cards", label="Strategy Cards"),
            ],
            heading="Investment Strategies",
        ),
        MultiFieldPanel(
            [FieldPanel("individuals_title"), FieldPanel("individuals_content")],
            heading="For Individuals",
        ),
        MultiFieldPanel(
            [FieldPanel("institutions_title"), FieldPanel("institutions_content")],
            heading="For Institutions",
        ),
        MultiFieldPanel(
            [FieldPanel("advisors_title"), FieldPanel("advisors_content")],
            heading="For Investment Advisers",
        ),
        MultiFieldPanel(
            [FieldPanel("cta_title"), FieldPanel("cta_description")],
            heading="Call to Action",
        ),
    ]

    # Wagtail admin panel configurations
    promote_panels = Page.promote_panels
    settings_panels = Page.settings_panels

    # Search fields for Wagtail search functionality
    search_fields = Page.search_fields + [
        index.SearchField("hero_title"),
        index.SearchField("hero_subtitle"),
        index.SearchField("hero_description"),
    ]

    class Meta:
        verbose_name = "Solutions Page"


class PRIDDQPage(SafeUrlMixin, Page):
    """PRI Due Diligence Questionnaire response page."""

    template = "public_site/pri_ddq_page.html"

    # Hero content
    hero_title = models.CharField(
        max_length=200,
        blank=True,
        help_text="Main headline",
    )
    hero_subtitle = models.TextField(
        max_length=500,
        blank=True,
        help_text="Subtitle text below the main headline",
    )
    hero_description = RichTextField(
        blank=True,
        help_text="Hero section description",
    )
    updated_at = models.CharField(
        max_length=50,
        blank=True,
        help_text="Month and year when this document was last updated",
    )

    # Executive Summary
    executive_summary = RichTextField(
        blank=True,
        help_text="Executive summary of ESG approach",
    )

    # Strategy & Governance section
    strategy_governance_content = RichTextField(
        blank=True, help_text="Strategy and governance practices content"
    )

    # ESG Integration section
    esg_integration_content = RichTextField(
        blank=True, help_text="ESG integration methodology and practices"
    )

    # Stewardship section
    stewardship_content = RichTextField(
        blank=True, help_text="Stewardship and engagement practices"
    )

    # Transparency section
    transparency_content = RichTextField(
        blank=True, help_text="Reporting and transparency practices"
    )

    # Climate & Environment section
    climate_content = RichTextField(
        blank=True, help_text="Climate change and environmental practices"
    )

    # Reporting & Verification section
    reporting_verification_content = RichTextField(
        blank=True, help_text="Reporting and verification practices content"
    )

    # Additional Information section
    additional_content = RichTextField(
        blank=True, help_text="Additional information and internal ESG management"
    )

    # Section Headers - Panel Titles
    section_title_overview = models.CharField(
        max_length=100,
        blank=True,
        help_text="Panel title for overview section",
    )
    section_title_executive = models.CharField(
        max_length=100,
        blank=True,
        help_text="Panel title for executive summary section",
    )
    section_title_strategy = models.CharField(
        max_length=100,
        blank=True,
        help_text="Panel title for strategy section",
    )
    section_title_esg = models.CharField(
        max_length=100,
        blank=True,
        help_text="Panel title for ESG integration section",
    )
    section_title_stewardship = models.CharField(
        max_length=100,
        blank=True,
        help_text="Panel title for stewardship section",
    )
    section_title_transparency = models.CharField(
        max_length=100,
        blank=True,
        help_text="Panel title for transparency section",
    )
    section_title_climate = models.CharField(
        max_length=100,
        blank=True,
        help_text="Panel title for climate section",
    )
    section_title_reporting = models.CharField(
        max_length=100,
        blank=True,
        help_text="Panel title for reporting section",
    )
    section_title_additional = models.CharField(
        max_length=100,
        blank=True,
        help_text="Panel title for additional information section",
    )

    # Section Headers - Section Subtitles (h2 elements)
    section_subtitle_executive = models.CharField(
        max_length=200,
        blank=True,
        help_text="Section subtitle for executive summary",
    )
    section_subtitle_strategy = models.CharField(
        max_length=200,
        blank=True,
        help_text="Section subtitle for strategy section",
    )
    section_subtitle_esg = models.CharField(
        max_length=200,
        blank=True,
        help_text="Section subtitle for ESG integration",
    )
    section_subtitle_stewardship = models.CharField(
        max_length=200,
        blank=True,
        help_text="Section subtitle for stewardship",
    )
    section_subtitle_transparency = models.CharField(
        max_length=200,
        blank=True,
        help_text="Section subtitle for transparency",
    )
    section_subtitle_climate = models.CharField(
        max_length=200,
        blank=True,
        help_text="Section subtitle for climate",
    )
    section_subtitle_reporting = models.CharField(
        max_length=200,
        blank=True,
        help_text="Section subtitle for reporting",
    )
    section_subtitle_additional = models.CharField(
        max_length=200,
        blank=True,
        help_text="Section subtitle for additional information",
    )

    # Document links
    screening_policy_url = models.URLField(
        blank=True,
        help_text="URL to open-source screening policy",
    )
    form_adv_url = models.URLField(
        blank=True,
        help_text="URL to Form ADV disclosure",
    )

    content_panels: ClassVar[list] = [
        *Page.content_panels,
        MultiFieldPanel(
            [
                FieldPanel("hero_title"),
                FieldPanel("hero_subtitle"),
                FieldPanel("hero_description"),
                FieldPanel("updated_at"),
            ],
            heading="Hero Section",
        ),
        MultiFieldPanel(
            [
                FieldPanel("section_title_overview"),
                FieldPanel("section_title_executive"),
                FieldPanel("section_title_strategy"),
                FieldPanel("section_title_esg"),
                FieldPanel("section_title_stewardship"),
                FieldPanel("section_title_transparency"),
                FieldPanel("section_title_climate"),
                FieldPanel("section_title_reporting"),
                FieldPanel("section_title_additional"),
            ],
            heading="Section Panel Titles",
        ),
        MultiFieldPanel(
            [
                FieldPanel("section_subtitle_executive"),
                FieldPanel("section_subtitle_strategy"),
                FieldPanel("section_subtitle_esg"),
                FieldPanel("section_subtitle_stewardship"),
                FieldPanel("section_subtitle_transparency"),
                FieldPanel("section_subtitle_climate"),
                FieldPanel("section_subtitle_reporting"),
                FieldPanel("section_subtitle_additional"),
            ],
            heading="Section Subtitles",
        ),
        FieldPanel("executive_summary"),
        MultiFieldPanel(
            [
                FieldPanel("strategy_governance_content"),
                FieldPanel("esg_integration_content"),
                FieldPanel("stewardship_content"),
                FieldPanel("transparency_content"),
                FieldPanel("reporting_verification_content"),
                FieldPanel("climate_content"),
                FieldPanel("additional_content"),
            ],
            heading="DDQ Response Sections",
        ),
        MultiFieldPanel(
            [FieldPanel("screening_policy_url"), FieldPanel("form_adv_url")],
            heading="Related Documents",
        ),
    ]

    # Wagtail admin panel configurations
    promote_panels = Page.promote_panels
    settings_panels = Page.settings_panels

    # Search fields for Wagtail search functionality
    search_fields = Page.search_fields + [
        index.SearchField("hero_title"),
        index.SearchField("hero_subtitle"),
        index.SearchField("hero_description"),
    ]

    def get_ddq_questions_for_faq(self):
        """Extract DDQ questions for use in FAQ sections."""
        questions = []

        # Strategy & Governance questions
        strategy_questions = [
            {
                "question": "What is your organisation's overall approach to responsible investment?",
                "answer": "Ethical Capital exists to create industry-leading responsible investment strategies. Our mission is to align our clients' capital with companies that avoid preventable harm to living things and make meaningful contributions to a better future. We do this because we believe it leads to better client outcomes. The companies we exclude are generally lower-quality businesses, and our process benefits significantly from not having to engage with them in much depth.",
                "category": "investment_approach",
            },
            {
                "question": "Does your organisation have a responsible investment policy?",
                "answer": "We do not segregate responsible investing from regular investing. All of our policy documents can be found on the process page of our website.",
                "category": "investment_approach",
            },
            {
                "question": "What international standards, industry guidelines, reporting frameworks, or initiatives has your organisation committed to?",
                "answer": "We are signatories to the plant based treaty and work closely with the investor community whenever we can to advance our mission. As a matter of policy, we do not sign onto statements that require membership payments to the sponsoring body, only activist-led initiatives.",
                "category": "investment_approach",
            },
        ]

        # ESG Integration questions
        esg_questions = [
            {
                "question": "How is ESG materiality analysed for this strategy?",
                "answer": "We focus on the degree to which a firm's revenue is directly associated with positive real-world outcomes. We do not use third-party tools, standards, or data to complete this analysis.",
                "category": "esg_integration",
            },
            {
                "question": "How are financially material ESG factors incorporated into this strategy?",
                "answer": "In the last twelve months: We exited a position in Eiffage SA (OTC:EFGSY) after uncovering evidence that the firm has failed to properly supervise some of its projects in the middle east, resulting in significant human rights challenges. We continued adding to our position in Badger Meter (NYSE:BMI) as their value-added water meters continued to add value to many municipal water systems. We re-entered our position in ELF cosmetics (NYSE:ELF) after a significant selloff in their stock price coincided with a stronger impact case and continued sales momentum.",
                "category": "esg_integration",
            },
        ]

        # Stewardship questions
        stewardship_questions = [
            {
                "question": "Does your organisation have a stewardship policy?",
                "answer": "We do not have a stewardship policy at this time. Our firm has historically prioritised making its strategies accessible to all clients, regardless of how much money they have available to invest. This has required us to make certain trade-offs. One of the most material is that we are not currently able to vote our proxies.",
                "category": "stewardship",
            }
        ]

        # Reporting & Verification questions
        reporting_questions = [
            {
                "question": "What information is disclosed in regular client reporting on the responsible investment activities and performance of this strategy?",
                "answer": "We choose to emphasise firm-specific outcomes in our client reporting rather than ratings, carbon intensity, or other data. For instance, we devoted a section of our client letter to discussion of how one of our companies, a real estate investment trust, was able to preserve a historic mill as a center of commerce in a rural town.",
                "category": "reporting",
            },
            {
                "question": "How does your organisation audit the quality of its responsible investment processes and/or data?",
                "answer": "We routinely look for third-party groups that credibly assess companies for their alignment with various indicators of sound corporate practice, and will routinely spot check our exclusions to ensure that we are adequately incorporating the latest and deepest analysis of companies implicated in objectionable behavior.",
                "category": "reporting",
            },
        ]

        questions.extend(strategy_questions)
        questions.extend(esg_questions)
        questions.extend(stewardship_questions)
        questions.extend(reporting_questions)

        return questions

    def sync_to_support_articles(self):  # noqa: PLR0912
        """Create or update FAQArticle entries for DDQ questions."""
        import logging

        logger = logging.getLogger(__name__)

        try:
            questions = self.get_ddq_questions_for_faq()

            # Find FAQ index page
            try:
                faq_index = FAQIndexPage.objects.first()
            except Exception as e:
                logger.warning(f"Failed to get FAQ index page: {e}")
                return

            if not faq_index:
                logger.info("No FAQ index page found, skipping DDQ sync")
                return

            # Process questions - collect failures for logging
            failed_articles = []

            for q in questions:
                try:
                    article = FAQArticle.objects.filter(title=q["question"]).first()
                    if not article:
                        # Create new article
                        article = FAQArticle(
                            title=q["question"],
                            slug=q["question"].lower().replace(" ", "-")[:50],
                            content=f"<p>{q['answer']}</p>",
                            category=q["category"],
                            keywords="PRI DDQ responsible investment ESG",
                            priority=5,
                            locale=self.locale,
                        )
                        faq_index.add_child(instance=article)
                    else:
                        # Update existing article
                        article.content = f"<p>{q['answer']}</p>"
                        article.category = q["category"]
                        article.save()
                except Exception as e:  # noqa: PERF203
                    logger.warning(
                        f"Failed to sync FAQ article '{q.get('question', 'unknown')}': {e}"
                    )
                    failed_articles.append(q.get("question", "unknown"))

            if failed_articles:
                logger.info(f"Failed to sync {len(failed_articles)} FAQ articles")

        except Exception as e:
            logger.error(f"DDQ to FAQ sync failed completely: {e}")
            # Don't re-raise - this is a non-critical operation that shouldn't break page saving

    def save(self, *args, **kwargs):
        """Override save to auto-update updated_at and sync to support articles when saved."""
        from django.utils import timezone

        # Auto-update the updated_at field with current month/year
        current_date = timezone.now()
        self.updated_at = current_date.strftime("%B %Y")

        super().save(*args, **kwargs)
        self.sync_to_support_articles()

    class Meta:
        verbose_name = "PRI DDQ Page"


# ============================================================================
# SITE SETTINGS
# ============================================================================
# Global site configuration and settings models


@register_setting
class SiteConfiguration(ClusterableModel, BaseSiteSetting):
    """Global site configuration and branding settings."""

    # Company Information
    company_name = models.CharField(
        max_length=100,
        default="Ethical Capital",
        help_text="Company brand name displayed in navigation and footer",
    )
    company_tagline = models.CharField(
        max_length=200,
        default="Institutional-Grade Ethical Investing",
        help_text="Main tagline for SEO and social media",
    )
    company_description = models.TextField(
        default="SEC-registered investment advisor specializing in ethical portfolio management and concentrated sustainable investing strategies.",
        help_text="Company description for meta tags and schema markup",
    )

    # Contact Information
    primary_email = models.EmailField(
        default="hello@ethicic.com", help_text="Primary contact email address"
    )
    support_email = models.EmailField(
        default="hello@ethicic.com", help_text="Support and accessibility contact email"
    )
    cio_email = models.EmailField(
        default="sloane@ethicic.com", help_text="Chief Investment Officer email"
    )
    primary_phone = models.CharField(
        max_length=20, default="+1 347 625 9000", help_text="Primary phone number"
    )
    accessibility_phone = models.CharField(
        max_length=20,
        default="+1 (801) 123-4567",
        help_text="Accessibility support phone number",
    )

    # Address Information
    street_address = models.CharField(
        max_length=200, default="90 N 400 E", help_text="Street address"
    )
    city = models.CharField(max_length=100, default="Provo", help_text="City")
    state = models.CharField(max_length=50, default="UT", help_text="State or region")
    postal_code = models.CharField(
        max_length=20, default="84606", help_text="Postal/ZIP code"
    )
    country = models.CharField(
        max_length=100, default="United States", help_text="Country"
    )

    # Social Media
    twitter_handle = models.CharField(
        max_length=50, default="@ethicalcapital", help_text="Twitter handle (include @)"
    )
    linkedin_url = models.URLField(blank=True, help_text="LinkedIn company page URL")

    # SEO and Meta
    default_meta_description = models.TextField(
        default="Ethical Capital - Institutional-Grade Ethical Investing",
        help_text="Default meta description for pages without custom descriptions",
    )
    meta_keywords = models.CharField(
        max_length=300,
        default="investment intelligence, compliance, portfolio management, financial advisory",
        help_text="Default meta keywords",
    )

    # Legal and Compliance
    founding_year = models.CharField(
        max_length=4, default="2021", help_text="Company founding year"
    )
    copyright_text = models.CharField(
        max_length=200,
        default="Ethical Capital Investment Collaborative. All rights reserved.",
        help_text="Footer copyright text",
    )

    # Business Information
    business_hours = models.CharField(
        max_length=100,
        default="Monday - Friday, 9:00 AM - 5:00 PM MT",
        help_text="Business hours display text",
    )
    minimum_investment = models.CharField(
        max_length=20, default="$25,000", help_text="Minimum investment amount"
    )

    # Form Messages
    contact_success_message = models.TextField(
        default="Thank you for your message! We will get back to you within 24 hours.",
        help_text="Success message for contact form submissions",
    )
    contact_error_message = models.TextField(
        default="Please correct the errors below and try again.",
        help_text="Error message for contact form submissions",
    )
    newsletter_success_message = models.TextField(
        default="Thank you for subscribing to our newsletter!",
        help_text="Success message for newsletter subscriptions",
    )

    # Newsletter Widget Content
    newsletter_title = models.CharField(
        max_length=100,
        default="Stay Updated",
        help_text="Newsletter signup widget title",
    )
    newsletter_description = models.TextField(
        default="Get our latest insights on ethical investing delivered to your inbox.",
        help_text="Newsletter signup description",
    )
    newsletter_privacy_text = models.CharField(
        max_length=200,
        default="We respect your privacy. Unsubscribe at any time.",
        help_text="Newsletter privacy notice",
    )

    # Investment Form Content
    investment_goal_growth_title = models.CharField(
        max_length=50,
        default="Long-term Growth",
        help_text="Growth investment goal title",
    )
    investment_goal_growth_desc = models.TextField(
        default="Building wealth over time, comfortable with market volatility",
        help_text="Growth investment goal description",
    )
    investment_goal_income_title = models.CharField(
        max_length=50,
        default="Current Income",
        help_text="Income investment goal title",
    )
    investment_goal_income_desc = models.TextField(
        default="Regular income from investments, with some growth potential",
        help_text="Income investment goal description",
    )
    investment_goal_balanced_title = models.CharField(
        max_length=50,
        default="Balanced Approach",
        help_text="Balanced investment goal title",
    )
    investment_goal_balanced_desc = models.TextField(
        default="Mix of growth and income, moderate risk tolerance",
        help_text="Balanced investment goal description",
    )
    investment_goal_preservation_title = models.CharField(
        max_length=50,
        default="Capital Preservation",
        help_text="Preservation investment goal title",
    )
    investment_goal_preservation_desc = models.TextField(
        default="Protecting principal, minimal risk, steady returns",
        help_text="Preservation investment goal description",
    )

    # Content Management Settings
    panels = [
        MultiFieldPanel(
            [
                FieldPanel("company_name"),
                FieldPanel("company_tagline"),
                FieldPanel("company_description"),
            ],
            heading="Company Information",
        ),
        MultiFieldPanel(
            [
                FieldPanel("primary_email"),
                FieldPanel("support_email"),
                FieldPanel("cio_email"),
                FieldPanel("primary_phone"),
                FieldPanel("accessibility_phone"),
            ],
            heading="Contact Information",
        ),
        MultiFieldPanel(
            [
                FieldPanel("street_address"),
                FieldPanel("city"),
                FieldPanel("state"),
                FieldPanel("postal_code"),
                FieldPanel("country"),
                FieldPanel("business_hours"),
            ],
            heading="Address & Hours",
        ),
        MultiFieldPanel(
            [
                FieldPanel("twitter_handle"),
                FieldPanel("linkedin_url"),
            ],
            heading="Social Media",
        ),
        MultiFieldPanel(
            [
                FieldPanel("default_meta_description"),
                FieldPanel("meta_keywords"),
            ],
            heading="SEO & Meta Tags",
        ),
        MultiFieldPanel(
            [
                FieldPanel("founding_year"),
                FieldPanel("copyright_text"),
                FieldPanel("minimum_investment"),
            ],
            heading="Business Information",
        ),
        MultiFieldPanel(
            [
                FieldPanel("contact_success_message"),
                FieldPanel("contact_error_message"),
                FieldPanel("newsletter_success_message"),
            ],
            heading="Form Messages",
        ),
        MultiFieldPanel(
            [
                FieldPanel("newsletter_title"),
                FieldPanel("newsletter_description"),
                FieldPanel("newsletter_privacy_text"),
            ],
            heading="Newsletter Widget Content",
        ),
        MultiFieldPanel(
            [
                FieldPanel("investment_goal_growth_title"),
                FieldPanel("investment_goal_growth_desc"),
                FieldPanel("investment_goal_income_title"),
                FieldPanel("investment_goal_income_desc"),
                FieldPanel("investment_goal_balanced_title"),
                FieldPanel("investment_goal_balanced_desc"),
                FieldPanel("investment_goal_preservation_title"),
                FieldPanel("investment_goal_preservation_desc"),
            ],
            heading="Investment Goal Options",
        ),
        InlinePanel("nav_items", label="Navigation Menu Items"),
    ]

    class Meta:
        verbose_name = "Site Configuration"


class NavigationMenuItem(Orderable):
    """Individual navigation menu item."""

    parent = ParentalKey("SiteConfiguration", related_name="nav_items")

    label = models.CharField(max_length=50, help_text="Text displayed in navigation")
    url = models.CharField(
        max_length=200, help_text="URL or path (e.g., /about/, /process/)"
    )
    external = models.BooleanField(default=False, help_text="Open in new tab/window")
    show_in_nav = models.BooleanField(
        default=True, help_text="Display this item in the main navigation"
    )
    show_in_footer = models.BooleanField(
        default=True, help_text="Display this item in the footer"
    )

    panels = [
        FieldPanel("label"),
        FieldPanel("url"),
        FieldPanel("external"),
        FieldPanel("show_in_nav"),
        FieldPanel("show_in_footer"),
    ]

    def __str__(self):
        return self.label

    class Meta:
        verbose_name = "Navigation Menu Item"


# Import new page models
