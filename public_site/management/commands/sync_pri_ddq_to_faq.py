"""
Management command to sync PRI DDQ content to Support Articles/FAQ.
"""
from django.core.management.base import BaseCommand

from public_site.models import FAQArticle, FAQIndexPage


class Command(BaseCommand):
    help = "Sync PRI DDQ content to Support Articles for FAQ integration"

    def handle(self, *args, **options):
        """Sync PRI DDQ questions to support articles."""

        # Define the DDQ questions manually
        questions = [
            {
                "question": "What is your organisation's overall approach to responsible investment?",
                "answer": "Ethical Capital exists to create industry-leading responsible investment strategies. Our mission is to align our clients' capital with companies that avoid preventable harm to living things and make meaningful contributions to a better future. We do this because we believe it leads to better client outcomes. The companies we exclude are generally lower-quality businesses, and our process benefits significantly from not having to engage with them in much depth.",
                "category": "investment_approach"
            },
            {
                "question": "Does your organisation have a responsible investment policy?",
                "answer": "We do not segregate responsible investing from regular investing. All of our policy documents can be found on the process page of our website.",
                "category": "investment_approach"
            },
            {
                "question": "What international standards, industry guidelines, reporting frameworks, or initiatives has your organisation committed to?",
                "answer": "We are signatories to the plant based treaty and work closely with the investor community whenever we can to advance our mission. As a matter of policy, we do not sign onto statements that require membership payments to the sponsoring body, only activist-led initiatives.",
                "category": "investment_approach"
            },
            {
                "question": "How is responsible investment overseen and implemented within your organisation?",
                "answer": "Responsible investment is inseparable from regular investment at our organisation. Accordingly, all relevant processes are overseen by our founder and chief investment officer.",
                "category": "investment_approach"
            },
            {
                "question": "How are responsible investment objectives incorporated into individual or team performance reviews and compensation mechanisms?",
                "answer": "We evaluate all teams on a holistic basis. There is no separate responsibility section.",
                "category": "investment_approach"
            },
            {
                "question": "What responsible investment training does your organisation provide to staff?",
                "answer": "All non-founding staff have undergone a rigorous training program designed to acquaint them with a holistic view of how companies create shared long-term value. Over the first six months of employee tenure, this happens in regular dialogues with the rest of the investment team. After that, it happens through staff-specific development plans that include external service opportunities, content generation activities, and other opportunities as they arise.",
                "category": "investment_approach"
            },
            {
                "question": "How is ESG materiality analysed for this strategy?",
                "answer": "We focus on the degree to which a firm's revenue is directly associated with positive real-world outcomes. We do not use third-party tools, standards, or data to complete this analysis.",
                "category": "esg_integration"
            },
            {
                "question": "How are financially material ESG factors incorporated into this strategy?",
                "answer": "In the last twelve months: We exited a position in Eiffage SA (OTC:EFGSY) after uncovering evidence that the firm has failed to properly supervise some of its projects in the middle east, resulting in significant human rights challenges. We continued adding to our position in Badger Meter (NYSE:BMI) as their value-added water meters continued to add value to many municipal water systems. We re-entered our position in ELF cosmetics (NYSE:ELF) after a significant selloff in their stock price coincided with a stronger impact case and continued sales momentum.",
                "category": "esg_integration"
            },
            {
                "question": "How are ESG screens applied to this strategy?",
                "answer": "We operate a distinctive screening process that materially informs all investment strategies we manage. We are able to apply client-directed screens to our strategies, but prefer to incorporate client ethical concerns into our overall strategy so that all clients can benefit from any given client's oversight.",
                "category": "esg_integration"
            },
            {
                "question": "Does this strategy seek to shape sustainability outcomes?",
                "answer": "We use our own judgement to determine whether each company's revenue is associated with a positive outcome. With that said, we do not seek to shape sustainability outcomes as defined by the SDGs or other frameworks.",
                "category": "esg_integration"
            },
            {
                "question": "How are ESG incidents involving investee companies managed?",
                "answer": "We promptly reach out to all named investor contacts in response to any perceived, potential, or documented ESG Incident. In these cases, we always take care to include tracking beacons in our emails that allow us to see how our inquiry is progressing through the company. This, coupled with our approach to lie detection and the strategic use of evidence, allows us to evaluate company responses for forthrightness. If we sense that a management team is misrepresenting any detail of the incident, we do not hesitate to reduce exposure. Our overall philosophy is that we want to be in business with teams we trust, so there is no such thing as a minor misrepresentation.",
                "category": "esg_integration"
            },
            {
                "question": "Does your organisation measure whether its responsible investment approach affects the financial performance of this strategy?",
                "answer": "In our annual performance discussion, we contrast our strategy's performance with the performance of our index as well as a naive implementation of our ethical criteria.",
                "category": "esg_integration"
            },
            {
                "question": "Does your organisation have a stewardship policy?",
                "answer": "We do not have a stewardship policy at this time. Our firm has historically prioritised making its strategies accessible to all clients, regardless of how much money they have available to invest. This has required us to make certain trade-offs. One of the most material is that we are not currently able to vote our proxies. If we were to secure an institutional client relationship, we would promptly work to address this.",
                "category": "stewardship"
            },
            {
                "question": "How does your organisation determine its stewardship priorities?",
                "answer": "When we determine that an issue affects substantially all of the companies in our portfolio, we will work to make our views public (as we did in the case of decarbonization). In other cases, we seek to uncover company-specific opportunities for a given firm to address. In general, we seek to make sure that these opportunities align with the company's current priorities as they express them. This allows us to ensure that we are always engaging in a way that is constructive, but also builds a deeper understanding of the opportunities and risks a given company is associated with.",
                "category": "stewardship"
            },
            {
                "question": "What stewardship methods does your organisation use?",
                "answer": "We sought to develop an open letter campaign around carbon removals late last year, but our firm's small size led potential partners to demur from working with us. In general, we emphasise collaborative engagement with the company's management teams. We have found that by asking good questions, expressing our appreciation for their work, and highlighting opportunities we see we can be quite effective. With that said, we hope to grow in size so that we'll be able to use other methods in the future if they are appropriate.",
                "category": "stewardship"
            },
            {
                "question": "What is your organisation's approach to (proxy) voting?",
                "answer": "As noted earlier, we have chosen to prioritise making our strategies available to low-income and low-asset households over voting our proxies at this time. This was a painful decision, and we hope that growth in our asset base will allow us to vote on client securities in time.",
                "category": "stewardship"
            },
            {
                "question": "How are stewardship activities integrated into the investment process?",
                "answer": "One of our largest positions (Agricultural Mortgage Corporation, NYSE:AGM) was selected in part because we believe that constructive engagement with its management team over time will allow us to drive positive outcomes for animals. They are the largest agricultural lender in the United States, which includes a number of loans to animal agriculture that we are not excited about. However, they are still a high quality business with a material role to play in the future of agriculture. We note that since our shareholding began, they have adopted at least one policy we have advocated for: discounted interest rates for farmers using regenerative agricultural practices like no-till, cover crops, and other such practices.",
                "category": "stewardship"
            },
            {
                "question": "How does your organisation assess the effectiveness of its stewardship activities?",
                "answer": "We view stewardship activities as part of the investment research process, and consider the clearest indicator of their effectiveness to be whether we continue to hold the position. In the case of our Farmer Mac (AGM) shareholding, our regular meetings with management have only deepened our understanding of the firm and our conviction that it is driving positive outcomes throughout rural america. It's nice to see them enact programs that we've pushed for at various times, but we lack the ability to directly attribute such actions to our engagement. With that said, we remain happy shareholders. In the case of our Welltower shareholding, we uncovered a failure of governance that was compounded by managerial misrepresentations. We sold the position as a result, and consider that to be a positive outcome for our clients.",
                "category": "stewardship"
            },
            {
                "question": "What information is disclosed in regular client reporting on the responsible investment activities and performance of this strategy?",
                "answer": "We choose to emphasise firm-specific outcomes in our client reporting rather than ratings, carbon intensity, or other data. For instance, we devoted a section of our client letter to discussion of how one of our companies, a real estate investment trust, was able to preserve a historic mill as a center of commerce in a rural town. We then emphasised that the firm's strategy of building multi-use developments makes this part of a pattern, not a photogenic show piece.",
                "category": "reporting"
            },
            {
                "question": "Which disclosure initiatives, and/or regulatory regimes, influence client reporting for this strategy, if any?",
                "answer": "We are not subject to jurisdiction-specific regulation or reporting, and do not report in alignment with any third-party framework.",
                "category": "reporting"
            },
            {
                "question": "How does your organisation audit the quality of its responsible investment processes and/or data?",
                "answer": "We routinely look for third-party groups that credibly assess companies for their alignment with various indicators of sound corporate practice, and will routinely spot check our exclusions to ensure that we are adequately incorporating the latest and deepest analysis of companies implicated in objectionable behavior. Additionally, we seek to update our internal assessments of our investable universe no less than quarterly, which helps us ensure that we are consistently and coherently aligning with the best opportunities in our coverage universe.",
                "category": "reporting"
            },
            {
                "question": "How does your organisation manage ESG risk internally?",
                "answer": "Our internal approach to managing ESG risks is relatively radical, and involves avoiding flights wherever possible, partnering with a sibling company (https://woodcache.org) to originate high-quality carbon removals, and continuously seeking community with others in the investment community to exceed our own expectations.",
                "category": "general"
            },
            {
                "question": "Is there any additional information that you would like to share about your organisation's approach to responsible investment?",
                "answer": "We believe that the investment industry's \"original sin\" is the way it prioritises the perspectives of the wealthy over all other stakeholders. Our firm has been designed to counteract this by ensuring that our strategies are both accessible and understandable to clients regardless of how much wealth they happen to have access to. This is a structural governance advantage, as it allows us to not only serve a more diverse client base than traditional wealth managers, but also maintain direct dialogue with individuals that are deeply engaged with sustainability themes.",
                "category": "general"
            }
        ]

        # Get or create the support index page
        try:
            support_index = FAQIndexPage.objects.first()
            if not support_index:
                self.stdout.write(
                    self.style.ERROR("Support index page not found. Please create one first.")
                )
                return
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Error finding support index: {e}")
            )
            return

        # Sync questions to support articles
        created_count = 0
        updated_count = 0

        for q in questions:
            # Check if article already exists
            try:
                article = FAQArticle.objects.get(title=q["question"])
                # Update existing article
                article.content = f"<p>{q['answer']}</p>"
                article.category = q["category"]
                article.summary = q["answer"][:450] + "..." if len(q["answer"]) > 450 else q["answer"]
                article.keywords = "PRI DDQ responsible investment ESG"
                article.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'Updated support article: {q["question"][:50]}...')
                )
            except FAQArticle.DoesNotExist:
                # Create new article as child of support index
                article = FAQArticle(
                    title=q["question"],
                    content=f"<p>{q['answer']}</p>",
                    category=q["category"],
                    keywords="PRI DDQ responsible investment ESG",
                    priority=5,  # Medium priority
                    summary=q["answer"][:450] + "..." if len(q["answer"]) > 450 else q["answer"],
                )
                support_index.add_child(instance=article)
                article.save()
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created support article: {q["question"][:50]}...')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"\nSync complete! Created {created_count} new articles, updated {updated_count} existing articles."
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                "PRI DDQ questions are now available as searchable FAQ items in the support section."
            )
        )
