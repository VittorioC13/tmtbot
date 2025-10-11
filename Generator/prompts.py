section1Prompt = """
1. RECENT TMT M&A ACTIVITY

=======================================================================================================================================================================================================
qualification_rules (softened):
  Qualify an item for DEAL TIER (Tier 1) if BOTH of these buckets are satisfied:

  A) action_signal (need ≥1):
     - acquisition / acquire / acquiring / bought / buyout
     - merger / merge / agreed to merge / merger-of-equals / reverse merger
     - take-private / privatization
     - carve-out / divestiture / spin-off
     - IPO or direct listing verbs: files prospectus/DRHP/F-1/S-1, prices IPO, lists
     - strategic equity: takes X% stake, majority stake, joint venture, board rights, exclusivity

  B) materiality_signal (need ≥1):
     - a hard number tied to the transaction (deal value, stake %, valuation, offer size/shares, multiple)
     - OR explicit control language (majority, control, board seats/rights, exclusivity)

  Notes:
    - Missing detailed multiples or segment tables does NOT disqualify a deal; use "N/A" where data isn’t in context.
    - Routine wording like “plans/consider/explore” alone is NOT an action_signal unless paired with a filing/pricing/listing or an explicit control/majority/board-rights statement.

do_not_include (minimal but firm):
  - routine fund/ETF/13F trading (increased/trimmed/holds) unless framed as strategic stake that meets materiality_signal
  - earnings, product launches, or partnerships with no equity/control
  - vague “planning to IPO next year” with no filing/pricing/listing/control

tiering_policy:
  - First, select up to TWO items that pass DEAL TIER (Tier 1) with the richest disclosed data.
  - If fewer than TWO exist, fill remaining slots with MARKET-REP TIER (Tier 2):
      * Items that best capture current Consumer & Retail market conditions (pricing power, demand trends, traffic, basket size, promotional intensity, retail sales, confidence, policy impacts), and have concrete metrics (comps %, revenue growth %, margins %, traffic %, ASP).
      * Exclude fund trading and rumor-only pieces.
  - If zero items exist for BOTH tiers, output exactly:
    @@@ Today is a peaceful day, nothing big happened in the Consumer space.

data_missing_policy:
  - If specific multiples/segment tables are not present in the provided context/company block, skip and proceed. Do not exclude otherwise-qualifying deals.

Choose max 2 with highest materiality (deal size, control, market impact) and richest disclosed data.

If only 1 qualifies, include just 1.

If 0 qualify, output the following line EXACTLY: "@@@ Today is a peaceful day, nothing big happened in the Consumer space."
=======================================================================================================================================================================================================

CRITICAL: Focus on ONLY 2 of the most significant M&A deals, IPOs, or major transactions from the provided news items. Prioritize deals with the most detailed financial information and market impact.
ONLY SELECT NEWS WHERE A corporate transaction is specifically reported: M&A/merger, acquisition/take-private, carve-out/divestiture/spin-off, IPO/direct listing, joint venture/strategic partnership with equity, or a significant strategic stake (≥10% ownership or ≥USD 100M consideration, or board/control rights). Exclude routine portfolio trades by funds (e.g., “asset manager purchased shares”) unless they meet the threshold above.
If there is only one recent deal, then just do one deal.
For each of the 2 selected deals, ONLY provide analysis with the following structured information:

**Deal Analysis Structure:**
- **Deal Size:** [USD amount - provide specific numbers when available, estimate based on comparable deals if not specified]
- **Deal Size Category:** [Define deal size: Small cap (<$2B), Mid cap ($2B-$10B), Large cap (>$10B)]
- [Classify today's deal's nature as either Horizontal/Vertical/Tuck-in&Bolt on/Carve out/Conglomerate]
- **Valuation Multiples:** [Detailed analysis of EV/EBITDA, P/E, or other relevant multiples with industry context and comparison to peers]
- **Companies:** [Buyer] acquiring [Target] - include company descriptions and market positions
- **Date Announced:** [Specific date if mentioned, or approximate timeline]
- **Strategic Rationale:** [In-depth analysis of the strategic logic, including market positioning, synergies, competitive advantages, and long-term strategic vision]
- **Risk Analysis:** [Comprehensive risk assessment including integration risks, regulatory challenges, market risks, execution risks, and potential value destruction scenarios]

**Key Financials Analysis:** 
For each deal, provide comprehensive financial analysis including:
- **Revenue Breakdown:** Revenue breakdown based on business segments (e.g., Apple revenue by products: iPhone, Mac, Services, etc. rather than by regions) + percentage share + year-over-year growth for 3 years (Only include if applicable, if no data is available, discard)
- **Profitability Ratios:** EBITDA/revenue, Net Income/revenue ratios (Only include if applicable, if no data is available, discard)
- **Leverage Analysis:** Debt-to-Equity ratio and analysis of long-term vs short-term debt structure
- **Asset Operating Efficiency:** Working capital analysis, inventory turnover days, accounts receivable turnover days, and accounts payable turnover days
- **Valuation Context:** Combine these financial metrics with P/E and EV/EBITDA multiples for comprehensive analysis

**Profitability Metrics:**  (Only include if applicable, if no data is available, discard)
-EBITDA, EBIT, Net Income and year-over-year growth for 3 years (WRITE THIS IN THE FORM OF A TABLE, see formatting guidelines below)

**Purpose:** Use this financial analysis to roughly assess performance and business growth/decline trends, then infer the strategic rationale (e.g., whether the acquisition target provides new businesses/technologies/brand influence that the parent company lacks)

**Analysis Requirements:**
- Provide specific valuation multiples with industry benchmarks and peer comparisons
- Include detailed rationale with strategic context and market implications
- Conduct thorough risk analysis with specific risk factors and mitigation strategies
- Use concrete data points and financial metrics wherever possible
- Focus on deals with the most significant TMT sector impact and detailed financial information
- Specify capital structure

------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Formatting guidelines:
Use ### as start of sections
Use #### as start of subsections
Use **title:** as start of subsections
Use - ** as bullet points
Use @@@ to bold a line

To draw tables, use the following format:
| A | B |
| --- | --- |
| a1 | b1 |
| a2 | b2 |


IMPORTANT!
USE ONLY ONE FORMATTING PATTING PER LINE AND ONLY USE AT THE START OF A LINE!


For instance: 
- **Apple Inc. (AAPL)**: Mandated to evaluate acquisitions in the AI space, with a focus on startups that can enhance its product offerings. The timeline for this initiative is projected for Q2 2026, as Apple aims to strengthen its competitive edge in AI.
This is fine
But never do this:
- **Indiegogo Acquisition by Gamefound**: This transaction is progressing, with regulatory approvals anticipated by **Q4 2025**. The integration aims to combine Indiegogo's **38 million users** with Gamefound's technology, thereby enhancing their market position in the crowdfunding space.
Instead of "**Q4 2025**", just do Q4 2025. The same applies to every other line pats


When adding links, use this EXACT format: **Link title** ([Link](https://linkURL))
example: **JPMorgan Reports Increased M&A Activity in TMT Sector** ([Link](https://www.businessinsider.com/merger-acquisition-trends-1h-hreport-sponsors-volumes-anu-aiyengar-jpmorgan-2025-7))
MAKE SURE THE LINKS MATCH THEIR TITLES
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

**Example Structure:**
### 1. RECENT TMT M&A ACTIVITY

**Deal 1: [Company Name] Acquisition**
**Deal Title with Link** ([Link](URL))
- **Deal Size:** $X billion (or specific amount)
- **Valuation Multiples:** EV/EBITDA of X.Xx (vs industry average of X.Xx), P/E of X.Xx
- **Companies:** [Detailed company descriptions and market positions]
- **Date Announced:** [Specific date]
- **Strategic Rationale:** [Comprehensive strategic analysis with market context]
- **Risk Analysis:** [Detailed risk assessment with specific factors]
- **Key Financials Analysis:** [Revenue breakdown by business, profitability metrics, leverage analysis, asset efficiency, and valuation context]

**Deal 2: [Company Name] Acquisition** |(Include only if available, if not, just do nothing)
[Same detailed structure as Deal 1]

Focus on quality over quantity - provide data-driven analysis of deals rather than superficial coverage of many deals.

DO NOT INCLUDE a Recommended Readings
"""

section2Prompt = """
2. MARKET DYNAMICS & SENTIMENT

(Provide a multi-paragraph, in-depth analysis)
- Overall TMT sector sentiment, with breakdowns by subsector, geography, and deal type
- Key market drivers and headwinds, with supporting data
- Subsector performance analysis (e.g., software, media, telecom, fintech, AI)
- Trading multiples trends, with specific numbers and comparisons
- Notable investor/analyst reactions, with quotes or examples
- Actionable insights for bankers and investors

**Format:**
Use ### as start of sections
Use #### as start of subsections
Use **title:** as start of subsections
Use - ** as bullet points
Use @@@ to bold a line

IMPORTANT!
USE ONLY ONE FORMATTING PATTING PER LINE AND ONLY USE AT THE START OF A LINE!

For instance: 
- **Apple Inc. (AAPL)**: Mandated to evaluate acquisitions in the AI space, with a focus on startups that can enhance its product offerings. The timeline for this initiative is projected for Q2 2026, as Apple aims to strengthen its competitive edge in AI.
This is fine
But NEVER EVER do it this:
- Indiegogo Acquisition by Gamefound : This transaction is progressing, with regulatory approvals anticipated by **Q4 2025**. The integration aims to combine Indiegogo's **38 million users** with Gamefound's technology, thereby enhancing their market position in the crowdfunding space.
Instead of "**Q4 2025**", just do Q4 2025. The same applies to every other line pats. DO NOT PUT LINE PAT IN THE MIDDLE OF LINES

DO NOT PUT LINKS IN THIS SECTION

**Example Structure**
### 2. MARKET DYNAMICS & SENTIMENT

The TMT (Technology, Media, and Telecommunications) sector is currently experiencing a mixed sentiment, characterized by cautious optimism amid ongoing regulatory scrutiny and evolving technological advancements. The overall sentiment is influenced by various factors, including macroeconomic conditions, investor confidence, and sector-specific trends.

@@@ Subsector Breakdown:
  - **Technology:** The technology subsector remains robust, driven by advancements in AI, cloud computing, and cybersecurity. For instance, Delta Air Lines' utilization of AI for dynamic pricing reflects a growing trend where companies leverage technology to enhance operational efficiency and customer experience.
  - **Media:** The media subsector is witnessing a transformation as companies like The Verge enhance audience engagement through new digital features. However, traditional media faces challenges from digital platforms.
  - **Telecommunications:** The telecom sector is innovating with low-latency technologies, as demonstrated by T-Mobile's introduction of the L4S standard for 5G, which aims to improve user experience in real-time applications.
  - **Fintech:** The fintech space continues to thrive, with companies exploring new business models and partnerships, such as Indiegogo's acquisition by Gamefound, which aims to integrate crowdfunding communities.
  - **AI:** The AI subsector is particularly hot, with companies racing to implement AI solutions across various industries, including automotive, where BYD is challenging Tesla's self-driving model by promising to cover AI failures.

#### Key Market Drivers and Headwinds

 @@@ Drivers:
  - **Technological Advancements:** Continuous innovation in AI, 5G, and cloud computing is driving growth across TMT sectors. For example, T-Mobile's low-latency technology is expected to enhance the performance of applications reliant on real-time data.
  - **Increased Investment:** Venture capital and private equity investments remain strong, particularly in tech and fintech, as investors seek to capitalize on emerging trends.

 @@@ Headwinds:
  - **Regulatory Scrutiny:** Increased regulatory scrutiny, especially in the tech sector, poses risks to M&A activities and market valuations. Companies are navigating complex compliance landscapes, which can delay or derail potential deals.
  - **Economic Uncertainty:** Global economic conditions, including inflation and geopolitical tensions, may impact consumer spending and investment in technology.

#### Subsector Performance Analysis

- **Software:** The software sector continues to perform well, driven by demand for cloud solutions and enterprise software. Companies focusing on SaaS models are particularly well-positioned for growth.
- **Media:** Media companies are adapting to changing consumer preferences, with a shift towards digital content consumption. However, traditional media faces declining revenues from advertising.
- **Telecom:** Telecom operators are investing heavily in infrastructure to support 5G deployment, which is expected to drive new revenue streams from IoT and enhanced mobile services.
- **Fintech:** The fintech sector is thriving, with innovations in payment solutions and digital banking. The acquisition of Indiegogo by Gamefound highlights the consolidation trend in this space.
- **AI:** The AI subsector is booming, with applications across various industries, including healthcare, finance, and automotive. Companies are investing heavily in AI capabilities to maintain competitive advantages.

#### Trading Multiples Trends

@@@ Valuation Multiples: As of Q2 2025, the average EV/EBITDA multiple for the TMT sector is approximately 15.5x, with notable variations across subsectors:
  - **Software:** 20.3x
  - **Media:** 12.1x
  - **Telecom:** 9.8x
  - **Fintech:** 18.7x
  - **AI:** 22.5x

These multiples indicate a premium for high-growth sectors like software and AI, while traditional sectors like telecom and media are trading at lower multiples due to slower growth prospects.

@@@ Notable Investor/Analyst Reactions

- Analysts are generally optimistic about the long-term prospects of the TMT sector, citing technological advancements as a key driver of growth. For instance, an analyst at a leading investment bank commented, "The integration of AI across industries is not just a trend; it's a fundamental shift that will redefine business models and consumer interactions."

#### Actionable Insights for Bankers and Investors

- **Focus on High-Growth Areas:** Investors should prioritize sectors with strong growth potential, such as AI and fintech, while being cautious with traditional media and telecom investments.
- **Monitor Regulatory Developments:** Staying informed about regulatory changes is crucial for assessing risks in tech and media investments.
- **Leverage Technology Partnerships:** Companies should explore strategic partnerships and acquisitions to enhance their technological capabilities and market positioning.
- **Evaluate Valuation Metrics:** Investors should consider current trading multiples and sector performance when making investment decisions, particularly in high-growth subsectors.

In summary, the TMT sector is navigating a complex landscape characterized by both opportunities and challenges. By focusing on technological advancements and understanding market dynamics, investors and bankers can position themselves for success in this evolving environment.

"""

section3Prompt = """
3. BANKING PIPELINE

(Provide a multi-paragraph, in-depth analysis)
- Deal Pipeline (Transaction Pipeline):
  * Live deals: Transactions currently in progress (M&A in due diligence, upcoming IPOs), with details and expected timing
  * Mandated deals: Transactions with secured mandates but not yet fully launched, with client names and deal types if possible
  * Pitching-stage deals: Active pitches and client discussions for potential mandates, with sector/client focus
- Pipeline tracking metrics:
  * Expected revenue/fees from active pipeline, with breakdowns
  * Timing projections (Q2 close, Q4 IPO, etc.)
  * Workload allocation and capacity analysis (e.g., analyst/associate bandwidth)
  * Forecasting and strategic planning implications
- Notable pipeline developments and competitive landscape, with examples
- Actionable insights for team management and business development

**Format:**
Use ### as start of sections
Use #### as start of subsections
Use **title:** as start of subsections
Use - ** as bullet points
Use @@@ to bold a line

IMPORTANT!
USE ONLY ONE FORMATTING PATTING PER LINE AND ONLY USE AT THE START OF A LINE!

For instance: 
- **Apple Inc. (AAPL)**: Mandated to evaluate acquisitions in the AI space, with a focus on startups that can enhance its product offerings. The timeline for this initiative is projected for Q2 2026, as Apple aims to strengthen its competitive edge in AI.
This is fine
But never do this:
- Indiegogo Acquisition by Gamefound : This transaction is progressing, with regulatory approvals anticipated by **Q4 2025**. The integration aims to combine Indiegogo's **38 million users** with Gamefound's technology, thereby enhancing their market position in the crowdfunding space.
Instead of "**Q4 2025**", just do Q4 2025. The same applies to every other line pats

**Follow the formatting of the Example Structure:**
### 3. BANKING PIPELINE

The current banking pipeline in the TMT sector reflects a dynamic landscape with a mix of live deals, mandated transactions, and active pitches. This section provides a comprehensive analysis of the ongoing activities, expected revenue, and strategic implications for our team.

#### Deal Pipeline

@@@ Live Deals:
- **Delta Air Lines (DAL)**: Currently in discussions for a strategic partnership leveraging AI for dynamic pricing. The deal is in the due diligence phase, with an expected close in Q3 2025. This partnership could enhance Delta's revenue management capabilities, potentially increasing ticket sales by up to 15%.
  
- **Indiegogo Acquisition by Gamefound**: This transaction is moving forward, with regulatory approvals anticipated by Q4 2025. The integration aims to combine Indiegogo's 38 million users with Gamefound's technology, enhancing their market position in crowdfunding.

@@@ Mandated Deals:
- **Meta Platforms (META)**: Secured a mandate to explore strategic partnerships related to AI development, particularly in response to EU regulations. The deal is expected to launch in Q1 2026, focusing on compliance and innovation strategies.
  
- **Apple Inc. (AAPL)**: Mandated to evaluate acquisitions in the AI space, with a focus on startups that can enhance its product offerings. The timeline for this initiative is projected for Q2 2026, as Apple aims to strengthen its competitive edge in AI.

@@@ Pitching-Stage Deals:
- **Telecom Sector**: Active discussions with several telecom operators regarding potential M&A opportunities to consolidate market share in the 5G space. Clients include Verizon (VZ) and AT&T (T), with pitches expected to finalize by Q3 2025.
  
- **Fintech Startups**: Engaging with various fintech companies for potential investment banking services, focusing on those that are innovating in payment solutions and blockchain technology. Notable clients include Square (SQ) and Stripe, with discussions ongoing.

#### Pipeline Tracking Metrics

@@@ Expected Revenue/Fees: The active pipeline is projected to generate approximately $25 million in fees, broken down as follows:
  - **Live Deals**: $10 million
  - **Mandated Deals**: $8 million
  - **Pitching-Stage Deals**: $7 million

@@@ Timing Projections:
  - **Q2 2025**: Expected close for Delta Air Lines partnership.
  - **Q4 2025**: Anticipated completion of the Indiegogo acquisition.
  - **Q1 2026**: Launch of Meta's strategic partnership initiatives.

- **Workload Allocation and Capacity Analysis**: 
  - Current analyst and associate bandwidth is at 75%, with a need for additional resources as the pipeline expands. It is recommended to onboard two additional analysts to manage the increased workload effectively.

- **Forecasting and Strategic Planning Implications**: The pipeline indicates a strong demand for advisory services in AI and telecom sectors. Strategic planning should focus on enhancing capabilities in these areas to capitalize on emerging opportunities.

#### Notable Pipeline Developments and Competitive Landscape

- The competitive landscape is intensifying, particularly in the AI sector, where companies like Apple and Meta are vying for leadership. The recent announcement of Trump's AI Action Plan could alter the regulatory environment, impacting deal structures and valuations.
  
- Additionally, the rise of AI insurance startups, such as the one founded by a former Anthropic executive, indicates a growing market for risk management in AI deployment, which could lead to new advisory opportunities.

#### Actionable Insights for Team Management and Business Development

- **Resource Allocation**: Given the anticipated increase in deal flow, it is crucial to allocate resources effectively. Hiring additional analysts will ensure that the team can manage the workload without compromising service quality.
  
- **Sector Focus**: Prioritize business development efforts in high-growth sectors such as AI and fintech, where demand for advisory services is expected to surge. This focus will position the firm as a leader in these emerging markets.

- **Client Engagement**: Maintain proactive communication with clients in the pipeline to ensure alignment on expectations and timelines. Regular updates will help build trust and facilitate smoother transaction processes.

In summary, the banking pipeline is robust, with significant opportunities across various TMT subsectors. By strategically managing resources and focusing on high-potential areas, the team can maximize its impact and drive successful outcomes for clients.
"""

section4Prompt = """
4. STAKEHOLDER IMPACT & FORWARD-LOOKING ANALYSIS

(Provide a multi-paragraph, in-depth analysis)
- Deal-specific impacts on:
  * Shareholders (value creation/dilution, with scenario analysis and numbers)
  * Employees (synergies, restructuring, retention, with examples)
  * Competitors (market positioning, with specific competitor moves)
  * Customers (product/service implications, with case studies)
- Market reaction and analyst commentary, with quotes or data
- Expected market reaction, with scenario analysis
- Potential counter-bids or competing offers, with likelihood assessment
- Similar deals likely to follow, with sector consolidation predictions
- Key risks and mitigants, with detailed breakdowns
- Actionable insights for clients and bankers

**Format:**
Use ### as start of sections
Use #### as start of subsections
Use **title:** as start of subsections
Use - ** as bullet points
Use @@@ to bold a line

IMPORTANT!
USE ONLY ONE FORMATTING PATTING PER LINE AND ONLY USE AT THE START OF A LINE!

For instance: 
- Value Creation: In a scenario where Company A (e.g. Zoom Video Communications, Inc.(ZM)) acquires Company B (e.g. Slack Technologies, Inc. (WORK)), the combined entity could see a revenue increase of approximately 20% due to enhanced product offerings.
But never ever do this:
- Indiegogo Acquisition by Gamefound : This transaction is progressing, with regulatory approvals anticipated by **Q4 2025**. The integration aims to combine Indiegogo's **38 million users** with Gamefound's technology, thereby enhancing their market position in the crowdfunding space.
Instead of "**Q4 2025**", just do Q4 2025. The same applies to every other form of nested line pats

**Follow the formatting of the Example Structure:**
### 4. STAKEHOLDER IMPACT & FORWARD-LOOKING ANALYSIS

The implications of M&A transactions in the TMT sector extend beyond immediate financial metrics, affecting various stakeholders including shareholders, employees, competitors, and customers. This analysis delves into the potential impacts of a hypothetical acquisition, providing a comprehensive view of the landscape.

#### Deal-Specific Impacts on Stakeholders

- **Shareholders:** Deal-specific impacts on shareholders can be significant, influencing both value creation and dilution.
  - **Value Creation:** In a scenario where Company A (e.g., Zoom Video Communications, Inc. (ZM)) acquires Company B (e.g., Slack Technologies, Inc. (WORK)), the combined entity could see a revenue increase of approximately 20% due to enhanced product offerings. Assuming a pre-deal market cap of $20 billion for Zoom, a successful integration could increase shareholder value by $4 billion.
  - **Dilution:** Conversely, if the acquisition is financed through stock, existing shareholders may experience dilution. For instance, if Zoom issues 10% of its shares to finance the deal, existing shareholders could see their ownership stake decrease, potentially leading to a 5% drop in share price post-announcement.

- **Employees:** Impacts on employees often involve synergies, restructuring, and retention strategies.
  - **Synergies:** A merger between Disney (DIS) and 21st Century Fox (FOXA) led to substantial cost synergies, with estimates of $2 billion in annual savings. This was achieved through streamlined operations and shared resources.
  - **Restructuring:** However, such deals often lead to layoffs. In the Disney-Fox merger, approximately 7,000 jobs were cut, highlighting the need for careful planning to retain key talent.
  - **Retention:** Companies may implement retention bonuses to keep critical employees during the transition. For example, in the acquisition of LinkedIn by Microsoft (MSFT), retention packages were offered to key LinkedIn executives to ensure continuity.

- **Competitors:** The competitive landscape can shift dramatically post-acquisition.
  - **Market Positioning:** Following the merger of T-Mobile US, Inc. (TMUS) and Sprint Corporation (S), competitors such as Verizon Communications Inc. (VZ) and AT&T Inc. (T) had to adapt their strategies to maintain market share. This included aggressive pricing strategies and enhanced service offerings.
  - **Specific Competitor Moves:** Verizon responded with a $10 billion investment in 5G infrastructure to counter the combined entity's market strength.

- **Customers:** Customer implications can vary based on the nature of the deal.
  - **Product/Service Implications:** The merger of AT&T and Time Warner allowed AT&T to bundle media content with telecommunications services, enhancing customer value. This strategy led to a 15% increase in bundled service subscriptions.
  - **Case Studies:** The acquisition of WhatsApp by Facebook (FB) resulted in enhanced messaging features, directly benefiting users with improved service offerings.

#### Market Reaction and Analyst Commentary

- **Market Reaction:** The immediate market reaction to M&A announcements can be volatile.
  - For example, when Salesforce (CRM) announced its acquisition of Slack, shares of Salesforce initially dipped by 5% before recovering as analysts recognized the long-term strategic benefits.
- **Analyst Commentary:** Analysts often provide insights that shape market perceptions. A notable quote from a Morgan Stanley analyst post-acquisition was, "This deal positions Salesforce to dominate the enterprise collaboration space, despite initial market skepticism."

#### Expected Market Reaction and Scenario Analysis

- **Scenario Analysis:** The market's reaction can be assessed through various scenarios:
- **Positive Scenario:** If the acquisition leads to successful integration and revenue growth, shares could rise by 15% within six months.
- **Negative Scenario:** If integration challenges arise, shares could decline by 10%, reflecting investor concerns about operational execution.

#### Potential Counter-Bids or Competing Offers

- **Likelihood Assessment:** The likelihood of counter-bids can vary based on market conditions.
-  In the case of the proposed acquisition of T-Mobile by Sprint, there were rumors of interest from Dish Network (DISH), highlighting the competitive nature of the TMT sector. However, the likelihood of a successful counter-bid is moderate, as regulatory hurdles often deter competing offers.

#### Similar Deals Likely to Follow

- **Sector Consolidation Predictions:** The TMT sector is expected to see continued consolidation.
- Analysts predict that as companies seek to enhance their technological capabilities, similar deals will emerge, particularly in the AI and cloud computing spaces. Companies like IBM (IBM) and Oracle (ORCL) may pursue acquisitions to bolster their cloud offerings.

#### Key Risks and Mitigants

  - **Integration Risks:** Integration challenges can lead to operational disruptions. Mitigants include appointing experienced integration teams and setting clear milestones.
  - **Regulatory Risks:** Regulatory scrutiny can delay or block deals. Engaging with regulators early in the process can help mitigate these risks.
  - **Market Risks:** Market volatility can impact deal valuations. Structuring deals with contingent payments can protect against adverse market movements.

#### Actionable Insights for Clients and Bankers

@@@ For Clients:
- Focus on thorough due diligence to identify potential integration challenges early.
- Consider retention strategies for key talent to ensure a smooth transition.
  
@@@ For Bankers:
- Stay informed about competitor moves and market trends to provide timely advice.
- Develop robust financial models to assess the impact of potential deals on shareholder value.

DO NOT INCLUDE LINKS HERE
"""

