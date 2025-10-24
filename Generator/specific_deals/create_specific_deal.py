#!/usr/bin/env python3
"""
Interactive script to create specific deal reports
Usage: python create_specific_deal.py
"""

from specific_deal_reporter import SpecificDealReporter
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
    
    reporter = SpecificDealReporter()
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

def create_custom_specific_deal():
    """Create a custom specific deal report with user input"""
    
    print("\n" + "="*80)
    print("CUSTOM SPECIFIC DEAL REPORT GENERATOR")
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
    
    reporter = SpecificDealReporter()
    pdf_path = reporter.generate_deal_report(deal_info, sector=sector, region=region)
    
    print("\n" + "="*80)
    print("CUSTOM SPECIFIC DEAL REPORT GENERATED")
    print("="*80)
    print(f"✓ Buyer: {deal_info['buyer']}")
    print(f"✓ Target: {deal_info['target']}")
    print(f"✓ Deal Value: {deal_info['deal_value']}")
    print(f"✓ Sector: {sector}")
    print(f"✓ Region: {region}")
    print(f"✓ Report Generated: {pdf_path}")
    print("="*80)
    
    return pdf_path

def list_existing_reports():
    """List all existing specific deal reports"""
    
    import os
    from pathlib import Path
    
    deals_dir = Path(__file__).resolve().parent
    pdf_files = [f for f in os.listdir(deals_dir) if f.endswith('.pdf')]
    
    if not pdf_files:
        print("\nNo specific deal reports found.")
        return
    
    print("\n" + "="*80)
    print("EXISTING SPECIFIC DEAL REPORTS")
    print("="*80)
    
    for i, pdf_file in enumerate(sorted(pdf_files, reverse=True), 1):
        file_path = deals_dir / pdf_file
        file_size = file_path.stat().st_size
        file_date = datetime.fromtimestamp(file_path.stat().st_mtime).strftime('%Y-%m-%d %H:%M')
        print(f"{i:2d}. {pdf_file}")
        print(f"    Size: {file_size:,} bytes | Modified: {file_date}")
    
    print("="*80)

def main():
    """Main function"""
    print("TMT BOT - SPECIFIC DEAL REPORT GENERATOR")
    print("="*80)
    print("1. Generate ExxonMobil & Pioneer Natural Resources Report")
    print("2. Create Custom Specific Deal Report")
    print("3. List Existing Reports")
    print("4. Exit")
    
    while True:
        choice = input("\nSelect option (1-4): ").strip()
        
        if choice == "1":
            create_exxon_pioneer_report()
            break
        elif choice == "2":
            create_custom_specific_deal()
            break
        elif choice == "3":
            list_existing_reports()
            break
        elif choice == "4":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please select 1, 2, 3, or 4.")

if __name__ == "__main__":
    main()
