import os
from datetime import datetime

class NewsAnalyzer:
    def run(self):
        print("Collecting news articles...")
        articles = self.collect_news()
        
        print(f"Analyzing {len(articles)} news articles...")
        analysis = self.analyze_news(articles)
        
        print("Formatting report...")
        today = datetime.now().strftime("%Y-%m-%d")
        # Use absolute path to ensure correct location
        output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "daily_briefs")
        os.makedirs(output_dir, exist_ok=True)
        filename = os.path.join(output_dir, f"brief_{today}.pdf")
        
        # Clean special characters from analysis
        analysis = analysis.replace('"', '"').replace('"', '"').replace(''', "'").replace(''', "'")
        
        self.generate_pdf(analysis, filename)
        print(f"\nAnalysis completed successfully!")
        print(f"Focused brief saved to: {filename}") 