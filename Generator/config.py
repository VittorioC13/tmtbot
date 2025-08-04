import os

NEWS_API_KEY = os.environ.get("NEWS_API") #set in project "secrets"
OPENAI_API_KEY = os.environ.get("OPENAI_API")

# News Categories
TMT_CATEGORIES = [
    "technology",          # broad umbrella
    "software",
    "semiconductors",
    "telecommunications",
    "artificial intelligence"
]

ENERGY_CATEGORIES = [
    "energy",              # broad umbrella
    "oil",
    "natural gas",
    "renewable",           # solar, wind, etc.
    "utilities"
]




HEALTHCARE_CATEGORIES = [
    "Healthcare mergers and acquisitions",
    "healthcare",
    "pharmaceuticals",
    "biotechnology",
    "healthcare technology"
]

# Time Settings
NEWS_LOOKBACK_DAYS = 7  # Number of days to look back for news 
