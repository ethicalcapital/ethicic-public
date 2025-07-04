-- Update PRI DDQ page content directly via SQL
-- This avoids the sync_to_support_articles issue

UPDATE public_site_priddqpage
SET 
    executive_summary = '<p>Ethical Capital Investment Management is a registered investment adviser specializing in values-based equity investing. We integrate comprehensive ESG criteria throughout our investment process, excluding 57% of the S&P 500 through our proprietary screening methodology.</p><p>Our approach is grounded in the belief that companies avoiding preventable harm to living things while making meaningful contributions to a better future represent superior long-term investment opportunities.</p>',
    
    strategy_governance_content = '<h3>1.1 What is your organisation''s overall approach to responsible investment?</h3>
<p class="ddq-instruction"><em>Your overview (no longer than 400 words) should address the following questions: i) Why does your organisation engage in responsible investment? ii) Does your organisation apply responsible investment principles across all asset classes and strategies, or across a selection? iii) Has your organisation''s approach to responsible investment changed significantly in the past 12 months?</em></p>

<p><strong>i) Why we engage in responsible investment:</strong> Ethical Capital exists to create industry-leading responsible investment strategies. Our mission is to align our clients'' capital with companies that avoid preventable harm to living things and make meaningful contributions to a better future. We do this because we believe it leads to better client outcomes. The companies we exclude are generally lower-quality businesses, and our process benefits significantly from not having to engage with them in much depth.</p>

<p><strong>ii) Application across asset classes:</strong> We are primarily an equity-oriented firm, but we do manage some strategies in fixed income for retail investors. We apply our ethical criteria in those cases as best we can, but are subject to material constraints based on product availability.</p>

<p><strong>iii) Changes in approach:</strong> No significant changes in the past 12 months.</p>

<h3>1.2 Does your organisation have a responsible investment policy?</h3>
<p>We do not segregate responsible investing from regular investing. All of our policy documents can be found on the process page of our website at <a href="https://ethicic.com/process/">ethicic.com/process</a></p>

<h3>1.3 What international standards has your organisation committed to?</h3>
<p>We are signatories to the Plant Based Treaty and work closely with the investor community to advance our mission. As a matter of policy, we do not sign onto statements that require membership payments to the sponsoring body, only activist-led initiatives. An up-to-date list of our current involvements is available at: <a href="https://ethicic.com/support/how-does-ethical-capital-use-its-influence-to-support-its-mission/">ethicic.com/support</a></p>

<h3>1.4 How is responsible investment overseen and implemented?</h3>
<p>Responsible investment is inseparable from regular investment at our organisation. Accordingly, all relevant processes are overseen by our founder and chief investment officer.</p>

<h3>1.5 How are responsible investment objectives incorporated into performance reviews?</h3>
<p>We evaluate all teams on a holistic basis. There is no separate responsibility section as ESG considerations are integral to all investment decisions.</p>

<h3>1.6 What responsible investment training does your organisation provide?</h3>
<p>All non-founding staff undergo a rigorous training program designed to acquaint them with a holistic view of how companies create shared long-term value. Over the first six months of employee tenure, this happens through regular dialogues with the investment team. After that, it happens through staff-specific development plans including external service opportunities and content generation activities.</p>',

    esg_integration_content = '<h3>2.1 How is ESG materiality analysed for this strategy?</h3>
<p>We focus on the degree to which a firm''s revenue is directly associated with positive real-world outcomes. We do not use third-party tools, standards, or data to complete this analysis. Our proprietary approach evaluates companies based on their fundamental business models and revenue streams.</p>

<h3>2.2 How are financially material ESG factors incorporated into this strategy?</h3>
<p>Material ESG factors directly influence our portfolio construction and security selection. In the last twelve months:</p>
<ul>
<li>We exited a position in Eiffage SA (OTC:EFGSY) after uncovering evidence that the firm has failed to properly supervise some of its projects in the Middle East, resulting in significant human rights challenges.</li>
<li>We continued adding to our position in Badger Meter (NYSE:BMI) as their value-added water meters continued to add value to many municipal water systems.</li>
<li>We re-entered our position in ELF cosmetics (NYSE:ELF) after a significant selloff in their stock price coincided with a stronger impact case and continued sales momentum.</li>
</ul>

<h3>2.3 How are ESG screens applied to this strategy?</h3>
<p>We operate a distinctive screening process that materially informs all investment strategies we manage. Our screening methodology is publicly available on GitHub for complete transparency. We are able to apply client-directed screens to our strategies, but prefer to incorporate client ethical concerns into our overall strategy so that all clients can benefit from any given client''s oversight.</p>

<h3>2.4 Does this strategy seek to shape sustainability outcomes?</h3>
<p>We use our own judgement to determine whether each company''s revenue is associated with a positive outcome. While we do not specifically target SDGs or other framework-defined outcomes, our investment process naturally favors companies creating positive real-world impact.</p>

<h3>2.5 How are ESG incidents involving investee companies managed?</h3>
<p>We promptly reach out to all named investor contacts in response to any perceived, potential, or documented ESG incident. We include tracking beacons in our emails that allow us to see how our inquiry is progressing through the company. This, coupled with our approach to lie detection and strategic use of evidence, allows us to evaluate company responses for forthrightness. If we sense that a management team is misrepresenting any detail of the incident, we do not hesitate to reduce exposure.</p>

