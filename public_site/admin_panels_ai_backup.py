"""
AI-Powered Admin Panels for Enhanced Blog Content Creation
Integrates Maverick AI agents with Wagtail admin interface
"""

# import asyncio  # No longer needed - using synchronous API calls
from typing import ClassVar

from django import forms
from django.forms.widgets import TextInput as AdminTextInput
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from wagtail.admin.panels import FieldPanel, ObjectList, TabbedInterface

# AI services available via API calls to main garden web container
from .blocks import call_ai_analysis_api


class AIAssistantWidget(AdminTextInput):
    """Widget that provides AI assistance for content creation."""

    template_name = "public_site/admin/ai_assistant_widget.html"

    def __init__(self, attrs=None, analysis_type="statistics"):
        super().__init__(attrs)
        self.analysis_type = analysis_type

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context.update(
            {
                "analysis_type": self.analysis_type,
                "ai_endpoint": reverse("public_site:ai_analysis_api"),
                "widget_id": attrs.get("id", name),
            }
        )
        return context

    class Media:
        css: ClassVar[dict] = {"all": ("css/admin/ai-assistant.css",)}
        js = ("js/admin/ai-assistant.js",)


class AIStatisticsPanel(FieldPanel):
    """Panel that shows AI-extracted statistics with enhanced editing capabilities."""

    template = "public_site/admin/ai_statistics_panel.html"

    def __init__(self, field_name, **kwargs):
        super().__init__(field_name, **kwargs)
        # AI service accessed via API calls to main container

    def clone_kwargs(self):
        return super().clone_kwargs()

    def get_form_options(self):
        opts = super().get_form_options()
        opts.update({"widget": AIAssistantWidget(analysis_type="statistics")})
        return opts

    def render_html(self, instance, request):
        """Render the panel with AI analysis data."""
        if not instance or not instance.pk:
            return self._render_no_content_message()

        # Get AI analysis for this blog post via API
        try:
            analysis = self._get_ai_analysis(instance)
            return self._render_with_analysis(instance, analysis, request)
        except Exception as e:
            return self._render_error_message(str(e))

    def _get_ai_analysis(self, instance):
        """Get AI analysis for the blog post via API call."""
        # Extract content from the instance
        content_text = ""
        if hasattr(instance, "body") and instance.body:
            content_text += str(instance.body)
        if hasattr(instance, "content") and instance.content:
            for block in instance.content:
                if hasattr(block, "value") and isinstance(block.value, str):
                    content_text += block.value

        if not content_text.strip():
            return {
                "meaningful_statistics": [],
                "key_insights": [],
                "recommended_charts": [],
            }

        # Make API call to main garden web container
        content_data = {"title": getattr(instance, "title", ""), "body": content_text}

        analysis = call_ai_analysis_api(content_data, "comprehensive")
        if analysis:
            return analysis
        # Return fallback data if API call fails
        return {
            "meaningful_statistics": [],
            "key_insights": [],
            "recommended_charts": [],
        }

    def _render_no_content_message(self):
        """Render message when no content is available for analysis."""
        return format_html(
            '<div class="ai-panel-placeholder">'
            "<h3>🤖 AI Statistics Analysis</h3>"
            "<p>Save the page first, then AI will analyze your content for meaningful statistics.</p>"
            "</div>"
        )

    def _render_with_analysis(self, instance, analysis, request):
        """Render the panel with AI analysis results."""
        stats = analysis.get("meaningful_statistics", [])
        insights = analysis.get("key_insights", [])
        charts = analysis.get("recommended_charts", [])

        html_parts = [
            '<div class="ai-statistics-panel">',
            "<h3>🤖 AI-Identified Statistics</h3>",
        ]

        if stats:
            html_parts.extend(
                [
                    '<div class="ai-stats-grid">',
                    self._render_statistics_grid(stats),
                    "</div>",
                ]
            )
        else:
            html_parts.append(
                '<p class="ai-no-stats">No meaningful statistics detected in content.</p>'
            )

        if insights:
            html_parts.extend(
                [
                    "<h4>💡 Key Insights</h4>",
                    '<ul class="ai-insights">',
                    "".join(f"<li>{insight}</li>" for insight in insights),
                    "</ul>",
                ]
            )

        if charts:
            html_parts.extend(
                [
                    "<h4>📊 Recommended Charts</h4>",
                    '<div class="ai-chart-recommendations">',
                    self._render_chart_recommendations(charts),
                    "</div>",
                ]
            )

        html_parts.extend(
            [
                '<div class="ai-panel-actions">',
                f'<button type="button" class="button" onclick="refreshAIAnalysis({instance.pk})">',
                "🔄 Refresh Analysis</button>",
                '<button type="button" class="button bicolor" onclick="applyAIStatistics()">',
                "✨ Apply to Content</button>",
                "</div>",
                "</div>",
            ]
        )

        return mark_safe("".join(html_parts))

    def _render_statistics_grid(self, stats):
        """Render grid of AI-identified statistics."""
        grid_items = []

        for i, stat in enumerate(stats[:8]):  # Limit to 8 most relevant
            confidence = stat.get("confidence", 0.5)
            significance = stat.get("significance", "medium")

            confidence_color = (
                "green" if confidence > 0.8 else "orange" if confidence > 0.6 else "red"
            )
            significance_icon = (
                "🔥"
                if significance == "high"
                else "⚡"
                if significance == "medium"
                else "💡"
            )

            grid_items.append(
                f"""
                <div class="ai-stat-card" data-stat-index="{i}">
                    <div class="ai-stat-header">
                        <span class="ai-stat-significance">{significance_icon}</span>
                        <span class="ai-stat-confidence" style="color: {confidence_color}">
                            {confidence:.0%}
                        </span>
                    </div>
                    <div class="ai-stat-value">{stat.get("value", "")}</div>
                    <div class="ai-stat-label">{stat.get("label", "")}</div>
                    <div class="ai-stat-context">{stat.get("context", "")[:100]}...</div>
                    <div class="ai-stat-actions">
                        <button type="button" class="button button-small"
                                onclick="addStatisticToContent({i})">
                            Add to Content
                        </button>
                        <button type="button" class="button button-small"
                                onclick="createChartFromStat({i})">
                            Create Chart
                        </button>
                    </div>
                </div>
            """
            )

        return "".join(grid_items)

    def _render_chart_recommendations(self, charts):
        """Render recommended chart configurations."""
        chart_items = []

        for i, chart in enumerate(charts[:4]):  # Limit to 4 recommendations
            chart_items.append(
                f"""
                <div class="ai-chart-rec" data-chart-index="{i}">
                    <div class="ai-chart-header">
                        <strong>{chart.get("title", "Untitled Chart")}</strong>
                        <span class="ai-chart-type">{chart.get("type", "unknown")}</span>
                    </div>
                    <div class="ai-chart-preview">
                        <div class="chart-placeholder">📊 {chart.get("type", "Chart")} Preview</div>
                    </div>
                    <button type="button" class="button button-small"
                            onclick="addChartToContent({i})">
                        Add Chart Block
                    </button>
                </div>
            """
            )

        return "".join(chart_items)

    def _render_error_message(self, error):
        """Render error message when analysis fails."""
        return format_html(
            '<div class="ai-panel-error">'
            "<h3>⚠️ AI Analysis Error</h3>"
            "<p>Failed to analyze content: {}</p>"
            '<button type="button" class="button" onclick="retryAIAnalysis()">Retry</button>'
            "</div>",
            error,
        )


