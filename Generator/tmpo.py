from pdf_report import format_brief
from pathlib import Path

base_path = Path(__file__).resolve().parent.parent 
raw_dir = base_path / 'api' / "static" / "assets" / "raw"
json_path = base_path/ 'term_definitions.json'
brief_dir = base_path / 'api' / 'static' / 'assets' / 'briefs'

def clean_text_for_pdf(text):
    """Clean text of problematic Unicode characters for PDF generation"""
    if not text:
        return text
    
    # Replace problematic Unicode characters with ASCII equivalents
    replacements = {
        '\u20b9': 'Replaced_Rs',  # Indian Rupee
        '\u20ac': 'Replaced_EUR',  # Euro
        '\u00a3': 'Replaced_GBP',  # Pound Sterling
        '\u00a5': 'Replaced_JPY',  # Yen
        '\u20bf': 'Replaced_BTC',  # Bitcoin
        '\u201c': 'Replaced_"',    # Left double quotation mark
        '\u201d': 'Replaced_"',    # Right double quotation mark
        '\u2018': "Replaced_'",    # Left single quotation mark
        '\u2019': "Replaced_'",    # Right single quotation mark
        '\u2013': 'Replaced_the hyphen',    # En dash
        '\u2014': 'Replaced_--',   # Em dash
        '\u2022': 'Replaced_-',    # Bullet
        '\u2026': 'Replaced_...',  # Ellipsis
    }
    
    for unicode_char, replacement in replacements.items():
        text: str = text.replace(unicode_char, replacement)
    
    # More aggressive cleaning - convert to ASCII and handle errors gracefully
    try:
        # First try to encode as UTF-8 and decode as ASCII
        text = text.encode('utf-8').decode('ascii', errors='ignore')
    except:
        # If that fails, use a more aggressive approach
        text = ''.join(char for char in text if ord(char) < 128)
    
    return text.strip()



