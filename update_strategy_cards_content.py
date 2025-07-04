#!/usr/bin/env python
"""
Update strategy cards to match exact content from strategy pages
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ethicic.settings')
django.setup()

from public_site.models import SolutionsPage, StrategyCard

def update_strategy_cards():
    """Update strategy cards to match actual strategy page content."""
    print("Updating strategy cards to match strategy pages...")
    
    # Get the solutions page
    solutions_page = SolutionsPage.objects.first()
    if not solutions_page:
        print("ERROR: No SolutionsPage found!")
        return
    
    # Clear existing strategy cards
    StrategyCard.objects.filter(page=solutions_page).delete()
    print("Cleared existing strategy cards")
    
    # Create strategy cards with exact content from strategy pages
    strategies = [
        {
            'icon': '📈',
            'title': 'Growth Strategy',
            'description': 'Our Flagship Approach - High-conviction portfolios where our ethical criteria can be fully implemented without compromise.',
            'features': 'Focus: 15-25 Companies\nScreening: Full Implementation\nManagement: Active & Continuous\nOwnership: Direct Securities',
            'url': '/strategies/growth/'
        },
        {
            'icon': '💰',
            'title': 'Income Strategy', 
            'description': 'Ethics Meets Yield - The same rigorous ethical screening applied to income-generating securities.',
            'features': 'Focus: Income Generation\nScreening: Full Implementation\nManagement: Active & Continuous\nOwnership: Direct Securities',
            'url': '/strategies/income/'
        },
        {
            'icon': '🎯',
            'title': 'Diversification Strategy',
            'description': 'Discretionary Management - We identify and manage allocations to external funds whose approaches align with ethical investing principles.',
            'features': 'Focus: Broader Markets\nScreening: Ethical Alignment\nManagement: Active & Continuous\nOwnership: External Funds',
            'url': '/strategies/diversification/'
        }
    ]
    
    for i, strategy in enumerate(strategies):
        StrategyCard.objects.create(
            page=solutions_page,
            sort_order=i,
            **strategy
        )
    
    print(f"Created {len(strategies)} updated strategy cards")
    
    # Save and republish the page
    solutions_page.save_revision().publish()
    print("Solutions page republished with updated strategy content")

if __name__ == "__main__":
    update_strategy_cards()
    print("\n✅ Strategy cards updated to match strategy pages!")
    print("🔗 Updated content:")
    print("  📈 Growth: Our Flagship Approach (15-25 companies, full screening)")
    print("  💰 Income: Ethics Meets Yield (income generation, full screening)")  
    print("  🎯 Diversification: Discretionary Management (external funds, ethical alignment)")