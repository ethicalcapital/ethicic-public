"""
PDF generation utilities using WeasyPrint for professional brochure creation.
"""

import os
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional
from io import BytesIO

from django.conf import settings
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.utils import timezone

from ..services.brochure_service import BrochureService

# Try to import WeasyPrint, fallback to simple generator if not available
try:
    from weasyprint import HTML, CSS
    from weasyprint.text.fonts import FontConfiguration
    WEASYPRINT_AVAILABLE = True
except (ImportError, OSError):
    # ImportError: WeasyPrint not installed
    # OSError: System libraries missing (like gobject-2.0)
    WEASYPRINT_AVAILABLE = False

# Import simple PDF generator as fallback
from .pdf_generator_simple import SimplePDFGenerator, SimplePDFResponseGenerator


class PDFGenerator:
    """Professional PDF generator for investment brochures."""
    
    def __init__(self):
        self.brochure_service = BrochureService()
        
        # Use WeasyPrint if available, otherwise fallback to simple generator
        if WEASYPRINT_AVAILABLE:
            self.font_config = FontConfiguration()
            # CSS file path
            self.css_path = Path(settings.STATIC_ROOT or settings.BASE_DIR / 'static') / 'css' / 'pdf-styles.css'
            if not self.css_path.exists():
                # Fallback to development static files
                self.css_path = Path(settings.BASE_DIR) / 'static' / 'css' / 'pdf-styles.css'
            self.use_weasyprint = True
        else:
            self.simple_generator = SimplePDFGenerator()
            self.use_weasyprint = False
    
    def generate_executive_summary(self, output_path: Optional[str] = None) -> bytes:
        """Generate Executive Summary PDF brochure."""
        if not self.use_weasyprint:
            return self.simple_generator.generate_executive_summary(output_path)
        
        data = self.brochure_service.get_executive_summary_data()
        return self._generate_pdf(
            template='pdf/executive_summary.html',
            data=data,
            output_path=output_path,
            filename='ethical_capital_executive_summary.pdf'
        )
    
    def generate_strategy_performance(self, strategy_slug: Optional[str] = None, output_path: Optional[str] = None) -> bytes:
        """Generate Strategy Performance PDF brochure."""
        if not self.use_weasyprint:
            return self.simple_generator.generate_strategy_performance(strategy_slug, output_path)
        
        data = self.brochure_service.get_strategy_performance_data(strategy_slug)
        filename = f'ethical_capital_strategy_performance{"_" + strategy_slug if strategy_slug else ""}.pdf'
        return self._generate_pdf(
            template='pdf/strategy_performance.html',
            data=data,
            output_path=output_path,
            filename=filename
        )
    
    def generate_ddq_package(self, output_path: Optional[str] = None) -> bytes:
        """Generate Due Diligence Package PDF."""
        if not self.use_weasyprint:
            return self.simple_generator.generate_ddq_package(output_path)
        
        data = self.brochure_service.get_ddq_package_data()
        return self._generate_pdf(
            template='pdf/due_diligence_package.html',
            data=data,
            output_path=output_path,
            filename='ethical_capital_due_diligence_package.pdf'
        )
    
    def generate_custom_prospect(self, include_sections: list = None, output_path: Optional[str] = None) -> bytes:
        """Generate Custom Prospect PDF brochure."""
        if not self.use_weasyprint:
            return self.simple_generator.generate_custom_prospect(include_sections, output_path)
        
        data = self.brochure_service.get_custom_prospect_data(include_sections)
        return self._generate_pdf(
            template='pdf/custom_prospect.html',
            data=data,
            output_path=output_path,
            filename='ethical_capital_investment_overview.pdf'
        )
    
    def _generate_pdf(self, template: str, data: Dict[str, Any], output_path: Optional[str] = None, filename: str = 'brochure.pdf') -> bytes:
        """
        Core PDF generation method.
        
        Args:
            template: Django template path
            data: Data context for template
            output_path: Optional file path to save PDF
            filename: Default filename for the PDF
            
        Returns:
            PDF content as bytes
        """
        # Prepare template context
        context = {
            'data': data,
            'css_file_path': str(self.css_path),
            'contact_info': 'info@ethicic.com | www.ethicic.com',
            'performance_disclaimer': self._get_standard_disclaimer(),
        }
        
        # Render HTML template
        html_content = render_to_string(template, context)
        
        # Create WeasyPrint HTML object
        html = HTML(string=html_content, base_url=str(settings.BASE_DIR))
        
        # Create CSS object if CSS file exists
        css_objects = []
        if self.css_path.exists():
            css_objects.append(CSS(filename=str(self.css_path), font_config=self.font_config))
        else:
            # Fallback CSS if file doesn't exist
            css_objects.append(CSS(string=self._get_fallback_css(), font_config=self.font_config))
        
        # Generate PDF
        if output_path:
            # Save to file
            html.write_pdf(output_path, stylesheets=css_objects, font_config=self.font_config)
            with open(output_path, 'rb') as file:
                return file.read()
        else:
            # Return bytes
            pdf_buffer = BytesIO()
            html.write_pdf(pdf_buffer, stylesheets=css_objects, font_config=self.font_config)
            return pdf_buffer.getvalue()
    
    def _get_standard_disclaimer(self) -> str:
        """Get standard performance disclaimer text."""
        return """
        Past performance is not indicative of future results. All investments involve risk, 
        including potential loss of principal. Performance data represents composite returns 
        and may not reflect the experience of individual client accounts. Please refer to 
        our Form ADV Part 2A for additional important disclosures.
        """
    
    def _get_fallback_css(self) -> str:
        """Fallback CSS if main CSS file is not available."""
        return """
        @page {
            margin: 0.75in;
            size: letter;
        }
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            font-size: 11pt;
        }
        h1, h2, h3 {
            color: #7c3aed;
            font-weight: bold;
        }
        h1 { font-size: 24pt; }
        h2 { font-size: 18pt; }
        h3 { font-size: 14pt; }
        .performance-table {
            width: 100%;
            border-collapse: collapse;
            margin: 1rem 0;
        }
        .performance-table th,
        .performance-table td {
            padding: 8px;
            border-bottom: 1px solid #ddd;
            text-align: left;
        }
        .performance-table th {
            background-color: #f5f5f5;
            font-weight: bold;
        }
        .positive { color: #059669; }
        .negative { color: #dc2626; }
        """


