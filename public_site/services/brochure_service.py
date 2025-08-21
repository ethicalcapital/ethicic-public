"""
Brochure generation service for creating professional PDF marketing materials.
Aggregates content from Wagtail pages and provides data for PDF templates.
"""

from datetime import datetime, date
from typing import Dict, List, Optional, Any
from django.conf import settings
from django.utils import timezone
from wagtail.models import Site

from ..models import HomePage, StrategyPage, PRIDDQPage, AboutPage
from ..utils.performance_calculator import (
    update_performance_from_monthly_data,
    format_percentage,
    parse_percentage,
)


class BrochureService:
    """Service for aggregating content and generating brochure data."""
    
    def __init__(self):
        self.site = Site.objects.filter(is_default_site=True).first()
        
    def get_firm_overview(self) -> Dict[str, Any]:
        """Get firm overview information from HomePage."""
        home_page = HomePage.objects.live().first()
        
        if not home_page:
            return self._get_default_firm_overview()
            
        return {
            'firm_name': 'Ethical Capital',
            'tagline': getattr(home_page, 'hero_subtitle', ''),
            'description': getattr(home_page, 'hero_description', ''),
            'philosophy': getattr(home_page, 'philosophy_content', ''),
            'principles': self._extract_principles(home_page),
            'key_statistics': self._extract_key_statistics(home_page),
            'founded_year': getattr(home_page, 'founded_year', ''),
            'aum': getattr(home_page, 'aum_amount', ''),
            'client_count': getattr(home_page, 'client_count', ''),
        }
    
    def get_team_information(self) -> Dict[str, Any]:
        """Get team information from AboutPage."""
        about_page = AboutPage.objects.live().first()
        
        if not about_page:
            return {'team_members': [], 'company_history': ''}
            
        return {
            'team_members': self._extract_team_members(about_page),
            'company_history': getattr(about_page, 'company_history', ''),
            'timeline': self._extract_timeline(about_page),
        }
    
    def get_all_strategies(self) -> List[Dict[str, Any]]:
        """Get all published strategy pages with performance data."""
        strategies = StrategyPage.objects.live().order_by('title')
        
        strategy_data = []
        for strategy in strategies:
            # Update performance data if monthly returns are available
            if strategy.monthly_returns:
                update_performance_from_monthly_data(strategy, strategy.monthly_returns)
            
            strategy_info = self._format_strategy_data(strategy)
            strategy_data.append(strategy_info)
            
        return strategy_data
    
    def get_strategy_by_slug(self, slug: str) -> Optional[Dict[str, Any]]:
        """Get specific strategy by slug."""
        try:
            strategy = StrategyPage.objects.live().get(slug=slug)
            
            # Update performance data
            if strategy.monthly_returns:
                update_performance_from_monthly_data(strategy, strategy.monthly_returns)
            
            return self._format_strategy_data(strategy)
        except StrategyPage.DoesNotExist:
            return None
    
    def get_ddq_content(self) -> Dict[str, Any]:
        """Get Due Diligence Questionnaire content."""
        ddq_page = PRIDDQPage.objects.live().first()
        
        if not ddq_page:
            return self._get_default_ddq_content()
            
        return {
            'title': ddq_page.title,
            'subtitle': getattr(ddq_page, 'hero_subtitle', ''),
            'updated_at': getattr(ddq_page, 'updated_at', ''),
            'executive_summary': getattr(ddq_page, 'executive_summary', ''),
            'sections': {
                'strategy_governance': {
                    'title': getattr(ddq_page, 'section_title_strategy', 'Strategy & Governance'),
                    'content': getattr(ddq_page, 'strategy_governance_content', ''),
                },
                'esg_integration': {
                    'title': getattr(ddq_page, 'section_title_esg', 'ESG Integration'),
                    'content': getattr(ddq_page, 'esg_integration_content', ''),
                },
                'stewardship': {
                    'title': getattr(ddq_page, 'section_title_stewardship', 'Stewardship'),
                    'content': getattr(ddq_page, 'stewardship_content', ''),
                },
                'transparency': {
                    'title': getattr(ddq_page, 'section_title_transparency', 'Transparency'),
                    'content': getattr(ddq_page, 'transparency_content', ''),
                },
                'climate': {
                    'title': getattr(ddq_page, 'section_title_climate', 'Climate & Environment'),
                    'content': getattr(ddq_page, 'climate_content', ''),
                },
                'reporting': {
                    'title': 'Reporting & Verification',
                    'content': getattr(ddq_page, 'reporting_verification_content', ''),
                },
                'additional': {
                    'title': 'Additional Information',
                    'content': getattr(ddq_page, 'additional_content', ''),
                },
            }
        }
    
    def get_executive_summary_data(self) -> Dict[str, Any]:
        """Get data for Executive Summary brochure."""
        return {
            'firm_overview': self.get_firm_overview(),
            'team_info': self.get_team_information(),
            'key_strategies': self.get_all_strategies()[:3],  # Top 3 strategies
            'generated_date': timezone.now().strftime('%B %d, %Y'),
        }
    
    def get_strategy_performance_data(self, strategy_slug: str = None) -> Dict[str, Any]:
        """Get data for Strategy Performance brochure."""
        if strategy_slug:
            strategies = [self.get_strategy_by_slug(strategy_slug)]
            strategies = [s for s in strategies if s is not None]
        else:
            strategies = self.get_all_strategies()
            
        return {
            'firm_overview': self.get_firm_overview(),
            'strategies': strategies,
            'performance_disclaimer': self._get_performance_disclaimer(),
            'generated_date': timezone.now().strftime('%B %d, %Y'),
        }
    
    def get_ddq_package_data(self) -> Dict[str, Any]:
        """Get data for Due Diligence Package."""
        return {
            'firm_overview': self.get_firm_overview(),
            'ddq_content': self.get_ddq_content(),
            'team_info': self.get_team_information(),
            'strategies': self.get_all_strategies(),
            'generated_date': timezone.now().strftime('%B %d, %Y'),
        }
    
    def get_custom_prospect_data(self, include_sections: List[str] = None) -> Dict[str, Any]:
        """Get data for Custom Prospect brochure."""
        if include_sections is None:
            include_sections = ['overview', 'strategies', 'team', 'ddq_summary']
            
        data = {
            'generated_date': timezone.now().strftime('%B %d, %Y'),
        }
        
        if 'overview' in include_sections:
            data['firm_overview'] = self.get_firm_overview()
            
        if 'strategies' in include_sections:
            data['strategies'] = self.get_all_strategies()
            
        if 'team' in include_sections:
            data['team_info'] = self.get_team_information()
            
        if 'ddq_summary' in include_sections:
            ddq_data = self.get_ddq_content()
            data['ddq_summary'] = {
                'executive_summary': ddq_data['executive_summary'],
                'key_sections': ['esg_integration', 'stewardship', 'transparency'],
            }
            
        if 'performance' in include_sections:
            data['performance_disclaimer'] = self._get_performance_disclaimer()
            
        return data
    
    def _format_strategy_data(self, strategy: StrategyPage) -> Dict[str, Any]:
        """Format strategy page data for brochure use."""
        return {
            'title': strategy.title,
            'slug': strategy.slug,
            'subtitle': strategy.strategy_subtitle,
            'description': strategy.strategy_description,
            'label': strategy.strategy_label,
            'risk_level': strategy.risk_level,
            'ethical_implementation': strategy.ethical_implementation,
            'holdings_count': strategy.holdings_count,
            'best_for': strategy.best_for,
            'cash_allocation': strategy.cash_allocation,
            'benchmark_name': strategy.benchmark_name,
            'inception_date': strategy.inception_date,
            'performance': {
                'ytd': {
                    'strategy': strategy.ytd_return,
                    'benchmark': strategy.ytd_benchmark,
                    'difference': strategy.ytd_difference,
                },
                'one_year': {
                    'strategy': strategy.one_year_return,
                    'benchmark': strategy.one_year_benchmark,
                    'difference': strategy.one_year_difference,
                },
                'three_year': {
                    'strategy': strategy.three_year_return,
                    'benchmark': strategy.three_year_benchmark,
                    'difference': strategy.three_year_difference,
                },
                'since_inception': {
                    'strategy': strategy.since_inception_return,
                    'benchmark': strategy.since_inception_benchmark,
                    'difference': strategy.since_inception_difference,
                },
            },
            'portfolio_content': strategy.portfolio_content,
            'commentary': {
                'title': strategy.commentary_title,
                'content': strategy.commentary_content,
            },
            'process': {
                'title': strategy.process_title,
                'content': strategy.process_content,
            },
            'documents': {
                'title': strategy.documents_title,
                'content': strategy.documents_content,
            },
            'notes': {
                'overweights': strategy.overweights_note,
                'exclusions': strategy.exclusions_note,
                'healthcare_exclusion': strategy.healthcare_exclusion_note,
            },
            'performance_last_updated': strategy.performance_last_updated,
        }
    
    def _extract_principles(self, home_page) -> List[str]:
        """Extract principles from home page content."""
        # This would need to be customized based on how principles are stored
        # For now, return empty list - can be enhanced based on actual data structure
        return []
    
    def _extract_key_statistics(self, home_page) -> List[Dict[str, str]]:
        """Extract key statistics from home page."""
        # Extract from StreamField or specific fields
        # This is a placeholder implementation
        return []
    
    def _extract_team_members(self, about_page) -> List[Dict[str, Any]]:
        """Extract team member information."""
        # This would extract from StreamField or related models
        # Placeholder implementation
        return []
    
    def _extract_timeline(self, about_page) -> List[Dict[str, Any]]:
        """Extract company timeline."""
        # Placeholder implementation
        return []
    
    def _get_default_firm_overview(self) -> Dict[str, Any]:
        """Default firm overview when HomePage is not available."""
        return {
            'firm_name': 'Ethical Capital',
            'tagline': 'Ethical Investment Management',
            'description': 'SEC-regulated investment advisory firm specializing in ethical capital allocation.',
            'philosophy': '',
            'principles': [],
            'key_statistics': [],
            'founded_year': '',
            'aum': '',
            'client_count': '',
        }
    
    def _get_default_ddq_content(self) -> Dict[str, Any]:
        """Default DDQ content when PRIDDQPage is not available."""
        return {
            'title': 'Due Diligence Questionnaire',
            'subtitle': 'PRI Due Diligence Questionnaire Response',
            'updated_at': '',
            'executive_summary': '',
            'sections': {},
        }
    
    def _get_performance_disclaimer(self) -> str:
        """Get standard performance disclaimer."""
        return """
        Past performance is not indicative of future results. All investments involve risk, 
        including potential loss of principal. Performance data represents composite returns 
        and may not reflect the experience of individual client accounts. Please refer to 
        our Form ADV Part 2A for additional important disclosures.
        """


