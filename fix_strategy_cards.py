#!/usr/bin/env python
"""
Fix strategy cards to match actual strategies: Growth, Income, Diversification
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ethicic.settings')
django.setup()

from public_site.models import SolutionsPage, StrategyCard

def fix_strategy_cards():
    """Update strategy cards to match actual strategies."""
    print("Fixing strategy cards...")
    
    # Get the solutions page
    solutions_page = SolutionsPage.objects.first()
    if not solutions_page:
        print("ERROR: No SolutionsPage found!")
        return
    
    # Clear existing strategy cards
    StrategyCard.objects.filter(page=solutions_page).delete()
    print("Cleared existing strategy cards")
    
    # Create correct strategy cards
    strategies = [
        {
            'icon': '📈',
            'title': 'Growth Strategy',
            'description': 'Long-term capital appreciation through carefully selected growth companies that align with our ethical criteria.',
            'features': 'High-conviction portfolio\nFocus on sustainable growth\nRigorous ethical screening\nQuarterly rebalancing',
            'url': '/strategies/growth/'
        },
        {
            'icon': '💰',
            'title': 'Income Strategy', 
            'description': 'Regular income generation through dividend-paying stocks and ethical fixed-income securities.',
            'features': 'Dividend-focused equity\nEthical bond allocation\nIncome optimization\nRisk management',
            'url': '/strategies/income/'
        },
        {
            'icon': '🎯',
            'title': 'Diversification Strategy',
            'description': 'Balanced portfolio approach that spreads risk across multiple asset classes while maintaining ethical standards.',
            'features': 'Multi-asset allocation\nRisk diversification\nEthical screening\nRegular rebalancing',
            'url': '/strategies/diversification/'
        }
    ]
    
    for i, strategy in enumerate(strategies):
        StrategyCard.objects.create(
            page=solutions_page,
            sort_order=i,
            **strategy
        )
    
    print(f"Created {len(strategies)} corrected strategy cards")
    
    # Save and republish the page
    solutions_page.save_revision().publish()
    print("Solutions page republished with corrected strategy cards")

if __name__ == "__main__":
    fix_strategy_cards()
    print("\n✅ Strategy cards fixed!")
    print("🔗 Now linking to:")
    print("  - Growth Strategy: /strategies/growth/")
    print("  - Income Strategy: /strategies/income/")  
    print("  - Diversification Strategy: /strategies/diversification/")