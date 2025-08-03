import os

#NEWS_API_KEY = os.environ.get("NEWS_API") #set in project "secrets"
#OPENAI_API_KEY = os.environ.get("OPENAI_API")

NEWS_API_KEY = "468310dccfbf4a668d97646431efdf35"
OPENAI_API_KEY = "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"

# News Categories
TMT_CATEGORIES = [
    "mergers and acquisitions",
    "technology",
    "artificial intelligence",
    "investment banking",
    "fintech"
]


ENERGY_CATEGORIES = [
    "mergers and acquisitions",
    "energy",
    "oil and gas",
    "renewable energy",
    "utilities"
]

# Time Settings
NEWS_LOOKBACK_DAYS = 7  # Number of days to look back for news 
