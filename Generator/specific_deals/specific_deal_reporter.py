#!/usr/bin/env python3
"""
Specific Deal Report Generator for TMT BOT
Creates PDF reports for specific deals with custom naming and dedicated folder
"""

from pathlib import Path
from datetime import datetime
import sys
import os
import re
import openai

# Add parent directory to path to import modules
sys.path.append(str(Path(__file__).resolve().parent.parent))
from pdf_report import format_brief
from config import OPENAI_API_KEY

class SpecificDealReporter:
    def __init__(self):
        # Try to get API key from environment or config
        api_key = os.environ.get("OPENAI_API") or OPENAI_API_KEY
        if not api_key:
            print("Warning: No OpenAI API key found. Using mock analysis.")
            self.openai_client = None
        else:
            self.openai_client = openai.Client(api_key=api_key)
        
        self.base_path = Path(__file__).resolve().parent.parent 
        # Create specific deals directory
        self.deals_dir = Path(__file__).resolve().parent
        self.deals_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_deal_report(self, deal_info, sector="Energy", region="US"):
        """Generate a comprehensive report for any specific deal"""
        
        # Create the analysis using GPT or mock data
        analysis = self._generate_analysis(deal_info, sector)
        
        # Generate PDF using the existing format_brief function
        pdf_path = format_brief(analysis, self.deals_dir, sector, region)
        
        # Rename the file to include deal name
        deal_name = self._create_deal_name(deal_info)
        new_filename = f"{deal_name}_Deal_Report_{datetime.now().strftime('%Y-%m-%d')}.pdf"
        new_pdf_path = self.deals_dir / new_filename
        
        # Rename the file
        if pdf_path.exists():
            pdf_path.rename(new_pdf_path)
            return new_pdf_path
        else:
            return pdf_path
    
    def _create_deal_name(self, deal_info):
        """Create a clean deal name for filename"""
        buyer = deal_info.get('buyer', 'Unknown').replace(' ', '_').replace('.', '').replace(',', '')
        target = deal_info.get('target', 'Unknown').replace(' ', '_').replace('.', '').replace(',', '')
        
        # Clean up common company suffixes
        buyer = re.sub(r'_(Inc|Corp|Corporation|Company|Ltd|Limited)$', '', buyer)
        target = re.sub(r'_(Inc|Corp|Corporation|Company|Ltd|Limited)$', '', target)
        
        return f"{buyer}_and_{target}"
    
    
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
        """Generate mock analysis using the EXACT same format as daily briefs"""
        
        return f"""
### 1. RECENT {sector.upper()} M&A ACTIVITY

**Deal 1: {deal_info.get('buyer', 'N/A')} Acquisition of {deal_info.get('target', 'N/A')}**
**{deal_info.get('buyer', 'N/A')} Announces {deal_info.get('transaction_type', 'Merger')} with {deal_info.get('target', 'N/A')}** ([Link]({deal_info.get('source_url', 'N/A')}))
- **Deal Size:** {deal_info.get('deal_value', 'N/A')} (Large cap >$10B)
- **Valuation Multiples:** EV/EBITDA of 8.5x (vs industry average of 12.3x), P/E of 12.3x
- **Companies:** {deal_info.get('buyer', 'N/A')} is a leading {sector} company with global operations, while {deal_info.get('target', 'N/A')} is a specialized {sector} company with strong market position in key regions
- **Date Announced:** {deal_info.get('announcement_date', 'N/A')}
- **Strategic Rationale:** The transaction creates the largest {sector} operator with significant production capacity and expected $2B+ in annual cost savings through operational efficiencies. The deal combines buyer's advanced technology with target's expertise, strengthening the combined entity's market leadership position
- **Risk Analysis:** Integration risks include large-scale transaction execution across complex operations, potential antitrust scrutiny given market concentration, sector volatility affecting deal economics, and operational disruption during integration period
- **Key Financials Analysis:** Combined entity will generate pro forma revenue of $47.8B with EBITDA of $18.2B, representing significant scale advantages and improved operational efficiency

**Profitability Metrics:**
| Metric | Pioneer (2023) | Combined Entity (Pro Forma) | Industry Average |
| --- | --- | --- | --- |
| Revenue | $19.2B | $47.8B | $25.1B |
| EBITDA | $7.6B | $18.2B | $8.9B |
| Net Income | $4.9B | $11.8B | $5.2B |
| EBITDA Margin | 39.6% | 38.1% | 35.4% |
| Net Income Margin | 25.5% | 24.7% | 20.7% |
| ROE | 18.4% | 16.8% | 12.1% |
| Production (boe/d) | 711K | 1.4M | 850K |

**Valuation Multiples Analysis:**
| Multiple | Pioneer | Combined Entity | Industry Average | Premium/Discount |
| --- | --- | --- | --- | --- |
| EV/EBITDA | 8.5x | 8.2x | 12.3x | -33% |
| P/E Ratio | 12.3x | 11.8x | 15.2x | -22% |
| EV/Revenue | 3.4x | 3.2x | 4.1x | -22% |
| Price/Book | 2.1x | 2.0x | 2.8x | -29% |

**Leverage Analysis:**
| Metric | Pioneer | Combined Entity | Industry Average |
| --- | --- | --- | --- |
| Net Debt/EBITDA | 1.2x | 1.1x | 2.3x |
| Interest Coverage | 15.2x | 18.5x | 8.1x |
| Debt-to-Equity | 0.3x | 0.2x | 0.8x |
| Credit Rating | A- | AA- | BBB+ |

### 2. MARKET DYNAMICS & SENTIMENT

The {sector} sector is currently experiencing positive sentiment, characterized by strong consolidation activity and strategic positioning for long-term growth. The overall sentiment is influenced by various factors, including market consolidation trends, operational efficiency gains, and sector-specific developments.

@@@ Subsector Breakdown:
- **{sector} Operations:** The {sector} sector remains robust, driven by strategic consolidation and operational efficiency improvements. Companies are focusing on scale advantages and cost optimization through M&A activity
- **Technology Integration:** Advanced technology adoption is driving operational improvements and cost reductions across the sector
- **Market Positioning:** Companies are strategically positioning themselves for long-term competitive advantages through strategic acquisitions

#### Key Market Drivers and Headwinds

@@@ Drivers:
- **Consolidation Activity:** Continued M&A activity in {sector} sector is driving operational efficiency and market consolidation
- **Technology Adoption:** Digital transformation and automation in operations are improving efficiency and reducing costs
- **Scale Advantages:** Larger operations provide significant cost advantages and market positioning benefits

@@@ Headwinds:
- **Regulatory Scrutiny:** Increased regulatory scrutiny poses risks to M&A activities and market valuations
- **Economic Uncertainty:** Global economic conditions may impact sector performance and investment decisions

#### Trading Multiples Trends

@@@ Valuation Multiples: The average EV/EBITDA multiple for the {sector} sector is approximately 12.3x, with notable variations:

**Sector Trading Multiples:**
| Company Type | EV/EBITDA | P/E Ratio | EV/Revenue | Price/Book |
| --- | --- | --- | --- | --- |
| Large Cap {sector} | 8.5x | 12.3x | 3.2x | 2.0x |
| Mid Cap {sector} | 10.2x | 14.8x | 3.8x | 2.4x |
| Small Cap {sector} | 15.1x | 18.9x | 4.5x | 3.1x |
| Industry Average | 12.3x | 15.2x | 3.8x | 2.5x |

**Performance Metrics by Subsector:**
| Subsector | Revenue Growth | EBITDA Margin | ROE | Debt/EBITDA |
| --- | --- | --- | --- | --- |
| Upstream {sector} | 8.2% | 38.1% | 16.8% | 1.1x |
| Midstream {sector} | 5.4% | 42.3% | 14.2% | 3.2x |
| Downstream {sector} | 3.1% | 28.7% | 11.5% | 2.8x |
| Integrated {sector} | 6.8% | 35.4% | 13.9% | 1.8x |

### 3. BANKING PIPELINE

The {sector} sector banking pipeline remains active with several high-profile transactions in various stages of completion. Investment banks are seeing increased activity in strategic M&A, with focus on operational synergies and market consolidation.

@@@ Active Deals:
- **Strategic M&A:** Multiple strategic acquisitions in the {sector} sector are in various stages of completion
- **Operational Synergies:** Deals are focusing on operational efficiency gains and cost reduction opportunities
- **Market Consolidation:** Continued consolidation activity is expected to drive further M&A opportunities

### 4. STAKEHOLDER IMPACT & FORWARD-LOOKING ANALYSIS

The {deal_info.get('buyer', 'N/A')} and {deal_info.get('target', 'N/A')} transaction will have significant impact on various stakeholders, including shareholders, employees, customers, and the broader {sector} sector.

@@@ Shareholder Impact:
- **Value Creation:** The transaction is expected to create significant value through operational synergies and market positioning
- **Risk Mitigation:** Diversified operations and improved scale provide risk mitigation benefits
- **Growth Opportunities:** Combined entity will have enhanced growth opportunities and market positioning

@@@ Employee Impact:
- **Integration Challenges:** Successful integration will be critical for realizing synergies and maintaining operational efficiency
- **Cultural Integration:** Combining different corporate cultures and systems will require careful management
- **Operational Efficiency:** Streamlined operations will improve efficiency and reduce costs

### 5. {sector.upper()} TRENDS

The {sector} sector is experiencing several key trends that are shaping the industry landscape and driving strategic decisions.

@@@ Key Trends:
- **Consolidation Wave:** Continued M&A activity is driving market consolidation and operational efficiency
- **Technology Integration:** Advanced technology adoption is improving operational efficiency and reducing costs
- **ESG Focus:** Increased emphasis on environmental and social responsibility is shaping strategic decisions
- **Operational Efficiency:** Companies are focusing on operational efficiency gains and cost reduction opportunities

@@@ Future Outlook:
- **Continued Consolidation:** Further consolidation activity is expected in the {sector} sector
- **Technology Adoption:** Advanced technology adoption will continue to drive operational improvements
- **Strategic Positioning:** Companies will continue to focus on strategic positioning for long-term competitive advantages

### 6. RECOMMENDED READINGS

**{deal_info.get('buyer', 'N/A')} Announces {deal_info.get('transaction_type', 'Merger')} with {deal_info.get('target', 'N/A')}** ([Link]({deal_info.get('source_url', 'N/A')}))

**{sector.upper()} Sector M&A Trends 2023** ([Link](https://www.mckinsey.com/industries/energy/our-insights/sector-trends))

**Market Analysis Report** ([Link](https://www.eia.gov/sector-analysis/))

**M&A Market Outlook** ([Link](https://www.pwc.com/us/en/industries/mergers-acquisitions.html))
"""

def main():
    """Main function to generate a specific deal report"""
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
        
        reporter = SpecificDealReporter()
        pdf_path = reporter.generate_deal_report(deal_info, sector="Energy", region="US")
        print(f"✓ Specific deal report generated successfully!")
        print(f"✓ Report saved to: {pdf_path}")
        return pdf_path
    except Exception as e:
        print(f"Error generating specific deal report: {str(e)}")
        raise

if __name__ == "__main__":
    main()
