from pathlib import Path
from report_generator import IBDMarketAnalyst
from datetime import datetime
from pdf_report import *
from config import TMT_CATEGORIES, ENERGY_CATEGORIES, HEALTHCARE_CATEGORIES, INDUSTRIAL_CATEGORIES, CONSUMER_CATEGORIES
from prompts import TMT_prompt, Energy_prompt, Healthcare_prompt, Industrial_prompt, Consumer_prompt
from email_briefs import send_emails

base_path = Path(__file__).resolve().parent.parent 
raw_dir = base_path / 'api' / "static" / "assets" / "raw"
json_path = base_path / 'api' / 'term_definitions.json'
brief_dir = base_path / 'api' / 'static' / 'assets' / 'briefs'
context_dir = base_path / 'api' / 'static' / 'assets' / 'context'
TLDR_dir = base_path / 'api' / 'static' / 'assets' / 'TLDR'
region_list = ["US", "Europe", "APAC"]



def generate_daily_brief(analyzer: IBDMarketAnalyst, prompts, brief_path, category, sector, text_file_name, sections, today, region):
        """Generate a comprehensive daily briefing"""
        try:
            print("Collecting news articles...")
            news = analyzer.collect_news(category, region)
            if not news:
                raise Exception("No news articles found")

            print("Now selecting best articles for later use...")
            links, companies = analyzer.choose_best_news_with_gpt(news, sections, sector, region)

            print("Crawling actual content of the previously selected articles...")
            news = analyzer.find_news_populate_context(links, companies, region)

            print("Storing news context...")
            file_name = f'{region}_{sector}_context_{today}.txt'
            context_dir.mkdir(parents=True, exist_ok=True)  # Ensure path exists

            with open(context_dir / file_name, "w", encoding="utf-8") as file:
                for section_context in news:
                    file.write(section_context.strip())  # write each article group
                    file.write("\n\n" + "="*80 + "\n\n")  # section separator

            print(f"Context file created as {file.name}")

            
            print(f"Analyzing the news articles...")
            analysis = analyzer.analyze_news(news, prompts, len(category), category) 
            if not analysis:
                raise Exception("Failed to generate analysis")
            
            print("Storing API output into txt file...")
            with open(raw_dir/text_file_name, "w") as file:
                file.write(analysis)
            print(f"file created as {file.name}")

            print("Testing links...")
            analysis = analyzer.replace_broken_links(analysis)
            print(f"✓ Links tested")
            
            print("Requesting gpt3.5 for technical terms definitions...")
            if not analyzer.detect_technical_terms(analysis):
                raise Exception
        
            print("Formatting report...")
            filename = format_brief(analysis, brief_path, sector, region)

            print("Generating TLDR...")
            TLDR = analyzer.generate_TLDR(analysis, sector, region)
            
            print("Formatting TLDR...")
            TLDR_filename = format_brief(TLDR, TLDR_dir, sector, region, True)
            
        except Exception as e:
            print(f"Error generating brief: {str(e)}")
            raise

def main(choice):
    """Main execution function"""
    try:
        # Initialize the analyzer
        analyzer = IBDMarketAnalyst()
        #category = int(input("Enter 1 to generate TMT report\nEnter 2 to generate energy report: "))
        prompts = []
        text_file_name = ""
        region = "US"
        today = str(datetime.now().strftime("%Y-%m-%d"))
        sector = ""
        match choice:
            case 1:
                print("Start generating Consumer Brief...")
                category = ENERGY_CATEGORIES
                prompts = Energy_prompt
                region = "Europe"
                sector = "US"
                text_file_name = f"{region}_{sector}_Brief_{today}_raw.txt"
                sections = [f"RECENT {sector} M&A ACTIVITY", "MARKET DYNAMICS & SENTIMENT", "BANKING PIPELINE",
                            "STAKEHOLDER IMPACT & FORWARD-LOOKING ANALYSIS", f"{sector} TRENDS"]
            case 2:
                print("Start generating Energy Brief...")
                category = TMT_CATEGORIES
                prompts = TMT_prompt
                sector = "TMT"
                region = "US"
                text_file_name = f"{region}_{sector}_Brief_{today}_raw.txt"
                sections = [f"RECENT {sector} M&A ACTIVITY", "MARKET DYNAMICS & SENTIMENT", "BANKING PIPELINE",
                            "STAKEHOLDER IMPACT & FORWARD-LOOKING ANALYSIS", f"{sector} TRENDS"]
            case 3:
                print("Start generating Europe TMT Brief...")
                category = INDUSTRIAL_CATEGORIES
                prompts = Industrial_prompt
                region = "Europe"
                text_file_name = f"Europe_Industry_Brief_{today}_raw.txt"
                sector = "Industry"
                sections = [f"RECENT {sector} M&A ACTIVITY", "MARKET DYNAMICS & SENTIMENT", "BANKING PIPELINE",
                            "STAKEHOLDER IMPACT & FORWARD-LOOKING ANALYSIS", f"{sector} TRENDS"]
            case 4: #run everything in one go
                sectors = ["TMT", "Energy", "Healthcare", "Industry", "Consumer"]
                categories = [TMT_CATEGORIES, ENERGY_CATEGORIES, HEALTHCARE_CATEGORIES, INDUSTRIAL_CATEGORIES, CONSUMER_CATEGORIES]
                prompt_matrices = [TMT_prompt, Energy_prompt, Healthcare_prompt, Industrial_prompt, Consumer_prompt]
                for region in region_list:
                    print(f"Running {region} briefs...")
                    try:
                        for sector, category, prompts in zip(sectors, categories, prompt_matrices):
                            sections = [f"RECENT {sector} M&A ACTIVITY", "MARKET DYNAMICS & SENTIMENT", "BANKING PIPELINE",
                            "STAKEHOLDER IMPACT & FORWARD-LOOKING ANALYSIS", f"{sector} TRENDS"] * len(prompt_matrices)
                            print(f"Start generating {region} {sector} brief...")
                            #text_file_name = f"{region}_{sector}_Brief_{today}_raw.txt"
                            text_file_name = f"{region}_{sector}_Brief_{today}_raw.txt"
                            brief_path = generate_daily_brief(analyzer, prompts, brief_dir, category, sector, text_file_name, sections, today, region)
                            print(f"{region} {sector} Analysis completed successfully!")
                            print(f"Focused brief saved to: {brief_path}")
                    except Exception as e:
                        print(f"Error generating {sector} brief: {str(e)}")
                print("All done, now sending briefs and raws via email...")
                send_emails()
                print("✓ Emails sent")
                return
            case _:
                return 
        # Generate the brief
        brief_path = generate_daily_brief(analyzer, prompts, brief_dir, category, sector, text_file_name, sections, today, region)
        
        print(f"Analysis completed successfully!")
        print(f"Focused brief saved to: {brief_path}")
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        if "insufficient_quota" in str(e):
            print("Please set up billing at platform.openai.com/account/billing")

if __name__ == "__main__":
    main(4) 
