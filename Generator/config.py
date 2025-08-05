import os

NEWS_API_KEY = os.environ.get("NEWS_API") #set in project "secrets"
NEWS_API_BACKUP = os.environ.get("NEWS_API")
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


SECTOR_DEAL_TERMS = {
            "healthcare": [
                "merger", "acquisition", "acquire", "acquires", "buyout", "stake",
                "takeover", "deal", "investment", "invests",
                "licensing", "collaboration",           # pharma/biotech flavour
                "FDA", "clinical", "drug", "biotech"    # help relevancy scoring
            ],
            "technology": [
                "merger", "acquisition", "acquire", "acquires", "buyout", "stake",
                "takeover", "deal", "investment", "invests",
                "funding", "venture capital", "IPO", "startup", "unicorn"
            ],
            "energy": [
                # generic M&A
                "merger", "acquisition", "acquire", "acquires",
                "buyout", "stake", "equity stake", "takeover",
                "deal", "transaction", "investment", "invests",
                "joint venture", "JV", "partnership",
                "divestiture", "asset sale", "asset purchase", "portfolio sale",

                # sector-specific structures
                "farm-in", "farm-out", "production sharing", "PSA",
                "offtake", "power purchase agreement", "PPA",

                # value-chain flags
                "upstream", "midstream", "downstream",
                "E&P", "exploration", "development", "drilling",
                "pipeline", "terminal", "refining", "LNG",

                # clean-energy flags
                "renewable", "wind farm", "solar farm",
                "hydrogen", "battery storage", "grid", "carbon capture"
            ],
            # default for any new sector you add later
            "_default": [
                "merger", "acquisition", "acquire", "acquires", "buyout", "stake",
                "takeover", "deal", "investment", "invests"
            ]
        }
