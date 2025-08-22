"""
Wagtail hooks for the public_site app.
Clean, simplified admin interface without AI features.
"""

from typing import ClassVar

from django.utils.html import format_html
from wagtail import hooks
from wagtail.admin.panels import TabbedInterface, ObjectList
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet

from .models import (
    BlogPost,
    MediaItem,
    SupportTicket,
)


# Register SupportTicket as a snippet for easier management
@register_snippet
class SupportTicketSnippetViewSet(SnippetViewSet):
    model = SupportTicket
    list_display: ClassVar[list] = [
        "name",
        "email",
        "subject",
        "status",
        "created_at",
    ]
    list_filter: ClassVar[list] = ["status", "ticket_type", "created_at"]
    search_fields: ClassVar[list] = [
        "name",
        "email",
        "subject",
        "message",
    ]
    ordering: ClassVar[list] = ["-created_at"]


# Add clean admin CSS to improve page editing experience
@hooks.register("insert_global_admin_css")
def global_admin_css():
    return """<style>
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

        .stream-field .sequence-type-label[data-streamfield-block-type="key_statistic"] {
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
            font-weight: normal;
            color: #666;
        }

        /* Help text styling */
        .c-panel__content .help {
            color: #666;
            font-size: 0.85em;
            font-style: italic;
            margin-top: 0.5rem;
        }
    </style>"""


@hooks.register("insert_global_admin_js")
def global_admin_js():
    """Add JavaScript for improved admin experience and StreamField support."""
    return """<script>
        document.addEventListener('DOMContentLoaded', function() {
            // Ensure collapsed panels can be expanded
            const collapsedPanels = document.querySelectorAll('.collapsed');
            collapsedPanels.forEach(function(panel) {
                const heading = panel.querySelector('.c-panel__heading, h2');
                if (heading) {
                    heading.style.cursor = 'pointer';
                    heading.addEventListener('click', function() {
                        panel.classList.toggle('collapsed');
                    });
                }
            });
            
            // Fix for missing content-count field in StreamField
            function ensureStreamFieldCount() {
                const form = document.querySelector('form.page-edit-form, form[action*="/pages/"]');
                if (!form) return;
                
                // Check if we have a content StreamField
                const contentField = form.querySelector('[data-contentpath="content"], [name^="content-"]');
                if (contentField && !form.querySelector('input[name="content-count"]')) {
                    const countInput = document.createElement('input');
                    countInput.type = 'hidden';
                    countInput.name = 'content-count';
                    countInput.value = '0';
                    form.appendChild(countInput);
                }
            }
            
            // Run immediately and on form changes
            ensureStreamFieldCount();
            
            // Also ensure it's there before form submission
            const forms = document.querySelectorAll('form.page-edit-form, form[action*="/pages/"]');
            forms.forEach(form => {
                form.addEventListener('submit', function(e) {
                    ensureStreamFieldCount();
                });
            });
        });
    </script>"""


@hooks.register("construct_homepage_panels")
def add_public_site_instructions(request, panels):
    """Add helpful instructions panel to the homepage admin."""
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

        def render(self):
            try:
                return format_html(
                    """
                    <div class="help-block">
                        <h3>📋 Content Management Tips</h3>
                        <ul>
                            <li><strong>Blog Posts:</strong> Use StreamField blocks for rich content layout</li>
                            <li><strong>Key Statistics:</strong> Use the Key Statistic block to highlight important data</li>
                            <li><strong>Images:</strong> Always add alt text for accessibility</li>
                            <li><strong>SEO:</strong> Fill in meta description and search keywords</li>
                        </ul>
                        <p>
                            <a href="/admin/pages/" class="button">📄 Manage Pages</a>
                            <a href="/admin/snippets/public_site/supportticket/" class="button">🎫 Support Tickets</a>
                        </p>
                    </div>
                    """
                )
            except Exception:
                return "<div class='help-block'>Content management tips temporarily unavailable.</div>"

    panels.append(InstructionsPanel())


# Register MediaItem as a snippet for easier management
@register_snippet
class MediaItemSnippetViewSet(SnippetViewSet):
    model = MediaItem
    list_display: ClassVar[list] = [
        "title",
        "publication",
        "publication_date",
        "featured",
        "get_page_title",
    ]
    list_filter: ClassVar[list] = ["featured", "publication", "publication_date"]
    search_fields: ClassVar[list] = ["title", "description", "publication"]
    ordering: ClassVar[list] = ["-featured", "-publication_date"]
    menu_label = "Media Items"
    menu_icon = "doc-full"
    menu_order = 200

    def get_page_title(self, obj):
        """Display the parent page title."""
        if obj is None:
            return "No page"
        return obj.page.title if obj.page else "No page"

    # Add the method to the model for display
    MediaItem.get_page_title = get_page_title
    MediaItem.get_page_title.short_description = "Page"
