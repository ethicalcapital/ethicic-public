"""
Views module for public site.
"""

from .pdf_views import (
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

__all__ = [
    'ExecutiveSummaryPDFView',
    'StrategyPerformancePDFView', 
    'DDQPackagePDFView',
    'CustomProspectPDFView',
    'pdf_brochure_menu',
    'strategy_list_json',
    'bulk_pdf_generation',
    'test_pdf_generation',
    'public_brochure_download',
]