class PDFResponseGenerator:
    """Helper class for generating HTTP responses with PDFs."""
    
    def __init__(self):
        if WEASYPRINT_AVAILABLE:
            self.generator = PDFGenerator()
            self.use_weasyprint = True
        else:
            self.generator = SimplePDFResponseGenerator()
            self.use_weasyprint = False
    
    def executive_summary_response(self) -> HttpResponse:
        """Generate HTTP response with Executive Summary PDF."""
        if self.use_weasyprint:
            pdf_content = self.generator.generate_executive_summary()
            return self._create_pdf_response(
                pdf_content, 
                'ethical_capital_executive_summary.pdf'
            )
        else:
            return self.generator.executive_summary_response()
    
    def strategy_performance_response(self, strategy_slug: Optional[str] = None) -> HttpResponse:
        """Generate HTTP response with Strategy Performance PDF."""
        if self.use_weasyprint:
            pdf_content = self.generator.generate_strategy_performance(strategy_slug)
            filename = f'ethical_capital_strategy_performance{"_" + strategy_slug if strategy_slug else ""}.pdf'
            return self._create_pdf_response(pdf_content, filename)
        else:
            return self.generator.strategy_performance_response(strategy_slug)
    
    def ddq_package_response(self) -> HttpResponse:
        """Generate HTTP response with Due Diligence Package PDF."""
        if self.use_weasyprint:
            pdf_content = self.generator.generate_ddq_package()
            return self._create_pdf_response(
                pdf_content, 
                'ethical_capital_due_diligence_package.pdf'
            )
        else:
            return self.generator.ddq_package_response()
    
    def custom_prospect_response(self, include_sections: list = None) -> HttpResponse:
        """Generate HTTP response with Custom Prospect PDF."""
        if self.use_weasyprint:
            pdf_content = self.generator.generate_custom_prospect(include_sections)
            return self._create_pdf_response(
                pdf_content, 
                'ethical_capital_investment_overview.pdf'
            )
        else:
            return self.generator.custom_prospect_response(include_sections)
    
    def _create_pdf_response(self, pdf_content: bytes, filename: str) -> HttpResponse:
        """Create HTTP response with PDF content."""
        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        response['Content-Length'] = len(pdf_content)
        return response


