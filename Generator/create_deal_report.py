#!/usr/bin/env python3
"""
Simple script to create deal reports for TMT BOT
Usage: python create_deal_report.py
"""

from general_deal_reporter import GeneralDealReporter
from datetime import datetime

def create_exxon_pioneer_report():
    """Create the ExxonMobil & Pioneer Natural Resources merger report"""
    
    deal_info = {
        "buyer": "ExxonMobil Corp.",
        "target": "Pioneer Natural Resources", 
        "deal_value": "$59.5 billion",
        "share_price": "$253 per share",
        "exchange_ratio": "2.3234 shares of ExxonMobil for each Pioneer share",
        "enterprise_value": "$64.5 billion",
        "announcement_date": "October 11, 2023",
        "transaction_type": "All-stock merger",
        "source_url": "https://corporate.exxonmobil.com/news/news-releases/2023/1011_exxonmobil-announces-merger-with-pioneer-natural-resources-in-an-all-stock-transaction"
    }
    
    reporter = GeneralDealReporter()
    pdf_path = reporter.generate_deal_report(deal_info, sector="Energy", region="US")
    
    print("="*80)
    print("EXXONMOBIL & PIONEER NATURAL RESOURCES MERGER REPORT")
    print("="*80)
    print(f"✓ Deal Value: {deal_info['deal_value']}")
    print(f"✓ Enterprise Value: {deal_info['enterprise_value']}")
    print(f"✓ Transaction Type: {deal_info['transaction_type']}")
    print(f"✓ Announcement Date: {deal_info['announcement_date']}")
    print(f"✓ Report Generated: {pdf_path}")
    print("="*80)
    
    return pdf_path

def create_custom_deal_report():
    """Create a custom deal report with user input"""
    
    print("\n" + "="*80)
    print("CUSTOM DEAL REPORT GENERATOR")
    print("="*80)
    
    # Get deal information from user
    deal_info = {}
    
    print("\nEnter deal information (press Enter to skip optional fields):")
    
    deal_info['buyer'] = input("Buyer Company: ").strip() or "N/A"
    deal_info['target'] = input("Target Company: ").strip() or "N/A"
    deal_info['deal_value'] = input("Deal Value (e.g., $59.5 billion): ").strip() or "N/A"
    deal_info['share_price'] = input("Share Price (e.g., $253 per share): ").strip() or "N/A"
    deal_info['exchange_ratio'] = input("Exchange Ratio: ").strip() or "N/A"
    deal_info['enterprise_value'] = input("Enterprise Value: ").strip() or "N/A"
    deal_info['announcement_date'] = input("Announcement Date: ").strip() or "N/A"
    deal_info['transaction_type'] = input("Transaction Type: ").strip() or "N/A"
    deal_info['source_url'] = input("Source URL: ").strip() or "N/A"
    
    # Get sector and region
    sector = input("Sector (Energy/TMT/Healthcare/Industrial/Consumer): ").strip() or "Energy"
    region = input("Region (US/Europe/APAC): ").strip() or "US"
    
    print(f"\nGenerating {sector} sector report for {region} region...")
    
    reporter = GeneralDealReporter()
    pdf_path = reporter.generate_deal_report(deal_info, sector=sector, region=region)
    
    print("\n" + "="*80)
    print("CUSTOM DEAL REPORT GENERATED")
    print("="*80)
    print(f"✓ Buyer: {deal_info['buyer']}")
    print(f"✓ Target: {deal_info['target']}")
    print(f"✓ Deal Value: {deal_info['deal_value']}")
    print(f"✓ Sector: {sector}")
    print(f"✓ Region: {region}")
    print(f"✓ Report Generated: {pdf_path}")
    print("="*80)
    
    return pdf_path

def main():
    """Main function"""
    print("TMT BOT - DEAL REPORT GENERATOR")
    print("="*80)
    print("1. Generate ExxonMobil & Pioneer Natural Resources Report")
    print("2. Create Custom Deal Report")
    print("3. Exit")
    
    while True:
        choice = input("\nSelect option (1-3): ").strip()
        
        if choice == "1":
            create_exxon_pioneer_report()
            break
        elif choice == "2":
            create_custom_deal_report()
            break
        elif choice == "3":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please select 1, 2, or 3.")

if __name__ == "__main__":
    main()
