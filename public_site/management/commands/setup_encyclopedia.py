from django.core.management.base import BaseCommand
from django.utils.text import slugify
from wagtail.models import Site

from public_site.models import EncyclopediaEntry, EncyclopediaIndexPage


class Command(BaseCommand):
    help = "Create encyclopedia index page and initial entries"

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

            # Create Encyclopedia Index Page if it doesn't exist
            if not EncyclopediaIndexPage.objects.filter(slug="encyclopedia").exists():
                encyclopedia_index = EncyclopediaIndexPage(
                    title="Investment Encyclopedia",
                    slug="encyclopedia",
                    intro_text="<p>Comprehensive investment terminology and concepts explained in plain language.</p>",
                    description="""<p>Our Investment Encyclopedia provides clear, accessible explanations of key investment terms and concepts. Whether you're new to investing or looking to expand your knowledge, this resource helps you understand the language of finance and ethical investing.</p>

                    <p>Each entry includes detailed explanations, real-world examples, and connections to related concepts. Our goal is to demystify investment terminology and help you make more informed decisions about your financial future.</p>""",
                )

                root_page.add_child(instance=encyclopedia_index)
                encyclopedia_index.save_revision().publish()

                self.stdout.write(self.style.SUCCESS("Created Encyclopedia Index Page"))
            else:
                encyclopedia_index = EncyclopediaIndexPage.objects.get(
                    slug="encyclopedia",
                )
                self.stdout.write(
                    self.style.WARNING("Encyclopedia Index Page already exists"),
                )

            # Encyclopedia entries data
            entries_data = [
                {
                    "title": "Active Management",
                    "summary": "Active portfolio management involves the selection of securities based on research. This is meaningfully distinct from passive approaches that track market indices.",
                    "detailed_content": """<p>Active management is an investment strategy where portfolio managers make specific investments with the goal of outperforming an investment benchmark index. Unlike passive management, which seeks to replicate index performance, active managers use research, analysis, and their own judgment to select securities.</p>

                    <h3>Key Characteristics</h3>
                    <ul>
                        <li><strong>Research-Driven:</strong> Decisions based on fundamental and technical analysis</li>
                        <li><strong>Selective Approach:</strong> Choosing specific securities rather than buying entire markets</li>
                        <li><strong>Performance Goal:</strong> Attempting to outperform benchmark indices</li>
                        <li><strong>Higher Costs:</strong> Generally more expensive than passive strategies due to research and trading costs</li>
                    </ul>

                    <h3>Active vs. Passive Management</h3>
                    <p>While passive management seeks to match market returns through index tracking, active management aims to exceed market performance through security selection and market timing. This approach requires more resources and expertise but offers the potential for higher returns.</p>""",
                    "category": "strategy",
                    "difficulty_level": "beginner",
                    "related_terms": "passive management, portfolio management, security selection, benchmark",
                    "examples": """<p><strong>Example 1:</strong> A fund manager analyzes technology companies and selects only those with strong growth prospects and ethical business practices, rather than buying all technology stocks in an index.</p>

                    <p><strong>Example 2:</strong> An ethical investment firm actively excludes companies involved in weapons, tobacco, or fossil fuels while seeking to outperform the broader market with their remaining investment universe.</p>""",
                },
                {
                    "title": "American Depositary Receipts (ADRs)",
                    "summary": "ADRs are securities designed to simplify the process of investing in foreign companies by allowing trading in U.S. dollars on American exchanges.",
                    "detailed_content": """<p>American Depositary Receipts (ADRs) are negotiable certificates issued by U.S. banks that represent shares in foreign companies. They allow American investors to buy shares in foreign companies without dealing with foreign exchanges or currency conversion.</p>

                    <h3>How ADRs Work</h3>
                    <p>A U.S. bank purchases shares of a foreign company and holds them in trust. The bank then issues ADRs that represent these underlying shares, typically on a 1:1 ratio, though this can vary. These ADRs trade on U.S. exchanges just like domestic stocks.</p>

                    <h3>Benefits for Investors</h3>
                    <ul>
                        <li><strong>Convenience:</strong> Trade in U.S. dollars during U.S. market hours</li>
                        <li><strong>Regulation:</strong> Subject to U.S. securities laws and reporting requirements</li>
                        <li><strong>Diversification:</strong> Easy access to international markets</li>
                        <li><strong>Dividends:</strong> Receive dividends in U.S. dollars</li>
                    </ul>""",
                    "category": "instruments",
                    "difficulty_level": "intermediate",
                    "related_terms": "foreign securities, international investing, currency risk, depositary receipts",
                    "examples": """<p><strong>Example:</strong> Nestle, a Swiss company, has ADRs that trade on U.S. exchanges under the ticker NSRGY. American investors can buy these ADRs just like any U.S. stock, receiving exposure to Nestle without dealing with Swiss franc currency conversion or Swiss exchange regulations.</p>""",
                },
                {
                    "title": "Currency Risk",
                    "summary": "The risk of loss from fluctuating foreign exchange rates when a portfolio has exposure to foreign currencies through international investments.",
                    "detailed_content": """<p>Currency risk, also known as exchange rate risk, is the potential for investment losses due to changes in currency exchange rates. This risk affects any investment denominated in a currency different from the investor's base currency.</p>

                    <h3>Types of Currency Risk</h3>
                    <ul>
                        <li><strong>Transaction Risk:</strong> Risk from currency fluctuations between transaction date and settlement</li>
                        <li><strong>Translation Risk:</strong> Risk from converting foreign subsidiaries' financial statements</li>
                        <li><strong>Economic Risk:</strong> Long-term risk from sustained currency movements affecting company valuations</li>
                    </ul>

                    <h3>Impact on Returns</h3>
                    <p>Even if a foreign investment performs well in its local currency, unfavorable currency movements can reduce or eliminate gains when converted back to the investor's base currency. Conversely, favorable currency movements can enhance returns.</p>

                    <h3>Managing Currency Risk</h3>
                    <p>Investors can manage currency risk through hedging strategies, currency-hedged funds, or by diversifying across multiple currencies.</p>""",
                    "category": "risk",
                    "difficulty_level": "intermediate",
                    "related_terms": "foreign securities, international investing, hedging, exchange rates",
                    "examples": """<p><strong>Example:</strong> A U.S. investor buys European stocks worth €10,000 when the EUR/USD exchange rate is 1.20 (costing $12,000). If the stock value stays the same in euros but the exchange rate falls to 1.10, the investment is now worth only $11,000 in U.S. dollars, representing a $1,000 currency loss despite no change in the underlying stock price.</p>""",
                },
                {
                    "title": "ESG Risk",
                    "summary": "Environmental, Social, and Governance risks that can impact investment performance through regulatory, reputational, or operational challenges.",
                    "detailed_content": """<p>ESG risk refers to the potential negative impact on investment returns from environmental, social, and governance factors. These risks have become increasingly important as stakeholders demand greater corporate responsibility and regulators implement stricter requirements.</p>

                    <h3>Environmental Risks</h3>
                    <ul>
                        <li>Climate change and extreme weather events</li>
                        <li>Resource scarcity and environmental degradation</li>
                        <li>Regulatory changes related to environmental protection</li>
                        <li>Transition costs to sustainable business models</li>
                    </ul>

                    <h3>Social Risks</h3>
                    <ul>
                        <li>Labor practices and human rights violations</li>
                        <li>Product safety and quality issues</li>
                        <li>Data privacy and cybersecurity breaches</li>
                        <li>Community relations and social license to operate</li>
                    </ul>

                    <h3>Governance Risks</h3>
                    <ul>
                        <li>Poor board oversight and executive compensation</li>
                        <li>Lack of transparency and disclosure</li>
                        <li>Corruption and unethical business practices</li>
                        <li>Inadequate risk management systems</li>
                    </ul>""",
                    "category": "ethics",
                    "difficulty_level": "intermediate",
                    "related_terms": "sustainable investing, corporate governance, environmental risk, social responsibility",
                    "examples": """<p><strong>Environmental Example:</strong> An oil company faces stranded asset risk as renewable energy adoption accelerates and carbon pricing policies are implemented.</p>

                    <p><strong>Social Example:</strong> A technology company experiences reputational damage and regulatory fines due to data privacy violations, leading to decreased user trust and potential loss of business.</p>

                    <p><strong>Governance Example:</strong> A company with poor board oversight experiences an accounting scandal, resulting in regulatory penalties, legal costs, and significant stock price decline.</p>""",
                },
                {
                    "title": "Exchange-Traded Funds (ETFs)",
                    "summary": "Investment funds that trade on stock exchanges like individual stocks, typically tracking an index, commodity, bonds, or basket of assets.",
                    "detailed_content": """<p>Exchange-Traded Funds (ETFs) are investment vehicles that combine features of mutual funds and individual stocks. They hold a basket of securities and trade on stock exchanges throughout the trading day at market-determined prices.</p>

                    <h3>Key Features</h3>
                    <ul>
                        <li><strong>Intraday Trading:</strong> Can be bought and sold during market hours</li>
                        <li><strong>Lower Costs:</strong> Generally have lower expense ratios than actively managed mutual funds</li>
                        <li><strong>Transparency:</strong> Holdings are disclosed daily</li>
                        <li><strong>Tax Efficiency:</strong> Structure typically results in fewer taxable events</li>
                    </ul>

                    <h3>Types of ETFs</h3>
                    <ul>
                        <li><strong>Index ETFs:</strong> Track specific market indices</li>
                        <li><strong>Sector ETFs:</strong> Focus on specific industries</li>
                        <li><strong>Commodity ETFs:</strong> Provide exposure to commodities</li>
                        <li><strong>Bond ETFs:</strong> Hold fixed-income securities</li>
                        <li><strong>ESG ETFs:</strong> Focus on environmental, social, and governance criteria</li>
                    </ul>""",
                    "category": "instruments",
                    "difficulty_level": "beginner",
                    "related_terms": "index funds, passive investing, diversification, expense ratios",
                    "examples": """<p><strong>Example:</strong> The SPDR S&P 500 ETF (SPY) tracks the S&P 500 index, giving investors exposure to 500 large U.S. companies in a single, tradeable security with an expense ratio of just 0.09%.</p>""",
                },
                {
                    "title": "Fundamental Analysis",
                    "summary": "Investment analysis method that evaluates securities by examining underlying economic, financial, and other qualitative factors.",
                    "detailed_content": """<p>Fundamental analysis is a method of evaluating securities by examining the underlying factors that affect a company's actual business and its future prospects. This analysis attempts to determine the intrinsic value of a security.</p>

                    <h3>Key Components</h3>
                    <ul>
                        <li><strong>Financial Statements:</strong> Analysis of income statements, balance sheets, and cash flow statements</li>
                        <li><strong>Economic Factors:</strong> GDP growth, inflation, interest rates, and industry trends</li>
                        <li><strong>Company Management:</strong> Quality of leadership and strategic direction</li>
                        <li><strong>Competitive Position:</strong> Market share, competitive advantages, and industry dynamics</li>
                    </ul>

                    <h3>Financial Ratios</h3>
                    <p>Fundamental analysts use various ratios to evaluate companies:</p>
                    <ul>
                        <li><strong>Valuation Ratios:</strong> P/E ratio, P/B ratio, EV/EBITDA</li>
                        <li><strong>Profitability Ratios:</strong> ROE, ROA, profit margins</li>
                        <li><strong>Liquidity Ratios:</strong> Current ratio, quick ratio</li>
                        <li><strong>Leverage Ratios:</strong> Debt-to-equity, interest coverage</li>
                    </ul>""",
                    "category": "analysis",
                    "difficulty_level": "intermediate",
                    "related_terms": "technical analysis, valuation, financial ratios, intrinsic value",
                    "examples": """<p><strong>Example:</strong> An analyst examining Apple Inc. would review its iPhone sales trends, service revenue growth, cash flow generation, competitive position against Android, management's capital allocation strategy, and compare valuation metrics to peers like Microsoft and Google to determine if the stock is fairly valued.</p>""",
                },
                {
                    "title": "Liquidity Risk",
                    "summary": "The risk that an investor will not be able to buy or sell an investment quickly enough to prevent or minimize a loss.",
                    "detailed_content": """<p>Liquidity risk is the risk that an investor may not be able to quickly convert an investment into cash without significantly affecting the security's price. This risk is particularly important during market stress when trading volumes may decline.</p>

                    <h3>Types of Liquidity Risk</h3>
                    <ul>
                        <li><strong>Market Liquidity Risk:</strong> Risk that a market becomes illiquid, making it difficult to trade</li>
                        <li><strong>Funding Liquidity Risk:</strong> Risk that an investor cannot meet short-term financial obligations</li>
                        <li><strong>Asset Liquidity Risk:</strong> Risk specific to certain assets that naturally have limited trading volume</li>
                    </ul>

                    <h3>Factors Affecting Liquidity</h3>
                    <ul>
                        <li>Market capitalization and trading volume</li>
                        <li>Number of market participants</li>
                        <li>Market maker presence</li>
                        <li>Economic conditions and market volatility</li>
                    </ul>

                    <h3>Managing Liquidity Risk</h3>
                    <p>Investors can manage liquidity risk by maintaining cash reserves, diversifying across liquid securities, and understanding the liquidity characteristics of their investments.</p>""",
                    "category": "risk",
                    "difficulty_level": "intermediate",
                    "related_terms": "market risk, trading volume, bid-ask spread, market makers",
                    "examples": """<p><strong>High Liquidity Example:</strong> Large-cap stocks like Apple or Microsoft can typically be sold immediately during market hours with minimal impact on price due to high trading volumes.</p>

                    <p><strong>Low Liquidity Example:</strong> Small-cap stocks or certain bonds may have limited buyers, requiring investors to accept lower prices for quick sales or wait longer to find buyers at desired prices.</p>""",
                },
                {
                    "title": "Market Risk",
                    "summary": "The risk of losses due to factors that affect the overall performance of financial markets, also known as systematic risk.",
                    "detailed_content": """<p>Market risk, also called systematic risk, is the possibility of an investor experiencing losses due to factors that affect the overall performance of the financial markets. This type of risk cannot be eliminated through diversification because it affects the entire market.</p>

                    <h3>Components of Market Risk</h3>
                    <ul>
                        <li><strong>Interest Rate Risk:</strong> Risk from changes in interest rates</li>
                        <li><strong>Inflation Risk:</strong> Risk that purchasing power will be eroded by inflation</li>
                        <li><strong>Currency Risk:</strong> Risk from fluctuating exchange rates</li>
                        <li><strong>Political Risk:</strong> Risk from political instability or policy changes</li>
                    </ul>

                    <h3>Measurement</h3>
                    <p>Market risk is often measured using:</p>
                    <ul>
                        <li><strong>Beta:</strong> Measures sensitivity to market movements</li>
                        <li><strong>Value at Risk (VaR):</strong> Estimates potential losses over a specific time period</li>
                        <li><strong>Standard Deviation:</strong> Measures volatility of returns</li>
                    </ul>

                    <h3>Managing Market Risk</h3>
                    <p>While market risk cannot be eliminated, it can be managed through asset allocation, hedging strategies, and maintaining appropriate time horizons for investments.</p>""",
                    "category": "risk",
                    "difficulty_level": "beginner",
                    "related_terms": "systematic risk, beta, volatility, diversification",
                    "examples": """<p><strong>Example:</strong> During the 2008 financial crisis, most stocks declined regardless of individual company fundamentals because the entire market was affected by systemic issues in the financial system. Even well-diversified portfolios experienced significant losses due to market risk.</p>""",
                },
                {
                    "title": "Passive Management",
                    "summary": "Investment strategy that aims to replicate the performance of a market index rather than outperform it through active security selection.",
                    "detailed_content": """<p>Passive management is an investment approach that seeks to replicate the performance of a specific market index or benchmark. Rather than trying to beat the market through active stock selection, passive managers aim to match market returns while minimizing costs.</p>

                    <h3>Key Principles</h3>
                    <ul>
                        <li><strong>Index Replication:</strong> Holdings mirror those of a chosen benchmark index</li>
                        <li><strong>Low Turnover:</strong> Minimal buying and selling reduces transaction costs</li>
                        <li><strong>Cost Efficiency:</strong> Lower management fees due to reduced research and trading</li>
                        <li><strong>Market Return:</strong> Accepts market returns rather than attempting to exceed them</li>
                    </ul>

                    <h3>Advantages</h3>
                    <ul>
                        <li>Lower expenses and fees</li>
                        <li>Broad market diversification</li>
                        <li>Transparency of holdings</li>
                        <li>Tax efficiency due to low turnover</li>
                        <li>Consistent with efficient market theory</li>
                    </ul>

                    <h3>Common Vehicles</h3>
                    <p>Passive management is typically implemented through index funds and ETFs that track major indices like the S&P 500, Total Stock Market, or bond indices.</p>""",
                    "category": "strategy",
                    "difficulty_level": "beginner",
                    "related_terms": "active management, index funds, ETFs, efficient market hypothesis",
                    "examples": """<p><strong>Example:</strong> The Vanguard S&P 500 Index Fund (VFIAX) is a passive fund that holds all 500 stocks in the S&P 500 index in the same proportions, providing investors with market returns at a very low 0.04% expense ratio.</p>""",
                },
                {
                    "title": "Portfolio Diversification",
                    "summary": "Risk management strategy that mixes a variety of investments within a portfolio to reduce exposure to any single asset or risk.",
                    "detailed_content": """<p>Portfolio diversification is a risk management technique that combines different types of investments in a single portfolio. The goal is to reduce risk by spreading investments across various asset classes, sectors, and securities that would each react differently to the same economic event.</p>

                    <h3>Types of Diversification</h3>
                    <ul>
                        <li><strong>Asset Class Diversification:</strong> Mixing stocks, bonds, commodities, and cash</li>
                        <li><strong>Geographic Diversification:</strong> Investing across different countries and regions</li>
                        <li><strong>Sector Diversification:</strong> Spreading investments across various industries</li>
                        <li><strong>Style Diversification:</strong> Combining growth and value investing approaches</li>
                        <li><strong>Time Diversification:</strong> Dollar-cost averaging over time</li>
                    </ul>

                    <h3>Benefits</h3>
                    <ul>
                        <li>Reduces portfolio volatility</li>
                        <li>Minimizes impact of poor-performing investments</li>
                        <li>Provides exposure to multiple growth opportunities</li>
                        <li>Helps preserve capital during market downturns</li>
                    </ul>

                    <h3>Limitations</h3>
                    <p>Diversification cannot eliminate all risk, particularly systematic risk that affects entire markets. Over-diversification can also lead to mediocre returns and increased complexity.</p>""",
                    "category": "strategy",
                    "difficulty_level": "beginner",
                    "related_terms": "risk management, asset allocation, correlation, systematic risk",
                    "examples": """<p><strong>Example:</strong> A diversified portfolio might include 60% stocks (split between U.S. and international, across various sectors), 30% bonds (government and corporate), 5% commodities, and 5% cash, rather than investing everything in a single stock or asset class.</p>""",
                },
            ]

            # Create encyclopedia entries
            for entry_data in entries_data:
                # Check if entry already exists
                if EncyclopediaEntry.objects.filter(
                    slug=slugify(entry_data["title"]),
                ).exists():
                    self.stdout.write(
                        self.style.WARNING(
                            f'Entry "{entry_data["title"]}" already exists, skipping...',
                        ),
                    )
                    continue

                # Create the entry
                entry = EncyclopediaEntry(
                    title=entry_data["title"],
                    slug=slugify(entry_data["title"]),
                    summary=entry_data["summary"],
                    detailed_content=entry_data["detailed_content"],
                    category=entry_data["category"],
                    difficulty_level=entry_data["difficulty_level"],
                    related_terms=entry_data["related_terms"],
                    examples=entry_data.get("examples", ""),
                )

                # Add the entry to the encyclopedia index
                encyclopedia_index.add_child(instance=entry)
                entry.save_revision().publish()

                self.stdout.write(
                    self.style.SUCCESS(
                        f'Created encyclopedia entry: "{entry_data["title"]}"',
                    ),
                )

            self.stdout.write(
                self.style.SUCCESS("Encyclopedia setup completed successfully!"),
            )

        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error setting up encyclopedia: {e!s}"))
