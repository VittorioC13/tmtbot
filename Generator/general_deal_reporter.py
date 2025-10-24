#!/usr/bin/env python3
"""
General Deal Report Generator for TMT BOT
Creates PDF reports for specific deals using the same formatting as daily briefs
"""

from pathlib import Path
from datetime import datetime
from pdf_report import format_brief
import openai
import os
import re
from config import OPENAI_API_KEY

class GeneralDealReporter:
    def __init__(self):
        # Try to get API key from environment or config
        api_key = os.environ.get("OPENAI_API") or OPENAI_API_KEY
        if not api_key:
            print("Warning: No OpenAI API key found. Using mock analysis.")
            self.openai_client = None
        else:
            self.openai_client = openai.Client(api_key=api_key)
        
        self.base_path = Path(__file__).resolve().parent.parent 
        self.brief_dir = self.base_path / 'api' / 'static' / 'assets' / 'briefs'
        self.brief_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_deal_report(self, deal_info, sector="Energy", region="US"):
        """Generate a comprehensive report for any deal"""
        
        # Create the analysis using GPT or mock data
        analysis = self._generate_analysis(deal_info, sector)
        
        # Generate PDF using the existing format_brief function
        pdf_path = format_brief(analysis, self.brief_dir, sector, region)
        
        return pdf_path
    
    def _generate_analysis(self, deal_info, sector):
        """Generate comprehensive analysis using GPT or mock data"""
        
        if not self.openai_client:
            return self._generate_mock_analysis(deal_info, sector)
        
        system_message = f"""You are a senior Investment Banking MD specializing in {sector} M&A.
        Provide precise, data-driven analysis with concrete examples, bullet points, and professional formatting.
        Focus on strategic rationale, financial implications, and market context.
        When adding links, use this EXACT format: **Link title** ([Link](https://linkURL))
        """
        
        user_prompt = f"""
        Analyze the following major {sector} sector transaction and provide a comprehensive investment banking report:

        **Deal Details:**
        - **Buyer:** {deal_info.get('buyer', 'N/A')}
        - **Target:** {deal_info.get('target', 'N/A')}
        - **Deal Value:** {deal_info.get('deal_value', 'N/A')}
        - **Share Price:** {deal_info.get('share_price', 'N/A')}
        - **Exchange Ratio:** {deal_info.get('exchange_ratio', 'N/A')}
        - **Total Enterprise Value:** {deal_info.get('enterprise_value', 'N/A')}
        - **Announcement Date:** {deal_info.get('announcement_date', 'N/A')}
        - **Transaction Type:** {deal_info.get('transaction_type', 'N/A')}
        - **Source:** {deal_info.get('source_url', 'N/A')}

        **Required Analysis Structure:**

        ### 1. DEAL OVERVIEW & FINANCIAL METRICS
        Provide comprehensive deal summary including:
        - **Deal Size:** {deal_info.get('deal_value', 'N/A')} - classify as Small cap (<$2B), Mid cap ($2B-$10B), Large cap (>$10B)
        - **Deal Type:** Classify as Horizontal/Vertical/Tuck-in&Bolt-on/Carve-out/Conglomerate
        - **Valuation Multiples:** Analyze EV/EBITDA, P/E, or other relevant multiples with industry context
        - **Strategic Rationale:** In-depth analysis of strategic logic, synergies, competitive advantages
        - **Risk Analysis:** Integration risks, regulatory challenges, market risks, execution risks

        ### 2. STRATEGIC RATIONALE & MARKET POSITIONING
        Analyze:
        - Strategic logic behind the transaction
        - Market positioning implications
        - Synergy potential and cost savings
        - Competitive landscape impact
        - Long-term strategic vision

        ### 3. FINANCIAL IMPACT & VALUATION ANALYSIS
        Include:
        - Revenue and profitability analysis
        - Debt structure and leverage analysis
        - Asset efficiency metrics
        - Valuation context with peer comparisons
        - Capital structure implications

        ### 4. REGULATORY & RISK ASSESSMENT
        Cover:
        - Regulatory approval requirements
        - Antitrust considerations
        - Integration risks
        - Market and execution risks
        - Value destruction scenarios

        ### 5. MARKET DYNAMICS & SECTOR IMPLICATIONS
        Analyze:
        - {sector} sector trends and implications
        - Peer company reactions
        - Market sentiment and investor response
        - Future M&A activity implications

        ### 6. RECOMMENDED READINGS
        Provide relevant industry reports and analysis links

        **Formatting Guidelines:**
        - Use ### for main sections
        - Use #### for subsections  
        - Use **title:** for bullet points
        - Use - ** for bullet points
        - Use @@@ for bold lines
        - Create tables using markdown format
        - Include specific financial metrics and multiples
        - Provide concrete data points and industry benchmarks

        **Important:** Focus on investment banking analysis with specific financial metrics, valuation multiples, and strategic insights. Use professional tone and include relevant industry context.
        """
        
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_prompt}
        ]
        
        response = self.openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=4000,
            temperature=0.3
        )
        
        return response.choices[0].message.content.strip()
    
    def _generate_mock_analysis(self, deal_info, sector):
        """Generate mock analysis when OpenAI API is not available"""
        
        return f"""
### 1. DEAL OVERVIEW & FINANCIAL METRICS

**Deal Size:** {deal_info.get('deal_value', 'N/A')} - Large cap (>$10B)
**Deal Size Category:** Large cap (>$10B)
**Deal Type:** Horizontal merger (both companies in {sector} sector)

**Valuation Multiples:**
- **EV/EBITDA:** ~8.5x (based on target's 2023 EBITDA)
- **P/E Ratio:** ~12.3x (based on target's 2023 earnings)
- **Premium to Market:** ~18% premium to target's 30-day VWAP

**Companies:** {deal_info.get('buyer', 'N/A')} acquiring {deal_info.get('target', 'N/A')}
- **Buyer:** Leading {sector} company with global operations
- **Target:** Specialized {sector} company with strong market position

**Date Announced:** {deal_info.get('announcement_date', 'N/A')}

**Strategic Rationale:**
- **Scale & Efficiency:** Creates largest {sector} operator with significant production capacity
- **Cost Synergies:** Expected $2B+ in annual cost savings through operational efficiencies
- **Technology Integration:** Combines buyer's advanced technology with target's expertise
- **Market Positioning:** Strengthens combined entity's market leadership

**Risk Analysis:**
- **Integration Risk:** Large-scale transaction execution across complex operations
- **Regulatory Risk:** Potential antitrust scrutiny given market concentration
- **Market Risk:** Sector volatility affecting deal economics
- **Execution Risk:** Operational disruption during integration period

### 2. STRATEGIC RATIONALE & MARKET POSITIONING

**Strategic Logic:**
The transaction represents a strategic pivot to focus on high-return, low-cost assets in the {sector} sector. This transaction positions the combined entity as a dominant player with significant operational and cost advantages.

**Market Positioning Implications:**
- **Market Dominance:** Combined entity will control significant market share
- **Cost Leadership:** Lowest-cost producer with significant scale advantages
- **Technology Leadership:** Advanced techniques across larger operations

**Synergy Potential:**
- **Operational Synergies:** $2B+ annual cost savings through:
  - Reduced operational costs through scale and efficiency
  - Optimized logistics and infrastructure utilization
  - Streamlined administrative functions
- **Revenue Synergies:** Enhanced marketing and sales capabilities
- **Technology Synergies:** Advanced techniques and digital optimization

### 3. FINANCIAL IMPACT & VALUATION ANALYSIS

**Revenue Analysis:**
| Metric | Target (2023) | Combined Entity (Pro Forma) |
| --- | --- | --- |
| Revenue | $19.2B | $47.8B |
| EBITDA | $7.6B | $18.2B |
| Net Income | $4.9B | $11.8B |
| Production/Operations | 711K units | 1.4M units |

**Profitability Metrics:**
- **EBITDA Margin:** Target 39.6% vs. Industry Average 35.2%
- **ROE:** Target 18.4% vs. Industry Average 12.1%
- **Cash Flow per Share:** Target $24.50 vs. Industry Average $18.20

**Leverage Analysis:**
- **Net Debt/EBITDA:** Combined entity ~1.2x (conservative leverage profile)
- **Interest Coverage:** >15x (strong credit profile)
- **Credit Rating:** Expected to maintain buyer's strong rating

### 4. REGULATORY & RISK ASSESSMENT

**Regulatory Approval Requirements:**
- **FTC Review:** Hart-Scott-Rodino Act filing required
- **State Approvals:** Relevant state regulatory approvals
- **Shareholder Approval:** Both companies require majority shareholder approval

**Antitrust Considerations:**
- **Market Concentration:** Combined entity will have significant market share
- **Competitive Impact:** Potential concerns about reduced competition
- **Remedies:** Possible divestiture requirements for overlapping assets

**Integration Risks:**
- **Operational Disruption:** Risk of operational delays during integration
- **Cultural Integration:** Combining different corporate cultures and systems
- **Technology Integration:** Merging different operational and IT systems

### 5. MARKET DYNAMICS & SECTOR IMPLICATIONS

**{sector} Sector Trends:**
- **Consolidation Wave:** Continued M&A activity in {sector} sector
- **ESG Focus:** Increased emphasis on environmental and social responsibility
- **Technology Adoption:** Digital transformation and automation in operations

**Peer Company Reactions:**
- **Competitors:** Likely to pursue similar consolidation strategies
- **Industry Players:** May accelerate sector-focused acquisitions
- **Other Targets:** Could become acquisition targets or pursue defensive M&A

**Market Sentiment:**
- **Investor Response:** Positive initial market reaction with both stocks up 5-8%
- **Analyst Upgrades:** Multiple upgrades to "Buy" ratings on both companies
- **Credit Rating:** S&P and Moody's maintain stable outlook

### 6. RECOMMENDED READINGS

**Transaction Announcement** ([Link]({deal_info.get('source_url', 'N/A')}))

**{sector} Sector M&A Trends 2023** ([Link](https://www.mckinsey.com/industries/energy/our-insights/sector-trends))

**Market Analysis Report** ([Link](https://www.eia.gov/sector-analysis/))

**M&A Market Outlook** ([Link](https://www.pwc.com/us/en/industries/mergers-acquisitions.html))
"""

def main():
    """Main function to generate a deal report"""
    try:
        # Example usage for ExxonMobil & Pioneer deal
        deal_info = {
            "buyer": "ExxonMobil Corp.",
            "target": "Pioneer Natural Resources",
            "deal_value": "$59.5 billion",
            "share_price": "$253 per share",
            "exchange_ratio": "2.3234 shares of ExxonMobil for each Pioneer share",
            "enterprise_value": "$64.5 billion",
            "announcement_date": "October 11, 2023",
            "transaction_type": "All-stock merger",
            "source_url": "https://corporate.exxonmobil.com/news/news-releases/2023/1011_exxonmobil-announces-merger-with-pioneer-natural-resources-in-an-all-stock-transaction"
        }
        
        reporter = GeneralDealReporter()
        pdf_path = reporter.generate_deal_report(deal_info, sector="Energy", region="US")
        print(f"✓ Deal report generated successfully!")
        print(f"✓ Report saved to: {pdf_path}")
        return pdf_path
    except Exception as e:
        print(f"Error generating deal report: {str(e)}")
        raise

if __name__ == "__main__":
    main()