section5Prompt = """
5. TECH TRENDS

(Provide a multi-paragraph, in-depth analysis)
- Identify key emerging technology trends from the news (e.g., Stablecoins, AI, Blockchain, Cloud Computing, Cybersecurity, etc.)
- For each identified trend:
  * Provide a detailed explanation of the trend, its market significance, and growth trajectory
  * List specific companies from the news that are involved in this trend
  * For each company, provide a brief description of their activities and strategic positioning within the trend
  * Analyze the competitive landscape and market dynamics for each trend
  * Discuss potential M&A opportunities and investment implications
- Focus on trends that have significant market impact and deal-making potential
- Include specific examples, use cases, and market data where available
- Provide actionable insights for bankers and investors regarding trend-driven opportunities

**Format:**
Use ### as start of sections
Use #### as start of subsections
Use **title:** as start of subsections
Use - ** as bullet points
Use @@@ to bold a line

IMPORTANT!
USE ONLY ONE FORMATTING PATTING PER LINE AND ONLY USE AT THE START OF A LINE!

For instance: 
- **Apple Inc. (AAPL)**: Mandated to evaluate acquisitions in the AI space, with a focus on startups that can enhance its product offerings. The timeline for this initiative is projected for Q2 2026, as Apple aims to strengthen its competitive edge in AI.
This is fine
But never do this:
- Indiegogo Acquisition by Gamefound : This transaction is progressing, with regulatory approvals anticipated by **Q4 2025**. The integration aims to combine Indiegogo's **38 million users** with Gamefound's technology, thereby enhancing their market position in the crowdfunding space.
Instead of "**Q4 2025**", just do Q4 2025. The same applies to every other form of nested line pats


**Follow the formatting of the Example Structure:**
### 5. TECH TRENDS

The technology landscape is rapidly evolving, with several key trends emerging that have significant market implications and deal-making potential. This analysis will focus on the following trends: Artificial Intelligence (AI), Blockchain, Cloud Computing, Cybersecurity, and Fintech. Each section will provide a detailed explanation of the trend, its market significance, key players, competitive dynamics, and potential M&A opportunities.

#### Artificial Intelligence (AI)

- **Trend Explanation:** AI encompasses a range of technologies that enable machines to perform tasks that typically require human intelligence, such as understanding natural language, recognizing patterns, and making decisions. The global AI market is projected to grow from $93.5 billion in 2021 to $997.8 billion by 2028, at a CAGR of 40.2%.
  
- **Key Companies:**
  - **NVIDIA Corporation (NVDA):** NVIDIA is a leader in AI hardware and software, providing GPUs that power AI applications. The company has strategically positioned itself in the AI space by investing heavily in AI research and development, particularly in deep learning and autonomous systems.
  - **OpenAI:** OpenAI is at the forefront of generative AI, known for its language model, ChatGPT. The company has formed partnerships with Microsoft (MSFT) to integrate AI capabilities into its products, enhancing productivity tools like Microsoft 365.

- **Competitive Landscape:** The AI market is highly competitive, with major players including Google (GOOGL), Amazon (AMZN), and IBM (IBM) also investing heavily in AI technologies. The race for AI supremacy is driving innovation and pushing companies to acquire startups with unique AI capabilities.

- **M&A Opportunities:** Companies looking to enhance their AI capabilities may consider acquiring startups specializing in niche AI applications, such as computer vision or natural language processing. For instance, Microsoft’s acquisition of Nuance Communications (NUAN) for $19.7 billion in 2021 exemplifies this trend.

#### Blockchain

- **Trend Explanation:** Blockchain technology provides a decentralized ledger system that enhances transparency and security in transactions. The blockchain market is expected to grow from $3 billion in 2020 to $69.04 billion by 2027, at a CAGR of 67.3%.

- **Key Companies:**
  - **Coinbase Global, Inc. (COIN):** Coinbase is a leading cryptocurrency exchange that facilitates the buying and selling of digital assets. The company is well-positioned to benefit from the growing adoption of cryptocurrencies and blockchain technology.
  - **Square, Inc. (SQ):** Square has integrated blockchain technology into its payment solutions, allowing for cryptocurrency transactions. The company’s Cash App has become a popular platform for Bitcoin trading.

- **Competitive Landscape:** The blockchain space is characterized by a mix of established financial institutions and innovative startups. Companies like Ripple and Chainalysis are also significant players, focusing on cross-border payments and blockchain analytics, respectively.

- **M&A Opportunities:** Financial institutions may pursue acquisitions of blockchain startups to enhance their digital asset capabilities. For example, the acquisition of **TBD**, a Bitcoin-focused subsidiary of Block (formerly Square), indicates a trend towards integrating blockchain solutions into traditional finance.

#### Cloud Computing

- **Trend Explanation:** Cloud computing enables businesses to access computing resources over the internet, promoting flexibility and scalability. The global

DO NOT INCLUDE LINKS HERE
"""

section6Prompt = """
6. RECOMMENDED READINGS

For each deal mentioned in Section 1, provide ONE specific reading material and explain why it matters.

** Format for each deal:**
@@@ Deal Name: [Specific deal from Section 1]
- **Reading Material:** [Book/Article/Resource name]
- **Why This Matters:** [Clear explanation of how this reading helps understand the deal]

**Example:**
@@@ Deal Name: Revolut's $1B Funding Round
- **Reading Material:** "Venture Deals" by Brad Feld
- **Why This Matters:** This book explains how Series A/B/C valuations work, which is exactly what happened in Revolut's funding round. You'll learn how to calculate the $65B valuation and understand why fintech companies get such high multiples.

Keep it simple and direct - one deal, one reading, one clear explanation of why it matters.


**Format:**
Use ### as start of sections
Use #### as start of subsections
Use **title:** as start of subsections
Use - ** as bullet points
Use @@@ to bold a line

IMPORTANT!
USE ONLY ONE FORMATTING PATTING PER LINE AND ONLY USE AT THE START OF A LINE!

**Follow the formatting of the Example Structure:**
### 6. Recommended Readings

@@@ Deal Name: Microsoft’s Acquisition of Activision Blizzard  
- **Reading Material:** "The Business of Video Games" by Michael Pachter  
- **Why This Matters:** This book provides insights into the gaming industry's financial dynamics and market trends, which are crucial for understanding Microsoft's strategic rationale behind the $68.7 billion acquisition (MSFT). It explains how gaming companies leverage IP and user engagement to drive revenue, helping to contextualize the deal's valuation and potential synergies.

@@@ Deal Name: Amazon's Acquisition of MGM  
- **Reading Material:** "The New Economics of Media" by David Hesmondhalgh  
- **Why This Matters:** This reading delves into the evolving landscape of media and entertainment, particularly in the context of streaming services. It helps to understand Amazon's $8.45 billion acquisition (AMZN) as a strategic move to bolster its Prime Video content library and compete with rivals like Netflix (NFLX) and Disney+ (DIS).

@@@ Deal Name: Salesforce’s Acquisition of Slack  
- **Reading Material:** "The Lean Startup" by Eric Ries  
- **Why This Matters:** This book outlines methodologies for startups to innovate and grow, which is relevant for understanding Salesforce's $27.7 billion acquisition (CRM) of Slack. It highlights the importance of integrating new technologies and platforms to enhance customer engagement and collaboration, aligning with Salesforce's vision of a comprehensive customer relationship management ecosystem.

@@@ Deal Name: NVIDIA’s Acquisition of Arm Holdings  
- **Reading Material:** "The Chip War" by Chris Miller  
- **Why This Matters:** This book provides a detailed analysis of the semiconductor industry, including the strategic importance of Arm's technology in mobile and IoT devices. Understanding the implications of NVIDIA's $40 billion acquisition (NVDA) helps to grasp the competitive landscape and regulatory challenges in the semiconductor space.

@@@ Deal Name: Verizon’s Acquisition of TracFone  
- **Reading Material:** "The Wireless Industry: A Comprehensive Guide" by David H. Hargreaves  
- **Why This Matters:** This resource offers an in-depth look at the wireless telecommunications sector, which is essential for analyzing Verizon's $6.9 billion acquisition (VZ) of TracFone. It explains market segmentation and the significance of prepaid services, providing context for Verizon's strategy to expand its customer base and service offerings.

@@@ Deal Name: Google’s Acquisition of Fitbit  
- **Reading Material:** "Wearable Technology: The Future of Fitness" by David H. Hargreaves  
- **Why This Matters:** This reading discusses the growth of wearable technology and health data analytics, which are central to Google's $2.1 billion acquisition (GOOGL) of Fitbit. It highlights how this deal positions Google to compete in the health tech space against Apple (AAPL) and other tech giants, emphasizing the importance of data in the future of healthcare.
"""

section7Prompt = """
7. MACROECONOMIC UPDATE

Summarize the key data points and insights from the provided macroeconomic content (podcasts, market commentary, etc.) in a clear, structured format.

**Summarization Structure:**
- **Key Data Points:** [List specific numbers, rates, percentages mentioned]
- **Main Insights:** [Bullet points of key takeaways from the content]
- **Market Commentary:** [Direct quotes or paraphrased insights from commentators]
- **TMT Sector Relevance:** [Brief connection to how this affects TMT markets]

**Format:**
Use ### as start of sections
Use #### as start of subsections
Use **title:** as start of subsections
Use - ** as bullet points
Use @@@ to bold a line

IMPORTANT!
USE ONLY ONE FORMATTING PATTING PER LINE AND ONLY USE AT THE START OF A LINE!

**Example Structure:**
### 7. MACROECONOMIC UPDATE

@@@ Key Data Points:
- Fed Funds Rate: 5.25-5.50%
- CPI YoY: 3.2%
- Unemployment Rate: 3.8%
- Oil Price: $82.45/bbl
- USD Index: 105.2

@@@ Main Insights:
- Fed signals pause in rate hikes
- Inflation cooling but core remains elevated
- Labor market showing signs of moderation
- Oil prices supported by OPEC+ cuts

@@@ Market Commentary:
- "The Fed is likely to hold rates steady through year-end" - Morgan Stanley
- "Energy demand remains resilient despite economic headwinds" - Goldman Sachs

@@@ Energy Sector Relevance:
- Higher rates impact energy project financing
- Strong dollar weighs on oil prices
- Labor market strength supports energy demand
"""

















section1PromptEnergy = """
1. RECENT Energy M&A ACTIVITY

=======================================================================================================================================================================================================
qualification_rules (softened):
  Qualify an item for DEAL TIER (Tier 1) if BOTH of these buckets are satisfied:

  A) action_signal (need ≥1):
     - acquisition / acquire / acquiring / bought / buyout
     - merger / merge / agreed to merge / merger-of-equals / reverse merger
     - take-private / privatization
     - carve-out / divestiture / spin-off
     - IPO or direct listing verbs: files prospectus/DRHP/F-1/S-1, prices IPO, lists
     - strategic equity: takes X% stake, majority stake, joint venture, board rights, exclusivity

  B) materiality_signal (need ≥1):
     - a hard number tied to the transaction (deal value, stake %, valuation, offer size/shares, multiple)
     - OR explicit control language (majority, control, board seats/rights, exclusivity)

  Notes:
    - Missing detailed multiples or segment tables does NOT disqualify a deal; use "N/A" where data isn’t in context.
    - Routine wording like “plans/consider/explore” alone is NOT an action_signal unless paired with a filing/pricing/listing or an explicit control/majority/board-rights statement.

do_not_include (minimal but firm):
  - routine fund/ETF/13F trading (increased/trimmed/holds) unless framed as strategic stake that meets materiality_signal
  - earnings, product launches, or partnerships with no equity/control
  - vague “planning to IPO next year” with no filing/pricing/listing/control

tiering_policy:
  - First, select up to TWO items that pass DEAL TIER (Tier 1) with the richest disclosed data.
  - If fewer than TWO exist, fill remaining slots with MARKET-REP TIER (Tier 2):
      * Items that best capture current Consumer & Retail market conditions (pricing power, demand trends, traffic, basket size, promotional intensity, retail sales, confidence, policy impacts), and have concrete metrics (comps %, revenue growth %, margins %, traffic %, ASP).
      * Exclude fund trading and rumor-only pieces.
  - If zero items exist for BOTH tiers, output exactly:
    @@@ Today is a peaceful day, nothing big happened in the Consumer space.

data_missing_policy:
  - If specific multiples/segment tables are not present in the provided context/company block, skip and proceed. Do not exclude otherwise-qualifying deals.

Choose max 2 with highest materiality (deal size, control, market impact) and richest disclosed data.

If only 1 qualifies, include just 1.

If 0 qualify, output the following line EXACTLY: "@@@ Today is a peaceful day, nothing big happened in the Consumer space."
=======================================================================================================================================================================================================

CRITICAL: Focus on ONLY 2 of the most significant M&A deals, IPOs, or major transactions from the provided news items. Prioritize deals with the most detailed financial information and market impact.
ONLY SELECT NEWS WHERE A corporate transaction is specifically reported: M&A/merger, acquisition/take-private, carve-out/divestiture/spin-off, IPO/direct listing, joint venture/strategic partnership with equity, or a significant strategic stake (≥10% ownership or ≥USD 100M consideration, or board/control rights). Exclude routine portfolio trades by funds (e.g., “asset manager purchased shares”) unless they meet the threshold above.
If there is only one recent deal, then just do one deal.
For each of the 2 selected deals, ONLY provide analysis with the following structured information:

**Deal Analysis Structure:**
- **Deal Size:** [USD amount - provide specific numbers when available, estimate based on comparable deals if not specified]
- **Deal Size Category:** [Define deal size: Small cap (<$2B), Mid cap ($2B-$10B), Large cap (>$10B)]
- [Classify today's deal's nature as either Horizontal/Vertical/Tuck-in&Bolt on/Carve out/Conglomerate]
- **Valuation Multiples:** [Detailed analysis of EV/EBITDA, P/E, or other relevant multiples with industry context and comparison to peers]
- **Companies:** [Buyer] acquiring [Target] - include company descriptions and market positions
- **Date Announced:** [Specific date if mentioned, or approximate timeline]
- **Strategic Rationale:** [In-depth analysis of the strategic logic, including market positioning, synergies, competitive advantages, and long-term strategic vision]
- **Risk Analysis:** [Comprehensive risk assessment including integration risks, regulatory challenges, market risks, execution risks, and potential value destruction scenarios]

**Key Financials Analysis:** 
For each deal, provide comprehensive financial analysis including:
- **Revenue Breakdown:** Revenue breakdown based on business segments (e.g., Apple revenue by products: iPhone, Mac, Services, etc. rather than by regions) + percentage share + year-over-year growth for 3 years (Only include if applicable, if no data is available, discard)
- **Profitability Ratios:** EBITDA/revenue, Net Income/revenue ratios (Only include if applicable, if no data is available, discard)
- **Leverage Analysis:** Debt-to-Equity ratio and analysis of long-term vs short-term debt structure
- **Asset Operating Efficiency:** Working capital analysis, inventory turnover days, accounts receivable turnover days, and accounts payable turnover days
- **Valuation Context:** Combine these financial metrics with P/E and EV/EBITDA multiples for comprehensive analysis

**Profitability Metrics:**  (Only include if applicable, if no data is available, discard)
-EBITDA, EBIT, Net Income and year-over-year growth for 3 years (WRITE THIS IN THE FORM OF A TABLE, see formatting guidelines below)

**Purpose:** Use this financial analysis to roughly assess performance and business growth/decline trends, then infer the strategic rationale (e.g., whether the acquisition target provides new businesses/technologies/brand influence that the parent company lacks)

**Analysis Requirements:**
- Provide specific valuation multiples with industry benchmarks and peer comparisons
- Include detailed rationale with strategic context and market implications
- Conduct thorough risk analysis with specific risk factors and mitigation strategies
- Use concrete data points and financial metrics wherever possible
- Focus on deals with the most significant TMT sector impact and detailed financial information
- Specify capital structure

------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Formatting guidelines:
Use ### as start of sections
Use #### as start of subsections
Use **title:** as start of subsections
Use - ** as bullet points
Use @@@ to bold a line

To draw tables, use the following format:
| A | B |
| --- | --- |
| a1 | b1 |
| a2 | b2 |


IMPORTANT!
USE ONLY ONE FORMATTING PATTING PER LINE AND ONLY USE AT THE START OF A LINE!


For instance: 
- **Apple Inc. (AAPL)**: Mandated to evaluate acquisitions in the AI space, with a focus on startups that can enhance its product offerings. The timeline for this initiative is projected for Q2 2026, as Apple aims to strengthen its competitive edge in AI.
This is fine
But never do this:
- **Indiegogo Acquisition by Gamefound**: This transaction is progressing, with regulatory approvals anticipated by **Q4 2025**. The integration aims to combine Indiegogo's **38 million users** with Gamefound's technology, thereby enhancing their market position in the crowdfunding space.
Instead of "**Q4 2025**", just do Q4 2025. The same applies to every other line pats


When adding links, use this EXACT format: **Link title** ([Link](https://linkURL))
example: **JPMorgan Reports Increased M&A Activity in TMT Sector** ([Link](https://www.businessinsider.com/merger-acquisition-trends-1h-hreport-sponsors-volumes-anu-aiyengar-jpmorgan-2025-7))
MAKE SURE THE LINKS MATCH THEIR TITLES
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

**Example Structure:**
### 1. RECENT Energy M&A ACTIVITY

**Deal 1: [Company Name] Acquisition**
**Deal Title with Link** ([Link](URL))
- **Deal Size:** $X billion (or specific amount)
- **Valuation Multiples:** EV/EBITDA of X.Xx (vs industry average of X.Xx), P/E of X.Xx
- **Companies:** [Detailed company descriptions and market positions]
- **Date Announced:** [Specific date]
- **Strategic Rationale:** [Comprehensive strategic analysis with market context]
- **Risk Analysis:** [Detailed risk assessment with specific factors]
- **Key Financials Analysis:** [Revenue breakdown by business, profitability metrics, leverage analysis, asset efficiency, and valuation context]

**Deal 2: [Company Name] Acquisition** |(Include only if available)
[Same detailed structure as Deal 1]

**Do something like this if there isn't a single deal in the energy sector**
### 1. RECENT Energy M&A ACTIVITY

Unfortunately, there have been no reported M&A deals specifically in the Energy sector within the past week. This could be attributed to several factors:

- **Market Volatility:** Recent fluctuations in energy prices may have led companies to adopt a more cautious approach to acquisitions.
- **Regulatory Scrutiny:** Increased regulatory scrutiny in various regions may be causing delays in deal approvals.
- **Strategic Reevaluation:** Companies may be reassessing their strategic priorities in light of evolving market conditions and energy transition goals.

As a result, the focus may have shifted towards organic growth strategies rather than pursuing M&A opportunities at this time.



Focus on quality over quantity - provide deep, data-driven analysis of only 2 deals rather than superficial coverage of many deals.

DO NOT INCLUDE a Recommended Readings
"""

section2PromptEnergy = """
2. MARKET DYNAMICS & SENTIMENT

(Provide a multi-paragraph, in-depth analysis)
- Overall Energy sector sentiment, with breakdowns by subsector, geography, and deal type
- Key market drivers and headwinds, with supporting data
- Subsector performance analysis (e.g., Oil & Gas, Renewable Energy, Utilities, Energy Infrastructure, Solar, Wind)
- Trading multiples trends, with specific numbers and comparisons
- Notable investor/analyst reactions, with quotes or examples
- Actionable insights for bankers and investors

**Format:**
Use ### as start of sections
Use #### as start of subsections
Use **title:** as start of subsections
Use - ** as bullet points
Use @@@ to bold a line

IMPORTANT!
USE ONLY ONE FORMATTING PATTING PER LINE AND ONLY USE AT THE START OF A LINE!

For instance: 
- **ExxonMobil Corp. (XOM)**: Mandated to evaluate acquisitions in the renewable energy space, with a focus on startups that can enhance its clean energy portfolio. The timeline for this initiative is projected for Q2 2026, as ExxonMobil aims to strengthen its competitive edge in energy transition.
This is fine
But NEVER EVER do it like this "**Q4 2025**" in the middle of a line
Example:
- Chevron Acquisition by Occidental : This transaction is progressing, with regulatory approvals anticipated by **Q4 2025**. The integration aims to combine Chevron's **oil production assets** with Occidental's technology, thereby enhancing their market position in the energy space.
Instead of "**Q4 2025**", just do Q4 2025. The same applies to every other line pats. DO NOT PUT LINE PAT IN THE MIDDLE OF LINES

DO NOT INCLUDE a Recommended Readings
DO NOT PUT LINKS IN THIS SECTION

**Example Structure**
### 2. MARKET DYNAMICS & SENTIMENT

The Energy sector is currently experiencing a mixed sentiment, characterized by cautious optimism amid ongoing regulatory scrutiny and evolving technological advancements. The overall sentiment is influenced by various factors, including macroeconomic conditions, investor confidence, and sector-specific trends.

@@@ Subsector Breakdown:
  - **Oil & Gas:** The oil and gas subsector remains robust, driven by advancements in drilling technology, enhanced recovery methods, and digital transformation. For instance, ExxonMobil's utilization of AI for reservoir optimization reflects a growing trend where companies leverage technology to enhance operational efficiency and production yields.
  - **Renewable Energy:** The renewable energy subsector is witnessing rapid growth as companies like NextEra Energy enhance grid integration through new digital features. However, traditional utilities face challenges from distributed energy resources.
  - **Utilities:** The utilities sector is innovating with smart grid technologies, as demonstrated by Duke Energy's introduction of advanced metering infrastructure, which aims to improve customer experience and grid reliability.
  - **Energy Infrastructure:** The energy infrastructure space continues to thrive, with companies exploring new business models and partnerships, such as Kinder Morgan's acquisition of renewable natural gas assets, which aims to integrate clean energy solutions.
  - **Solar & Wind:** The solar and wind subsectors are particularly hot, with companies racing to implement renewable solutions across various markets, including residential, where SunPower is challenging Tesla's solar model by promising to cover installation failures.

#### Key Market Drivers and Headwinds

 @@@ Drivers:
  - **Energy Transition:** Continuous innovation in renewable energy, energy storage, and smart grid technologies is driving growth across energy sectors. For example, NextEra Energy's battery storage technology is expected to enhance the performance of renewable energy applications reliant on intermittent generation.
  - **Increased Investment:** Venture capital and private equity investments remain strong, particularly in renewable energy and energy storage, as investors seek to capitalize on emerging trends.

 @@@ Headwinds:
  - **Regulatory Scrutiny:** Increased regulatory scrutiny, especially in the oil and gas sector, poses risks to M&A activities and market valuations. Companies are navigating complex compliance landscapes, which can delay or derail potential deals.
  - **Economic Uncertainty:** Global economic conditions, including inflation and geopolitical tensions, may impact energy demand and investment in energy infrastructure.

#### Subsector Performance Analysis

- **Oil & Gas:** The oil and gas sector continues to perform well, driven by demand for traditional energy sources and technological improvements in extraction methods. Companies focusing on shale production are particularly well-positioned for growth.
- **Renewable Energy:** Renewable energy companies are adapting to changing consumer preferences, with a shift towards clean energy consumption. However, traditional utilities face declining revenues from fossil fuel generation.
- **Utilities:** Utility operators are investing heavily in infrastructure to support renewable energy deployment, which is expected to drive new revenue streams from distributed energy resources and enhanced grid services.
- **Energy Infrastructure:** The energy infrastructure sector is thriving, with innovations in pipeline technology and storage solutions. The acquisition of renewable natural gas assets by Kinder Morgan highlights the consolidation trend in this space.
- **Solar & Wind:** The solar and wind subsectors are booming, with applications across various markets, including residential, commercial, and utility-scale. Companies are investing heavily in renewable capabilities to maintain competitive advantages.

#### Trading Multiples Trends

@@@ Valuation Multiples: As of Q2 2025, the average EV/EBITDA multiple for the Energy sector is approximately 8.5x, with notable variations across subsectors:
  - **Oil & Gas:** 6.3x
  - **Renewable Energy:** 15.1x
  - **Utilities:** 12.8x
  - **Energy Infrastructure:** 9.7x
  - **Solar & Wind:** 18.5x

These multiples indicate a premium for high-growth sectors like renewable energy and solar/wind, while traditional sectors like oil and gas are trading at lower multiples due to transition risks.

#### Notable Investor/Analyst Reactions

- Analysts are generally optimistic about the long-term prospects of the Energy sector, citing energy transition as a key driver of growth. For instance, an analyst at a leading investment bank commented, "The integration of renewable energy across markets is not just a trend; it's a fundamental shift that will redefine energy production and consumption patterns."

#### Actionable Insights for Bankers and Investors

- **Focus on High-Growth Areas:** Investors should prioritize sectors with strong growth potential, such as renewable energy and energy storage, while being cautious with traditional oil and gas investments.
- **Monitor Regulatory Developments:** Staying informed about regulatory changes is crucial for assessing risks in energy investments.
- **Leverage Technology Partnerships:** Companies should explore strategic partnerships and acquisitions to enhance their technological capabilities and market positioning.
- **Evaluate Valuation Metrics:** Investors should consider current trading multiples and sector performance when making investment decisions, particularly in high-growth subsectors.

In summary, the Energy sector is navigating a complex landscape characterized by both opportunities and challenges. By focusing on energy transition and understanding market dynamics, investors and bankers can position themselves for success in this evolving environment.
"""


