"""
Wagtail hooks for the public_site app.
This ensures pages are properly editable in the Wagtail admin.
Uses Wagtail's modern admin viewsets instead of deprecated wagtail-modeladmin.
"""
from typing import ClassVar

from django.urls import reverse
from django.utils.html import format_html
from wagtail import hooks
from wagtail.admin.viewsets.pages import PageListingViewSet
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet

from .models import (
    AboutPage,
    BlogPost,
    FAQArticle,
    HomePage,
    PRIDDQPage,
    StrategyPage,
    SupportTicket,
)


# Register SupportTicket as a snippet for easier management
@register_snippet
class SupportTicketSnippetViewSet(SnippetViewSet):
    model = SupportTicket
    list_display: ClassVar[list] = ['first_name', 'last_name', 'subject', 'status', 'created_at']
    list_filter: ClassVar[list] = ['status', 'category', 'created_at']
    search_fields: ClassVar[list] = ['first_name', 'last_name', 'email', 'subject', 'message']
    ordering: ClassVar[list] = ['-created_at']


# Add AI-enhanced admin CSS to improve page editing experience
@hooks.register('insert_global_admin_css')
def global_admin_css():
    return '''<style>
        /* Improve Wagtail admin styling for public site pages */
        .page-editor .object h2.c-panel__heading {
            background-color: #f3f3f3;
            padding: 1rem;
            margin-bottom: 0;
        }

        .page-editor .object .field {
            margin-bottom: 1.5rem;
        }

        .page-editor .help {
            color: #666;
            font-size: 0.9em;
            margin-top: 0.5rem;
        }

        /* Make rich text fields taller */
        .page-editor .Draftail-Editor__wrapper {
            min-height: 200px;
        }

        /* Improve panel visibility */
        .page-editor .c-panel {
            border: 1px solid #e0e0e0;
            margin-bottom: 1rem;
        }

        /* StreamField specific styling */
        .stream-field .sequence-controls {
            background: #f8f9fa;
            padding: 10px;
            border-radius: 4px;
            margin-bottom: 10px;
        }

        .stream-field .sequence-member {
            border: 1px solid #e9ecef;
            border-radius: 6px;
            margin-bottom: 15px;
            background: #fff;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }

        .stream-field .sequence-member-inner {
            padding: 15px;
        }

        .stream-field .sequence-type-label {
            background: #007cba;
            color: white;
            padding: 4px 8px;
            border-radius: 3px;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
            margin-bottom: 10px;
            display: inline-block;
        }

        /* Block-specific styling */
        .stream-field .sequence-type-label[data-streamfield-block-type="image"] {
            background: #28a745;
        }

        .stream-field .sequence-type-label[data-streamfield-block-type="quote"] {
            background: #6f42c1;
        }

        .stream-field .sequence-type-label[data-streamfield-block-type="callout"] {
            background: #fd7e14;
        }

        .stream-field .sequence-type-label[data-streamfield-block-type="code"] {
            background: #20c997;
        }

        .stream-field .sequence-type-label[data-streamfield-block-type="stats"] {
            background: #dc3545;
        }

        /* Legacy field styling */
        .object[data-field="body"] {
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 4px;
            padding: 10px;
            margin-bottom: 20px;
        }

        .object[data-field="body"] .object-label {
            color: #856404;
        }

        .object[data-field="body"] .object-label::after {
            content: " (Legacy - Consider migrating to StreamField)";
            font-size: 0.8em;
            font-weight: normal;
            color: #856404;
        }

        /* Collapsed panel styling */
        .collapsed .c-panel__content {
            display: none;
        }

        .collapsed .c-panel__heading::after {
            content: " (Click to expand)";
            font-size: 0.8em;
            color: #666;
        }

        /* Add block button styling */
        .stream-field .stream-menu .stream-menu-item {
            display: flex;
            align-items: center;
            padding: 8px 12px;
        }

        .stream-field .stream-menu .stream-menu-item::before {
            margin-right: 8px;
            font-size: 16px;
        }

        /* Help text improvements */
        .c-panel__content .help {
            background: #f8f9fa;
            border-left: 3px solid #007cba;
            padding: 10px;
            margin: 10px 0;
            border-radius: 0 4px 4px 0;
        }

        /* AI Panel Styling */
        .ai-panel {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }

        .ai-panel h3 {
            color: white;
            margin-top: 0;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .ai-panel .ai-assistant-tabs {
            display: flex;
            gap: 8px;
            margin-bottom: 16px;
        }

        .ai-panel .tab-button {
            background: rgba(255,255,255,0.2);
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
            transition: background 0.2s;
        }

        .ai-panel .tab-button.active,
        .ai-panel .tab-button:hover {
            background: rgba(255,255,255,0.3);
        }

        .ai-stat-card {
            background: rgba(255,255,255,0.9);
            color: #333;
            border-radius: 6px;
            padding: 12px;
            margin: 8px 0;
            border-left: 4px solid #4f46e5;
        }

        .ai-stat-confidence {
            font-weight: bold;
            font-size: 0.9em;
        }

        .ai-stat-value {
            font-size: 1.5em;
            font-weight: bold;
            color: #4f46e5;
        }

        .ai-stat-label {
            font-weight: 600;
            margin: 4px 0;
        }

        .ai-stat-context {
            font-size: 0.9em;
            color: #666;
            font-style: italic;
        }

        .add-stat-btn {
            background: #10b981;
            color: white;
            border: none;
            padding: 6px 12px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 0.85em;
            margin-top: 8px;
        }

        .add-stat-btn:hover {
            background: #059669;
        }
    </style>'''


