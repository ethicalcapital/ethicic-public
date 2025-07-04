"""
Enhanced StreamField blocks for AI-powered blog content with intelligent statistics
"""

import json
import logging
from decimal import Decimal

# AI services via API calls to main garden web container
import requests
from django.conf import settings
from wagtail import blocks
from wagtail.blocks import StructValue
from wagtail.contrib.table_block.blocks import TableBlock
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.embeds.blocks import EmbedBlock
from wagtail.fields import StreamField
from wagtail.images.blocks import ImageChooserBlock

logger = logging.getLogger(__name__)

# Configuration for AI API calls
AI_API_BASE_URL = getattr(settings, "AI_API_BASE_URL", "http://garden-platform:8000")

# Try to import AI services for direct integration
try:
    from ai_services.providers import get_provider  # noqa: F401

    AI_SERVICES_DIRECT = True
    logger.info("AI services available for direct integration")
except ImportError:
    AI_SERVICES_DIRECT = False
    logger.info(
        "AI services not available - will use API calls if main platform is running"
    )


def call_ai_analysis_api(content_data, analysis_type="comprehensive"):
    """Make API call to main garden web container for AI analysis."""
    try:
        # Use the platform client for better error handling
        from .services.platform_client import platform_client

        if analysis_type == "quick":
            result = platform_client.quick_analyze_content(content_data)
        else:
            result = platform_client.analyze_content(content_data, analysis_type)

        if result:
            return result
        logger.warning("AI API call failed - main platform may be unavailable")
        return None

    except Exception:
        logger.exception("AI API call failed")
        return None


def call_quick_stat_api(text):
    """Make API call for quick statistic analysis."""
    try:
        response = requests.post(
            f"{AI_API_BASE_URL}/admin/ai/quick-stat-analysis/",
            json={"text": text},
            headers={"Content-Type": "application/json"},
            timeout=10,
        )

        if response.status_code == 200:
            return response.json()
        logger.warning(f"Quick stat API call failed with status {response.status_code}")
        return None

    except requests.RequestException:
        logger.exception("Quick stat API call failed")
        return None


# ============================================================================
# BASIC STREAMFIELD BLOCKS (for backwards compatibility)
# ============================================================================


class HeadingBlock(blocks.StructBlock):
    """Heading block with size options."""

    heading_text = blocks.CharBlock(classname="title")
    size = blocks.ChoiceBlock(
        choices=[
            ("h2", "H2"),
            ("h3", "H3"),
            ("h4", "H4"),
        ],
        default="h2",
    )

    class Meta:
        template = "blocks/heading_block.html"
        icon = "title"
        label = "Heading"


class ParagraphBlock(blocks.RichTextBlock):
    """Rich text paragraph block."""

    class Meta:
        template = "blocks/paragraph_block.html"
        icon = "pilcrow"
        label = "Paragraph"


class RichTextBlock(blocks.RichTextBlock):
    """Standard rich text block."""

    class Meta:
        template = "blocks/rich_text_block.html"
        icon = "pilcrow"
        label = "Rich Text"


class ImageBlock(blocks.StructBlock):
    """Image block with caption and alignment."""

    image = ImageChooserBlock()
    caption = blocks.CharBlock(required=False)
    alignment = blocks.ChoiceBlock(
        choices=[
            ("left", "Left"),
            ("right", "Right"),
            ("center", "Center"),
            ("full", "Full Width"),
        ],
        default="center",
    )

    class Meta:
        template = "blocks/image_block.html"
        icon = "image"
        label = "Image"


class EmbedVideoBlock(EmbedBlock):
    """Video embed block."""

    class Meta:
        template = "blocks/video_block.html"
        icon = "media"
        label = "Video"


class DocumentBlock(blocks.StructBlock):
    """Document download block."""

    document = DocumentChooserBlock()
    title = blocks.CharBlock(
        required=False, help_text="Optional title to override document filename"
    )
    description = blocks.TextBlock(required=False)

    class Meta:
        template = "blocks/document_block.html"
        icon = "doc-full"
        label = "Document"


