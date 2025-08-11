from fpdf import FPDF
import os
from datetime import datetime
import re
import openai
from newsapi import NewsApiClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')

def clean_duplicate_deals(text):
    # Find the M&A Activity section
    sections = text.split("###")
    for i, section in enumerate(sections):
        if "1. RECENT TMT M&A ACTIVITY" in section:
            # Pattern to match short summary deal lines
            pattern = r'\d+\.\s+\*\*.*?Deal:\*\*.*?\n'
            sections[i] = re.sub(pattern, '', section)
            break
    return "###".join(sections)

class PDF(FPDF):
    def __init__(self):
        super().__init__()
        # Set margins (left, top, right) in mm
        self.set_margins(20, 20, 20)
        # Set auto page break with margin
        self.set_auto_page_break(auto=True, margin=25)
        self.add_page()
        self.set_font('Arial', 'B', 16)
        
    def clean_text(self, text):
        """Clean text to handle special characters"""
        return text.encode('latin-1', 'replace').decode('latin-1')
        
    def header(self):
        # Add confidentiality notice
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 5, 'CONFIDENTIAL - FOR INTERNAL USE ONLY', 0, 1, 'R')
        self.set_text_color(0, 0, 0)
        # Add date
        self.cell(0, 5, f'Generated on {datetime.now().strftime("%Y-%m-%d")}', 0, 1, 'R')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 14)
        self.set_fill_color(240, 240, 240)
        # Add some spacing before title
        self.ln(5)
        self.cell(0, 10, self.clean_text(title), 0, 1, 'L', fill=True)
        self.ln(5)
        self.set_font('Arial', '', 11)

    def chapter_body(self, body):
        self.set_font('Arial', '', 11)
        # Calculate effective width for text wrapping
        effective_width = self.w - self.l_margin - self.r_margin
        
        # Handle bold text (text between **)
        if "**" in body:
            parts = body.split("**")
            for i, part in enumerate(parts):
                if i % 2 == 0:  # Regular text
                    self.set_font('Arial', '', 11)
                    self.multi_cell(effective_width, 5, self.clean_text(part.strip()))
                else:  # Bold text
                    self.set_font('Arial', 'B', 11)
                    self.multi_cell(effective_width, 5, self.clean_text(part.strip()))
            self.ln(5)
            return
            
        # Regular text handling
        lines = self.multi_cell(effective_width, 5, self.clean_text(body), split_only=True)
        for line in lines:
            self.multi_cell(effective_width, 5, line)
        self.ln(5)

    def bullet_point(self, text):
        self.set_font('Arial', '', 11)
        # Calculate effective width for text with bullet point
        effective_width = self.w - self.l_margin - self.r_margin - 10
        # Add bullet point
        self.cell(5, 5, '-', 0, 0, 'R')
        self.cell(5, 5, '', 0, 0)  # Space after bullet
        # Split and wrap text after bullet point
        lines = self.multi_cell(effective_width, 5, self.clean_text(text), split_only=True)
        
        # Print first line
        if lines:
            self.multi_cell(effective_width, 5, lines[0])
            # Print remaining lines with proper indentation
            for line in lines[1:]:
                self.cell(10, 5, '', 0, 0)  # Indentation
                self.multi_cell(effective_width, 5, line)
        self.ln(2)

    def format_analysis(self, analysis_text):
        # Clean up duplicate deal summaries before formatting
        cleaned_analysis = clean_duplicate_deals(analysis_text)
        
        # Split the analysis into sections
        sections = cleaned_analysis.split("###")
        
        for section in sections:
            if not section.strip():
                continue
                
            # Extract and format the section title
            lines = section.strip().split("\n")
            title = lines[0].strip()
            self.chapter_title(title)
            
            # Format the content
            content = "\n".join(lines[1:]).strip()
            if content:
                for line in content.split("\n"):
                    line = line.strip()
                    if line:
                        if line.startswith("-") or line.startswith("*"):
                            self.bullet_point(line[1:].strip())
                        else:
                            self.chapter_body(line)