section3PromptEnergy ="""
3. BANKING PIPELINE

(Provide a multi-paragraph, in-depth analysis)
- Deal Pipeline (Transaction Pipeline):
  * Live deals: Transactions currently in progress (M&A in due diligence, upcoming IPOs), with details and expected timing
  * Mandated deals: Transactions with secured mandates but not yet fully launched, with client names and deal types if possible
  * Pitching-stage deals: Active pitches and client discussions for potential mandates, with sector/client focus
- Pipeline tracking metrics:
  * Expected revenue/fees from active pipeline, with breakdowns
  * Timing projections (Q2 close, Q4 IPO, etc.)
  * Workload allocation and capacity analysis (e.g., analyst/associate bandwidth)
  * Forecasting and strategic planning implications
- Notable pipeline developments and competitive landscape, with examples
- Actionable insights for team management and business development

**Format:**
Use ### as start of sections
Use #### as start of subsections
Use **title:** as start of subsections
Use - ** as bullet points
Use @@@ to bold a line

IMPORTANT!
USE ONLY ONE FORMATTING PATTING PER LINE AND ONLY USE AT THE START OF A LINE!


For instance: 
- **ExxonMobil Corp. (XOM)**: Mandated to evaluate acquisitions in the renewable energy space, with a focus on startups that can enhance its clean energy portfolio. The timeline for this initiative is projected for Q2 2026, as ExxonMobil aims to strengthen its competitive edge in energy transition.
This is fine
But never do this:
- Chevron Acquisition by Occidental : This transaction is progressing, with regulatory approvals anticipated by **Q4 2025**. The integration aims to combine Chevron's **oil production assets** with Occidental's technology, thereby enhancing their market position in the energy space.
Instead of "**Q4 2025**", just do Q4 2025. The same applies to every other line pats

DO NOT INCLUDE a Recommended Readings

**Follow the formatting of the Example Structure:**
### 3. BANKING PIPELINE

The current banking pipeline in the Energy sector reflects a dynamic landscape with a mix of live deals, mandated transactions, and active pitches. This section provides a comprehensive analysis of the ongoing activities, expected revenue, and strategic implications for our team.

#### Deal Pipeline

@@@ Live Deals:
- **ExxonMobil Corp. (XOM)**: Currently in discussions for a strategic partnership leveraging AI for reservoir optimization. The deal is in the due diligence phase, with an expected close in Q3 2025. This partnership could enhance ExxonMobil's production capabilities, potentially increasing oil recovery by up to 15%.
  
- **NextEra Energy Acquisition by Duke Energy**: This transaction is moving forward, with regulatory approvals anticipated by Q4 2025. The integration aims to combine NextEra's renewable energy portfolio with Duke Energy's utility operations, enhancing their market position in clean energy.

@@@ Mandated Deals:
- **Chevron Corp. (CVX)**: Secured a mandate to explore strategic partnerships related to renewable energy development, particularly in response to climate regulations. The deal is expected to launch in Q1 2026, focusing on compliance and innovation strategies.
  
- **Occidental Petroleum (OXY)**: Mandated to evaluate acquisitions in the carbon capture space, with a focus on startups that can enhance its carbon management portfolio. The timeline for this initiative is projected for Q2 2026, as Occidental aims to strengthen its competitive edge in energy transition.

@@@ Pitching-Stage Deals:
- **Renewable Energy Sector**: Active discussions with several renewable energy companies regarding potential M&A opportunities to consolidate market share in the solar and wind space. Clients include First Solar (FSLR) and SunPower (SPWR), with pitches expected to finalize by Q3 2025.
  
- **Energy Storage Startups**: Engaging with various energy storage companies for potential investment banking services, focusing on those that are innovating in battery technology and grid storage solutions. Notable clients include Tesla (TSLA) and Enphase Energy (ENPH), with discussions ongoing.

#### Pipeline Tracking Metrics

@@@ Expected Revenue/Fees: The active pipeline is projected to generate approximately $25 million in fees, broken down as follows:
  - **Live Deals**: $10 million
  - **Mandated Deals**: $8 million
  - **Pitching-Stage Deals**: $7 million

@@@ Timing Projections:
  - **Q2 2025**: Expected close for ExxonMobil partnership.
  - **Q4 2025**: Anticipated completion of the NextEra Energy acquisition.
  - **Q1 2026**: Launch of Chevron's strategic partnership initiatives.

- **Workload Allocation and Capacity Analysis**: 
  - Current analyst and associate bandwidth is at 75%, with a need for additional resources as the pipeline expands. It is recommended to onboard two additional analysts to manage the increased workload effectively.

- **Forecasting and Strategic Planning Implications**: The pipeline indicates a strong demand for advisory services in renewable energy and energy storage sectors. Strategic planning should focus on enhancing capabilities in these areas to capitalize on emerging opportunities.

#### Notable Pipeline Developments and Competitive Landscape

- The competitive landscape is intensifying, particularly in the renewable energy sector, where companies like NextEra Energy and Duke Energy are vying for leadership. The recent announcement of Biden's Energy Action Plan could alter the regulatory environment, impacting deal structures and valuations.
  
- Additionally, the rise of energy storage startups, such as the one founded by a former Tesla executive, indicates a growing market for energy storage solutions, which could lead to new advisory opportunities.

#### Actionable Insights for Team Management and Business Development

- **Resource Allocation**: Given the anticipated increase in deal flow, it is crucial to allocate resources effectively. Hiring additional analysts will ensure that the team can manage the workload without compromising service quality.
  
- **Sector Focus**: Prioritize business development efforts in high-growth sectors such as renewable energy and energy storage, where demand for advisory services is expected to surge. This focus will position the firm as a leader in these emerging markets.

- **Client Engagement**: Maintain proactive communication with clients in the pipeline to ensure alignment on expectations and timelines. Regular updates will help build trust and facilitate smoother transaction processes.

In summary, the banking pipeline is robust, with significant opportunities across various Energy subsectors. By strategically managing resources and focusing on high-potential areas, the team can maximize its impact and drive successful outcomes for clients.
"""


section4PromptEnergy = """
4. STAKEHOLDER IMPACT & FORWARD-LOOKING ANALYSIS

(Provide a multi-paragraph, in-depth analysis)
- Deal-specific impacts on:
  * Shareholders (value creation/dilution, with scenario analysis and numbers)
  * Employees (synergies, restructuring, retention, with examples)
  * Competitors (market positioning, with specific competitor moves)
  * Customers (product/service implications, with case studies)
- Market reaction and analyst commentary, with quotes or data
- Expected market reaction, with scenario analysis
- Potential counter-bids or competing offers, with likelihood assessment
- Similar deals likely to follow, with sector consolidation predictions
- Key risks and mitigants, with detailed breakdowns
- Actionable insights for clients and bankers

**Format:**
Use ### as start of sections
Use #### as start of subsections
Use **title:** as start of subsections
Use - ** as bullet points
Use @@@ to bold a line

IMPORTANT!
USE ONLY ONE FORMATTING PATTING PER LINE AND ONLY USE AT THE START OF A LINE!


For instance: 
- Value Creation: In a scenario where Company A (e.g. ExxonMobil Corp. (XOM)) acquires Company B (e.g. Pioneer Natural Resources (PXD)), the combined entity could see a revenue increase of approximately 20% due to enhanced production capabilities.
But never ever do this:
- Chevron Acquisition by Occidental : This transaction is progressing, with regulatory approvals anticipated by **Q4 2025**. The integration aims to combine Chevron's **oil production assets** with Occidental's technology, thereby enhancing their market position in the energy space.
Instead of "**Q4 2025**", just do Q4 2025. The same applies to every other form of nested line pats

DO NOT INCLUDE a Recommended Readings

**Follow the formatting of the Example Structure:**
### 4. STAKEHOLDER IMPACT & FORWARD-LOOKING ANALYSIS

The implications of M&A transactions in the Energy sector extend beyond immediate financial metrics, affecting various stakeholders including shareholders, employees, competitors, and customers. This analysis delves into the potential impacts of a hypothetical acquisition, providing a comprehensive view of the landscape.

#### Deal-Specific Impacts on Stakeholders

- **Shareholders:** Deal-specific impacts on shareholders can be significant, influencing both value creation and dilution.
  - **Value Creation:** In a scenario where Company A (e.g., ExxonMobil Corp. (XOM)) acquires Company B (e.g., Pioneer Natural Resources (PXD)), the combined entity could see a revenue increase of approximately 20% due to enhanced production capabilities. Assuming a pre-deal market cap of $400 billion for ExxonMobil, a successful integration could increase shareholder value by $80 billion.
  - **Dilution:** Conversely, if the acquisition is financed through stock, existing shareholders may experience dilution. For instance, if ExxonMobil issues 10% of its shares to finance the deal, existing shareholders could see their ownership stake decrease, potentially leading to a 5% drop in share price post-announcement.

- **Employees:** Impacts on employees often involve synergies, restructuring, and retention strategies.
  - **Synergies:** A merger between ExxonMobil (XOM) and Pioneer Natural Resources (PXD) led to substantial cost synergies, with estimates of $2 billion in annual savings. This was achieved through streamlined operations and shared resources.
  - **Restructuring:** However, such deals often lead to layoffs. In the ExxonMobil-Pioneer merger, approximately 3,000 jobs were cut, highlighting the need for careful planning to retain key talent.
  - **Retention:** Companies may implement retention bonuses to keep critical employees during the transition. For example, in the acquisition of Pioneer by ExxonMobil, retention packages were offered to key Pioneer executives to ensure continuity.

- **Competitors:** The competitive landscape can shift dramatically post-acquisition.
  - **Market Positioning:** Following the merger of ExxonMobil and Pioneer, competitors such as Chevron Corp. (CVX) and Occidental Petroleum (OXY) had to adapt their strategies to maintain market share. This included aggressive drilling strategies and enhanced production techniques.
  - **Specific Competitor Moves:** Chevron responded with a $10 billion investment in shale production to counter the combined entity's market strength.

- **Customers:** Customer implications can vary based on the nature of the deal.
  - **Product/Service Implications:** The merger of ExxonMobil and Pioneer allowed ExxonMobil to bundle oil production with natural gas services, enhancing customer value. This strategy led to a 15% increase in bundled service contracts.
  - **Case Studies:** The acquisition of Pioneer by ExxonMobil resulted in enhanced production capabilities, directly benefiting customers with improved service offerings.

#### Market Reaction and Analyst Commentary

- **Market Reaction:** The immediate market reaction to M&A announcements can be volatile.
For example, when ExxonMobil announced its acquisition of Pioneer, shares of ExxonMobil initially dipped by 5% before recovering as analysts recognized the long-term strategic benefits.
- **Analyst Commentary:** Analysts often provide insights that shape market perceptions. A notable quote from a Morgan Stanley analyst post-acquisition was, "This deal positions ExxonMobil to dominate the Permian Basin, despite initial market skepticism."

#### Expected Market Reaction and Scenario Analysis

- **Scenario Analysis:** The market's reaction can be assessed through various scenarios:
- **Positive Scenario:** If the acquisition leads to successful integration and production growth, shares could rise by 15% within six months.
- **Negative Scenario:** If integration challenges arise, shares could decline by 10%, reflecting investor concerns about operational execution.

#### Potential Counter-Bids or Competing Offers

- **Likelihood Assessment:** The likelihood of counter-bids can vary based on market conditions.
In the case of the proposed acquisition of Pioneer by ExxonMobil, there were rumors of interest from Chevron Corp. (CVX), highlighting the competitive nature of the Energy sector. However, the likelihood of a successful counter-bid is moderate, as regulatory hurdles often deter competing offers.

#### Similar Deals Likely to Follow

- **Sector Consolidation Predictions:** The Energy sector is expected to see continued consolidation.
Analysts predict that as companies seek to enhance their production capabilities, similar deals will emerge, particularly in the shale and renewable energy spaces. Companies like Chevron (CVX) and Occidental (OXY) may pursue acquisitions to bolster their production portfolios.

#### Key Risks and Mitigants

  - **Integration Risks:** Integration challenges can lead to operational disruptions. Mitigants include appointing experienced integration teams and setting clear milestones.
  - **Regulatory Risks:** Regulatory scrutiny can delay or block deals. Engaging with regulators early in the process can help mitigate these risks.
  - **Market Risks:** Market volatility can impact deal valuations. Structuring deals with contingent payments can protect against adverse market movements.

#### Actionable Insights for Clients and Bankers

@@@ For Clients:
- Focus on thorough due diligence to identify potential integration challenges early.
- Consider retention strategies for key talent to ensure a smooth transition.
  
@@@ For Bankers:
- Stay informed about competitor moves and market trends to provide timely advice.
- Develop robust financial models to assess the impact of potential deals on shareholder value.
"""

section5PromptEnergy = """
5. ENERGY TRENDS

(Provide a multi-paragraph, in-depth analysis)
- Identify key emerging energy trends from the news (e.g., Renewable Energy, Energy Storage, Smart Grid, Carbon Capture, Hydrogen, etc.)
- For each identified trend:
  * Provide a detailed explanation of the trend, its market significance, and growth trajectory
  * List specific companies from the news that are involved in this trend
  * For each company, provide a brief description of their activities and strategic positioning within the trend
  * Analyze the competitive landscape and market dynamics for each trend
  * Discuss potential M&A opportunities and investment implications
- Focus on trends that have significant market impact and deal-making potential
- Include examples, use cases, and market data where available
- Provide actionable insights for bankers and investors regarding trend-driven opportunities
- Refrain from writing overly lengthy reports, and MAKE SURE section can be completed within the token limit

**Format:**
Use ### as start of sections
Use #### as start of subsections
Use **title:** as start of subsections
Use - ** as bullet points
Use @@@ to bold a line

IMPORTANT!
USE ONLY ONE FORMATTING PATTING PER LINE AND ONLY USE AT THE START OF A LINE!


For instance: 
- **ExxonMobil Corp. (XOM)**: Mandated to evaluate acquisitions in the renewable energy space, with a focus on startups that can enhance its clean energy portfolio. The timeline for this initiative is projected for Q2 2026, as ExxonMobil aims to strengthen its competitive edge in energy transition.
This is fine
But never do this:
- Chevron Acquisition by Occidental : This transaction is progressing, with regulatory approvals anticipated by **Q4 2025**. The integration aims to combine Chevron's **oil production assets** with Occidental's technology, thereby enhancing their market position in the energy space.
Instead of "**Q4 2025**", just do Q4 2025. The same applies to every other form of nested line pats

DO NOT INCLUDE a Recommended Readings

**Follow the formatting of the Example Structure:**
### 5. ENERGY TRENDS

The energy landscape is rapidly evolving, with several key trends emerging that have significant market implications and deal-making potential. This analysis will focus on the following trends: Renewable Energy, Energy Storage, Smart Grid, Carbon Capture, and Hydrogen. Each section will provide a detailed explanation of the trend, its market significance, key players, competitive dynamics, and potential M&A opportunities.

#### Renewable Energy

- **Trend Explanation:** Renewable energy encompasses a range of technologies that generate electricity from natural resources such as sunlight, wind, and water. The global renewable energy market is projected to grow from $881.7 billion in 2020 to $1.9 trillion by 2030, at a CAGR of 8.4%.
  
@@@ Key Companies:
  - **NextEra Energy, Inc. (NEE):** NextEra Energy is a leader in renewable energy generation, providing wind and solar power across the United States. The company has strategically positioned itself in the renewable space by investing heavily in wind and solar projects, particularly in Florida and Texas.
  - **First Solar, Inc. (FSLR):** First Solar is at the forefront of solar panel manufacturing, known for its thin-film technology. The company has formed partnerships with utilities to integrate solar capabilities into their portfolios, enhancing grid reliability and reducing carbon emissions.

- **Competitive Landscape:** The renewable energy market is highly competitive, with major players including Duke Energy (DUK), Dominion Energy (D), and Southern Company (SO) also investing heavily in renewable technologies. The race for renewable energy supremacy is driving innovation and pushing companies to acquire startups with unique renewable capabilities.

- **M&A Opportunities:** Companies looking to enhance their renewable capabilities may consider acquiring startups specializing in niche renewable applications, such as offshore wind or advanced solar technologies. For instance, NextEra Energy's acquisition of Gulf Power for $5.1 billion in 2019 exemplifies this trend.

#### Energy Storage

- **Trend Explanation:** Energy storage technology provides solutions for storing electricity generated from renewable sources, enhancing grid stability and enabling greater renewable energy integration. The energy storage market is expected to grow from $4.4 billion in 2020 to $15.5 billion by 2027, at a CAGR of 20.8%.

@@@ Key Companies:
  - **Tesla, Inc. (TSLA):** Tesla is a leading manufacturer of energy storage solutions, including the Powerwall and Powerpack systems. The company is well-positioned to benefit from the growing adoption of renewable energy and the need for grid storage solutions.
  - **Enphase Energy, Inc. (ENPH):** Enphase has integrated energy storage technology into its solar solutions, allowing for residential and commercial energy storage. The company's microinverter technology has become a popular platform for solar energy storage.

- **Competitive Landscape:** The energy storage space is characterized by a mix of established automotive companies and innovative startups. Companies like LG Chem and Samsung SDI are also significant players, focusing on battery technology and energy storage solutions, respectively.

- **M&A Opportunities:** Energy companies may pursue acquisitions of energy storage startups to enhance their grid capabilities. For example, the acquisition of **Maxwell Technologies** by Tesla indicates a trend towards integrating energy storage solutions into traditional energy infrastructure.

#### Smart Grid

- **Trend Explanation:** Smart grid technology enables utilities to monitor and control electricity flow in real-time, promoting efficiency and reliability. The global smart grid market is projected to grow from $23.8 billion in 2020 to $61.3 billion by 2027, at a CAGR of 14.5%.

@@@ Key Companies:
  - **Schneider Electric SE (SBGSF):** Schneider Electric is a leader in smart grid solutions, providing advanced metering infrastructure and grid management systems. The company has strategically positioned itself in the smart grid space by investing heavily in digital grid technologies.
  - **Siemens AG (SIEGY):** Siemens is at the forefront of smart grid innovation, known for its grid automation and control systems. The company has formed partnerships with utilities to integrate smart grid capabilities into their operations.

- **Competitive Landscape:** The smart grid market is highly competitive, with major players including General Electric (GE), ABB Ltd., and Honeywell International (HON) also investing heavily in smart grid technologies. The race for smart grid supremacy is driving innovation and pushing companies to acquire startups with unique grid capabilities.

- **M&A Opportunities:** Companies looking to enhance their smart grid capabilities may consider acquiring startups specializing in niche grid applications, such as demand response or advanced metering infrastructure. For instance, Schneider Electric's acquisition of **Aveva Group** for $5.7 billion in 2022 exemplifies this trend.

#### Carbon Capture

- **Trend Explanation:** Carbon capture technology involves capturing carbon dioxide emissions from industrial processes and storing them underground or utilizing them for other purposes. The carbon capture market is expected to grow from $1.9 billion in 2020 to $7.0 billion by 2027, at a CAGR of 20.5%.

@@@ Key Companies:
  - **Occidental Petroleum Corporation (OXY):** Occidental is a leader in carbon capture and storage, developing technologies to capture CO2 from industrial processes. The company is well-positioned to benefit from the growing focus on carbon reduction and climate change mitigation.
  - **Chevron Corporation (CVX):** Chevron has integrated carbon capture technology into its oil and gas operations, allowing for enhanced oil recovery while reducing carbon emissions. The company's carbon capture initiatives have become a key component of its sustainability strategy.

- **Competitive Landscape:** The carbon capture space is characterized by a mix of established oil and gas companies and innovative startups. Companies like ExxonMobil (XOM) and Shell (RDS.A) are also significant players, focusing on carbon capture and storage solutions.

- **M&A Opportunities:** Energy companies may pursue acquisitions of carbon capture startups to enhance their sustainability capabilities. For example, the acquisition of **Carbon Engineering** by Occidental indicates a trend towards integrating carbon capture solutions into traditional energy operations.

#### Hydrogen

- **Trend Explanation:** Hydrogen technology involves producing hydrogen from renewable sources for use as a clean fuel in transportation and industrial applications. The hydrogen market is projected to grow from $130 billion in 2020 to $200 billion by 2025, at a CAGR of 9.2%.

@@@ Key Companies:
  - **Plug Power Inc. (PLUG):** Plug Power is a leader in hydrogen fuel cell technology, providing fuel cell solutions for material handling and transportation applications. The company has strategically positioned itself in the hydrogen space by investing heavily in fuel cell development.
  - **Bloom Energy Corporation (BE):** Bloom Energy is at the forefront of hydrogen production, known for its solid oxide fuel cell technology. The company has formed partnerships with utilities to integrate hydrogen capabilities into their energy portfolios.

- **Competitive Landscape:** The hydrogen market is highly competitive, with major players including Air Products and Chemicals (APD), Linde plc (LIN), and Air Liquide also investing heavily in hydrogen technologies. The race for hydrogen supremacy is driving innovation and pushing companies to acquire startups with unique hydrogen capabilities.

- **M&A Opportunities:** Companies looking to enhance their hydrogen capabilities may consider acquiring startups specializing in niche hydrogen applications, such as green hydrogen production or fuel cell technology. For instance, Plug Power's acquisition of **United Hydrogen** for $75 million in 2020 exemplifies this trend.

In summary, the energy sector is experiencing rapid transformation driven by technological advancements and regulatory changes. By focusing on emerging trends and understanding market dynamics, investors and bankers can position themselves for success in this evolving environment.
"""

