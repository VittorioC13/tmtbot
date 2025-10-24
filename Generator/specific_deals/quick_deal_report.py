#!/usr/bin/env python3
"""
Quick Deal Report Generator
Usage: python quick_deal_report.py
Simple script to quickly generate reports for any deal
"""

from specific_deal_reporter import SpecificDealReporter
from datetime import datetime

def quick_deal_report():
    """Generate a quick deal report with minimal input"""
    
    print("="*80)
    print("QUICK DEAL REPORT GENERATOR")
    print("="*80)
    print("Enter the essential deal information:")
    print("(Press Enter to skip optional fields)")
    print()
    
    # Get essential deal information
    deal_info = {}
    
    deal_info['buyer'] = input("Buyer Company: ").strip()
    if not deal_info['buyer']:
        print("Buyer company is required!")
        return None
    
    deal_info['target'] = input("Target Company: ").strip()
    if not deal_info['target']:
        print("Target company is required!")
        return None
    
    deal_info['deal_value'] = input("Deal Value (e.g., $59.5 billion): ").strip() or "N/A"
    deal_info['enterprise_value'] = input("Enterprise Value: ").strip() or "N/A"
    deal_info['announcement_date'] = input("Announcement Date: ").strip() or "N/A"
    deal_info['transaction_type'] = input("Transaction Type: ").strip() or "N/A"
    deal_info['source_url'] = input("Source URL: ").strip() or "N/A"
    
    # Optional fields
    deal_info['share_price'] = input("Share Price (optional): ").strip() or "N/A"
    deal_info['exchange_ratio'] = input("Exchange Ratio (optional): ").strip() or "N/A"
    
    # Get sector and region
    sector = input("Sector (Energy/TMT/Healthcare/Industrial/Consumer) [Energy]: ").strip() or "Energy"
    region = input("Region (US/Europe/APAC) [US]: ").strip() or "US"
    
    print(f"\nGenerating {sector} sector report for {region} region...")
    print("This may take a moment...")
    
    try:
        reporter = SpecificDealReporter()
        pdf_path = reporter.generate_deal_report(deal_info, sector=sector, region=region)
        
        print("\n" + "="*80)
        print("DEAL REPORT GENERATED SUCCESSFULLY!")
        print("="*80)
        print(f"✓ Buyer: {deal_info['buyer']}")
        print(f"✓ Target: {deal_info['target']}")
        print(f"✓ Deal Value: {deal_info['deal_value']}")
        print(f"✓ Sector: {sector}")
        print(f"✓ Region: {region}")
        print(f"✓ Report Location: {pdf_path}")
        print("="*80)
        
        return pdf_path
        
    except Exception as e:
        print(f"\nError generating report: {str(e)}")
        return None

def main():
    """Main function"""
    print("TMT BOT - QUICK DEAL REPORT GENERATOR")
    print("="*80)
    print("This tool helps you quickly generate professional M&A deal reports")
    print("using the same formatting as TMT BOT daily briefs.")
    print()
    
    while True:
        try:
            pdf_path = quick_deal_report()
            
            if pdf_path:
                print(f"\n✓ Report successfully generated!")
                print(f"✓ File saved as: {pdf_path.name}")
                
                # Ask if user wants to generate another report
                another = input("\nGenerate another report? (y/n): ").strip().lower()
                if another not in ['y', 'yes']:
                    break
            else:
                print("\nReport generation failed. Please try again.")
                
        except KeyboardInterrupt:
            print("\n\nExiting...")
            break
        except Exception as e:
            print(f"\nUnexpected error: {str(e)}")
            break
    
    print("\nThank you for using TMT BOT Deal Report Generator!")

if __name__ == "__main__":
    main()