<h3>2.6 Does your organisation measure whether its responsible investment approach affects performance?</h3>
<p>In our annual performance discussion, we contrast our strategy''s performance with the performance of our index as well as a naive implementation of our ethical criteria. This allows us to isolate the value added by our active management approach.</p>',

    stewardship_content = '<h3>3.1 Does your organisation have a stewardship policy?</h3>
<p>We do not have a formal stewardship policy at this time. Our firm has historically prioritised making its strategies accessible to all clients, regardless of how much money they have available to invest. This has required us to make certain trade-offs. One of the most material is that we are not currently able to vote our proxies.</p>
<p>If we were to secure an institutional client relationship, we would promptly work to address this limitation.</p>

<h3>3.2 How does your organisation determine its stewardship priorities?</h3>
<p>When we determine that an issue affects substantially all of the companies in our portfolio, we will work to make our views public. For example, we have published our perspective on decarbonization strategies that corporate stewards should consider.</p>

<h3>3.3 How does your organisation engage with investee companies?</h3>
<p>Our engagement focuses on direct communication with company management when ESG concerns arise. We maintain a clear escalation process and document all interactions for transparency and accountability.</p>',

    transparency_content = '<h3>4.1 What information is disclosed in regular client reporting?</h3>
<p>We choose to emphasise firm-specific outcomes in our client reporting rather than ratings, carbon intensity, or other aggregated data. For instance, we devoted a section of our client letter to discussion of how one of our companies, a real estate investment trust, was able to preserve a historic mill as a center of commerce in a rural town.</p>

<h3>4.2 How frequently do you report on responsible investment activities?</h3>
<p>We provide quarterly updates to clients that include ESG-related developments within portfolio companies. Annual letters provide more comprehensive analysis of our responsible investment approach and its outcomes.</p>

<h3>4.3 Do you provide transparency on your screening criteria?</h3>
<p>Yes, our complete screening criteria and methodology are publicly available on GitHub at <a href="https://github.com/ethicalcapital/sage/blob/main/screening_policy.md">github.com/ethicalcapital/sage</a>. This ensures complete transparency about what we exclude and why.</p>',

    climate_content = '<h3>5.1 How does your organisation address climate-related risks and opportunities?</h3>
<p>Climate considerations are integrated throughout our investment process. We exclude companies with significant fossil fuel exposure and actively seek opportunities in climate solutions, including renewable energy, sustainable agriculture, and resource efficiency technologies.</p>

<h3>5.2 Do you measure and report on portfolio carbon emissions?</h3>
<p>While we do not currently calculate portfolio-level carbon metrics, our screening process effectively eliminates the highest emitters by excluding fossil fuel companies, airlines, and other carbon-intensive industries.</p>

<h3>5.3 How do you engage with companies on climate issues?</h3>
<p>We have published guidance for corporate stewards on practical decarbonization questions. When climate-related concerns arise with portfolio companies, we engage directly with management to understand their transition plans and risk mitigation strategies.</p>',

    reporting_verification_content = '<h3>6.1 How does your organisation audit the quality of its responsible investment processes?</h3>
<p>We routinely look for third-party groups that credibly assess companies for their alignment with various indicators of sound corporate practice. We routinely spot check our exclusions to ensure that we are adequately incorporating the latest and deepest analysis of companies implicated in objectionable behavior.</p>

<h3>6.2 Is your responsible investment approach subject to external verification?</h3>
<p>As an SEC-registered investment adviser, our processes are subject to regulatory oversight. Our open-source screening criteria on GitHub also allows for public scrutiny and feedback.</p>

<h3>6.3 How do you ensure data quality in your ESG analysis?</h3>
<p>We rely primarily on primary sources including company disclosures, regulatory filings, and direct engagement. This approach, while more labor-intensive than using third-party ESG data providers, ensures higher accuracy and relevance to our specific criteria.</p>',

    additional_content = '<h3>7.1 How is responsible investment integrated into your firm culture?</h3>
<p>Responsible investment is not a separate function but the core of our firm''s identity. Every team member, from investment professionals to operations staff, understands and contributes to our mission of aligning capital with positive outcomes.</p>

<h3>7.2 How do you stay current with responsible investment best practices?</h3>
<p>We actively participate in the responsible investment community through conference attendance, collaborative initiatives, and ongoing dialogue with peers. We also maintain relationships with academic institutions and NGOs working on sustainability issues.</p>

<h3>7.3 What are your future plans for enhancing your responsible investment approach?</h3>
<p>We continuously refine our screening criteria based on new research and evolving understanding of corporate impacts. Future enhancements may include more sophisticated impact measurement and expanded stewardship capabilities as our assets under management grow.</p>

<p><strong>For more information:</strong> Please visit our website at <a href="https://ethicic.com">ethicic.com</a> or contact us at <a href="mailto:hello@ethicic.com">hello@ethicic.com</a></p>'

WHERE page_ptr_id = 387;