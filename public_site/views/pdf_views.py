"""
Views for PDF brochure generation and download.
"""

from django.http import HttpResponse, Http404, JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.conf import settings

import json
import logging
from typing import List, Optional

from ..utils.pdf_generator import PDFResponseGenerator, PDFGenerator
from ..models import StrategyPage
from ..services.brochure_service import BrochureService

logger = logging.getLogger(__name__)


class PDFBrochureView(View):
    """Base view for PDF brochure generation."""
    
    def __init__(self):
        super().__init__()
        self.pdf_response_generator = PDFResponseGenerator()
        self.brochure_service = BrochureService()
    
    def dispatch(self, request, *args, **kwargs):
        """Add logging and error handling for all PDF requests."""
        try:
            logger.info(f"PDF request: {request.path} from {request.META.get('REMOTE_ADDR')}")
            return super().dispatch(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"PDF generation error: {str(e)}", exc_info=True)
            return JsonResponse({
                'error': 'PDF generation failed',
                'message': str(e) if settings.DEBUG else 'Internal server error'
            }, status=500)


@method_decorator(staff_member_required, name='dispatch')
class ExecutiveSummaryPDFView(PDFBrochureView):
    """Generate and download Executive Summary PDF."""
    
    def get(self, request):
        """Generate Executive Summary PDF response."""
        try:
            return self.pdf_response_generator.executive_summary_response()
        except Exception as e:
            logger.error(f"Executive Summary PDF generation failed: {str(e)}")
            raise Http404("PDF generation failed")


@method_decorator(staff_member_required, name='dispatch')
class StrategyPerformancePDFView(PDFBrochureView):
    """Generate and download Strategy Performance PDF."""
    
    def get(self, request, strategy_slug=None):
        """Generate Strategy Performance PDF response."""
        try:
            # Validate strategy exists if slug provided
            if strategy_slug:
                strategy = get_object_or_404(StrategyPage, slug=strategy_slug)
                logger.info(f"Generating PDF for strategy: {strategy.title}")
            
            return self.pdf_response_generator.strategy_performance_response(strategy_slug)
        except Exception as e:
            logger.error(f"Strategy Performance PDF generation failed: {str(e)}")
            raise Http404("PDF generation failed")


@method_decorator(staff_member_required, name='dispatch')
class DDQPackagePDFView(PDFBrochureView):
    """Generate and download Due Diligence Package PDF."""
    
    def get(self, request):
        """Generate DDQ Package PDF response."""
        try:
            return self.pdf_response_generator.ddq_package_response()
        except Exception as e:
            logger.error(f"DDQ Package PDF generation failed: {str(e)}")
            raise Http404("PDF generation failed")


@method_decorator(staff_member_required, name='dispatch')
class CustomProspectPDFView(PDFBrochureView):
    """Generate and download Custom Prospect PDF."""
    
    def get(self, request):
        """Generate Custom Prospect PDF response."""
        try:
            # Parse sections from query parameters
            sections_param = request.GET.get('sections', '')
            include_sections = None
            
            if sections_param:
                valid_sections = ['overview', 'strategies', 'team', 'ddq_summary', 'performance']
                requested_sections = [s.strip() for s in sections_param.split(',')]
                include_sections = [s for s in requested_sections if s in valid_sections]
                
                if include_sections:
                    logger.info(f"Custom prospect PDF with sections: {include_sections}")
            
            return self.pdf_response_generator.custom_prospect_response(include_sections)
        except Exception as e:
            logger.error(f"Custom Prospect PDF generation failed: {str(e)}")
            raise Http404("PDF generation failed")


@staff_member_required
def pdf_brochure_menu(request):
    """Admin interface to show available PDF downloads."""
    strategies = BrochureService().get_all_strategies()
    
    context = {
        'strategies': strategies,
        'current_date': timezone.now().strftime('%B %d, %Y'),
        'title': 'PDF Brochure Generator',
    }
    
    return render(request, 'admin/pdf_generator.html', context)


