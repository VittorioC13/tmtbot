from pathlib import Path
from report_generator import *
from pdf_report import *


base_path = Path(__file__).resolve().parent.parent 
raw_dir = base_path / 'api' / "static" / "assets" / "raw"
json_path = base_path/ 'term_definitions.json'
brief_dir = base_path / 'api' / 'static' / 'assets' / 'briefs'
section1Prompt = """
1. RECENT TMT M&A ACTIVITY

CRITICAL: Focus on ONLY 2 of the most significant M&A deals, IPOs, or major transactions from the provided news items. Prioritize deals with the most detailed financial information and market impact.

For each of the 2 selected deals, provide comprehensive analysis with the following structured information:

**Deal Analysis Structure:**
- **Deal Size:** [USD amount - provide specific numbers when available, estimate based on comparable deals if not specified]
- **Valuation Multiples:** [Detailed analysis of EV/EBITDA, P/E, or other relevant multiples with industry context and comparison to peers]
- **Companies:** [Buyer] acquiring [Target] - include company descriptions and market positions
- **Date Announced:** [Specific date if mentioned, or approximate timeline]
- **Strategic Rationale:** [In-depth analysis of the strategic logic, including market positioning, synergies, competitive advantages, and long-term strategic vision]
- **Risk Analysis:** [Comprehensive risk assessment including integration risks, regulatory challenges, market risks, execution risks, and potential value destruction scenarios]

**Analysis Requirements:**
- Provide specific valuation multiples with industry benchmarks and peer comparisons
- Include detailed rationale with strategic context and market implications
- Conduct thorough risk analysis with specific risk factors and mitigation strategies
- Use concrete data points and financial metrics wherever possible
- Focus on deals with the most significant TMT sector impact and detailed financial information

**Format:**
Use ### as start of sections
Use **title:** as start of subsections
Use - ** as bullet points
When adding links, use this EXACT format: **Link title** ([Link](https://linkURL))

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

**Deal 2: [Company Name] Acquisition**
[Same detailed structure as Deal 1]

Focus on quality over quantity - provide deep, data-driven analysis of only 2 deals rather than superficial coverage of many deals.
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

For each deal mentioned in Section 1, provide ONE specific reading material and explain why it matters.

**Format for each deal:**
**Deal Name:** [Specific deal from Section 1]
**Reading Material:** [Book/Article/Resource name]
**Why This Matters:** [Clear explanation of how this reading helps understand the deal]
  
**Example:**
**Deal Name:** Revolut's $1B Funding Round
**Reading Material:** "Venture Deals" by Brad Feld
**Why This Matters:** This book explains how Series A/B/C valuations work, which is exactly what happened in Revolut's funding round. You'll learn how to calculate the $65B valuation and understand why fintech companies get such high multiples.

Keep it simple and direct - one deal, one reading, one clear explanation of why it matters.
"""




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


def generate_daily_brief(analyzer, prompts, brief_path):
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
            txtFileName = f"TMT_Brief_{str(datetime.now().strftime('%Y-%m-%d'))}_raw.txt"
            with open(raw_dir/txtFileName, "w") as file:
                file.write(analysis)
            print(f"file created as {file.name}")
            
            print("requesting gpt3.5 for technical terms definitions")
            if not analyzer.detect_technical_terms(analysis):
                raise Exception
        
            print("Formatting report...")
            filename = format_brief(analysis, brief_path)
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
        brief_path = generate_daily_brief(analyzer, prompts, brief_dir)
        
        print(f"\nAnalysis completed successfully!")
        print(f"Focused brief saved to: {brief_path}")
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        if "insufficient_quota" in str(e):
            print("Please set up billing at platform.openai.com/account/billing")

if __name__ == "__main__":
    main() 
