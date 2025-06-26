from django.core.management.base import BaseCommand

from public_site.models import FAQArticle, FAQIndexPage


class Command(BaseCommand):
    help = "Import remaining support articles"

    def handle(self, *args, **options):
        # Get FAQIndexPage
        support_index = FAQIndexPage.objects.filter(slug="support").first()
        if not support_index:
            self.stdout.write(self.style.ERROR("FAQIndexPage not found."))
            return

        # Missing articles data
        articles_data = [
            # Company & Account Management Articles
            {
                "title": (
                    "How Does Ethical Capital Use Its Influence to Support Its Mission?"
                ),
                "slug": "how-does-ethical-capital-use-influence",
                "category": "company",
                "priority": 5,
                "featured": True,
                "summary": (
                    "Learn how we engage with companies and use shareholder advocacy "
                    "to promote ethical business practices."
                ),
                "content": """<p>As investment managers, we have several tools to influence corporate behavior beyond just choosing which companies to invest in.</p>

<h2>Shareholder Advocacy</h2>
<p>We actively use our position as shareholders to advocate for positive change:</p>
<ul>
<li><strong>Proxy Voting:</strong> We vote on shareholder proposals that align 
with our values, supporting measures that promote environmental responsibility, 
social justice, and good governance</li>
<li><strong>Shareholder Resolutions:</strong> We support and sometimes co-file 
resolutions asking companies to improve their practices</li>
<li><strong>Direct Engagement:</strong> We communicate directly with company 
management about our concerns</li>
</ul>

<h2>Public Advocacy</h2>
<p>We use our platform to promote ethical investing:</p>
<ul>
<li>Publishing research on ethical investment opportunities</li>
<li>Speaking at conferences and events</li>
<li>Educating investors about values-aligned options</li>
<li>Collaborating with other ethical investors</li>
</ul>

<h2>Industry Leadership</h2>
<p>We work to improve the entire investment industry:</p>
<ul>
<li>Sharing our screening methodologies openly</li>
<li>Advocating for better ESG disclosure standards</li>
<li>Supporting regulatory improvements</li>
<li>Mentoring other ethical investment initiatives</li>
</ul>

<h2>Client Empowerment</h2>
<p>We help our clients become advocates too:</p>
<ul>
<li>Providing education about shareholder rights</li>
<li>Facilitating client input on proxy voting</li>
<li>Sharing opportunities for direct action</li>
<li>Building a community of conscious investors</li>
</ul>

<p>Our influence extends beyond just portfolio management - we're building a 
movement for more ethical capitalism.</p>""",
                "keywords": (
                    "shareholder advocacy, proxy voting, corporate engagement, "
                    "ethical influence, ESG"
                ),
            },
            {
                "title": "Are We Invested in Congolese Mining?",
                "slug": "are-we-invested-in-congolese-mining",
                "category": "investment",
                "priority": 7,
                "featured": False,
                "summary": (
                    "Our position on investments in Congolese mining operations and "
                    "conflict minerals."
                ),
                "content": """<p>This is an important question about our ethical screening process, particularly regarding conflict minerals and human rights concerns in the Democratic Republic of Congo (DRC).</p>

<h2>Our Position</h2>
<p>We do not directly invest in companies engaged in mining operations in the DRC due to:</p>
<ul>
<li>Human rights concerns including child labor</li>
<li>Environmental destruction</li>
<li>Funding of armed conflicts</li>
<li>Lack of transparency in supply chains</li>
</ul>

<h2>Supply Chain Complexity</h2>
<p>The challenge extends beyond direct mining companies:</p>
<ul>
<li>Many technology companies use minerals from the DRC</li>
<li>Supply chains can be opaque and complex</li>
<li>Companies may unknowingly source conflict minerals</li>
</ul>

<h2>Our Approach</h2>
<p>We address this through:</p>
<ul>
<li><strong>Direct Exclusions:</strong> No investments in DRC mining operations</li>
<li><strong>Supply Chain Screening:</strong> Evaluating companies' conflict mineral policies</li>
<li><strong>Engagement:</strong> Encouraging better supply chain transparency</li>
<li><strong>Supporting Leaders:</strong> Investing in companies with strong responsible sourcing programs</li>
</ul>

<h2>Ongoing Monitoring</h2>
<p>This is an evolving issue that we continuously monitor. We update our policies as new information becomes available and work with experts in conflict minerals to improve our screening.</p>

<p>If you have specific concerns about Congolese mining or conflict minerals, please contact us to discuss how we can customize your portfolio accordingly.</p>""",
                "keywords": "Congolese mining, conflict minerals, DRC, human rights, supply chain ethics",
            },
            {
                "title": "Will You Invest in My Startup?",
                "slug": "will-you-invest-in-my-startup",
                "category": "company",
                "priority": 3,
                "featured": False,
                "summary": "Information about our investment focus and why we don't directly invest in startups.",
                "content": """<p>We appreciate your interest, but Ethical Capital Investment Collaborative manages client portfolios invested in publicly traded securities, not private startups.</p>

<h2>What We Do</h2>
<p>We are a registered investment advisor that:</p>
<ul>
<li>Manages diversified portfolios for individual investors</li>
<li>Invests exclusively in publicly traded stocks and bonds</li>
<li>Focuses on liquid, transparent investments</li>
<li>Provides professional portfolio management services</li>
</ul>

<h2>Why We Don't Invest in Startups</h2>
<ul>
<li><strong>Regulatory Limitations:</strong> Our registration and client agreements limit us to public securities</li>
<li><strong>Liquidity Requirements:</strong> Client portfolios need to remain liquid for withdrawals</li>
<li><strong>Diversification Mandate:</strong> We maintain broadly diversified portfolios</li>
<li><strong>Transparency Standards:</strong> We require the disclosure standards of public companies</li>
</ul>

<h2>Alternative Resources</h2>
<p>For startup funding, consider:</p>
<ul>
<li>Angel investor networks in your area</li>
<li>Venture capital firms aligned with your values</li>
<li>Impact investment funds</li>
<li>Crowdfunding platforms</li>
<li>Small business loans and grants</li>
</ul>

<h2>Future Possibilities</h2>
<p>Once your company goes public through an IPO and meets our ethical screening criteria, we would be happy to consider it for client portfolios.</p>

<p>We wish you the best with your venture and hope to see it succeed!</p>""",
                "keywords": "startup investment, venture capital, private equity, investment focus",
            },
            {
                "title": "Is Ethical Capital a Mutual Fund, ETF, or Hedge Fund?",
                "slug": "is-ethical-capital-mutual-fund-etf-hedge-fund",
                "category": "company",
                "priority": 4,
                "featured": False,
                "summary": "Understanding what type of investment firm we are and how we differ from funds.",
                "content": """<p>No, Ethical Capital is none of these. We are a Registered Investment Advisor (RIA) that provides personalized portfolio management services.</p>

<h2>What We Are: Registered Investment Advisor</h2>
<p>As an RIA, we:</p>
<ul>
<li>Manage separate accounts for each client</li>
<li>Provide personalized portfolio management</li>
<li>Act as fiduciaries with a legal duty to clients</li>
<li>Offer direct ownership of securities</li>
<li>Customize portfolios based on individual values</li>
</ul>

<h2>How We Differ from Mutual Funds</h2>
<p>Unlike mutual funds:</p>
<ul>
<li>You directly own your securities (not fund shares)</li>
<li>Full transparency into every holding</li>
<li>Customization based on your values</li>
<li>Better tax efficiency through direct ownership</li>
<li>No hidden fees or expense ratios</li>
</ul>

<h2>How We Differ from ETFs</h2>
<p>Unlike ETFs:</p>
<ul>
<li>Actively managed based on ethical criteria</li>
<li>Personalized to your specific values</li>
<li>Direct communication with portfolio managers</li>
<li>No tracking of arbitrary indexes</li>
<li>Flexible rebalancing and tax management</li>
</ul>

<h2>How We Differ from Hedge Funds</h2>
<p>Unlike hedge funds:</p>
<ul>
<li>No performance fees (just 1% annual management fee)</li>
<li>Complete transparency in holdings and strategy</li>
<li>No lock-up periods - your money is always accessible</li>
<li>No complex derivatives or leverage</li>
<li>Open to all investors (not just accredited)</li>
</ul>

<h2>The RIA Advantage</h2>
<p>Working with an RIA provides:</p>
<ul>
<li>Personalized service and direct relationships</li>
<li>Fiduciary standard of care</li>
<li>Complete transparency</li>
<li>Tax efficiency through direct ownership</li>
<li>Values-based customization</li>
</ul>

<p>This structure allows us to provide institutional-quality investment management tailored to your specific needs and values.</p>""",
                "keywords": "RIA, registered investment advisor, mutual fund, ETF, hedge fund, investment structure",
            },
            {
                "title": "What Types of Accounts Do You Offer?",
                "slug": "what-types-of-accounts-do-you-offer",
                "category": "account",
                "priority": 9,
                "featured": True,
                "summary": "Overview of the investment account types available through Ethical Capital.",
                "content": """<p>We offer a comprehensive range of investment accounts to meet your financial goals.</p>

<h2>Individual & Joint Accounts</h2>
<ul>
<li><strong>Individual Taxable:</strong> Standard investment account with full flexibility</li>
<li><strong>Joint Tenants with Rights of Survivorship:</strong> Shared ownership with automatic transfer</li>
<li><strong>Joint Tenants in Common:</strong> Shared ownership with designated percentages</li>
</ul>

<h2>Retirement Accounts</h2>
<ul>
<li><strong>Traditional IRA:</strong> Tax-deferred growth with deductible contributions</li>
<li><strong>Roth IRA:</strong> Tax-free growth with after-tax contributions</li>
<li><strong>SEP IRA:</strong> Simplified Employee Pension for self-employed individuals</li>
<li><strong>Rollover IRA:</strong> For consolidating old 401(k) and 403(b) accounts</li>
</ul>

<h2>Trust & Entity Accounts</h2>
<ul>
<li><strong>Revocable Living Trust:</strong> Estate planning with maintained control</li>
<li><strong>Irrevocable Trust:</strong> Advanced estate planning strategies</li>
<li><strong>LLC/Partnership:</strong> Business entity accounts</li>
<li><strong>Corporate:</strong> C-Corp and S-Corp accounts</li>
</ul>

<h2>Specialty Accounts</h2>
<ul>
<li><strong>UTMA/UGMA:</strong> Custodial accounts for minors</li>
<li><strong>529 Education Savings:</strong> Tax-advantaged college savings - contact us for details</li>
<li><strong>Charitable:</strong> Donor-advised funds and foundations - contact us for setup</li>
</ul>

<h2>Account Features</h2>
<p>All accounts include:</p>
<ul>
<li>Professional portfolio management</li>
<li>Ethical screening and customization</li>
<li>Online access and reporting</li>
<li>Tax-loss harvesting (where applicable)</li>
<li>No account minimums or setup fees</li>
</ul>

<h2>Getting Started</h2>
<p>Opening an account is simple:</p>
<ol>
<li>Choose your account type</li>
<li>Complete online application</li>
<li>Fund your account</li>
<li>We'll build your ethical portfolio</li>
</ol>

<p>Not sure which account type is right for you? Contact us for guidance.</p>""",
                "keywords": "account types, IRA, joint account, trust, retirement accounts, investment accounts",
            },
            {
                "title": "Does Ethical Capital Offer Financial Planning?",
                "slug": "does-ethical-capital-offer-financial-planning",
                "category": "planning",
                "priority": 8,
                "featured": False,
                "summary": "Information about our investment management focus and financial planning resources.",
                "content": """<p>While we don't provide comprehensive financial planning services, we do offer investment guidance and can refer you to trusted planning professionals.</p>

<h2>What We Provide</h2>
<p>Our investment management service includes:</p>
<ul>
<li><strong>Investment Strategy:</strong> Developing appropriate asset allocation</li>
<li><strong>Portfolio Guidance:</strong> Answering questions about your investments</li>
<li><strong>Tax Efficiency:</strong> Managing portfolios to minimize tax impact</li>
<li><strong>Values Alignment:</strong> Ensuring investments match your ethics</li>
<li><strong>Market Education:</strong> Helping you understand investment concepts</li>
</ul>

<h2>What We Don't Provide</h2>
<p>We don't offer:</p>
<ul>
<li>Comprehensive financial plans</li>
<li>Cash flow/budgeting analysis</li>
<li>Insurance planning</li>
<li>Estate planning documents</li>
<li>Tax preparation services</li>
</ul>

<h2>Why We Focus on Investments</h2>
<p>By specializing in ethical investment management, we can:</p>
<ul>
<li>Provide deeper expertise in values-based investing</li>
<li>Keep our fees low and transparent</li>
<li>Focus on what we do best</li>
<li>Avoid conflicts of interest from selling products</li>
</ul>

<h2>Planning Resources</h2>
<p>For comprehensive planning, we recommend:</p>
<ul>
<li><strong>Fee-Only Financial Planners:</strong> NAPFA.org directory</li>
<li><strong>XY Planning Network:</strong> For younger investors</li>
<li><strong>Garrett Planning Network:</strong> Hourly planning services</li>
<li><strong>CFP Board:</strong> Certified Financial Planner directory</li>
</ul>

<h2>Working Together</h2>
<p>If you have a financial planner, we're happy to:</p>
<ul>
<li>Coordinate on investment strategy</li>
<li>Provide portfolio reports for planning</li>
<li>Implement their asset allocation recommendations</li>
<li>Ensure investments align with overall plan</li>
</ul>

<p>While we focus on investment management, we're always here to help you think through how your portfolio fits into your broader financial picture.</p>""",
                "keywords": "financial planning, investment management, planning services, CFP, fee-only",
            },
            {
                "title": "What's the Best Way to Refer a Friend to Ethical Capital?",
                "slug": "best-way-to-refer-friend",
                "category": "company",
                "priority": 2,
                "featured": False,
                "summary": "How to share Ethical Capital with friends and family who might benefit from ethical investing.",
                "content": """<p>We're honored that you'd like to share Ethical Capital with others! Here are the best ways to make a referral.</p>

<h2>Simple Introduction</h2>
<p>The easiest method is a warm email introduction:</p>
<ul>
<li>Send an email to both your friend and us (support@ec1c.com)</li>
<li>Briefly explain why you think we'd be a good fit</li>
<li>We'll take it from there with your friend's permission</li>
</ul>

<h2>Share Our Resources</h2>
<p>Help them learn about ethical investing:</p>
<ul>
<li>Forward our website: ethicic.com</li>
<li>Share specific articles from our Knowledge Base</li>
<li>Mention our $1 minimum investment</li>
<li>Explain how we've helped with your investments</li>
</ul>

<h2>Schedule a Joint Call</h2>
<p>Sometimes a three-way introduction works best:</p>
<ul>
<li>Schedule a call with you, your friend, and our team</li>
<li>You can share your experience directly</li>
<li>We can answer questions together</li>
<li>Book at: https://tidycal.com/ecic</li>
</ul>

<h2>What to Mention</h2>
<p>Key points that resonate with most people:</p>
<ul>
<li>No investment minimums - start with just $1</li>
<li>Complete transparency in holdings and fees</li>
<li>Investments aligned with personal values</li>
<li>Direct access to decision makers</li>
<li>Simple 1% annual fee with no hidden costs</li>
</ul>

<h2>Referral Program</h2>
<p>While we don't offer financial incentives for referrals (to avoid conflicts of interest), we do:</p>
<ul>
<li>Treat every referral with special care</li>
<li>Keep you updated (with permission) on their progress</li>
<li>Express our gratitude for growing our community</li>
<li>Continue improving our services based on feedback</li>
</ul>

<h2>Thank You!</h2>
<p>Referrals from satisfied clients are the highest compliment we can receive. They help us build a community of conscious investors working toward a more ethical economy.</p>

<p>If you have any questions about making a referral, just let us know!</p>""",
                "keywords": "referral, refer a friend, share, introduction, client referral",
            },
            # Account Management Articles
            {
                "title": "How Do I Transfer My Old 401(k) or 403(b) to Ethical Capital?",
                "slug": "transfer-401k-403b",
                "category": "account",
                "priority": 8,
                "featured": True,
                "summary": "Step-by-step guide to rolling over your retirement accounts to Ethical Capital.",
                "content": """<p>Rolling over an old employer retirement plan is a smart move that gives you more control and investment options. Here's how to do it.</p>

<h2>Why Roll Over?</h2>
<p>Benefits of moving your old 401(k)/403(b):</p>
<ul>
<li>Access to ethical investment options</li>
<li>Lower fees than most employer plans</li>
<li>Consolidate multiple accounts</li>
<li>Better investment choices</li>
<li>Direct professional management</li>
</ul>

<h2>Step-by-Step Process</h2>
<ol>
<li><strong>Open a Rollover IRA with us</strong>
   <ul>
   <li>Complete online application</li>
   <li>Select "Rollover IRA" as account type</li>
   <li>No funding required initially</li>
   </ul>
</li>

<li><strong>Contact your old plan</strong>
   <ul>
   <li>Call the 401(k)/403(b) provider</li>
   <li>Request a "direct rollover" to Ethical Capital</li>
   <li>Provide our custodian details (we'll give you these)</li>
   </ul>
</li>

<li><strong>Complete transfer forms</strong>
   <ul>
   <li>Your old provider will send forms</li>
   <li>We'll help you complete them</li>
   <li>Always choose "direct rollover" to avoid taxes</li>
   </ul>
</li>

<li><strong>Wait for transfer</strong>
   <ul>
   <li>Usually takes 2-4 weeks</li>
   <li>Check arrives at our custodian</li>
   <li>Automatically deposited to your account</li>
   </ul>
</li>

<li><strong>We invest the funds</strong>
   <ul>
   <li>Build your ethical portfolio</li>
   <li>Align with your values</li>
   <li>Begin professional management</li>
   </ul>
</li>
</ol>

<h2>Important Notes</h2>
<ul>
<li><strong>Always use direct rollover:</strong> Avoids 20% tax withholding</li>
<li><strong>60-day rule:</strong> If you receive the check, you must deposit within 60 days</li>
<li><strong>Multiple accounts:</strong> You can consolidate several old accounts</li>
<li><strong>Current employer:</strong> Usually can't roll over active 401(k)</li>
</ul>

<h2>We're Here to Help</h2>
<p>Rollovers can seem complex, but we guide you through every step. Contact us for:</p>
<ul>
<li>Custodian information for forms</li>
<li>Help understanding your options</li>
<li>Assistance with paperwork</li>
<li>Status updates during transfer</li>
</ul>

<p>Most clients find the process easier than expected, and the benefits of consolidation and ethical investing make it worthwhile!</p>""",
                "keywords": "401k rollover, 403b transfer, retirement account, IRA rollover, consolidation",
            },
            {
                "title": "Setting Up Recurring Deposits",
                "slug": "setting-up-recurring-deposits",
                "category": "account",
                "priority": 7,
                "featured": False,
                "summary": "How to automate regular contributions to build wealth consistently.",
                "content": """<p>Automating your investments through recurring deposits is one of the best ways to build wealth consistently. Here's how to set them up.</p>

<h2>Benefits of Recurring Deposits</h2>
<ul>
<li><strong>Dollar-cost averaging:</strong> Reduce market timing risk</li>
<li><strong>Consistent habit:</strong> Build wealth automatically</li>
<li><strong>Convenience:</strong> Set it and forget it</li>
<li><strong>Flexibility:</strong> Adjust or pause anytime</li>
</ul>

<h2>How to Set Up</h2>
<ol>
<li><strong>Log into your account</strong>
   <ul>
   <li>Access your Ethical Capital dashboard</li>
   <li>Navigate to "Funding" or "Deposits"</li>
   </ul>
</li>

<li><strong>Choose recurring option</strong>
   <ul>
   <li>Select "Set up recurring deposit"</li>
   <li>Choose frequency: Weekly, bi-weekly, or monthly</li>
   </ul>
</li>

<li><strong>Enter amount</strong>
   <ul>
   <li>Minimum $1 per deposit</li>
   <li>No maximum limit</li>
   <li>Can differ by account if you have multiple</li>
   </ul>
</li>

<li><strong>Connect bank account</strong>
   <ul>
   <li>Securely link checking or savings</li>
   <li>Verify with micro-deposits if needed</li>
   </ul>
</li>

<li><strong>Confirm schedule</strong>
   <ul>
   <li>Review deposit dates</li>
   <li>Confirm amount and frequency</li>
   <li>Start immediately or pick future date</li>
   </ul>
</li>
</ol>

<h2>Smart Strategies</h2>
<ul>
<li><strong>Align with payday:</strong> Schedule deposits right after you're paid</li>
<li><strong>Start small:</strong> Even $25/month adds up over time</li>
<li><strong>Increase gradually:</strong> Boost deposits with raises</li>
<li><strong>Split goals:</strong> Different amounts for different accounts</li>
</ul>

<h2>Managing Recurring Deposits</h2>
<p>You maintain full control:</p>
<ul>
<li>Pause anytime without penalty</li>
<li>Change amount up or down</li>
<li>Skip individual deposits if needed</li>
<li>Cancel with one click</li>
</ul>

<h2>Common Questions</h2>
<p><strong>What if my bank account is low?</strong><br>
Deposits will fail safely - no overdraft from us. You can retry when ready.</p>

<p><strong>Can I deposit to multiple accounts?</strong><br>
Yes! Set up separate recurring deposits for each account.</p>

<p><strong>Are there fees?</strong><br>
No fees for deposits of any size or frequency.</p>

<p>Start building wealth automatically today with recurring deposits!</p>""",
                "keywords": "recurring deposits, automatic investing, dollar cost averaging, systematic investment",
            },
            {
                "title": "Withdrawing Your Funds",
                "slug": "withdrawing-your-funds",
                "category": "account",
                "priority": 6,
                "featured": False,
                "summary": "How to access your money when you need it, including the withdrawal process and timeline.",
                "content": """<p>Your money is always accessible when you need it. Here's everything you need to know about withdrawing funds.</p>

<h2>How to Request a Withdrawal</h2>
<ol>
<li><strong>Log into your account</strong>
   <ul>
   <li>Go to "Withdraw" or "Transfer" section</li>
   <li>Available 24/7 online</li>
   </ul>
</li>

<li><strong>Enter withdrawal details</strong>
   <ul>
   <li>Amount to withdraw</li>
   <li>Which account (if multiple)</li>
   <li>Destination bank account</li>
   </ul>
</li>

<li><strong>Review and confirm</strong>
   <ul>
   <li>Check amount and destination</li>
   <li>Understand any tax implications</li>
   <li>Submit request</li>
   </ul>
</li>
</ol>

<h2>Processing Timeline</h2>
<ul>
<li><strong>Request received:</strong> Immediately</li>
<li><strong>Securities sold:</strong> Same or next business day</li>
<li><strong>Settlement:</strong> 2 business days (SEC requirement)</li>
<li><strong>Bank transfer:</strong> 1-2 additional days</li>
<li><strong>Total time:</strong> Usually 3-5 business days</li>
</ul>

<h2>Withdrawal Options</h2>
<ul>
<li><strong>Partial withdrawal:</strong> Take only what you need</li>
<li><strong>Full withdrawal:</strong> Close account completely</li>
<li><strong>Recurring withdrawals:</strong> Set up regular distributions</li>
<li><strong>Specific holdings:</strong> We'll optimize which securities to sell</li>
</ul>

<h2>Tax Considerations</h2>
<p>For taxable accounts:</p>
<ul>
<li>We use tax-smart selling to minimize impact</li>
<li>Sell losses first when possible</li>
<li>Provide detailed tax reporting</li>
<li>Consider timing for tax efficiency</li>
</ul>

<p>For retirement accounts:</p>
<ul>
<li>Traditional IRA: Withdrawals are taxable income</li>
<li>Roth IRA: Qualified withdrawals are tax-free</li>
<li>Early withdrawal penalties may apply if under 59½</li>
</ul>

<h2>No Penalties or Fees</h2>
<ul>
<li>No withdrawal fees from Ethical Capital</li>
<li>No account closing fees</li>
<li>No minimum balance requirements</li>
<li>No questions asked</li>
</ul>

<h2>Emergency Withdrawals</h2>
<p>Need funds urgently? Contact us for:</p>
<ul>
<li>Expedited processing when possible</li>
<li>Wire transfer option (bank may charge fee)</li>
<li>Assistance with urgent situations</li>
</ul>

<p>Your money is yours, and we make accessing it as simple as possible while maintaining security and tax efficiency.</p>""",
                "keywords": "withdrawal, access funds, liquidity, cash out, distribution",
            },
            {
                "title": "How Do I Deposit Funds?",
                "slug": "how-do-i-deposit-funds",
                "category": "account",
                "priority": 5,
                "featured": True,
                "summary": "All the ways you can add money to your Ethical Capital investment account.",
                "content": """<p>Funding your account is quick and easy. Here are all the ways you can deposit money to start investing.</p>

<h2>Online Bank Transfer (ACH)</h2>
<p>The most common method:</p>
<ol>
<li>Log into your account</li>
<li>Click "Deposit" or "Add Funds"</li>
<li>Enter amount (minimum $1)</li>
<li>Connect your bank account</li>
<li>Confirm transfer</li>
</ol>
<p><strong>Timeline:</strong> 3-5 business days<br>
<strong>Limits:</strong> Typically $50,000 per day<br>
<strong>Cost:</strong> Free</p>

<h2>Wire Transfer</h2>
<p>For larger deposits or faster processing:</p>
<ol>
<li>Request wire instructions from us</li>
<li>Initiate wire from your bank</li>
<li>Include your account number as reference</li>
<li>Funds invest same day if received by 1 PM ET</li>
</ol>
<p><strong>Timeline:</strong> Same or next business day<br>
<strong>Limits:</strong> No maximum<br>
<strong>Cost:</strong> Your bank may charge $15-30</p>

<h2>Check Deposit</h2>
<p>Mail a physical check:</p>
<ol>
<li>Make check payable to "Altruist FBO [Your Name]"</li>
<li>Include your account number</li>
<li>Mail to address we provide</li>
<li>We'll deposit upon receipt</li>
</ol>
<p><strong>Timeline:</strong> 5-7 business days<br>
<strong>Limits:</strong> No maximum<br>
<strong>Cost:</strong> Free</p>

<h2>Transfer from Another Brokerage</h2>
<p>Move existing investments:</p>
<ol>
<li>Initiate ACATS transfer</li>
<li>We'll help with paperwork</li>
<li>Securities transfer "in kind"</li>
<li>No tax consequences</li>
</ol>
<p><strong>Timeline:</strong> 5-10 business days<br>
<strong>Limits:</strong> No maximum<br>
<strong>Cost:</strong> Free (other broker may charge)</p>

<h2>Rollover from Retirement Account</h2>
<p>Transfer 401(k), 403(b), or IRA:</p>
<ul>
<li>Direct rollover avoids taxes</li>
<li>We provide receiving instructions</li>
<li>Usually arrives as check</li>
<li>See our full rollover guide</li>
</ul>

<h2>Important Notes</h2>
<ul>
<li>All deposits invest immediately upon clearing</li>
<li>No deposit fees from Ethical Capital</li>
<li>Deposits are SIPC insured up to $500,000</li>
<li>Set up recurring deposits for automatic investing</li>
</ul>

<h2>Questions?</h2>
<p>Contact us for help with:</p>
<ul>
<li>Wire instructions</li>
<li>Mailing address for checks</li>
<li>Transfer forms</li>
<li>Large deposit planning</li>
</ul>

<p>Ready to start investing ethically? Fund your account today!</p>""",
                "keywords": "deposit funds, fund account, ACH transfer, wire transfer, account funding",
            },
            {
                "title": "Where Are My Assets Held?",
                "slug": "where-are-my-assets-held",
                "category": "account",
                "priority": 4,
                "featured": False,
                "summary": "Understanding custody, security, and protection of your investments.",
                "content": """<p>Your assets are held by Altruist, an independent qualified custodian, not by Ethical Capital directly. This structure provides important protections.</p>

<h2>What is a Custodian?</h2>
<p>A custodian is a financial institution that:</p>
<ul>
<li>Physically holds your securities</li>
<li>Maintains official records</li>
<li>Processes trades and transactions</li>
<li>Provides regulatory protection</li>
<li>Issues official statements</li>
</ul>

<h2>Why Altruist?</h2>
<p>We chose Altruist because they:</p>
<ul>
<li>Are a modern, technology-first custodian</li>
<li>Provide excellent security and protection</li>
<li>Offer low costs we pass to clients</li>
<li>Share our values of transparency</li>
<li>Have strong regulatory compliance</li>
</ul>

<h2>Your Protections</h2>
<p><strong>SIPC Insurance:</strong></p>
<ul>
<li>Up to $500,000 per account ($250,000 cash)</li>
<li>Protects against custodian failure</li>
<li>Doesn't protect against market losses</li>
</ul>

<p><strong>Separation of Assets:</strong></p>
<ul>
<li>Your assets are held in your name</li>
<li>Segregated from Ethical Capital's assets</li>
<li>Cannot be used for our business operations</li>
<li>Protected from our creditors</li>
</ul>

<p><strong>Regulatory Oversight:</strong></p>
<ul>
<li>Altruist is regulated by SEC and FINRA</li>
<li>Regular audits and examinations</li>
<li>Strict custody requirements</li>
<li>Daily reconciliation requirements</li>
</ul>

<h2>What This Means for You</h2>
<ul>
<li><strong>Direct ownership:</strong> Securities are in your name</li>
<li><strong>Full transparency:</strong> See all holdings and transactions</li>
<li><strong>Independent verification:</strong> Statements from custodian</li>
<li><strong>Easy transfers:</strong> Can move assets if needed</li>
</ul>

<h2>Access and Reporting</h2>
<p>You receive:</p>
<ul>
<li>24/7 online access to your account</li>
<li>Monthly statements from Altruist</li>
<li>Trade confirmations</li>
<li>Annual tax documents</li>
<li>Real-time portfolio viewing</li>
</ul>

<h2>Additional Security</h2>
<ul>
<li>Two-factor authentication</li>
<li>Encrypted connections</li>
<li>Secure document storage</li>
<li>Identity verification</li>
<li>Account alerts</li>
</ul>

<p>Your assets are secure, protected, and always in your control. The custodial structure ensures that even if something happened to Ethical Capital, your investments remain safe and accessible.</p>""",
                "keywords": "custody, custodian, Altruist, asset protection, SIPC insurance, security",
            },
            {
                "title": "How Do I Add or Update a Beneficiary?",
                "slug": "how-do-i-add-update-beneficiary",
                "category": "account",
                "priority": 3,
                "featured": False,
                "summary": "Step-by-step guide to designating beneficiaries for your investment accounts.",
                "content": """<p>Adding beneficiaries ensures your assets transfer smoothly to your chosen recipients. Here's how to set them up.</p>

<h2>Why Add Beneficiaries?</h2>
<ul>
<li>Assets transfer directly, avoiding probate</li>
<li>Faster distribution to loved ones</li>
<li>Clear designation of your wishes</li>
<li>Can reduce estate settlement costs</li>
<li>Maintains privacy (not public record)</li>
</ul>

<h2>How to Add a Beneficiary</h2>
<ol>
<li><strong>Log into your account</strong>
   <ul>
   <li>Go to "Account Settings" or "Profile"</li>
   <li>Select "Beneficiaries" section</li>
   </ul>
</li>

<li><strong>Add beneficiary information</strong>
   <ul>
   <li>Full legal name</li>
   <li>Date of birth</li>
   <li>Social Security Number</li>
   <li>Address</li>
   <li>Relationship to you</li>
   </ul>
</li>

<li><strong>Specify percentage</strong>
   <ul>
   <li>Must total 100%</li>
   <li>Can split among multiple beneficiaries</li>
   <li>Example: Spouse 50%, Child 1 25%, Child 2 25%</li>
   </ul>
</li>

<li><strong>Designate type</strong>
   <ul>
   <li>Primary: First in line to inherit</li>
   <li>Contingent: Inherits if primary unavailable</li>
   </ul>
</li>

<li><strong>Save and confirm</strong>
   <ul>
   <li>Review all information</li>
   <li>Submit changes</li>
   <li>Receive confirmation</li>
   </ul>
</li>
</ol>

<h2>Important Considerations</h2>
<p><strong>For Retirement Accounts:</strong></p>
<ul>
<li>Spouses have special rights</li>
<li>May need spousal consent for non-spouse beneficiary</li>
<li>Different distribution rules apply</li>
</ul>

<p><strong>For Minor Children:</strong></p>
<ul>
<li>Consider setting up a trust</li>
<li>May need custodian until age of majority</li>
<li>Consult estate planning attorney</li>
</ul>

<p><strong>Regular Updates:</strong></p>
<ul>
<li>Review after major life events</li>
<li>Marriage, divorce, births, deaths</li>
<li>Changes in relationships</li>
</ul>

<h2>Updating Beneficiaries</h2>
<p>To change existing beneficiaries:</p>
<ol>
<li>Follow same process as adding</li>
<li>Remove outdated beneficiaries</li>
<li>Add new ones as needed</li>
<li>Adjust percentages</li>
<li>Save changes</li>
</ol>

<h2>No Beneficiary Designated?</h2>
<p>Without beneficiaries:</p>
<ul>
<li>Assets go to your estate</li>
<li>Must go through probate</li>
<li>Delays and costs for heirs</li>
<li>Court determines distribution</li>
</ul>

<p>Take a few minutes today to ensure your beneficiaries are up to date. It's one of the most important steps in protecting your loved ones.</p>""",
                "keywords": "beneficiary, beneficiaries, estate planning, inheritance, account beneficiary",
            },
        ]

        # Create articles
        created_count = 0
        for article_data in articles_data:
            article = FAQArticle.objects.filter(slug=article_data["slug"]).first()
            if not article:
                article = FAQArticle(**article_data)
                support_index.add_child(instance=article)
                article.save_revision().publish()
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f"Created article: {article.title}"),
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f"Article already exists: {article.title}"),
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"\nSuccessfully imported {created_count} missing support articles.",
            ),
        )
        self.stdout.write(
            self.style.SUCCESS(f"Total articles now: {FAQArticle.objects.count()}"),
        )
