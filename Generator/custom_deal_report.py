#!/usr/bin/env python3
"""
Custom Deal Report Generator for TMT BOT
Creates PDF reports for specific deals using the same formatting as daily briefs
"""

from pathlib import Path
from datetime import datetime
from pdf_report import format_brief
import openai
import os
import re
from config import OPENAI_API_KEY

class CustomDealReporter:
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
    
    def generate_exxon_pioneer_report(self):
        """Generate a comprehensive report for ExxonMobil & Pioneer Natural Resources merger"""
        
        # Deal information
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
        
        # Create the analysis using GPT
        analysis = self._generate_analysis(deal_info)
        
        # Generate PDF using the existing format_brief function
        today = datetime.now().strftime("%Y-%m-%d")
        pdf_path = format_brief(analysis, self.brief_dir, "Energy", "US")
        
        return pdf_path
    
    def _generate_analysis(self, deal_info):
        """Generate comprehensive analysis using GPT or mock data"""
        
        if not self.openai_client:
            return self._generate_mock_analysis(deal_info)
        
        system_message = """You are a senior Investment Banking MD specializing in Energy M&A.
        Provide precise, data-driven analysis with concrete examples, bullet points, and professional formatting.
        Focus on strategic rationale, financial implications, and market context.
        When adding links, use this EXACT format: **Link title** ([Link](https://linkURL))
        """
        
        user_prompt = f"""
        Analyze the following major energy sector merger and provide a comprehensive investment banking report:

        **Deal Details:**
        - **Buyer:** {deal_info['buyer']}
        - **Target:** {deal_info['target']}
        - **Deal Value:** {deal_info['deal_value']}
        - **Share Price:** {deal_info['share_price']}
        - **Exchange Ratio:** {deal_info['exchange_ratio']}
        - **Total Enterprise Value:** {deal_info['enterprise_value']}
        - **Announcement Date:** {deal_info['announcement_date']}
        - **Transaction Type:** {deal_info['transaction_type']}
        - **Source:** {deal_info['source_url']}

        **Required Analysis Structure:**

        ### 1. DEAL OVERVIEW & FINANCIAL METRICS
        Provide comprehensive deal summary including:
        - **Deal Size:** {deal_info['deal_value']} - classify as Small cap (<$2B), Mid cap ($2B-$10B), Large cap (>$10B)
        - **Deal Type:** Classify as Horizontal/Vertical/Tuck-in&Bolt-on/Carve-out/Conglomerate
        - **Valuation Multiples:** Analyze EV/EBITDA, P/E, or other relevant multiples with industry context
        - **Strategic Rationale:** In-depth analysis of strategic logic, synergies, competitive advantages
        - **Risk Analysis:** Integration risks, regulatory challenges, market risks, execution risks

        ### 2. STRATEGIC RATIONALE & MARKET POSITIONING
        Analyze:
        - Strategic logic behind the merger
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
        - Energy sector trends and implications
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
    
    def _generate_mock_analysis(self, deal_info):
        """Generate mock analysis when OpenAI API is not available"""
        
        return f"""
### 1. DEAL OVERVIEW & FINANCIAL METRICS

**Deal Size:** {deal_info['deal_value']} - Large cap (>$10B)
**Deal Size Category:** Large cap (>$10B)
**Deal Type:** Horizontal merger (both companies in upstream oil & gas exploration and production)

