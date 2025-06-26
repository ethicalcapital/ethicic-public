from django.core.management.base import BaseCommand
from wagtail.models import Page

from public_site.models import FAQArticle, FAQIndexPage


class Command(BaseCommand):
    help = "Import support articles from Ethical Capital website"

    def handle(self, *args, **options):
        self.stdout.write("Starting support article import...")

        # Get or create the homepage to add support under
        try:
            homepage = Page.objects.get(slug="home")
        except Page.DoesNotExist:
            homepage = Page.objects.first()
            if not homepage:
                self.stdout.write(
                    self.style.ERROR(
                        "No homepage found. Please create a homepage first.",
                    ),
                )
                return

        # Create FAQIndexPage if it doesn't exist
        support_index, created = FAQIndexPage.objects.get_or_create(
            slug="support",
            defaults={
                "title": "Support Center",
                "intro_text": "<p>Find answers to frequently asked questions about Ethical Capital Investment Collaborative.</p>",
                "description": "<p>Our comprehensive support center provides detailed answers to help you understand our investment approach, account management, and ethical screening process.</p>",
                "contact_email": "support@ec1c.com",
                "contact_phone": "+1 347 625 9000",
                "contact_address": "90 N 400 E, Provo, UT, 84606",
                "meeting_link": "https://tidycal.com/ecic",
            },
        )

        if created:
            homepage.add_child(instance=support_index)
            support_index.save_revision().publish()
            self.stdout.write(
                self.style.SUCCESS(f"Created FAQIndexPage: {support_index.title}"),
            )
        else:
            self.stdout.write(f"FAQIndexPage already exists: {support_index.title}")

        # Articles data
        articles_data = [
            {
                "title": "Should I Opt Into the Sweep Program?",
                "category": "altruist",
                "priority": 10,
                "featured": True,
                "summary": "Learn about sweep programs that automatically invest unallocated cash in money market funds to generate additional yield.",
                "content": """<p>There are countless ways to hold cash in your investment account.</p>

<p>In the simplest form, you can just hold cash itself. But there are downsides to that. Specifically, cash doesn't generally pay any interest.</p>

<p>Sweep programs are designed to take unallocated cash and invest it in a money market fund so that clients can generate a small additional yield on their cash holdings. They rarely make the difference between success and failure of an investment program, but can definitely be helpful at the margin.</p>

<p>We encourage clients to opt into Altruist's sweep program for that reason, but clients are free not to do so.</p>""",
                "keywords": "sweep program, cash management, money market fund, yield, interest",
            },
            {
                "title": "Should I Opt In to the Dividend Reinvestment Program (DRIP) for Stocks and ETFs?",
                "category": "altruist",
                "priority": 9,
                "featured": True,
                "summary": "Understand how dividend reinvestment programs work and whether you should opt in when your account is professionally managed.",
                "content": """<p>When you receive a dividend from a stock that you own, it typically arrives in your account as cash. Dividend Reinvestment Programs automatically reinvest those dividends into the securities that sent you the dividend, and can significantly increase your total return.</p>

<p>If your account is managed here, it will be automatically rebalanced about once a month. In effect, this means that we are continuously reallocating all new income and dividends regularly, so it's unlikely that a mountain of dividend cash will build up in your account.</p>

<p>The practical implication of this for our clients is simple: you can opt into the program or not. Your account will be looked after either way.</p>""",
                "keywords": "DRIP, dividend reinvestment, automatic rebalancing, dividends, portfolio management",
            },
            {
                "title": "Should I Opt In to the Securities Lending Program?",
                "category": "altruist",
                "priority": 8,
                "featured": False,
                "summary": "Learn about securities lending programs, their risks and benefits, and whether participation makes sense for your account.",
                "content": """<p>While opening your account, you will be asked whether you'd like to opt into this program or not. Before we get to whether or not you should, here's a bit of an overview of what securities lending is.</p>

<p>Securities lending involves temporarily transferring securities, such as stocks or bonds, from one party (the lender) to another (the borrower).</p>

<p>The borrower typically needs these securities to cover short positions, facilitate trading strategies, or meet collateral requirements. In return, the borrower provides collateral, usually in the form of cash or other securities, to the lender and pays a lending fee.</p>

<p>This activity can be somewhat abstract. If you're relatively new to markets, that's sort of scary on its own. But the risks of allowing your securities to be lent out are extremely limited. And in many cases, the firms sponsoring these securities lending programs share the extra income with clients.</p>

<p>In the case of Altruist, those fees are not shared with our clients. So while we do not see a tangible harm to participating in this program at this time we also don't mind if our clients opt out of it.</p>""",
                "keywords": "securities lending, lending fees, collateral, short positions, program participation",
            },
            {
                "title": "How Much Does This Cost?",
                "category": "company",
                "priority": 10,
                "featured": True,
                "summary": "Understanding Ethical Capital's fee structure and what you pay for investment management services.",
                "content": """<p>Clients pay Ethical Capital 1% of their account's value each year in quarterly installments.</p>""",
                "keywords": "fees, cost, 1%, quarterly, investment management fees",
            },
            {
                "title": "What are your investment minimums?",
                "category": "company",
                "priority": 9,
                "featured": True,
                "summary": "Learn about the minimum investment required to open an account with Ethical Capital.",
                "content": """<p>Our internally managed strategies have a minimum investment of $1.</p>""",
                "keywords": "minimum investment, $1, account opening, investment requirements",
            },
            {
                "title": "Who can invest with Ethical Capital Investment Collaborative?",
                "category": "company",
                "priority": 8,
                "featured": True,
                "summary": "Eligibility requirements for opening an investment account with Ethical Capital.",
                "content": """<p>Anyone eligible to open a US Bank account can open an investment account with us.</p>""",
                "keywords": "eligibility, US bank account, investment account, requirements",
            },
            {
                "title": "Is Ethical Capital a Fiduciary?",
                "category": "company",
                "priority": 7,
                "featured": False,
                "summary": "Confirmation of Ethical Capital's fiduciary status and what that means for clients.",
                "content": """<p>Yes, Ethical Capital is a Fiduciary.</p>""",
                "keywords": "fiduciary, fiduciary duty, regulatory status, client protection",
            },
            {
                "title": "Can I exclude certain stocks from my portfolio?",
                "category": "investment",
                "priority": 10,
                "featured": True,
                "summary": "Learn how to customize your portfolio by excluding specific stocks that don't align with your values.",
                "content": """<p>Yes, Ethical Capital is happy to discuss and can easily implement stock exclusions according to your preferences.</p>""",
                "keywords": "stock exclusions, portfolio customization, ethical preferences, values alignment",
            },
            {
                "title": "Is It Ethical to Invest in Real Estate?",
                "category": "investment",
                "priority": 8,
                "featured": False,
                "summary": "Exploring the ethical considerations around real estate investing and how Ethical Capital approaches this sector.",
                "content": """<p>There's a lot of informed apprehension about investing in real estate.</p>

<p>After all, it's not hard to find examples of landlords or real estate developers behaving improperly. But there's a lot of nuance in a deeper ethical analysis of this massive sector.</p>

<p>In response to a question from a client, Sloane explores the ethical considerations that are relevant to these investments from her standpoint and gives an overview of the investments we currently hold in our flagship Global Opportunities strategy.</p>""",
                "keywords": "real estate, ethical investing, landlords, property development, Global Opportunities strategy",
            },
            {
                "title": "How can I balance my own needs and my desire to give generously?",
                "category": "planning",
                "priority": 9,
                "featured": True,
                "summary": "Practical guidance on sustainable philanthropy and balancing personal financial security with generous giving.",
                "content": """<p>When Gabe pulled together some resources to help you on your philanthropic journey, he took care to include the following guidance for folks interested in giving generously at the top of the article:</p>

<p>Giving is best understood as a continuous practice, not a one-time check writing extravaganza. The most effective donors tend to view it as something they try to get better at over time, and often develop an intensely personal sense of what matters.</p>

<p>In other words, even though it would be amazing to make a huge donation to your favorite organization through great personal sacrifice, it would be much healthier to support them in ways that are sustainable for you.</p>

<p>That can include giving non-monetary resources like your time and energy, but also remembering that you're no good to the causes you care about if you don't take care of yourself.</p>

<p>Think about what they tell you on airplanes: 'put on your own oxygen mask first before assisting other passengers.' This is intensely practical! If you help others without thinking about yourself, you stand a very good chance of making things worse overall by putting yourself into a position where you need saving.</p>

<p>So what should you do? Here are a couple of steps that might feel productive and impactful apart from volunteering:</p>

<ul>
<li>Identify the organizations you'd like to support and put them in your will. That way the organizations you care about will get your resources when you're no longer using them.</li>
<li>Organize a get-together with a suggested donation to your favorite organization. For bonus points, provide some resources to the folks who attend that help them see why the cause matters to you.</li>
<li>Spend time amplifying messages from activists and organizations you care about on your social media platforms.</li>
<li>Decide in advance to give a percentage of any extra money you come into to causes you care about, but only if it doesn't put your personal finances in peril.</li>
<li>Take steps to be someone that others can rely on in emergency situations by keeping things like naloxone and band-aids handy while you're out moving through the world.</li>
</ul>

<p>The most important thing to remember is that you're not alone. As you navigate these complex tradeoffs, please never hesitate to use the team at Ethical Capital as a resource.</p>

<p>Thanks to Jasmine Rashid for asking these questions in her newsletter and inspiring us to pull this help page together.</p>""",
                "keywords": "philanthropy, giving, sustainable donating, financial planning, charity, ethical tradeoffs",
            },
        ]

        # Create articles
        created_count = 0
        for article_data in articles_data:
            article, created = FAQArticle.objects.get_or_create(
                slug=article_data["title"]
                .lower()
                .replace(" ", "-")
                .replace("?", "")
                .replace("(", "")
                .replace(")", "")
                .replace('"', "")
                .replace("'", ""),
                defaults=article_data,
            )

            if created:
                support_index.add_child(instance=article)
                article.save_revision().publish()
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f"Created article: {article.title}"),
                )
            else:
                self.stdout.write(f"Article already exists: {article.title}")

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully imported {created_count} support articles. "
                f"Support index available at: {support_index.get_url()}",
            ),
        )
