from pathlib import Path
from report_generator import *
from pdf_report import *


base_path = Path(__file__).resolve().parent.parent 
raw_dir = base_path / 'api' / "static" / "assets" / "raw"
json_path = base_path/ 'term_definitions.json'
section1Prompt = """
1. RECENT TMT M&A ACTIVITY

CRITICAL: Include actual M&A deals, IPOs, or significant transactions that are mentioned in the provided news items. The news covers the past week, so focus on the most recent and significant deals.

- If significant M&A deals, IPOs, or major transactions are found in the news items, list them with the following structured information with clear headings:
  
  Deal Size: [USD amount - only if explicitly mentioned in news]
  Valuation Multiples: [EV/EBITDA or P/E if available in news, or estimated based on news data]
  Companies: [Buyer] acquiring [Target] - only use actual company names from news
  Date Announced: [Date - only if mentioned in news]
  Rationale: [Market share, synergies, geographic expansion, etc. - based on news content]
  Risk: [Short paragraph on key risks - based on news analysis]
  
  If the deal is actually an IPO, provide IPO-specific information instead:
  IPO Rationale: [Reason for listing - from news]
  Valuation: [Expected valuation - only if mentioned in news]
  Pricing Range: [Expected pricing range - only if mentioned in news]
  Timing: [Expected IPO timing - only if mentioned in news]
  
- If no significant recent deals are found, include a brief summary of notable M&A trends or market activity from the past week based on the news content
- Ensure each deal has all required fields with clear headings for parsing
- If any field information is not available in the news, state "Not specified in news" rather than making up data
- Always cite the specific news source when providing deal information
- Focus on deals that are most relevant to the TMT sector and have significant market impact

Use ### as start of sections
Use **title:** as start of subsections
use - ** as bullet points
When adding links, use this EXACT format (especially note: do not add - in front of links)
**Link title** ([Link](https://linkURL))  

Follow this example as template:
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

Do not include a recommended reading subsection here
"""

section2Prompt = """
2. MARKET DYNAMICS & SENTIMENT

(Provide a multi-paragraph, in-depth analysis)
- Overall TMT sector sentiment, with breakdowns by subsector, geography, and deal type
- Key market drivers and headwinds, with supporting data
- Subsector performance analysis (e.g., software, media, telecom, fintech, AI)
- Trading multiples trends, with specific numbers and comparisons
- Notable investor/analyst reactions, with quotes or examples
- Actionable insights for bankers and investors"""

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
- Actionable insights for team management and business development"""

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
- Actionable insights for clients and bankers"""

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
- Provide actionable insights for bankers and investors regarding trend-driven opportunities"""

section6Prompt = """
6. RECOMMENDED READINGS

(For Finance Beginners)
- Based on the specific deals and trends identified in this report, provide educational resources that directly connect to today's market events
- For each major deal or trend mentioned in sections 1-5, recommend specific resources that explain the underlying concepts
- Structure recommendations as follows:
  
  **For each deal/trend identified:**
  [Deal/Trend Name]: [Brief description of what happened]
  → **Why this matters:** [Explain the broader significance]
  → **Read this to understand:** [Specific resource with direct connection]
  → **Key concept to learn:** [What specific finance concept this deal illustrates]
  
  **Example format:**
  "Revolut's $1B Funding Round"
  → **Why this matters:** Shows how fintech valuations work in current market conditions
  → **Read this to understand:** "Venture Deals" by Brad Feld - Chapter 8 on valuation methods
  → **Key concept to learn:** How to calculate and interpret Series A/B/C valuations
  
- Include specific connections like:
  * If a deal mentions "EV/EBITDA multiple of 15x" → Recommend "Valuation" by McKinsey Chapter 3
  * If AI companies are acquiring → Recommend "The Innovator's Dilemma" by Clayton Christensen
  * If fintech IPOs are mentioned → Recommend "The Psychology of Money" by Morgan Housel
  * If blockchain deals appear → Recommend "Digital Gold" by Nathaniel Popper
- Provide 3-5 specific recommendations that directly relate to today's news
- Explain exactly how each resource helps understand the specific deals mentioned"""




#this matrix stores necessary information needed to issue api calls, compositions are as follows
#[section_specific_prompt, context_from_news_api, max_tokens]
prompts = [
    [section1Prompt, None, 2500],
    [section2Prompt, None, 1800],
    [section3Prompt, None, 1500],
    [section4Prompt, None, 1200],
    [section5Prompt, None, 700],
    [section6Prompt, None, 400]
]


def generate_daily_brief(analyzer, prompts):
        """Generate a comprehensive daily briefing"""
        try:
            print("Collecting news articles...")
            news = analyzer.collect_news()
            if not news:
                raise Exception("No news articles found")
            
            print(f"Analyzing the news articles...")
            analysis = analyzer.analyze_news(news, prompts, 5) 
            if not analysis:
                raise Exception("Failed to generate analysis")
            
            print("Storing API output into txt file...")
            txtFileName = f"TMT_Brief_{str(datetime.now().strftime("%Y-%m-%d"))}_raw.txt"
            with open(raw_dir/txtFileName, "w") as file:
                file.write(analysis)
            print(f"file created as {file.name}")
            
            print("requesting gpt3.5 for technical terms definitions")
            if not analyzer.detect_technical_terms(analysis):
                raise Exception
        
            print("Formatting report...")
            filename = format_brief(analysis)
            return filename
            
        except Exception as e:
            print(f"Error generating brief: {str(e)}")
            raise

def main():
    """Main execution function"""
    try:
        # Initialize the analyzer
        analyzer = IBDMarketAnalyst()
        
        # Generate the brief
        brief_path = generate_daily_brief(analyzer, prompts)
        
        print(f"\nAnalysis completed successfully!")
        print(f"Focused brief saved to: {brief_path}")
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        if "insufficient_quota" in str(e):
            print("Please set up billing at platform.openai.com/account/billing")

if __name__ == "__main__":
    main() 
