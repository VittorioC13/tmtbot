from newsapi import NewsApiClient
from datetime import datetime, timedelta
import openai
import os
import traceback
from fpdf import FPDF
from config import NEWS_API_KEY, OPENAI_API_KEY, CATEGORIES, NEWS_LOOKBACK_DAYS
import requests

class PDF(FPDF):
    def __init__(self):
        super().__init__()
        # Set margins (left, top, right) in mm
        self.set_margins(15, 15, 15)
        self.set_auto_page_break(auto=True, margin=15)
        self.title = None
        
    def set_title(self, title):
        self.title = title
        
    def header(self):
        """Add header to the page"""
        if self.title:
            # Logo
            self.set_font('Helvetica', 'B', 15)
            self.cell(0, 10, self.title, 0, 1, 'C')
            self.set_font('Helvetica', 'I', 10)
            self.cell(0, 5, 'Technology, Media & Telecommunications Sector', 0, 1, 'C')
            self.ln(10)
        
    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def chapter_title(self, title):
        self.set_font('Helvetica', 'B', 12)
        self.ln(4)
        self.cell(0, 6, title, 0, 1, 'L')
        self.ln(2)
        
    def chapter_body(self, body):
        self.set_font('Helvetica', '', 11)
        # Calculate effective width for text
        effective_width = self.w - 2 * self.l_margin
        self.multi_cell(effective_width, 5, body)
        self.ln(2)

    def bullet_point(self, text):
        self.set_font('Helvetica', '', 11)
        # Calculate effective width for text
        effective_width = self.w - 2 * self.l_margin - 10
        self.cell(5, 5, '-', 0, 0, 'R')
        self.multi_cell(effective_width, 5, ' ' + text)
        self.ln(1)