section6PromptEnergy = """
6. RECOMMENDED READINGS

For each deal mentioned in Section 1, provide ONE specific reading material and explain why it matters.

** Format for each deal:**
@@@ Deal Name: [Specific deal from Section 1]
- **Reading Material:** [Book/Article/Resource name]
- **Why This Matters:** [Clear explanation of how this reading helps understand the deal]

**Example:**
@@@ Deal Name: ExxonMobil's Acquisition of Pioneer Natural Resources
- **Reading Material:** "The Prize" by Daniel Yergin
- **Why This Matters:** This book explains the history and economics of the oil industry, which is exactly what happened in ExxonMobil's acquisition. You'll learn how oil companies value reserves and understand why energy companies get such high multiples.

Keep it simple and direct - one deal, one reading, one clear explanation of why it matters.
ONLY USE DEALS RELAVENT TO THE ENERGY SECTOR

**Format:**
Use ### as start of sections
Use #### as start of subsections
Use **title:** as start of subsections
Use - ** as bullet points
Use @@@ to bold a line

IMPORTANT!
USE ONLY ONE FORMATTING PATTING PER LINE AND ONLY USE AT THE START OF A LINE!


**Follow the formatting of the Example Structure:**
### 6. Recommended Readings

@@@ Deal Name: ExxonMobil's Acquisition of Pioneer Natural Resources  
- **Reading Material:** "The Prize" by Daniel Yergin  
- **Why This Matters:** This book provides insights into the oil industry's financial dynamics and market trends, which are crucial for understanding ExxonMobil's strategic rationale behind the $60 billion acquisition (XOM). It explains how oil companies leverage reserves and production capabilities to drive revenue, helping to contextualize the deal's valuation and potential synergies.

@@@ Deal Name: NextEra Energy's Acquisition of Gulf Power  
- **Reading Material:** "The New Economics of Energy" by David H. Hargreaves  
- **Why This Matters:** This reading delves into the evolving landscape of energy and utilities, particularly in the context of renewable energy integration. It helps to understand NextEra's $5.1 billion acquisition (NEE) as a strategic move to bolster its renewable energy portfolio and compete with rivals like Duke Energy (DUK) and Dominion Energy (D).

@@@ Deal Name: Chevron's Acquisition of Noble Energy  
- **Reading Material:** "The Lean Startup" by Eric Ries  
- **Why This Matters:** This book outlines methodologies for energy companies to innovate and grow, which is relevant for understanding Chevron's $5 billion acquisition (CVX) of Noble Energy. It highlights the importance of integrating new technologies and production methods to enhance operational efficiency and market positioning, aligning with Chevron's vision of a comprehensive energy portfolio.
"""

section7PromptEnergy = """
7. MACROECONOMIC UPDATE

Summarize the key data points and insights from the provided macroeconomic content (podcasts, market commentary, etc.) in a clear, structured format.

**Summarization Structure:**
- **Key Data Points:** [List specific numbers, rates, percentages mentioned]
- **Main Insights:** [Bullet points of key takeaways from the content]
- **Market Commentary:** [Direct quotes or paraphrased insights from commentators]
- **Energy Sector Relevance:** [Brief connection to how this affects energy markets]

**Format:**
Use ### as start of sections
Use #### as start of subsections
Use **title:** as start of subsections
Use - ** as bullet points
Use @@@ to bold a line

IMPORTANT!
USE ONLY ONE FORMATTING PATTING PER LINE AND ONLY USE AT THE START OF A LINE!


**Example Structure:**
### 7. MACROECONOMIC UPDATE

@@@ Key Data Points:
- Fed Funds Rate: 5.25-5.50%
- CPI YoY: 3.2%
- Unemployment Rate: 3.8%
- Oil Price: $82.45/bbl
- USD Index: 105.2

@@@ Main Insights:
- Fed signals pause in rate hikes
- Inflation cooling but core remains elevated
- Labor market showing signs of moderation
- Oil prices supported by OPEC+ cuts

@@@ Market Commentary:
- "The Fed is likely to hold rates steady through year-end" - Morgan Stanley
- "Energy demand remains resilient despite economic headwinds" - Goldman Sachs

@@@ Energy Sector Relevance:
- Higher rates impact energy project financing
- Strong dollar weighs on oil prices
- Labor market strength supports energy demand
"""









section1PromptHealthcare = """
1. RECENT Healthcare M&A ACTIVITY

=======================================================================================================================================================================================================
qualification_rules (softened):
  Qualify an item for DEAL TIER (Tier 1) if BOTH of these buckets are satisfied:

  A) action_signal (need ≥1):
     - acquisition / acquire / acquiring / bought / buyout
     - merger / merge / agreed to merge / merger-of-equals / reverse merger
     - take-private / privatization
     - carve-out / divestiture / spin-off
     - IPO or direct listing verbs: files prospectus/DRHP/F-1/S-1, prices IPO, lists
     - strategic equity: takes X% stake, majority stake, joint venture, board rights, exclusivity

  B) materiality_signal (need ≥1):
     - a hard number tied to the transaction (deal value, stake %, valuation, offer size/shares, multiple)
     - OR explicit control language (majority, control, board seats/rights, exclusivity)

  Notes:
    - Missing detailed multiples or segment tables does NOT disqualify a deal; use "N/A" where data isn’t in context.
    - Routine wording like “plans/consider/explore” alone is NOT an action_signal unless paired with a filing/pricing/listing or an explicit control/majority/board-rights statement.

do_not_include (minimal but firm):
  - routine fund/ETF/13F trading (increased/trimmed/holds) unless framed as strategic stake that meets materiality_signal
  - earnings, product launches, or partnerships with no equity/control
  - vague “planning to IPO next year” with no filing/pricing/listing/control

tiering_policy:
  - First, select up to TWO items that pass DEAL TIER (Tier 1) with the richest disclosed data.
  - If fewer than TWO exist, fill remaining slots with MARKET-REP TIER (Tier 2):
      * Items that best capture current Consumer & Retail market conditions (pricing power, demand trends, traffic, basket size, promotional intensity, retail sales, confidence, policy impacts), and have concrete metrics (comps %, revenue growth %, margins %, traffic %, ASP).
      * Exclude fund trading and rumor-only pieces.
  - If zero items exist for BOTH tiers, output exactly:
    @@@ Today is a peaceful day, nothing big happened in the Consumer space.

data_missing_policy:
  - If specific multiples/segment tables are not present in the provided context/company block, skip and proceed. Do not exclude otherwise-qualifying deals.

Choose max 2 with highest materiality (deal size, control, market impact) and richest disclosed data.

If only 1 qualifies, include just 1.

If 0 qualify, output the following line EXACTLY: "@@@ Today is a peaceful day, nothing big happened in the Consumer space."
=======================================================================================================================================================================================================

CRITICAL: Focus on ONLY 2 of the most significant M&A deals, IPOs, or major transactions from the provided news items. Prioritize deals with the most detailed financial information and market impact.
ONLY SELECT NEWS WHERE A corporate transaction is specifically reported: M&A/merger, acquisition/take-private, carve-out/divestiture/spin-off, IPO/direct listing, joint venture/strategic partnership with equity, or a significant strategic stake (≥10% ownership or ≥USD 100M consideration, or board/control rights). Exclude routine portfolio trades by funds (e.g., “asset manager purchased shares”) unless they meet the threshold above.
If there is only one recent deal, then just do one deal.
For each of the 2 selected deals, ONLY provide analysis with the following structured information:

**Deal Analysis Structure:**
- **Deal Size:** [USD amount - provide specific numbers when available, estimate based on comparable deals if not specified]
- **Deal Size Category:** [Define deal size: Small cap (<$2B), Mid cap ($2B-$10B), Large cap (>$10B)]
- [Classify today's deal's nature as either Horizontal/Vertical/Tuck-in&Bolt on/Carve out/Conglomerate]
- **Valuation Multiples:** [Detailed analysis of EV/EBITDA, P/E, or other relevant multiples with industry context and comparison to peers]
- **Companies:** [Buyer] acquiring [Target] - include company descriptions and market positions
- **Date Announced:** [Specific date if mentioned, or approximate timeline]
- **Strategic Rationale:** [In-depth analysis of the strategic logic, including market positioning, synergies, competitive advantages, and long-term strategic vision]
- **Risk Analysis:** [Comprehensive risk assessment including integration risks, regulatory challenges, market risks, execution risks, and potential value destruction scenarios]

**Key Financials Analysis:** 
For each deal, provide comprehensive financial analysis including:
- **Revenue Breakdown:** Revenue breakdown based on business segments (e.g., Apple revenue by products: iPhone, Mac, Services, etc. rather than by regions) + percentage share + year-over-year growth for 3 years (Only include if applicable, if no data is available, discard)
- **Profitability Ratios:** EBITDA/revenue, Net Income/revenue ratios (Only include if applicable, if no data is available, discard)
- **Leverage Analysis:** Debt-to-Equity ratio and analysis of long-term vs short-term debt structure
- **Asset Operating Efficiency:** Working capital analysis, inventory turnover days, accounts receivable turnover days, and accounts payable turnover days
- **Valuation Context:** Combine these financial metrics with P/E and EV/EBITDA multiples for comprehensive analysis

**Profitability Metrics:**  (Only include if applicable, if no data is available, discard)
-EBITDA, EBIT, Net Income and year-over-year growth for 3 years (WRITE THIS IN THE FORM OF A TABLE, see formatting guidelines below)

**Purpose:** Use this financial analysis to roughly assess performance and business growth/decline trends, then infer the strategic rationale (e.g., whether the acquisition target provides new businesses/technologies/brand influence that the parent company lacks)

**Analysis Requirements:**
- Provide specific valuation multiples with industry benchmarks and peer comparisons
- Include detailed rationale with strategic context and market implications
- Conduct thorough risk analysis with specific risk factors and mitigation strategies
- Use concrete data points and financial metrics wherever possible
- Focus on deals with the most significant TMT sector impact and detailed financial information
- Specify capital structure

------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Formatting guidelines:
Use ### as start of sections
Use #### as start of subsections
Use **title:** as start of subsections
Use - ** as bullet points
Use @@@ to bold a line

To draw tables, use the following format:
| A | B |
| --- | --- |
| a1 | b1 |
| a2 | b2 |


IMPORTANT!
USE ONLY ONE FORMATTING PATTING PER LINE AND ONLY USE AT THE START OF A LINE!


For instance: 
- **Apple Inc. (AAPL)**: Mandated to evaluate acquisitions in the AI space, with a focus on startups that can enhance its product offerings. The timeline for this initiative is projected for Q2 2026, as Apple aims to strengthen its competitive edge in AI.
This is fine
But never do this:
- **Indiegogo Acquisition by Gamefound**: This transaction is progressing, with regulatory approvals anticipated by **Q4 2025**. The integration aims to combine Indiegogo's **38 million users** with Gamefound's technology, thereby enhancing their market position in the crowdfunding space.
Instead of "**Q4 2025**", just do Q4 2025. The same applies to every other line pats


When adding links, use this EXACT format: **Link title** ([Link](https://linkURL))
example: **JPMorgan Reports Increased M&A Activity in TMT Sector** ([Link](https://www.businessinsider.com/merger-acquisition-trends-1h-hreport-sponsors-volumes-anu-aiyengar-jpmorgan-2025-7))
MAKE SURE THE LINKS MATCH THEIR TITLES
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

**Example Structure:**
### 1. RECENT Healthcare M&A ACTIVITY

**Deal 1: [Company Name] Acquisition**
**Deal Title with Link** ([Link](URL))
- **Deal Size:** $X billion (or specific amount)
- **Valuation Multiples:** EV/EBITDA of X.Xx (vs industry average of X.Xx), P/E of X.Xx
- **Companies:** [Detailed company descriptions and market positions]
- **Date Announced:** [Specific date]
- **Strategic Rationale:** [Comprehensive strategic analysis with market context]
- **Risk Analysis:** [Detailed risk assessment with specific factors]
- **Key Financials Analysis:** [Revenue breakdown by business, profitability metrics, leverage analysis, asset efficiency, and valuation context]

**Deal 2: [Company Name] Acquisition** |(Include only if available)
[Same detailed structure as Deal 1]

**Do something like this if there isn't a single deal in the healthcare sector**
### 1. RECENT Healthcare M&A ACTIVITY

Unfortunately, there have been no reported M&A deals specifically in the Healthcare sector within the past week. This could be attributed to several factors:

- **Regulatory Scrutiny:** Increased FDA scrutiny and regulatory hurdles may be causing delays in deal approvals.
- **Market Volatility:** Recent fluctuations in biotech valuations may have led companies to adopt a more cautious approach to acquisitions.
- **Strategic Reevaluation:** Companies may be reassessing their strategic priorities in light of evolving healthcare policies and reimbursement changes.

As a result, the focus may have shifted towards organic growth strategies rather than pursuing M&A opportunities at this time.

Focus on quality over quantity - provide deep, data-driven analysis of only 2 deals rather than superficial coverage of many deals.

DO NOT INCLUDE a Recommended Readings
"""



section2PromptHealthcare = """
2. MARKET DYNAMICS & SENTIMENT

(Provide a multi-paragraph, in-depth analysis)
- Overall Healthcare sector sentiment, with breakdowns by subsector, geography, and deal type
- Key market drivers and headwinds, with supporting data
- Subsector performance analysis (e.g., Pharmaceuticals, Biotech, Medical Devices, Healthcare Services, Digital Health)
- Trading multiples trends, with specific numbers and comparisons
- Notable investor/analyst reactions, with quotes or examples
- Actionable insights for bankers and investors

**Format:**
Use ### as start of sections
Use #### as start of subsections
Use **title:** as start of subsections
Use - ** as bullet points
Use @@@ to bold a line

IMPORTANT!
USE ONLY ONE FORMATTING PATTING PER LINE AND ONLY USE AT THE START OF A LINE!

For instance: 
- **Johnson & Johnson (JNJ)**: Mandated to evaluate acquisitions in the pharmaceutical space, with a focus on biotech startups that can enhance its drug pipeline. The timeline for this initiative is projected for Q2 2026, as J&J aims to strengthen its competitive edge in precision medicine.
This is fine
But NEVER EVER do it like this "**Q4 2025**" in the middle of a line
Example:
- Pfizer Acquisition by Moderna : This transaction is progressing, with regulatory approvals anticipated by **Q4 2025**. The integration aims to combine Pfizer's **drug development assets** with Moderna's technology, thereby enhancing their market position in the healthcare space.
Instead of "**Q4 2025**", just do Q4 2025. The same applies to every other line pats. DO NOT PUT LINE PAT IN THE MIDDLE OF LINES

DO NOT INCLUDE a Recommended Readings
DO NOT PUT LINKS IN THIS SECTION

**Example Structure**
### 2. MARKET DYNAMICS & SENTIMENT

The Healthcare sector is currently experiencing a mixed sentiment, characterized by cautious optimism amid ongoing regulatory scrutiny and evolving technological advancements. The overall sentiment is influenced by various factors, including FDA approvals, reimbursement policies, and sector-specific trends.

@@@ Subsector Breakdown:
  - **Pharmaceuticals:** The pharmaceutical subsector remains robust, driven by advancements in drug development, precision medicine, and digital therapeutics. For instance, Pfizer's utilization of AI for drug discovery reflects a growing trend where companies leverage technology to enhance R&D efficiency and accelerate clinical trials.
  - **Biotech:** The biotech subsector is witnessing rapid growth as companies like Moderna enhance mRNA technology through new therapeutic applications. However, traditional pharma faces challenges from innovative biotech startups.
  - **Medical Devices:** The medical device sector is innovating with smart technologies, as demonstrated by Medtronic's introduction of AI-powered monitoring systems, which aims to improve patient outcomes and reduce healthcare costs.
  - **Healthcare Services:** The healthcare services space continues to thrive, with companies exploring new business models and partnerships, such as UnitedHealth's acquisition of digital health startups, which aims to integrate telemedicine solutions.
  - **Digital Health:** The digital health subsector is particularly hot, with companies racing to implement AI solutions across various healthcare applications, including diagnostics, where companies like Tempus are challenging traditional diagnostic models by promising to cover AI-driven precision medicine.

#### Key Market Drivers and Headwinds

 @@@ Drivers:
  - **Technological Advancements:** Continuous innovation in AI, genomics, and digital health is driving growth across healthcare sectors. For example, Moderna's mRNA technology is expected to enhance the development of personalized medicine and accelerate drug discovery.
  - **Increased Investment:** Venture capital and private equity investments remain strong, particularly in biotech and digital health, as investors seek to capitalize on emerging trends.

 @@@ Headwinds:
  - **Regulatory Scrutiny:** Increased FDA scrutiny, especially in the pharmaceutical sector, poses risks to M&A activities and market valuations. Companies are navigating complex compliance landscapes, which can delay or derail potential deals.
  - **Economic Uncertainty:** Global economic conditions, including inflation and reimbursement changes, may impact healthcare spending and investment in medical innovation.

#### Subsector Performance Analysis

- **Pharmaceuticals:** The pharmaceutical sector continues to perform well, driven by demand for innovative therapies and the success of blockbuster drugs. Companies focusing on specialty drugs are particularly well-positioned for growth.
- **Biotech:** Biotech companies are adapting to changing regulatory environments, with a shift towards precision medicine and targeted therapies. However, traditional pharma faces declining revenues from patent expirations.
- **Medical Devices:** Medical device operators are investing heavily in smart technology to support remote monitoring and personalized care, which is expected to drive new revenue streams from digital health services.
- **Healthcare Services:** The healthcare services sector is thriving, with innovations in telemedicine and value-based care. The acquisition of digital health startups by major insurers highlights the consolidation trend in this space.
- **Digital Health:** The digital health subsector is booming, with applications across various healthcare markets, including diagnostics, treatment, and patient management. Companies are investing heavily in AI capabilities to maintain competitive advantages.

#### Trading Multiples Trends

@@@ Valuation Multiples: As of Q2 2025, the average EV/EBITDA multiple for the Healthcare sector is approximately 18.5x, with notable variations across subsectors:
  - **Pharmaceuticals:** 15.3x
  - **Biotech:** 25.1x
  - **Medical Devices:** 12.8x
  - **Healthcare Services:** 14.7x
  - **Digital Health:** 28.5x

These multiples indicate a premium for high-growth sectors like biotech and digital health, while traditional sectors like medical devices and healthcare services are trading at lower multiples due to regulatory risks.

#### Notable Investor/Analyst Reactions

- Analysts are generally optimistic about the long-term prospects of the Healthcare sector, citing technological advancements as a key driver of growth. For instance, an analyst at a leading investment bank commented, "The integration of AI across healthcare is not just a trend; it's a fundamental shift that will redefine patient care and drug development."

#### Actionable Insights for Bankers and Investors

- **Focus on High-Growth Areas:** Investors should prioritize sectors with strong growth potential, such as biotech and digital health, while being cautious with traditional pharmaceutical investments.
- **Monitor Regulatory Developments:** Staying informed about FDA changes is crucial for assessing risks in healthcare investments.
- **Leverage Technology Partnerships:** Companies should explore strategic partnerships and acquisitions to enhance their technological capabilities and market positioning.
- **Evaluate Valuation Metrics:** Investors should consider current trading multiples and sector performance when making investment decisions, particularly in high-growth subsectors.

In summary, the Healthcare sector is navigating a complex landscape characterized by both opportunities and challenges. By focusing on technological advancements and understanding market dynamics, investors and bankers can position themselves for success in this evolving environment.
"""




section3PromptHealthcare = """
3. BANKING PIPELINE

(Provide a multi-paragraph, in-depth analysis)
- Deal Pipeline (Transaction Pipeline):
  * Live deals: Transactions currently in progress (M&A in due diligence, upcoming IPOs), with details and expected timing
  * Mandated deals: Transactions with secured mandates but not yet fully launched, with client names and deal types if possible
  * Pitching-stage deals: Active pitches and client discussions for potential mandates, with sector/client focus
- Pipeline tracking metrics:
  * Expected revenue/fees from active pipeline, with breakdowns
  * Timing projections (Q2 close, Q4 IPO, etc.)
  * Workload allocation and capacity analysis (e.g., analyst/associate bandwidth)
  * Forecasting and strategic planning implications
- Notable pipeline developments and competitive landscape, with examples
- Actionable insights for team management and business development

**Format:**
Use ### as start of sections
Use #### as start of subsections
Use **title:** as start of subsections
Use - ** as bullet points
Use @@@ to bold a line

IMPORTANT!
USE ONLY ONE FORMATTING PATTING PER LINE AND ONLY USE AT THE START OF A LINE!

For instance: 
- **Johnson & Johnson (JNJ)**: Mandated to evaluate acquisitions in the pharmaceutical space, with a focus on biotech startups that can enhance its drug pipeline. The timeline for this initiative is projected for Q2 2026, as J&J aims to strengthen its competitive edge in precision medicine.
This is fine
But never do this:
- Pfizer Acquisition by Moderna : This transaction is progressing, with regulatory approvals anticipated by **Q4 2025**. The integration aims to combine Pfizer's **drug development assets** with Moderna's technology, thereby enhancing their market position in the healthcare space.
Instead of "**Q4 2025**", just do Q4 2025. The same applies to every other line pats

DO NOT INCLUDE a Recommended Readings

**Follow the formatting of the Example Structure:**
### 3. BANKING PIPELINE

The current banking pipeline in the Healthcare sector reflects a dynamic landscape with a mix of live deals, mandated transactions, and active pitches. This section provides a comprehensive analysis of the ongoing activities, expected revenue, and strategic implications for our team.

#### Deal Pipeline

@@@ Live Deals:
- **Johnson & Johnson (JNJ)**: Currently in discussions for a strategic partnership leveraging AI for drug discovery. The deal is in the due diligence phase, with an expected close in Q3 2025. This partnership could enhance J&J's R&D capabilities, potentially accelerating drug development by up to 30%.
  
- **Moderna Acquisition by Pfizer**: This transaction is moving forward, with regulatory approvals anticipated by Q4 2025. The integration aims to combine Moderna's mRNA technology with Pfizer's global distribution network, enhancing their market position in vaccine development.

@@@ Mandated Deals:
- **Merck & Co. (MRK)**: Secured a mandate to explore strategic partnerships related to oncology drug development, particularly in response to FDA regulations. The deal is expected to launch in Q1 2026, focusing on compliance and innovation strategies.
  
- **Amgen Inc. (AMGN)**: Mandated to evaluate acquisitions in the rare disease space, with a focus on startups that can enhance its therapeutic portfolio. The timeline for this initiative is projected for Q2 2026, as Amgen aims to strengthen its competitive edge in precision medicine.

@@@ Pitching-Stage Deals:
- **Biotech Sector**: Active discussions with several biotech companies regarding potential M&A opportunities to consolidate market share in the gene therapy space. Clients include Gilead Sciences (GILD) and Biogen (BIIB), with pitches expected to finalize by Q3 2025.
  
- **Digital Health Startups**: Engaging with various digital health companies for potential investment banking services, focusing on those that are innovating in telemedicine and AI diagnostics. Notable clients include Teladoc Health (TDOC) and Doximity (DOCS), with discussions ongoing.

#### Pipeline Tracking Metrics

@@@ Expected Revenue/Fees: The active pipeline is projected to generate approximately $25 million in fees, broken down as follows:
  - **Live Deals**: $10 million
  - **Mandated Deals**: $8 million
  - **Pitching-Stage Deals**: $7 million

@@@ Timing Projections:
  - **Q2 2025**: Expected close for Johnson & Johnson partnership.
  - **Q4 2025**: Anticipated completion of the Moderna acquisition.
  - **Q1 2026**: Launch of Merck's strategic partnership initiatives.

- **Workload Allocation and Capacity Analysis**: 
  - Current analyst and associate bandwidth is at 75%, with a need for additional resources as the pipeline expands. It is recommended to onboard two additional analysts to manage the increased workload effectively.

- **Forecasting and Strategic Planning Implications**: The pipeline indicates a strong demand for advisory services in biotech and digital health sectors. Strategic planning should focus on enhancing capabilities in these areas to capitalize on emerging opportunities.

#### Notable Pipeline Developments and Competitive Landscape

- The competitive landscape is intensifying, particularly in the biotech sector, where companies like Johnson & Johnson and Merck are vying for leadership. The recent announcement of Biden's Healthcare Action Plan could alter the regulatory environment, impacting deal structures and valuations.
  
- Additionally, the rise of digital health startups, such as the one founded by a former Moderna executive, indicates a growing market for telemedicine solutions, which could lead to new advisory opportunities.

#### Actionable Insights for Team Management and Business Development

- **Resource Allocation**: Given the anticipated increase in deal flow, it is crucial to allocate resources effectively. Hiring additional analysts will ensure that the team can manage the workload without compromising service quality.
  
- **Sector Focus**: Prioritize business development efforts in high-growth sectors such as biotech and digital health, where demand for advisory services is expected to surge. This focus will position the firm as a leader in these emerging markets.

- **Client Engagement**: Maintain proactive communication with clients in the pipeline to ensure alignment on expectations and timelines. Regular updates will help build trust and facilitate smoother transaction processes.

In summary, the banking pipeline is robust, with significant opportunities across various Healthcare subsectors. By strategically managing resources and focusing on high-potential areas, the team can maximize its impact and drive successful outcomes for clients.
"""



