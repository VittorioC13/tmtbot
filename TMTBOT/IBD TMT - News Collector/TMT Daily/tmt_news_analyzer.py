"""
TMT News Analyzer
A Python script that collects, analyzes, and generates daily briefs of Technology, Media, and Telecommunications (TMT) news,
with a focus on investment banking pipeline implications.

Required packages:
pip install openai fpdf requests beautifulsoup4 python-dotenv newsapi-python

Usage:
1. Set up your environment variables:
   - OPENAI_API_KEY: Your OpenAI API key
   - NEWS_API_KEY: Your NewsAPI key

2. Run the script:
   python tmt_news_analyzer.py

The script will:
1. Collect TMT news from various sources
2. Analyze the news using GPT-4 Turbo
3. Generate a professional PDF report
"""

from fpdf import FPDF
import os
from datetime import datetime
import re
from openai import OpenAI
from newsapi import NewsApiClient
import requests

# Set API keys directly
OPENAI_API_KEY = "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"
NEWS_API_KEY = "ca607f1696c646fd807335abee3432a7"

# Set up OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

def clean_duplicate_deals(text):
    """Remove duplicate deal summaries from the analysis."""
    sections = text.split("###")
    for i, section in enumerate(sections):
        if "1. RECENT TMT M&A ACTIVITY" in section:
            pattern = r'\d+\.\s+\*\*.*?Deal:\*\*.*?\n'
            sections[i] = re.sub(pattern, '', section)
            break
    return "###".join(sections)

class PDF(FPDF):
    """Custom PDF class for generating professional reports."""
    
    def __init__(self):
        super().__init__()
        self.set_margins(20, 20, 20)
        self.set_auto_page_break(auto=True, margin=25)
        self.add_page()
        self.set_font('Arial', 'B', 16)
        
    def clean_text(self, text):
        """Clean text to handle special characters."""
        return text.encode('latin-1', 'replace').decode('latin-1')
        
    def header(self):
        """Add header with confidentiality notice and date."""
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 5, 'CONFIDENTIAL - FOR INTERNAL USE ONLY', 0, 1, 'R')
        self.set_text_color(0, 0, 0)
        self.cell(0, 5, f'Generated on {datetime.now().strftime("%Y-%m-%d")}', 0, 1, 'R')
        self.ln(10)

    def footer(self):
        """Add footer with page number."""
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def chapter_title(self, title):
        """Format chapter titles."""
        self.set_font('Arial', 'B', 14)
        self.set_fill_color(240, 240, 240)
        self.ln(5)
        self.cell(0, 10, self.clean_text(title), 0, 1, 'L', fill=True)
        self.ln(5)
        self.set_font('Arial', '', 11)

    def chapter_body(self, body):
        """Format chapter body text with support for bold text."""
        self.set_font('Arial', '', 11)
        effective_width = self.w - self.l_margin - self.r_margin
        
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
            
        lines = self.multi_cell(effective_width, 5, self.clean_text(body), split_only=True)
        for line in lines:
            self.multi_cell(effective_width, 5, line)
        self.ln(5)

    def bullet_point(self, text):
        """Format bullet points with proper indentation."""
        self.set_font('Arial', '', 11)
        effective_width = self.w - self.l_margin - self.r_margin - 10
        self.cell(5, 5, '-', 0, 0, 'R')
        self.cell(5, 5, '', 0, 0)
        lines = self.multi_cell(effective_width, 5, self.clean_text(text), split_only=True)
        
        if lines:
            self.multi_cell(effective_width, 5, lines[0])
            for line in lines[1:]:
                self.cell(10, 5, '', 0, 0)
                self.multi_cell(effective_width, 5, line)
        self.ln(2)

    def format_analysis(self, analysis_text):
        """Format the entire analysis into the PDF."""
        cleaned_analysis = clean_duplicate_deals(analysis_text)
        sections = cleaned_analysis.split("###")
        
        for section in sections:
            if not section.strip():
                continue
                
            lines = section.strip().split("\n")
            title = lines[0].strip()
            self.chapter_title(title)
            
            content = "\n".join(lines[1:]).strip()
            if content:
                for line in content.split("\n"):
                    line = line.strip()
                    if line:
                        if line.startswith("-") or line.startswith("*"):
                            self.bullet_point(line[1:].strip())
                        else:
                            self.chapter_body(line)

class TMTNewsAnalyzer:
    """Main class for collecting and analyzing TMT news."""
    
    def __init__(self):
        """Initialize the analyzer with NewsAPI key."""
        self.api_key = NEWS_API_KEY
        
    def collect_news(self):
        """Collect TMT sector news from various sources."""
        articles = []
        queries = [
            'technology M&A',
            'tech acquisition',
            'media merger',
            'telecommunications deal',
            'TMT sector',
            'tech valuation'
        ]
        
        for query in queries:
            url = f"https://newsapi.org/v2/everything?q={query}&language=en&sortBy=relevancy&pageSize=3&apiKey={self.api_key}"
            response = requests.get(url).json()
            print(f"\nQuery: {query}")
            print(f"Response: {response}")
            
            if response.get('status') == 'ok' and response.get('articles'):
                for article in response['articles']:
                    content = article.get('content', '')[:300] if article.get('content') else ''
                    description = article.get('description', '')[:150] if article.get('description') else ''
                    url = article.get('url', '')
                    
                    articles.append(
                        f"Title: {article['title']}\n"
                        f"Description: {description}\n"
                        f"Content: {content}\n"
                        f"URL: {url}\n"
                    )
        
        return articles[:12]

    def analyze_news(self, articles):
        """Analyze collected news using GPT-4 Turbo."""
        articles_text = "\n\n".join([f"Article {i+1}:\n{article}" for i, article in enumerate(articles)])
        
        system_message = """You are a professional investment banking analyst specializing in TMT sector analysis.
Your task is to provide a comprehensive, detailed analysis without any space limitations.
Include specific examples, quantitative metrics, and detailed banking pipeline implications for each section.
Do not truncate or summarize any sections. Provide thorough analysis regardless of length.
Each trend or deal analysis must include specific banking pipeline implications."""

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
- Banking Pipeline Impact

Please provide a comprehensive analysis for each section, including specific examples and quantitative metrics where applicable."""

        try:
            response = client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": f"{analysis_prompt}\n\nNews Articles:\n{articles_text}"}
                ],
                temperature=0.7,
                max_tokens=4000
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error during analysis: {str(e)}")
            return "Error: Failed to analyze news articles."

    def generate_pdf(self, analysis_text, filename):
        """Generate a PDF report from the analysis."""
        pdf = PDF()
        pdf.format_analysis(analysis_text)
        pdf.output(filename)

    def run(self):
        """Main execution method."""
        try:
            print("Collecting news articles...")
            news_articles = self.collect_news()
            
            if not news_articles:
                print("No news articles found.")
                return
            
            print(f"Analyzing {len(news_articles)} news articles...")
            analysis = self.analyze_news(news_articles)
            
            print("Formatting report...")
            pdf = PDF()
            pdf.add_page()
            
            # Add content to PDF
            pdf.chapter_title("TMT Daily Brief")
            pdf.chapter_body(analysis)
            
            # Save to static website assets folder
            output_path = "/Users/chechangyuan/Desktop/static-website/assets/brief.pdf"
            pdf.output(output_path)
            
            print(f"\nAnalysis completed successfully!")
            print(f"Focused brief saved to: {output_path}")
            
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    analyzer = TMTNewsAnalyzer()
    analyzer.run() 