class IBDMarketAnalyst:
    def __init__(self):
        self.news_api = NewsApiClient(api_key=NEWS_API_KEY)
        self.openai_client = openai.Client(api_key=OPENAI_API_KEY)
        self.briefs_dir = 'daily_briefs'
        os.makedirs(self.briefs_dir, exist_ok=True)
        
    def collect_news(self):
        """Collect news from NewsAPI"""
        try:
            # Get news from the last 24 hours
            yesterday = datetime.now() - timedelta(days=1)
            date_str = yesterday.strftime('%Y-%m-%d')
            
            news_items = []
            for category in CATEGORIES:
                response = requests.get(
                    f'https://newsapi.org/v2/everything',
                    params={
                        'q': category,
                        'from': date_str,
                        'sortBy': 'relevancy',  # Sort by relevance instead of date
                        'language': 'en',
                        'pageSize': 10,  # Limit to 10 most relevant articles per category
                        'apiKey': NEWS_API_KEY
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('articles'):
                        for article in data['articles']:
                            # Only include articles that mention deals, mergers, acquisitions, or valuations
                            title = article.get('title', '') or ''
                            desc = article.get('description', '') or ''
                            if any(keyword in (title + desc).lower() for keyword in ['deal', 'merger', 'acquisition', 'valuation', 'billion', 'million']):
                                # Format article with source information
                                formatted_article = f"""
                                Title: {article.get('title', 'N/A')}
                                Description: {article.get('description', 'N/A')}
                                Content: {article.get('content', 'N/A')}
                                """
                                news_items.append(formatted_article)
                else:
                    print(f"Error fetching news for category '{category}': {response.status_code}")
                    
            return news_items
        except Exception as e:
            print(f"Error collecting news: {str(e)}")
            return []

    def analyze_news(self, news_items):
        """Perform focused analysis on M&A and valuation aspects"""
        # Group news by category for better analysis
        formatted_news = self._format_news_by_category(news_items)
        
        md_analysis_prompt = """
        As a senior Investment Banking MD specializing in TMT M&A, provide a comprehensive analysis of recent deals and market movements.
        Structure your analysis with the following sections:

        EXECUTIVE SUMMARY
        - Key highlights from the past 24 hours
        - Major deal announcements and their significance
        - Critical market movements and their implications
        - Key takeaways for investors and stakeholders

        1. RECENT TMT M&A ACTIVITY
        - List all significant M&A deals announced in the past 24 hours
        - For each deal:
          * Deal structure (all-cash, all-stock, or mixed)
          * Transaction value and multiples
          * Key terms and conditions
          * Strategic rationale and fit
          * Expected synergies and integration timeline
          * Regulatory considerations

        2. MARKET DYNAMICS & SENTIMENT
        - Overall TMT sector sentiment
        - Key market drivers and headwinds
        - Subsector performance analysis
        - Trading multiples trends
        - Notable investor/analyst reactions

        3. TECH/AI LANDSCAPE
        - Major technological announcements
        - AI/ML developments and their market impact
        - Emerging technology trends
        - Impact on:
          * Deal valuations
          * Strategic priorities
          * Competitive dynamics

        4. STAKEHOLDER ANALYSIS
        - Deal-specific impacts on:
          * Shareholders (value creation/dilution)
          * Employees (synergies, restructuring)
          * Competitors (market positioning)
          * Customers (product/service implications)
        - Market reaction and analyst commentary
        - Board and management perspectives

        5. VALUATION & FINANCIAL METRICS
        - For each M&A deal:
          * Transaction multiples (EV/Revenue, EV/EBITDA, P/E)
          * Premium analysis vs. historical averages
          * Comparable company analysis
          * Precedent transaction analysis
        - Sector-specific metrics:
          * Growth rates
          * Margin profiles
          * Return metrics
        - Key valuation drivers and assumptions

        6. FORWARD-LOOKING ANALYSIS
        - Expected market reaction
        - Potential counter-bids or competing offers
        - Similar deals likely to follow
        - Sector consolidation predictions
        - Key risks and mitigants

        Base your analysis on these news items:
        {news_items}

        IMPORTANT:
        1. Focus on concrete data points and specific metrics
        2. Provide actionable insights
        3. Highlight key risks and opportunities
        4. Include specific numbers and comparisons where possible
        5. Maintain a professional, analytical tone
        """.format(news_items=formatted_news)
        
        try:
            analysis = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a senior Investment Banking MD specializing in TMT M&A. You are known for providing precise, data-driven analysis focused on deal structures and valuations. Your analysis is highly regarded for its depth, accuracy, and actionable insights."},
                    {"role": "user", "content": md_analysis_prompt}
                ],
                max_tokens=3000,  # Increased token limit for more detailed analysis
                temperature=0.3  # Lower temperature for more focused, precise analysis
            )
            return analysis.choices[0].message.content
        except Exception as e:
            if "insufficient_quota" in str(e):
                return "Error: OpenAI API quota exceeded. Please set up billing at platform.openai.com/account/billing"
            raise e

    def _format_news_by_category(self, news_items):
        """Format news items by category for analysis"""
        formatted_news = []
        for item in news_items:
            if isinstance(item, str):
                formatted_news.append(item)
            else:
                formatted_news.append(str(item))
        return "\n\n".join(formatted_news)

    def format_brief(self, analysis):
        """Format the analysis into a professional PDF brief"""
        # Generate filename with today's date
        today = datetime.now().strftime('%Y-%m-%d')
        filename = os.path.join(self.briefs_dir, f'brief_{today}.pdf')
        
        # Create PDF
        pdf = PDF()
        pdf.set_title(f'TMT Sector M&A & Valuation Brief - {today}')
        pdf.add_page()
        
        # Add date and confidentiality notice
        pdf.set_font('Helvetica', 'I', 8)
        pdf.cell(0, 5, f'Generated on {today}', 0, 1, 'R')
        pdf.cell(0, 5, 'CONFIDENTIAL - FOR INTERNAL USE ONLY', 0, 1, 'R')
        pdf.ln(10)
        
        # Split analysis into sections
        sections = analysis.split('\n\n')
        
        for section in sections:
            if section.strip():
                # Check if this is the executive summary
                if section.strip().startswith('EXECUTIVE SUMMARY'):
                    pdf.set_font('Helvetica', 'B', 14)
                    pdf.cell(0, 10, 'EXECUTIVE SUMMARY', 0, 1, 'L')
                    pdf.ln(2)
                # Check if this is a main section header
                elif section.strip().startswith(('1.', '2.', '3.', '4.', '5.', '6.')):
                    pdf.chapter_title(section.strip())
                else:
                    # Handle bullet points and regular text
                    lines = section.strip().split('\n')
                    for line in lines:
                        line = line.strip()
                        if line.startswith('*') or line.startswith('-'):
                            # This is a bullet point
                            content = line[1:].strip()
                            pdf.bullet_point(content)
                        else:
                            # Regular text
                            pdf.chapter_body(line)
        
        # Add footer with page numbers
        pdf.set_auto_page_break(auto=True, margin=15)
        
        # Save the PDF
        pdf.output(filename)
        return filename

    def list_past_briefs(self):
        """List all past briefs"""
        try:
            briefs = []
            if os.path.exists(self.briefs_dir):
                for file in os.listdir(self.briefs_dir):
                    if file.startswith('brief_') and file.endswith('.pdf'):
                        briefs.append(file)
            return sorted(briefs, reverse=True)
        except Exception as e:
            print(f"Error listing briefs: {str(e)}")
            return []

    def generate_daily_brief(self):
        """Generate a comprehensive daily briefing"""
        try:
            print("Collecting news articles...")
            news = self.collect_news()
            if not news:
                raise Exception("No news articles found")
            
            print(f"Analyzing {len(news)} news articles...")
            analysis = self.analyze_news(news)
            if not analysis:
                raise Exception("Failed to generate analysis")
            
            print("Formatting report...")
            filename = self.format_brief(analysis)
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
        brief_path = analyzer.generate_daily_brief()
        
        print(f"\nAnalysis completed successfully!")
        print(f"Focused brief saved to: {brief_path}")
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        if "insufficient_quota" in str(e):
            print("Please set up billing at platform.openai.com/account/billing")

if __name__ == "__main__":
    main()