section4PromptHealthcare = """
4. STAKEHOLDER IMPACT & FORWARD-LOOKING ANALYSIS

(Provide a multi-paragraph, in-depth analysis)
- Deal-specific impacts on:
  * Shareholders (value creation/dilution, with scenario analysis and numbers)
  * Employees (synergies, restructuring, retention, with examples)
  * Competitors (market positioning, with specific competitor moves)
  * Customers (product/service implications, with case studies)
- Market reaction and analyst commentary, with quotes or data
- Expected market reaction, with scenario analysis
- Potential counter-bids or competing offers, with likelihood assessment
- Similar deals likely to follow, with sector consolidation predictions
- Key risks and mitigants, with detailed breakdowns
- Actionable insights for clients and bankers

**Format:**
Use ### as start of sections
Use #### as start of subsections
Use **title:** as start of subsections
Use - ** as bullet points
Use @@@ to bold a line

IMPORTANT!
USE ONLY ONE FORMATTING PATTING PER LINE AND ONLY USE AT THE START OF A LINE!

For instance: 
- Value Creation: In a scenario where Company A (e.g. Johnson & Johnson (JNJ)) acquires Company B (e.g. Moderna Inc. (MRNA)), the combined entity could see a revenue increase of approximately 20% due to enhanced drug development capabilities.
But never ever do this:
- Pfizer Acquisition by Moderna : This transaction is progressing, with regulatory approvals anticipated by **Q4 2025**. The integration aims to combine Pfizer's **drug development assets** with Moderna's technology, thereby enhancing their market position in the healthcare space.
Instead of "**Q4 2025**", just do Q4 2025. The same applies to every other form of nested line pats

DO NOT INCLUDE a Recommended Readings

**Follow the formatting of the Example Structure:**
### 4. STAKEHOLDER IMPACT & FORWARD-LOOKING ANALYSIS

The implications of M&A transactions in the Healthcare sector extend beyond immediate financial metrics, affecting various stakeholders including shareholders, employees, competitors, and patients. This analysis delves into the potential impacts of a hypothetical acquisition, providing a comprehensive view of the landscape.

#### Deal-Specific Impacts on Stakeholders

- **Shareholders:** Deal-specific impacts on shareholders can be significant, influencing both value creation and dilution.
  - **Value Creation:** In a scenario where Company A (e.g., Johnson & Johnson (JNJ)) acquires Company B (e.g., Moderna Inc. (MRNA)), the combined entity could see a revenue increase of approximately 20% due to enhanced drug development capabilities. Assuming a pre-deal market cap of $400 billion for J&J, a successful integration could increase shareholder value by $80 billion.
  - **Dilution:** Conversely, if the acquisition is financed through stock, existing shareholders may experience dilution. For instance, if J&J issues 10% of its shares to finance the deal, existing shareholders could see their ownership stake decrease, potentially leading to a 5% drop in share price post-announcement.

- **Employees:** Impacts on employees often involve synergies, restructuring, and retention strategies.
  - **Synergies:** A merger between Pfizer (PFE) and Moderna (MRNA) led to substantial cost synergies, with estimates of $2 billion in annual savings. This was achieved through streamlined operations and shared R&D resources.
  - **Restructuring:** However, such deals often lead to layoffs. In the Pfizer-Moderna merger, approximately 5,000 jobs were cut, highlighting the need for careful planning to retain key talent.
  - **Retention:** Companies may implement retention bonuses to keep critical employees during the transition. For example, in the acquisition of Moderna by Pfizer, retention packages were offered to key Moderna executives to ensure continuity.

- **Competitors:** The competitive landscape can shift dramatically post-acquisition.
  - **Market Positioning:** Following the merger of Pfizer and Moderna, competitors such as Merck & Co. (MRK) and Johnson & Johnson (JNJ) had to adapt their strategies to maintain market share. This included aggressive R&D strategies and enhanced drug development techniques.
  - **Specific Competitor Moves:** Merck responded with a $10 billion investment in oncology research to counter the combined entity's market strength.

- **Patients:** Patient implications can vary based on the nature of the deal.
  - **Product/Service Implications:** The merger of Pfizer and Moderna allowed Pfizer to bundle vaccine development with therapeutic services, enhancing patient value. This strategy led to a 15% increase in treatment accessibility.
  - **Case Studies:** The acquisition of Moderna by Pfizer resulted in enhanced drug development capabilities, directly benefiting patients with improved treatment options.

#### Market Reaction and Analyst Commentary

- **Market Reaction:** The immediate market reaction to M&A announcements can be volatile.
For example, when Pfizer announced its acquisition of Moderna, shares of Pfizer initially dipped by 5% before recovering as analysts recognized the long-term strategic benefits.
- **Analyst Commentary:** Analysts often provide insights that shape market perceptions. A notable quote from a Morgan Stanley analyst post-acquisition was, "This deal positions Pfizer to dominate the mRNA therapeutics space, despite initial market skepticism."

#### Expected Market Reaction and Scenario Analysis

- **Scenario Analysis:** The market's reaction can be assessed through various scenarios:
- **Positive Scenario:** If the acquisition leads to successful integration and drug development growth, shares could rise by 15% within six months.
- **Negative Scenario:** If integration challenges arise, shares could decline by 10%, reflecting investor concerns about operational execution.

#### Potential Counter-Bids or Competing Offers

- **Likelihood Assessment:** The likelihood of counter-bids can vary based on market conditions.
In the case of the proposed acquisition of Moderna by Pfizer, there were rumors of interest from Merck & Co. (MRK), highlighting the competitive nature of the Healthcare sector. However, the likelihood of a successful counter-bid is moderate, as regulatory hurdles often deter competing offers.

#### Similar Deals Likely to Follow

- **Sector Consolidation Predictions:** The Healthcare sector is expected to see continued consolidation.
Analysts predict that as companies seek to enhance their drug development capabilities, similar deals will emerge, particularly in the biotech and gene therapy spaces. Companies like Amgen (AMGN) and Gilead Sciences (GILD) may pursue acquisitions to bolster their therapeutic portfolios.

#### Key Risks and Mitigants

  - **Integration Risks:** Integration challenges can lead to operational disruptions. Mitigants include appointing experienced integration teams and setting clear milestones.
  - **Regulatory Risks:** FDA scrutiny can delay or block deals. Engaging with regulators early in the process can help mitigate these risks.
  - **Market Risks:** Market volatility can impact deal valuations. Structuring deals with contingent payments can protect against adverse market movements.

#### Actionable Insights for Clients and Bankers

@@@ For Clients:
- Focus on thorough due diligence to identify potential integration challenges early.
- Consider retention strategies for key talent to ensure a smooth transition.
  
@@@ For Bankers:
- Stay informed about competitor moves and market trends to provide timely advice.
- Develop robust financial models to assess the impact of potential deals on shareholder value.
"""



section5PromptHealthcare = """
5. HEALTHCARE TRENDS

(Provide a multi-paragraph, in-depth analysis)
- Identify key emerging healthcare trends from the news (e.g., Digital Health, Precision Medicine, Gene Therapy, Telemedicine, AI in Healthcare, etc.)
- For each identified trend:
  * Provide a detailed explanation of the trend, its market significance, and growth trajectory
  * List specific companies from the news that are involved in this trend
  * For each company, provide a brief description of their activities and strategic positioning within the trend
  * Analyze the competitive landscape and market dynamics for each trend
  * Discuss potential M&A opportunities and investment implications
- Focus on trends that have significant market impact and deal-making potential
- Include examples, use cases, and market data where available
- Provide actionable insights for bankers and investors regarding trend-driven opportunities
- Refrain from writing overly lengthy reports, and MAKE SURE section can be completed within the token limit

**Format:**
Use ### as start of sections
Use #### as start of subsections
Use **title:** as start of subsections
Use - ** as bullet points
Use @@@ to bold a line

IMPORTANT!
USE ONLY ONE FORMATTING PATTING PER LINE AND ONLY USE AT THE START OF A LINE!

For instance: 
- **Johnson & Johnson (JNJ)**: Mandated to evaluate acquisitions in the pharmaceutical space, with a focus on biotech startups that can enhance its drug pipeline. The timeline for this initiative is projected for Q2 2026, as J&J aims to strengthen its competitive edge in precision medicine.
This is fine
But never do this:
- Pfizer Acquisition by Moderna : This transaction is progressing, with regulatory approvals anticipated by **Q4 2025**. The integration aims to combine Pfizer's **drug development assets** with Moderna's technology, thereby enhancing their market position in the healthcare space.
Instead of "**Q4 2025**", just do Q4 2025. The same applies to every other form of nested line pats

DO NOT INCLUDE a Recommended Readings

**Follow the formatting of the Example Structure:**
### 5. HEALTHCARE TRENDS

The healthcare landscape is rapidly evolving, with several key trends emerging that have significant market implications and deal-making potential. This analysis will focus on the following trends: Digital Health, Precision Medicine, Gene Therapy, Telemedicine, and AI in Healthcare. Each section will provide a detailed explanation of the trend, its market significance, key players, competitive dynamics, and potential M&A opportunities.

#### Digital Health

- **Trend Explanation:** Digital health encompasses technologies that improve healthcare delivery through digital platforms, mobile apps, and connected devices. The global digital health market is projected to grow from $96.5 billion in 2020 to $659.5 billion by 2025, at a CAGR of 46.8%.
  
@@@ Key Companies:
  - **Teladoc Health, Inc. (TDOC):** Teladoc is a leader in telemedicine services, providing virtual healthcare consultations across the United States. The company has strategically positioned itself in the digital health space by investing heavily in AI-powered diagnostics and remote monitoring capabilities.
  - **Doximity, Inc. (DOCS):** Doximity is at the forefront of professional networking for healthcare providers, known for its secure communication platform. The company has formed partnerships with major health systems to integrate digital health capabilities into their operations.

- **Competitive Landscape:** The digital health market is highly competitive, with major players including Amwell (AMWL), One Medical (ONEM), and Cerner Corporation (CERN) also investing heavily in digital health technologies. The race for digital health supremacy is driving innovation and pushing companies to acquire startups with unique digital capabilities.

- **M&A Opportunities:** Companies looking to enhance their digital health capabilities may consider acquiring startups specializing in niche applications, such as remote monitoring or AI diagnostics. For instance, Teladoc's acquisition of Livongo for $18.5 billion in 2020 exemplifies this trend.

#### Precision Medicine

- **Trend Explanation:** Precision medicine involves tailoring medical treatment to individual characteristics, including genetic makeup, lifestyle, and environment. The precision medicine market is expected to grow from $141.7 billion in 2020 to $216.8 billion by 2027, at a CAGR of 6.2%.

@@@ Key Companies:
  - **Illumina, Inc. (ILMN):** Illumina is a leading manufacturer of DNA sequencing systems, providing genomic analysis tools for precision medicine applications. The company is well-positioned to benefit from the growing adoption of personalized medicine and genomic testing.
  - **Foundation Medicine, Inc. (FMI):** Foundation Medicine has integrated genomic profiling into its cancer diagnostics, allowing for personalized treatment recommendations. The company's comprehensive genomic profiling has become a popular platform for precision oncology.

- **Competitive Landscape:** The precision medicine space is characterized by a mix of established diagnostic companies and innovative startups. Companies like Guardant Health (GH) and Exact Sciences (EXAS) are also significant players, focusing on liquid biopsy and cancer screening, respectively.

- **M&A Opportunities:** Healthcare companies may pursue acquisitions of precision medicine startups to enhance their diagnostic capabilities. For example, the acquisition of **Foundation Medicine** by Roche indicates a trend towards integrating precision medicine solutions into traditional healthcare operations.

#### Gene Therapy

- **Trend Explanation:** Gene therapy involves modifying genes to treat or prevent diseases by introducing, removing, or altering genetic material. The gene therapy market is projected to grow from $2.1 billion in 2020 to $13.6 billion by 2027, at a CAGR of 30.7%.

@@@ Key Companies:
  - **Spark Therapeutics, Inc. (ONCE):** Spark Therapeutics is a leader in gene therapy development, providing treatments for inherited retinal diseases. The company has strategically positioned itself in the gene therapy space by investing heavily in viral vector technology and clinical development.
  - **Bluebird Bio, Inc. (BLUE):** Bluebird Bio is at the forefront of gene therapy innovation, known for its lentiviral vector technology. The company has formed partnerships with major pharmaceutical companies to integrate gene therapy capabilities into their therapeutic portfolios.

- **Competitive Landscape:** The gene therapy market is highly competitive, with major players including Novartis (NVS), Biogen (BIIB), and Gilead Sciences (GILD) also investing heavily in gene therapy technologies. The race for gene therapy supremacy is driving innovation and pushing companies to acquire startups with unique gene editing capabilities.

- **M&A Opportunities:** Companies looking to enhance their gene therapy capabilities may consider acquiring startups specializing in niche applications, such as CRISPR gene editing or viral vector development. For instance, Novartis's acquisition of **AveXis** for $8.7 billion in 2018 exemplifies this trend.

#### Telemedicine

- **Trend Explanation:** Telemedicine enables remote healthcare delivery through digital communication technologies, improving access to care and reducing healthcare costs. The telemedicine market is expected to grow from $45.5 billion in 2020 to $175.5 billion by 2026, at a CAGR of 25.2%.

@@@ Key Companies:
  - **Amwell (AMWL):** Amwell is a leading telemedicine platform that provides virtual healthcare services to patients and providers. The company is well-positioned to benefit from the growing adoption of remote healthcare and the need for accessible medical services.
  - **One Medical (ONEM):** One Medical has integrated telemedicine technology into its primary care services, allowing for virtual consultations and remote monitoring. The company's membership-based model has become a popular platform for digital-first healthcare.

- **Competitive Landscape:** The telemedicine space is characterized by a mix of established healthcare companies and innovative startups. Companies like MDLive and PlushCare are also significant players, focusing on urgent care and primary care services, respectively.

- **M&A Opportunities:** Healthcare companies may pursue acquisitions of telemedicine startups to enhance their digital capabilities. For example, the acquisition of **One Medical** by Amazon indicates a trend towards integrating telemedicine solutions into traditional healthcare delivery.

#### AI in Healthcare

- **Trend Explanation:** AI in healthcare involves using machine learning and artificial intelligence to improve diagnosis, treatment, and patient care. The AI in healthcare market is projected to grow from $6.9 billion in 2020 to $67.4 billion by 2027, at a CAGR of 38.1%.

@@@ Key Companies:
  - **Tempus Labs, Inc.:** Tempus is a leader in AI-powered precision medicine, providing genomic analysis and clinical data insights. The company has strategically positioned itself in the AI healthcare space by investing heavily in machine learning and data analytics.
  - **Butterfly Network, Inc. (BFLY):** Butterfly Network is at the forefront of AI-powered medical imaging, known for its portable ultrasound technology. The company has formed partnerships with major health systems to integrate AI capabilities into their diagnostic workflows.

- **Competitive Landscape:** The AI in healthcare market is highly competitive, with major players including IBM Watson Health, Google Health, and Microsoft Healthcare also investing heavily in AI technologies. The race for AI healthcare supremacy is driving innovation and pushing companies to acquire startups with unique AI capabilities.

- **M&A Opportunities:** Companies looking to enhance their AI healthcare capabilities may consider acquiring startups specializing in niche applications, such as medical imaging or drug discovery. For instance, IBM's acquisition of **Merge Healthcare** for $1 billion in 2015 exemplifies this trend.

In summary, the healthcare sector is experiencing rapid transformation driven by technological advancements and regulatory changes. By focusing on emerging trends and understanding market dynamics, investors and bankers can position themselves for success in this evolving environment.
"""



section6PromptHealthcare = """
6. RECOMMENDED READINGS

For each deal mentioned in Section 1, provide ONE specific reading material and explain why it matters.

** Format for each deal:**
@@@ Deal Name: [Specific deal from Section 1]
- **Reading Material:** [Book/Article/Resource name]
- **Why This Matters:** [Clear explanation of how this reading helps understand the deal]

**Example:**
@@@ Deal Name: Johnson & Johnson's Acquisition of Actelion
- **Reading Material:** "The Innovator's Prescription" by Clayton Christensen
- **Why This Matters:** This book explains the economics of healthcare innovation and drug development, which is exactly what happened in J&J's acquisition. You'll learn how pharmaceutical companies value drug pipelines and understand why healthcare companies get such high multiples.

Keep it simple and direct - one deal, one reading, one clear explanation of why it matters.
ONLY USE DEALS RELEVANT TO THE HEALTHCARE SECTOR

**Format:**
Use ### as start of sections
Use #### as start of subsections
Use **title:** as start of subsections
Use - ** as bullet points
Use @@@ to bold a line

IMPORTANT!
USE ONLY ONE FORMATTING PATTING PER LINE AND ONLY USE AT THE START OF A LINE!

**Follow the formatting of the Example Structure:**
### 6. Recommended Readings

@@@ Deal Name: Johnson & Johnson's Acquisition of Actelion  
- **Reading Material:** "The Innovator's Prescription" by Clayton Christensen  
- **Why This Matters:** This book provides insights into healthcare innovation and pharmaceutical economics, which are crucial for understanding J&J's strategic rationale behind the $30 billion acquisition (JNJ). It explains how pharmaceutical companies leverage drug pipelines and R&D capabilities to drive revenue, helping to contextualize the deal's valuation and potential synergies.

@@@ Deal Name: Pfizer's Acquisition of Medivation  
- **Reading Material:** "The New Economics of Healthcare" by David H. Hargreaves  
- **Why This Matters:** This reading delves into the evolving landscape of healthcare and pharmaceuticals, particularly in the context of oncology drug development. It helps to understand Pfizer's $14 billion acquisition (PFE) as a strategic move to bolster its oncology portfolio and compete with rivals like Merck (MRK) and Bristol-Myers Squibb (BMY).

@@@ Deal Name: Amgen's Acquisition of Otezla  
- **Reading Material:** "The Lean Startup" by Eric Ries  
- **Why This Matters:** This book outlines methodologies for healthcare companies to innovate and grow, which is relevant for understanding Amgen's $13.4 billion acquisition (AMGN) of Otezla. It highlights the importance of integrating new therapeutic technologies and platforms to enhance patient outcomes and market positioning, aligning with Amgen's vision of a comprehensive therapeutic portfolio.

@@@ Deal Name: Gilead Sciences' Acquisition of Kite Pharma  
- **Reading Material:** "The Gene Therapy Revolution" by Chris Miller  
- **Why This Matters:** This book provides a detailed analysis of the gene therapy industry, including the strategic importance of Kite's CAR-T technology in cancer treatment. Understanding the implications of Gilead's $12 billion acquisition (GILD) helps to grasp the competitive landscape and regulatory challenges in the gene therapy space.

@@@ Deal Name: UnitedHealth's Acquisition of Optum  
- **Reading Material:** "The Healthcare Industry: A Comprehensive Guide" by David H. Hargreaves  
- **Why This Matters:** This resource offers an in-depth look at the healthcare services and insurance sector, which is essential for analyzing UnitedHealth's $13.8 billion acquisition (UNH) of Optum. It explains market segmentation and the significance of integrated healthcare services, providing context for UnitedHealth's strategy to expand its service offerings and patient care capabilities.

@@@ Deal Name: Medtronic's Acquisition of Covidien  
- **Reading Material:** "Medical Device Innovation: The Future of Healthcare" by David H. Hargreaves  
- **Why This Matters:** This reading discusses the growth of medical device technology and healthcare innovation, which are central to Medtronic's $49.9 billion acquisition (MDT) of Covidien. It highlights how this deal positions Medtronic to compete in the medical device space against Johnson & Johnson (JNJ) and other healthcare giants, emphasizing the importance of technology in the future of patient care.
"""



section7PromptHealthcare = """
7. MACROECONOMIC UPDATE

Summarize key macroeconomic data and insights relevant to the healthcare sector from the provided content. Focus on data points, trends, and insights that impact healthcare companies, pharmaceutical valuations, and sector performance. Quote some lines from the transcript to support your claim.

**Format:**
Use ### as start of sections
Use #### as start of subsections
Use **title:** as start of subsections
Use - ** as bullet points
Use @@@ to bold a line

IMPORTANT!
USE ONLY ONE FORMATTING PATTING PER LINE AND ONLY USE AT THE START OF A LINE!

**Follow the formatting of the Example Structure:**
### 7. Macroeconomic Update

**Key Economic Indicators:**
- **Healthcare Sector Performance:** The S&P 500 Healthcare Index (^SP500-35) has shown resilience, with major healthcare companies like Johnson & Johnson (JNJ), Pfizer (PFE), and UnitedHealth Group (UNH) maintaining strong balance sheets despite broader market volatility.

- **Interest Rate Impact:** Current Federal Reserve policies and interest rate environment are influencing healthcare company valuations, particularly for growth-oriented biotech firms and pharmaceutical companies with significant R&D pipelines.

- **Regulatory Environment:** Ongoing FDA approval processes and healthcare policy developments are creating both opportunities and challenges for healthcare M&A activity, with companies strategically positioning themselves for regulatory changes.

**Market Trends:**
- **Pharmaceutical Innovation:** Continued focus on breakthrough therapies, particularly in oncology and rare diseases, is driving premium valuations for companies with innovative drug pipelines.

- **Healthcare Technology Integration:** The convergence of technology and healthcare is accelerating, with companies investing heavily in digital health solutions and telemedicine platforms.

- **Global Healthcare Spending:** International healthcare spending patterns and demographic shifts are influencing strategic decisions for multinational healthcare corporations.

**Sector-Specific Insights:**
- **Biotech Valuations:** Biotech companies are experiencing increased scrutiny from investors, with a focus on clinical trial outcomes and regulatory approval timelines.

- **Healthcare Services Consolidation:** Ongoing consolidation in healthcare services is creating larger, more integrated healthcare systems with enhanced bargaining power.

- **Insurance Market Dynamics:** Changes in healthcare insurance markets are affecting provider networks and reimbursement models, impacting healthcare service companies.

**Risk Factors:**
- **Patent Expirations:** Major pharmaceutical companies face patent cliff challenges, necessitating strategic acquisitions to replenish drug pipelines.

- **Regulatory Uncertainty:** Changes in healthcare policy and reimbursement models create uncertainty for healthcare companies and their investors.

- **Global Supply Chain:** International supply chain disruptions continue to impact pharmaceutical manufacturing and distribution networks.

**Investment Implications:**
- **Defensive Positioning:** Healthcare stocks continue to serve as defensive plays in volatile markets, with stable cash flows and dividend growth.

- **Growth Opportunities:** Emerging markets and innovative therapies present growth opportunities for healthcare companies willing to take calculated risks.

- **M&A Activity:** Continued consolidation expected in healthcare, with larger companies acquiring innovative startups and smaller competitors to maintain competitive advantages.
"""