class QuoteBlock(blocks.StructBlock):
    """Quote block with attribution."""

    quote = blocks.TextBlock()
    attribution = blocks.CharBlock(required=False)
    cite_url = blocks.URLBlock(required=False)

    class Meta:
        template = "blocks/quote_block.html"
        icon = "openquote"
        label = "Quote"


class CalloutBlock(blocks.StructBlock):
    """Callout/alert block."""

    type = blocks.ChoiceBlock(
        choices=[
            ("info", "Info"),
            ("warning", "Warning"),
            ("success", "Success"),
            ("error", "Error"),
        ],
        default="info",
    )
    title = blocks.CharBlock(required=False)
    content = blocks.RichTextBlock()

    class Meta:
        template = "public_site/blocks/callout.html"
        icon = "warning"
        label = "Callout"


class CodeBlock(blocks.StructBlock):
    """Code block with syntax highlighting."""

    language = blocks.ChoiceBlock(
        choices=[
            ("python", "Python"),
            ("javascript", "JavaScript"),
            ("css", "CSS"),
            ("html", "HTML"),
            ("bash", "Bash"),
            ("sql", "SQL"),
            ("json", "JSON"),
        ],
        default="python",
    )
    code = blocks.TextBlock()

    class Meta:
        template = "blocks/code_block.html"
        icon = "code"
        label = "Code"


class ButtonBlock(blocks.StructBlock):
    """Call-to-action button block."""

    text = blocks.CharBlock()
    url = blocks.URLBlock()
    style = blocks.ChoiceBlock(
        choices=[
            ("primary", "Primary"),
            ("secondary", "Secondary"),
            ("success", "Success"),
            ("warning", "Warning"),
        ],
        default="primary",
    )

    class Meta:
        template = "blocks/button_block.html"
        icon = "redirect"
        label = "Button"


class SimpleTableBlock(blocks.StructBlock):
    """Simple table block."""

    caption = blocks.CharBlock(required=False)
    table = TableBlock()

    class Meta:
        template = "blocks/table_block.html"
        icon = "table"
        label = "Table"


class DataTableBlock(blocks.StructBlock):
    """Data table block for financial data."""

    caption = blocks.CharBlock(required=False, help_text="Table title or caption")
    description = blocks.RichTextBlock(
        required=False, help_text="Optional description or context"
    )
    table = TableBlock(help_text="Add table data - first row will be used as headers")
    source = blocks.CharBlock(required=False, help_text="Data source attribution")

    class Meta:
        template = "public_site/blocks/table_block.html"
        icon = "table"
        label = "Data Table"


class StatsBlock(blocks.StructBlock):
    """Statistics display block."""

    title = blocks.CharBlock(required=False)
    stats = blocks.ListBlock(
        blocks.StructBlock(
            [
                ("value", blocks.CharBlock()),
                ("label", blocks.CharBlock()),
                ("description", blocks.TextBlock(required=False)),
            ]
        )
    )

    class Meta:
        template = "blocks/stats_block.html"
        icon = "list-ol"
        label = "Statistics"


class SeparatorBlock(blocks.StaticBlock):
    """Horizontal separator/divider."""

    class Meta:
        template = "blocks/separator_block.html"
        icon = "horizontalrule"
        label = "Separator"
        admin_text = "Horizontal line separator"


# ============================================================================
# AI-ENHANCED BLOCKS
# ============================================================================


class AIEnhancedStatisticValue(StructValue):
    """Enhanced StructValue for AI-powered statistics with dynamic properties."""

    @property
    def is_meaningful(self):
        """Check if AI has identified this statistic as meaningful."""
        return self.get("ai_confidence", 0.0) > 0.7

    @property
    def visualization_config(self):
        """Get AI-recommended visualization configuration."""
        viz_type = self.get("visualization_type", "bar")
        chart_config_str = self.get("chart_config", None)
        chart_config = {}
        if chart_config_str:
            try:
                chart_config = json.loads(chart_config_str)
            except (json.JSONDecodeError, TypeError):
                chart_config = {}

        return {
            "type": viz_type,
            "title": self.get("chart_title", ""),
            "config": chart_config,
        }

    @property
    def context_summary(self):
        """Get AI-generated context summary."""
        return self.get("ai_context", self.get("description", ""))


