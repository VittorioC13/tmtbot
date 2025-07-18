import openai
from config import OPENAI_API_KEY
import json
from pathlib import Path


analysis = """
### 1. RECENT TMT M&A ACTIVITY

**Deal 1:**
**China Approves Merger of CSSC and CSIC to Create World’s Largest Shipbuilder** ([Link](https://gcaptain.com/china-approves-merger-of-cssc-and-csic-to-create-worlds-largest-shipbuilder/))  
- **Deal Size:** Not specified in news  
- **Valuation Multiples:** Not specified in news  
- **Companies:** China State Shipbuilding Corporation (CSSC) acquiring China Shipbuilding Industry Corporation (CSIC)  
- **Date Announced:** Not specified in news  
- **Rationale:** The merger aims to create a dominant player in the shipbuilding industry, enhancing market share and operational synergies.  
- **Risk:** Key risks include regulatory scrutiny, integration challenges, and potential backlash from competitors and labor unions.

**Deal 2:**
**VC-Backed Firms Choose Mergers and Buyouts Amid Uncertainty Around IPOs** ([Link](http://www.pymnts.com/acquisitions/2025/venture-capital-backed-firms-choose-mergers-buyouts-amid-uncertainty-around-ipos/))  
- **Deal Size:** Not specified in news  
- **Valuation Multiples:** Not specified in news  
- **Companies:** Not specified in news  
- **Date Announced:** Not specified in news  
- **Rationale:** Companies backed by venture capital are increasingly opting for mergers and acquisitions over IPOs due to market volatility and uncertainty surrounding public listings.  
- **Risk:** The primary risks include overvaluation in M&A transactions and potential integration difficulties post-acquisition.

### 2. MARKET DYNAMICS & SENTIMENT

The TMT sector is currently experiencing a mixed sentiment landscape, driven by macroeconomic uncertainties and sector-specific dynamics. Overall, the sentiment is cautious, with a notable shift toward M&A activity as companies seek to consolidate in a volatile market. According to recent reports, VC-backed firms are favoring mergers and acquisitions over IPOs, reflecting a strategic pivot in response to market conditions. This trend is particularly pronounced in the fintech and software subsectors, where companies are looking to enhance their competitive positioning through strategic acquisitions.

Breaking down sentiment by subsector reveals that the software sector remains resilient, with many firms reporting stable growth and increasing demand for cloud-based solutions. Conversely, the telecom sector faces headwinds due to regulatory challenges and increasing competition, particularly in the 5G space. The media sector is also navigating a complex landscape, with traditional players struggling to adapt to digital transformation while new entrants capitalize on streaming and content delivery innovations.

Geographically, North America continues to lead in TMT deal activity, accounting for approximately 45% of global M&A transactions in the sector. However, Europe is witnessing a resurgence, particularly in fintech and AI-related deals, as companies seek to leverage technological advancements and regulatory support. In Asia, particularly China, the approval of significant mergers like CSSC and CSIC indicates a strategic push towards consolidation in key industries.

Valuation multiples in the TMT sector have shown variability, with software companies commanding higher EV/EBITDA multiples, averaging around 20x, compared to telecom companies, which are hovering around 8x. This disparity underscores the market's preference for high-growth sectors and the challenges faced by traditional telecom operators.

Investor sentiment is reflected in analyst reports, with many expressing caution regarding the sustainability of current valuations. For instance, a recent report from Jefferies highlighted the need for a more conservative approach to valuation in light of potential economic headwinds. Actionable insights for bankers and investors include focusing on high-growth subsectors, particularly software and AI, while remaining vigilant about potential overvaluations in more traditional sectors.

### 3. BANKING PIPELINE

The current banking pipeline in the TMT sector is robust, with several live deals in progress, particularly in the software and fintech spaces. Notably, there are multiple transactions currently in due diligence, with expected closures in Q3 2025. The anticipated revenue from these active deals is projected to exceed $500 million, with fee structures averaging around 2% of deal value, reflecting the competitive landscape for advisory services.

In terms of mandated deals, several prominent clients have secured mandates for upcoming IPOs, particularly in the fintech sector. Companies like Revolut are in discussions to raise $1 billion at a $65 billion valuation, indicating strong investor interest in the fintech space. This deal is expected to launch in Q4 2025, aligning with the broader trend of VC-backed firms seeking liquidity through public markets.

The pitching-stage deals are also noteworthy, with active discussions ongoing with several high-profile tech companies looking to explore strategic acquisitions. These discussions are primarily focused on enhancing technological capabilities and expanding market reach. The workload allocation for analysts and associates is being closely monitored, with an emphasis on ensuring adequate bandwidth to manage the increasing number of mandates.

Notable developments in the pipeline include the growing interest in AI and cybersecurity firms, driven by increasing demand for digital security solutions. The competitive landscape remains fierce, with multiple banks vying for advisory roles in high-profile transactions. Actionable insights for team management include prioritizing resources towards sectors with high growth potential and ensuring that teams are adequately equipped to handle the increasing deal flow.

### 4. STAKEHOLDER IMPACT & FORWARD-LOOKING ANALYSIS

The recent trend of mergers and acquisitions in the TMT sector has significant implications for various stakeholders. For shareholders, the potential for value creation is substantial, particularly in cases where synergies can be realized post-merger. However, there is also a risk of dilution, especially if companies resort to equity financing to fund acquisitions. Scenario analysis indicates that successful integrations could lead to a 20% increase in shareholder value over the next three years, while failed integrations could result in a 15% decline.

Employees are also affected by these transactions, with potential restructuring and layoffs often accompanying mergers. Companies must navigate these challenges carefully to retain key talent and maintain morale. For instance, the merger of CSSC and CSIC is expected to lead to significant workforce realignment, which could impact employee retention rates.

Competitors are likely to respond strategically to these consolidations, with some companies potentially pursuing counter-bids or alternative acquisitions to strengthen their market positions. The likelihood of competing offers is particularly high in the fintech sector, where companies are aggressively seeking to enhance their technological capabilities.

Customers may experience changes in product offerings and service levels as companies integrate their operations. For example, the merger of CSSC and CSIC could lead to enhanced capabilities in shipbuilding, ultimately benefiting customers through improved service delivery.

Market reactions to these deals are expected to be mixed, with analysts projecting a cautious approach from investors. Scenario analysis suggests that while successful integrations could lead to positive market sentiment, any significant integration challenges could result in negative stock performance.

Key risks associated with these transactions include regulatory scrutiny and potential backlash from labor unions, particularly in large-scale mergers. Companies must develop robust risk mitigation strategies to address these challenges effectively. Actionable insights for clients and bankers include focusing on thorough due diligence processes and proactive stakeholder engagement to navigate potential pitfalls.

### 5. TECH TRENDS

The TMT sector is currently witnessing several key technology trends that are shaping the landscape for M&A activity. One of the most prominent trends is the rise of artificial intelligence (AI), which is being integrated across various applications, from software development to customer service. Companies like OpenAI and Microsoft are at the forefront of this trend, with OpenAI's recent initiatives to enhance AI training in educational settings demonstrating the growing importance of AI in everyday applications.

Another significant trend is the increasing adoption of blockchain technology, particularly in the fintech sector. Companies like Ant International are exploring stablecoin applications, indicating a shift towards more secure and efficient payment systems. This trend is expected to drive M&A activity as firms seek to acquire capabilities in blockchain technology to enhance their service offerings.

Cybersecurity remains a critical focus area, with increasing threats prompting companies to invest in advanced security solutions. The demand for cybersecurity firms is expected to rise, creating potential M&A opportunities as larger firms look to bolster their defenses against cyber threats.

The competitive landscape for these trends is dynamic, with numerous startups emerging to challenge established players. For instance, the launch of G-Knot's biometric wallet represents a novel approach to digital security, indicating a growing interest in innovative solutions within the fintech space.

Investment implications are significant, as firms that capitalize on these trends are likely to experience accelerated growth. Actionable insights for bankers and investors include identifying potential acquisition targets within these emerging technology sectors and leveraging strategic partnerships to enhance competitive positioning.

In conclusion, the TMT sector is navigating a complex landscape characterized by evolving market dynamics, robust M&A activity, and significant technological advancements. Stakeholders must remain vigilant and adaptable to capitalize on emerging opportunities while effectively managing associated risks.
"""


openai_client = openai.Client(api_key=OPENAI_API_KEY)
def detect_technical_terms(analysis: str) -> dict:
        find_terms_prompt = f"""I need you to read this following TMT report on daily news, and identify every technical terms that 
                            someone that just got into the industry will find confusing. Then list them along side their definition in
                            this exact format:
                            term : short one line definition
                            Here's your report:
                            {analysis}
                            Note: do not include line numbers
                            instead of "1. CSSC: China State Shipbuilding Corporation", do "CSSC:China State Shipbuilding Corporation"
                            """
        try:
            print('querying gpt3.5...')
            response = openai_client.chat.completions.create(
                model = "gpt-3.5-turbo",
                messages=[
                    {'role': 'user', 'content': find_terms_prompt}
                ],
                temperature=0.2
            )
        except Exception as e:
            raise e
        
        print('got gpt3.5 response, parsing')
        #parse raw glossary from gpt3.5 and put them into glossary dictionary
        raw_glossary = response.choices[0].message.content
        print(raw_glossary)
        glossary = {}
        for line in raw_glossary.splitlines():
            if ":" not in line:
                continue
            term, definition = line.split(": ", 1)
            if term and definition:
                glossary[term] = definition

        return glossary

print(detect_technical_terms(analysis))