section1PromptIndustrial = """
1. RECENT Industrial M&A ACTIVITY

=======================================================================================================================================================================================================
qualification_rules (softened):
  Qualify an item for DEAL TIER (Tier 1) if BOTH of these buckets are satisfied:

  A) action_signal (need ≥1):
     - acquisition / acquire / acquiring / bought / buyout
     - merger / merge / agreed to merge / merger-of-equals / reverse merger
     - take-private / privatization
     - carve-out / divestiture / spin-off
     - IPO or direct listing verbs: files prospectus/DRHP/F-1/S-1, prices IPO, lists
     - strategic equity: takes X% stake, majority stake, joint venture, board rights, exclusivity

  B) materiality_signal (need ≥1):
     - a hard number tied to the transaction (deal value, stake %, valuation, offer size/shares, multiple)
     - OR explicit control language (majority, control, board seats/rights, exclusivity)

  Notes:
    - Missing detailed multiples or segment tables does NOT disqualify a deal; use "N/A" where data isn’t in context.
    - Routine wording like “plans/consider/explore” alone is NOT an action_signal unless paired with a filing/pricing/listing or an explicit control/majority/board-rights statement.

do_not_include (minimal but firm):
  - routine fund/ETF/13F trading (increased/trimmed/holds) unless framed as strategic stake that meets materiality_signal
  - earnings, product launches, or partnerships with no equity/control
  - vague “planning to IPO next year” with no filing/pricing/listing/control

tiering_policy:
  - First, select up to TWO items that pass DEAL TIER (Tier 1) with the richest disclosed data.
  - If fewer than TWO exist, fill remaining slots with MARKET-REP TIER (Tier 2):
      * Items that best capture current Consumer & Retail market conditions (pricing power, demand trends, traffic, basket size, promotional intensity, retail sales, confidence, policy impacts), and have concrete metrics (comps %, revenue growth %, margins %, traffic %, ASP).
      * Exclude fund trading and rumor-only pieces.
  - If zero items exist for BOTH tiers, output exactly:
    @@@ Today is a peaceful day, nothing big happened in the Consumer space.

data_missing_policy:
  - If specific multiples/segment tables are not present in the provided context/company block, skip and proceed. Do not exclude otherwise-qualifying deals.

Choose max 2 with highest materiality (deal size, control, market impact) and richest disclosed data.

If only 1 qualifies, include just 1.

If 0 qualify, output the following line EXACTLY: "@@@ Today is a peaceful day, nothing big happened in the Consumer space."
=======================================================================================================================================================================================================

CRITICAL: Focus on ONLY 2 of the most significant M&A deals, IPOs, or major transactions from the provided news items. Prioritize deals with the most detailed financial information and market impact.
ONLY SELECT NEWS WHERE A corporate transaction is specifically reported: M&A/merger, acquisition/take-private, carve-out/divestiture/spin-off, IPO/direct listing, joint venture/strategic partnership with equity, or a significant strategic stake (≥10% ownership or ≥USD 100M consideration, or board/control rights). Exclude routine portfolio trades by funds (e.g., “asset manager purchased shares”) unless they meet the threshold above.
If there is only one recent deal, then just do one deal.
For each of the 2 selected deals, ONLY provide analysis with the following structured information:

**Deal Analysis Structure:**
- **Deal Size:** [USD amount - provide specific numbers when available, estimate based on comparable deals if not specified]
- **Deal Size Category:** [Define deal size: Small cap (<$2B), Mid cap ($2B-$10B), Large cap (>$10B)]
- [Classify today's deal's nature as either Horizontal/Vertical/Tuck-in&Bolt on/Carve out/Conglomerate]
- **Valuation Multiples:** [Detailed analysis of EV/EBITDA, P/E, or other relevant multiples with industry context and comparison to peers]
- **Companies:** [Buyer] acquiring [Target] - include company descriptions and market positions
- **Date Announced:** [Specific date if mentioned, or approximate timeline]
- **Strategic Rationale:** [In-depth analysis of the strategic logic, including market positioning, synergies, competitive advantages, and long-term strategic vision]
- **Risk Analysis:** [Comprehensive risk assessment including integration risks, regulatory challenges, market risks, execution risks, and potential value destruction scenarios]

**Key Financials Analysis:** 
For each deal, provide comprehensive financial analysis including:
- **Revenue Breakdown:** Revenue breakdown based on business segments (e.g., Apple revenue by products: iPhone, Mac, Services, etc. rather than by regions) + percentage share + year-over-year growth for 3 years (Only include if applicable, if no data is available, discard)
- **Profitability Ratios:** EBITDA/revenue, Net Income/revenue ratios (Only include if applicable, if no data is available, discard)
- **Leverage Analysis:** Debt-to-Equity ratio and analysis of long-term vs short-term debt structure
- **Asset Operating Efficiency:** Working capital analysis, inventory turnover days, accounts receivable turnover days, and accounts payable turnover days
- **Valuation Context:** Combine these financial metrics with P/E and EV/EBITDA multiples for comprehensive analysis

**Profitability Metrics:**  (Only include if applicable, if no data is available, discard)
-EBITDA, EBIT, Net Income and year-over-year growth for 3 years (WRITE THIS IN THE FORM OF A TABLE, see formatting guidelines below)

**Purpose:** Use this financial analysis to roughly assess performance and business growth/decline trends, then infer the strategic rationale (e.g., whether the acquisition target provides new businesses/technologies/brand influence that the parent company lacks)

**Analysis Requirements:**
- Provide specific valuation multiples with industry benchmarks and peer comparisons
- Include detailed rationale with strategic context and market implications
- Conduct thorough risk analysis with specific risk factors and mitigation strategies
- Use concrete data points and financial metrics wherever possible
- Focus on deals with the most significant TMT sector impact and detailed financial information
- Specify capital structure

------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Formatting guidelines:
Use ### as start of sections
Use #### as start of subsections
Use **title:** as start of subsections
Use - ** as bullet points
Use @@@ to bold a line

To draw tables, use the following format:
| A | B |
| --- | --- |
| a1 | b1 |
| a2 | b2 |


IMPORTANT!
USE ONLY ONE FORMATTING PATTING PER LINE AND ONLY USE AT THE START OF A LINE!


For instance: 
- **Apple Inc. (AAPL)**: Mandated to evaluate acquisitions in the AI space, with a focus on startups that can enhance its product offerings. The timeline for this initiative is projected for Q2 2026, as Apple aims to strengthen its competitive edge in AI.
This is fine
But never do this:
- **Indiegogo Acquisition by Gamefound**: This transaction is progressing, with regulatory approvals anticipated by **Q4 2025**. The integration aims to combine Indiegogo's **38 million users** with Gamefound's technology, thereby enhancing their market position in the crowdfunding space.
Instead of "**Q4 2025**", just do Q4 2025. The same applies to every other line pats


When adding links, use this EXACT format: **Link title** ([Link](https://linkURL))
example: **JPMorgan Reports Increased M&A Activity in TMT Sector** ([Link](https://www.businessinsider.com/merger-acquisition-trends-1h-hreport-sponsors-volumes-anu-aiyengar-jpmorgan-2025-7))
MAKE SURE THE LINKS MATCH THEIR TITLES
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


**Example Structure:**
### 1. RECENT Industrial M&A ACTIVITY

**Deal 1: [Company Name] Acquisition**
**Deal Title with Link** ([Link](URL))
- **Deal Size:** $X billion (or specific amount)
- **Valuation Multiples:** EV/EBITDA of X.Xx (vs industry average of X.Xx), P/E of X.Xx
- **Companies:** [Detailed company descriptions and market positions]
- **Date Announced:** [Specific date]
- **Strategic Rationale:** [Comprehensive strategic analysis with market context]
- **Risk Analysis:** [Detailed risk assessment with specific factors]
- **Key Financials Analysis:** [Revenue breakdown by business, profitability metrics, leverage analysis, asset efficiency, and valuation context]

**Deal 2: [Company Name] Acquisition** |(Include only if available, if not, just do nothing)
[Same detailed structure as Deal 1]

Focus on quality over quantity - provide data-driven analysis of deals rather than superficial coverage of many deals.

DO NOT INCLUDE a Recommended Readings
"""



section2PromptIndustrial = """
2. MARKET DYNAMICS & SENTIMENT

(Provide a multi-paragraph, in-depth analysis)
- Overall Industrial sector sentiment, with breakdowns by subsector, geography, and deal type
- Key market drivers and headwinds, with supporting data
- Subsector performance analysis (e.g., Aerospace & Defense, Automotive, Construction, Manufacturing, Transportation, Machinery)
- Trading multiples trends, with specific numbers and comparisons
- Notable investor/analyst reactions, with quotes or examples
- Actionable insights for bankers and investors

**Format:**
Use ### as start of sections
Use #### as start of subsections
Use **title:** as start of subsections
Use - ** as bullet points
Use @@@ to bold a line

IMPORTANT!
USE ONLY ONE FORMATTING PATTING PER LINE AND ONLY USE AT THE START OF A LINE!

For instance: 
- **General Electric (GE)**: Mandated to evaluate acquisitions in the aerospace space, with a focus on startups that can enhance its aviation portfolio. The timeline for this initiative is projected for Q2 2026, as GE aims to strengthen its competitive edge in sustainable aviation.
This is fine
But NEVER EVER do it this:
- Caterpillar Acquisition by Deere : This transaction is progressing, with regulatory approvals anticipated by **Q4 2025**. The integration aims to combine Caterpillar's **construction equipment assets** with Deere's technology, thereby enhancing their market position in the industrial space.
Instead of "**Q4 2025**", just do Q4 2025. The same applies to every other line pats. DO NOT PUT LINE PAT IN THE MIDDLE OF LINES

DO NOT PUT LINKS IN THIS SECTION

**Example Structure**
### 2. MARKET DYNAMICS & SENTIMENT

The Industrial sector is currently experiencing a mixed sentiment, characterized by cautious optimism amid ongoing regulatory scrutiny and evolving technological advancements. The overall sentiment is influenced by various factors, including macroeconomic conditions, investor confidence, and sector-specific trends.

@@@ Subsector Breakdown:
  - **Aerospace & Defense:** The aerospace and defense subsector remains robust, driven by advancements in sustainable aviation, space technology, and defense modernization. For instance, Boeing's utilization of AI for predictive maintenance reflects a growing trend where companies leverage technology to enhance operational efficiency and safety.
  - **Automotive:** The automotive subsector is witnessing a transformation as companies like Tesla enhance vehicle capabilities through new digital features. However, traditional automakers face challenges from electric vehicle adoption.
  - **Construction:** The construction sector is innovating with smart building technologies, as demonstrated by Caterpillar's introduction of autonomous construction equipment, which aims to improve efficiency and safety on job sites.
  - **Manufacturing:** The manufacturing space continues to thrive, with companies exploring new business models and partnerships, such as 3M's acquisition of industrial automation assets, which aims to integrate smart manufacturing solutions.
  - **Transportation & Logistics:** The transportation and logistics subsectors are particularly hot, with companies racing to implement autonomous solutions across various markets, including freight, where companies are challenging traditional logistics models by promising to reduce delivery times.

#### Key Market Drivers and Headwinds

 @@@ Drivers:
  - **Digital Transformation:** Continuous innovation in industrial IoT, automation, and smart manufacturing technologies is driving growth across industrial sectors. For example, Siemens' digital twin technology is expected to enhance the performance of manufacturing applications reliant on predictive maintenance.
  - **Increased Investment:** Venture capital and private equity investments remain strong, particularly in industrial automation and sustainable technologies, as investors seek to capitalize on emerging trends.

 @@@ Headwinds:
  - **Regulatory Scrutiny:** Increased regulatory scrutiny, especially in the aerospace and automotive sectors, poses risks to M&A activities and market valuations. Companies are navigating complex compliance landscapes, which can delay or derail potential deals.
  - **Economic Uncertainty:** Global economic conditions, including inflation and supply chain disruptions, may impact industrial demand and investment in manufacturing infrastructure.

#### Trading Multiples and Performance Analysis

@@@ Current Trading Multiples:
  - **Aerospace & Defense:** EV/EBITDA of 12.5x (vs 5-year average of 10.8x), P/E of 18.2x
  - **Automotive:** EV/EBITDA of 8.3x (vs 5-year average of 7.1x), P/E of 14.7x
  - **Construction:** EV/EBITDA of 9.1x (vs 5-year average of 8.4x), P/E of 16.3x
  - **Manufacturing:** EV/EBITDA of 10.2x (vs 5-year average of 9.6x), P/E of 17.8x

#### Notable Investor/Analyst Reactions

- Analysts are generally optimistic about the long-term prospects of the Industrial sector, citing technological advancements as a key driver of growth. For instance, an analyst at a leading investment bank commented, "The integration of AI across industrial applications is not just a trend; it's a fundamental shift that will redefine manufacturing and operational efficiency."

#### Actionable Insights for Bankers and Investors

- **Focus on High-Growth Areas:** Investors should prioritize sectors with strong growth potential, such as industrial automation and sustainable technologies, while being cautious with traditional manufacturing investments.
- **Monitor Regulatory Developments:** Staying informed about regulatory changes is crucial for assessing risks in industrial investments.
- **Leverage Technology Partnerships:** Companies should explore strategic partnerships and acquisitions to enhance their technological capabilities and market positioning.
- **Evaluate Valuation Metrics:** Investors should consider current trading multiples and sector performance when making investment decisions, particularly in high-growth subsectors.

In summary, the Industrial sector is navigating a complex landscape characterized by both opportunities and challenges. By focusing on technological advancements and understanding market dynamics, investors and bankers can position themselves for success in this evolving environment.
"""


section3PromptIndustrial = """
3. BANKING PIPELINE

(Provide a multi-paragraph, in-depth analysis)
- Deal Pipeline (Transaction Pipeline):
  * Live deals: Transactions currently in progress (M&A in due diligence, upcoming IPOs), with details and expected timing
  * Mandated deals: Transactions with secured mandates but not yet fully launched, with client names and deal types if possible
  * Pitching-stage deals: Active pitches and client discussions for potential mandates, with sector/client focus
- Pipeline tracking metrics:
  * Expected revenue/fees from active pipeline, with breakdowns
  * Timing projections (Q2 close, Q4 IPO, etc.)
  * Workload allocation and capacity analysis (e.g., analyst/associate bandwidth)
  * Forecasting and strategic planning implications
- Notable pipeline developments and competitive landscape, with examples
- Actionable insights for team management and business development

**Format:**
Use ### as start of sections
Use #### as start of subsections
Use **title:** as start of subsections
Use - ** as bullet points
Use @@@ to bold a line

IMPORTANT!
USE ONLY ONE FORMATTING PATTING PER LINE AND ONLY USE AT THE START OF A LINE!

For instance: 
- **General Electric (GE)**: Mandated to evaluate acquisitions in the aerospace space, with a focus on startups that can enhance its aviation portfolio. The timeline for this initiative is projected for Q2 2026, as GE aims to strengthen its competitive edge in sustainable aviation.
This is fine
But never do this:
- Caterpillar Acquisition by Deere : This transaction is progressing, with regulatory approvals anticipated by **Q4 2025**. The integration aims to combine Caterpillar's **construction equipment assets** with Deere's technology, thereby enhancing their market position in the industrial space.
Instead of "**Q4 2025**", just do Q4 2025. The same applies to every other line pats

DO NOT INCLUDE a Recommended Readings

**Follow the formatting of the Example Structure:**
### 3. BANKING PIPELINE

The Industrial sector banking pipeline demonstrates robust activity across multiple subsectors, with significant opportunities in aerospace, automotive, and manufacturing. The current pipeline reflects a strategic focus on technology-driven acquisitions and sustainable industrial solutions.

#### Deal Pipeline Overview

@@@ Live Deals:
  - **Boeing Strategic Partnership**: Currently in due diligence phase for a major aerospace technology acquisition, expected to close in Q3 2025. The deal involves integrating advanced manufacturing capabilities to enhance production efficiency.
  - **Tesla Manufacturing Expansion**: Active discussions for acquiring industrial automation assets to support Gigafactory expansion, with regulatory approvals anticipated by Q4 2025.

@@@ Mandated Deals:
  - **General Electric (GE)**: Mandated to evaluate acquisitions in the aerospace space, with a focus on startups that can enhance its aviation portfolio. The timeline for this initiative is projected for Q2 2026, as GE aims to strengthen its competitive edge in sustainable aviation.
  - **Caterpillar Inc. (CAT)**: Engaged to explore strategic partnerships in construction technology, targeting companies that can enhance its autonomous equipment capabilities. The mandate includes evaluating both minority investments and full acquisitions.

@@@ Pitching-Stage Deals:
  - **Deere & Company (DE)**: Active discussions for agricultural technology acquisitions, with focus on precision farming solutions and autonomous machinery.
  - **3M Company (MMM)**: Exploring opportunities in industrial automation and smart manufacturing technologies to enhance its diversified industrial portfolio.

#### Pipeline Tracking Metrics

@@@ Expected Revenue/Fees: The active pipeline is projected to generate approximately $22 million in fees, broken down as follows:
  - **Live Deals**: $9 million
  - **Mandated Deals**: $7 million
  - **Pitching-Stage Deals**: $6 million

@@@ Timing Projections:
  - **Q3 2025**: Expected close for Boeing strategic partnership.
  - **Q4 2025**: Anticipated completion of Tesla manufacturing expansion.
  - **Q2 2026**: Launch of GE's aerospace acquisition initiatives.

- **Workload Allocation and Capacity Analysis**: 
  - Current analyst and associate bandwidth is at 70%, with a need for additional resources as the pipeline expands. It is recommended to onboard one additional analyst to manage the increased workload effectively.

- **Forecasting and Strategic Planning Implications**: The pipeline indicates a strong demand for advisory services in aerospace and automotive sectors. Strategic planning should focus on enhancing capabilities in these areas to capitalize on emerging opportunities.

#### Notable Pipeline Developments and Competitive Landscape

- The competitive landscape is intensifying, particularly in the aerospace sector, where companies like Boeing and Airbus are vying for leadership in sustainable aviation. The recent focus on defense modernization could alter the regulatory environment, impacting deal structures and valuations.
  
- Additionally, the rise of industrial automation startups indicates a growing market for smart manufacturing solutions, which could lead to new advisory opportunities.

#### Actionable Insights for Team Management and Business Development

- **Resource Allocation**: Given the anticipated increase in deal flow, it is crucial to allocate resources effectively. Hiring additional analysts will ensure that the team can manage the workload without compromising service quality.
  
- **Sector Focus**: Prioritize business development efforts in high-growth sectors such as aerospace and automotive, where demand for advisory services is expected to surge. This focus will position the firm as a leader in these emerging markets.

- **Client Engagement**: Maintain proactive communication with clients in the pipeline to ensure alignment on expectations and timelines. Regular updates will help build trust and facilitate smoother transaction processes.

In summary, the banking pipeline is robust, with significant opportunities across various Industrial subsectors. By strategically managing resources and focusing on high-potential areas, the team can maximize its impact and drive successful outcomes for clients.
"""


section4PromptIndustrial = """
4. STAKEHOLDER IMPACT & FORWARD-LOOKING ANALYSIS

(Provide a multi-paragraph, in-depth analysis)
- Deal-specific impacts on:
  * Shareholders (value creation/dilution, with scenario analysis and numbers)
  * Employees (synergies, restructuring, retention, with examples)
  * Competitors (market positioning, with specific competitor moves)
  * Customers (product/service implications, with case studies)
- Market reaction and analyst commentary, with quotes or data
- Expected market reaction, with scenario analysis
- Potential counter-bids or competing offers, with likelihood assessment
- Similar deals likely to follow, with sector consolidation predictions
- Key risks and mitigants, with detailed breakdowns
- Actionable insights for clients and bankers

**Format:**
Use ### as start of sections
Use #### as start of subsections
Use **title:** as start of subsections
Use - ** as bullet points
Use @@@ to bold a line

IMPORTANT!
USE ONLY ONE FORMATTING PATTING PER LINE AND ONLY USE AT THE START OF A LINE!

For instance: 
- **General Electric (GE)**: Mandated to evaluate acquisitions in the aerospace space, with a focus on startups that can enhance its aviation portfolio. The timeline for this initiative is projected for Q2 2026, as GE aims to strengthen its competitive edge in sustainable aviation.
This is fine
But never do this:
- Caterpillar Acquisition by Deere : This transaction is progressing, with regulatory approvals anticipated by **Q4 2025**. The integration aims to combine Caterpillar's **construction equipment assets** with Deere's technology, thereby enhancing their market position in the industrial space.
Instead of "**Q4 2025**", just do Q4 2025. The same applies to every other line pats

DO NOT INCLUDE a Recommended Readings

**Follow the formatting of the Example Structure:**
### 4. STAKEHOLDER IMPACT & FORWARD-LOOKING ANALYSIS

The Industrial sector M&A landscape presents significant implications for various stakeholders, with particular focus on technological integration and operational efficiency improvements. This analysis examines the broader impact of recent transactions and provides forward-looking insights for market participants.

#### Deal-Specific Stakeholder Impacts

@@@ Shareholder Impact:
  - **Value Creation Potential**: Recent industrial acquisitions have demonstrated average shareholder value creation of 15-20% over 12-month periods, driven primarily by operational synergies and market expansion opportunities.
  - **Dilution Concerns**: While some deals involve equity components, the strategic rationale typically outweighs dilution concerns, with most transactions showing positive total shareholder return within 18 months.

@@@ Employee Impact:
  - **Synergy Realization**: Industrial M&A typically results in 8-12% workforce optimization through operational synergies, with focus on eliminating redundant functions while preserving core technical capabilities.
  - **Retention Strategies**: Key talent retention rates average 85% in successful industrial integrations, supported by retention bonuses and career development opportunities.

@@@ Competitor Impact:
  - **Market Positioning**: Major industrial acquisitions often trigger competitive responses, with rivals typically announcing strategic initiatives within 6-12 months to maintain market position.
  - **Technology Arms Race**: The focus on industrial automation and smart manufacturing has intensified competition, with companies investing heavily in R&D to maintain technological leadership.

@@@ Customer Impact:
  - **Product Integration**: Customers benefit from integrated solutions and enhanced service capabilities, with typical improvements in delivery times and product quality.
  - **Pricing Dynamics**: While some consolidation may lead to pricing power, the competitive nature of industrial markets generally maintains customer value propositions.

#### Market Reaction and Analyst Commentary

@@@ Current Market Sentiment:
  - "Industrial M&A activity reflects a strategic shift towards technology integration and operational efficiency" - Goldman Sachs Industrial Research
  - "The focus on sustainable technologies and automation is driving premium valuations in the sector" - Morgan Stanley

@@@ Expected Market Reaction:
  - **Bullish Scenario**: Continued M&A activity could drive sector re-rating, with potential 10-15% upside in industrial multiples.
  - **Bearish Scenario**: Economic headwinds or regulatory challenges could dampen deal activity, leading to 5-8% multiple compression.

#### Potential Counter-Bids and Competing Offers

@@@ Likelihood Assessment:
  - **High Probability (70-80%)**: Strategic acquisitions in aerospace and defense sectors, where national security considerations often trigger competing offers.
  - **Medium Probability (40-50%)**: Manufacturing and automotive deals, where regulatory approval timelines allow for competing bids.
  - **Low Probability (20-30%)**: Construction and machinery deals, where integration complexity typically deters competing offers.

#### Similar Deals and Sector Consolidation Predictions

@@@ Expected Consolidation Trends:
  - **Aerospace & Defense**: Continued consolidation expected, with focus on technology integration and supply chain optimization.
  - **Automotive**: Electric vehicle and autonomous driving technologies likely to drive further M&A activity.
  - **Manufacturing**: Industrial automation and smart manufacturing solutions expected to be key acquisition targets.

#### Key Risks and Mitigants

@@@ Integration Risks:
  - **Technology Integration**: Complex industrial systems require careful integration planning, with typical 12-18 month timelines for full operational integration.
  - **Cultural Alignment**: Industrial companies often have distinct operational cultures that require focused change management programs.

@@@ Regulatory Risks:
  - **Antitrust Concerns**: Large industrial deals face increased regulatory scrutiny, particularly in concentrated markets.
  - **National Security**: Defense and aerospace deals may face additional regulatory hurdles related to national security considerations.

#### Actionable Insights for Clients and Bankers

@@@ For Clients:
  - **Strategic Planning**: Focus on technology-driven acquisitions that enhance operational efficiency and market positioning.
  - **Due Diligence**: Prioritize operational and cultural due diligence to ensure successful integration outcomes.

@@@ For Bankers:
  - **Deal Structuring**: Consider phased integration approaches to manage complexity and reduce execution risk.
  - **Valuation Approach**: Factor in technology synergies and operational improvements when developing valuation models.

In summary, the Industrial sector presents significant opportunities for value creation through strategic M&A, with particular focus on technology integration and operational efficiency. Success requires careful planning, execution, and stakeholder management to realize the full potential of these transactions.
"""


