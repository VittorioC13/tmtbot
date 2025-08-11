from fpdf import FPDF
import os
from datetime import datetime
import re
import openai
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
        self.cell(0, 10, title, 0, 1, 'L', fill=True)
        self.ln(5)
        self.set_font('Arial', '', 11)

    def chapter_body(self, body):
        self.set_font('Arial', '', 11)
        # Calculate effective width for text wrapping
        effective_width = self.w - self.l_margin - self.r_margin
        
        # Special handling for deal information
        if "Deal Structure:" in body or "**" in body:
            self.deal_info(body)
            return
            
        # Regular text handling
        lines = self.multi_cell(effective_width, 5, body, split_only=True)
        for line in lines:
            self.multi_cell(effective_width, 5, line)
        self.ln(5)

    def deal_info(self, text):
        self.set_font('Arial', '', 11)
        effective_width = self.w - self.l_margin - self.r_margin
        
        # Split the text by deal components
        if " - " in text:
            components = text.split(" - ")
            
            # Handle deal name (first component)
            self.set_font('Arial', 'B', 11)
            self.multi_cell(effective_width, 5, components[0].strip())
            self.ln(2)
            
            # Handle other components
            self.set_font('Arial', '', 11)
            for component in components[1:]:
                self.cell(10, 5, '•', 0, 0)  # Bullet point
                self.cell(5, 5, '', 0, 0)    # Space after bullet
                remaining_width = effective_width - 15
                self.multi_cell(remaining_width, 5, component.strip())
                self.ln(2)
        else:
            # If no special formatting needed, use regular multi_cell
            self.multi_cell(effective_width, 5, text)
        self.ln(3)

    def bullet_point(self, text):
        self.set_font('Arial', '', 11)
        # Calculate effective width for text with bullet point
        effective_width = self.w - self.l_margin - self.r_margin - 10
        # Add bullet point
        self.cell(5, 5, '•', 0, 0, 'R')
        self.cell(5, 5, '', 0, 0)  # Space after bullet
        # Split and wrap text after bullet point
        lines = self.multi_cell(effective_width, 5, text, split_only=True)
        
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
                        if line.startswith("-"):
                            self.bullet_point(line[1:].strip())
                        else:
                            self.chapter_body(line)
                            
        return cleaned_analysis

    def analyze_news(self, articles):
        md_analysis_prompt = """
Please analyze the provided TMT sector news articles and create a focused M&A and valuation brief. Structure the analysis as follows:

### EXECUTIVE SUMMARY
- Key market trends and major announcements
- Notable valuation metrics and deal activity
- Strategic implications for the sector

### 1. RECENT TMT M&A ACTIVITY
For each significant deal:
- Deal name and participants
- Transaction value and key terms
- Strategic rationale
- Expected synergies

### 2. MARKET DYNAMICS & SENTIMENT
- Current market conditions
- Investor sentiment
- Key drivers and challenges

### 3. TECH/AI LANDSCAPE
- Major technological developments
- Impact on valuations and deal activity
- Innovation trends

### 4. STAKEHOLDER ANALYSIS
- Impact on shareholders
- Industry consolidation effects
- Competitive landscape changes

### 5. VALUATION & FINANCIAL METRICS
- Transaction multiples
- Sector-specific KPIs
- Premium analysis

### 6. FORWARD-LOOKING ANALYSIS
- Expected market reactions
- Potential risks and opportunities
- Future deal activity predictions

Focus on actionable insights and quantitative metrics where available. Maintain a professional tone suitable for investment banking analysis.
"""
        # Prepare articles for analysis
        articles_text = "\n\n".join([f"Article {i+1}:\n{article}" for i, article in enumerate(articles)])
        
        # Create the messages for the chat completion
        messages = [
            {"role": "system", "content": "You are a professional investment banking analyst specializing in TMT sector analysis."},
            {"role": "user", "content": f"Here are the news articles to analyze:\n\n{articles_text}\n\n{md_analysis_prompt}"}
        ]
        
        # Get completion from OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            temperature=0.7,
            max_tokens=3000
        )
        
        # Store and return the analysis
        self.analysis_text = response.choices[0].message['content']
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