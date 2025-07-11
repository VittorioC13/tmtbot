from newsapi import NewsApiClient
from datetime import datetime, timedelta
from openai import OpenAI
import os
from fpdf import FPDF
from config import NEWS_API_KEY, OPENAI_API_KEY, CATEGORIES, NEWS_LOOKBACK_DAYS
import requests
from interview_generator import IBInterviewGenerator
import re

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
        self.set_text_color(0, 0, 0)
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def chapter_title(self, title):
        """Enhanced chapter title with bold formatting, shading, and better spacing"""
        if self.get_y() + 15 > self.page_break_trigger:
            self.add_page()
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
        if self.get_y() + 15 > self.page_break_trigger:
                    self.add_page()

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
        self.set_font('Helvetica', '', 11)
        # Clean text for PDF compatibility
        body = clean_text_for_pdf(body)
        # Calculate effective width for text
        effective_width = self.w - 2 * self.l_margin
        self.multi_cell(effective_width, 5, body)
        self.ln(3)  # Add space between paragraphs

    def inline_bold_text(self, text):
        """Format text with inline bold headings while maintaining tight flow"""
        # Clean text for PDF compatibility
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
                    self.cell(0, 5, heading, 0, 0, 'L')
                    self.set_font('Helvetica', '', 11)  # Reset to normal font
                    
                    # Add the text after the heading
                    if parts[1].strip():
                        self.chapter_body(parts[1].strip())
                    return
        
        # If no headings found, just add as regular text
        self.chapter_body(text)

    def bullet_point(self, text):
        """Enhanced bullet point with better formatting"""
        self.set_font('Helvetica', '', 11)
        # Clean text for PDF compatibility
        text = clean_text_for_pdf(text)
        # Calculate effective width for text
        effective_width = self.w - 2 * self.l_margin - 10
        self.cell(5, 5, '-', 0, 0, 'L')  # Use dash instead of bullet character for compatibility
        self.multi_cell(effective_width, 5, ' ' + text)
        self.ln(2)  # Add space after bullet point

    def deal_date(self, date_text):
        """Display deal date in smaller italic font for easy reading"""
        self.set_font('Helvetica', 'I', 9)  # Smaller italic font
        self.set_text_color(100, 100, 100)  # Dark gray color for subtle appearance
        # Clean text for PDF compatibility
        date_text = clean_text_for_pdf(date_text)
        # Calculate effective width for text
        effective_width = self.w - 2 * self.l_margin
        self.multi_cell(effective_width, 4, date_text)  # Smaller line height
        self.ln(2)  # Add small space after date
        # Reset text color and font
        self.set_text_color(0, 0, 0)  # Reset to black
        self.set_font('Helvetica', '', 11)  # Reset to normal font


