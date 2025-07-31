from newsapi.newsapi_client import NewsApiClient
import httpx
from datetime import datetime, timedelta,date 
import openai
import os
import traceback
from fpdf import FPDF
from config import NEWS_API_KEY, OPENAI_API_KEY, CATEGORIES, NEWS_LOOKBACK_DAYS
import requests
from interview_generator import IBInterviewGenerator
import re
from pathlib import Path
import json


base_path = Path(__file__).resolve().parent.parent 
raw_dir = base_path / 'api' / "static" / "assets" / "raw"
json_path = base_path/ 'term_definitions.json'
section1Prompt = """
1. RECENT TMT M&A ACTIVITY

CRITICAL: Include actual M&A deals, IPOs, or significant transactions that are mentioned in the provided news items. The news covers the past week, so focus on the most recent and significant deals.

- If significant M&A deals, IPOs, or major transactions are found in the news items, list them with the following structured information with clear headings:
  
  Deal Size: [USD amount - only if explicitly mentioned in news]
  Valuation Multiples: [EV/EBITDA or P/E if available in news, or estimated based on news data]
  Companies: [Buyer] acquiring [Target] - only use actual company names from news
  Date Announced: [Date - only if mentioned in news]
  Rationale: [Market share, synergies, geographic expansion, etc. - based on news content]
  Risk: [Short paragraph on key risks - based on news analysis]
  
  If the deal is actually an IPO, provide IPO-specific information instead:
  IPO Rationale: [Reason for listing - from news]
  Valuation: [Expected valuation - only if mentioned in news]
  Pricing Range: [Expected pricing range - only if mentioned in news]
  Timing: [Expected IPO timing - only if mentioned in news]
  
- If no significant recent deals are found, include a brief summary of notable M&A trends or market activity from the past week based on the news content
- Ensure each deal has all required fields with clear headings for parsing
- If any field information is not available in the news, state "Not specified in news" rather than making up data
- Always cite the specific news source when providing deal information
- Focus on deals that are most relevant to the TMT sector and have significant market impact

Use ### as start of sections
Use **title:** as start of subsections
use - ** as bullet points
When adding links, use this EXACT format
**Link title** ([Link](https://linkURL))  
Follow this example as template:
### 1. RECENT TMT M&A ACTIVITY

**Deal 1:**
**China Approves Merger of CSSC and CSIC to Create World’s Largest Shipbuilder** ([Link](https://gcaptain.com/china-approves-merger-of-cssc-and-csic-to-create-worlds-largest-shipbuilder/))  
- **Deal Size:** Not specified in news  
- **Valuation Multiples:** Not specified in news  
- **Companies:** China State Shipbuilding Corporation (CSSC) acquiring China Shipbuilding Industry Corporation (CSIC)  
- **Date Announced:** Not specified in news  
- **Rationale:** The merger aims to create a dominant player in the shipbuilding industry, enhancing market share and operational synergies.  
- **Risk:** Key risks include regulatory scrutiny, integration challenges, and potential backlash from competitors and labor unions.

**Deal 2:**
**VC-Backed Firms Choose Mergers and Buyouts Amid Uncertainty Around IPOs** ([Link](http://www.pymnts.com/acquisitions/2025/venture-capital-backed-firms-choose-mergers-buyouts-amid-uncertainty-around-ipos/))  
- **Deal Size:** Not specified in news  
- **Valuation Multiples:** Not specified in news  
- **Companies:** Not specified in news  
- **Date Announced:** Not specified in news  
- **Rationale:** Companies backed by venture capital are increasingly opting for mergers and acquisitions over IPOs due to market volatility and uncertainty surrounding public listings.  
- **Risk:** The primary risks include overvaluation in M&A transactions and potential integration difficulties post-acquisition.

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

(For Finance Beginners)
- Based on the specific deals and trends identified in this report, provide educational resources that directly connect to today's market events
- For each major deal or trend mentioned in sections 1-5, recommend specific resources that explain the underlying concepts
- Structure recommendations as follows:
  
  **For each deal/trend identified:**
  [Deal/Trend Name]: [Brief description of what happened]
  → **Why this matters:** [Explain the broader significance]
  → **Read this to understand:** [Specific resource with direct connection]
  → **Key concept to learn:** [What specific finance concept this deal illustrates]
  
  **Example format:**
  "Revolut's $1B Funding Round"
  → **Why this matters:** Shows how fintech valuations work in current market conditions
  → **Read this to understand:** "Venture Deals" by Brad Feld - Chapter 8 on valuation methods
  → **Key concept to learn:** How to calculate and interpret Series A/B/C valuations
  
- Include specific connections like:
  * If a deal mentions "EV/EBITDA multiple of 15x" → Recommend "Valuation" by McKinsey Chapter 3
  * If AI companies are acquiring → Recommend "The Innovator's Dilemma" by Clayton Christensen
  * If fintech IPOs are mentioned → Recommend "The Psychology of Money" by Morgan Housel
  * If blockchain deals appear → Recommend "Digital Gold" by Nathaniel Popper
- Provide 3-5 specific recommendations that directly relate to today's news
- Explain exactly how each resource helps understand the specific deals mentioned"""

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
    def __init__(self):
        self.news_api = NewsApiClient(api_key=NEWS_API_KEY)
        self.customHttpXClient = httpx.Client(timeout=httpx.Timeout(120.0), # 120 s for connect/read/write/pool
                                              limits=httpx.Limits(max_connections=5, max_keepalive_connections=5)
                                             )
        self.openai_client = openai.Client(api_key=OPENAI_API_KEY,
                                            http_client=self.customHttpXClient)
        self.interview_generator = IBInterviewGenerator()
        self.briefs_dir = base_path / 'api' /'static'/'assets'/'briefs'
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
            sectionNum = 0
            number_of_news_collected = 0
            for category in CATEGORIES:
                response = requests.get(
                    f'https://newsapi.org/v2/everything',
                    params={
                        'q': category,
                        'from': date_str,
                        'sortBy': 'relevancy',  # Sort by relevance instead of date
                        'language': 'en',
                        'pageSize': 8,  # Reduced to avoid context length issues
                        'apiKey': NEWS_API_KEY
                    }
                )
                news_by_category = []
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
                            relevant_keywords = ['deal', 'merger', 'acquisition', 'valuation', 'billion', 'million', 
                                               'technology', 'ai', 'artificial intelligence', 'fintech', 'investment',
                                               'ipo', 'funding', 'venture capital', 'startup', 'tech', 'software']
                            
                            if any(keyword in (title + desc + content).lower() for keyword in relevant_keywords):
                                # Format article with source information and URL
                                formatted_article = f"""
                                Title: {title}
                                Description: {article.get('description', 'N/A')}
                                Content: {content}
                                Source: {article.get('source', {}).get('name', 'N/A')}
                                Published: {article.get('publishedAt', 'N/A')}
                                URL: {url}
                                """

                                news_by_category.append(formatted_article)
                        number_of_news_collected += len(news_by_category)
                else:
                    print(f"Error fetching news for category '{category}': {response.status_code}")
                print(f'Collected news for category "{category}"')
                news_items.append(news_by_category)
            print(f"Collected {number_of_news_collected} relevant news articles")
            return news_items
        except Exception as e:
            print(f"Error collecting news: {str(e)}")
            return []

    def analyze_news(self, news_items, prompts, categories_required):
        if not prompts:
            raise TypeError("Prompts matrix is missing or empty.")
        if len(news_items) != categories_required:
            raise ValueError(f"Mismatch: expected {categories_required} categories, got {len(news_items)}")

        # ─── Fill prompt contexts ───────────────────────────────────────────
        for idx, articles in enumerate(news_items):
            if not articles:
                raise ValueError(f'No news for category "{CATEGORIES[idx]}"')
            prompts[idx][1] = "\n\n".join(articles)

        analysis  = ""
        SYSTEM_MSG = (
            "You are a senior Investment Banking MD specializing in TMT M&A. "
            "Provide precise, data-driven analysis. Expand generic phrases into concrete "
            "examples with tickers, use bullet points, and link Recommended Readings to the report."
        )
        messages  = [{"role": "system", "content": SYSTEM_MSG}]

        # ——— Sections 1-5 ————————————————————————————————————————————————
        for idx, (section_prompt, context, max_tokens) in enumerate(prompts[:-1]):
            user_prompt = section_prompt + ("\n\n" + context if context else "")
            messages.append({"role": "user", "content": user_prompt})

            # keep system + last 4 turns (sliding window)
            context_window = [messages[0]] + messages[-4:]

            print(f"Sending section {idx + 1} …")
            resp = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=context_window,
                max_tokens=max_tokens,
                temperature=0.3,
                timeout=120
            )
            reply = resp.choices[0].message.content.strip()
            print(f"✓ got section {idx + 1}")

            analysis += "\n\n" + reply
            messages.append({"role": "assistant", "content": reply})

        # ——— Section 6 – Recommended Readings ————————————————
        readings_prompt, _, max_tokens = prompts[-1]
        messages.append({"role": "user", "content": readings_prompt})

        print("Generating Recommended Readings …")
        resp = self.openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[messages[0], messages[-1]],   # just system + this user prompt
            max_tokens=max_tokens,
            temperature=0.3,
            timeout=120
        )
        readings = resp.choices[0].message.content.strip()
        analysis += "\n\n" + readings

        return analysis
            

    def detect_technical_terms(self, analysis: str) -> dict:
        find_terms_prompt = f"""I need you to read this following TMT report on daily news, and identify every technical terms that 
                            someone that just got into the industry will find confusing. Then list them along side their definition in
                            this exact format:
                            term : short one line definition
                            Here's your report:
                            {analysis}
                            Note: do not include line numbers
                            instead of "1. CSSC: China State Shipbuilding Corporation", do "CSSC:China State Shipbuilding Corporation"
                            """
        try:
            response = self.openai_client.chat.completions.create(
                model = "gpt-3.5-turbo",
                messages=[
                    {'role': 'user', 'content': find_terms_prompt}
                ],
                temperature=0.2
            )
        except Exception as e:
            raise e
        
        #parse raw glossary from gpt3.5 and put them into glossary dictionary
        raw_glossary = response.choices[0].message.content
        glossary = {}
        for line in raw_glossary.splitlines():
            if ":" not in line:
                continue
            term, definition = line.split(": ", 1)
            if term and definition:
                glossary[term] = definition

        #get the dictionary from json file, put it into master_terms dict
        if json_path.exists():
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    master_terms = json.load(f)
            except json.JSONDecodeError:
                master_terms = {}
        else:
            master_terms = {}

        #merge the glossary from gpt3.5 with master dict and write it back
        master_terms.update(glossary)
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(master_terms, f, indent=2, ensure_ascii=False)

        return glossary

    def generate_daily_brief(self):
        """Generate a comprehensive daily briefing"""
        try:
            analysis = """
### 1. RECENT TMT M&A ACTIVITY

**Deal 1:**
**US banking giants reap gains from dealmaking rebound** ([Link](https://ca.finance.yahoo.com/news/us-banking-giants-reap-gains-132811723.html))  
- **Deal Size:** Not specified in news  
- **Valuation Multiples:** Not specified in news  
- **Companies:** Not specified in news  
- **Date Announced:** Not specified in news  
- **Rationale:** Large U.S. banks are experiencing a resurgence in investment banking activities, indicating a rebound in M&A activity driven by favorable market conditions.  
- **Risk:** Potential risks include market volatility and regulatory changes that could impact future deal-making activities.

**Deal 2:**
**Do Upstream Mergers Really Deliver Value for Shareholders?** ([Link](https://finance.yahoo.com/news/upstream-mergers-really-deliver-value-220000607.html))  
- **Deal Size:** Not specified in news  
- **Valuation Multiples:** Not specified in news  
- **Companies:** Not specified in news  
- **Date Announced:** Not specified in news  
- **Rationale:** The article discusses the effectiveness of large-scale mergers in the upstream energy sector, questioning whether they deliver tangible returns for shareholders, which could influence future M&A strategies in the TMT sector.  
- **Risk:** Risks include overvaluation of targets and the potential failure to realize expected synergies post-merger.

**Deal 3:**
**Weil, Gotshal & Manges and CMS lead European M&A legal advisers in H1 2025** ([Link](https://biztoc.com/x/386f06a4f953a88d))  
- **Deal Size:** Not specified in news  
- **Valuation Multiples:** Not specified in news  
- **Companies:** Not specified in news  
- **Date Announced:** Not specified in news  
- **Rationale:** The report highlights the leading legal advisers in European M&A, reflecting increased activity and the importance of legal frameworks in facilitating transactions in the TMT sector.  
- **Risk:** The primary risk involves potential legal challenges that could delay or derail M&A transactions.

### Summary of Notable M&A Trends
- The TMT sector is witnessing a cautious optimism as large U.S. banks report a rebound in deal-making activities, suggesting a potential increase in M&A transactions in the latter half of 2025.
- Companies are increasingly weighing the benefits of mergers against the backdrop of market volatility and regulatory scrutiny, particularly in the tech and media sectors.
- Legal advisement plays a crucial role in navigating the complexities of M&A, as highlighted by the performance of leading firms in Europe.

**Recommended Readings:**
- **M&A Enforcement Easing Under The Trump Administration** ([Link](https://www.forbes.com/sites/aldenabbott/2025/07/16/ma-enforcement-easing-under-the-trump-administration/))  
- **Trump's antitrust cops are OK with new mergers. Old tech monopolies, not so much.** ([Link](https://finance.yahoo.com/news/trumps-antitrust-cops-are-ok-with-new-mergers-old-tech-monopolies-not-so-much-140038953.html))

### MARKET DYNAMICS & SENTIMENT

The Technology, Media, and Telecommunications (TMT) sector is currently experiencing a complex landscape characterized by both optimism and caution. Overall sentiment remains cautiously optimistic, driven by advancements in technology, particularly in AI and quantum computing, alongside a rebound in M&A activities. However, challenges such as regulatory scrutiny and market volatility continue to pose risks.

#### Overall TMT Sector Sentiment
- **Subsector Breakdown:**
  - **Software:** The software subsector remains robust, with companies leveraging AI to enhance operational efficiencies. For instance, Delta Air Lines is utilizing AI to optimize ticket pricing, indicating a trend towards dynamic pricing models across industries ([Link](https://www.theverge.com/news/709556/delta-air-lines-ai-ticket-price-rollout)).
  - **Media:** The media sector is adapting to new content consumption patterns, with companies like Ring reintroducing features that allow users to share video footage with law enforcement, reflecting a growing intersection of technology and public safety ([Link](https://www.theverge.com/news/709836/ring-police-video-sharing-police-axon-partnership)).
  - **Telecom:** The telecom sector is facing pressure from regulatory changes and competition, particularly in the 5G rollout, which is critical for future growth.
  - **Fintech:** The fintech subsector is thriving, driven by innovations in payment processing and digital banking solutions, although it faces challenges from regulatory compliance.
  - **AI:** The AI sector is witnessing exponential growth, with analysts at Bank of America suggesting that quantum computing could represent a breakthrough comparable to the discovery of fire, emphasizing its transformative potential ([Link](https://finance.yahoo.com/news/quantum-computing-fire-no-seriously-190420811.html)).

#### Key Market Drivers and Headwinds
- **Drivers:**
  - **Technological Advancements:** Innovations in AI, quantum computing, and cloud technologies are driving growth. For example, Rivian's partnership with Google Maps to enhance EV navigation showcases the integration of advanced technology in consumer products ([Link](https://www.androidcentral.com/apps-software/google-maps/rivian-partners-with-google-maps-for-enhanced-ev-navigation-experience)).
  - **Increased M&A Activity:** A rebound in M&A activities, particularly among large U.S. banks, indicates a renewed confidence in the market, as firms seek strategic acquisitions to bolster their competitive positions.

- **Headwinds:**
  - **Regulatory Challenges:** Increased scrutiny from regulators, particularly in the tech sector, poses risks to M&A transactions and operational strategies.
  - **Market Volatility:** Economic uncertainties and geopolitical tensions could impact investment decisions and consumer spending.

#### Subsector Performance Analysis
- **Software:** Trading multiples for software companies have remained strong, with average EV/EBITDA multiples hovering around 20x, reflecting high investor confidence in growth potential.
- **Media:** Media companies are facing declining traditional revenue streams, leading to EV/EBITDA multiples around 12x, as they pivot towards digital content and streaming services.
- **Telecom:** Telecom companies are trading at lower multiples, averaging around 8x EV/EBITDA, due to high capital expenditures and competitive pressures.
- **Fintech:** Fintech firms are experiencing robust growth, with multiples around 15x EV/EBITDA, driven by digital transformation in financial services.
- **AI:** The AI subsector is seeing multiples soar, with some companies trading at 25x EV/EBITDA, as investors are eager to capitalize on the technology's potential.

#### Notable Investor/Analyst Reactions
- Analysts have expressed enthusiasm for the potential of quantum computing, with Bank of America stating, "This technology could warp-speed human knowledge and development," highlighting the transformative impact it could have across sectors ([Link](https://finance.yahoo.com/news/quantum-computing-fire-no-seriously-190420811.html)).
- Investors are closely monitoring regulatory developments, particularly in the tech sector, as these could significantly impact future valuations and M&A activities.

#### Actionable Insights for Bankers and Investors
- **Focus on Strategic Acquisitions:** With the rebound in M&A activity, bankers should identify potential targets that align with technological advancements, particularly in AI and software.
- **Monitor Regulatory Changes:** Investors should stay informed about regulatory developments that could impact the TMT sector, adjusting strategies accordingly.
- **Leverage Technological Trends:** Capitalize on the growth in AI and quantum computing by investing in companies that are at the forefront of these technologies, as they are likely to yield substantial returns in the long term.
- **Evaluate Valuation Multiples:** Investors should conduct thorough analyses of trading multiples across subsectors to identify undervalued opportunities, particularly in media and telecom, which may offer attractive entry points.

In conclusion, while the TMT sector is poised for growth driven by technological advancements and a resurgence in M&A activity, it is essential for stakeholders to navigate the complexities of regulatory challenges and market dynamics to maximize opportunities.

### BANKING PIPELINE

The current banking pipeline in the TMT sector reflects a dynamic landscape characterized by a mix of live deals, mandated transactions, and active pitches. This analysis provides a comprehensive overview of the ongoing and upcoming transactions, expected revenues, workload allocation, and strategic implications for our team.

#### Deal Pipeline Overview

**1. Live Deals:**
- **Transaction Type:** M&A in Due Diligence
  - **Companies Involved:** Nvidia (NVDA) and a leading Chinese tech firm
  - **Details:** Nvidia is resuming sales of its H20 AI chip to China, which could lead to a strategic partnership or acquisition discussions ([Link](https://www.cnn.com/2025/07/15/business/nvidia-resume-h20-chip-sales-to-china-intl-hnk)).
  - **Expected Timing:** Closing expected in Q3 2025.
  
- **Upcoming IPOs:**
  - **Company:** Rivian
  - **Details:** Rivian is preparing for an IPO to fund its expansion in electric vehicle technology, particularly in partnership with Google Maps.
  - **Expected Timing:** Q4 2025.

**2. Mandated Deals:**
- **Transaction Type:** M&A
  - **Client:** Delta Air Lines (DAL)
  - **Details:** Delta has secured a mandate for strategic acquisitions to enhance its AI capabilities in dynamic pricing, aiming to set 20% of ticket prices using AI by the end of 2025 ([Link](https://www.theverge.com/news/709556/delta-air-lines-ai-ticket-price-rollout)).
  - **Expected Timing:** Launching in Q2 2025.

**3. Pitching-Stage Deals:**
- **Sector Focus:** AI and Fintech
  - **Clients:** Several fintech startups looking to leverage AI for operational efficiencies.
  - **Details:** Active discussions are ongoing with potential clients in the AI-driven fintech space, focusing on digital payment solutions and risk management.
  - **Expected Timing:** Initial pitches scheduled for Q3 2025.

#### Pipeline Tracking Metrics

- **Expected Revenue/Fees:**
  - **Live Deals:** Estimated fees from live deals are projected at $5 million, with Nvidia's deal contributing approximately $2 million.
  - **Mandated Deals:** Expected fees from mandated deals are around $3 million, primarily from Delta Air Lines.
  - **Pitching-Stage Deals:** Potential fees from pitching-stage deals could reach $4 million if successful.

- **Timing Projections:**
  - **Q2 2025:** Anticipated close for Nvidia's partnership.
  - **Q4 2025:** Rivian's IPO is expected to launch, which could significantly impact market dynamics in the EV sector.

- **Workload Allocation and Capacity Analysis:**
  - Current bandwidth for analysts and associates is stretched due to the number of live and mandated deals. A review of team capacity indicates a need for additional resources, particularly in the due diligence phase of live deals.
  - **Analyst/Associate Bandwidth:** Currently at 70% capacity, suggesting the need for hiring or reallocating resources to manage the workload effectively.

- **Forecasting and Strategic Planning Implications:**
  - The pipeline indicates a strong potential for revenue growth in the upcoming quarters, particularly from AI and fintech sectors. Strategic planning should focus on enhancing capabilities in these areas to capitalize on emerging opportunities.

#### Notable Pipeline Developments and Competitive Landscape

- **Competitive Landscape:** The TMT sector is increasingly competitive, with major players like Meta aggressively recruiting top talent from competitors, such as Apple, to bolster their AI capabilities ([Link](https://www.macrumors.com/2025/07/17/meta-poaches-two-more-apple-ai-executives/)). This trend highlights the importance of talent acquisition in maintaining a competitive edge.
- **Market Dynamics:** The resurgence of M&A activity, particularly in the AI and fintech sectors, indicates a shift towards consolidation as companies seek to enhance their technological capabilities.

#### Actionable Insights for Team Management and Business Development

- **Resource Allocation:** Given the current workload, it is imperative to assess the need for additional hires or temporary resources to manage the increasing volume of deals effectively.
- **Focus on High-Growth Sectors:** Prioritize pitches and mandates in high-growth areas such as AI and fintech, as these sectors are expected to drive significant revenue in the coming years.
- **Enhance Client Engagement:** Strengthen relationships with existing clients, particularly those in the live and mandated deal stages, to ensure successful closings and capitalize on future opportunities.
- **Monitor Competitive Movements:** Stay informed about competitor activities, particularly in talent acquisition and technological advancements, to adapt strategies accordingly and maintain a competitive edge.

In conclusion, the current banking pipeline reflects a robust landscape with significant opportunities in the TMT sector. By strategically managing resources and focusing on high-growth areas, our team can position itself for success in the evolving market.

### STAKEHOLDER IMPACT & FORWARD-LOOKING ANALYSIS

The recent surge in deal-making activity within the TMT sector has significant implications for various stakeholders, including shareholders, employees, competitors, and customers. This analysis delves into the deal-specific impacts, market reactions, potential future developments, and actionable insights for clients and bankers.

#### Deal-Specific Impacts

**1. Shareholders:**
- **Value Creation/Dilution:**
  - **Scenario Analysis:** For a hypothetical acquisition of a fintech company by a larger tech firm, if the acquisition is valued at $1 billion with a share price of $50, the dilution effect on existing shareholders could be calculated as follows:
    - **Pre-Acquisition Market Cap:** $10 billion (200 million shares outstanding)
    - **Post-Acquisition Market Cap:** $11 billion (including acquisition value)
    - **New Shares Issued:** 20 million shares (to fund the acquisition)
    - **New Share Price:** $55 (assuming the market values the acquisition positively)
    - **Dilution Impact:** Existing shareholders see a dilution of 10% in their ownership percentage but benefit from the increased valuation.
  
- **Expected Outcomes:** If the acquisition leads to synergy realization of $200 million annually, the long-term value creation could outweigh the initial dilution, leading to a projected share price increase of 15% over the next 12 months.

**2. Employees:**
- **Synergies and Restructuring:**
  - **Example:** In the case of Delta Air Lines (DAL) integrating AI capabilities, employees involved in pricing strategy may see enhanced roles and job security due to increased operational efficiencies. However, there may be restructuring in IT departments to accommodate new AI systems.
  - **Retention Strategies:** Companies may implement retention bonuses for key talent during the transition period to mitigate turnover risks.

**3. Competitors:**
- **Market Positioning:**
  - **Competitor Moves:** As JPMorgan reported a 7% rise in investment banking fees, competitors like Goldman Sachs are also expected to ramp up their deal-making efforts, indicating a competitive landscape where firms are aggressively pursuing M&A opportunities to enhance market share ([Link](https://www.businessinsider.com/jpmorgan-second-quarter-earnings-surprise-gain-investment-banking-fees-dealmaking-2025-7)).
  - **Strategic Implications:** Competitors may respond with counter-offers or accelerated acquisition strategies to maintain their market position.

**4. Customers:**
- **Product/Service Implications:**
  - **Case Study:** The integration of AI in Delta's pricing strategy is expected to enhance customer experience by offering more personalized pricing, potentially increasing customer loyalty and satisfaction. This could lead to a 5% increase in ticket sales as customers respond positively to dynamic pricing models.
  - **Service Enhancements:** As companies like Nvidia resume sales of AI chips, customers in the tech sector can expect improved product offerings and faster innovation cycles.

#### Market Reaction and Analyst Commentary

- **Market Sentiment:** Analysts have expressed optimism regarding the rebound in deal-making, with JPMorgan's results serving as a bellwether for the sector. Jamie Dimon stated, "The investment banking outlook is brighter than expected, and we are well-positioned to capitalize on this momentum" ([Link](https://www.businessinsider.com/jpmorgan-second-quarter-earnings-surprise-gain-investment-banking-fees-dealmaking-2025-7)).
- **Expected Market Reaction:** If the current trends continue, analysts predict a bullish market reaction, particularly for firms actively engaging in strategic acquisitions. A positive earnings surprise could lead to a 10% increase in stock prices for major players in the sector.

#### Potential Counter-Bids or Competing Offers

- **Likelihood Assessment:** Given the competitive landscape, there is a high likelihood of counter-bids for attractive targets. For instance, if a major tech firm is pursuing a fintech acquisition, it is probable that other firms will enter the fray, particularly if the target has strong growth potential.
- **Example:** If a tech company announces an acquisition of a promising AI startup, competitors may quickly mobilize to make competing offers, reflecting the high stakes in the current environment.

#### Similar Deals Likely to Follow

- **Sector Consolidation Predictions:** The current deal-making environment suggests a trend towards consolidation in the TMT sector, particularly in AI and fintech. Analysts predict that companies will increasingly seek to acquire innovative startups to enhance their technological capabilities and market reach.
- **Future Deals:** Expect to see more strategic partnerships and acquisitions in the next 12-18 months as firms look to bolster their competitive positions.

#### Key Risks and Mitigants

- **Regulatory Risks:** Increased scrutiny from regulators could pose challenges for M&A transactions. Companies must conduct thorough due diligence and engage with regulatory bodies early in the process to mitigate these risks.
- **Market Volatility:** Economic uncertainties could impact valuations and deal closures. Firms should maintain flexible deal structures to accommodate potential market fluctuations.

#### Actionable Insights for Clients and Bankers

- **Strategic Focus:** Clients should prioritize strategic acquisitions that align with their long-term growth objectives, particularly in high-growth areas such as AI and fintech.
- **Proactive Engagement:** Maintain proactive communication with stakeholders to manage expectations and foster a collaborative environment during transitions.
- **Risk Management:** Develop comprehensive risk management strategies that account for regulatory changes and market volatility to ensure successful deal execution.

In conclusion, the current landscape presents both opportunities and challenges for stakeholders in the TMT sector. By understanding the implications of deal-making activities and preparing for potential market shifts, clients and bankers can position themselves for success in the evolving market.

### TECH TRENDS

The technology landscape is rapidly evolving, with several key trends emerging that have significant market impact and deal-making potential. This analysis identifies and explores these trends, including AI, Stablecoins, and Cloud Computing, highlighting their market significance, growth trajectories, and the competitive landscape.

#### 1. Artificial Intelligence (AI)

**Trend Explanation:**
AI continues to revolutionize various sectors, enhancing operational efficiencies, improving customer experiences, and driving innovation. The market for AI is projected to grow from $136.55 billion in 2022 to $1,811.75 billion by 2030, at a CAGR of 38.1% ([Source](https://www.researchnester.com/reports/artificial-intelligence-market/3107)).

**Key Companies:**
- **Stripe (STRIP):** Stripe's CEO, Patrick Collison, emphasizes the use of AI for answering factual questions, indicating a strategic focus on integrating AI to streamline operations and enhance customer service ([Link](https://www.businessinsider.com/stripe-ceo-patrick-collison-ai-ask-questions-writing-grok-2025-7)).
- **Nvidia (NVDA):** A leader in AI hardware and software, Nvidia's GPUs are critical for AI applications, and the company is actively involved in developing AI solutions for various industries.

**Competitive Landscape:**
The AI market is highly competitive, with major players like Google (GOOGL), Microsoft (MSFT), and Amazon (AMZN) investing heavily in AI capabilities. The competition is driving innovation but also leading to potential M&A activity as companies seek to acquire niche AI startups to enhance their offerings.

**M&A Opportunities:**
- **Potential Acquisitions:** Companies like Nvidia may look to acquire smaller AI startups to bolster their technology stack, particularly in areas like natural language processing and machine learning.

**Investment Implications:**
Investors should consider companies that are not only leaders in AI but also those that are integrating AI into their business models, as these firms are likely to see significant growth.

#### 2. Stablecoins

**Trend Explanation:**
Stablecoins are gaining traction as a bridge between traditional finance and cryptocurrencies, providing a stable digital currency option. The GENIUS Act, aimed at regulating digital currencies, could allow banks to issue stablecoins, which is expected to significantly impact the financial landscape ([Link](https://www.businessinsider.com/wall-street-banks-stablecoin-goldman-jpmorgan-citi-bofa-morgan-stanley-2025-7)).

**Key Companies:**
- **JPMorgan Chase (JPM):** JPMorgan is exploring stablecoin issuance as part of its digital currency strategy, positioning itself as a leader in the evolving digital finance space.
- **Goldman Sachs (GS):** Goldman is also actively involved in stablecoin discussions, indicating a strong interest in leveraging stablecoins for transaction efficiency.

**Competitive Landscape:**
The stablecoin market is becoming increasingly competitive, with traditional banks and fintech companies vying for market share. The entry of major banks into the stablecoin space could lead to increased regulatory scrutiny and competition.

**M&A Opportunities:**
- **Strategic Partnerships:** Banks may seek to partner with fintech firms specializing in blockchain technology to develop robust stablecoin solutions.

**Investment Implications:**
Investors should monitor developments in the stablecoin regulatory landscape, as favorable regulations could lead to significant growth in this

### Recommended Readings

**1. Microsoft’s Acquisition of Activision Blizzard (MSFT, ATVI)**
- **Brief description of what happened:** Microsoft announced its intention to acquire Activision Blizzard for approximately $68.7 billion, marking one of the largest deals in the gaming sector.
  
  → **Why this matters:** This acquisition highlights the increasing convergence of gaming and technology, as well as the strategic importance of gaming content in enhancing Microsoft's cloud and subscription services.

  → **Read this to understand:** "The Business of Video Games" by Michael P. Wolf - Chapter 4 on mergers and acquisitions in the gaming industry.

  → **Key concept to learn:** Understanding the strategic rationale behind M&A in the tech and gaming sectors, including synergies and market expansion.

---

**2. NVIDIA’s $40 Billion Acquisition of Arm Holdings (NVDA)**
- **Brief description of what happened:** NVIDIA announced its intention to acquire Arm Holdings, a key player in semiconductor design, for $40 billion, although the deal faced regulatory hurdles.

  → **Why this matters:** This deal underscores the critical role of semiconductor technology in powering AI and machine learning applications, as well as the competitive landscape in the chip industry.

  → **Read this to understand:** "Chip War: The Fight for the World's Most Critical Technology" by Chris Miller - Chapter 5 on the semiconductor industry's consolidation trends.

  → **Key concept to learn:** The importance of vertical integration in technology sectors and the implications of regulatory scrutiny on large tech acquisitions.

---

**3. Stripe’s $6.5 Billion Funding Round**
- **Brief description of what happened:** Stripe raised $6.5 billion in a funding round to expand its payment processing capabilities and enhance its product offerings.

  → **Why this matters:** This funding round reflects the ongoing investor confidence in fintech, particularly as digital payment solutions become increasingly essential in a post-pandemic economy.

  → **Read this to understand:** "Venture Deals" by
"""
            
        
            print("Formatting report...")
            filename = self.format_brief(analysis)
            return filename
            
        except Exception as e:
            print(f"Error generating brief: {str(e)}")
            raise


    def format_brief(self, analysis):
        """Format the analysis into a professional PDF brief"""
        # Generate filename with today's date
        today = datetime.now().strftime('%Y-%m-%d')
        filename = os.path.join(self.briefs_dir, f'TMT_Brief_{today}.pdf')
        
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
                # Check if this is a main section header (numbered, e.g., '1.', '2.', ..., '6.')
                first_line = section.strip().split('\n')[0]
                if re.match(r'^\d+\.', first_line):
                    # Clean the header and apply formatting
                    header = first_line.replace('#', '').replace('*', '').strip()
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
    
    # More aggressive cleaning - convert to ASCII and handle errors gracefully
    try:
        # First try to encode as UTF-8 and decode as ASCII
        text = text.encode('utf-8').decode('ascii', errors='ignore')
    except:
        # If that fails, use a more aggressive approach
        text = ''.join(char for char in text if ord(char) < 128)
    
    return text.strip()



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