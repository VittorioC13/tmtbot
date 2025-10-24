# Specific Deals Report Generator

This folder contains tools for generating PDF reports for specific M&A deals with custom naming and dedicated storage.

## Features

- **Custom File Naming**: Files are named after the deal participants (e.g., `ExxonMobil_and_Pioneer_Natural_Resources_Deal_Report_2025-10-24.pdf`)
- **Dedicated Storage**: All specific deal reports are stored in this folder, separate from daily briefs
- **Same Formatting**: Uses the same professional PDF formatting as daily briefs
- **Interactive Interface**: Easy-to-use script for creating reports

## Files

- `specific_deal_reporter.py` - Core reporter class for generating specific deal reports
- `create_specific_deal.py` - Interactive script for easy report creation
- `README.md` - This documentation file

## Usage

### Option 1: Interactive Script (Recommended)

```bash
cd specific_deals
python create_specific_deal.py
```

This will present you with options to:
1. Generate the ExxonMobil & Pioneer Natural Resources report
2. Create a custom specific deal report with your own deal information
3. List existing reports
4. Exit

### Option 2: Direct Script Execution

```bash
cd specific_deals
python specific_deal_reporter.py
```

This will generate the ExxonMobil & Pioneer report directly.

### Option 3: Programmatic Usage

```python
from specific_deal_reporter import SpecificDealReporter

# Define deal information
deal_info = {
    "buyer": "Company A",
    "target": "Company B", 
    "deal_value": "$10 billion",
    "share_price": "$100 per share",
    "exchange_ratio": "1.5 shares for each target share",
    "enterprise_value": "$12 billion",
    "announcement_date": "October 24, 2025",
    "transaction_type": "Stock merger",
    "source_url": "https://example.com/press-release"
}

# Generate report
reporter = SpecificDealReporter()
pdf_path = reporter.generate_deal_report(deal_info, sector="TMT", region="US")
print(f"Report saved to: {pdf_path}")
```

## File Naming Convention

Reports are named using the following pattern:
`{Buyer}_{Target}_Deal_Report_{YYYY-MM-DD}.pdf`

Examples:
- `ExxonMobil_and_Pioneer_Natural_Resources_Deal_Report_2025-10-24.pdf`
- `Apple_and_Intel_Deal_Report_2025-10-24.pdf`
- `Microsoft_and_Activision_Deal_Report_2025-10-24.pdf`

## Deal Information Required

The following information can be provided for each deal:

- **buyer**: Acquiring company name
- **target**: Target company name  
- **deal_value**: Total deal value (e.g., "$59.5 billion")
- **share_price**: Price per share (e.g., "$253 per share")
- **exchange_ratio**: Share exchange ratio
- **enterprise_value**: Total enterprise value including debt
- **announcement_date**: Date the deal was announced
- **transaction_type**: Type of transaction (e.g., "All-stock merger")
- **source_url**: Link to official announcement

## Report Structure

Each generated report includes the same comprehensive structure as daily briefs:

### 1. Deal Overview & Financial Metrics
- Deal size classification (Small/Mid/Large cap)
- Deal type classification (Horizontal/Vertical/etc.)
- Valuation multiples analysis
- Strategic rationale
- Risk analysis

### 2. Strategic Rationale & Market Positioning
- Strategic logic behind the transaction
- Market positioning implications
- Synergy potential and cost savings
- Competitive landscape impact

### 3. Financial Impact & Valuation Analysis
- Revenue and profitability analysis
- Debt structure and leverage analysis
- Asset efficiency metrics
- Valuation context with peer comparisons

### 4. Regulatory & Risk Assessment
- Regulatory approval requirements
- Antitrust considerations
- Integration risks
- Market and execution risks

### 5. Market Dynamics & Sector Implications
- Sector trends and implications
- Peer company reactions
- Market sentiment and investor response
- Future M&A activity implications

### 6. Recommended Readings
- Relevant industry reports and analysis links

## Example: ExxonMobil & Pioneer Natural Resources Merger

The system includes a pre-built example for the ExxonMobil & Pioneer Natural Resources merger:

- **Deal Value**: $59.5 billion
- **Enterprise Value**: $64.5 billion
- **Transaction Type**: All-stock merger
- **Announcement Date**: October 11, 2023
- **Source**: [ExxonMobil Press Release](https://corporate.exxonmobil.com/news/news-releases/2023/1011_exxonmobil-announces-merger-with-pioneer-natural-resources-in-an-all-stock-transaction)

This creates a comprehensive investment banking analysis covering all aspects of the merger from strategic rationale to regulatory considerations.

## Configuration

### OpenAI API Key (Optional)
If you have an OpenAI API key, set it as an environment variable:
```bash
export OPENAI_API="your-api-key-here"
```

Without an API key, the system will use mock analysis data that still provides comprehensive deal analysis.

### Sectors Supported
- Energy
- TMT (Technology, Media, Telecom)
- Healthcare
- Industrial
- Consumer

### Regions Supported
- US
- Europe
- APAC

## Troubleshooting

### Common Issues

1. **Unicode Encoding Errors**: The system automatically handles Unicode characters in the PDF generation
2. **Missing API Key**: The system will use mock analysis if no OpenAI API key is provided
3. **File Permissions**: Ensure the specific_deals directory is writable

### Dependencies

Required Python packages:
- fpdf2
- openai (optional)
- pathlib
- datetime
- re

All dependencies are included in the main TMT BOT requirements.txt file.

## Output Location

All specific deal reports are saved in this directory (`/Generator/specific_deals/`) with descriptive filenames that include the deal participants and date.
