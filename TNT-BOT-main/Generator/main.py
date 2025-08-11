from pathlib import Path
from report_generator import IBDMarketAnalyst
from pdf_report import *
from config import TMT_CATEGORIES, ENERGY_CATEGORIES
from prompts import TMT_prompt, Energy_prompt

base_path = Path(__file__).resolve().parent.parent 
raw_dir = base_path / 'api' / "static" / "assets" / "raw"
json_path = base_path/ 'term_definitions.json'
brief_dir = base_path / 'api' / 'static' / 'assets' / 'briefs'



def generate_daily_brief(analyzer: IBDMarketAnalyst, prompts, brief_path, category, sector, text_file_name):
        """Generate a comprehensive daily briefing"""
        try:
            print("Collecting news articles...")
            news = analyzer.collect_news(category)
            if not news:
                raise Exception("No news articles found")
            
            print(f"Analyzing the news articles...")
            analysis = analyzer.analyze_news(news, prompts, 5, category) 
            if not analysis:
                raise Exception("Failed to generate analysis")
            
            print("Storing API output into txt file...")
            with open(raw_dir/text_file_name, "w") as file:
                file.write(analysis)
            print(f"file created as {file.name}")

            print("Testing links...")
            analyzer.replace_broken_links(analysis)
            print(f"✓ Links tested")
            
            print("Requesting gpt3.5 for technical terms definitions...")
            if not analyzer.detect_technical_terms(analysis):
                raise Exception
        
            print("Formatting report...")
            filename = format_brief(analysis, brief_path, sector)
            return filename
            
        except Exception as e:
            print(f"Error generating brief: {str(e)}")
            raise

def main():
    """Main execution function"""
    try:
        # Initialize the analyzer
        analyzer = IBDMarketAnalyst()
        #category = int(input("Enter 1 to generate TMT report\nEnter 2 to generate energy report: "))
        category = 3
        sector = category
        prompts = []
        text_file_name = ""
        match category:
            case 1:
                category = TMT_CATEGORIES
                prompts = TMT_prompt
                text_file_name = f"TMT_Brief_{str(datetime.now().strftime("%Y-%m-%d"))}_raw.txt"
            case 2:
                category = ENERGY_CATEGORIES
                prompts = Energy_prompt
                text_file_name = f"Energy_Brief_{str(datetime.now().strftime("%Y-%m-%d"))}_raw.txt"
            case 3: #run both in one go
                print("Start generating TMT brief...")
                category = TMT_CATEGORIES
                prompts = TMT_prompt
                text_file_name = f"TMT_Brief_{str(datetime.now().strftime("%Y-%m-%d"))}_raw.txt"
                brief_path = generate_daily_brief(analyzer, prompts, brief_dir, category, sector, text_file_name)

                print("Start generating Energy Brief")
                category = ENERGY_CATEGORIES
                prompts = Energy_prompt
                text_file_name = f"Energy_Brief_{str(datetime.now().strftime("%Y-%m-%d"))}_raw.txt"
                brief_path = generate_daily_brief(analyzer, prompts, brief_dir, category, sector, text_file_name)
            case _:
                return 
        # Generate the brief
        brief_path = generate_daily_brief(analyzer, prompts, brief_dir, category, sector, text_file_name)
        
        print(f"\nAnalysis completed successfully!")
        print(f"Focused brief saved to: {brief_path}")
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        if "insufficient_quota" in str(e):
            print("Please set up billing at platform.openai.com/account/billing")

if __name__ == "__main__":
    main() 
