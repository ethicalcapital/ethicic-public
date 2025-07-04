"""
URL configuration for AI-powered blog content analysis
"""

from django.urls import path

from .views.ai_analysis_api import (
    AIContentAnalysisView,
    generate_chart_preview,
    quick_statistic_analysis,
)

app_name = "public_site_ai"

urlpatterns = [
    # Main AI content analysis endpoint
    path(
        "ai/analyze-content/", AIContentAnalysisView.as_view(), name="ai_analysis_api"
    ),
    # Quick statistic analysis for real-time feedback
    path(
        "ai/quick-stat-analysis/", quick_statistic_analysis, name="quick_stat_analysis"
    ),
    # Chart preview generation
    path(
        "ai/generate-chart-preview/",
        generate_chart_preview,
        name="generate_chart_preview",
    ),
]
