"""
Simple PDF generation using ReportLab as a fallback when WeasyPrint isn't available.
This provides basic PDF functionality for brochure generation.
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

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.platypus.frames import Frame
from reportlab.platypus.doctemplate import PageTemplate, BaseDocTemplate
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

from ..services.brochure_service import BrochureService


class SimplePDFGenerator:
    """Simple PDF generator using ReportLab for basic brochure creation."""
    
    def __init__(self):
        self.brochure_service = BrochureService()
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles."""
        # Brand colors
        purple = HexColor('#7c3aed')
        teal = HexColor('#0d9488')
        gray = HexColor('#374151')
        
        # Title style
        self.styles.add(ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            spaceAfter=20,
            textColor=purple,
            alignment=TA_CENTER,
        ))
        
        # Heading 1
        self.styles.add(ParagraphStyle(
            'CustomHeading1',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=12,
            textColor=purple,
        ))
        
        # Heading 2
        self.styles.add(ParagraphStyle(
            'CustomHeading2',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=8,
            textColor=gray,
        ))
        
        # Body text
        self.styles.add(ParagraphStyle(
            'CustomBody',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=8,
            alignment=TA_JUSTIFY,
        ))
        
        # Subtitle
        self.styles.add(ParagraphStyle(
            'CustomSubtitle',
            parent=self.styles['Normal'],
            fontSize=14,
            spaceAfter=12,
            textColor=teal,
            alignment=TA_CENTER,
        ))
    
    def generate_executive_summary(self, output_path: Optional[str] = None) -> bytes:
        """Generate Executive Summary PDF brochure."""
        data = self.brochure_service.get_executive_summary_data()
        return self._generate_simple_pdf(
            data=data,
            output_path=output_path,
            filename='ethical_capital_executive_summary.pdf',
            pdf_type='executive'
        )
    
    def generate_strategy_performance(self, strategy_slug: Optional[str] = None, output_path: Optional[str] = None) -> bytes:
        """Generate Strategy Performance PDF brochure."""
        data = self.brochure_service.get_strategy_performance_data(strategy_slug)
        filename = f'ethical_capital_strategy_performance{"_" + strategy_slug if strategy_slug else ""}.pdf'
        return self._generate_simple_pdf(
            data=data,
            output_path=output_path,
            filename=filename,
            pdf_type='performance'
        )
    
    def generate_ddq_package(self, output_path: Optional[str] = None) -> bytes:
        """Generate Due Diligence Package PDF."""
        data = self.brochure_service.get_ddq_package_data()
        return self._generate_simple_pdf(
            data=data,
            output_path=output_path,
            filename='ethical_capital_due_diligence_package.pdf',
            pdf_type='ddq'
        )
    
    def generate_custom_prospect(self, include_sections: list = None, output_path: Optional[str] = None) -> bytes:
        """Generate Custom Prospect PDF brochure."""
        data = self.brochure_service.get_custom_prospect_data(include_sections)
        return self._generate_simple_pdf(
            data=data,
            output_path=output_path,
            filename='ethical_capital_investment_overview.pdf',
            pdf_type='prospect'
        )
    
    def _generate_simple_pdf(self, data: Dict[str, Any], output_path: Optional[str] = None, 
                           filename: str = 'brochure.pdf', pdf_type: str = 'generic') -> bytes:
        """
        Core PDF generation method using ReportLab.
        """
        if output_path:
            pdf_file = output_path
        else:
            pdf_file = BytesIO()
        
        # Create PDF document
        doc = SimpleDocTemplate(
            pdf_file,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        # Build story (content)
        story = []
        
        # Add content based on PDF type
        if pdf_type == 'executive':
            story.extend(self._build_executive_summary_content(data))
        elif pdf_type == 'performance':
            story.extend(self._build_performance_content(data))
        elif pdf_type == 'ddq':
            story.extend(self._build_ddq_content(data))
        elif pdf_type == 'prospect':
            story.extend(self._build_prospect_content(data))
        
        # Build PDF
        doc.build(story)
        
        if output_path:
            with open(output_path, 'rb') as file:
                return file.read()
        else:
            return pdf_file.getvalue()
    
    def _build_executive_summary_content(self, data: Dict[str, Any]) -> list:
        """Build content for Executive Summary PDF."""
        story = []
        
        # Title page
        story.append(Paragraph("Ethical Capital", self.styles['CustomTitle']))
        story.append(Paragraph("Executive Summary", self.styles['CustomSubtitle']))
        story.append(Paragraph(f"Generated: {data['generated_date']}", self.styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Firm overview
        if 'firm_overview' in data:
            firm = data['firm_overview']
            story.append(Paragraph("Firm Overview", self.styles['CustomHeading1']))
            
            if firm.get('description'):
                story.append(Paragraph(self._clean_html(firm['description']), self.styles['CustomBody']))
            
            if firm.get('philosophy'):
                story.append(Paragraph("Investment Philosophy", self.styles['CustomHeading2']))
                story.append(Paragraph(self._clean_html(firm['philosophy']), self.styles['CustomBody']))
        
        # Key strategies
        if 'key_strategies' in data and data['key_strategies']:
            story.append(PageBreak())
            story.append(Paragraph("Key Investment Strategies", self.styles['CustomHeading1']))
            
            for strategy in data['key_strategies']:
                story.append(Paragraph(strategy['title'], self.styles['CustomHeading2']))
                
                if strategy.get('subtitle'):
                    story.append(Paragraph(strategy['subtitle'], self.styles['Normal']))
                
                if strategy.get('description'):
                    story.append(Paragraph(self._clean_html(strategy['description']), self.styles['CustomBody']))
                
                # Performance table
                if strategy.get('performance'):
                    perf_data = [['Period', 'Strategy', 'Benchmark', 'Difference']]
                    perf = strategy['performance']
                    
                    if perf.get('ytd', {}).get('strategy') and perf['ytd']['strategy'] != '-':
                        perf_data.append(['YTD', perf['ytd']['strategy'], perf['ytd']['benchmark'], perf['ytd']['difference']])
                    
                    if perf.get('one_year', {}).get('strategy') and perf['one_year']['strategy'] != '-':
                        perf_data.append(['1 Year', perf['one_year']['strategy'], perf['one_year']['benchmark'], perf['one_year']['difference']])
                    
                    if len(perf_data) > 1:
                        table = Table(perf_data)
                        table.setStyle(TableStyle([
                            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#f8fafc')),
                            ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#374151')),
                            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('FONTSIZE', (0, 0), (-1, 0), 10),
                            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                            ('BACKGROUND', (0, 1), (-1, -1), HexColor('#ffffff')),
                            ('GRID', (0, 0), (-1, -1), 1, HexColor('#e5e7eb'))
                        ]))
                        story.append(table)
                
                story.append(Spacer(1, 12))
        
        # Team information
        if 'team_info' in data and data['team_info'].get('team_members'):
            story.append(PageBreak())
            story.append(Paragraph("Leadership Team", self.styles['CustomHeading1']))
            
            for member in data['team_info']['team_members']:
                story.append(Paragraph(member['name'], self.styles['CustomHeading2']))
                if member.get('title'):
                    story.append(Paragraph(member['title'], self.styles['Normal']))
                if member.get('bio'):
                    story.append(Paragraph(self._clean_html(member['bio']), self.styles['CustomBody']))
                story.append(Spacer(1, 8))
        
        # Footer
        story.append(PageBreak())
        story.append(Paragraph("Contact Information", self.styles['CustomHeading1']))
        story.append(Paragraph("Ethical Capital", self.styles['CustomHeading2']))
        story.append(Paragraph("Email: info@ethicic.com", self.styles['CustomBody']))
        story.append(Paragraph("Website: www.ethicic.com", self.styles['CustomBody']))
        
        return story
    
    def _build_performance_content(self, data: Dict[str, Any]) -> list:
        """Build content for Strategy Performance PDF."""
        story = []
        
        # Title page
        story.append(Paragraph("Ethical Capital", self.styles['CustomTitle']))
        story.append(Paragraph("Strategy Performance Report", self.styles['CustomSubtitle']))
        story.append(Paragraph(f"Generated: {data['generated_date']}", self.styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Performance summary table
        if 'strategies' in data and data['strategies']:
            story.append(Paragraph("Performance Summary", self.styles['CustomHeading1']))
            
            table_data = [['Strategy', 'YTD', '1 Year', '3 Year', 'Since Inception']]
            
            for strategy in data['strategies']:
                perf = strategy['performance']
                row = [
                    strategy['title'],
                    perf.get('ytd', {}).get('strategy', '-'),
                    perf.get('one_year', {}).get('strategy', '-'),
                    perf.get('three_year', {}).get('strategy', '-'),
                    perf.get('since_inception', {}).get('strategy', '-'),
                ]
                table_data.append(row)
            
            table = Table(table_data, colWidths=[2*inch, inch, inch, inch, inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#f8fafc')),
                ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#374151')),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), HexColor('#ffffff')),
                ('GRID', (0, 0), (-1, -1), 1, HexColor('#e5e7eb'))
            ]))
            story.append(table)
            story.append(Spacer(1, 20))
            
            # Detailed strategy information
            for strategy in data['strategies']:
                story.append(PageBreak())
                story.append(Paragraph(strategy['title'], self.styles['CustomHeading1']))
                
                if strategy.get('subtitle'):
                    story.append(Paragraph(strategy['subtitle'], self.styles['Normal']))
                
                if strategy.get('description'):
                    story.append(Paragraph(self._clean_html(strategy['description']), self.styles['CustomBody']))
                
                # Strategy characteristics
                chars = []
                if strategy.get('risk_level'):
                    chars.append(f"Risk Level: {strategy['risk_level']}")
                if strategy.get('benchmark_name'):
                    chars.append(f"Benchmark: {strategy['benchmark_name']}")
                if strategy.get('holdings_count'):
                    chars.append(f"Holdings: {strategy['holdings_count']}")
                
                if chars:
                    story.append(Paragraph(" | ".join(chars), self.styles['Normal']))
                
                story.append(Spacer(1, 12))
        
        return story
    
    def _build_ddq_content(self, data: Dict[str, Any]) -> list:
        """Build content for DDQ Package PDF."""
        story = []
        
        # Title page
        story.append(Paragraph("Ethical Capital", self.styles['CustomTitle']))
        story.append(Paragraph("Due Diligence Package", self.styles['CustomSubtitle']))
        story.append(Paragraph(f"Generated: {data['generated_date']}", self.styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Firm overview
        if 'firm_overview' in data:
            story.append(Paragraph("Firm Overview", self.styles['CustomHeading1']))
            firm = data['firm_overview']
            if firm.get('description'):
                story.append(Paragraph(self._clean_html(firm['description']), self.styles['CustomBody']))
        
        # DDQ content
        if 'ddq_content' in data:
            ddq = data['ddq_content']
            
            if ddq.get('executive_summary'):
                story.append(PageBreak())
                story.append(Paragraph("Executive Summary", self.styles['CustomHeading1']))
                story.append(Paragraph(self._clean_html(ddq['executive_summary']), self.styles['CustomBody']))
            
            # DDQ sections
            if ddq.get('sections'):
                for section_key, section_data in ddq['sections'].items():
                    if section_data.get('content'):
                        story.append(PageBreak())
                        story.append(Paragraph(section_data['title'], self.styles['CustomHeading1']))
                        story.append(Paragraph(self._clean_html(section_data['content']), self.styles['CustomBody']))
        
        return story
    
    def _build_prospect_content(self, data: Dict[str, Any]) -> list:
        """Build content for Custom Prospect PDF."""
        story = []
        
        # Title page
        story.append(Paragraph("Ethical Capital", self.styles['CustomTitle']))
        story.append(Paragraph("Investment Overview", self.styles['CustomSubtitle']))
        story.append(Paragraph(f"Generated: {data['generated_date']}", self.styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Firm overview if included
        if 'firm_overview' in data:
            story.append(Paragraph("About Our Firm", self.styles['CustomHeading1']))
            firm = data['firm_overview']
            if firm.get('description'):
                story.append(Paragraph(self._clean_html(firm['description']), self.styles['CustomBody']))
        
        # Strategies if included
        if 'strategies' in data and data['strategies']:
            story.append(PageBreak())
            story.append(Paragraph("Investment Strategies", self.styles['CustomHeading1']))
            
            for strategy in data['strategies']:
                story.append(Paragraph(strategy['title'], self.styles['CustomHeading2']))
                if strategy.get('subtitle'):
                    story.append(Paragraph(strategy['subtitle'], self.styles['Normal']))
                if strategy.get('description'):
                    story.append(Paragraph(self._clean_html(strategy['description']), self.styles['CustomBody']))
                story.append(Spacer(1, 8))
        
        return story
    
    def _clean_html(self, html_content: str) -> str:
        """Clean HTML content for ReportLab."""
        if not html_content:
            return ""
        
        # Simple HTML cleaning - remove tags but keep text
        import re
        # Remove HTML tags
        clean = re.sub('<.*?>', '', html_content)
        # Replace HTML entities
        clean = clean.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
        clean = clean.replace('&quot;', '"').replace('&#39;', "'")
        return clean.strip()


class SimplePDFResponseGenerator:
    """Helper class for generating HTTP responses with simple PDFs."""
    
    def __init__(self):
        self.generator = SimplePDFGenerator()
    
    def executive_summary_response(self) -> HttpResponse:
        """Generate HTTP response with Executive Summary PDF."""
        pdf_content = self.generator.generate_executive_summary()
        return self._create_pdf_response(
            pdf_content, 
            'ethical_capital_executive_summary.pdf'
        )
    
    def strategy_performance_response(self, strategy_slug: Optional[str] = None) -> HttpResponse:
        """Generate HTTP response with Strategy Performance PDF."""
        pdf_content = self.generator.generate_strategy_performance(strategy_slug)
        filename = f'ethical_capital_strategy_performance{"_" + strategy_slug if strategy_slug else ""}.pdf'
        return self._create_pdf_response(pdf_content, filename)
    
    def ddq_package_response(self) -> HttpResponse:
        """Generate HTTP response with Due Diligence Package PDF."""
        pdf_content = self.generator.generate_ddq_package()
        return self._create_pdf_response(
            pdf_content, 
            'ethical_capital_due_diligence_package.pdf'
        )
    
    def custom_prospect_response(self, include_sections: list = None) -> HttpResponse:
        """Generate HTTP response with Custom Prospect PDF."""
        pdf_content = self.generator.generate_custom_prospect(include_sections)
        return self._create_pdf_response(
            pdf_content, 
            'ethical_capital_investment_overview.pdf'
        )
    
    def _create_pdf_response(self, pdf_content: bytes, filename: str) -> HttpResponse:
        """Create HTTP response with PDF content."""
        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        response['Content-Length'] = len(pdf_content)
        return response