# Custom page permissions hook
@hooks.register('register_permissions')
def register_public_site_permissions():
    """Register custom permissions for public site pages."""
    return [
        'public_site.add_homepage',
        'public_site.change_homepage',
        'public_site.delete_homepage',
        'public_site.add_aboutpage',
        'public_site.change_aboutpage',
        'public_site.delete_aboutpage',
        'public_site.add_contactpage',
        'public_site.change_contactpage',
        'public_site.delete_contactpage',
        'public_site.add_blogpost',
        'public_site.change_blogpost',
        'public_site.delete_blogpost',
        'public_site.add_researchpage',
        'public_site.change_researchpage',
        'public_site.delete_researchpage',
        'public_site.add_strategypage',
        'public_site.change_strategypage',
        'public_site.delete_strategypage',
    ]


# Add page preview templates
@hooks.register('register_page_preview_template')
def register_preview_templates():
    """Register preview templates for better editing experience."""
    return {
        'public_site.HomePage': 'public_site/preview/homepage_preview.html',
        'public_site.AboutPage': 'public_site/preview/aboutpage_preview.html',
        'public_site.ContactPage': 'public_site/preview/contactpage_preview.html',
        'public_site.BlogPost': 'public_site/preview/blogpost_preview.html',
        'public_site.ResearchPage': 'public_site/preview/researchpage_preview.html',
    }


