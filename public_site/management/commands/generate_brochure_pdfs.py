"""
Management command to generate PDF brochures from the command line.
"""

import os
from pathlib import Path
from typing import List

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from public_site.utils.pdf_generator import PDFGenerator, BulkPDFGenerator
from public_site.services.brochure_service import BrochureService


class Command(BaseCommand):
    help = 'Generate PDF brochures for marketing and client presentations'
    
    def add_arguments(self, parser):
        # Brochure type selection
        parser.add_argument(
            '--type',
            type=str,
            choices=['executive', 'performance', 'ddq', 'prospect', 'all'],
            default='all',
            help='Type of brochure to generate (default: all)'
        )
        
        # Strategy-specific options
        parser.add_argument(
            '--strategy',
            type=str,
            help='Generate brochure for specific strategy (use strategy slug)'
        )
        
        # Output directory
        parser.add_argument(
            '--output-dir',
            type=str,
            default='./brochures',
            help='Output directory for generated PDFs (default: ./brochures)'
        )
        
        # Custom prospect options
        parser.add_argument(
            '--sections',
            type=str,
            nargs='+',
            choices=['overview', 'strategies', 'team', 'ddq_summary', 'performance'],
            help='Sections to include in custom prospect brochure'
        )
        
        # Output options
        parser.add_argument(
            '--list-strategies',
            action='store_true',
            help='List available strategies and exit'
        )
        
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be generated without creating files'
        )
        
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed progress information'
        )
    
    def handle(self, *args, **options):
        # Handle list strategies option
        if options['list_strategies']:
            self._list_strategies()
            return
        
        # Setup
        self.verbosity = 2 if options['verbose'] else 1
        output_dir = Path(options['output_dir']).resolve()
        
        if options['dry_run']:
            self.stdout.write(
                self.style.WARNING(f"DRY RUN: Would generate PDFs in {output_dir}")
            )
        else:
            # Create output directory
            output_dir.mkdir(parents=True, exist_ok=True)
            self.stdout.write(f"Output directory: {output_dir}")
        
        # Initialize generators
        pdf_generator = PDFGenerator()
        bulk_generator = BulkPDFGenerator(str(output_dir)) if not options['dry_run'] else None
        
        # Generate based on type
        brochure_type = options['type']
        strategy_slug = options['strategy']
        
        try:
            if brochure_type == 'all':
                self._generate_all_brochures(bulk_generator, options['dry_run'])
            elif brochure_type == 'executive':
                self._generate_executive_summary(pdf_generator, output_dir, options['dry_run'])
            elif brochure_type == 'performance':
                self._generate_performance_brochure(pdf_generator, output_dir, strategy_slug, options['dry_run'])
            elif brochure_type == 'ddq':
                self._generate_ddq_package(pdf_generator, output_dir, options['dry_run'])
            elif brochure_type == 'prospect':
                self._generate_custom_prospect(pdf_generator, output_dir, options['sections'], options['dry_run'])
                
        except Exception as e:
            raise CommandError(f'Error generating PDF: {str(e)}')
        
        if not options['dry_run']:
            self.stdout.write(
                self.style.SUCCESS(f'PDF generation completed. Files saved to: {output_dir}')
            )
    
    def _list_strategies(self):
        """List available strategies."""
        self.stdout.write(self.style.HTTP_INFO("Available Strategies:"))
        
        try:
            service = BrochureService()
            strategies = service.get_all_strategies()
            
            if not strategies:
                self.stdout.write("No strategies found.")
                return
            
            for strategy in strategies:
                status = "✓" if strategy['performance']['ytd']['strategy'] not in ['-', 'N/A', ''] else "○"
                inception = strategy['inception_date'].strftime('%Y-%m-%d') if strategy['inception_date'] else 'N/A'
                
                self.stdout.write(
                    f"  {status} {strategy['slug']:20} | {strategy['title'][:40]:40} | Inception: {inception}"
                )
            
            self.stdout.write(f"\nTotal: {len(strategies)} strategies")
            self.stdout.write("✓ = Has performance data, ○ = No performance data")
            
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Error listing strategies: {str(e)}'))
    
    def _generate_all_brochures(self, bulk_generator, dry_run):
        """Generate all brochure types."""
        self.stdout.write("Generating all brochure types...")
        
        if dry_run:
            self.stdout.write("  • Executive Summary")
            self.stdout.write("  • Strategy Performance Report (All Strategies)")
            self.stdout.write("  • Due Diligence Package") 
            self.stdout.write("  • Investment Overview (Custom Prospect)")
            
            # List individual strategy brochures
            service = BrochureService()
            strategies = service.get_all_strategies()
            for strategy in strategies:
                self.stdout.write(f"  • Strategy Performance: {strategy['title']}")
            return
        
        results = bulk_generator.generate_all_brochures()
        
        # Report results
        success_count = 0
        error_count = 0
        
        for key, value in results.items():
            if key.endswith('_error'):
                error_count += 1
                if self.verbosity >= 2:
                    self.stderr.write(self.style.ERROR(f"Error in {key.replace('_error', '')}: {value}"))
            else:
                success_count += 1
                if self.verbosity >= 2:
                    self.stdout.write(self.style.SUCCESS(f"Generated: {Path(value).name}"))
        
        self.stdout.write(f"Successfully generated: {success_count} PDFs")
        if error_count > 0:
            self.stdout.write(self.style.WARNING(f"Errors encountered: {error_count}"))
    
    def _generate_executive_summary(self, pdf_generator, output_dir, dry_run):
        """Generate executive summary brochure."""
        self.stdout.write("Generating Executive Summary...")
        
        if dry_run:
            self.stdout.write("  • Executive Summary PDF")
            return
        
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        output_path = output_dir / f'executive_summary_{timestamp}.pdf'
        
        pdf_generator.generate_executive_summary(str(output_path))
        self.stdout.write(self.style.SUCCESS(f"Generated: {output_path.name}"))
    
    def _generate_performance_brochure(self, pdf_generator, output_dir, strategy_slug, dry_run):
        """Generate strategy performance brochure."""
        if strategy_slug:
            self.stdout.write(f"Generating Strategy Performance for: {strategy_slug}")
        else:
            self.stdout.write("Generating Strategy Performance (All Strategies)")
        
        if dry_run:
            if strategy_slug:
                self.stdout.write(f"  • Strategy Performance: {strategy_slug}")
            else:
                self.stdout.write("  • Strategy Performance: All Strategies")
            return
        
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        filename = f'strategy_performance{"_" + strategy_slug if strategy_slug else "_all"}_{timestamp}.pdf'
        output_path = output_dir / filename
        
        pdf_generator.generate_strategy_performance(strategy_slug, str(output_path))
        self.stdout.write(self.style.SUCCESS(f"Generated: {output_path.name}"))
    
    def _generate_ddq_package(self, pdf_generator, output_dir, dry_run):
        """Generate due diligence package."""
        self.stdout.write("Generating Due Diligence Package...")
        
        if dry_run:
            self.stdout.write("  • Due Diligence Package PDF")
            return
        
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        output_path = output_dir / f'due_diligence_package_{timestamp}.pdf'
        
        pdf_generator.generate_ddq_package(str(output_path))
        self.stdout.write(self.style.SUCCESS(f"Generated: {output_path.name}"))
    
    def _generate_custom_prospect(self, pdf_generator, output_dir, sections, dry_run):
        """Generate custom prospect brochure."""
        sections_text = ', '.join(sections) if sections else 'default'
        self.stdout.write(f"Generating Custom Prospect Brochure (sections: {sections_text})...")
        
        if dry_run:
            self.stdout.write(f"  • Custom Prospect PDF with sections: {sections_text}")
            return
        
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        output_path = output_dir / f'investment_overview_{timestamp}.pdf'
        
        pdf_generator.generate_custom_prospect(sections, str(output_path))
        self.stdout.write(self.style.SUCCESS(f"Generated: {output_path.name}"))


# Example usage comments for documentation
"""
Example usage:

# List available strategies
python manage.py generate_brochure_pdfs --list-strategies

# Generate all brochures
python manage.py generate_brochure_pdfs --type all --output-dir ./marketing_materials

# Generate executive summary only
python manage.py generate_brochure_pdfs --type executive

# Generate performance brochure for specific strategy
python manage.py generate_brochure_pdfs --type performance --strategy sustainable-equity

# Generate custom prospect brochure with specific sections
python manage.py generate_brochure_pdfs --type prospect --sections overview strategies team

# Dry run to see what would be generated
python manage.py generate_brochure_pdfs --type all --dry-run --verbose

# Generate DDQ package
python manage.py generate_brochure_pdfs --type ddq --output-dir ./due_diligence
"""