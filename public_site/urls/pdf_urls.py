"""
URL patterns for PDF brochure generation and download.
"""

from django.urls import path

from ..views.pdf_views import (
    ExecutiveSummaryPDFView,
    StrategyPerformancePDFView,
    DDQPackagePDFView,
    CustomProspectPDFView,
    pdf_brochure_menu,
    strategy_list_json,
    bulk_pdf_generation,
    test_pdf_generation,
    public_brochure_download,
)

app_name = 'pdf'

urlpatterns = [
    # Main PDF endpoints (staff only)
    path('executive-summary/', ExecutiveSummaryPDFView.as_view(), name='executive_summary'),
    path('strategy-performance/', StrategyPerformancePDFView.as_view(), name='strategy_performance_all'),
    path('strategy-performance/<slug:strategy_slug>/', StrategyPerformancePDFView.as_view(), name='strategy_performance'),
    path('ddq-package/', DDQPackagePDFView.as_view(), name='ddq_package'),
    path('custom-prospect/', CustomProspectPDFView.as_view(), name='custom_prospect'),
    
    # Admin/management endpoints
    path('menu/', pdf_brochure_menu, name='brochure_menu'),
    path('api/strategies/', strategy_list_json, name='strategy_list_api'),
    path('api/bulk-generate/', bulk_pdf_generation, name='bulk_generate'),
    
    # Public access (authenticated users only)
    path('public/<str:brochure_type>/', public_brochure_download, name='public_download'),
    
    # Development/testing endpoint
    path('test/', test_pdf_generation, name='test_generation'),
]