# Add AI assistant JavaScript to admin
@hooks.register('insert_editor_js')
def editor_js():
    return '''<script>
        document.addEventListener('DOMContentLoaded', function() {
            // Add helpful tooltips for public site pages
            const pageTitle = document.querySelector('h1.icon');
            if (pageTitle && pageTitle.textContent.includes('Edit')) {
                const helpText = document.createElement('div');
                helpText.className = 'help-block help-info';
                helpText.innerHTML = '<p>💡 Tip: Use the preview button to see how your changes will look on the live site.</p>';

                const header = document.querySelector('.content-wrapper');
                if (header) {
                    header.insertBefore(helpText, header.firstChild.nextSibling);
                }
            }

            // StreamField enhancements
            enhanceStreamFieldInterface();

            // Add content migration helper
            addContentMigrationHelper();
        });

        function enhanceStreamFieldInterface() {
            // Add tooltips to StreamField block buttons
            const blockButtons = document.querySelectorAll('.stream-menu-item');
            blockButtons.forEach(function(button) {
                const blockType = button.textContent.trim().toLowerCase();
                const tooltips = {
                    'image': 'Add images with captions, alt text, and alignment options',
                    'quote': 'Add styled quotes with attribution and citation',
                    'callout': 'Highlight important information with colored boxes',
                    'code': 'Add syntax-highlighted code snippets',
                    'stats': 'Display key metrics and statistics with animations',
                    'button': 'Add call-to-action buttons with custom styling',
                    'table': 'Insert data tables with headers and formatting',
                    'document': 'Provide document downloads with descriptions',
                    'video': 'Embed videos from YouTube, Vimeo, or other platforms',
                    'separator': 'Add visual dividers between content sections'
                };

                if (tooltips[blockType]) {
                    button.title = tooltips[blockType];
                }
            });

            // Add visual indicators for different block types
            const streamBlocks = document.querySelectorAll('.sequence-member');
            streamBlocks.forEach(function(block) {
                const blockTypeElement = block.querySelector('.sequence-type-label');
                if (blockTypeElement) {
                    const blockType = blockTypeElement.textContent.toLowerCase();
                    blockTypeElement.setAttribute('data-streamfield-block-type', blockType);
                }
            });
        }

        function addContentMigrationHelper() {
            // Check for legacy content that could be migrated
            const legacyField = document.querySelector('[data-field="body"]');
            const streamField = document.querySelector('[data-field="content"]');

            if (legacyField && streamField) {
                const legacyTextarea = legacyField.querySelector('textarea, .DraftEditor-root');
                const streamFieldEmpty = !streamField.querySelector('.sequence-member');

                if (legacyTextarea && streamFieldEmpty) {
                    const hasContent = legacyTextarea.value ||
                                     (legacyTextarea.textContent && legacyTextarea.textContent.trim());

                    if (hasContent) {
                        // Create migration helper
                        const migrationHelper = document.createElement('div');
                        migrationHelper.className = 'help-block';
                        migrationHelper.style.cssText = `
                            background: #d1ecf1;
                            border: 1px solid #bee5eb;
                            color: #0c5460;
                            padding: 12px;
                            margin: 10px 0;
                            border-radius: 4px;
                            font-size: 14px;
                        `;
                        migrationHelper.innerHTML = `
                            <strong>💡 Content Migration Tip:</strong><br>
                            This post has content in the legacy rich text field. Consider copying this content to the new StreamField above for better formatting options including:
                            <ul style="margin: 8px 0 0 20px;">
                                <li>Image blocks with captions and alignment</li>
                                <li>Quote blocks with attribution</li>
                                <li>Callout boxes for important information</li>
                                <li>Code blocks with syntax highlighting</li>
                                <li>Tables and statistics displays</li>
                            </ul>
                        `;

                        // Insert before the legacy field
                        const legacyPanel = legacyField.closest('.c-panel');
                        if (legacyPanel) {
                            legacyPanel.insertBefore(migrationHelper, legacyPanel.firstChild);
                        }
                    }
                }
            }
        }

        // Auto-save functionality for StreamField
        function setupAutoSave() {
            let saveTimeout;
            const streamFieldInputs = document.querySelectorAll('.stream-field input, .stream-field textarea');

            streamFieldInputs.forEach(function(input) {
                input.addEventListener('input', function() {
                    clearTimeout(saveTimeout);
                    saveTimeout = setTimeout(function() {
                        // Trigger Wagtail's auto-save if available
                        if (window.wagtail && window.wagtail.ui && window.wagtail.ui.sidebar) {
                            const saveButton = document.querySelector('button[type="submit"][name="action-draft"]');
                            if (saveButton) {
                                console.log('Auto-saving StreamField changes...');
                                // Could implement auto-save here if needed
                            }
                        }
                    }, 2000); // Auto-save after 2 seconds of inactivity
                });
            });
        }

        // Initialize auto-save on page load
        document.addEventListener('DOMContentLoaded', setupAutoSave);

        // Initialize AI Assistant if available
        if (typeof window.AIContentAssistant !== 'undefined') {
            window.aiAssistant = new window.AIContentAssistant();
            window.aiAssistant.init();
        }
    </script>'''


