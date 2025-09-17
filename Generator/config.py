import os

NEWS_API_KEY = os.environ.get("NEWS_API") #set in project "secrets"
NEWS_API_BACKUP = os.environ.get("NEWS_API_BACKUP")
NEWS_API_BACKUP2 = os.environ.get("NEWS_API_BACKUP2")
OPENAI_API_KEY = os.environ.get("OPENAI_API")

# Time Settings
NEWS_LOOKBACK_DAYS = 7  # Number of days to look back for news 

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

INDUSTRIAL_CATEGORIES = [
    "manufacturing",
    "capital goods",
    "transportation",
    "construction",
    "aerospace"
]

CONSUMER_CATEGORIES = [
    "retail",
    "consumer goods",
    "food & beverage",
    "apparel",
    "e-commerce"
]

SECTOR_DEAL_TERMS = {
    "healthcare": [
        "merger", "acquisition", "acquire", "acquires", "buyout", "stake",
        "takeover", "deal", "investment", "invests",
        "licensing", "collaboration",
        "FDA", "clinical", "drug", "biotech"
    ],
    "technology": [
        "merger", "acquisition", "acquire", "acquires", "buyout", "stake",
        "takeover", "deal", "investment", "invests",
        "funding", "venture capital", "IPO", "startup", "unicorn"
    ],
    "energy": [
        "merger", "acquisition", "acquire", "acquires",
        "buyout", "stake", "equity stake", "takeover",
        "deal", "transaction", "investment", "invests",
        "joint venture", "JV", "partnership",
        "divestiture", "asset sale", "asset purchase", "portfolio sale"
    ],
    "industry": [
        # core M&A / finance
        "merger", "acquisition", "buyout", "stake",
        "takeover", "deal", "transaction", "investment",
        "joint venture", "partnership",

        # industry-specific
        "plant expansion", "facility investment", "factory construction",
        "infrastructure project", "engineering contract",
        "logistics partnership", "supply chain agreement",
        "defense contract", "aerospace order"
    ],

    "consumer": [
        # core M&A / finance
        "merger", "acquisition", "buyout", "stake",
        "takeover", "deal", "transaction", "investment",
        "joint venture", "partnership",

        # consumer-specific
        "brand acquisition", "retail expansion", "store opening",
        "franchise agreement", "product launch",
        "e-commerce investment", "food & beverage deal",
        "luxury brand deal"
    ],

    "_default": [
        "merger", "acquisition", "acquire", "acquires", "buyout", "stake",
        "takeover", "deal", "investment", "invests"
    ]
}

REGION_ANCHORS = {
    "Europe": [
    "Europe", "European Union", "EU", "Eurozone",
    "European Commission", "DG COMP", "ECB", "ESMA", "CMA", 
    "Euro Stoxx", "DAX", "CAC", "FTSE"
    ]
}
