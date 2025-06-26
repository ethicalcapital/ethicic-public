from django.core.management.base import BaseCommand
from wagtail.models import Site

from public_site.models import StrategyPage


class Command(BaseCommand):
    help = "Create initial strategy pages"

    def handle(self, *args, **options):
        try:
            # Get the default site and root page
            try:
                site = Site.objects.get(is_default_site=True)
            except Site.MultipleObjectsReturned:
                site = Site.objects.filter(is_default_site=True).first()
            except Site.DoesNotExist:
                site = Site.objects.first()

            root_page = site.root_page

            # Strategy data
            strategies = [
                {
                    "title": "Growth Strategy",
                    "slug": "growth-strategy",
                    "strategy_subtitle": "Maximum impact, full market exposure",
                    "strategy_description": "<p>Our flagship strategy where we can fully implement our ethical criteria without compromise. Designed for long-term growth investors comfortable with equity market exposure.</p>",
                    "strategy_label": "Our Flagship",
                    "risk_level": "Full market exposure",
                    "ethical_implementation": "100% Full Criteria",
                    "holdings_count": "~25 positions",
                    "best_for": "Long-term growth",
                    "ytd_return": "8.2%",
                    "one_year_return": "15.7%",
                    "three_year_return": "9.8%",
                    "since_inception_return": "12.1%",
                    "portfolio_content": """
                        <h3>Investment Universe</h3>
                        <p>Our Growth strategy invests in companies that pass our comprehensive ethical screening process, focusing on businesses that create positive societal impact while delivering strong financial returns. We exclude 57% of the S&P 500 based on our ethical criteria.</p>

                        <h3>Portfolio Construction</h3>
                        <p>We maintain a concentrated portfolio of our highest-conviction ideas, typically holding 20-30 positions with target allocation of approximately 2% per holding. This approach allows us to maintain meaningful exposure to our best ideas while ensuring adequate diversification.</p>

                        <h3>Sector Allocation</h3>
                        <p>Our sector allocation is driven by bottom-up security selection rather than top-down sector targets. We maintain broad diversification across sectors while avoiding industries that conflict with our ethical criteria including weapons, tobacco, fossil fuels, and companies on the BDS list.</p>
                    """,
                    "commentary_content": """
                        <h3>Current Market Environment</h3>
                        <p>In the current market environment, we continue to find attractive opportunities in companies that are creating positive societal impact while maintaining strong competitive positions. Our proprietary research process has identified several compelling investment themes that align with both our ethical criteria and financial objectives.</p>

                        <h3>Strategy Positioning</h3>
                        <p>The Growth strategy remains positioned for long-term value creation through our disciplined approach to ethical investing. We maintain our focus on companies with sustainable business models, strong management teams, and clear paths to continued growth. Our screening process eliminates companies involved in weapons, tobacco, fossil fuels, human rights violations, and other harmful activities.</p>

                        <h3>Recent Developments</h3>
                        <p>We continue to enhance our research capabilities with AI-powered analysis tools and multi-agent systems that help us identify ethical concerns beyond traditional ESG ratings. 40% of our exclusions come from proprietary research that identifies issues others miss.</p>

                        <h3>Outlook</h3>
                        <p>While market volatility creates near-term uncertainty, we remain optimistic about the long-term prospects for ethical investing. Our research continues to identify companies that can deliver both financial returns and positive societal impact, creating what we believe to be sustainable competitive advantages.</p>
                    """,
                    "process_content": """
                        <p>Our Growth strategy follows the same rigorous three-step process outlined on our main process page, with specific focus on companies that offer the best growth potential within our ethical universe.</p>

                        <div class="process-steps">
                            <div class="process-step">
                                <div class="step-number">1</div>
                                <div class="step-content">
                                    <h3>Comprehensive Ethical Screening</h3>
                                    <p>We exclude companies involved in weapons, tobacco, fossil fuels, human rights violations, and companies on the BDS list. We've signed the Apartheid Free Pledge and maintain comprehensive screening for companies involved in violations of Palestinian human rights.</p>
                                </div>
                            </div>

                            <div class="process-step">
                                <div class="step-number">2</div>
                                <div class="step-content">
                                    <h3>Growth-Focused Research</h3>
                                    <p>Within our ethical universe, we evaluate companies through six fundamental lenses: People, Product, Execution, Valuation, Moat, and Risk, with particular emphasis on companies with strong growth prospects and sustainable competitive advantages.</p>
                                </div>
                            </div>

                            <div class="process-step">
                                <div class="step-number">3</div>
                                <div class="step-content">
                                    <h3>Portfolio Construction</h3>
                                    <p>We build concentrated portfolios targeting approximately 2% allocation per holding, focusing on our highest-conviction growth ideas while maintaining appropriate diversification and risk management.</p>
                                </div>
                            </div>
                        </div>
                    """,
                },
                {
                    "title": "Income Strategy",
                    "slug": "income-strategy",
                    "strategy_subtitle": "Current income with full ethical criteria",
                    "strategy_description": "<p>Our income strategy applies the same rigorous ethical criteria as our growth strategy, focused on the best income-generating securities in our universe.</p>",
                    "strategy_label": "Full Ethics, Different Universe",
                    "risk_level": "Moderate",
                    "ethical_implementation": "100% Full Criteria",
                    "holdings_count": "~20-30 positions",
                    "best_for": "Income generation",
                    "ytd_return": "6.8%",
                    "one_year_return": "11.2%",
                    "three_year_return": "7.9%",
                    "since_inception_return": "8.7%",
                    "portfolio_content": """
                        <h3>Investment Universe</h3>
                        <p>Our Income strategy focuses on dividend-paying stocks, REITs, and other income-generating securities that pass our comprehensive ethical screening. We maintain the same rigorous exclusion criteria as our Growth strategy while targeting securities that provide consistent income streams.</p>

                        <h3>Income Focus</h3>
                        <p>We target companies with sustainable dividend policies, strong cash flow generation, and histories of consistent income distribution. Our approach emphasizes dividend sustainability over yield maximization, focusing on companies with the financial strength to maintain distributions through market cycles.</p>

                        <h3>Sector Considerations</h3>
                        <p>Traditional high-yield sectors like utilities and telecommunications often conflict with our ethical criteria due to fossil fuel exposure. We instead focus on ethical alternatives including sustainable infrastructure, healthcare services, and technology companies with strong cash generation and dividend policies.</p>
                    """,
                    "commentary_content": """
                        <h3>Income Strategy Positioning</h3>
                        <p>Our Income strategy continues to demonstrate that investors don't need to compromise their values to generate consistent income. By focusing on companies with sustainable business models and strong cash generation, we've built a portfolio that delivers both current income and ethical alignment.</p>

                        <h3>Market Environment</h3>
                        <p>The current interest rate environment creates both challenges and opportunities for income investors. While rising rates pressure some traditional income securities, they also create opportunities for companies with strong balance sheets and sustainable competitive advantages.</p>

                        <h3>Dividend Sustainability</h3>
                        <p>We maintain our focus on dividend sustainability over yield maximization. Our research process evaluates payout ratios, cash flow coverage, and management's commitment to maintaining distributions, ensuring our income strategy can weather various market environments.</p>
                    """,
                },
                {
                    "title": "Diversification Strategy",
                    "slug": "diversification-strategy",
                    "strategy_subtitle": "Broader diversification through aligned managers",
                    "strategy_description": "<p>For broader diversification, we work with carefully selected external managers. While we can't warrant full compliance, we choose managers whose values align with ours.</p>",
                    "strategy_label": "Risk Management Focus",
                    "risk_level": "Lower volatility",
                    "ethical_implementation": "Best efforts",
                    "holdings_count": "Multiple managers",
                    "best_for": "Risk management",
                    "ytd_return": "5.9%",
                    "one_year_return": "9.8%",
                    "three_year_return": "6.7%",
                    "since_inception_return": "7.2%",
                    "portfolio_content": """
                        <h3>Manager Selection</h3>
                        <p>Our Diversification strategy provides access to broader market exposure through carefully selected external managers who share our commitment to ethical investing. While we cannot guarantee full compliance with our screening criteria, we partner with managers whose investment philosophies align with our values.</p>

                        <h3>Risk Management</h3>
                        <p>This strategy is designed for investors who prioritize risk management and broader diversification over maximum ethical implementation. It provides exposure to asset classes and investment strategies that complement our direct investment approaches.</p>

                        <h3>Due Diligence</h3>
                        <p>We conduct comprehensive due diligence on potential partners, evaluating their investment processes, organizational culture, and commitment to responsible investing. We maintain ongoing dialogue with our partners about ethical considerations and portfolio alignment.</p>
                    """,
                    "commentary_content": """
                        <h3>Balanced Approach</h3>
                        <p>Our Diversification strategy represents a balanced approach for investors who want broader market exposure while maintaining a commitment to ethical investing. This strategy acknowledges that perfect ethical alignment may not always be possible while still striving for the best possible outcomes.</p>

                        <h3>Manager Partnerships</h3>
                        <p>We continue to strengthen our relationships with like-minded investment managers who share our commitment to responsible investing. These partnerships allow us to offer our clients access to specialized expertise and investment opportunities beyond our direct capabilities.</p>

                        <h3>Evolution and Improvement</h3>
                        <p>We actively work with our partner managers to improve their ethical screening processes and alignment with our values. This collaborative approach helps advance the broader ethical investing movement while providing our clients with diversified exposure.</p>
                    """,
                },
            ]

            for strategy_data in strategies:
                # Check if strategy page already exists
                if StrategyPage.objects.filter(slug=strategy_data["slug"]).exists():
                    self.stdout.write(
                        self.style.WARNING(
                            f'Strategy page "{strategy_data["title"]}" already exists, skipping...',
                        ),
                    )
                    continue

                # Create the strategy page
                strategy_page = StrategyPage(
                    title=strategy_data["title"],
                    slug=strategy_data["slug"],
                    strategy_subtitle=strategy_data["strategy_subtitle"],
                    strategy_description=strategy_data["strategy_description"],
                    strategy_label=strategy_data["strategy_label"],
                    risk_level=strategy_data["risk_level"],
                    ethical_implementation=strategy_data["ethical_implementation"],
                    holdings_count=strategy_data["holdings_count"],
                    best_for=strategy_data["best_for"],
                    ytd_return=strategy_data["ytd_return"],
                    one_year_return=strategy_data["one_year_return"],
                    three_year_return=strategy_data["three_year_return"],
                    since_inception_return=strategy_data["since_inception_return"],
                    portfolio_content=strategy_data["portfolio_content"],
                    commentary_content=strategy_data["commentary_content"],
                    process_content=strategy_data.get("process_content", ""),
                )

                # Add the page to the root
                root_page.add_child(instance=strategy_page)
                strategy_page.save_revision().publish()

                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully created strategy page: "{strategy_data["title"]}"',
                    ),
                )

            self.stdout.write(
                self.style.SUCCESS("Strategy pages setup completed successfully!"),
            )

        except Exception as e:
            self.stderr.write(
                self.style.ERROR(f"Error setting up strategy pages: {e!s}"),
            )