# Modern Wagtail Page Listing ViewSets (replaces deprecated ModelAdmin)
class HomePageListingViewSet(PageListingViewSet):
    model = HomePage
    menu_label = 'Home Pages'
    icon = 'home'
    menu_order = 100
    add_to_admin_menu = True
    list_display: ClassVar[list] = ['title', 'hero_title', 'live', 'latest_revision_created_at', 'has_features_content', 'has_cta_content']
    search_fields: ClassVar[list] = ['title', 'hero_title', 'hero_subtitle']
    list_filter: ClassVar[list] = ['live', 'latest_revision_created_at']

    def has_features_content(self, obj):
        """Show whether the page has features content."""
        return bool(obj.features_content and obj.features_content.strip())
    has_features_content.boolean = True
    has_features_content.short_description = 'Has Features'

    def has_cta_content(self, obj):
        """Show whether the page has CTA content."""
        return bool(obj.cta_description and obj.cta_description.strip())
    has_cta_content.boolean = True
    has_cta_content.short_description = 'Has CTA'

    def get_queryset(self, request):
        return super().get_queryset(request).filter(depth__gte=2)


class AboutPageListingViewSet(PageListingViewSet):
    model = AboutPage
    menu_label = 'About Pages'
    icon = 'info-circle'
    menu_order = 110
    add_to_admin_menu = True
    list_display: ClassVar[list] = ['title', 'live', 'latest_revision_created_at']
    search_fields: ClassVar[list] = ['title', 'intro_text']
    list_filter: ClassVar[list] = ['live', 'latest_revision_created_at']


class BlogPostListingViewSet(PageListingViewSet):
    model = BlogPost
    menu_label = 'Blog Posts'
    icon = 'edit'
    menu_order = 120
    add_to_admin_menu = True
    list_display: ClassVar[list] = ['title', 'author', 'publish_date', 'featured', 'live', 'has_streamfield_content']
    list_filter: ClassVar[list] = ['live', 'featured', 'publish_date', 'author']
    search_fields: ClassVar[list] = ['title', 'excerpt']

    def has_streamfield_content(self, obj):
        """Show whether the post uses the new StreamField."""
        return bool(obj.content)
    has_streamfield_content.boolean = True
    has_streamfield_content.short_description = 'Uses StreamField'


class StrategyPageListingViewSet(PageListingViewSet):
    model = StrategyPage
    menu_label = 'Strategy Pages'
    icon = 'tasks'
    menu_order = 130
    add_to_admin_menu = True
    list_display: ClassVar[list] = ['title', 'risk_level', 'live', 'latest_revision_created_at']
    search_fields: ClassVar[list] = ['title', 'strategy_description']
    list_filter: ClassVar[list] = ['live', 'latest_revision_created_at']


class FAQArticleListingViewSet(PageListingViewSet):
    model = FAQArticle
    menu_label = 'FAQ Articles'
    icon = 'help'
    menu_order = 140
    add_to_admin_menu = True
    list_display: ClassVar[list] = ['title', 'category', 'priority', 'featured', 'live']
    list_filter: ClassVar[list] = ['category', 'featured', 'live']
    search_fields: ClassVar[list] = ['title', 'summary']


class PRIDDQPageListingViewSet(PageListingViewSet):
    model = PRIDDQPage
    menu_label = 'PRI DDQ Pages'
    icon = 'doc-full'
    menu_order = 150
    add_to_admin_menu = True
    list_display: ClassVar[list] = ['title', 'last_updated', 'live', 'latest_revision_created_at']
    search_fields: ClassVar[list] = ['title', 'hero_title', 'hero_subtitle', 'executive_summary']
    list_filter: ClassVar[list] = ['live', 'latest_revision_created_at']


