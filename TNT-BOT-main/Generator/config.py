import os

NEWS_API_KEY = os.environ.get("NEWS_API") #set in project "secrets"
OPENAI_API_KEY = os.environ.get("OPENAI_API")

# News Categories
CATEGORIES = [
    "mergers and acquisitions",
    "technology",
    "artificial intelligence",
    "investment banking",
    "fintech"
]

# Time Settings
NEWS_LOOKBACK_DAYS = 7  # Number of days to look back for news 