class BrochureContentAggregator:
    """Helper class for advanced content aggregation and formatting."""
    
    def __init__(self, brochure_service: BrochureService):
        self.service = brochure_service
    
    def format_performance_table(self, strategies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format performance data for table display."""
        table_data = []
        
        for strategy in strategies:
            perf = strategy['performance']
            table_data.append({
                'strategy_name': strategy['title'],
                'benchmark': strategy['benchmark_name'],
                'ytd': {
                    'strategy': perf['ytd']['strategy'],
                    'benchmark': perf['ytd']['benchmark'],
                    'difference': perf['ytd']['difference'],
                },
                'one_year': {
                    'strategy': perf['one_year']['strategy'],
                    'benchmark': perf['one_year']['benchmark'],
                    'difference': perf['one_year']['difference'],
                },
                'three_year': {
                    'strategy': perf['three_year']['strategy'],
                    'benchmark': perf['three_year']['benchmark'],
                    'difference': perf['three_year']['difference'],
                },
                'since_inception': {
                    'strategy': perf['since_inception']['strategy'],
                    'benchmark': perf['since_inception']['benchmark'],
                    'difference': perf['since_inception']['difference'],
                },
            })
            
        return table_data
    
    def get_top_performing_strategies(self, strategies: List[Dict[str, Any]], period: str = 'ytd') -> List[Dict[str, Any]]:
        """Get top performing strategies for a given period."""
        def get_return_value(strategy):
            perf_str = strategy['performance'][period]['strategy']
            if not perf_str or perf_str in ['-', 'N/A']:
                return -999.0  # Sort non-available data to bottom
            return parse_percentage(perf_str)
        
        sorted_strategies = sorted(strategies, key=get_return_value, reverse=True)
        return sorted_strategies
    
    def calculate_aggregate_statistics(self, strategies: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate aggregate statistics across all strategies."""
        if not strategies:
            return {}
        
        total_strategies = len(strategies)
        active_strategies = len([s for s in strategies if s['performance']['ytd']['strategy'] not in ['-', 'N/A', '']])
        
        # Calculate average returns where available
        ytd_returns = []
        for strategy in strategies:
            ytd_str = strategy['performance']['ytd']['strategy']
            if ytd_str and ytd_str not in ['-', 'N/A']:
                ytd_returns.append(parse_percentage(ytd_str))
        
        avg_ytd = format_percentage(sum(ytd_returns) / len(ytd_returns)) if ytd_returns else 'N/A'
        
        return {
            'total_strategies': total_strategies,
            'active_strategies': active_strategies,
            'average_ytd_return': avg_ytd,
        }