# Register the ViewSets with Wagtail using hooks
@hooks.register('register_admin_viewset')
def register_homepage_viewset():
    return HomePageListingViewSet('homepage_listing')

@hooks.register('register_admin_viewset')
def register_aboutpage_viewset():
    return AboutPageListingViewSet('aboutpage_listing')

@hooks.register('register_admin_viewset')
def register_blogpost_viewset():
    return BlogPostListingViewSet('blogpost_listing')

@hooks.register('register_admin_viewset')
def register_strategypage_viewset():
    return StrategyPageListingViewSet('strategypage_listing')

@hooks.register('register_admin_viewset')
def register_faqarticle_viewset():
    return FAQArticleListingViewSet('faqarticle_listing')

@hooks.register('register_admin_viewset')
def register_priddqpage_viewset():
    return PRIDDQPageListingViewSet('priddqpage_listing')


# Custom admin menu items for quick access
@hooks.register('register_admin_menu_item')
def register_public_pages_menu_item():
    """Add quick access menu item for public pages."""
    from wagtail.admin.menu import MenuItem

    return MenuItem(
        'Edit Homepage',
        reverse('wagtailadmin_pages:edit', args=[3]),  # ID 3 is the HomePage
        icon_name='home',
        order=201
    )


# Add additional menu item for page explorer
@hooks.register('register_admin_menu_item')
def register_page_explorer_menu_item():
    """Add page explorer menu item."""
    from wagtail.admin.menu import MenuItem

    return MenuItem(
        'Page Explorer',
        reverse('wagtailadmin_explore_root'),
        icon_name='folder-open',
        order=202
    )


# Hook to ensure pages show in explorer
@hooks.register('construct_explorer_page_queryset')
def show_public_pages_in_explorer(parent_page, pages, request):
    """Ensure public site pages are visible in explorer."""
    # Return the queryset as-is to show all pages
    return pages


# Add page listing buttons
@hooks.register('register_page_listing_buttons')
def page_listing_buttons(page, user, next_url=None):
    """Add custom buttons to page listings."""
    from wagtail.admin import widgets as wagtailadmin_widgets

    # Add "View Live" button for all public pages
    if hasattr(page.specific, 'url') and page.live:
        yield wagtailadmin_widgets.ListingButton(
            'View Live',
            page.specific.url,
            priority=10
        )


# Add StreamField-specific hooks
@hooks.register('after_create_page')
def after_create_blog_post(request, page):
    """Handle actions after creating a blog post."""
    if isinstance(page, BlogPost):
        from django.contrib import messages

        # Guide users to use StreamField for new posts
        if not page.content and not page.body:
            messages.success(
                request,
                "✨ Blog post created! Use the 'Main Content' StreamField to add rich content blocks like images, quotes, and code snippets."
            )
        elif page.body and not page.content:
            messages.info(
                request,
                "💡 Consider using the new StreamField for better content formatting options."
            )


@hooks.register('after_edit_page')
def after_edit_blog_post(request, page):
    """Handle actions after editing a blog post."""
    if isinstance(page, BlogPost):
        from django.contrib import messages

        # Check if using legacy content only
        if page.body and not page.content:
            messages.warning(
                request,
                "📝 This post uses the legacy rich text field. The new StreamField offers better formatting options including images, quotes, callouts, and code blocks."
            )
        elif page.content:
            messages.success(
                request,
                "✅ Great! This post uses the new StreamField with rich content blocks."
            )


