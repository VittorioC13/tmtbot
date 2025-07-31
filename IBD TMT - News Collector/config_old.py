# API Keys Configuration
NEWS_API_KEY = "468310dccfbf4a668d97646431efdf35"
OPENAI_API_KEY = "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"

# News Categories
CATEGORIES = [
    "mergers and acquisitions",
    "technology",
    "artificial intelligence",
    "investment banking",
    "fintech",
    "Revolut",
    "fintech funding"
]

# Time Settings
NEWS_LOOKBACK_DAYS = 7  # Number of days to look back for news 

SECTOR_CONFIGS = {
    "TMT": {
        "CATEGORIES": [
            "technology", "media", "telecommunications", "fintech", "software", "AI", "cloud computing"
        ],
        "prompt_sector": "Technology, Media & Telecommunications (TMT)",
        "brief_title": "TMT Sector M&A & Valuation Brief"
    },
    "Energy": {
        "CATEGORIES": [
            "energy", "oil", "gas", "renewables", "power", "utilities", "clean energy", "carbon"
        ],
        "prompt_sector": "Energy",
        "brief_title": "Energy Sector M&A & Valuation Brief"
    }
} 