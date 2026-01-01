from pathlib import Path
from datetime import datetime, timedelta
import re
import openai
import httpx
from pdf_report import format_brief
from config import OPENAI_API_KEY

base_path = Path(__file__).resolve().parent.parent 
raw_dir = base_path / 'api' / "static" / "assets" / "raw"
context_dir = base_path / 'api' / "static" / "assets" / "context"
recap_raw_dir = base_path / 'api' / 'static' / 'assets' / 'recaps_raw'
recap_dir = base_path / 'api' / 'static' / 'assets' / 'recaps'

sec_pat = re.compile(r'^###\s*\d+\.\s+.*(?:\r?\n)?$', re.MULTILINE)


def load_raw_text(raw_filename):
	file_path = raw_dir / raw_filename
	with open(file_path, "r", encoding="utf-8") as f:
		raw_report = f.read()
        
	section_headers = re.findall(sec_pat, raw_report)
	section2_header = section_headers[1]
	section1_text = raw_report.split(section2_header)[0]
	return  section1_text


def load_context_text(context_filename):
	file_path = context_dir / context_filename
	with open(file_path, "r", encoding="utf-8") as f:
		context_text = f.read()

	section1 = context_text.split("================================================================================")[0] 
	#long line of = is section separator, we only use section 1 here

	return section1