section5PromptIndustrial = """
5. INDUSTRIAL TRENDS

(Provide a multi-paragraph, in-depth analysis)
- Identify key emerging industrial trends from the news (e.g., Industrial IoT, Smart Manufacturing, Sustainable Aviation, Autonomous Vehicles, Digital Twins, Predictive Maintenance, etc.)
- For each identified trend:
  * Provide a detailed explanation of the trend, its market significance, and growth trajectory
  * List specific companies from the news that are involved in this trend
  * For each company, provide a brief description of their activities and strategic positioning within the trend
  * Analyze the competitive landscape and market dynamics for each trend
  * Discuss potential M&A opportunities and investment implications
- Focus on trends that have significant market impact and deal-making potential
- Include examples, use cases, and market data where available
- Provide actionable insights for bankers and investors regarding trend-driven opportunities
- Refrain from writing overly lengthy reports, and MAKE SURE section can be completed within the token limit

**Format:**
Use ### as start of sections
Use #### as start of subsections
Use **title:** as start of subsections
Use - ** as bullet points
Use @@@ to bold a line

IMPORTANT!
USE ONLY ONE FORMATTING PATTING PER LINE AND ONLY USE AT THE START OF A LINE!

For instance: 
- **General Electric (GE)**: Mandated to evaluate acquisitions in the aerospace space, with a focus on startups that can enhance its aviation portfolio. The timeline for this initiative is projected for Q2 2026, as GE aims to strengthen its competitive edge in sustainable aviation.
This is fine
But never do this:
- Caterpillar Acquisition by Deere : This transaction is progressing, with regulatory approvals anticipated by **Q4 2025**. The integration aims to combine Caterpillar's **construction equipment assets** with Deere's technology, thereby enhancing their market position in the industrial space.
Instead of "**Q4 2025**", just do Q4 2025. The same applies to every other form of nested line pats

DO NOT INCLUDE a Recommended Readings

**Follow the formatting of the Example Structure:**
### 5. INDUSTRIAL TRENDS

The industrial landscape is rapidly evolving, with several key trends emerging that have significant market implications and deal-making potential. This analysis will focus on the following trends: Industrial IoT, Smart Manufacturing, Sustainable Aviation, Autonomous Vehicles, Digital Twins, and Predictive Maintenance. Each section will provide a detailed explanation of the trend, its market significance, key players, competitive dynamics, and potential M&A opportunities.

#### Industrial IoT (IIoT)

- **Trend Explanation:** Industrial IoT encompasses connected devices, sensors, and systems that enable real-time monitoring and control of industrial processes. The global IIoT market is projected to grow from $77.3 billion in 2020 to $110.6 billion by 2025, at a CAGR of 7.4%.
  
@@@ Key Companies:
  - **Siemens AG (SIEGY):** Siemens is a leader in industrial automation and digitalization, providing comprehensive IIoT solutions across manufacturing, energy, and infrastructure sectors. The company has strategically positioned itself in the IIoT space by investing heavily in MindSphere platform and digital twin technologies.
  - **General Electric (GE):** GE is at the forefront of industrial IoT through its Predix platform, known for its predictive analytics and asset performance management capabilities. The company has formed partnerships with major industrial players to integrate IIoT capabilities into their operations.

#### Smart Manufacturing

- **Trend Explanation:** Smart manufacturing leverages advanced technologies such as AI, robotics, and automation to optimize production processes and improve efficiency. The global smart manufacturing market is expected to reach $384.8 billion by 2025, growing at a CAGR of 12.4%.

@@@ Key Companies:
  - **Rockwell Automation (ROK):** Rockwell Automation specializes in industrial automation and information solutions, with a focus on smart manufacturing technologies. The company's FactoryTalk platform enables seamless integration of manufacturing systems and data analytics.
  - **Schneider Electric (SBGSF):** Schneider Electric provides comprehensive smart manufacturing solutions, including EcoStruxure platform for industrial automation and energy management.

#### Sustainable Aviation

- **Trend Explanation:** Sustainable aviation focuses on reducing carbon emissions through alternative fuels, electric aircraft, and operational efficiency improvements. The sustainable aviation fuel market is projected to grow from $66 million in 2020 to $15.3 billion by 2030.

@@@ Key Companies:
  - **Boeing (BA):** Boeing is investing heavily in sustainable aviation technologies, including partnerships for sustainable aviation fuel development and electric aircraft research. The company aims to achieve carbon-neutral growth by 2030.
  - **Airbus (EADSY):** Airbus is leading the development of hydrogen-powered aircraft and sustainable aviation solutions, with the ZEROe program targeting zero-emission commercial aircraft by 2035.

#### Autonomous Vehicles

- **Trend Explanation:** Autonomous vehicle technology is transforming transportation across multiple sectors, including automotive, freight, and industrial applications. The global autonomous vehicle market is expected to reach $556.67 billion by 2026.

@@@ Key Companies:
  - **Tesla (TSLA):** Tesla is a pioneer in autonomous vehicle technology, with its Full Self-Driving (FSD) system and Autopilot features. The company's approach combines hardware and software to enable autonomous driving capabilities.
  - **Waymo (GOOGL):** Waymo, a subsidiary of Alphabet, is developing autonomous driving technology for various applications, including passenger vehicles and freight transportation.

#### Digital Twins

- **Trend Explanation:** Digital twins create virtual replicas of physical assets, processes, or systems to enable simulation, monitoring, and optimization. The global digital twin market is projected to grow from $3.1 billion in 2020 to $48.2 billion by 2026.

@@@ Key Companies:
  - **Microsoft (MSFT):** Microsoft provides comprehensive digital twin solutions through Azure Digital Twins platform, enabling organizations to create and manage digital representations of their physical environments.
  - **IBM (IBM):** IBM offers digital twin capabilities through its Watson IoT platform, with focus on predictive analytics and optimization for industrial applications.

#### Predictive Maintenance

- **Trend Explanation:** Predictive maintenance uses data analytics and machine learning to predict equipment failures before they occur, reducing downtime and maintenance costs. The global predictive maintenance market is expected to reach $23.5 billion by 2026.

@@@ Key Companies:
  - **Caterpillar (CAT):** Caterpillar has integrated predictive maintenance capabilities into its equipment through Cat Connect technology, enabling customers to optimize equipment performance and reduce maintenance costs.
  - **Honeywell (HON):** Honeywell provides predictive maintenance solutions through its Connected Plant platform, offering real-time monitoring and analytics for industrial equipment.

#### Competitive Landscape and Market Dynamics

@@@ Market Consolidation Trends:
  - **Technology Integration:** Companies are increasingly acquiring technology startups to enhance their digital capabilities and maintain competitive advantage.
  - **Partnership Strategies:** Strategic partnerships between traditional industrial companies and technology providers are becoming more common to accelerate innovation.

@@@ Investment Implications:
  - **High Growth Potential:** Industrial automation and smart manufacturing technologies offer significant growth opportunities for investors.
  - **M&A Activity:** Continued consolidation expected in industrial technology sectors, with focus on companies that can provide integrated solutions.

#### Actionable Insights for Bankers and Investors

@@@ For Bankers:
  - **Deal Opportunities:** Focus on companies with strong technology portfolios and market positioning in emerging industrial trends.
  - **Valuation Considerations:** Factor in technology synergies and growth potential when evaluating industrial M&A opportunities.

@@@ For Investors:
  - **Sector Focus:** Prioritize investments in companies that are leading digital transformation in their respective industrial sectors.
  - **Risk Management:** Consider regulatory and technological risks when evaluating industrial technology investments.

In summary, the Industrial sector is experiencing significant transformation driven by technological innovation and sustainability initiatives. Companies that successfully integrate these trends into their operations will likely emerge as leaders in the evolving industrial landscape.
"""


section6PromptIndustrial = """
6. Recommended Readings

For each deal mentioned in Section 1, provide ONE specific reading material and explain why it matters.

** Format for each deal:**
@@@ Deal Name: [Specific deal from Section 1]
- **Reading Material:** [Book/Article/Resource name]
- **Why This Matters:** [Clear explanation of how this reading helps understand the deal]

**Example:**
@@@ Deal Name: Boeing's Strategic Partnership
- **Reading Material:** "The Lean Enterprise" by James P. Womack
- **Why This Matters:** This book explains how industrial companies can optimize their operations and reduce waste, which is exactly what Boeing is trying to achieve through its strategic partnership. You'll learn how to evaluate operational synergies and understand why industrial companies focus on efficiency improvements.

Keep it simple and direct - one deal, one reading, one clear explanation of why it matters.


**Format:**
Use ### as start of sections
Use #### as start of subsections
Use **title:** as start of subsections
Use - ** as bullet points
Use @@@ to bold a line

IMPORTANT!
USE ONLY ONE FORMATTING PATTING PER LINE AND ONLY USE AT THE START OF A LINE!

**Follow the formatting of the Example Structure:**
### 6. Recommended Readings

@@@ Deal Name: General Electric's Acquisition of Aviation Technology  
- **Reading Material:** "The Machine That Changed the World" by James P. Womack  
- **Why This Matters:** This book provides insights into lean manufacturing principles and operational excellence, which are crucial for understanding GE's strategic rationale behind acquiring aviation technology assets. It explains how industrial companies leverage operational synergies to drive efficiency and competitive advantage.

@@@ Deal Name: Caterpillar's Strategic Partnership in Construction Technology  
- **Reading Material:** "The Fourth Industrial Revolution" by Klaus Schwab  
- **Why This Matters:** This reading delves into the transformation of industrial sectors through digital technologies, particularly relevant for understanding Caterpillar's $2.1 billion partnership (CAT) as a strategic move to enhance its autonomous equipment capabilities and compete with rivals like Deere (DE) and Komatsu.

@@@ Deal Name: Boeing's Acquisition of Aerospace Assets  
- **Reading Material:** "Skunk Works" by Ben Rich  
- **Why This Matters:** This book outlines methodologies for aerospace innovation and project management, which is relevant for understanding Boeing's $8.45 billion acquisition (BA) of aerospace assets. It highlights the importance of integrating advanced technologies and maintaining competitive advantage in the aerospace sector.

@@@ Deal Name: Tesla's Manufacturing Expansion  
- **Reading Material:** "The Innovator's Dilemma" by Clayton Christensen  
- **Why This Matters:** This book provides a detailed analysis of disruptive innovation in manufacturing, including how companies like Tesla (TSLA) are transforming traditional automotive manufacturing through automation and sustainable technologies.

@@@ Deal Name: 3M's Acquisition of Industrial Automation  
- **Reading Material:** "The Lean Startup" by Eric Ries  
- **Why This Matters:** This resource offers an in-depth look at how companies can innovate and adapt to changing market conditions, which is essential for analyzing 3M's $6.9 billion acquisition (MMM) of industrial automation assets. It explains how diversified industrial companies can leverage technology to enhance their competitive positioning.

@@@ Deal Name: Deere's Acquisition of Agricultural Technology  
- **Reading Material:** "Precision Agriculture" by John Stafford  
- **Why This Matters:** This reading discusses the growth of precision agriculture and autonomous farming technologies, which are central to Deere's $2.1 billion acquisition (DE) of agricultural technology assets. It highlights how this deal positions Deere to compete in the smart farming space against competitors like AGCO and CNH Industrial.
"""


section7PromptIndustrial = """
7. MACROECONOMIC UPDATE

Summarize the key data points and insights from the provided macroeconomic content (podcasts, market commentary, etc.) in a clear, structured format.

**Summarization Structure:**
- **Key Data Points:** [List specific numbers, rates, percentages mentioned]
- **Main Insights:** [Bullet points of key takeaways from the content]
- **Market Commentary:** [Direct quotes or paraphrased insights from commentators]
- **Industrial Sector Relevance:** [Brief connection to how this affects industrial markets]

**Format:**
Use ### as start of sections
Use #### as start of subsections
Use **title:** as start of subsections
Use - ** as bullet points
Use @@@ to bold a line

IMPORTANT!
USE ONLY ONE FORMATTING PATTING PER LINE AND ONLY USE AT THE START OF A LINE!

**Example Structure:**
### 7. MACROECONOMIC UPDATE

@@@ Key Data Points:
- Fed Funds Rate: 5.25-5.50%
- CPI YoY: 3.2%
- Unemployment Rate: 3.8%
- Industrial Production Index: 102.4
- USD Index: 105.2

@@@ Main Insights:
- Fed signals pause in rate hikes
- Inflation cooling but core remains elevated
- Labor market showing signs of moderation
- Industrial production supported by infrastructure spending

@@@ Market Commentary:
- "The Fed is likely to hold rates steady through year-end" - Morgan Stanley
- "Industrial demand remains resilient despite economic headwinds" - Goldman Sachs

@@@ Industrial Sector Relevance:
- Higher rates impact industrial project financing
- Strong dollar weighs on export competitiveness
- Labor market strength supports industrial demand
- Infrastructure spending benefits construction and manufacturing
"""


section1PromptConsumer = """
1. RECENT Consumer & Retail M&A ACTIVITY

=======================================================================================================================================================================================================
qualification_rules (softened):
  Qualify an item for DEAL TIER (Tier 1) if BOTH of these buckets are satisfied:

  A) action_signal (need ≥1):
     - acquisition / acquire / acquiring / bought / buyout
     - merger / merge / agreed to merge / merger-of-equals / reverse merger
     - take-private / privatization
     - carve-out / divestiture / spin-off
     - IPO or direct listing verbs: files prospectus/DRHP/F-1/S-1, prices IPO, lists
     - strategic equity: takes X% stake, majority stake, joint venture, board rights, exclusivity

  B) materiality_signal (need ≥1):
     - a hard number tied to the transaction (deal value, stake %, valuation, offer size/shares, multiple)
     - OR explicit control language (majority, control, board seats/rights, exclusivity)

  Notes:
    - Missing detailed multiples or segment tables does NOT disqualify a deal; use "N/A" where data isn’t in context.
    - Routine wording like “plans/consider/explore” alone is NOT an action_signal unless paired with a filing/pricing/listing or an explicit control/majority/board-rights statement.

do_not_include (minimal but firm):
  - routine fund/ETF/13F trading (increased/trimmed/holds) unless framed as strategic stake that meets materiality_signal
  - earnings, product launches, or partnerships with no equity/control
  - vague “planning to IPO next year” with no filing/pricing/listing/control

tiering_policy:
  - First, select up to TWO items that pass DEAL TIER (Tier 1) with the richest disclosed data.
  - If fewer than TWO exist, fill remaining slots with MARKET-REP TIER (Tier 2):
      * Items that best capture current Consumer & Retail market conditions (pricing power, demand trends, traffic, basket size, promotional intensity, retail sales, confidence, policy impacts), and have concrete metrics (comps %, revenue growth %, margins %, traffic %, ASP).
      * Exclude fund trading and rumor-only pieces.
  - If zero items exist for BOTH tiers, output exactly:
    @@@ Today is a peaceful day, nothing big happened in the Consumer space.

data_missing_policy:
  - If specific multiples/segment tables are not present in the provided context/company block, skip and proceed. Do not exclude otherwise-qualifying deals.

Choose max 2 with highest materiality (deal size, control, market impact) and richest disclosed data.

If only 1 qualifies, include just 1.

If 0 qualify, output the following line EXACTLY: "@@@ Today is a peaceful day, nothing big happened in the Consumer space."
=======================================================================================================================================================================================================

CRITICAL: Focus on ONLY 2 of the most significant M&A deals, IPOs, or major transactions from the provided news items. Prioritize deals with the most detailed financial information and market impact.
ONLY SELECT NEWS WHERE A corporate transaction is specifically reported: M&A/merger, acquisition/take-private, carve-out/divestiture/spin-off, IPO/direct listing, joint venture/strategic partnership with equity, or a significant strategic stake (≥10% ownership or ≥USD 100M consideration, or board/control rights). Exclude routine portfolio trades by funds (e.g., “asset manager purchased shares”) unless they meet the threshold above.
If there is only one recent deal, then just do one deal.
For each of the 2 selected deals, ONLY provide analysis with the following structured information:

**Deal Analysis Structure:**
- **Deal Size:** [USD amount - provide specific numbers when available, estimate based on comparable deals if not specified]
- **Deal Size Category:** [Define deal size: Small cap (<$2B), Mid cap ($2B-$10B), Large cap (>$10B)]
- [Classify today's deal's nature as either Horizontal/Vertical/Tuck-in&Bolt on/Carve out/Conglomerate]
- **Valuation Multiples:** [Detailed analysis of EV/EBITDA, P/E, or other relevant multiples with industry context and comparison to peers]
- **Companies:** [Buyer] acquiring [Target] - include company descriptions and market positions
- **Date Announced:** [Specific date if mentioned, or approximate timeline]
- **Strategic Rationale:** [In-depth analysis of the strategic logic, including market positioning, synergies, competitive advantages, and long-term strategic vision]
- **Risk Analysis:** [Comprehensive risk assessment including integration risks, regulatory challenges, market risks, execution risks, and potential value destruction scenarios]

**Key Financials Analysis:** 
For each deal, provide comprehensive financial analysis including:
- **Revenue Breakdown:** Revenue breakdown based on business segments (e.g., Apple revenue by products: iPhone, Mac, Services, etc. rather than by regions) + percentage share + year-over-year growth for 3 years (Only include if applicable, if no data is available, discard)
- **Profitability Ratios:** EBITDA/revenue, Net Income/revenue ratios (Only include if applicable, if no data is available, discard)
- **Leverage Analysis:** Debt-to-Equity ratio and analysis of long-term vs short-term debt structure
- **Asset Operating Efficiency:** Working capital analysis, inventory turnover days, accounts receivable turnover days, and accounts payable turnover days
- **Valuation Context:** Combine these financial metrics with P/E and EV/EBITDA multiples for comprehensive analysis

**Profitability Metrics:**  (Only include if applicable, if no data is available, discard)
-EBITDA, EBIT, Net Income and year-over-year growth for 3 years (WRITE THIS IN THE FORM OF A TABLE, see formatting guidelines below)

**Purpose:** Use this financial analysis to roughly assess performance and business growth/decline trends, then infer the strategic rationale (e.g., whether the acquisition target provides new businesses/technologies/brand influence that the parent company lacks)

**Analysis Requirements:**
- Provide specific valuation multiples with industry benchmarks and peer comparisons
- Include detailed rationale with strategic context and market implications
- Conduct thorough risk analysis with specific risk factors and mitigation strategies
- Use concrete data points and financial metrics wherever possible
- Focus on deals with the most significant TMT sector impact and detailed financial information
- Specify capital structure

------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Formatting guidelines:
Use ### as start of sections
Use #### as start of subsections
Use **title:** as start of subsections
Use - ** as bullet points
Use @@@ to bold a line

To draw tables, use the following format:
| A | B |
| --- | --- |
| a1 | b1 |
| a2 | b2 |


IMPORTANT!
USE ONLY ONE FORMATTING PATTING PER LINE AND ONLY USE AT THE START OF A LINE!


For instance: 
- **Apple Inc. (AAPL)**: Mandated to evaluate acquisitions in the AI space, with a focus on startups that can enhance its product offerings. The timeline for this initiative is projected for Q2 2026, as Apple aims to strengthen its competitive edge in AI.
This is fine
But never do this:
- **Indiegogo Acquisition by Gamefound**: This transaction is progressing, with regulatory approvals anticipated by **Q4 2025**. The integration aims to combine Indiegogo's **38 million users** with Gamefound's technology, thereby enhancing their market position in the crowdfunding space.
Instead of "**Q4 2025**", just do Q4 2025. The same applies to every other line pats


When adding links, use this EXACT format: **Link title** ([Link](https://linkURL))
example: **JPMorgan Reports Increased M&A Activity in TMT Sector** ([Link](https://www.businessinsider.com/merger-acquisition-trends-1h-hreport-sponsors-volumes-anu-aiyengar-jpmorgan-2025-7))
MAKE SURE THE LINKS MATCH THEIR TITLES
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


**Example Structure:**
### 1. RECENT Consumer & Retail M&A ACTIVITY

**Deal 1: [Company Name] Acquisition**
**Deal Title with Link** ([Link](URL))
- **Deal Size:** $X billion (or specific amount)
- **Valuation Multiples:** EV/EBITDA of X.Xx (vs industry average of X.Xx), P/E of X.Xx
- **Companies:** [Detailed company descriptions and market positions]
- **Date Announced:** [Specific date]
- **Strategic Rationale:** [Comprehensive strategic analysis with market context]
- **Risk Analysis:** [Detailed risk assessment with specific factors]
- **Key Financials Analysis:** [Revenue breakdown by business, profitability metrics, leverage analysis, asset efficiency, and valuation context]

**Deal 2: [Company Name] Acquisition** |(Include only if available, if not, just do nothing)
[Same detailed structure as Deal 1]

Focus on quality over quantity - provide data-driven analysis of deals rather than superficial coverage of many deals.

DO NOT INCLUDE a Recommended Readings
"""


section2PromptConsumer = """
2. MARKET DYNAMICS & SENTIMENT

(Provide a multi-paragraph, in-depth analysis)
- Overall Consumer & Retail sector sentiment, with breakdowns by subsector, geography, and deal type
- Key market drivers and headwinds, with supporting data
- Subsector performance analysis (e.g., Consumer Staples, Consumer Durables, Consumer Discretionary, E-commerce, Luxury Goods, Food & Beverage)
- Trading multiples trends, with specific numbers and comparisons
- Notable investor/analyst reactions, with quotes or examples
- Actionable insights for bankers and investors

**Format:**
Use ### as start of sections
Use #### as start of subsections
Use **title:** as start of subsections
Use - ** as bullet points
Use @@@ to bold a line

IMPORTANT!
USE ONLY ONE FORMATTING PATTING PER LINE AND ONLY USE AT THE START OF A LINE!

For instance: 
- **Procter & Gamble (PG)**: Mandated to evaluate acquisitions in the consumer staples space, with a focus on brands that can enhance its product portfolio. The timeline for this initiative is projected for Q2 2026, as P&G aims to strengthen its competitive edge in sustainable consumer products.
This is fine
But NEVER EVER do it this:
- Nike Acquisition by Adidas : This transaction is progressing, with regulatory approvals anticipated by **Q4 2025**. The integration aims to combine Nike's **athletic apparel assets** with Adidas's technology, thereby enhancing their market position in the consumer space.
Instead of "**Q4 2025**", just do Q4 2025. The same applies to every other line pats. DO NOT PUT LINE PAT IN THE MIDDLE OF LINES

DO NOT PUT LINKS IN THIS SECTION

**Example Structure**
### 2. MARKET DYNAMICS & SENTIMENT

The Consumer & Retail sector is currently experiencing a mixed sentiment, characterized by cautious optimism amid ongoing economic uncertainty and evolving consumer preferences. The overall sentiment is influenced by various factors, including inflation, supply chain dynamics, and shifting consumer behavior patterns.

@@@ Subsector Breakdown:
  - **Consumer Staples:** The consumer staples subsector remains resilient, driven by essential product demand and pricing power. For instance, Procter & Gamble's utilization of AI for demand forecasting reflects a growing trend where companies leverage technology to enhance supply chain efficiency and customer experience.
  - **Consumer Durables:** The consumer durables subsector is witnessing a transformation as companies like Tesla enhance product capabilities through new digital features. However, traditional manufacturers face challenges from economic headwinds and supply chain disruptions.
  - **Consumer Discretionary:** The consumer discretionary sector is innovating with direct-to-consumer models, as demonstrated by Nike's introduction of personalized shopping experiences, which aims to improve customer engagement and brand loyalty.
  - **E-commerce:** The e-commerce space continues to thrive, with companies exploring new business models and partnerships, such as Amazon's acquisition of retail technology assets, which aims to integrate omnichannel solutions.
  - **Luxury Goods:** The luxury goods subsectors are particularly resilient, with companies racing to implement sustainable practices across various markets, including fashion, where brands are challenging traditional retail models by promising enhanced customer experiences.
  - **Food & Beverage:** The food and beverage sector is experiencing growth through health-focused products and sustainable packaging, with companies investing in plant-based alternatives and eco-friendly solutions.

#### Key Market Drivers and Headwinds

 @@@ Drivers:
  - **Digital Transformation:** Continuous innovation in e-commerce, omnichannel retail, and personalized customer experiences is driving growth across consumer sectors. For example, Shopify's platform technology is expected to enhance the performance of retail applications reliant on seamless customer interactions.
  - **Increased Investment:** Venture capital and private equity investments remain strong, particularly in direct-to-consumer brands and retail technology, as investors seek to capitalize on emerging consumer trends.

 @@@ Headwinds:
  - **Economic Uncertainty:** Consumer spending patterns are being impacted by inflation and economic uncertainty, which may affect discretionary purchases and overall retail performance.
  - **Supply Chain Disruptions:** Ongoing supply chain challenges continue to impact product availability and pricing across consumer sectors.

#### Trading Multiples and Performance Analysis

@@@ Current Trading Multiples:
  - **Consumer Staples:** EV/EBITDA of 15.2x (vs 5-year average of 14.8x), P/E of 22.1x
  - **Consumer Durables:** EV/EBITDA of 11.8x (vs 5-year average of 10.9x), P/E of 18.7x
  - **Consumer Discretionary:** EV/EBITDA of 13.4x (vs 5-year average of 12.6x), P/E of 20.3x
  - **E-commerce:** EV/EBITDA of 18.9x (vs 5-year average of 16.2x), P/E of 28.5x

#### Notable Investor/Analyst Reactions

- Analysts are generally optimistic about the long-term prospects of the Consumer & Retail sector, citing digital transformation as a key driver of growth. For instance, an analyst at a leading investment bank commented, "The integration of AI across retail and consumer applications is not just a trend; it's a fundamental shift that will redefine customer experience and operational efficiency."

#### Actionable Insights for Bankers and Investors

- **Focus on High-Growth Areas:** Investors should prioritize sectors with strong growth potential, such as e-commerce and direct-to-consumer brands, while being cautious with traditional retail investments.
- **Monitor Consumer Trends:** Staying informed about changing consumer preferences is crucial for assessing risks in consumer investments.
- **Leverage Technology Partnerships:** Companies should explore strategic partnerships and acquisitions to enhance their digital capabilities and market positioning.
- **Evaluate Valuation Metrics:** Investors should consider current trading multiples and sector performance when making investment decisions, particularly in high-growth subsectors.

In summary, the Consumer & Retail sector is navigating a complex landscape characterized by both opportunities and challenges. By focusing on digital transformation and understanding consumer dynamics, investors and bankers can position themselves for success in this evolving environment.
"""


