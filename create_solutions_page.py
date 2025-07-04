#!/usr/bin/env python
"""
Create proper SolutionsPage to replace the current legalpage
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ethicic.settings')
django.setup()

from wagtail.models import Page
from public_site.models import SolutionsPage, HomePage
from django.utils import timezone

def create_solutions_page():
    """Create or update the SolutionsPage."""
    print("Creating proper SolutionsPage...")
    
    # Get the home page as parent
    home_page = HomePage.objects.first()
    if not home_page:
        print("ERROR: No home page found!")
        return
    
    # Check if SolutionsPage already exists
    existing_page = SolutionsPage.objects.first()
    
    if existing_page:
        print(f"Updating existing SolutionsPage: {existing_page.title}")
        page = existing_page
    else:
        print("Creating new SolutionsPage...")
        
        # Create new page
        page = SolutionsPage(
            title="Investment Solutions",
            slug="solutions-new",  # Use different slug initially
            live=True,
            first_published_at=timezone.now()
        )
        
        # Add as child of home page
        home_page.add_child(instance=page)
    
    # Update content
    page.hero_title = "Investment Solutions"
    page.hero_subtitle = "Ethical investment strategies tailored for individuals, institutions, and investment advisers."
    page.hero_description = """<p>Whether you're an individual investor, institutional client, or investment adviser, we provide sophisticated ethical investment solutions that align your portfolio with your principles without compromising on performance.</p>"""
    
    # Strategies section
    page.strategies_section_title = "Three Core Strategies, Infinite Possibilities"
    page.strategies_intro = "Our investment solutions are built around three core strategies, tailored to three distinct audiences, and delivered through multiple channels to meet you where you are."
    
    # Individuals section
    page.individuals_title = "For Individual Investors"
    page.individuals_content = """<p>Take your first step toward ethical investing or jump in with both feet. Our personalized approach helps you align your investments with your values while achieving your financial goals.</p>
    
<p><strong>What we offer:</strong></p>
<ul>
<li>Concentrated ethical portfolios that exclude 57% of the S&P 500</li>
<li>Transparent screening criteria publicly available on GitHub</li>
<li>Direct access to our investment team</li>
<li>Quarterly reporting with real impact stories</li>
</ul>

<p><a href="/onboarding/" class="garden-action">Get Started →</a></p>"""
    
    # Institutions section
    page.institutions_title = "For Institutional Investors"
    page.institutions_content = """<p>Scalable ethical investment solutions for endowments, pension funds, and institutional clients who require sophisticated strategies at institutional scale.</p>
    
<p><strong>Our institutional capabilities:</strong></p>
<ul>
<li>Custom investment mandates and reporting</li>
<li>Comprehensive due diligence documentation</li>
<li>Integration with existing operational systems</li>
<li>Stewardship and proxy voting when applicable</li>
</ul>

<p><a href="/institutions/" class="garden-action">Learn More →</a></p>"""
    
    # Advisors section
    page.advisors_title = "For Investment Advisers"
    page.advisors_content = """<p>Partner with us to serve clients who want their portfolios to align with their principles. We provide the specialized research, proven strategies, and operational support you need.</p>
    
<p><strong>Adviser partnership benefits:</strong></p>
<ul>
<li>White-label investment strategies and reporting</li>
<li>Comprehensive research and due diligence support</li>
<li>Client education materials and resources</li>
<li>Flexible fee structures and minimum investments</li>
</ul>

<p><a href="/advisers/" class="garden-action">Partner With Us →</a></p>"""
    
    # Call to action
    page.cta_title = "Ready to Align Your Investments with Your Values?"
    page.cta_description = """<p>Let's find the perfect solution for your needs. Contact us to discuss how we can help you achieve your investment goals while staying true to your values.</p>
    
<p><a href="/consultation/" class="garden-action garden-action--primary">Schedule a Consultation</a></p>"""
    
    # Save the page
    page.save()
    
    print(f"SolutionsPage {'updated' if existing_page else 'created'} successfully!")
    print(f"URL: {page.url}")
    return page

def create_strategy_cards(solutions_page):
    """Create strategy cards for the solutions page."""
    print("Creating strategy cards...")
    
    from public_site.models import StrategyCard
    
    # Clear existing strategy cards
    StrategyCard.objects.filter(page=solutions_page).delete()
    
    # Create strategy cards
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
            'icon': '⚖️',
            'title': 'Value Equity Strategy',
            'description': 'Fundamental value investing combined with comprehensive ESG analysis for long-term wealth building.',
            'features': 'Deep value analysis\nESG integration\nLong-term focus\nActive management',
            'url': '/strategies/value-equity-strategy/'
        }
    ]
    
    for i, strategy in enumerate(strategies):
        StrategyCard.objects.create(
            page=solutions_page,
            sort_order=i,
            **strategy
        )
    
    print(f"Created {len(strategies)} strategy cards")

def update_page_urls():
    """Update the page URLs to replace the old legalpage."""
    print("Updating page URLs...")
    
    # Get the old legal page
    try:
        old_page = Page.objects.get(id=264, slug='solutions')
        print(f"Found old solutions page: {old_page.title}")
        
        # Update its slug to avoid conflicts
        old_page.slug = 'solutions-old'
        old_page.save()
        print("Renamed old page to 'solutions-old'")
        
        # Get the new SolutionsPage
        new_page = SolutionsPage.objects.first()
        if new_page:
            new_page.slug = 'solutions'
            new_page.save()
            print("Updated new SolutionsPage slug to 'solutions'")
            
    except Page.DoesNotExist:
        print("No old solutions page found")

if __name__ == "__main__":
    # Create the solutions page
    solutions_page = create_solutions_page()
    
    # Create strategy cards
    if solutions_page:
        create_strategy_cards(solutions_page)
        
        # Save and publish the page
        solutions_page.save_revision().publish()
        print("Solutions page published successfully!")
        
        # Update URLs
        update_page_urls()
        
        print(f"\n✅ Solutions page is ready at: {solutions_page.url}")
        print("🔗 Links to:")
        print("  - Individual onboarding: /onboarding/")
        print("  - Institutional services: /institutions/")  
        print("  - Adviser partnerships: /advisers/")
        print("  - Strategy details: /strategies/[strategy-name]/")
        print("  - Consultation booking: /consultation/")