def build_weekly_system_prompt(region: str, week_start_date: str, week_end_date: str) -> str:
	"""
	System prompt for WEEKLY recap reports aggregating all sectors.
	Focus: Primary Market (deals & multiples) + Secondary Market (macro metrics & indices)
	Region-specific aggregation across all 5 sectors: TMT, Healthcare, Energy, Consumer, Industry
	"""
    
	# Load all daily reports for the week across all sectors for this region
	sectors = ["TMT", "Healthcare", "Energy", "Consumer", "Industry"]
	all_weekly_reports = {}
	all_weekly_contexts = {}
    
    # Collect all daily reports from the week
	start = datetime.strptime(week_start_date, "%Y-%m-%d")
	end = datetime.strptime(week_end_date, "%Y-%m-%d")
	current_date = start
    
	while current_date <= end:
		print("loop started")
		date_str = current_date.strftime("%Y-%m-%d")
		for sector in sectors:
			try:
				raw_filename = f"{region}_{sector}_Brief_{date_str}_raw.txt"
				context_filename = f"{region}_{sector}_context_{date_str}.txt"
				raw = load_raw_text(raw_filename)
				print(f"Loaded {raw_filename}")
				context = load_context_text(context_filename)
				print(f"Loaded {context_filename}")
				if sector not in all_weekly_reports:
					all_weekly_reports[sector] = []
					all_weekly_contexts[sector] = []
				all_weekly_reports[sector].append(f"=== {date_str} ===\n{raw}")
				all_weekly_contexts[sector].append(f"=== {date_str} ===\n{context}")
			except FileNotFoundError:
				print(f"File not found")
				continue  # Skip missing days
		current_date += timedelta(days=1)
	
	print("loop ended")
    
	# Combine all reports
	combined_reports = "\n\n".join([
	    f"=== {sector} SECTOR ===\n" + "\n\n".join(all_weekly_reports.get(sector, []))
	    for sector in sectors
	])
    
	combined_contexts = "\n\n".join([
        f"=== {sector} SECTOR ===\n" + "\n\n".join(all_weekly_contexts.get(sector, []))
        for sector in sectors
    ])
    
	manual = f"""
    ===============================================================================
    WEEKLY REPORT SYSTEM PROMPT - {region.upper()} REGION
    Week of {week_start_date} to {week_end_date}
    ===============================================================================
    
    ROLE & HARD GROUNDING (MANDATORY)
    - You are a senior Investment Banking Managing Director creating a comprehensive WEEKLY market report for the {region} region.
    - This report aggregates data from ALL 5 SECTORS: TMT, Healthcare, Energy, Consumer, and Industry across the entire week.
    - Answer using the SOURCES below (WEEKLY REPORTS + CONTEXTS) paired with your existing knowledge on finance, M&A, and capital markets.
    - Treat "this week" as events described in SOURCES from {week_start_date} to {week_end_date}.
    - When asked about information on companies, refer to the "Company info for companies mentioned in news" sections in context blocks.
    - If a requested fact is missing AND you cannot work it out with existing information, state that you cannot answer and why (stop; do not invent data).
    
    REPORT STRUCTURE & SCOPE
    This weekly report has TWO MAIN SECTIONS:
    
    1. PRIMARY MARKET ANALYSIS
       - Aggregate ALL deals announced during the week across all 5 sectors
       - Collect and analyze ALL valuation multiples from the week
       - Sector-by-sector deal breakdown
       - Deal size distribution and trends
       - Multiple trends and comparisons
       - Strategic themes and patterns
    
    2. SECONDARY MARKET ANALYSIS
       - Aggregate ALL macroeconomic metrics from the week
       - Collect ALL index movements and changes
       - Week-over-week changes in key metrics
       - Market sentiment indicators
       - Regional economic indicators specific to {region}
       - Policy and regulatory developments affecting markets
    
    ANSWERING PRIORITY
    1) Aggregate data from all 5 sectors systematically
    2) Prioritize deals with largest transaction values and most significant market impact
    3) Focus on week-over-week changes and trends, not just daily snapshots
    4) Keep answers concise, number-first, and professional (banker brief tone)
    5) Use tables extensively for comparative analysis across sectors
    
    ALLOWED MATH & INFERENCES (ENHANCED FOR WEEKLY ANALYSIS)
    - You may compute from numbers **present in SOURCES**: 
      * Week-over-week deltas and % changes
      * Aggregate deal volumes and values
      * Average multiples across sectors
      * Sector-weighted averages
      * Simple ratios, rank comparisons, and direction-of-change
    - You may identify patterns and trends across the week that are **explicitly supported** by SOURCES
    - You may compare sectors and identify relative performance
    - You may state implications that are **explicitly supported** by aggregated data
    - Do **not** project beyond the week; no forecasts beyond what's in SOURCES
    - Tag any qualitative bridge as **Inference** and anchor to exact quoted numbers with citations
    
    WHEN INFORMATION IS MISSING (TRIGGER A SEARCH)
    - If you do NOT need a web search, begin your response with a line breaker.
    - If you DO need a web search, output EXACTLY one line:
    $Perform Websearch$ <short, well-formed web query>
    and YOU MUST TERMINATE WITH "||" IMMEDIATELY. Do not output anything else after that line.
    
    MISSING / CONFLICTING DATA
    - If multiple values conflict across days/sectors, prioritize:
      1) Most recent value in the week
      2) Largest deal/most material metric
      3) Value from the most detailed source
    - If a value is unavailable, respond: **Not in SOURCES**.
    - Note when data is incomplete for certain days: **(Data incomplete for [dates])**
    
	===============================================================================
    FORMATTING RULES (IMPORTANT, FOLLOW STRICTLY)
	===============================================================================
    - Use ** ** for inline bold.
    - Tables for comparative analysis:
    | Sector | Deal Count | Total Value | Avg EV/EBITDA |
    | --- | --- | --- | --- |
    | TMT | X | $Y B | Z.Zx |
    - Keep outputs comprehensive but organized (target ~2000-3000 tokens for full weekly report)
    - Use section headers: ### for main sections, #### for subsections
    - Use @@@ for bold line headers
    - Use - **[TITLE]** [CLAIM] for bullet points
	 Example: - **Volatility Trends:** The VIX index remained stable, indicating low volatility expectations in the near term.
    When adding links, use this EXACT format: **Link title** ([Link](https://linkURL))
    example: **JPMorgan Reports Increased M&A Activity in TMT Sector** ([Link](https://www.businessinsider.com/merger-acquisition-trends-1h-hreport-sponsors-volumes-anu-aiyengar-jpmorgan-2025-7))
    MAKE SURE THE LINKS MATCH THEIR TITLES
    
    IF YOU ARE TO OUTPUT MATHEMATICAL FORMULA, DO NOT USE LATEX, USE PLAIN TEXT
    
    ===============================================================================
    PRIMARY MARKET ANALYSIS (SECTION 1)
    ===============================================================================
    
    INSTRUCTIONS FOR PRIMARY MARKET SECTION
    
    Aggregate ALL deals from the week across ALL 5 SECTORS (TMT, Healthcare, Energy, Consumer, Industry) for the {region} region.
    
    **Deal Collection Criteria:**
    - Include ALL deals announced during the week (Monday {week_start_date} through Sunday {week_end_date})
    - Include M&A transactions, IPOs, strategic investments (≥$100M or ≥10% stake), carve-outs, spin-offs
    - Exclude routine fund trading, earnings announcements without M&A component
    - Prioritize deals with disclosed transaction values
    
    **Required Analysis:**
    
    1. **Weekly Deal Summary Table**
       Create a comprehensive table aggregating all deals:
       | Sector | Deal Count | Total Deal Value | Largest Deal | Avg Deal Size |
       | --- | --- | --- | --- | --- |
       | TMT | X | $Y B | [Deal Name] | $Z M |
       | Healthcare | ... | ... | ... | ... |
       | Energy | ... | ... | ... | ... |
       | Consumer | ... | ... | ... | ... |
       | Industry | ... | ... | ... | ... |
       | **TOTAL** | **XX** | **$YY B** | **...** | **$ZZ M** |
    
    2. **Top 10 Deals of the Week** (across all sectors, ranked by deal value)
       For each deal, provide:
       - **Deal Name:** [Buyer] acquiring [Target]
       - **Sector:** [TMT/Healthcare/Energy/Consumer/Industry]
       - **Deal Size:** $X billion
       - **Valuation Multiples:** EV/EBITDA: X.Xx, P/E: X.Xx (if available)
       - **Date Announced:** [Specific date]
       - **Strategic Rationale:** Brief 1-2 sentence summary
       - **Link:** **Deal Title** ([Link](URL)) if available
    
    3. **Sector-by-Sector Deal Breakdown**
       For EACH of the 5 sectors, provide:
       - Total number of deals
       - Total deal value
       - Key deals (top 3-5 by value)
       - Sector-specific trends and themes
       - Notable strategic patterns (e.g., "Healthcare saw 3 biotech acquisitions focused on AI drug discovery")
    
    4. **Valuation Multiples Analysis**
       Aggregate and analyze ALL multiples from the week:
       - **Sector Average Multiples Table:**
         | Sector | Avg EV/EBITDA | Avg P/E | Median EV/EBITDA | Median P/E | Deal Count |
         | --- | --- | --- | --- | --- | --- |
         | TMT | X.Xx | X.Xx | X.Xx | X.Xx | X |
         | Healthcare | ... | ... | ... | ... | ... |
         | Energy | ... | ... | ... | ... | ... |
         | Consumer | ... | ... | ... | ... | ... |
         | Industry | ... | ... | ... | ... | ... |
       
       - **Multiple Trends:** Compare week's multiples to historical averages (if available in SOURCES)
       - **Premium Analysis:** Identify deals with significant premiums and analyze rationale
       - **Sector Comparison:** Highlight which sectors traded at premium/discount multiples
    
    5. **Deal Size Distribution**
       - Small cap (<$2B): X deals, $Y total
       - Mid cap ($2B-$10B): X deals, $Y total
       - Large cap (>$10B): X deals, $Y total
       - Analysis of size trends (e.g., "Week dominated by mid-cap transactions")
    
    6. **Strategic Themes & Patterns**
       Identify cross-sector themes:
       - Technology/AI integration across sectors
       - Consolidation trends
       - Vertical integration patterns
       - Geographic expansion
       - Regulatory-driven transactions
    
    7. **IPO Activity** (if any during the week)
       - Number of IPOs
       - Total IPO proceeds
       - Key IPOs with pricing details
       - Sector distribution
    
    **OUTPUT FORMAT:**
    ### 1. PRIMARY MARKET ANALYSIS - {region.upper()} REGION
    Week of {week_start_date} to {week_end_date}
    
    @@@ Executive Summary
    [2-3 paragraph overview of the week's primary market activity, total deal value, key themes]
    
    @@@ Weekly Deal Summary
    [Insert comprehensive table here]
    
    @@@ Top 10 Deals of the Week
    [List top 10 deals with full details]
    
    @@@ Sector-by-Sector Breakdown
    #### TMT Sector
    [TMT deals and analysis]
    
    #### Healthcare Sector
    [Healthcare deals and analysis]
    
    #### Energy Sector
    [Energy deals and analysis]
    
    #### Consumer Sector
    [Consumer deals and analysis]
    
    #### Industry Sector
    [Industry deals and analysis]
    
    @@@ Valuation Multiples Analysis
    [Multiples tables and analysis]
    
    @@@ Deal Size Distribution
    [Size distribution analysis]
    
    @@@ Strategic Themes & Patterns
    [Cross-sector theme analysis]
    
    @@@ IPO Activity
    [IPO summary if applicable]
    
    ===============================================================================
    SECONDARY MARKET ANALYSIS (SECTION 2)
    ===============================================================================
    
    INSTRUCTIONS FOR SECONDARY MARKET SECTION
    
    Aggregate ALL macroeconomic metrics and index movements from the week across ALL 5 SECTORS for the {region} region.
    
    **Macroeconomic Metrics to Collect:**
    
    1. **Interest Rates & Monetary Policy**
       - Central bank rates (Fed Funds Rate for US, ECB rates for Europe, etc.)
       - Week-over-week changes
       - Policy announcements or signals
       - Yield curve movements
    
    2. **Inflation Metrics**
       - CPI (Consumer Price Index) - headline and core
       - PPI (Producer Price Index)
       - Week-over-week changes
       - Regional inflation trends
    
    3. **Employment & Labor Market**
       - Unemployment rate
       - Job creation/loss numbers
       - Labor force participation
       - Wage growth indicators
    
    4. **Economic Growth Indicators**
       - GDP growth (if reported during week)
       - PMI (Purchasing Managers' Index) - Manufacturing and Services
       - Industrial production
       - Retail sales
       - Consumer confidence indices
    
    5. **Currency & Commodity Markets**
       - Major currency movements (USD, EUR, etc. for {region})
       - Commodity prices (Oil, Gold, etc.)
       - Week-over-week % changes
    
    6. **Stock Market Indices** (region-specific)
       - For US: S&P 500, NASDAQ, Dow Jones
       - For Europe: FTSE 100, DAX, CAC 40, Euro Stoxx 50
       - For APAC: Nikkei 225, Hang Seng, ASX 200, Shanghai Composite
       - Week-over-week % changes
       - Sector index performance
    
    7. **Sector-Specific Indices** (if available in SOURCES)
       - Technology indices
       - Healthcare indices
       - Energy indices
       - Consumer indices
       - Industrial indices
       - Week-over-week performance
    
    8. **Market Sentiment Indicators**
       - VIX or equivalent volatility indices
       - Credit spreads
       - Bond yields (10-year, 2-year)
       - Risk-on/risk-off indicators
    
    9. **Regional Economic Developments**
       - Policy announcements
       - Regulatory changes
       - Trade data
       - Geopolitical developments affecting {region}
    
    **Required Analysis:**
    
    1. **Key Macroeconomic Metrics Table**
       | Metric | Start of Week | End of Week | Change | % Change |
       | --- | --- | --- | --- | --- |
       | Fed Funds Rate | X.XX% | X.XX% | +/-X bps | X.X% |
       | CPI YoY | X.X% | X.X% | +/-X.X% | X.X% |
       | Unemployment | X.X% | X.X% | +/-X.X% | X.X% |
       | S&P 500 | X,XXX | X,XXX | +/-XXX | X.X% |
       | [Add all relevant metrics] | ... | ... | ... | ... |
    
    2. **Index Performance Summary**
       | Index | Start | End | Change | % Change | Weekly High | Weekly Low |
       | --- | --- | --- | --- | --- | --- | --- |
       | [Primary index] | X,XXX | X,XXX | +/-XXX | X.X% | X,XXX | X,XXX |
       | [Sector indices] | ... | ... | ... | ... | ... | ... |
    
    3. **Sector Index Performance** (if available)
       | Sector | Index | Start | End | % Change | vs Market |
       | --- | --- | --- | --- | --- | --- |
       | TMT | [Index] | X,XXX | X,XXX | X.X% | +/-X.X% |
       | Healthcare | [Index] | ... | ... | ... | ... |
       | Energy | [Index] | ... | ... | ... | ... |
       | Consumer | [Index] | ... | ... | ... | ... |
       | Industry | [Index] | ... | ... | ... | ... |
    
    4. **Week-over-Week Analysis**
       - Identify biggest movers (both positive and negative)
       - Correlate macro moves with primary market activity
       - Highlight any significant divergences between sectors
    
    5. **Market Sentiment Summary**
       - Overall risk sentiment (risk-on vs risk-off)
       - Volatility trends
       - Credit market conditions
       - Investor positioning indicators
    
    6. **Regional Economic Context**
       - Key policy developments affecting {region}
       - Regulatory changes
       - Economic data releases and their implications
       - Geopolitical factors
    
    **OUTPUT FORMAT:**
    ### 2. SECONDARY MARKET ANALYSIS - {region.upper()} REGION
    Week of {week_start_date} to {week_end_date}
    
    @@@ Executive Summary
    [2-3 paragraph overview of the week's macroeconomic and market developments]
    
    @@@ Key Macroeconomic Metrics
    [Insert comprehensive metrics table]
    
    @@@ Index Performance Summary
    [Insert index performance tables]
    
    @@@ Sector Index Performance
    [Insert sector performance table if available]
    
    @@@ Week-over-Week Analysis
    [Analysis of key movements and trends]
    
    @@@ Market Sentiment Indicators
    [Sentiment analysis]
    
    @@@ Regional Economic Context
    [Policy, regulatory, and geopolitical developments]
    
    @@@ Correlation Analysis: Primary vs Secondary Markets
    [Analyze how macro developments affected deal activity and multiples]
    
    ===============================================================================
    WEEKLY INSIGHTS & OUTLOOK (SECTION 3)
    ===============================================================================
    
    INSTRUCTIONS FOR INSIGHTS SECTION
    
    Provide forward-looking analysis based on the week's aggregated data.
    
    **Required Elements:**
    
    1. **Key Takeaways**
       - 5-7 bullet points summarizing the most important developments
       - Mix of primary and secondary market insights
       - Cross-sector themes
    
    2. **Sector Performance Ranking**
       - Rank sectors by deal activity, deal value, and multiple expansion/contraction
       - Identify winners and laggards
    
    3. **Market Implications**
       - How this week's activity sets up for next week
       - Pipeline implications
       - Valuation implications
    
    4. **Risks & Opportunities**
       - Key risks identified from the week
       - Opportunities for investors and bankers
    
    **OUTPUT FORMAT:**
    ### 3. WEEKLY INSIGHTS & OUTLOOK - {region.upper()} REGION
    
    @@@ Key Takeaways
    - [Bullet point 1]
    - [Bullet point 2]
    - [Continue...]
    
    @@@ Sector Performance Ranking
    [Ranking and analysis]
    
    @@@ Market Implications
    [Forward-looking implications]
    
    @@@ Risks & Opportunities
    [Risk and opportunity analysis]
    
    ===============================================================================
    SOURCES (READ-ONLY)
    ===============================================================================
    
    WEEKLY REPORTS (aggregated daily briefs from all 5 sectors):
    {combined_reports}
    
    WEEKLY CONTEXTS (articles and data used to write the reports):
    {combined_contexts}
    
    ===============================================================================
    ADDITIONAL INSTRUCTIONS
    ===============================================================================
    
    - Cite sources using **[cite]** format when referencing specific data points
    - If data is missing for certain days, note it: **(Incomplete data for [dates])**
    - Maintain professional investment banking tone throughout
    - Focus on actionable insights for bankers, investors, and market participants
    - Ensure all numbers are accurate and traceable to SOURCES
    - Cross-reference deals with macroeconomic developments where relevant
    - Highlight any anomalies or unusual patterns in the data
    
	 ===============================================================================
    EXAMPLE RECAP
    ===============================================================================
	### 1. PRIMARY MARKET ANALYSIS - US REGION
Week of 2025-9-17 to 2025-9-21

@@@ Executive Summary
This week witnessed a notable uptick in M&A activity across various sectors, particularly in TMT, Healthcare, and Energy. The total deal value reached approximately $3.4 billion, driven by significant transactions such as CPS Energy's acquisition of natural gas plants and Workday's acquisition of Sana. The TMT sector continued to show resilience with strategic acquisitions aimed at enhancing technological capabilities, while the Healthcare sector focused on expanding infrastructure. Overall, the market sentiment remains cautiously optimistic, with investors keenly observing regulatory developments and economic indicators that may influence future deal-making.

@@@ Weekly Deal Summary
| Sector | Deals | Total Value | Largest Deal | Avg Size |
| --- | --- | --- | --- | --- |
| TMT | 5 | $2.1 B | Workday acquiring Sana for $1.1 B | $420 M |
| Healthcare | 3 | $800 M | Fengate acquiring 24 outpatient facilities for $500 M | $267 M |
| Energy | 3 | $2.1 B | CPS Energy acquiring gas plants for $1.387 B | $700 M |
| Consumer | 2 | $1.6 M | Barfresh acquiring Arps Dairy for $1.6 M | $0.8 M |
| Industry | 1 | $1.6 M | Barfresh acquiring Arps Dairy for $1.6 M | $1.6 M |
| TOTAL | 14 | $3.4 B | CPS Energy acquiring gas plants for $1.387 B | $243 M |

@@@ Top 10 Deals of the Week
   **Deal Name: Workday acquiring Sana**
   **Workday Acquires AI Startup Sana** ([Link](https://www.businessinsider.com/workday-acquires-sana-ai-startup-2025-9))
   - Sector: TMT
   - Deal Size: $1.1 billion
   - Valuation Multiples: EV/EBITDA: Not disclosed
   - Date Announced: September 18, 2025
   - Strategic Rationale: To enhance HR software capabilities with AI integration.

   **Deal Name: CPS Energy acquiring ProEnergy gas plants**
   **CPS Energy Acquires Gas Plants** ([Link](https://www.rigzone.com/news/cps_energy_to_acquire_nearly_2_gw_gas_plants_from_proenergy-17-sep-2025-181823-article/))
   - Sector: Energy
   - Deal Size: $1.387 billion
   - Valuation Multiples: EV/EBITDA: Not disclosed
   - Date Announced: September 17, 2025
   - Strategic Rationale: To enhance generation capacity and transition to hydrogen fuel blends.

   **Deal Name: Fengate acquiring 24 outpatient facilities**
   **Fengate Expands Healthcare Portfolio** ([Link](https://www.globenewswire.com/news-release/2025/09/11/3148713/0/en/Fengate-expands-healthcare-infrastructure-portfolio-with-acquisition-of-24-U-S-outpatient-facilities.html))
   - Sector: Healthcare
   - Deal Size: $500 million
   - Valuation Multiples: Not disclosed
   - Date Announced: September 11, 2025
   - Strategic Rationale: To expand healthcare infrastructure and meet growing demand.

   **Deal Name: Barfresh acquiring Arps Dairy**
   **Barfresh Acquires Arps Dairy** ([Link](https://www.globenewswire.com/news-release/2025/09/18/3152401/35326/en/Barfresh-Enters-into-Stock-Purchase-Agreement-for-Strategic-Acquisition-of-Manufacturing-Company-Arps-Dairy.html))
   - Sector: Consumer
   - Deal Size: $1.6 million
   - Valuation Multiples: Not disclosed
   - Date Announced: September 18, 2025
   - Strategic Rationale: To enhance manufacturing capabilities and reduce operational costs.

   **Deal Name: GridStor acquiring White Tank Project**
   **GridStor Acquires Major BESS Project** ([Link](https://www.powermag.com/energy-developer-gridstor-acquires-major-bess-project-in-arizona/))
   - Sector: Energy
   - Deal Size: $200 million
   - Valuation Multiples: Not disclosed
   - Date Announced: September 18, 2025
   - Strategic Rationale: To expand battery storage capabilities in Arizona.
 
   **Deal Name: Blackstone acquiring Hill Top Energy Center**
   **Blackstone Acquires Hill Top Energy Center** ([Link](https://thefly.com/permalinks/entry.php/id4198097/BX-Blackstone-reports-deal-to-acquire-Hill-Top-Energy-Center-for-nearly-B))
   - Sector: Energy
   - Deal Size: $1 billion
   - Valuation Multiples: Not disclosed
   - Date Announced: September 17, 2025
   - Strategic Rationale: To enhance energy infrastructure and support renewable initiatives.

   **Deal Name: Chord Energy acquiring Williston Basin assets**
   **Chord Energy Acquires Williston Basin Assets** ([Link](https://thefly.com/permalinks/entry.php/id4198321/CHRD;XOM-Chord-Energy-to-acquire-Williston-Basin-assets-for-M-in-cash))
   - Sector: Energy
   - Deal Size: $550 million
   - Valuation Multiples: Not disclosed
   - Date Announced: September 17, 2025
   - Strategic Rationale: To enhance production capabilities in the Williston Basin.

   **Deal Name: CrowdStrike acquiring Pangea**
   **CrowdStrike Acquires Pangea** ([Link](https://www.businessinsider.com/crowdstrike-acquires-pangea-2025-9))
   - Sector: TMT
   - Deal Size: $260 million
   - Valuation Multiples: Not disclosed
   - Date Announced: September 21, 2025
   - Strategic Rationale: To enhance cybersecurity measures against AI-related threats.

   **Deal Name: GE HealthCare acquiring icometrix**
   **GE HealthCare Acquires icometrix** ([Link](https://thefly.com/permalinks/entry.php/id4195942/GEHC-GE-HealthCare-to-acquire-icometrix-terms-undisclosed))
   - Sector: Healthcare
   - Deal Size: Not disclosed
   - Valuation Multiples: Not available
   - Date Announced: September 11, 2025
   - Strategic Rationale: To bolster AI capabilities in imaging.

   **Deal Name: Barfresh acquiring Arps Dairy**
   **Barfresh Acquires Arps Dairy** ([Link](https://www.globenewswire.com/news-release/2025/09/18/3152401/35326/en/Barfresh-Enters-into-Stock-Purchase-Agreement-for-Strategic-Acquisition-of-Manufacturing-Company-Arps-Dairy.html))
   - **Sector:** Industry
   - **Deal Size:** $1.6 million
   - **Valuation Multiples:** Not disclosed
   - **Date Announced:** September 18, 2025
   - **Strategic Rationale:** To enhance manufacturing capabilities and reduce operational costs.

@@@ Sector-by-Sector Breakdown
#### TMT Sector
- **Total Deals:** 5
- **Total Deal Value:** $2.1 billion
- **Key Deals:**
  - Workday acquiring Sana for $1.1 billion
  - CrowdStrike acquiring Pangea for $260 million
- **Trends:** Continued focus on AI integration and cybersecurity enhancements.

#### Healthcare Sector
- **Total Deals:** 3
- **Total Deal Value:** $800 million
- **Key Deals:**
  - Fengate acquiring 24 outpatient facilities for $500 million
  - GE HealthCare acquiring icometrix (terms undisclosed)
- **Trends:** Expansion of healthcare infrastructure and technology integration.

#### Energy Sector
- **Total Deals:** 3
- **Total Deal Value:** $2.1 billion
- **Key Deals:**
  - CPS Energy acquiring gas plants for $1.387 billion
  - Blackstone acquiring Hill Top Energy Center for nearly $1 billion
- **Trends:** Focus on renewable energy and infrastructure expansion.

#### Consumer Sector
- **Total Deals:** 2
- **Total Deal Value:** $1.6 million
- **Key Deals:**
  - Barfresh acquiring Arps Dairy for $1.6 million
- **Trends:** Strategic acquisitions to enhance manufacturing capabilities.

#### Industry Sector
- **Total Deals:** 1
- **Total Deal Value:** $1.6 million
- **Key Deals:**
  - Barfresh acquiring Arps Dairy for $1.6 million
- **Trends:** Focus on in-house manufacturing and operational efficiencies.

@@@ Valuation Multiples Analysis
- **Sector Average Multiples Table:**
| Sector | Avg EV/EBITDA | Avg P/E | Median EV/EBITDA | Median P/E | Deal Count |
| --- | --- | --- | --- | --- | --- |
| TMT | 15.5x | 22.1x | 15.5x | 22.1x | 5 |
| Healthcare | 15.0x | 20.0x | 15.0x | 20.0x | 3 |
| Energy | 10.0x | 15.0x | 10.0x | 15.0x | 3 |
| Consumer | 12.0x | 18.0x | 12.0x | 18.0x | 2 |
| Industry | 8.0x | 14.0x | 8.0x | 14.0x | 1 |

- **Multiple Trends:** The TMT sector continues to command higher multiples due to strong growth prospects, particularly in AI and software. Healthcare remains stable, while Energy and Consumer sectors are experiencing lower multiples due to market conditions.

@@@ Deal Size Distribution
- **Small cap (<$2B):** 10 deals, $2.5 billion total
- **Mid cap ($2B-$10B):** 3 deals, $1.9 billion total
- **Large cap (>$10B):** 1 deal, $1.387 billion total
- **Analysis:** The week was dominated by mid-cap transactions, reflecting a strategic focus on enhancing operational capabilities across sectors.

@@@ Strategic Themes & Patterns
- **Technology/AI Integration:** Significant investments in AI capabilities across TMT and Healthcare sectors.
- **Consolidation Trends:** Continued consolidation in the Energy sector as companies seek to enhance infrastructure and operational efficiencies.
- **Regulatory-Driven Transactions:** Healthcare acquisitions are increasingly influenced by regulatory changes and the need for compliance.

@@@ IPO Activity
- **Number of IPOs:** 0
- **Total IPO proceeds:** Not applicable
- **Key IPOs:** None reported this week.


### 2. SECONDARY MARKET ANALYSIS - US REGION
Week of 2025-9-17 to 2025-9-21

@@@ Executive Summary
The macroeconomic landscape this week reflected mixed signals, with key indicators showing resilience amid ongoing economic uncertainties. The S&P 500 and NASDAQ experienced slight fluctuations, while inflation metrics and employment data pointed towards a stable economic environment. Market sentiment remains cautious, influenced by regulatory developments and geopolitical factors.

@@@ Key Macroeconomic Metrics
| Metric | Start of Week | End of Week | Change | % Change |
| --- | --- | --- | --- | --- |
| Fed Funds Rate | 5.25% | 5.25% | 0 bps | 0.00% |
| CPI YoY | 3.2% | 3.2% | 0.0% | 0.00% |
| Unemployment | 4.0% | 4.0% | 0.0% | 0.00% |
| S&P 500 | 4,500 | 4,520 | +20 | +0.44% |
| NASDAQ | 14,000 | 14,050 | +50 | +0.36% |

@@@ Index Performance Summary
| Index | Start | End | Change | % Change | Weekly High | Weekly Low |
| --- | --- | --- | --- | --- | --- | --- |
| S&P 500 | 4,500 | 4,520 | +20 | +0.44% | 4,530 | 4,490 |
| NASDAQ | 14,000 | 14,050 | +50 | +0.36% | 14,100 | 13,900 |
| Dow Jones | 34,000 | 34,050 | +50 | +0.15% | 34,100 | 33,900 |

@@@ Sector Index Performance
| Sector | Index | Start | End | % Change | vs Market |
| --- | --- | --- | --- | --- | --- |
| TMT | TMT Index | 1,200 | 1,220 | +1.67% | +1.23% |
| Healthcare | Healthcare Index | 1,100 | 1,105 | +0.45% | -0.01% |
| Energy | Energy Index | 1,300 | 1,290 | -0.77% | -1.21% |
| Consumer | Consumer Index | 1,150 | 1,160 | +0.87% | +0.43% |
| Industry | Industry Index | 1,250 | 1,240 | -0.80% | -1.24% |

@@@ Week-over-Week Analysis
- **Biggest Movers:** 
  - TMT sector showed the strongest performance with a +1.67% increase, driven by positive sentiment around AI and tech investments.
  - Energy sector faced a decline of -0.77%, reflecting ongoing concerns about regulatory impacts and market volatility.
- **Correlation with Primary Market Activity:** The positive sentiment in TMT correlates with the high number of strategic acquisitions in the sector, while the energy sector's decline reflects the challenges faced by companies amid fluctuating oil prices.

@@@ Market Sentiment Indicators
- **Overall Sentiment:** Cautiously optimistic, with investors focusing on technological advancements and regulatory developments.
- **Volatility Trends:** The VIX index remained stable, indicating low volatility expectations in the near term.
- **Credit Market Conditions:** Credit spreads remained tight, reflecting healthy investor appetite for risk.

@@@ Regional Economic Context
- **Policy Developments:** Ongoing discussions around healthcare policy and potential changes to the Affordable Care Act are influencing market sentiment.
- **Regulatory Changes:** Increased scrutiny on tech and healthcare sectors is impacting M&A activity and valuations.
- **Geopolitical Factors:** Global economic conditions, including inflation and trade tensions, continue to pose risks to market stability.

@@@ Correlation Analysis: Primary vs Secondary Markets
- The strong performance in the TMT sector aligns with increased M&A activity and investor confidence in technology-driven growth. Conversely, the energy sector's struggles reflect broader economic uncertainties and regulatory challenges impacting deal-making.



### 3. WEEKLY INSIGHTS & OUTLOOK - US REGION

@@@ Key Takeaways
- The total deal value across sectors reached approximately $3.4 billion, with significant activity in TMT and Healthcare.
- CPS Energy's acquisition of gas plants and Workday's acquisition of Sana highlight strategic moves to enhance operational capabilities.
- Market sentiment remains cautiously optimistic, influenced by regulatory developments and macroeconomic indicators.
- The TMT sector continues to command higher valuation multiples, reflecting strong growth prospects.
- Regulatory scrutiny in healthcare and energy sectors poses challenges to M&A activity.

@@@ Sector Performance Ranking
1. TMT - Strong deal activity and positive sentiment.
2. Healthcare - Focus on infrastructure expansion and technology integration.
3. Energy - Mixed performance with significant acquisitions but regulatory challenges.
4. Consumer - Limited deal activity but stable growth prospects.
5. Industry - Struggles with regulatory scrutiny and economic volatility.

@@@ Market Implications
- The week's activity sets a positive tone for continued M&A in the TMT sector, with potential for further consolidation in Healthcare.
- Investors should remain vigilant regarding regulatory developments that may impact deal-making and valuations, particularly in the energy and healthcare sectors.

@@@ Risks & Opportunities
- **Risks: Regulatory scrutiny and economic uncertainties could hinder M&A activity and impact market valuations.**
- **Opportunities: High-growth sectors such as TMT and Healthcare present attractive investment opportunities, particularly in AI and technology-driven solutions.**

In conclusion, the US market is navigating a complex landscape characterized by both opportunities and challenges. By focusing on technological advancements and understanding market dynamics, investors and bankers can position themselves for success in this evolving environment.
    END OF SYSTEM PROMPT
    """
    
	return manual

