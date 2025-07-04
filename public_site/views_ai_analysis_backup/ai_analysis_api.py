"""
AI Analysis API Views for Blog Content
Provides endpoints for AI-powered content analysis using Maverick agents
"""

import asyncio
import json
import logging
import re
from typing import Any

from ai_services.services.blog_content_analysis_service import BlogAnalysisService
from django.contrib.admin.views.decorators import staff_member_required
from django.core.cache import cache
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.http import require_http_methods

logger = logging.getLogger(__name__)


class AIContentAnalysisView(View):
    """API view for AI-powered content analysis."""

    def __init__(self):
        super().__init__()
        self.blog_analysis_service = BlogAnalysisService()

    @method_decorator(staff_member_required)
    # SECURITY FIX: Removed csrf_exempt to prevent CSRF attacks
    # Staff-only endpoints should still have CSRF protection
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request):
        """Analyze content and return AI-generated insights."""
        try:
            # Parse request data
            data = json.loads(request.body)
            content = data.get("content", {})
            analysis_type = data.get("analysis_type", "statistics")
            options = data.get("options", {})

            # Validate content
            if not content:
                return JsonResponse({
                    "error": "No content provided for analysis"
                }, status=400)

            # Check cache first
            cache_key = self._generate_cache_key(content, analysis_type)
            cached_result = cache.get(cache_key)
            if cached_result and not options.get("force_refresh", False):
                logger.info("Returning cached AI analysis result")
                return JsonResponse(cached_result)

            # Run AI analysis
            content_text = self._extract_content_text(content)
            analysis_result = asyncio.run(
                self.blog_analysis_service.content_processor.analyze_content(
                    content_text,
                    context={"analysis_type": analysis_type, **options}
                )
            )

            # Enhance results based on analysis type
            enhanced_result = self._enhance_analysis_result(
                analysis_result, analysis_type, options
            )

            # Cache results for 30 minutes
            cache.set(cache_key, enhanced_result, timeout=1800)

            logger.info(f"AI content analysis completed for {len(content_text)} characters")
            return JsonResponse(enhanced_result)

        except json.JSONDecodeError:
            return JsonResponse({
                "error": "Invalid JSON in request body"
            }, status=400)
        except Exception as e:
            logger.error(f"AI content analysis failed: {str(e)}")
            return JsonResponse({
                "error": "Analysis failed",
                "details": str(e)
            }, status=500)

    def _extract_content_text(self, content: dict[str, Any]) -> str:
        """Extract plain text from content structure."""
        content_parts = []

        # Extract title
        if content.get("title"):
            content_parts.append(f"Title: {content['title']}")

        # Extract body text
        if content.get("body"):
            content_parts.append(content["body"])

        # Extract StreamField content
        if content.get("streamfield_content"):
            for block in content["streamfield_content"]:
                block_type = block.get("type", "")
                block_content = block.get("content", "")

                if block_type == "rich_text" and isinstance(block_content, str):
                    content_parts.append(block_content)
                elif block_type == "ai_statistic" and isinstance(block_content, dict):
                    value = block_content.get("value", "")
                    label = block_content.get("label", "")
                    desc = block_content.get("description", "")
                    content_parts.append(f"Statistic: {value} ({label}) - {desc}")
                elif isinstance(block_content, str):
                    content_parts.append(block_content)

        return "\n\n".join(filter(None, content_parts))

    def _enhance_analysis_result(
        self,
        analysis: dict[str, Any],
        analysis_type: str,
        options: dict[str, Any]
    ) -> dict[str, Any]:
        """Enhance analysis results based on type and options."""
        enhanced = dict(analysis)

        # Add metadata
        enhanced["analysis_metadata"] = {
            "type": analysis_type,
            "timestamp": str(asyncio.get_event_loop().time()),
            "options": options,
            "statistics_count": len(analysis.get("meaningful_statistics", [])),
            "insights_count": len(analysis.get("key_insights", [])),
            "charts_count": len(analysis.get("recommended_charts", []))
        }

        # Generate content suggestions if requested
        if options.get("include_suggestions", True):
            enhanced["content_suggestions"] = self._generate_content_suggestions(analysis)

        # Add visualization recommendations if requested
        if options.get("include_charts", True):
            enhanced["recommended_charts"] = self._enhance_chart_recommendations(
                analysis.get("recommended_charts", [])
            )

        # Add portfolio context if available
        if options.get("include_portfolio_context", False):
            enhanced["portfolio_context"] = self._add_portfolio_context(analysis)

        return enhanced

    def _generate_content_suggestions(self, analysis: dict[str, Any]) -> list:
        """Generate content improvement suggestions based on analysis."""
        suggestions = []
        stats = analysis.get("meaningful_statistics", [])

        # Suggest improvements based on statistics quality
        if len(stats) == 0:
            suggestions.append({
                "type": "content_enhancement",
                "content": "Consider adding specific financial metrics with context to make your analysis more data-driven.",
                "priority": "high"
            })
        elif len(stats) < 3:
            suggestions.append({
                "type": "content_enhancement",
                "content": "Your content would benefit from additional supporting statistics and metrics.",
                "priority": "medium"
            })

        # Suggest chart additions
        high_confidence_stats = [s for s in stats if s.get("confidence", 0) > 0.8]
        if len(high_confidence_stats) >= 2:
            suggestions.append({
                "type": "visualization",
                "content": "Consider adding a comparison chart to visualize the relationship between your key metrics.",
                "priority": "medium"
            })

        # Suggest time period clarifications
        stats_without_time = [s for s in stats if not s.get("time_period")]
        if len(stats_without_time) > 0:
            suggestions.append({
                "type": "context_clarity",
                "content": 'Add time periods to your performance metrics for better context (e.g., "annual", "quarterly").',
                "priority": "medium"
            })

        return suggestions

    def _enhance_chart_recommendations(self, charts: list) -> list:
        """Enhance chart recommendations with additional configuration."""
        enhanced_charts = []

        for chart in charts:
            enhanced_chart = dict(chart)

            # Add Chart.js configuration
            enhanced_chart["chartjs_config"] = self._generate_chartjs_config(chart)

            # Add color schemes
            enhanced_chart["color_schemes"] = {
                "default": ["#4f46e5", "#06b6d4", "#10b981", "#f59e0b"],
                "performance": ["#10b981", "#ef4444", "#6b7280"],
                "monochrome": ["#374151", "#6b7280", "#9ca3af", "#d1d5db"]
            }

            # Add responsive options
            enhanced_chart["responsive_config"] = {
                "maintainAspectRatio": True,
                "aspectRatio": 2,
                "scales": {
                    "x": {"display": True},
                    "y": {"display": True}
                }
            }

            enhanced_charts.append(enhanced_chart)

        return enhanced_charts

    def _generate_chartjs_config(self, chart: dict[str, Any]) -> dict[str, Any]:
        """Generate Chart.js configuration for a chart recommendation."""
        chart_type = chart.get("type", "bar")

        base_config = {
            "type": "bar" if chart_type == "performance_comparison" else chart_type,
            "data": {
                "labels": chart.get("labels", ["Data"]),
                "datasets": [{
                    "label": chart.get("title", "Dataset"),
                    "data": chart.get("data_points", [1]),
                    "backgroundColor": "#4f46e5",
                    "borderColor": "#4338ca",
                    "borderWidth": 1
                }]
            },
            "options": {
                "responsive": True,
                "plugins": {
                    "title": {
                        "display": True,
                        "text": chart.get("title", "")
                    },
                    "legend": {
                        "display": True
                    }
                }
            }
        }

        # Customize based on chart type
        if chart_type == "allocation_breakdown":
            base_config["type"] = "doughnut"
            base_config["data"]["datasets"][0]["backgroundColor"] = [
                "#4f46e5", "#06b6d4", "#10b981", "#f59e0b", "#ef4444"
            ]
        elif chart_type == "trend_analysis":
            base_config["type"] = "line"
            base_config["data"]["datasets"][0]["fill"] = False
            base_config["data"]["datasets"][0]["tension"] = 0.1

        return base_config

    def _add_portfolio_context(self, analysis: dict[str, Any]) -> dict[str, Any]:
        """Add portfolio-specific context to the analysis."""
        # This would integrate with portfolio data
        # For now, return placeholder context
        return {
            "portfolio_relevance": "high",
            "risk_implications": "moderate",
            "performance_context": "outperforming",
            "allocation_impact": "significant"
        }

    def _generate_cache_key(self, content: dict[str, Any], analysis_type: str) -> str:
        """Generate cache key for content analysis."""
        content_hash = hash(str(content))
        return f"ai_analysis_{analysis_type}_{content_hash}"