class IBDMarketAnalyst:
    def __init__(self):
        self.news_api = NewsApiClient(api_key=NEWS_API_KEY)
        self.openai_client = OpenAI(api_key=OPENAI_API_KEY)
        self.interview_generator = IBInterviewGenerator()
        self.briefs_dir = 'daily_briefs'
        self.interview_dir = 'interview_packages'
        os.makedirs(self.briefs_dir, exist_ok=True)
        os.makedirs(self.interview_dir, exist_ok=True)
        
    def collect_news(self):
        """Collect news from NewsAPI"""
        try:
            # Get news from the configured lookback period
            start_date = datetime.now() - timedelta(days=NEWS_LOOKBACK_DAYS)
            date_str = start_date.strftime('%Y-%m-%d')
            
            news_items = []
            for category in CATEGORIES:
                response = requests.get(
                    f'https://newsapi.org/v2/everything',
                    params={
                        'q': category,
                        'from': date_str,
                        'sortBy': 'relevancy',  # Sort by relevance instead of date
                        'language': 'en',
                        'pageSize': 15,  # Increased to get more articles per category
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
                            
                            # Relaxed filtering to include more relevant TMT news
                            relevant_keywords = ['deal', 'merger', 'acquisition', 'valuation', 'billion', 'million', 
                                               'technology', 'ai', 'artificial intelligence', 'fintech', 'investment',
                                               'ipo', 'funding', 'venture capital', 'startup', 'tech', 'software']
                            
                            if any(keyword in (title + desc + content).lower() for keyword in relevant_keywords):
                                # Format article with source information
                                formatted_article = f"""
                                Title: {article.get('title', 'N/A')}
                                Description: {article.get('description', 'N/A')}
                                Content: {article.get('content', 'N/A')}
                                Source: {article.get('source', {}).get('name', 'N/A')}
                                URL: {article.get('url', 'N/A')}
                                Published: {article.get('publishedAt', 'N/A')}
                                """
                                news_items.append(formatted_article)
                else:
                    print(f"Error fetching news for category '{category}': {response.status_code}")
                    
            print(f"Collected {len(news_items)} relevant news articles")
            return news_items
        except Exception as e:
            print(f"Error collecting news: {str(e)}")
            return []

    def analyze_news(self, news_items):
        """Perform focused analysis on M&A and valuation aspects"""
        # Group news by category for better analysis
        formatted_news = self._format_news_by_category(news_items)
        
        md_analysis_prompt = """
            As a senior Investment Banking MD specializing in TMT M&A, provide a comprehensive, in-depth analysis of recent deals and market movements.
            Structure your analysis with the following sections. For sections 2 (Market Dynamics & Sentiment), 3 (Banking Pipeline), 4 (Stakeholder Impact & Forward-looking Analysis), and 5 (Tech Trends), your response MUST be multi-paragraph, highly detailed, and data-driven. Avoid generic or superficial summaries. Instead, provide:
            - Multiple paragraphs per section
            - Specific examples, numbers, and comparisons
            - Deeper breakdowns (e.g., for sentiment: by subsector, by geography, by deal type, etc.; for pipeline: by stage, by fee, by client type, etc.; for stakeholder/forward: by stakeholder group, with scenario analysis, etc.)
            - Actionable insights and professional-level commentary

            1. RECENT TMT M&A ACTIVITY
            CRITICAL: Include actual M&A deals, IPOs, or significant transactions that are mentioned in the provided news items. The news covers the past week, so focus on the most recent and significant deals.
            -When adding news titles (**News Title Goes Here**), follow this example: **China Approves Merger of CSSC and CSIC to Create World’s Largest Shipbuilder**  ([Link](https://gcaptain.com/china-approves-merger-of-cssc-and-csic-to-create-worlds-largest-shipbuilder/)) 
            -Only include links in section 1 and no other sections
            - If significant M&A deals, IPOs, or major transactions are found in the news items, list them with the following structured information with clear headings:
            Deal 1:
            **News Title Goes Here** ([Link](https://another.com)) 
            -Deal Size: [USD amount - only if explicitly mentioned in news]
            -Valuation Multiples: [EV/EBITDA or P/E if available in news, or estimated based on news data]
            -Companies: [Buyer] acquiring [Target] - only use actual company names from news
            -Date Announced: [Date - only if mentioned in news]
            -Rationale: [Market share, synergies, geographic expansion, etc. - based on news content]
            -Risk: [Short paragraph on key risks - based on news analysis]
            
            Deal 2:
            **News Title Goes Here** ([Link](https://another.com))
            -Deal Size: [USD amount - only if explicitly mentioned in news]
            -Valuation Multiples: [EV/EBITDA or P/E if available in news, or estimated based on news data]
            -Companies: [Buyer] acquiring [Target] - only use actual company names from news
            -Date Announced: [Date - only if mentioned in news]
            -Rationale: [Market share, synergies, geographic expansion, etc. - based on news content]
            -Risk: [Short paragraph on key risks - based on news analysis]
            
            If the deal is actually an IPO, provide IPO-specific information instead:
            IPO Rationale: [Reason for listing - from news]
            Valuation: [Expected valuation - only if mentioned in news]
            Pricing Range: [Expected pricing range - only if mentioned in news]
            Timing: [Expected IPO timing - only if mentioned in news]

            2. MARKET DYNAMICS & SENTIMENT (Provide a multi-paragraph, in-depth analysis)
            - Overall TMT sector sentiment, with breakdowns by subsector, geography, and deal type
            - Key market drivers and headwinds, with supporting data
            - Subsector performance analysis (e.g., software, media, telecom, fintech, AI)
            - Trading multiples trends, with specific numbers and comparisons
            - Notable investor/analyst reactions, with quotes or examples
            - Actionable insights for bankers and investors

            3. BANKING PIPELINE (Provide a multi-paragraph, in-depth analysis)
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
            - Actionable insights for team management and business development

            4. STAKEHOLDER IMPACT & FORWARD-LOOKING ANALYSIS (Provide a multi-paragraph, in-depth analysis)
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
            - Actionable insights for clients and bankers

            5. TECH TRENDS (Provide a multi-paragraph, in-depth analysis)
            - Identify key emerging technology trends from the news (e.g., Stablecoins, AI, Blockchain, Cloud Computing, Cybersecurity, etc.)
            - For each identified trend:
              * Provide a detailed explanation of the trend, its market significance, and growth trajectory
              * List specific companies from the news that are involved in this trend
              * For each company, provide a brief description of their activities and strategic positioning within the trend
              * Analyze the competitive landscape and market dynamics for each trend
              * Discuss potential M&A opportunities and investment implications
            - Focus on trends that have significant market impact and deal-making potential
            - Include specific examples, use cases, and market data where available
            - Provide actionable insights for bankers and investors regarding trend-driven opportunities

            Base your analysis on these news items:
            {news_items}

            IMPORTANT:
            1. Focus on concrete data points and specific metrics
            2. Provide actionable insights
            3. Highlight key risks and opportunities
            4. Include specific numbers and comparisons where possible
            5. Maintain a professional, analytical tone
            6. For sections 2, 3, 4, and 5, your response MUST be multi-paragraph, detailed, and data-driven. Avoid generic summaries.
            7. CRITICAL: For section 1, ONLY include deals that are explicitly mentioned in the provided news items. Do not fabricate any deal information, company names, or transaction details.
            """.format(news_items=formatted_news)
        
        try:
            analysis = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a senior Investment Banking MD specializing in TMT M&A. You are known for providing precise, data-driven analysis focused on deal structures and valuations. Your analysis is highly regarded for its depth, accuracy, and actionable insights."},
                    {"role": "user", "content": md_analysis_prompt}
                ],
                max_tokens=8000,  # Maximum allowed for GPT-4o-mini is 16K token for output and 128K token for context(input message). Using 8K for cost effectiveness and time concern
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
        sections = re.split(r'(?m)(?=^\s*#*\s*[1-6]\.)', analysis)

        for  section in sections:
            if section.strip():
                # Check if this is a main section header (numbered)
                if section.strip().startswith(('1.', '2.', '3.', '4.', '5.')):
                    # Clean the header and apply formatting
                    header = section.strip().split('\n')[0]
                    header = header.replace('#', '').replace('*', '').strip()
                    pdf.chapter_title(header)
                    
                    # Process the rest of the section content
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
            
            print("Storing API output into txt file...")
            txtFileName = f"raw_{str(datetime.now())}.txt"
            with open(txtFileName, "w") as file:
                file.write(analysis)
            
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
    while i < len(lines):
        line = lines[i].strip()
        
        m_link = link_re.match(line)
        if m_link:
            draw_hyperlink(pdf, m_link['title'].rstrip('* '), m_link['url'])
            i += 1
            continue

        # Add check for empty lines
        if not line.strip():
            i += 1
            continue
            
        # Remove markdown formatting
        line = line.replace('#', '').replace('*', '').strip()
        
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
            
            # 4️⃣ Check for standalone actionable insights or key takeaways
            if any(phrase in line for phrase in ['Actionable Insights:', 'Key Takeaways:', 'Key Insights:']):
                # Remove the colon for the title
                title = line[:-1].strip()
                pdf.subsection_title(title)
            else:
                # Remove the colon for the title
                title = line[:-1].strip()
                pdf.subsection_title(title)
        
        # Check for specific deal field headings that should be rendered as subsection titles
        elif (line.endswith(':') and 
              any(field in line for field in [
                  'Deal Size:', 'Valuation Multiples:', 'Companies:', 'Date Announced:', 
                  'Rationale:', 'Risk:', 'IPO Rationale:', 'Valuation:', 'Pricing Range:', 'Timing:'
              ])):
            
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

def render_sources_section(pdf: PDF, section_text: str) -> None:
    """
    Pretty-print the “6. SOURCES” block that GPT gives us.

        *Sources for Section 1*
        - **Article** ([Link](https://...))  "Snippet"

    Works even if bullets start with “- **” or plain “- ” and
    accepts leading ### on the subsection header.
    """

    # split -> keep non-empty -> trim
    lines = [ln.strip() for ln in section_text.splitlines() if ln.strip()]

    for line in lines:
        # 1)  recognize   *Sources for Section 2*   or   ### Sources..
        #     regardless of stray *, #, -, or spaces at either end
        cleaned = re.sub(r'^[#\*\-\s]+', '', line)     # strip leading junk
        cleaned = cleaned.rstrip('* ').strip()         # strip trailing ** / *
        hdr = re.match(r'^Sources\s+for\s+Section\s+(\d+)', cleaned, flags=re.I)
        if hdr:
            pdf.subsection_title(f"Sources for Section {hdr.group(1)}")
            continue

        # 2)  A bullet line with a title + ([Link]()) + optional snippet
        # remove ONE leading dash/• plus spaces – keep any ** that follows
        bullet = re.sub(r'^[-\u2022]\s*', '', line, count=1)

        m = re.match(
            r'(?:\*\*(?P<bold>.+?)\*\*|(?P<plain>.+?))\s*'      # title, bold or plain
            r'\(\s*\[Link\]\((?P<url>https?://[^\s)]+)\)\s*\)'  # ([Link](URL))
            r'(?:\s*(?P<rest>.*))?$',                           # optional snippet
            bullet,
            flags=re.S,
        )

        if m:
            # title text – strip any trailing ** that survived the lstrip
            title = (m.group('bold') or m.group('plain')).rstrip('* ').strip()
            url   = m.group('url')
            rest  = (m.group('rest') or '').strip()

            # clickable blue, underlined link
            pdf.set_text_color(0, 0, 255)
            pdf.set_font('Helvetica', 'U', 11)
            pdf.cell(0, 5, clean_text_for_pdf(title), ln=1, link=url)

            # reset
            pdf.set_text_color(0, 0, 0)
            pdf.set_font('Helvetica', '', 11)

            if rest:
                pdf.chapter_body(rest)
            continue

        # 3)  Stand-alone quoted snippet on its own line
        if line.startswith('"') and line.endswith('"'):
            pdf.chapter_body(line)
            continue

        # fallback – just write whatever text we got
        pdf.chapter_body(clean_text_for_pdf(line))

link_re = re.compile(
    r'\*\*(?P<title>.+?)\*\*\s*'
    r'\(\s*\[Link\]\((?P<url>https?://[^\s)]+)\)\s*\)'
)

def draw_hyperlink(pdf: PDF, title: str, url: str) -> None:
    """Render one blue, under-lined clickable link line."""
    pdf.set_text_color(0, 0, 255)
    pdf.set_font('Helvetica', 'U', 11)
    pdf.cell(0, 5, clean_text_for_pdf(title), ln=1, link=url)
    # reset for the rest of the text
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Helvetica', '', 11)


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
    
    # Remove any other non-ASCII characters that might cause issues
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)
    
    return text.strip()

def main():
    """Main execution function"""
    try:
        # Initialize the analyzer
        analyzer = IBDMarketAnalyst()
        
        # Generate the brief
        brief_path = analyzer.generate_daily_brief()
        
        print(f"Analysis completed successfully!")
        print(f"Focused brief saved to: {brief_path}")
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        if "insufficient_quota" in str(e):
            print("Please set up billing at platform.openai.com/account/billing")

if __name__ == "__main__":
    main() 