class AIContentAssistantPanel(FieldPanel):
    """Panel that provides AI-powered content assistance and suggestions."""

    template = "public_site/admin/ai_content_assistant_panel.html"

    def __init__(self, field_name, **kwargs):
        super().__init__(field_name, **kwargs)
        self.suggestions_cache = {}

    def render_html(self, instance, request):
        """Render content assistant with real-time suggestions."""
        if not instance or not instance.pk:
            return self._render_getting_started()

        return self._render_assistant_interface(instance, request)

    def _render_getting_started(self):
        """Render getting started interface for new posts."""
        return format_html(
            '<div class="ai-content-assistant">'
            "<h3>✨ AI Content Assistant</h3>"
            '<div class="ai-assistant-getting-started">'
            "<h4>Getting Started</h4>"
            "<ul>"
            "<li>📝 Write your content in the rich text editor</li>"
            "<li>🤖 AI will automatically identify meaningful statistics</li>"
            "<li>📊 Get suggestions for charts and visualizations</li>"
            "<li>💡 Receive insights on content structure and flow</li>"
            "</ul>"
            '<div class="ai-assistant-tips">'
            "<h5>Tips for Better AI Analysis:</h5>"
            "<ul>"
            '<li>Include specific numbers with context (e.g., "12.4% annual return")</li>'
            "<li>Mention time periods for performance metrics</li>"
            "<li>Reference benchmarks for comparison</li>"
            "<li>Use precise financial terminology</li>"
            "</ul>"
            "</div>"
            "</div>"
            "</div>"
        )

    def _render_assistant_interface(self, instance, request):
        """Render the full assistant interface."""
        return format_html(
            '<div class="ai-content-assistant">'
            "<h3>✨ AI Content Assistant</h3>"
            '<div class="ai-assistant-tabs">'
            '<div class="tab-nav">'
            '<button class="tab-button active" data-tab="statistics">Statistics</button>'
            '<button class="tab-button" data-tab="insights">Insights</button>'
            '<button class="tab-button" data-tab="charts">Charts</button>'
            '<button class="tab-button" data-tab="suggestions">Suggestions</button>'
            "</div>"
            '<div class="tab-content" id="statistics-tab">'
            '<div id="ai-statistics-live"></div>'
            "</div>"
            '<div class="tab-content" id="insights-tab" style="display:none">'
            '<div id="ai-insights-live"></div>'
            "</div>"
            '<div class="tab-content" id="charts-tab" style="display:none">'
            '<div id="ai-charts-live"></div>'
            "</div>"
            '<div class="tab-content" id="suggestions-tab" style="display:none">'
            '<div id="ai-suggestions-live"></div>'
            "</div>"
            "</div>"
            '<div class="ai-assistant-controls">'
            '<button type="button" class="button" onclick="analyzeContentLive()">🔍 Analyze Current Content</button>'
            '<button type="button" class="button bicolor" onclick="optimizeContent()">⚡ Optimize Content</button>'
            "</div>"
            "</div>"
        )