**Valuation Multiples:**
- **EV/EBITDA:** ~8.5x (based on Pioneer's 2023 EBITDA of ~$7.6B)
- **P/E Ratio:** ~12.3x (based on Pioneer's 2023 earnings)
- **Premium to Market:** ~18% premium to Pioneer's 30-day VWAP

**Companies:** {deal_info['buyer']} acquiring {deal_info['target']}
- **ExxonMobil:** Integrated oil & gas major with global operations, market cap ~$400B
- **Pioneer Natural Resources:** Leading Permian Basin producer, market cap ~$50B

**Date Announced:** {deal_info['announcement_date']}

**Strategic Rationale:**
- **Scale & Efficiency:** Creates largest Permian Basin operator with ~1.4M boe/d production
- **Cost Synergies:** Expected $2B+ in annual cost savings through operational efficiencies
- **Technology Integration:** Combines ExxonMobil's advanced technology with Pioneer's Permian expertise
- **ESG Positioning:** Strengthens ExxonMobil's energy transition capabilities

**Risk Analysis:**
- **Integration Risk:** Large-scale merger execution across complex operations
- **Regulatory Risk:** Potential antitrust scrutiny given market concentration
- **Market Risk:** Oil price volatility affecting deal economics
- **Execution Risk:** Operational disruption during integration period

### 2. STRATEGIC RATIONALE & MARKET POSITIONING

**Strategic Logic:**
The merger represents ExxonMobil's strategic pivot to focus on high-return, low-cost assets in the Permian Basin, the most prolific oil-producing region in the US. This transaction positions the combined entity as the dominant player in the Permian, with significant operational and cost advantages.

**Market Positioning Implications:**
- **Permian Dominance:** Combined entity will control ~15% of total Permian production
- **Cost Leadership:** Lowest-cost producer in the basin with significant scale advantages
- **Technology Leadership:** Advanced drilling and completion techniques across larger acreage position

**Synergy Potential:**
- **Operational Synergies:** $2B+ annual cost savings through:
  - Reduced drilling costs through scale and efficiency
  - Optimized logistics and infrastructure utilization
  - Streamlined administrative functions
- **Revenue Synergies:** Enhanced marketing and trading capabilities
- **Technology Synergies:** Advanced recovery techniques and digital optimization

### 3. FINANCIAL IMPACT & VALUATION ANALYSIS

**Revenue Analysis:**
| Metric | Pioneer (2023) | Combined Entity (Pro Forma) |
| --- | --- | --- |
| Revenue | $19.2B | $47.8B |
| EBITDA | $7.6B | $18.2B |
| Net Income | $4.9B | $11.8B |
| Production (boe/d) | 711K | 1.4M |

**Profitability Metrics:**
- **EBITDA Margin:** Pioneer 39.6% vs. Industry Average 35.2%
- **ROE:** Pioneer 18.4% vs. Industry Average 12.1%
- **Cash Flow per Share:** Pioneer $24.50 vs. Industry Average $18.20

**Leverage Analysis:**
- **Net Debt/EBITDA:** Combined entity ~1.2x (conservative leverage profile)
- **Interest Coverage:** >15x (strong credit profile)
- **Credit Rating:** Expected to maintain ExxonMobil's AA- rating

### 4. REGULATORY & RISK ASSESSMENT

**Regulatory Approval Requirements:**
- **FTC Review:** Hart-Scott-Rodino Act filing required
- **State Approvals:** Texas and New Mexico regulatory approvals
- **Shareholder Approval:** Both companies require majority shareholder approval

**Antitrust Considerations:**
- **Market Concentration:** Combined entity will have significant Permian market share
- **Competitive Impact:** Potential concerns about reduced competition
- **Remedies:** Possible divestiture requirements for overlapping assets

**Integration Risks:**
- **Operational Disruption:** Risk of production delays during integration
- **Cultural Integration:** Combining different corporate cultures and systems
- **Technology Integration:** Merging different operational and IT systems

### 5. MARKET DYNAMICS & SECTOR IMPLICATIONS

**Energy Sector Trends:**
- **Consolidation Wave:** Continued M&A activity in upstream oil & gas sector
- **ESG Focus:** Increased emphasis on environmental and social responsibility
- **Technology Adoption:** Digital transformation and automation in operations

**Peer Company Reactions:**
- **Chevron:** Likely to pursue similar consolidation strategies
- **ConocoPhillips:** May accelerate Permian-focused acquisitions
- **EOG Resources:** Could become acquisition target or pursue defensive M&A

**Market Sentiment:**
- **Investor Response:** Positive initial market reaction with both stocks up 5-8%
- **Analyst Upgrades:** Multiple upgrades to "Buy" ratings on both companies
- **Credit Rating:** S&P and Moody's maintain stable outlook

### 6. RECOMMENDED READINGS

**ExxonMobil Announces Merger with Pioneer Natural Resources** ([Link]({deal_info['source_url']}))

**Energy Sector M&A Trends 2023** ([Link](https://www.mckinsey.com/industries/oil-and-gas/our-insights/the-future-of-oil-and-gas-in-a-net-zero-world))

**Permian Basin Production Analysis** ([Link](https://www.eia.gov/petroleum/drilling/))

**Oil & Gas M&A Market Outlook** ([Link](https://www.pwc.com/us/en/industries/energy-utilities-mining/oil-gas-mergers-acquisitions.html))
"""
    
    def _create_custom_pdf(self, analysis, filename, file_header, deal_info):
        """Create PDF with custom formatting for deal reports"""
        
        from pdf_report import PDF
        
        # Create PDF using the custom PDF class
        pdf = PDF()
        pdf.set_margins(15, 15, 15)
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_title(file_header)
        pdf.set_context(sector="Energy", region="US")
        pdf.add_page()
        
        # Header with deal info
        pdf.set_font('Helvetica', 'B', 16)
        pdf.cell(0, 12, file_header, 0, 1, 'C')
        
        pdf.set_font('Helvetica', 'I', 11)
        pdf.cell(0, 6, f"{deal_info['buyer']} & {deal_info['target']} Merger Analysis", 0, 1, 'C')
        
        # Deal summary box
        pdf.ln(10)
        pdf.set_fill_color(240, 240, 240)
        pdf.set_font('Helvetica', 'B', 12)
        pdf.cell(0, 8, "Deal Summary", 0, 1, 'L', fill=True)
        pdf.set_font('Helvetica', '', 10)
        
        summary_items = [
            f"Deal Value: {deal_info['deal_value']}",
            f"Enterprise Value: {deal_info['enterprise_value']}",
            f"Announcement Date: {deal_info['announcement_date']}",
            f"Transaction Type: {deal_info['transaction_type']}"
        ]
        
        for item in summary_items:
            pdf.cell(0, 5, item, 0, 1, 'L')
        
        pdf.ln(5)
        
        # Process the analysis content
        self._process_analysis_content(analysis, pdf)
        
        # Save PDF
        pdf_path = self.brief_dir / filename
        pdf.output(str(pdf_path))
        
        return pdf_path
    
    def _process_analysis_content(self, analysis, pdf):
        """Process analysis content and format for PDF"""
        
        # Split into sections
        sections = re.split(r"(?m)(?=^###\s*\d+\.)", analysis)
        
        for section in sections:
            if not section.strip():
                continue
            
            first_line = section.lstrip().split('\n', 1)[0]
            
            # Main sections (### 1. etc.)
            if re.match(r'^###\s*\d+\.', first_line):
                title = first_line.replace('###', '').strip()
                pdf.chapter_title(title)
                
                body = section.split('\n', 1)[1] if '\n' in section else ''
                if body.strip():
                    self._process_section_body(body, pdf)
            else:
                self._process_section_body(section, pdf)
    
    def _process_section_body(self, content, pdf):
        """Process section body content"""
        
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Bold lines (@@@)
            if line.startswith('@@@'):
                pdf.bold_line(line[4:])
            # Bullet points
            elif line.startswith('- **'):
                # Extract bold part and regular text
                match = re.match(r'-\s*\*\*(.+?)\*\*:\s*(.*)', line)
                if match:
                    bold_part, text_part = match.groups()
                    pdf.bullet_point(f"{bold_part}: {text_part}")
                else:
                    pdf.bullet_point(line[2:])
            # Subsection titles
            elif line.startswith('####'):
                pdf.subsection_title(line[5:])
            # Regular text
            else:
                pdf.chapter_body(line)

def main():
    """Main function to generate the ExxonMobil & Pioneer deal report"""
    try:
        reporter = CustomDealReporter()
        pdf_path = reporter.generate_exxon_pioneer_report()
        print(f"✓ Deal report generated successfully!")
        print(f"✓ Report saved to: {pdf_path}")
        return pdf_path
    except Exception as e:
        print(f"Error generating deal report: {str(e)}")
        raise

if __name__ == "__main__":
    main()
