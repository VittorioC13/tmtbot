from pathlib import Path
from report_generator import IBDMarketAnalyst
from datetime import datetime
from pdf_report import *
from config import TMT_CATEGORIES, ENERGY_CATEGORIES, HEALTHCARE_CATEGORIES
from prompts import TMT_prompt, Energy_prompt, Healthcare_prompt
from email_briefs import send_emails

base_path = Path(__file__).resolve().parent.parent 
raw_dir = base_path / 'api' / "static" / "assets" / "raw"
json_path = base_path / 'api' / 'term_definitions.json'
brief_dir = base_path / 'api' / 'static' / 'assets' / 'briefs'



def generate_daily_brief(analyzer: IBDMarketAnalyst, prompts, brief_path, category, sector, text_file_name):
        """Generate a comprehensive daily briefing"""
        try:
            print("Collecting news articles...")
            news = analyzer.collect_news(category)
            if not news:
                raise Exception("No news articles found")
            
            print(f"Analyzing the news articles...")
            analysis = analyzer.analyze_news(news, prompts, len(category), category) 
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
        choice = 3
        prompts = []
        text_file_name = ""
        match choice:
            case 1:
                print("Start generating TMT Brief...")
                category = TMT_CATEGORIES
                prompts = TMT_prompt
                text_file_name = f"TMT_Brief_{str(datetime.now().strftime("%Y-%m-%d"))}_raw.txt"
                sector = "TMT"
            case 2:
                print("Start generating Energy Brief...")
                category = ENERGY_CATEGORIES
                prompts = Energy_prompt
                text_file_name = f"Energy_Brief_{str(datetime.now().strftime("%Y-%m-%d"))}_raw.txt"
                sector = "Energy"
            case 3:
                print("Start generating Healthcare Brief...")
                category = HEALTHCARE_CATEGORIES
                prompts = Healthcare_prompt
                text_file_name = f"Healthcare_Brief_{str(datetime.now().strftime("%Y-%m-%d"))}_raw.txt"
                sector = "Healthcare"
            case 4: #run everything in one go
                sectors = ["TMT", "Energy", "Healthcare"]
                categories = [TMT_CATEGORIES, ENERGY_CATEGORIES, HEALTHCARE_CATEGORIES]
                prompt_matrices = [TMT_prompt, Energy_prompt, Healthcare_prompt]

                try:
                    for sector, category, prompts in zip(sectors, categories, prompt_matrices):
                        print(f"Start generating {sectors[i]} brief...")
                        text_file_name = f"{sector}_Brief_{str(datetime.now().strftime("%Y-%m-%d"))}_raw.txt"
                        brief_path = generate_daily_brief(analyzer, prompts, brief_dir, category, sector, text_file_name)
                        print(f"{sector} Analysis completed successfully!")
                        print(f"Focused brief saved to: {brief_path}")
                except:
                    print(f"Error generating {sectors[i]} brief: {str(e)}")
                print("All done, now sending briefs and raws via email...")
                send_emails()
                print("✓ Emails sent")
                return
            case _:
                return 
        # Generate the brief
        brief_path = generate_daily_brief(analyzer, prompts, brief_dir, category, sector, text_file_name)
        
        print(f"Analysis completed successfully!")
        print(f"Focused brief saved to: {brief_path}")
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        if "insufficient_quota" in str(e):
            print("Please set up billing at platform.openai.com/account/billing")

if __name__ == "__main__":
    main() 