@staff_member_required
@require_GET
def strategy_list_json(request):
    """API endpoint to get available strategies for PDF generation."""
    try:
        service = BrochureService()
        strategies = service.get_all_strategies()
        
        strategy_data = []
        for strategy in strategies:
            strategy_data.append({
                'slug': strategy['slug'],
                'title': strategy['title'],
                'subtitle': strategy['subtitle'],
                'has_performance': strategy['performance']['ytd']['strategy'] not in ['-', 'N/A', ''],
                'inception_date': strategy['inception_date'].strftime('%Y-%m-%d') if strategy['inception_date'] else None,
                'risk_level': strategy['risk_level'],
                'pdf_url': f'/pdf/strategy-performance/{strategy["slug"]}/',
            })
        
        return JsonResponse({
            'strategies': strategy_data,
            'count': len(strategy_data),
        })
    except Exception as e:
        logger.error(f"Strategy list API error: {str(e)}")
        return JsonResponse({'error': 'Failed to fetch strategies'}, status=500)


@staff_member_required
@csrf_exempt
@require_POST
def bulk_pdf_generation(request):
    """API endpoint for bulk PDF generation."""
    try:
        data = json.loads(request.body)
        pdf_types = data.get('types', ['all'])
        output_format = data.get('format', 'download')  # 'download' or 'zip'
        
        if 'all' in pdf_types:
            # Generate all PDF types
            generator = PDFGenerator()
            
            results = {
                'executive_summary': generator.generate_executive_summary(),
                'strategy_performance': generator.generate_strategy_performance(),
                'ddq_package': generator.generate_ddq_package(),
                'custom_prospect': generator.generate_custom_prospect(),
            }
            
            if output_format == 'zip':
                # For zip format, we'd need to create a zip file
                # This is a simplified response for now
                return JsonResponse({
                    'status': 'success',
                    'message': 'Bulk generation completed',
                    'files_generated': len(results),
                    'download_urls': {
                        'executive_summary': '/pdf/executive-summary/',
                        'strategy_performance': '/pdf/strategy-performance/',
                        'ddq_package': '/pdf/ddq-package/',
                        'custom_prospect': '/pdf/custom-prospect/',
                    }
                })
        
        return JsonResponse({
            'status': 'success',
            'message': 'Bulk PDF generation initiated',
        })
        
    except Exception as e:
        logger.error(f"Bulk PDF generation error: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': str(e) if settings.DEBUG else 'Generation failed'
        }, status=500)


# Utility view for testing PDF generation during development
@staff_member_required
def test_pdf_generation(request):
    """Development endpoint to test PDF generation."""
    if not settings.DEBUG:
        raise Http404("Not available in production")
    
    pdf_type = request.GET.get('type', 'executive')
    
    try:
        generator = PDFGenerator()
        
        if pdf_type == 'executive':
            pdf_content = generator.generate_executive_summary()
            filename = 'test_executive_summary.pdf'
        elif pdf_type == 'performance':
            strategy_slug = request.GET.get('strategy')
            pdf_content = generator.generate_strategy_performance(strategy_slug)
            filename = f'test_performance_{strategy_slug or "all"}.pdf'
        elif pdf_type == 'ddq':
            pdf_content = generator.generate_ddq_package()
            filename = 'test_ddq_package.pdf'
        elif pdf_type == 'prospect':
            sections = request.GET.get('sections', '').split(',') if request.GET.get('sections') else None
            pdf_content = generator.generate_custom_prospect(sections)
            filename = 'test_prospect.pdf'
        else:
            return JsonResponse({'error': 'Invalid PDF type'}, status=400)
        
        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{filename}"'
        return response
        
    except Exception as e:
        logger.error(f"Test PDF generation error: {str(e)}")
        return JsonResponse({
            'error': 'PDF generation failed',
            'message': str(e),
            'type': pdf_type,
        }, status=500)


# Public-facing view (requires authentication but not staff)
@login_required
@require_GET
def public_brochure_download(request, brochure_type):
    """
    Public endpoint for authenticated users to download brochures.
    Limited to certain brochure types for security.
    """
    allowed_types = ['executive', 'prospect']
    
    if brochure_type not in allowed_types:
        raise Http404("Brochure type not available")
    
    try:
        generator = PDFResponseGenerator()
        
        if brochure_type == 'executive':
            return generator.executive_summary_response()
        elif brochure_type == 'prospect':
            # Limited sections for public access
            sections = ['overview', 'strategies']
            return generator.custom_prospect_response(sections)
            
    except Exception as e:
        logger.error(f"Public brochure download error: {str(e)}")
        raise Http404("Brochure generation failed")