class IBDMarketAnalyst:
    def __init__(self):
        # Initialize NewsAPI client
        self.newsapi = NewsApiClient(api_key=os.getenv('NEWS_API_KEY'))
        
    def collect_news(self):
        # Get news about TMT sector
        articles = []
        
        # Define search queries
        queries = [
            'technology M&A',
            'tech acquisition',
            'media merger',
            'telecommunications deal',
            'TMT sector',
            'tech valuation'
        ]
        
        # Collect news for each query
        for query in queries:
            response = self.newsapi.get_everything(
                q=query,
                language='en',
                sort_by='relevancy',
                page_size=3  # Reduced from 5 to 3 articles per query
            )
            
            if response['articles']:
                for article in response['articles']:
                    # Truncate content if it's too long
                    content = article.get('content', '')
                    if content:
                        content = content[:300]  # Reduced from 500 to 300 characters
                    
                    description = article.get('description', '')
                    if description:
                        description = description[:150]  # Reduced from 200 to 150 characters
                    
                    articles.append(
                        f"Title: {article['title']}\n"
                        f"Description: {description}\n"
                        f"Content: {content}\n"
                    )
        
        # Limit total number of articles
        return articles[:12]  # Reduced from 20 to 12 articles

    def analyze_news(self, articles):
        # Prepare articles for analysis
        articles_text = "\n\n".join([f"Article {i+1}:\n{article}" for i, article in enumerate(articles)])
        
        # Create system message with detailed instructions
        system_message = """You are a professional investment banking analyst specializing in TMT sector analysis.
Your task is to provide a comprehensive, detailed analysis without any space limitations.
Include specific examples, quantitative metrics, and detailed banking pipeline implications for each section.
Do not truncate or summarize any sections. Provide thorough analysis regardless of length.
Each trend or deal analysis must include specific banking pipeline implications."""

        # Create the analysis prompt with full detail
        analysis_prompt = """Analyze the provided TMT sector news articles and create a comprehensive M&A and valuation brief.
Include detailed analysis for ALL sections, with specific banking pipeline implications for each trend and deal.

Structure:

### EXECUTIVE SUMMARY
- Key market trends and major announcements
- Notable valuation metrics and deal activity
- Strategic implications for the sector
- Banking Pipeline Impact:
  * Potential advisory mandates
  * Financing opportunities
  * Strategic implications for our clients
  * Competitive positioning

### 1. RECENT TMT M&A ACTIVITY
For each significant deal:
- Deal name and participants
- Transaction value and key terms
- Strategic Rationale (include at least 2-3 of these components with specific examples):
  * Market Expansion (geographic/customer segment)
  * Product/Service Diversification
  * Synergies (Revenue/Cost)
  * Vertical Integration
  * Defensive Strategy
  * Talent/Technology Acquisition
- Banking Pipeline Implications for each deal

### 2. MARKET DYNAMICS & SENTIMENT
- Current market conditions and trends
- Sector-specific growth drivers
- Regulatory environment
- Investor sentiment
- Market consolidation trends
- Banking Pipeline Impact

### 3. TECH/AI LANDSCAPE
- Major technological developments
- AI/ML adoption trends
- Cloud computing evolution
- Cybersecurity landscape
- Digital transformation initiatives
- Banking Pipeline Impact

### 4. STAKEHOLDER ANALYSIS
- Impact on shareholders
- Industry consolidation effects
- Competitive landscape changes
- Customer impact
- Employee considerations
- Regulatory considerations
- Banking Pipeline Impact

### 5. VALUATION & FINANCIAL METRICS
- Transaction multiples analysis
- Sector-specific KPIs
- Premium analysis
- Financial health indicators
- Comparable company analysis
- Banking Pipeline Impact

### 6. FORWARD-LOOKING ANALYSIS
- Expected market reactions
- Potential risks and opportunities
- Future deal activity predictions
- Growth projections
- Strategic roadmap
- Banking Pipeline Impact

For each section:
- Provide specific examples and data
- Include quantitative metrics
- Detail banking pipeline implications
- Address risks and opportunities"""

        # Create the messages for the chat completion
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": f"Here are the news articles to analyze:\n\n{articles_text}\n\n{analysis_prompt}"}
        ]
        
        # Get completion from OpenAI using GPT-4 Turbo
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",  # Using GPT-4 Turbo for larger context window
            messages=messages,
            temperature=0.7,
            max_tokens=4000  # Adjusted to stay within model limits
        )
        
        # Store and return the analysis
        self.analysis_text = response.choices[0].message.content
        return self.analysis_text

    def generate_pdf(self, analysis_text, filename):
        pdf = PDF()
        pdf.format_analysis(analysis_text)
        pdf.output(filename)
        print(f"\nAnalysis completed successfully!")
        print(f"Focused brief saved to: {filename}")

    def run(self):
        print("Collecting news articles...")
        articles = self.collect_news()
        
        print(f"Analyzing {len(articles)} news articles...")
        analysis = self.analyze_news(articles)
        
        print("Formatting report...")
        today = datetime.now().strftime("%Y-%m-%d")
        os.makedirs("daily_briefs", exist_ok=True)
        filename = f"daily_briefs/brief_{today}.pdf"
        self.generate_pdf(analysis, filename)

if __name__ == "__main__":
    analyst = IBDMarketAnalyst()
    analyst.run() 