class BulkPDFGenerator:
    """Utility for generating multiple PDFs at once."""
    
    def __init__(self, output_directory: str):
        self.output_directory = Path(output_directory)
        self.output_directory.mkdir(parents=True, exist_ok=True)
        self.generator = PDFGenerator()
    
    def generate_all_brochures(self) -> Dict[str, str]:
        """Generate all available brochure types."""
        results = {}
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        
        try:
            # Executive Summary
            exec_path = self.output_directory / f'executive_summary_{timestamp}.pdf'
            self.generator.generate_executive_summary(str(exec_path))
            results['executive_summary'] = str(exec_path)
        except Exception as e:
            results['executive_summary_error'] = str(e)
        
        try:
            # Strategy Performance (all strategies)
            perf_path = self.output_directory / f'strategy_performance_all_{timestamp}.pdf'
            self.generator.generate_strategy_performance(output_path=str(perf_path))
            results['strategy_performance_all'] = str(perf_path)
        except Exception as e:
            results['strategy_performance_all_error'] = str(e)
        
        try:
            # Individual strategy PDFs
            strategies = self.generator.brochure_service.get_all_strategies()
            for strategy in strategies:
                slug = strategy['slug']
                strategy_path = self.output_directory / f'strategy_performance_{slug}_{timestamp}.pdf'
                self.generator.generate_strategy_performance(slug, str(strategy_path))
                results[f'strategy_{slug}'] = str(strategy_path)
        except Exception as e:
            results['individual_strategies_error'] = str(e)
        
        try:
            # Due Diligence Package
            ddq_path = self.output_directory / f'due_diligence_package_{timestamp}.pdf'
            self.generator.generate_ddq_package(str(ddq_path))
            results['due_diligence_package'] = str(ddq_path)
        except Exception as e:
            results['due_diligence_package_error'] = str(e)
        
        try:
            # Custom Prospect (default sections)
            prospect_path = self.output_directory / f'investment_overview_{timestamp}.pdf'
            self.generator.generate_custom_prospect(output_path=str(prospect_path))
            results['investment_overview'] = str(prospect_path)
        except Exception as e:
            results['investment_overview_error'] = str(e)
        
        return results
    
    def generate_strategy_specific_set(self, strategy_slug: str) -> Dict[str, str]:
        """Generate a set of PDFs focused on a specific strategy."""
        results = {}
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        
        try:
            # Strategy-specific performance brochure
            perf_path = self.output_directory / f'strategy_{strategy_slug}_performance_{timestamp}.pdf'
            self.generator.generate_strategy_performance(strategy_slug, str(perf_path))
            results['strategy_performance'] = str(perf_path)
        except Exception as e:
            results['strategy_performance_error'] = str(e)
        
        try:
            # Custom prospect brochure focused on this strategy
            prospect_path = self.output_directory / f'strategy_{strategy_slug}_overview_{timestamp}.pdf'
            self.generator.generate_custom_prospect(
                include_sections=['overview', 'strategies'], 
                output_path=str(prospect_path)
            )
            results['strategy_overview'] = str(prospect_path)
        except Exception as e:
            results['strategy_overview_error'] = str(e)
        
        try:
            # Executive summary (for context)
            exec_path = self.output_directory / f'executive_summary_{timestamp}.pdf'
            self.generator.generate_executive_summary(str(exec_path))
            results['executive_summary'] = str(exec_path)
        except Exception as e:
            results['executive_summary_error'] = str(e)
        
        return results