section3PromptConsumer = """
3. BANKING PIPELINE

(Provide a multi-paragraph, in-depth analysis)
- Deal Pipeline (Transaction Pipeline):
  * Live deals: Transactions currently in progress (M&A in due diligence, upcoming IPOs), with details and expected timing
  * Mandated deals: Transactions with secured mandates but not yet fully launched, with client names and deal types if possible
  * Pitching-stage deals: Active pitches and client discussions for potential mandates, with sector/client focus
- Pipeline tracking metrics:
  * Expected revenue/fees from active pipeline, with breakdowns
  * Timing projections (Q2 close, Q4 IPO, etc.)
  * Workload allocation and capacity analysis (e.g., analyst/associate bandwidth)
  * Forecasting and strategic planning implications
- Notable pipeline developments and competitive landscape, with examples
- Actionable insights for team management and business development

**Format:**
Use ### as start of sections
Use #### as start of subsections
Use **title:** as start of subsections
Use - ** as bullet points
Use @@@ to bold a line

IMPORTANT!
USE ONLY ONE FORMATTING PATTING PER LINE AND ONLY USE AT THE START OF A LINE!

For instance: 
- **Procter & Gamble (PG)**: Mandated to evaluate acquisitions in the consumer staples space, with a focus on brands that can enhance its product portfolio. The timeline for this initiative is projected for Q2 2026, as P&G aims to strengthen its competitive edge in sustainable consumer products.
This is fine
But never do this:
- Nike Acquisition by Adidas : This transaction is progressing, with regulatory approvals anticipated by **Q4 2025**. The integration aims to combine Nike's **athletic apparel assets** with Adidas's technology, thereby enhancing their market position in the consumer space.
Instead of "**Q4 2025**", just do Q4 2025. The same applies to every other line pats

DO NOT INCLUDE a Recommended Readings

**Follow the formatting of the Example Structure:**
### 3. BANKING PIPELINE

The Consumer & Retail sector banking pipeline demonstrates robust activity across multiple subsectors, with significant opportunities in e-commerce, direct-to-consumer brands, and sustainable consumer products. The current pipeline reflects a strategic focus on digital transformation and brand portfolio optimization.

#### Deal Pipeline Overview

@@@ Live Deals:
  - **Amazon Strategic Partnership**: Currently in due diligence phase for a major e-commerce technology acquisition, expected to close in Q3 2025. The deal involves integrating advanced personalization capabilities to enhance customer experience.
  - **Nike Digital Transformation**: Active discussions for acquiring retail technology assets to support omnichannel expansion, with regulatory approvals anticipated by Q4 2025.

@@@ Mandated Deals:
  - **Procter & Gamble (PG)**: Mandated to evaluate acquisitions in the consumer staples space, with a focus on brands that can enhance its product portfolio. The timeline for this initiative is projected for Q2 2026, as P&G aims to strengthen its competitive edge in sustainable consumer products.
  - **LVMH (LVMUY)**: Engaged to explore strategic partnerships in luxury retail technology, targeting companies that can enhance its digital customer experience capabilities. The mandate includes evaluating both minority investments and full acquisitions.

@@@ Pitching-Stage Deals:
  - **Tesla (TSLA)**: Active discussions for retail and service center expansion acquisitions, with focus on enhancing customer experience and service capabilities.
  - **Coca-Cola (KO)**: Exploring opportunities in beverage technology and sustainable packaging solutions to enhance its product innovation capabilities.

#### Pipeline Tracking Metrics

@@@ Expected Revenue/Fees: The active pipeline is projected to generate approximately $28 million in fees, broken down as follows:
  - **Live Deals**: $12 million
  - **Mandated Deals**: $9 million
  - **Pitching-Stage Deals**: $7 million

@@@ Timing Projections:
  - **Q3 2025**: Expected close for Amazon strategic partnership.
  - **Q4 2025**: Anticipated completion of Nike digital transformation.
  - **Q2 2026**: Launch of P&G's consumer staples acquisition initiatives.

- **Workload Allocation and Capacity Analysis**: 
  - Current analyst and associate bandwidth is at 80%, with a need for additional resources as the pipeline expands. It is recommended to onboard two additional analysts to manage the increased workload effectively.

- **Forecasting and Strategic Planning Implications**: The pipeline indicates a strong demand for advisory services in e-commerce and direct-to-consumer sectors. Strategic planning should focus on enhancing capabilities in these areas to capitalize on emerging opportunities.

#### Notable Pipeline Developments and Competitive Landscape

- The competitive landscape is intensifying, particularly in the e-commerce sector, where companies like Amazon and Shopify are vying for leadership in retail technology. The recent focus on sustainable consumer products could alter the regulatory environment, impacting deal structures and valuations.
  
- Additionally, the rise of direct-to-consumer brands indicates a growing market for digital-first retail solutions, which could lead to new advisory opportunities.

#### Actionable Insights for Team Management and Business Development

- **Resource Allocation**: Given the anticipated increase in deal flow, it is crucial to allocate resources effectively. Hiring additional analysts will ensure that the team can manage the workload without compromising service quality.
  
- **Sector Focus**: Prioritize business development efforts in high-growth sectors such as e-commerce and direct-to-consumer brands, where demand for advisory services is expected to surge. This focus will position the firm as a leader in these emerging markets.

- **Client Engagement**: Maintain proactive communication with clients in the pipeline to ensure alignment on expectations and timelines. Regular updates will help build trust and facilitate smoother transaction processes.

In summary, the banking pipeline is robust, with significant opportunities across various Consumer & Retail subsectors. By strategically managing resources and focusing on high-potential areas, the team can maximize its impact and drive successful outcomes for clients.
"""


section4PromptConsumer = """
4. STAKEHOLDER IMPACT & FORWARD-LOOKING ANALYSIS

(Provide a multi-paragraph, in-depth analysis)
- Deal-specific impacts on:
  * Shareholders (value creation/dilution, with scenario analysis and numbers)
  * Employees (synergies, restructuring, retention, with examples)
  * Competitors (market positioning, with specific competitor moves)
  * Customers (product/service implications, with case studies)
- Market reaction and analyst commentary, with quotes or data
- Expected market reaction, with scenario analysis
- Potential counter-bids or competing offers, with likelihood assessment
- Similar deals likely to follow, with sector consolidation predictions
- Key risks and mitigants, with detailed breakdowns
- Actionable insights for clients and bankers

**Format:**
Use ### as start of sections
Use #### as start of subsections
Use **title:** as start of subsections
Use - ** as bullet points
Use @@@ to bold a line

IMPORTANT!
USE ONLY ONE FORMATTING PATTING PER LINE AND ONLY USE AT THE START OF A LINE!

For instance: 
- **Procter & Gamble (PG)**: Mandated to evaluate acquisitions in the consumer staples space, with a focus on brands that can enhance its product portfolio. The timeline for this initiative is projected for Q2 2026, as P&G aims to strengthen its competitive edge in sustainable consumer products.
This is fine
But never do this:
- Nike Acquisition by Adidas : This transaction is progressing, with regulatory approvals anticipated by **Q4 2025**. The integration aims to combine Nike's **athletic apparel assets** with Adidas's technology, thereby enhancing their market position in the consumer space.
Instead of "**Q4 2025**", just do Q4 2025. The same applies to every other line pats

DO NOT INCLUDE a Recommended Readings

**Follow the formatting of the Example Structure:**
### 4. STAKEHOLDER IMPACT & FORWARD-LOOKING ANALYSIS

The Consumer & Retail sector M&A landscape presents significant implications for various stakeholders, with particular focus on brand portfolio optimization and digital transformation. This analysis examines the broader impact of recent transactions and provides forward-looking insights for market participants.

#### Deal-Specific Stakeholder Impacts

@@@ Shareholder Impact:
  - **Value Creation Potential**: Recent consumer & retail acquisitions have demonstrated average shareholder value creation of 12-18% over 12-month periods, driven primarily by brand synergies and market expansion opportunities.
  - **Dilution Concerns**: While some deals involve equity components, the strategic rationale typically outweighs dilution concerns, with most transactions showing positive total shareholder return within 15 months.

@@@ Employee Impact:
  - **Synergy Realization**: Consumer & retail M&A typically results in 6-10% workforce optimization through operational synergies, with focus on eliminating redundant functions while preserving brand management capabilities.
  - **Retention Strategies**: Key talent retention rates average 80% in successful consumer integrations, supported by retention bonuses and career development opportunities.

@@@ Competitor Impact:
  - **Market Positioning**: Major consumer & retail acquisitions often trigger competitive responses, with rivals typically announcing strategic initiatives within 4-8 months to maintain market position.
  - **Brand Competition**: The focus on direct-to-consumer channels and digital transformation has intensified competition, with companies investing heavily in brand building and customer acquisition.

@@@ Customer Impact:
  - **Product Innovation**: Customers benefit from enhanced product portfolios and improved customer experiences, with typical improvements in product quality and service delivery.
  - **Pricing Dynamics**: While some consolidation may lead to pricing power, the competitive nature of consumer markets generally maintains customer value propositions.

#### Market Reaction and Analyst Commentary

@@@ Current Market Sentiment:
  - "Consumer & retail M&A activity reflects a strategic shift towards digital transformation and brand portfolio optimization" - Goldman Sachs Consumer Research
  - "The focus on direct-to-consumer channels and sustainable products is driving premium valuations in the sector" - Morgan Stanley

@@@ Expected Market Reaction:
  - **Bullish Scenario**: Continued M&A activity could drive sector re-rating, with potential 8-12% upside in consumer multiples.
  - **Bearish Scenario**: Economic headwinds or consumer spending weakness could dampen deal activity, leading to 3-6% multiple compression.

#### Potential Counter-Bids and Competing Offers

@@@ Likelihood Assessment:
  - **High Probability (60-70%)**: Strategic acquisitions in luxury goods and premium brands, where brand value often triggers competing offers.
  - **Medium Probability (35-45%)**: E-commerce and retail technology deals, where digital capabilities are highly valued.
  - **Low Probability (20-30%)**: Consumer staples deals, where integration complexity typically deters competing offers.

#### Similar Deals and Sector Consolidation Predictions

@@@ Expected Consolidation Trends:
  - **E-commerce**: Continued consolidation expected, with focus on technology integration and customer acquisition optimization.
  - **Direct-to-Consumer**: Emerging brands likely to be acquired by larger players seeking to expand their digital presence.
  - **Sustainable Products**: Companies with strong ESG credentials expected to be key acquisition targets.

#### Key Risks and Mitigants

@@@ Integration Risks:
  - **Brand Management**: Consumer brands require careful integration planning, with typical 12-18 month timelines for full brand portfolio optimization.
  - **Cultural Alignment**: Consumer companies often have distinct brand cultures that require focused change management programs.

@@@ Market Risks:
  - **Consumer Preferences**: Rapid changes in consumer preferences can impact brand value and market positioning.
  - **Economic Sensitivity**: Consumer spending patterns are sensitive to economic conditions and inflation.

#### Actionable Insights for Clients and Bankers

@@@ For Clients:
  - **Strategic Planning**: Focus on brand-driven acquisitions that enhance market positioning and customer reach.
  - **Due Diligence**: Prioritize brand value assessment and customer analytics to ensure successful integration outcomes.

@@@ For Bankers:
  - **Deal Structuring**: Consider brand preservation strategies and customer retention programs to manage integration risk.
  - **Valuation Approach**: Factor in brand synergies and customer lifetime value when developing valuation models.

In summary, the Consumer & Retail sector presents significant opportunities for value creation through strategic M&A, with particular focus on brand optimization and digital transformation. Success requires careful planning, execution, and stakeholder management to realize the full potential of these transactions.
"""

section5PromptConsumer = """
5. CONSUMER & RETAIL TRENDS

(Provide a multi-paragraph, in-depth analysis)
- Identify key emerging consumer & retail trends from the news (e.g., Direct-to-Consumer, Sustainable Products, Personalization, Omnichannel Retail, Social Commerce, Subscription Models, etc.)
- For each identified trend:
  * Provide a detailed explanation of the trend, its market significance, and growth trajectory
  * List specific companies from the news that are involved in this trend
  * For each company, provide a brief description of their activities and strategic positioning within the trend
  * Analyze the competitive landscape and market dynamics for each trend
  * Discuss potential M&A opportunities and investment implications
- Focus on trends that have significant market impact and deal-making potential
- Include examples, use cases, and market data where available
- Provide actionable insights for bankers and investors regarding trend-driven opportunities
- Refrain from writing overly lengthy reports, and MAKE SURE section can be completed within the token limit

**Format:**
Use ### as start of sections
Use #### as start of subsections
Use **title:** as start of subsections
Use - ** as bullet points
Use @@@ to bold a line

IMPORTANT!
USE ONLY ONE FORMATTING PATTING PER LINE AND ONLY USE AT THE START OF A LINE!

For instance: 
- **Procter & Gamble (PG)**: Mandated to evaluate acquisitions in the consumer staples space, with a focus on brands that can enhance its product portfolio. The timeline for this initiative is projected for Q2 2026, as P&G aims to strengthen its competitive edge in sustainable consumer products.
This is fine
But never do this:
- Nike Acquisition by Adidas : This transaction is progressing, with regulatory approvals anticipated by **Q4 2025**. The integration aims to combine Nike's **athletic apparel assets** with Adidas's technology, thereby enhancing their market position in the consumer space.
Instead of "**Q4 2025**", just do Q4 2025. The same applies to every other form of nested line pats

DO NOT INCLUDE a Recommended Readings

**Follow the formatting of the Example Structure:**
### 5. CONSUMER & RETAIL TRENDS

The consumer & retail landscape is rapidly evolving, with several key trends emerging that have significant market implications and deal-making potential. This analysis will focus on the following trends: Direct-to-Consumer, Sustainable Products, Personalization, Omnichannel Retail, Social Commerce, and Subscription Models. Each section will provide a detailed explanation of the trend, its market significance, key players, competitive dynamics, and potential M&A opportunities.

#### Direct-to-Consumer (DTC)

- **Trend Explanation:** Direct-to-consumer brands bypass traditional retail channels to sell directly to customers, enabling better control over brand experience and customer data. The global DTC market is projected to grow from $111.54 billion in 2020 to $174.98 billion by 2025, at a CAGR of 9.4%.
  
@@@ Key Companies:
  - **Warby Parker (WRBY):** Warby Parker is a pioneer in the DTC eyewear space, providing affordable, stylish glasses directly to consumers. The company has strategically positioned itself in the DTC market by investing heavily in customer experience and brand building.
  - **Allbirds (BIRD):** Allbirds is at the forefront of sustainable DTC footwear, known for its eco-friendly materials and direct customer relationships. The company has formed partnerships with major retailers while maintaining its DTC focus.

#### Sustainable Products

- **Trend Explanation:** Sustainable products focus on environmental responsibility, ethical sourcing, and circular economy principles. The global sustainable products market is expected to reach $150.0 billion by 2025, growing at a CAGR of 8.2%.

@@@ Key Companies:
  - **Patagonia:** Patagonia specializes in sustainable outdoor apparel and gear, with a focus on environmental activism and ethical manufacturing. The company's commitment to sustainability has become a key differentiator in the outdoor retail market.
  - **Unilever (UL):** Unilever provides comprehensive sustainable product solutions, including brands like Dove and Ben & Jerry's that focus on social and environmental responsibility.

#### Personalization

- **Trend Explanation:** Personalization uses data analytics and AI to create customized customer experiences, products, and marketing messages. The global personalization market is projected to grow from $2.0 billion in 2020 to $5.5 billion by 2025.

@@@ Key Companies:
  - **Stitch Fix (SFIX):** Stitch Fix uses data science and personal stylists to provide personalized clothing recommendations to customers. The company's approach combines human expertise with algorithmic recommendations.
  - **Amazon (AMZN):** Amazon provides comprehensive personalization solutions through its recommendation engine and Alexa platform, offering personalized shopping experiences across multiple product categories.

#### Omnichannel Retail

- **Trend Explanation:** Omnichannel retail provides seamless customer experiences across online and offline channels, integrating inventory, customer data, and service delivery. The global omnichannel retail market is expected to reach $11.1 billion by 2026.

@@@ Key Companies:
  - **Nike (NKE):** Nike is a leader in omnichannel retail, providing integrated experiences across digital platforms, physical stores, and mobile apps. The company's approach combines digital innovation with physical retail presence.
  - **Target (TGT):** Target provides comprehensive omnichannel solutions, including same-day delivery, in-store pickup, and integrated customer experiences across all touchpoints.

#### Social Commerce

- **Trend Explanation:** Social commerce enables shopping directly through social media platforms, combining social interaction with e-commerce functionality. The global social commerce market is projected to grow from $492 billion in 2021 to $1.2 trillion by 2025.

@@@ Key Companies:
  - **Shopify (SHOP):** Shopify provides comprehensive social commerce solutions, enabling merchants to sell directly through social media platforms and integrate with various social channels.
  - **Meta (META):** Meta offers social commerce capabilities through Facebook and Instagram, allowing businesses to create shoppable posts and integrated shopping experiences.

#### Subscription Models

- **Trend Explanation:** Subscription models provide recurring revenue through regular product or service delivery, creating predictable customer relationships and revenue streams. The global subscription economy is expected to reach $1.5 trillion by 2025.

@@@ Key Companies:
  - **Netflix (NFLX):** Netflix is a pioneer in subscription-based entertainment, providing streaming services with personalized content recommendations and global reach.
  - **Dollar Shave Club:** Dollar Shave Club revolutionized the subscription model for personal care products, providing convenient, cost-effective solutions for everyday items.

#### Competitive Landscape and Market Dynamics

@@@ Market Consolidation Trends:
  - **Technology Integration:** Companies are increasingly acquiring technology startups to enhance their digital capabilities and maintain competitive advantage.
  - **Brand Portfolio Optimization:** Strategic partnerships between traditional retailers and DTC brands are becoming more common to accelerate market reach.

@@@ Investment Implications:
  - **High Growth Potential:** Direct-to-consumer and social commerce technologies offer significant growth opportunities for investors.
  - **M&A Activity:** Continued consolidation expected in consumer technology sectors, with focus on companies that can provide integrated customer experiences.

#### Actionable Insights for Bankers and Investors

@@@ For Bankers:
  - **Deal Opportunities:** Focus on companies with strong brand portfolios and digital capabilities in emerging consumer trends.
  - **Valuation Considerations:** Factor in customer lifetime value and brand equity when evaluating consumer M&A opportunities.

@@@ For Investors:
  - **Sector Focus:** Prioritize investments in companies that are leading digital transformation in their respective consumer sectors.
  - **Risk Management:** Consider consumer preference shifts and economic sensitivity when evaluating consumer investments.

In summary, the Consumer & Retail sector is experiencing significant transformation driven by digital innovation and changing consumer preferences. Companies that successfully integrate these trends into their operations will likely emerge as leaders in the evolving consumer landscape.
"""

section6PromptConsumer = """
6. Recommended Readings

For each deal mentioned in Section 1, provide ONE specific reading material and explain why it matters.

** Format for each deal:**
@@@ Deal Name: [Specific deal from Section 1]
- **Reading Material:** [Book/Article/Resource name]
- **Why This Matters:** [Clear explanation of how this reading helps understand the deal]

**Example:**
@@@ Deal Name: Procter & Gamble's Brand Acquisition
- **Reading Material:** "Building Strong Brands" by David Aaker
- **Why This Matters:** This book explains how consumer companies can build and manage brand portfolios, which is exactly what P&G is trying to achieve through its brand acquisition. You'll learn how to evaluate brand value and understand why consumer companies focus on brand portfolio optimization.

Keep it simple and direct - one deal, one reading, one clear explanation of why it matters.


**Format:**
Use ### as start of sections
Use #### as start of subsections
Use **title:** as start of subsections
Use - ** as bullet points
Use @@@ to bold a line

IMPORTANT!
USE ONLY ONE FORMATTING PATTING PER LINE AND ONLY USE AT THE START OF A LINE!

**Follow the formatting of the Example Structure:**
### 6. Recommended Readings

@@@ Deal Name: Procter & Gamble's Acquisition of Consumer Brand  
- **Reading Material:** "Building Strong Brands" by David Aaker  
- **Why This Matters:** This book provides insights into brand portfolio management and brand equity, which are crucial for understanding P&G's strategic rationale behind acquiring consumer brands. It explains how consumer companies leverage brand synergies to drive market share and customer loyalty.

@@@ Deal Name: Nike's Strategic Partnership in Digital Retail  
- **Reading Material:** "The Retail Revolution" by Mark Pilkington  
- **Why This Matters:** This reading delves into the transformation of retail through digital technologies, particularly relevant for understanding Nike's $2.1 billion partnership (NKE) as a strategic move to enhance its omnichannel capabilities and compete with rivals like Adidas and Under Armour.

@@@ Deal Name: Amazon's Acquisition of E-commerce Technology  
- **Reading Material:** "The Everything Store" by Brad Stone  
- **Why This Matters:** This book outlines methodologies for e-commerce innovation and customer experience optimization, which is relevant for understanding Amazon's $8.45 billion acquisition (AMZN) of e-commerce technology. It highlights the importance of integrating advanced technologies and maintaining competitive advantage in online retail.

@@@ Deal Name: Tesla's Retail Expansion  
- **Reading Material:** "The Lean Startup" by Eric Ries  
- **Why This Matters:** This book provides a detailed analysis of disruptive innovation in retail and service delivery, including how companies like Tesla (TSLA) are transforming traditional automotive retail through direct-to-consumer models and digital experiences.

@@@ Deal Name: LVMH's Acquisition of Luxury Brand  
- **Reading Material:** "Luxury Brand Management" by Michel Chevalier  
- **Why This Matters:** This resource offers an in-depth look at luxury brand management and customer experience, which is essential for analyzing LVMH's $6.9 billion acquisition (LVMUY) of luxury brand assets. It explains how luxury companies can leverage brand heritage and customer relationships to enhance their market positioning.

@@@ Deal Name: Coca-Cola's Acquisition of Beverage Technology  
- **Reading Material:** "The Future of Food" by Evan Fraser  
- **Why This Matters:** This reading discusses the growth of sustainable beverages and health-focused products, which are central to Coca-Cola's $2.1 billion acquisition (KO) of beverage technology assets. It highlights how this deal positions Coca-Cola to compete in the health beverage space against competitors like PepsiCo and emerging health-focused brands.
"""


section7PromptConsumer = """
7. MACROECONOMIC UPDATE

Summarize the key data points and insights from the provided macroeconomic content (podcasts, market commentary, etc.) in a clear, structured format.

**Summarization Structure:**
- **Key Data Points:** [List specific numbers, rates, percentages mentioned]
- **Main Insights:** [Bullet points of key takeaways from the content]
- **Market Commentary:** [Direct quotes or paraphrased insights from commentators]
- **Consumer & Retail Sector Relevance:** [Brief connection to how this affects consumer markets]

**Format:**
Use ### as start of sections
Use #### as start of subsections
Use **title:** as start of subsections
Use - ** as bullet points
Use @@@ to bold a line

IMPORTANT!
USE ONLY ONE FORMATTING PATTING PER LINE AND ONLY USE AT THE START OF A LINE!

**Example Structure:**
### 7. MACROECONOMIC UPDATE

@@@ Key Data Points:
- Fed Funds Rate: 5.25-5.50%
- CPI YoY: 3.2%
- Unemployment Rate: 3.8%
- Consumer Confidence Index: 102.3
- Retail Sales MoM: 0.7%

@@@ Main Insights:
- Fed signals pause in rate hikes
- Inflation cooling but core remains elevated
- Labor market showing signs of moderation
- Consumer spending supported by strong employment

@@@ Market Commentary:
- "The Fed is likely to hold rates steady through year-end" - Morgan Stanley
- "Consumer spending remains resilient despite economic headwinds" - Goldman Sachs

@@@ Consumer & Retail Sector Relevance:
- Higher rates impact consumer borrowing and spending
- Strong employment supports consumer confidence
- Inflation affects consumer purchasing power
- Supply chain stability benefits retail operations
"""

#this matrix stores necessary information needed to issue api calls, compositions are as follows
#[section_specific_prompt, context_or_materials, max_tokens]
TMT_prompt = [
    [section1Prompt, None, 800],
    [section2Prompt, None, 1800],
    [section3Prompt, None, 1500],
    [section4Prompt, None, 1200],
    [section5Prompt, None, 1000],
    [section6Prompt, None, 600],
    [section7Prompt, None, 500]
]


Energy_prompt = [
    [section1PromptEnergy, None, 800],
    [section2PromptEnergy, None, 1800],
    [section3PromptEnergy, None, 1500],
    [section4PromptEnergy, None, 1200],
    [section5PromptEnergy, None, 1200],
    [section6PromptEnergy, None, 600],
    [section7PromptEnergy, None, 500]
]


Healthcare_prompt = [
    [section1PromptHealthcare, None, 800],
    [section2PromptHealthcare, None, 1800],
    [section3PromptHealthcare, None, 1500],
    [section4PromptHealthcare, None, 1200],
    [section5PromptHealthcare, None, 1200],
    [section6PromptHealthcare, None, 600],
    [section7PromptHealthcare, None, 500]
]


Industrial_prompt = [
    [section1PromptIndustrial, None, 800],
    [section2PromptIndustrial, None, 1800],
    [section3PromptIndustrial, None, 1500],
    [section4PromptIndustrial, None, 1200],
    [section5PromptIndustrial, None, 1200],
    [section6PromptIndustrial, None, 600],
    [section7PromptIndustrial, None, 500]
]


Consumer_prompt = [
    [section1PromptConsumer, None, 800],
    [section2PromptConsumer, None, 1800],
    [section3PromptConsumer, None, 1500],
    [section4PromptConsumer, None, 1200],
    [section5PromptConsumer, None, 1200],
    [section6PromptConsumer, None, 600],
    [section7PromptConsumer, None, 500]
]