class KeyStatisticBlock(blocks.StructBlock):
    """Key statistic block for highlighting important data points and metrics."""

    # Core statistic data
    value = blocks.CharBlock(
        max_length=50, help_text="The statistic value (e.g., '12.4%', '$1.2M', '3.8x')"
    )
    label = blocks.CharBlock(
        max_length=100,
        help_text="Statistic label (e.g., 'Annual Return', 'Market Cap')",
    )
    description = blocks.TextBlock(
        required=False, help_text="Optional description or context for this statistic"
    )

    # AI enhancement fields (populated automatically)
    ai_confidence = blocks.DecimalBlock(
        default=Decimal("0.0"),
        max_digits=3,
        decimal_places=2,
        help_text="AI confidence in significance (0.0-1.0) - auto-populated",
    )
    ai_context = blocks.TextBlock(
        required=False,
        help_text="AI-generated context for this statistic - auto-populated",
    )
    significance_level = blocks.ChoiceBlock(
        choices=[
            ("high", "High Significance"),
            ("medium", "Medium Significance"),
            ("low", "Low Significance"),
        ],
        default="medium",
        help_text="AI assessment of statistical significance",
    )

    # Visualization configuration
    visualization_type = blocks.ChoiceBlock(
        choices=[
            ("bar", "Bar Chart"),
            ("performance_comparison", "Performance Comparison"),
            ("allocation_pie", "Allocation Pie Chart"),
            ("trend_line", "Trend Line"),
            ("gauge", "Gauge/Meter"),
            ("callout", "Highlighted Callout"),
        ],
        default="bar",
        help_text="AI-recommended visualization type",
    )
    chart_title = blocks.CharBlock(
        max_length=100,
        required=False,
        help_text="Chart title - auto-generated based on context",
    )
    chart_config = blocks.TextBlock(
        required=False, help_text="JSON configuration for chart - auto-generated"
    )

    # Categorization
    statistic_category = blocks.ChoiceBlock(
        choices=[
            ("performance", "Performance/Returns"),
            ("valuation", "Valuation Metrics"),
            ("risk", "Risk Metrics"),
            ("allocation", "Portfolio Allocation"),
            ("fundamental", "Fundamental Analysis"),
            ("market", "Market Data"),
        ],
        default="performance",
        help_text="Category of statistic - auto-identified by AI",
    )

    # Related entities (auto-populated by AI)
    related_entities = blocks.ListBlock(
        blocks.CharBlock(max_length=100),
        required=False,
        help_text="Related companies, funds, or securities - auto-identified",
    )

    time_period = blocks.ChoiceBlock(
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
        help_text="Time period for this statistic",
    )

    class Meta:
        template = "public_site/blocks/key_statistic.html"
        value_class = AIEnhancedStatisticValue
        icon = "success"
        label = "Key Statistic"

    def get_context(self, value, parent_context=None):
        """Enhanced context with AI analysis data."""
        context = super().get_context(value, parent_context)

        # Add visualization data
        context["chart_data"] = self._prepare_chart_data(value)
        context["is_significant"] = value.is_meaningful
        context["context_summary"] = value.context_summary

        return context

    def _prepare_chart_data(self, value):
        """Prepare chart data based on AI recommendations."""
        viz_config = value.visualization_config

        if viz_config["type"] == "performance_comparison":
            return {
                "type": "bar",
                "data": {
                    "labels": [value.get("label", "Statistic")],
                    "datasets": [
                        {
                            "data": [
                                self._parse_numeric_value(value.get("value", "0"))
                            ],
                            "backgroundColor": ["#4f46e5"],
                        }
                    ],
                },
            }
        if viz_config["type"] == "gauge":
            numeric_value = self._parse_numeric_value(value.get("value", "0"))
            return {
                "type": "doughnut",
                "data": {
                    "datasets": [
                        {
                            "data": [numeric_value, 100 - numeric_value],
                            "backgroundColor": ["#4f46e5", "#e5e7eb"],
                        }
                    ]
                },
            }

        return {}

    def _parse_numeric_value(self, value_str):
        """Parse numeric value from string, handling percentages and currency."""
        import re

        # Remove currency symbols and commas
        cleaned = re.sub(r"[$,]", "", value_str)

        # Handle percentages
        if "%" in cleaned:
            cleaned = cleaned.replace("%", "")
            return (
                float(cleaned)
                if cleaned.replace(".", "").replace("-", "").isdigit()
                else 0.0
            )

        # Handle multipliers (K, M, B)
        multipliers = {"K": 1000, "M": 1000000, "B": 1000000000}
        for suffix, multiplier in multipliers.items():
            if suffix in cleaned.upper():
                cleaned = cleaned.upper().replace(suffix, "")
                return (
                    float(cleaned) * multiplier
                    if cleaned.replace(".", "").replace("-", "").isdigit()
                    else 0.0
                )

        return (
            float(cleaned)
            if cleaned.replace(".", "").replace("-", "").isdigit()
            else 0.0
        )


