#!/usr/bin/env python3
"""
Script to generate a PDF in the static-website/assets folder
"""

import sys
import os

# Add the news collector directory to the path
sys.path.append('IBD TMT - News Collector')

from main import IBDMarketAnalyst, process_section_content
from datetime import datetime, timedelta
import requests
from config import NEWS_API_KEY, CATEGORIES

def collect_broader_news():
    """Collect news with broader criteria to ensure we get content"""
    try:
        # Look back 3 days instead of 1
        three_days_ago = datetime.now() - timedelta(days=3)
        date_str = three_days_ago.strftime('%Y-%m-%d')
        
        news_items = []
        for category in CATEGORIES:
            response = requests.get(
                f'https://newsapi.org/v2/everything',
                params={
                    'q': category,
                    'from': date_str,
                    'sortBy': 'relevancy',
                    'language': 'en',
                    'pageSize': 15,  # Increased from 10
                    'apiKey': NEWS_API_KEY
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('articles'):
                    for article in data['articles']:
                        # Relaxed filtering - include more articles
                        title = article.get('title', '') or ''
                        desc = article.get('description', '') or ''
                        content = title + ' ' + desc
                        
                        # Include if it mentions any relevant terms
                        relevant_terms = ['deal', 'merger', 'acquisition', 'valuation', 'billion', 'million', 
                                        'tech', 'ai', 'artificial intelligence', 'investment', 'fintech', 
                                        'startup', 'funding', 'ipo', 'venture', 'capital']
                        
                        if any(term in content.lower() for term in relevant_terms):
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

def generate_pdf_in_assets():
    """Generate a PDF in the static-website/assets folder"""
    
    try:
        print("🚀 Generating TMT Brief PDF in static-website/assets...")
        
        # Initialize the analyzer
        analyzer = IBDMarketAnalyst()
        
        # Override the briefs directory to save in assets
        assets_dir = 'static-website/assets'
        os.makedirs(assets_dir, exist_ok=True)
        
        # Generate the brief with broader news collection
        print("📊 Collecting news articles (broader search)...")
        news = collect_broader_news()
        if not news:
            raise Exception("No news articles found even with broader search")
        
        print(f"🔍 Analyzing {len(news)} news articles...")
        analysis = analyzer.analyze_news(news)
        if not analysis:
            raise Exception("Failed to generate analysis")
        
        # Generate filename with today's date
        today = datetime.now().strftime('%Y-%m-%d')
        filename = os.path.join(assets_dir, f'TMT_Brief_{today}.pdf')
        
        print("📄 Creating PDF with enhanced formatting...")
        
        # Use the analyzer's format_brief method which includes all our improvements
        # Temporarily change the briefs directory
        original_briefs_dir = analyzer.briefs_dir
        analyzer.briefs_dir = assets_dir
        
        # Generate the brief using the improved format_brief method
        pdf_filename = analyzer.format_brief(analysis)
        
        # Restore original directory
        analyzer.briefs_dir = original_briefs_dir
        
        # Rename the file to match the expected naming convention
        if pdf_filename and os.path.exists(pdf_filename):
            new_filename = os.path.join(assets_dir, f'TMT_Brief_{today}.pdf')
            os.rename(pdf_filename, new_filename)
            pdf_filename = new_filename
        
        if pdf_filename and os.path.exists(pdf_filename):
            print(f"✅ PDF generated successfully!")
            print(f"📁 Location: {pdf_filename}")
            print(f"📊 File size: {os.path.getsize(pdf_filename)} bytes")
            
            # Also create an index.html file to make the PDF easily accessible
            create_index_html(assets_dir, today)
            
            return pdf_filename
        else:
            raise Exception("PDF file was not created successfully")
        
    except Exception as e:
        print(f"❌ Error generating PDF: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def create_index_html(assets_dir, today):
    """Create an index.html file to make the PDF easily accessible"""
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TMT Sector M&A & Valuation Brief - {today}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            background: white;
            padding: 40px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        h1 {{
            color: #2c3e50;
            margin-bottom: 10px;
        }}
        .subtitle {{
            color: #7f8c8d;
            font-size: 18px;
            margin-bottom: 30px;
        }}
        .download-btn {{
            display: inline-block;
            background: #3498db;
            color: white;
            padding: 15px 30px;
            text-decoration: none;
            border-radius: 8px;
            font-weight: 600;
            transition: background 0.3s;
        }}
        .download-btn:hover {{
            background: #2980b9;
        }}
        .features {{
            margin-top: 40px;
            padding: 20px;
            background: #ecf0f1;
            border-radius: 8px;
        }}
        .features h3 {{
            color: #2c3e50;
            margin-bottom: 15px;
        }}
        .features ul {{
            color: #34495e;
            line-height: 1.6;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>TMT Sector M&A & Valuation Brief</h1>
        <p class="subtitle">Technology, Media & Telecommunications Sector Analysis</p>
        <p>Generated on {today}</p>
        
        <a href="TMT_Brief_{today}.pdf" class="download-btn" download>
            📄 Download Latest Brief
        </a>
        
        <div class="features">
            <h3>📊 What's Included:</h3>
            <ul>
                <li><strong>Recent TMT M&A Activity:</strong> Real deals from actual news sources</li>
                <li><strong>Market Dynamics & Sentiment:</strong> Comprehensive sector analysis</li>
                <li><strong>Banking Pipeline:</strong> Deal pipeline insights and metrics</li>
                <li><strong>Stakeholder Impact:</strong> Forward-looking analysis and risks</li>
                <li><strong>Tech Trends:</strong> Emerging technologies and company analysis</li>
            </ul>
        </div>
        
        <div class="features">
            <h3>✨ Enhanced Features:</h3>
            <ul>
                <li>Anti-fabrication protection - only real deals from news</li>
                <li>Smart date formatting under deal names</li>
                <li>Professional bullet point formatting</li>
                <li>Inline bold headings for key insights</li>
                <li>Optimized spacing and visual hierarchy</li>
            </ul>
        </div>
    </div>
</body>
</html>"""
    
    index_path = os.path.join(assets_dir, 'index.html')
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"📄 Created index.html for easy access")

if __name__ == "__main__":
    generate_pdf_in_assets() 