@hooks.register('after_edit_page')
def after_edit_homepage(request, page):
    """Handle actions after editing the homepage."""
    if isinstance(page, HomePage):
        from django.contrib import messages

        # Check if all key sections are populated
        sections_populated = []
        if page.hero_description and page.hero_description.strip():
            sections_populated.append("Hero")
        if page.features_content and page.features_content.strip():
            sections_populated.append("Features")
        if page.cta_description and page.cta_description.strip():
            sections_populated.append("CTA")

        if len(sections_populated) == 3:
            messages.success(
                request,
                "🏠 ✅ Homepage fully configured! All sections (Hero, Features, CTA) have content."
            )
        elif len(sections_populated) >= 1:
            missing_sections = []
            if not (page.hero_description and page.hero_description.strip()):
                missing_sections.append("Hero Description")
            if not (page.features_content and page.features_content.strip()):
                missing_sections.append("Features Content")
            if not (page.cta_description and page.cta_description.strip()):
                missing_sections.append("CTA Description")

            if missing_sections:
                messages.info(
                    request,
                    f"🏠 📝 Homepage partially configured. Consider adding content to: {', '.join(missing_sections)}"
                )
        else:
            messages.warning(
                request,
                "🏠 ⚠️ Homepage needs content! Add descriptions to Hero, Features, and CTA sections for a complete homepage."
            )


# Hook to add instructions to the Wagtail admin dashboard
@hooks.register('construct_homepage_panels')
def add_public_site_instructions(request, panels):
    """Add instructions for editing public site pages."""
    from wagtail.admin.panels import Panel

    class InstructionsPanel(Panel):
        def __init__(self):
            super().__init__()
            self.order = 100  # Set display order for the panel

        @property
        def media(self):
            """Return empty Media object since this panel doesn't need additional CSS/JS."""
            from django.forms import Media
            return Media()

        def render_html(self, parent_context=None):
            return format_html('''
                <div class="help-block help-info" style="padding: 20px; margin: 20px 0;">
                    <h2>Editing Public Site Pages</h2>
                    <p>To edit pages on the public-facing website:</p>
                    <ol>
                        <li>Click <strong>"Pages"</strong> in the left sidebar</li>
                        <li>Navigate to <strong>"Ethical Capital | Investment Advisory"</strong></li>
                        <li>Click on any page to edit its content</li>
                        <li>Use the <strong>"Save draft"</strong> button to save without publishing</li>
                        <li>Use the <strong>"Publish"</strong> button to make changes live</li>
                    </ol>
                    <p>Quick links:</p>
                    <ul>
                        <li><a href="/cms-admin/pages/3/edit/">Edit Homepage</a></li>
                        <li><a href="/cms-admin/pages/3/">Browse All Pages</a></li>
                        <li><a href="/cms-admin/pages/add/public_site/homepage/3/">Add New Page</a></li>
                    </ul>
                </div>
            ''')

        def render_as_object(self):
            return self.render_html()

    panels.append(InstructionsPanel())


# Include AI assistant JavaScript and CSS files
@hooks.register('insert_global_admin_js')
def global_admin_js():
    """Include AI assistant JavaScript for blog editing."""
    return '''
    <script src="/static/js/admin/ai-assistant.js"></script>
    '''


@hooks.register('insert_global_admin_css')
def ai_admin_css():
    """Include AI assistant CSS for admin interface."""
    return '''<link rel="stylesheet" type="text/css" href="/static/css/admin/ai-assistant.css">'''


# Register AI panels for BlogPost model
@hooks.register('register_page_action_menu_item')
def register_ai_assistant_menu_item():
    """Add AI Assistant menu item to BlogPost pages."""
    from wagtail.admin.action_menu import ActionMenuItem

    class AIAssistantMenuItem(ActionMenuItem):
        label = "AI Assistant"
        name = "ai-assistant"
        icon_name = "lightning-bolt"
        classname = "ai-assistant-button"

        def is_shown(self, context):
            # Only show for BlogPost pages
            page = context.get('page')
            return page and hasattr(page, 'content')  # Has StreamField

    return AIAssistantMenuItem(order=100)