class AIContentAnalysisBlock(blocks.StructBlock):
    """Block for AI-powered content analysis and statistic extraction."""

    content = blocks.RichTextBlock(
        help_text="Enter your content - AI will automatically identify meaningful statistics"
    )

    # AI analysis results (populated automatically)
    extracted_statistics = blocks.ListBlock(
        KeyStatisticBlock(),
        required=False,
        help_text="Statistics automatically extracted by AI",
    )

    ai_insights = blocks.ListBlock(
        blocks.TextBlock(), required=False, help_text="Key insights identified by AI"
    )

    analysis_confidence = blocks.DecimalBlock(
        default=Decimal("0.0"),
        max_digits=3,
        decimal_places=2,
        help_text="Overall AI confidence in analysis (0.0-1.0)",
    )

    last_analyzed = blocks.DateTimeBlock(
        required=False, help_text="When this content was last analyzed by AI"
    )

    class Meta:
        template = "public_site/blocks/ai_content_analysis.html"
        icon = "cogs"
        label = "AI Content Analysis"

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context)

        # Prepare summary statistics for display
        context["summary_stats"] = self._get_summary_statistics(value)
        context["high_confidence_stats"] = [
            stat
            for stat in value.get("extracted_statistics", [])
            if stat.get("ai_confidence", 0) > 0.8
        ]

        return context

    def _get_summary_statistics(self, value):
        """Get summary of extracted statistics by category."""
        stats = value.get("extracted_statistics", [])
        summary = {}

        for stat in stats:
            category = stat.get("statistic_category", "other")
            if category not in summary:
                summary[category] = []
            summary[category].append(stat)

        return summary


