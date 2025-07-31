from newsapi import NewsApiClient
from datetime import datetime, timedelta
import openai
import os
import traceback
from fpdf import FPDF
from config import NEWS_API_KEY, OPENAI_API_KEY, SECTOR_CONFIGS, NEWS_LOOKBACK_DAYS
import requests
from interview_generator import IBInterviewGenerator
import re
import httpx

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
        """Enhanced header with better formatting"""
        if self.title:
            # Main title
            self.set_font('Helvetica', 'B', 16)  # Larger, bold font
            self.set_text_color(0, 0, 0)  # Black text
            self.cell(0, 12, self.title, 0, 1, 'C')
            
            # Subtitle
            self.set_font('Helvetica', 'I', 11)
            self.set_text_color(100, 100, 100)  # Dark gray text
            self.cell(0, 6, 'Technology, Media & Telecommunications Sector', 0, 1, 'C')
            
            # Reset text color
            self.set_text_color(0, 0, 0)
            self.ln(8)
        
    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def chapter_title(self, title):
        """Enhanced chapter title with bold formatting, shading, and better spacing"""
        title = clean_text_for_pdf(title)
        self.ln(8)  # Add space before title
        
        # Set up the title formatting
        self.set_font('Helvetica', 'B', 14)  # Bold, larger font
        
        # Calculate title dimensions
        title_width = self.get_string_width(title) + 20  # Add padding
        title_height = 12  # Height for the shaded area
        title_x = self.l_margin
        title_y = self.get_y()
        
        # Draw shaded background rectangle
        self.set_fill_color(220, 220, 220)  # Light gray background
        self.rect(title_x, title_y, title_width, title_height, 'F')
        
        # Add the title text on top of the background
        self.set_text_color(0, 0, 0)  # Black text
        self.set_xy(title_x + 5, title_y + 2)  # Position text with padding
        self.cell(title_width - 10, title_height - 4, title, 0, 0, 'L')
        
        # Move to next line after title
        self.set_xy(self.l_margin, title_y + title_height + 4)
        
        # Add a subtle line under the title
        self.set_line_width(0.5)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(6)  # Add space after line

    def subsection_title(self, title):
        """Subsection title with bold formatting, shading, and smaller font than chapter_title"""
        title = clean_text_for_pdf(title)
        self.ln(4)  # Add space before title
        
        # Set up the title formatting
        self.set_font('Helvetica', 'B', 12)  # Bold, smaller font than chapter_title
        
        # Calculate title dimensions
        title_width = self.get_string_width(title) + 15  # Add padding
        title_height = 10  # Height for the shaded area
        title_x = self.l_margin
        title_y = self.get_y()
        
        # Draw shaded background rectangle
        self.set_fill_color(240, 240, 240)  # Lighter gray background than chapter_title
        self.rect(title_x, title_y, title_width, title_height, 'F')
        
        # Add the title text on top of the background
        self.set_text_color(0, 0, 0)  # Black text
        self.set_xy(title_x + 3, title_y + 2)  # Position text with padding
        self.cell(title_width - 6, title_height - 4, title, 0, 0, 'L')
        
        # Move to next line after title
        self.set_xy(self.l_margin, title_y + title_height + 2)
        self.ln(2)  # Add space after title

    def chapter_body(self, body):
        """Enhanced chapter body with better formatting"""
        body = clean_text_for_pdf(body)
        self.set_font('Helvetica', '', 11)
        # Calculate effective width for text
        effective_width = self.w - 2 * self.l_margin
        self.multi_cell(effective_width, 5, body)
        self.ln(3)  # Add space between paragraphs

    def inline_bold_text(self, text):
        """Format text with inline bold headings while maintaining tight flow"""
        text = clean_text_for_pdf(text)
        
        # Split text by common inline headings
        headings = [
            'Key market drivers:', 'Headwinds:', 'Investor sentiment:', 'Actionable insights:',
            'Market drivers:', 'Key drivers:', 'Market sentiment:', 'Key insights:',
            'Trading multiples:', 'Performance analysis:', 'Competitive landscape:',
            'Risk factors:', 'Opportunities:', 'Challenges:', 'Outlook:'
        ]
        
        # Check if text contains any of these headings
        for heading in headings:
            if heading.lower() in text.lower():
                # Split the text at the heading
                parts = text.split(heading, 1)
                if len(parts) == 2:
                    # Add the text before the heading
                    if parts[0].strip():
                        self.chapter_body(parts[0].strip())
                    
                    # Add the heading in bold
                    self.set_font('Helvetica', 'B', 11)
                    self.cell(0, 5, clean_text_for_pdf(heading), 0, 0, 'L')
                    self.set_font('Helvetica', '', 11)  # Reset to normal font
                    
                    # Add the text after the heading
                    if parts[1].strip():
                        self.chapter_body(parts[1].strip())
                    return
        
        # If no headings found, just add as regular text
        self.chapter_body(text)

    def bullet_point(self, text):
        """Enhanced bullet point with better formatting"""
        text = clean_text_for_pdf(text)
        self.set_font('Helvetica', '', 11)
        # Calculate effective width for text
        effective_width = self.w - 2 * self.l_margin - 10
        self.cell(5, 5, '-', 0, 0, 'L')  # Use dash instead of bullet character for compatibility
        self.multi_cell(effective_width, 5, ' ' + text)
        self.ln(2)  # Add space after bullet point

    def deal_date(self, date_text):
        """Display deal date in smaller italic font for easy reading"""
        date_text = clean_text_for_pdf(date_text)
        self.set_font('Helvetica', 'I', 9)  # Smaller italic font
        self.set_text_color(100, 100, 100)  # Dark gray color for subtle appearance
        # Calculate effective width for text
        effective_width = self.w - 2 * self.l_margin
        self.multi_cell(effective_width, 4, date_text)  # Smaller line height
        self.ln(2)  # Add small space after date
        # Reset text color and font
        self.set_text_color(0, 0, 0)  # Reset to black
        self.set_font('Helvetica', '', 11)  # Reset to normal font

    def deal_header(self, deal_number):
        title = f"Deal {deal_number}"
        self.ln(6)
        self.set_fill_color(230, 230, 230)
        self.set_font('Helvetica', 'B', 14)
        self.cell(0, 12, title, 0, 1, 'L', fill=True)
        self.ln(2)

    def draw_hyperlink(self, title, url):
        self.set_text_color(0, 0, 255)
        self.set_font('Helvetica', 'U', 11)
        self.cell(0, 5, clean_text_for_pdf(title), ln=1, link=url)
        self.set_text_color(0, 0, 0)
        self.set_font('Helvetica', '', 11)