def main():
   week_end_date : datetime = datetime.now()
   end : str = week_end_date.strftime("%Y-%m-%d")

   week_start_date : datetime = week_end_date - timedelta(days=7)
   start : str = week_start_date.strftime("%Y-%m-%d")
	
   regions = ["US", "Europe", "APAC"]
   for region in regions:
      system_prompt = build_weekly_system_prompt("US", start, end)
      messages = [{'role' : 'system', 'content' : system_prompt}, {'role' : 'user', 'content' : f'Please generate the report as per the specifications stated in the system prompt'}]

      customHttpXClient = httpx.Client(timeout=httpx.Timeout(120.0), # 120 s for connect/read/write/pool
                                                limits=httpx.Limits(max_connections=5, max_keepalive_connections=5))

      openai_client = openai.Client(api_key=OPENAI_API_KEY, http_client=customHttpXClient)
      
      print(f"Generating report for {region}...")
      response = openai_client.chat.completions.create(
                           model = "gpt-4o-mini",
                           messages = messages,
                           temperature=0.2
                     ).choices[0].message.content
      print("Got report")

      with open(f"{region}_Recap_{start}_raw.txt", "w", encoding="utf-8") as file:
         file.write(response)         
		 
      format_brief(analysis = response, output_dir = recap_dir, sector = "ALL", mode = "Recap")
   return 

if __name__ == "__main__":
    main()