@staff_member_required
@require_http_methods(["POST"])
# SECURITY FIX: Removed csrf_exempt - staff endpoints need CSRF protection
def quick_statistic_analysis(request):
    """Quick endpoint for analyzing individual statistics."""
    try:
        data = json.loads(request.body)
        statistic_text = data.get("text", "")

        if not statistic_text:
            return JsonResponse({"error": "No text provided"}, status=400)

        # Simple regex-based quick analysis for immediate feedback
        import re

        patterns = {
            "percentage": r"([+-]?\d+\.?\d*%)",
            "currency": r"\$(\d+(?:,\d{3})*(?:\.\d{2})?[BMK]?)",
            "ratio": r"(\d+\.?\d*x)",
            "return": r"([+-]?\d+\.?\d*%)\s*(?:return|performance|gain|loss)",
        }

        matches = {}
        for pattern_type, pattern in patterns.items():
            found = re.findall(pattern, statistic_text, re.IGNORECASE)
            if found:
                matches[pattern_type] = found

        # Quick confidence scoring
        confidence = 0.5
        if matches:
            confidence += 0.3
            if "return" in matches:
                confidence += 0.2

        return JsonResponse({
            "matches": matches,
            "confidence": min(confidence, 1.0),
            "is_meaningful": confidence > 0.7,
            "suggested_category": "performance" if "return" in matches else "general"
        })

    except Exception as e:
        logger.error(f"Quick statistic analysis failed: {str(e)}")
        return JsonResponse({"error": str(e)}, status=500)


@staff_member_required
@require_http_methods(["POST"])
# SECURITY FIX: Removed csrf_exempt - staff endpoints need CSRF protection
def generate_chart_preview(request):
    """Generate a chart preview based on statistics."""
    try:
        data = json.loads(request.body)
        chart_type = data.get("chart_type", "bar")
        statistics = data.get("statistics", [])

        if not statistics:
            return JsonResponse({"error": "No statistics provided"}, status=400)

        # Generate preview configuration
        preview_config = {
            "type": chart_type,
            "data": {
                "labels": [stat.get("label", f"Stat {i+1}") for i, stat in enumerate(statistics)],
                "datasets": [{
                    "label": "Values",
                    "data": [float(re.sub(r"[^\d.-]", "", stat.get("value", "0"))) for stat in statistics],
                    "backgroundColor": "#4f46e5"
                }]
            },
            "options": {
                "responsive": True,
                "plugins": {
                    "legend": {"display": False}
                }
            }
        }

        return JsonResponse({
            "preview_config": preview_config,
            "preview_html": f'<div class="chart-preview">Chart with {len(statistics)} data points</div>'
        })

    except Exception as e:
        logger.error(f"Chart preview generation failed: {str(e)}")
        return JsonResponse({"error": str(e)}, status=500)