class IBDMarketAnalyst:
    def __init__(self, sector_config):
        self.news_api = NewsApiClient(api_key=NEWS_API_KEY)
        # Use improved OpenAI client with better connection handling
        self.openai_client = openai.Client(
            api_key=OPENAI_API_KEY,
            http_client=httpx.Client(
                timeout=60,  # Increased timeout for large requests
                limits=httpx.Limits(max_connections=10, max_keepalive_connections=5)  # More connections
            )
        )
        self.interview_generator = IBInterviewGenerator()
        self.briefs_dir = 'daily_briefs'
        self.interview_dir = 'interview_packages'
        os.makedirs(self.briefs_dir, exist_ok=True)
        os.makedirs(self.interview_dir, exist_ok=True)
        self.sector_config = sector_config
        
    def collect_news(self):
        """Collect news from NewsAPI"""
        try:
            # Get news from the configured lookback period
            start_date = datetime.now() - timedelta(days=NEWS_LOOKBACK_DAYS)
            date_str = start_date.strftime('%Y-%m-%d')
            
            news_items = []
            
            for category in self.sector_config["CATEGORIES"]:
                response = requests.get(
                    f'https://newsapi.org/v2/everything',
                    params={
                        'q': f'{category} AND (acquisition OR merger OR investment OR deal OR funding OR buyout)',
                        'from': date_str,
                        'sortBy': 'relevancy',  # Sort by relevance instead of date
                        'language': 'en',
                        'pageSize': 10,  # Increased to get more relevant articles
                        'apiKey': NEWS_API_KEY
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('articles'):
                        for article in data['articles']:
                            # Include articles that mention deals, mergers, acquisitions, valuations, or general TMT news
                            title = article.get('title', '') or ''
                            desc = article.get('description', '') or ''
                            content = article.get('content', '') or ''
                            url = article.get('url', '') or ''
                            
                            # Relaxed filtering to include more relevant TMT news
                            relevant_keywords = [k for k in self.sector_config["CATEGORIES"]]
                            
                            # Add deal-specific keywords for better M&A coverage
                            deal_keywords = ["acquisition", "merger", "buyout", "investment", "funding", "deal", "purchase", "stake", "partnership", "joint venture", "ipo", "public listing"]
                            
                            # Check if article contains sector keywords OR deal keywords
                            sector_match = any(keyword in (title + desc + content).lower() for keyword in relevant_keywords)
                            deal_match = any(keyword in (title + desc + content).lower() for keyword in deal_keywords)
                            
                            if sector_match or deal_match:
                                # Format article with source information and URL
                                formatted_article = f"""
                                Title: {title}
                                Description: {article.get('description', 'N/A')}
                                Content: {content[:500] if content else 'N/A'}  # Truncate content to reduce tokens
                                Source: {article.get('source', {}).get('name', 'N/A')}
                                Published: {article.get('publishedAt', 'N/A')}
                                URL: {url}
                                """
                                news_items.append(formatted_article)
                else:
                    print(f"Error fetching news for category '{category}': {response.status_code}")
                    
            print(f"Collected {len(news_items)} relevant news articles")
            # Debug: Print first few article titles to see what we're getting
            if news_items:
                print("Sample news titles:")
                for i, item in enumerate(news_items[:3]):
                    lines = item.split('\n')
                    title_line = next((line for line in lines if line.strip().startswith('Title:')), 'No title found')
                    print(f"  {i+1}. {title_line}")
            return news_items
        except Exception as e:
            print(f"Error collecting news: {str(e)}")
            return []

    def analyze_news(self, news_items):
        """Perform focused analysis on M&A and valuation aspects"""
        # Group news by category for better analysis
        formatted_news = self._format_news_by_category(news_items)
        
        # 1. Update the prompt
        md_analysis_prompt = f"""
        IMPORTANT: Create a CONCISE, DENSE report with minimal redundancy. Focus on key data points, specific numbers, and actionable insights. Avoid verbose explanations and repetitive content.

        For EACH DEAL, you MUST include a line with the original news source URL in the format: Read the original news: [URL].

        As a senior Investment Banking MD specializing in {self.sector_config['prompt_sector']} M&A, provide a focused, data-driven analysis.
        Structure your analysis with the following sections. Be CONCISE and DENSE - avoid redundancy and verbose explanations.

        1. RECENT {self.sector_config['prompt_sector'].upper()} M&A ACTIVITY
        CRITICAL: You MUST analyze the provided news items thoroughly and identify ALL M&A deals, IPOs, acquisitions, mergers, or significant transactions mentioned. Do not skip this section - find the deals!
        
        - Search through the news items for ANY mention of:
          * Mergers and acquisitions
          * Company acquisitions
          * Investment rounds
          * Strategic partnerships
          * IPOs or public listings
          * Asset sales or purchases
          * Joint ventures
          * Minority stake purchases
        
        - For each deal found, provide the following structured information:
          
          Deal Size: [USD amount - only if explicitly mentioned in news]
          Valuation Multiples: [EV/EBITDA or P/E if available in news]
          Companies: [Buyer] acquiring [Target] - only use actual company names from news
          Date Announced: [Date - only if mentioned in news]
          Rationale: [Brief market share, synergies, geographic expansion - based on news content]
          Risk: [Key risks - based on news analysis]
          
          If the deal is actually an IPO, provide IPO-specific information instead:
          IPO Rationale: [Reason for listing - from news]
          Valuation: [Expected valuation - only if mentioned in news]
          Pricing Range: [Expected pricing range - only if mentioned in news]
          Timing: [Expected IPO timing - only if mentioned in news]
          
        - If you find deals, list them ALL. Do not skip deals that seem small - include everything mentioned.
        - Focus on deals that are most relevant to the {self.sector_config['prompt_sector']} sector and have significant market impact

        2. MARKET DYNAMICS & SENTIMENT (CONCISE ANALYSIS)
        - Overall {self.sector_config['prompt_sector']} sector sentiment with key metrics
        - Key market drivers and headwinds with specific data points
        - Subsector performance analysis with numbers
        - Trading multiples trends with specific comparisons
        - Notable investor/analyst reactions with key quotes
        - Actionable insights for bankers and investors

        3. BANKING PIPELINE (CONCISE ANALYSIS)
        - Deal Pipeline:
          * Live deals: Transactions in progress with expected timing
          * Mandated deals: Secured mandates with client names if possible
          * Pitching-stage deals: Active pitches with sector focus
        - Pipeline metrics:
          * Expected revenue/fees from active pipeline
          * Timing projections (Q2 close, Q4 IPO, etc.)
          * Workload allocation analysis
        - Notable pipeline developments and competitive landscape
        - Actionable insights for team management

        4. STAKEHOLDER IMPACT & FORWARD-LOOKING ANALYSIS (CONCISE ANALYSIS)
        - Deal-specific impacts on:
          * Shareholders (value creation/dilution with numbers)
          * Employees (synergies, restructuring with examples)
          * Competitors (market positioning with specific moves)
          * Customers (product/service implications)
        - Market reaction and analyst commentary with key quotes
        - Expected market reaction with scenario analysis
        - Potential counter-bids or competing offers
        - Similar deals likely to follow
        - Key risks and mitigants
        - Actionable insights for clients and bankers

        5. TECH TRENDS & INNOVATION (CONCISE ANALYSIS)
        - Key technological developments affecting {self.sector_config['prompt_sector']} M&A
        - Innovation trends with specific examples and company names
        - Impact on deal structures and valuations
        - Emerging opportunities and threats
        - Actionable insights for deal teams

        6. RECOMMENDED READINGS
        - Provide 3-5 specific educational resources that directly connect to today's deals and trends
        - For each major deal or trend, recommend specific resources that explain those exact concepts
        - Include direct links to resources when possible
        - Explain exactly how each resource helps understand the specific deals mentioned

        Base your analysis on these news items:
        {formatted_news}

        IMPORTANT:
        1. Be CONCISE and DENSE - avoid redundancy and verbose explanations
        2. Focus on specific data points, numbers, and actionable insights
        3. Highlight key risks and opportunities
        4. Include specific numbers and comparisons where possible
        5. Maintain a professional, analytical tone
        6. For sections 2, 3, 4, and 5, provide focused analysis without excessive detail
        7. CRITICAL: For section 1, ONLY include deals that are explicitly mentioned in the provided news items
        8. For section 6, provide specific, actionable recommendations
        """
        
        try:
            # Use GPT-3.5-turbo directly to avoid connection issues
            analysis = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": f"You are a senior Investment Banking MD specializing in {self.sector_config['prompt_sector']} M&A. You are known for providing precise, data-driven analysis focused on deal structures and valuations. Your analysis is highly regarded for its depth, accuracy, and actionable insights. CRITICAL: Always expand general phrases into specific, concrete examples with company names and ticker symbols. Use bullet points when expanding concepts for clarity. For the Recommended Readings section, make direct connections between specific deals/trends mentioned in the report and educational resources that explain those exact concepts."},
                    {"role": "user", "content": md_analysis_prompt}
                ],
                max_tokens=3072,  # Reduced to avoid context length issues
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
        pdf.set_title(f'{self.sector_config["brief_title"]} - {today}')
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
                # Check if this is a main section header (numbered, e.g., '1.', '2.', ..., '6.')
                first_line = section.strip().split('\n')[0]
                if re.match(r'^\d+\.', first_line):
                    header = first_line.replace('#', '').replace('*', '').strip()
                    # --- PAGE BREAK LOGIC: Ensure enough space for header and at least one line (especially for Recommended Readings) ---
                    if header.lower().startswith('6. recommended readings') and pdf.get_y() > pdf.h - pdf.b_margin - 30:
                        pdf.add_page()
                    pdf.chapter_title(header)
                    remaining_content = '\n'.join(section.strip().split('\n')[1:])
                    if remaining_content.strip():
                        process_section_content(remaining_content, pdf)
                else:
                    # Check if this is a subsection header (uppercase, may have numbering)
                    lines = section.strip().split('\n')
                    first_line = lines[0].strip()
                    
                    # Detect subsection headers: uppercase text, may have numbering like "1.1" or "A." or just uppercase
                    if (first_line.isupper() or 
                        (first_line and first_line.split()[0].replace('.', '').isdigit() and first_line.isupper()) or
                        (first_line and len(first_line.split()) <= 8 and first_line.isupper())):
                        
                        # Clean the header and apply formatting
                        header = first_line.replace('#', '').replace('*', '').strip()
                        pdf.chapter_title(header)
                        
                        # Process the rest of the section content
                        remaining_content = '\n'.join(lines[1:])
                        if remaining_content.strip():
                            process_section_content(remaining_content, pdf)
                    else:
                        # Process regular content blocks
                        process_section_content(section, pdf)
        
        # Add macroeconomic insights section at the end
        add_macro_insights(pdf)
        
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

    def generate_interview_package(self):
        """Generate a comprehensive interview preparation package"""
        try:
            print("Collecting news for interview questions...")
            news = self.collect_news()
            if not news:
                raise Exception("No news articles found for interview generation")
            
            print("Generating interview package...")
            package_content = self.interview_generator.generate_comprehensive_interview_package(news)
            
            # Save the package
            today = datetime.now().strftime('%Y-%m-%d')
            filename = os.path.join(self.interview_dir, f'interview_package_{today}.txt')
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(package_content)
            
            return filename
            
        except Exception as e:
            print(f"Error generating interview package: {str(e)}")
            raise
    
    def list_interview_packages(self):
        """List all available interview packages"""
        try:
            packages = []
            if os.path.exists(self.interview_dir):
                for file in os.listdir(self.interview_dir):
                    if file.startswith('interview_package_') and file.endswith('.txt'):
                        packages.append(file)
            return sorted(packages, reverse=True)
        except Exception as e:
            print(f"Error listing interview packages: {str(e)}")
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

def process_section_content(content, pdf):
    """Process section content and apply proper formatting"""
    lines = content.strip().split('\n')
    
    i = 0
    deal_counter = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Add check for empty lines
        if not line.strip():
            i += 1
            continue
            
        # Remove markdown formatting
        line = line.replace('#', '').replace('*', '').strip()
        
        # Detect 'Deal X' headers
        if line.lower().startswith('deal ') and (line[5:].strip().isdigit() or (line[5:6].isdigit() and line[6:7] == ':')):
            deal_counter += 1
            # --- PAGE BREAK LOGIC: Ensure enough space for header and at least one line ---
            if pdf.get_y() > pdf.h - pdf.b_margin - 20:
                pdf.add_page()
            # Force correct numbering regardless of what AI generates
            pdf.deal_header(str(deal_counter))
            i += 1
            continue

        # Detect and render hyperlinks for deals
        if line.lower().startswith('url:') or line.lower().startswith('read the original news:'):
            url = line.split('URL:', 1)[-1].strip() if 'URL:' in line else line.split('Read the original news:', 1)[-1].strip()
            if 'http' in url:
                url = url[url.find('http'):].strip()
                url = url.rstrip(').,?!;:').strip()
                title = 'Read the original news'
                print(f"[DEBUG] Adding hyperlink for section: '{title}' URL: {url}")  # Debug print
                pdf.draw_hyperlink(title, url)
            else:
                print(f"[DEBUG] No valid URL found in line: {line}")  # Debug print
            i += 1
            continue

        # 1️⃣ Check for bullet points (lines starting with -, •, or *)
        if line.startswith(('-', '•', '*')):
            # This is a bullet point
            content = line[1:].strip()
            if content:
                pdf.bullet_point(content)
        
        # Check if this is a subsection title (ends with colon, not a bullet point)
        elif (line.endswith(':') and 
              not line.startswith(('-', '•', '*')) and
              len(line.split()) <= 8 and  # Reasonable length for a title
              not line.isupper()):  # Not a main section header
            # --- PAGE BREAK LOGIC: Ensure enough space for header and at least one line ---
            if pdf.get_y() > pdf.h - pdf.b_margin - 20:
                pdf.add_page()
            # 4️⃣ Check for standalone actionable insights or key takeaways
            if any(phrase in line for phrase in ['Actionable Insights:', 'Key Takeaways:', 'Key Insights:']):
                # Remove the colon for the title
                title = line[:-1].strip()
                pdf.subsection_title(title)
            else:
                # Remove the colon for the title
                title = line[:-1].strip()
                pdf.subsection_title(title)
        
        # Special handling for Recommended Readings section formatting
        elif line.startswith('→') or line.startswith('**Why this matters:**') or line.startswith('**Read this to understand:**') or line.startswith('**Key concept to learn:**'):
            # Format as bullet points for better readability in Recommended Readings
            content = line.strip()
            if content.startswith('→'):
                content = content[1:].strip()  # Remove the arrow
            elif content.startswith('**') and content.endswith('**'):
                content = content[2:-2].strip()  # Remove bold markers
            pdf.bullet_point(content)
        
        # Handle deal names in Recommended Readings (lines that end with quotes and contain deal descriptions)
        elif (line.strip().endswith('"') and 
              ('Funding Round' in line or 'Partnership' in line or 'Acquisition' in line or 'IPO' in line or 'Merger' in line)):
            # Format deal names as subsection titles for better organization
            title = line.strip().strip('"')
            pdf.subsection_title(title)
        
        # Check for specific deal field headings that should be rendered as subsection titles
        elif (line.endswith(':') and 
              any(field in line for field in [
                  'Deal Size:', 'Valuation Multiples:', 'Companies:', 'Date Announced:', 
                  'Rationale:', 'Risk:', 'IPO Rationale:', 'Valuation:', 'Pricing Range:', 'Timing:'
              ])):
            # --- PAGE BREAK LOGIC: Ensure enough space for header and at least one line ---
            if pdf.get_y() > pdf.h - pdf.b_margin - 20:
                pdf.add_page()
            # Special handling for Companies followed by Date Announced
            if 'Companies:' in line:
                # Remove the colon for the title
                title = line[:-1].strip()
                pdf.subsection_title(title)
                
                # Check if next line is Date Announced
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if 'Date Announced:' in next_line:
                        # Extract the date value (everything after "Date Announced:")
                        date_value = next_line.split('Date Announced:', 1)[1].strip()
                        if date_value:
                            pdf.deal_date(date_value)
                        i += 1  # Skip the Date Announced line since we've processed it
                    else:
                        # Regular companies content
                        companies_content = line.split('Companies:', 1)[1].strip()
                        if companies_content:
                            pdf.chapter_body(companies_content)
            else:
                # Remove the colon for the title
                title = line[:-1].strip()
                pdf.subsection_title(title)
                
                # Get the content for this field (everything after the colon)
                field_content = line.split(':', 1)[1].strip()
                if field_content:
                    pdf.chapter_body(field_content)
        
        else:
            # 2️⃣ Check for inline headings in regular text
            if any(phrase in line for phrase in [
                'Key market drivers:', 'Headwinds:', 'Investor sentiment:', 'Actionable insights:',
                'Market drivers:', 'Key drivers:', 'Market sentiment:', 'Key insights:',
                'Trading multiples:', 'Performance analysis:', 'Competitive landscape:',
                'Risk factors:', 'Opportunities:', 'Challenges:', 'Outlook:'
            ]):
                # Use inline bold formatting
                pdf.inline_bold_text(line)
            else:
                # Regular text - ensure it's not empty before adding
                if line.strip():
                    pdf.chapter_body(line)
        
        i += 1

def clean_text_for_pdf(text):
    """Clean text of problematic Unicode characters for PDF generation"""
    if not text:
        return text
    
    # Replace problematic Unicode characters with ASCII equivalents
    replacements = {
        '\u20b9': 'Rs',  # Indian Rupee
        '\u20ac': 'EUR',  # Euro
        '\u00a3': 'GBP',  # Pound Sterling
        '\u00a5': 'JPY',  # Yen
        '\u20bf': 'BTC',  # Bitcoin
        '\u201c': '"',    # Left double quotation mark
        '\u201d': '"',    # Right double quotation mark
        '\u2018': "'",    # Left single quotation mark
        '\u2019': "'",    # Right single quotation mark
        '\u2013': '-',    # En dash
        '\u2014': '--',   # Em dash
        '\u2022': '-',    # Bullet
        '\u2026': '...',  # Ellipsis
    }
    
    for unicode_char, replacement in replacements.items():
        text = text.replace(unicode_char, replacement)
    
    # More aggressive cleaning - convert to ASCII and handle errors gracefully
    try:
        # First try to encode as UTF-8 and decode as ASCII
        text = text.encode('utf-8').decode('ascii', errors='ignore')
    except:
        # If that fails, use a more aggressive approach
        text = ''.join(char for char in text if ord(char) < 128)
    
    return text.strip()

def add_macro_insights(pdf, macro_summary=None):
    """Add a concise macroeconomic insights section to the PDF with bullet points."""
    pdf.chapter_title("7. MACROECONOMIC INSIGHTS")
    if macro_summary is None:
        macro_summary = (
            "US Policy Risks Rising: New tariffs could push average US tariff rates above 20%, raising costs for companies and consumers.\n"
            "Market Reaction Muted: Despite policy headlines, the S&P 500 and US dollar are up, and Treasury yields are only modestly higher.\n"
            "Lagged Economic Impact: The true effect of tariffs may not show up in data for months, as companies use existing inventories.\n"
            "Key Watchpoints: Details of tariff implementation (exceptions, quotas); hard economic data in coming months; ongoing trade negotiations with major partners (China, Mexico, Canada, Europe).\n"
            "Bottom Line: Markets are assuming benign outcomes, but risks from trade policy and economic data remain."
        )
    # Add each line as a bullet point
    for line in macro_summary.split('\n'):
        if line.strip():
            pdf.bullet_point(line.strip())

def main():
    """Main execution function"""
    from config import SECTOR_CONFIGS
    print("Available sectors:", ", ".join(SECTOR_CONFIGS.keys()))
    sector = input("Enter sector (TMT, Energy): ").strip()
    if sector not in SECTOR_CONFIGS:
        print(f"Sector '{sector}' not recognized. Available: {list(SECTOR_CONFIGS.keys())}")
        return
    config = SECTOR_CONFIGS[sector]
    analyzer = IBDMarketAnalyst(config)
    brief_path = analyzer.generate_daily_brief()
    print(f"\nAnalysis completed successfully!")
    print(f"Focused brief saved to: {brief_path}")

if __name__ == "__main__":
    main() 