class AIVisualizationPanel(FieldPanel):
    """Panel for AI-powered chart and visualization management."""

    template = "public_site/admin/ai_visualization_panel.html"

    def render_html(self, instance, request):
        """Render visualization management interface."""
        return format_html(
            '<div class="ai-visualization-panel">'
            "<h3>📊 AI-Powered Visualizations</h3>"
            '<div class="viz-panel-content">'
            '<div class="viz-gallery" id="ai-viz-gallery">'
            '<div class="viz-placeholder">Charts will appear here after content analysis</div>'
            "</div>"
            '<div class="viz-controls">'
            '<button type="button" class="button" onclick="generateCharts()">🎨 Generate Charts</button>'
            '<button type="button" class="button" onclick="customizeChart()">⚙️ Customize</button>'
            '<button type="button" class="button bicolor" onclick="exportCharts()">💾 Export</button>'
            "</div>"
            "</div>"
            "</div>"
        )


class AIEnhancedBlogPostEdit(TabbedInterface):
    """Enhanced blog post edit interface with AI panels."""

    def __init__(self, children=None, **kwargs):
        if children is None:
            children = [
                ObjectList(
                    [
                        FieldPanel("title"),
                        FieldPanel("body"),  # This should use BlogStreamField
                    ],
                    heading="Content",
                ),
                ObjectList(
                    [
                        AIStatisticsPanel("body"),
                        AIContentAssistantPanel("body"),
                    ],
                    heading="🤖 AI Assistant",
                ),
                ObjectList(
                    [
                        AIVisualizationPanel("body"),
                    ],
                    heading="📊 Visualizations",
                ),
                ObjectList(
                    [
                        FieldPanel("tags"),
                        FieldPanel("search_description"),
                        FieldPanel("seo_title"),
                    ],
                    heading="Settings",
                ),
            ]

        super().__init__(children, **kwargs)


# Custom form for AI-enhanced editing
class AIEnhancedBlogPostForm(forms.ModelForm):
    """Form with AI assistance for blog post creation."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Add AI assistance to relevant fields
        if "body" in self.fields:
            self.fields["body"].widget.attrs.update(
                {
                    "data-ai-enabled": "true",
                    "data-analysis-endpoint": reverse("public_site:ai_analysis_api"),
                }
            )

    def clean(self):
        """Enhanced validation with AI assistance."""
        cleaned_data = super().clean()

        # Run AI validation if content is provided
        if cleaned_data.get("body"):
            # This could include AI-powered content validation
            pass

        return cleaned_data

    class Media:
        css: ClassVar[dict] = {"all": ("css/admin/ai-enhanced-form.css",)}
        js = (
            "js/admin/ai-enhanced-form.js",
            "js/admin/chart-generator.js",
            "js/admin/statistics-extractor.js",
        )
