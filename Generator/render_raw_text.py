from pdf_report import format_brief
from pathlib import Path

base_path = Path(__file__).resolve().parent.parent 
raw_dir = base_path / 'api' / "static" / "assets" / "raw"
json_path = base_path/ 'term_definitions.json'
brief_dir = base_path / 'api' / 'static' / 'assets' / 'briefs'

def clean_text_for_pdf(text):
    """Clean text of problematic Unicode characters for PDF generation"""
    if not text:
        return text
    
    # Replace problematic Unicode characters with ASCII equivalents
    replacements = {
        '\u20b9': 'Replaced_Rs',  # Indian Rupee
        '\u20ac': 'Replaced_EUR',  # Euro
        '\u00a3': 'Replaced_GBP',  # Pound Sterling
        '\u00a5': 'Replaced_JPY',  # Yen
        '\u20bf': 'Replaced_BTC',  # Bitcoin
        '\u201c': 'Replaced_"',    # Left double quotation mark
        '\u201d': 'Replaced_"',    # Right double quotation mark
        '\u2018': "Replaced_'",    # Left single quotation mark
        '\u2019': "Replaced_'",    # Right single quotation mark
        '\u2013': 'Replaced_the hyphen',    # En dash
        '\u2014': 'Replaced_--',   # Em dash
        '\u2022': 'Replaced_-',    # Bullet
        '\u2026': 'Replaced_...',  # Ellipsis
    }
    
    for unicode_char, replacement in replacements.items():
        text: str = text.replace(unicode_char, replacement)
    
    # More aggressive cleaning - convert to ASCII and handle errors gracefully
    try:
        # First try to encode as UTF-8 and decode as ASCII
        text = text.encode('utf-8').decode('ascii', errors='ignore')
    except:
        # If that fails, use a more aggressive approach
        text = ''.join(char for char in text if ord(char) < 128)
    
    return text.strip()

filename = raw_dir / "TMT_Brief_2025-07-29_raw.txt"
with open(filename, "r", encoding="utf-8") as f:
  text_to_be_rendered = f.read()


#print(clean_text_for_pdf(testText))
#for the third argument: 1 for TMT, 2 for Energy
format_brief(clean_text_for_pdf(text_to_be_rendered), brief_dir, 2) 