import openai
from config import NEWS_API_KEY, OPENAI_API_KEY, NEWS_LOOKBACK_DAYS
from newsapi.newsapi_client import NewsApiClient
import httpx
from datetime import datetime, timedelta
from interview_generator import IBInterviewGenerator
from pathlib import Path
import os
import requests
import json
from datetime import date, timedelta
import re
from transcript_crawler import fetch_latest_transcript
#from main import base_path, json_path

base_path = Path(__file__).resolve().parent.parent 
raw_dir = base_path / 'api' / "static" / "assets" / "raw"
json_path = base_path/ 'api' / 'term_definitions.json'
brief_dir = base_path / 'api' / 'static' / 'assets' / 'briefs'

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
        
    def collect_news(self, CATEGORIES):
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

                            date_str = str(article.get('publishedAt', 'N/A'))
                            date_list = date_str[: 10].split("-")
                            date_OBJ = date(*map(int, date_list))
                            seven_days_ago = date.today() - timedelta(days=7)

                            if date_OBJ < seven_days_ago:
                                raise ValueError(f"Bad news date: {date_str} for article: {title}, news articles cannot be older than 7 days")

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

    def analyze_news(self, news_items, prompts, categories_required, CATEGORIES):
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
            """You are a senior Investment Banking MD specializing in TMT M&A.
            Provide precise, data-driven analysis. Expand generic phrases into concrete 
            examples with tickers, use bullet points, and link Recommended Readings to the report.
            You should only use articles provided by the users.
            Take special care to formatting and follow the guidelines provided by users strictly.
            When adding links, use this EXACT format: **Link title** ([Link](https://linkURL))
            example: **JPMorgan Reports Increased M&A Activity in TMT Sector** ([Link](https://www.businessinsider.com/merger-acquisition-trends-1h-hreport-sponsors-volumes-anu-aiyengar-jpmorgan-2025-7))
            MAKE SURE THE LINKS MATCH THEIR TITLES
            For each link, ensure the link format is strictly maintained without any changes,
            and ensure that the link is valid and reachable. Do not modify the URL, and avoid any broken links."""
        )
        messages  = [{"role": "system", "content": SYSTEM_MSG}]

        # ——— Sections 1-5 ————————————————————————————————————————————————
        for idx, (section_prompt, context, max_tokens) in enumerate(prompts[:5]):
            max_token_limit = f"You have a maximum of {max_tokens}.\n Consider the token limit when writing reports and delegate them fairly."
            user_prompt = max_token_limit + section_prompt + ("\n You should only use these following news for this section: \n\n" + context if context else "")
            messages.append({"role": "user", "content": user_prompt})

            # keep system + last 2 turns (sliding window)
            context_window = [messages[0]] + messages[-2:]

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
        readings_prompt, _, max_tokens = prompts[5]
        messages.append({"role": "user", "content": readings_prompt})

        print("Generating Recommended Readings …")
        resp = self.openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[messages[0], messages[2], messages[-1]],   # just system + response for section 1+ this user prompt
            max_tokens=max_tokens,
            temperature=0.3,
            timeout=120
        )
        readings = resp.choices[0].message.content.strip()
        analysis += "\n\n" + readings
        print(f"✓ got recommended readings")

        # ——— Section 7 – Macro Economics ————————————————
        print(f"Using crawler to extract podcast transcript...")
        podcast_transcript = fetch_latest_transcript()
        print(f"✓ got podcast transcript")
        podcast_prompt, _, max_tokens = prompts[6]
        podcast_prompt += "\n\n Here is the latest transcript: \n" + podcast_transcript
        messages.append({"role": "user", "content": podcast_prompt})

        print("Sending request for podcast (section 7)...")
        resp = self.openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[messages[0], messages[2], messages[-1]],   # just system + response for section 1+ this user prompt
            max_tokens=max_tokens,
            temperature=0.3,
            timeout=120
        )

        resp = resp.choices[0].message.content.strip()
        analysis += "\n\n" + resp
        return analysis
    
    def verify_link(self, url):
        try:
            response = requests.head(url, timeout=10)
            if response.status_code == 200:
                return True
            else:
                return False
        except requests.RequestException:
            return False
        
    def gather_information_via_gpt(self, user_prompt: str, link: str = None):
        """
        Simple helper method to gether information via gpt4o-mini-search-preview
        Pass in user prompt and optional source link to look at specifically
        """
        if link:
            user_prompt += "\n\n" + f"This is the link: {link}"

        response = self.openai_client.chat.completions.create(
            model="gpt-4o-mini-search-preview", 
            web_search_options={},
            messages=[{"role": "user", "content": user_prompt}]
        )
        response = response.choices[0].message.content.strip()
        return response


    def search_article_via_gpt(self, title, link):
        print(f"searching for link for {title}...")
        search_prompt = f"""Please search for the latest news article with the title '{title}' on the same website as this link: {link}. 
        Provide the full URL if available. And have ONLY ONE WORKING URL (which is the URL for the article you found) in an independent line in your response and NOTHING ELSE.
        When adding links, use this EXACT format: **Link title** ([Link](https://linkURL))
        example: **JPMorgan Reports Increased M&A Activity in TMT Sector** ([Link](https://www.businessinsider.com/merger-acquisition-trends-1h-hreport-sponsors-volumes-anu-aiyengar-jpmorgan-2025-7))
        """
        
        response = self.openai_client.chat.completions.create(
            model="gpt-4o-mini-search-preview", 
            web_search_options={},
            messages=[{"role": "user", "content": search_prompt}]
        )

        # Extract the URL from the response
        response = response.choices[0].message.content.strip()
        found_url = re.findall(r'\[Link\]\((https?://[^\s]+)\)', response)
        
        # Check if URL looks valid and return it
        if found_url:  # basic check to see if URL is provided
            url = found_url[0][:-1]
            print(url)
            return url
        else:
            return None

    def replace_broken_links(self, analysis: str):
        link_pat   = re.compile(r'\*\*(?P<title>.+?)\*\*\s*\(\s*\[Link\]\((?P<url>https?://[^\s)]+)\)\s*\)') #links
        hits = re.findall(link_pat, analysis)
        for hit in hits:
            title = hit[0]
            link = hit[1]
            if link and not self.verify_link(link):
                # Search for the article using GPT
                new_link = self.search_article_via_gpt(title, link)

                if new_link and self.verify_link(new_link):
                    print(f"✓ found working link for {title}")
                    print(f"Replaced link for {title}")
                    # Replace old broken link with new one
                    analysis = analysis.replace(link, new_link)
                else:
                    print(f"link not found for '{title}'...")
        
        return analysis
            

    def detect_technical_terms(self, analysis: str) -> dict:
        find_terms_prompt = f"""I need you to read this following report on daily news, and identify every technical terms that 
                            someone that just got into the industry will find confusing. Then list them along side their definition in
                            this exact format:
                            term : short one line definition
                            Here's your report:
                            {analysis}
                            Note: do not include line numbers, and do not include overly simple words like "risks"
                            instead of '1. CSSC: China State Shipbuilding Corporation', do 'CSSC:China State Shipbuilding Corporation'
                            """
        try:
            response = self.openai_client.chat.completions.create(
                model = "gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert finance instructor. Read the user-supplied TMT report, "
                    "find every technical finance, M&A, or market term that a newcomer might "
                    "not understand, and output them as one term per line in the exact format "},
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
                term: str = term.strip().lower()
                definition: str = definition.strip().lower()
                print(f"{term} : {definition}")
                glossary[term] = definition
        #print(f"terms gathered today: \n{glossary}")

        #get the dictionary from json file, put it into master_terms dict
        if json_path.exists():
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    print("\n\nFound JSON dictionary")
                    master_terms = json.load(f)
            except json.JSONDecodeError:
                print("Failed to get JSON dictionary")
                master_terms = {}
        else:
            print(f"Error: JSON file doesn't exist in path {json_path.resolve()}")
            master_terms = {}

        #merge the glossary from gpt3.5 with master dict and write it back
        print("Merging and writing updated glossary...")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(master_terms, f, indent=2, ensure_ascii=False)
        print(f"✓ Glossary written successfully")

        return glossary

    
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
        