class DynamicChartBlock(blocks.StructBlock):
    """Dynamic chart block that generates visualizations from AI-identified statistics."""

    title = blocks.CharBlock(max_length=100, help_text="Chart title")

    chart_type = blocks.ChoiceBlock(
        choices=[
            ("performance_comparison", "Performance Comparison"),
            ("allocation_breakdown", "Allocation Breakdown"),
            ("trend_analysis", "Trend Analysis"),
            ("risk_metrics", "Risk Metrics Dashboard"),
            ("custom", "Custom Configuration"),
        ],
        default="performance_comparison",
    )

    data_source = blocks.ChoiceBlock(
        choices=[
            ("ai_extracted", "AI-Extracted from Content"),
            ("manual_entry", "Manual Data Entry"),
            ("portfolio_integration", "Portfolio Data Integration"),
        ],
        default="ai_extracted",
        help_text="Source of data for this chart",
    )

    # For manual data entry
    manual_data = blocks.TextBlock(
        required=False,
        help_text="JSON data for manual charts - only used if data_source is manual_entry",
    )

    # AI-powered configuration
    auto_generate = blocks.BooleanBlock(
        default=True,
        help_text="Let AI automatically configure this chart based on content statistics",
    )

    chart_config = blocks.TextBlock(
        required=False,
        help_text="Advanced chart configuration (JSON) - auto-generated if empty",
    )

    # Styling options
    color_scheme = blocks.ChoiceBlock(
        choices=[
            ("default", "Default Garden Colors"),
            ("performance", "Performance (Green/Red)"),
            ("monochrome", "Monochrome"),
            ("categorical", "Categorical Colors"),
        ],
        default="default",
    )

    show_legend = blocks.BooleanBlock(default=True)
    show_values = blocks.BooleanBlock(default=True)
    responsive = blocks.BooleanBlock(default=True)

    class Meta:
        template = "public_site/blocks/dynamic_chart.html"
        icon = "image"
        label = "Dynamic Chart"

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context)

        # Generate chart configuration
        context["chart_config"] = self._generate_chart_config(value, parent_context)
        context["chart_id"] = f"chart_{hash(str(value))}"

        return context

    def _generate_chart_config(self, value, parent_context):
        """Generate Chart.js configuration based on settings and data source."""
        chart_type = value.get("chart_type")

        if value.get("data_source") == "ai_extracted":
            # Get AI-extracted statistics from the page context
            chart_data = self._get_ai_statistics_for_chart(parent_context, chart_type)
        elif value.get("data_source") == "manual_entry":
            manual_data_str = value.get("manual_data", "{}")
            try:
                chart_data = json.loads(manual_data_str) if manual_data_str else {}
            except (json.JSONDecodeError, TypeError):
                chart_data = {}
        else:
            chart_data = {}

        # Generate configuration based on chart type
        if chart_type == "performance_comparison":
            return self._generate_performance_chart_config(chart_data, value)
        if chart_type == "allocation_breakdown":
            return self._generate_allocation_chart_config(chart_data, value)
        return self._generate_default_chart_config(chart_data, value)

    def _get_ai_statistics_for_chart(self, parent_context, chart_type):
        """Extract relevant AI statistics for chart generation."""
        # This would typically extract from the parent page's AI analysis
        # For now, return sample data structure
        return {
            "labels": ["Portfolio", "Benchmark"],
            "datasets": [
                {
                    "label": "Annual Return",
                    "data": [12.4, 9.8],
                    "backgroundColor": ["#4f46e5", "#6b7280"],
                }
            ],
        }

    def _generate_performance_chart_config(self, data, value):
        """Generate Chart.js config for performance comparison."""
        return {
            "type": "bar",
            "data": data,
            "options": {
                "responsive": value.get("responsive", True),
                "plugins": {
                    "legend": {"display": value.get("show_legend", True)},
                    "title": {"display": True, "text": value.get("title", "")},
                },
                "scales": {
                    "y": {
                        "beginAtZero": True,
                        "ticks": {
                            "callback": 'function(value) { return value + "%"; }'
                        },
                    }
                },
            },
        }

    def _generate_allocation_chart_config(self, data, value):
        """Generate Chart.js config for allocation breakdown."""
        return {
            "type": "doughnut",
            "data": data,
            "options": {
                "responsive": value.get("responsive", True),
                "plugins": {
                    "legend": {"display": value.get("show_legend", True)},
                    "title": {"display": True, "text": value.get("title", "")},
                },
            },
        }

    def _generate_default_chart_config(self, data, value):
        """Generate default Chart.js configuration."""
        return {
            "type": "line",
            "data": data,
            "options": {
                "responsive": value.get("responsive", True),
                "plugins": {
                    "legend": {"display": value.get("show_legend", True)},
                    "title": {"display": True, "text": value.get("title", "")},
                },
            },
        }


# Enhanced StreamField definition with AI blocks
class BlogStreamField(StreamField):
    """Enhanced StreamField with AI-powered blocks for intelligent content creation."""

    def __init__(self, *args, **kwargs):
        block_types = [
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
            ("ai_content_analysis", AIContentAnalysisBlock()),
            ("key_statistic", KeyStatisticBlock()),
            ("dynamic_chart", DynamicChartBlock()),
            ("table", DataTableBlock()),
            ("image", ImageChooserBlock()),
            ("embed", EmbedBlock()),
            ("callout", CalloutBlock()),
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
        ]

        super().__init__(block_types, *args, **kwargs)