testText = """
### 1. RECENT TMT M&A ACTIVITY

**Deal 1:**
**JPMorgan Reports Increased M&A Activity in TMT Sector** ([Link](https://www.businessinsider.com/merger-acquisition-trends-1h-hreport-sponsors-volumes-anu-aiyengar-jpmorgan-2025-7))  
- **Deal Size:** Not specified in news  
- **Valuation Multiples:** Not specified in news  
- **Companies:** Not specified in news  
- **Date Announced:** Not specified in news  
- **Rationale:** JPMorgan noted a resurgence in M&A activity across various sectors, including Technology, Media, and Telecommunications (TMT), driven by favorable market conditions and strategic realignments.  
- **Risk:** The key risks include potential regulatory hurdles, market volatility affecting valuations, and integration challenges post-acquisition.

**Deal 2:**
**Antitrust Policies Impacting M&A in Tech Sector** ([Link](https://finance.yahoo.com/news/trumps-antitrust-cops-are-ok-with-new-mergers-old-tech-monopolies-not-so-much-140038953.html))  
- **Deal Size:** Not specified in news  
- **Valuation Multiples:** Not specified in news  
- **Companies:** Not specified in news  
- **Date Announced:** Not specified in news  
- **Rationale:** The current administration's antitrust policies are creating a more favorable environment for new mergers while maintaining scrutiny on existing tech monopolies, influencing strategic decisions in the TMT sector.  
- **Risk:** The primary risks involve potential regulatory pushbacks and the uncertainty of future antitrust actions that could derail planned mergers.

**Deal 3:**
**Increased M&A Activity Among VC-Backed Firms** ([Link](http://www.pymnts.com/acquisitions/2025/venture-capital-backed-firms-choose-mergers-buyouts-amid-uncertainty-around-ipos/))  
- **Deal Size:** Not specified in news  
- **Valuation Multiples:** Not specified in news  
- **Companies:** Not specified in news  
- **Date Announced:** Not specified in news  
- **Rationale:** Venture capital-backed companies are increasingly favoring mergers and acquisitions over IPOs due to market volatility, indicating a shift in strategy towards consolidation in the TMT sector.  
- **Risk:** Risks include overvaluation in M&A transactions and potential integration difficulties that could arise post-acquisition.

### Summary of Notable M&A Trends
- **Increased Activity:** There is a notable uptick in M&A activity across the TMT sector, as highlighted by JPMorgan's recent analysis.
- **Regulatory Environment:** The evolving antitrust landscape is influencing merger strategies, particularly in technology, where scrutiny on monopolistic practices remains high.
- **Shift from IPOs to M&A:** Many VC-backed firms are opting for mergers and acquisitions as a more stable route compared to the uncertainties surrounding IPOs, reflecting a strategic pivot in the current market climate.

### 2. MARKET DYNAMICS & SENTIMENT

The Technology, Media, and Telecommunications (TMT) sector is currently experiencing a mixed sentiment, characterized by both optimism and caution. The overall market sentiment is buoyed by increased M&A activity, particularly among venture-capital backed firms, as they pivot towards consolidation strategies in response to market volatility. However, regulatory scrutiny, especially in the tech sector, poses significant headwinds that could dampen deal-making enthusiasm.

#### Subsector Breakdown
- **Technology:** The technology subsector remains robust, driven by advancements in artificial intelligence (AI) and cloud computing. Companies like Delta Air Lines are leveraging AI for dynamic pricing strategies, indicating a growing reliance on technology for operational efficiency ([Link](https://www.theverge.com/news/709556/delta-air-lines-ai-ticket-price-rollout)).
- **Media:** The media sector is seeing innovative engagement strategies, as exemplified by The Verge's launch of new site features aimed at deepening audience interaction ([Link](https://www.theverge.com/press-room/710921/verge-site-features-launch-newsletters)). This reflects a shift towards more personalized content delivery.
- **Telecommunications:** The telecom sector is witnessing technological advancements, particularly with T-Mobile's introduction of low-latency technology for 5G, enhancing user experience for applications like video calls and cloud gaming ([Link](https://www.theverge.com/news/710312/t-mobile-low-latency-l4s-5g)).
- **Fintech:** The fintech landscape remains competitive, with firms increasingly focusing on mergers and acquisitions to bolster their market positions amid economic uncertainties.
- **AI:** The AI subsector is experiencing rapid growth, with companies like BYD challenging traditional players such as Tesla in the self-driving car market by offering unique guarantees ([Link](https://gizmodo.com/chinas-byd-takes-the-lead-over-tesla-in-the-self-driving-car-wars-2000631712)).

#### Key Market Drivers and Headwinds
- **Drivers:**
  - **Increased M&A Activity:** The resurgence of M&A activity, particularly among VC-backed firms, is a significant driver. Companies are opting for strategic acquisitions over IPOs due to market volatility.
  - **Technological Advancements:** Innovations in AI and 5G technology are driving growth across various TMT subsectors, enhancing operational efficiencies and user experiences.

- **Headwinds:**
  - **Regulatory Scrutiny:** Heightened antitrust scrutiny in the tech sector could impede merger activities and create uncertainty for investors.
  - **Market Volatility:** Economic uncertainties and fluctuating market conditions may lead to cautious investment strategies among firms.

#### Trading Multiples Trends
Trading multiples in the TMT sector have shown variability, with technology companies generally commanding higher valuations compared to media and telecommunications. As of Q2 2025:
- **Technology Sector:** Average EV/EBITDA multiples are around 20x, reflecting strong investor confidence.
- **Media Sector:** Average EV/EBITDA multiples hover around 12x, indicating a more cautious outlook.
- **Telecommunications Sector:** Average EV/EBITDA multiples are approximately 8x, reflecting the sector's mature nature and competitive pressures.

#### Notable Investor/Analyst Reactions
Analysts have expressed mixed sentiments regarding the future of the TMT sector. For instance, a recent report from JPMorgan highlighted that while M&A activity is picking up, the long-term sustainability of this trend depends on regulatory outcomes and market stability. An analyst noted, "The current environment is ripe for consolidation, but we must remain vigilant about the regulatory landscape that could reshape our strategies."

#### Actionable Insights for Bankers and Investors
- **Focus on M&A Opportunities:** Given the current market dynamics, bankers should prioritize advising clients on potential M&A opportunities, especially in the technology and AI sectors where valuations remain high.
- **Monitor Regulatory Developments:** Investors should keep a close eye on regulatory changes that could impact deal-making in the tech sector, adjusting their strategies accordingly.
- **Diversification Strategies:** Firms should consider diversifying their portfolios across different TMT subsectors to mitigate risks associated with market volatility and regulatory scrutiny.

In conclusion, while the TMT sector exhibits promising growth potential driven by technological advancements and M&A activity, the looming regulatory challenges necessitate a cautious approach for investors and bankers alike.

### 3. BANKING PIPELINE

The current banking pipeline within the TMT sector is characterized by a diverse array of transactions, ranging from live deals in due diligence to mandated and pitching-stage opportunities. This analysis provides a comprehensive overview of the current state of the pipeline, expected revenue, workload allocation, and actionable insights for team management and business development.

#### Deal Pipeline Overview

**Live Deals:**
- **Delta Air Lines (DAL)**: Currently in discussions for a strategic partnership leveraging AI for dynamic pricing, expected to close by Q4 2025. The anticipated deal size is estimated at $500 million, with significant implications for operational efficiencies ([Link](https://www.theverge.com/news/709556/delta-air-lines-ai-ticket-price-rollout)).
- **Meta Platforms (META)**: Engaged in negotiations regarding compliance with EU AI regulations, with a potential settlement or partnership expected by Q3 2025. The deal is valued at approximately $300 million, focusing on regulatory compliance and innovation ([Link](https://www.theverge.com/news/710576/meta-eu-ai-act-code-of-practice-agreement)).

**Mandated Deals:**
- **Indiegogo**: Secured a mandate for acquisition by Gamefound, a board game crowdfunding platform. The deal is expected to be fully launched in Q3 2025, with a valuation of around $150 million. This acquisition aims to integrate Indiegogo's community with Gamefound's technology ([Link](https://www.theverge.com/news/712733/indiegogo-acquired-gamefound-crowdfunding)).
- **Former Anthropic Executive's AI Insurance Startup**: Mandate secured for advisory services in raising $15 million for a new AI insurance startup. The launch is projected for Q4 2025, focusing on liability coverage for AI deployments ([Link](https://venturebeat.com/ai/former-anthropic-exec-raises-15m-to-insure-ai-agents-and-help-startups-deploy-safely/)).

**Pitching-Stage Deals:**
- **Apple Inc. (AAPL)**: Actively pitching for strategic partnerships in AI development, with discussions ongoing for potential collaborations with startups focused on AI technologies. Expected to finalize mandates by Q4 2025 ([Link](https://finance.yahoo.com/news/apple-going-surprise-wall-street-003026452.html)).
- **Telecom Sector**: Engaged in discussions with multiple telecom firms for potential M&A opportunities focused on 5G technology advancements. Expected mandates to be finalized by Q1 2026.

#### Pipeline Tracking Metrics
- **Expected Revenue/Fees**: 
  - Live deals are projected to generate approximately $10 million in advisory fees.
  - Mandated deals are expected to yield around $5 million in fees.
  - Pitching-stage deals could potentially add another $3 million if successful.
  
- **Timing Projections**:
  - **Q2 2025**: Expected close for Delta Air Lines deal.
  - **Q3 2025**: Anticipated launch of the Indiegogo acquisition and Meta's regulatory compliance deal.
  - **Q4 2025**: Potential finalization of Apple’s AI partnerships and Anthropic's insurance startup funding.

- **Workload Allocation and Capacity Analysis**:
  - Current analyst bandwidth is stretched due to multiple live deals and pitching-stage activities. It is advisable to assess team capacity and consider reallocating resources or hiring temporary staff to manage workload effectively.

- **Forecasting and Strategic Planning Implications**:
  - The current pipeline suggests a robust year ahead, with significant revenue potential. Strategic planning should focus on enhancing team capacity, especially in high-demand areas like AI and telecommunications.

#### Notable Pipeline Developments and Competitive Landscape
The competitive landscape remains dynamic, with several firms vying for leadership in AI and telecommunications. For instance, Delta Air Lines' innovative use of AI for pricing strategies positions it as a leader in operational efficiency within the airline industry. Meanwhile, Meta's resistance to EU regulations could create opportunities for competitors to capture market share in the AI compliance space.

#### Actionable Insights for Team Management and Business Development
- **Resource Allocation**: Given the current workload, consider hiring additional analysts or reallocating existing resources to ensure timely execution of live deals and effective management of pitching-stage opportunities.
- **Focus on High-Growth Areas**: Prioritize business development efforts in AI and telecommunications, as these sectors are expected to drive significant revenue growth in the coming quarters.
- **Strengthen Client Relationships**: Engage proactively with clients in the pipeline to solidify relationships and increase the likelihood of successful deal closures.

In conclusion, the TMT banking pipeline is poised for growth, driven by a mix of live, mandated, and pitching-stage deals. By strategically managing resources and focusing on high-potential sectors, the team can capitalize on emerging opportunities and enhance overall performance.

### 4. STAKEHOLDER IMPACT & FORWARD-LOOKING ANALYSIS

As the TMT sector continues to evolve through strategic mergers and acquisitions, the implications for various stakeholders become increasingly significant. This analysis delves into the deal-specific impacts on shareholders, employees, competitors, and customers, while also considering market reactions, potential counter-bids, and the broader landscape of sector consolidation.

#### Deal-Specific Impacts

**Shareholders:**
- **Value Creation/Dilution**: Shareholders of acquiring companies often experience immediate impacts on stock prices post-announcement. For example, when Delta Air Lines (DAL) announced its partnership leveraging AI for dynamic pricing, the stock saw a 5% increase, reflecting investor optimism about future revenue growth. 
  - **Scenario Analysis**:
    - **Best Case**: If the AI pricing strategy leads to a 10% increase in revenue, DAL’s market cap could rise by approximately $1 billion, translating to an estimated $2.50 increase in share price.
    - **Worst Case**: If the implementation faces challenges, resulting in a 5% revenue decline, the market cap could decrease by $500 million, leading to a potential $1.25 drop in share price.
  
**Employees:**
- **Synergies and Restructuring**: Mergers often lead to operational synergies, but they can also result in restructuring. For instance, in the merger between Indiegogo and Gamefound, the integration strategy emphasizes retaining key talent from both companies while streamlining operations to eliminate redundancies. 
  - **Retention Strategies**: Offering retention bonuses and career development opportunities can mitigate turnover. In a similar case, after the merger of two tech firms, employee turnover was reduced by 30% through targeted retention initiatives.

**Competitors:**
- **Market Positioning**: The competitive landscape shifts significantly post-deal. For example, Meta Platforms' refusal to comply with EU AI regulations may provide an opportunity for competitors like Google (GOOGL) to capture market share in the AI compliance sector. 
  - **Competitor Moves**: Following Meta's stance, companies like Microsoft (MSFT) have ramped up their compliance offerings, positioning themselves as more favorable partners for European entities.

**Customers:**
- **Product/Service Implications**: Customers can benefit from enhanced products and services post-merger. For instance, Delta’s AI-driven pricing model aims to provide more personalized ticket pricing, potentially increasing customer satisfaction and loyalty.
  - **Case Study**: After a merger between two telecommunications companies, customers reported a 20% improvement in service quality due to combined resources and technology investments.

#### Market Reaction and Analyst Commentary
Market reactions to these deals have been generally positive, with analysts highlighting the strategic foresight of companies like Delta and Meta. An analyst from Morgan Stanley commented, “Delta’s innovative approach to pricing could redefine customer engagement in the airline industry, positioning it ahead of competitors.” 

#### Expected Market Reaction
- **Scenario Analysis**:
  - **Positive Scenario**: If Delta's AI strategy proves successful, we could see a 10% increase in share price over the next year.
  - **Negative Scenario**: Conversely, if regulatory challenges arise or implementation fails, a 5% decline in share price could occur.

#### Potential Counter-Bids or Competing Offers
The likelihood of counter-bids remains moderate. For instance, if Delta's AI strategy garners significant market attention, competitors may seek to acquire similar technology firms to enhance their offerings. However, the financial health and strategic focus of these companies will dictate the feasibility of such moves.

#### Similar Deals Likely to Follow
Given the current trends, we anticipate increased consolidation in the AI and telecommunications sectors. Companies are likely to pursue acquisitions that enhance their technological capabilities, with a focus on AI integration and compliance solutions.

#### Key Risks and Mitigants
- **Regulatory Risks**: Heightened scrutiny from regulatory bodies, particularly in the EU, poses a risk to tech mergers. Mitigants include proactive engagement with regulators and compliance investments.
- **Integration Risks**: Post-merger integration challenges can lead to operational disruptions. Companies should implement robust integration plans and maintain clear communication with stakeholders.

#### Actionable Insights for Clients and Bankers
- **Strategic Advisory**: Clients should consider engaging in proactive discussions about potential acquisitions that align with their strategic goals, particularly in high-growth areas like AI.
- **Risk Management**: Developing comprehensive risk management strategies will be crucial in navigating regulatory landscapes and ensuring successful integrations.
- **Stakeholder Engagement**: Maintaining open lines of communication with all stakeholders—shareholders, employees, and customers—will be essential to foster trust and support during transitions.

In conclusion, the impacts of TMT sector deals extend across various stakeholders, with implications for shareholder value, employee retention, competitive positioning, and customer satisfaction. By understanding these dynamics and preparing for potential challenges, companies can better navigate the complexities of the evolving market landscape.

### 5. TECH TRENDS

The technology landscape is rapidly evolving, with several key trends emerging that are reshaping industries and creating new opportunities for investment and deal-making. This analysis highlights significant trends such as Fintech, Stablecoins, AI, and the intersection of gaming and finance, providing insights into their market significance, competitive dynamics, and potential M&A opportunities.

#### 1. Fintech

**Trend Explanation**: 
Fintech, or financial technology, encompasses a wide range of services and solutions that leverage technology to enhance financial services. The sector is experiencing explosive growth, driven by increasing consumer demand for digital financial solutions and the need for financial institutions to innovate.

**Market Significance and Growth Trajectory**: 
The global fintech market is projected to grow from $127.66 billion in 2021 to $309.98 billion by 2025, at a CAGR of 25.2%. This growth is fueled by advancements in mobile payment solutions, digital banking, and blockchain technology.

**Key Companies**:
- **JPMorgan Chase (JPM)**: Recently announced plans to introduce new fees for fintech companies accessing its data, indicating a strategic move to monetize its data assets while maintaining competitive pressure on emerging fintechs.
- **Goldman Sachs (GS)**: Actively investing in fintech startups and expanding its digital banking services through Marcus, its online bank, which aims to capture a larger share of the consumer banking market.

**Competitive Landscape**: 
The fintech space is characterized by intense competition between traditional banks and emerging fintech startups. Traditional banks are increasingly adopting fintech solutions to enhance their service offerings, while fintechs are innovating rapidly to disrupt established financial services.

**M&A Opportunities**: 
As traditional banks seek to bolster their digital capabilities, there will be significant M&A activity in the fintech space. Potential targets include niche fintech startups that offer innovative solutions in payments, lending, and wealth management.

#### 2. Stablecoins

**Trend Explanation**: 
Stablecoins are digital currencies pegged to stable assets, such as fiat currencies, designed to minimize volatility. The recent introduction of the GENIUS Act in the U.S. Congress aims to regulate stablecoins, paving the way for banks to issue their own stablecoins.

**Market Significance and Growth Trajectory**: 
The stablecoin market has seen exponential growth, with the total market capitalization reaching approximately $130 billion in 2023. As regulatory frameworks solidify, the market is expected to expand further, with banks likely to play a significant role.

**Key Companies**:
- **Circle**: The issuer of USDC, a popular stablecoin, is positioning itself as a leader in the stablecoin space, focusing on compliance and partnerships with financial institutions.
- **Tether (USDT)**: As one of the first stablecoins, Tether continues to dominate the market, but faces scrutiny regarding its reserves and transparency.

**Competitive Landscape**: 
The stablecoin market is becoming increasingly competitive, with traditional financial institutions entering the space. The regulatory environment will play a crucial role in determining which players succeed.

**M&A Opportunities**: 
Banks may look to acquire established stablecoin issuers or technology firms specializing in blockchain to enhance their digital currency offerings.

#### 3. AI in Financial Services

**Trend Explanation**: 
Artificial Intelligence (AI) is transforming financial services by automating processes, enhancing decision-making, and improving customer experiences. The integration of AI in fintech

### Recommended Readings

**1. Microsoft's $69B Acquisition of Activision Blizzard (ATVI)**
- **Why this matters:** This deal highlights the growing importance of gaming and metaverse strategies in the tech landscape, especially as companies like Microsoft (MSFT) seek to diversify their revenue streams.
- **Read this to understand:** "The Business of Video Games" by Michael P. Wolf - This book provides insights into the gaming industry’s economics and strategic considerations.
- **Key concept to learn:** Understanding mergers and acquisitions in the context of market expansion and competitive positioning.

**2. Amazon's $3.9B Acquisition of MGM (Metro-Goldwyn-Mayer)**
- **Why this matters:** This acquisition underscores the significance of content ownership in the streaming wars, as Amazon (AMZN) aims to bolster its Prime Video offerings against competitors like Netflix (NFLX).
- **Read this to understand:** "The Content Trap" by Bharat Anand - This book explains how content strategy is crucial for digital platforms.
- **Key concept to learn:** The role of intellectual property in enhancing competitive advantage in media and entertainment.

**3. Nvidia's $40B Acquisition of Arm Holdings**
- **Why this matters:** This deal reflects the ongoing consolidation in the semiconductor industry, particularly as AI and machine learning applications drive demand for advanced chip technology.
- **Read this to understand:** "Chip War: The Fight for the World’s Most Critical Technology" by Chris Miller - This book dives into the semiconductor industry's dynamics and geopolitical implications.
- **Key concept to learn:** The impact of technology acquisitions on innovation and market leadership in high-tech sectors.

**4. Salesforce's $27.7B Acquisition of Slack Technologies (WORK)**
- **Why this matters:** This acquisition illustrates the trend of enterprise software companies integrating collaboration tools to enhance their service offerings amid a shift to remote work.
- **Read this to understand:** "The Lean Startup" by Eric Ries - This book provides a framework for
"""

#print(clean_text_for_pdf(testText))
format_brief(clean_text_for_pdf(testText), brief_dir)