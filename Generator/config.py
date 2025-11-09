import os

NEWS_API_KEY = "72a07184dc6c4c3aa8b4aa6bba0d53bc"
NEWS_API_BACKUP = "fc46f478c68949258cb116b544c3a34c"
NEWS_API_BACKUP2 = "468310dccfbf4a668d97646431efdf35"
NEWS_API_BACKUP3 = "26c598643cf74961b4211ed9d0aaaa1b"
NEWS_API_BACKUP4 = "7dcd2208b6e24aa49420d49e879d82a0"
NEWS_API_BACKUP5 = "0feabf17f84f4ab19e5d2658b4b52672"
NEWS_API_BACKUP6 = "96ab65e4ad2c4bb8aca16eee95a92319"
NEWS_API_BACKUP7 = "3f3277eef32a4a6587d9b2525d551cc2"
NEWS_API_BACKUP8 = "d5063af4cca84465b9328a7e961a66ca"
NEWS_API_BACKUP9 = "0b4e66e5458a47608feff3d398c07821"
NEWS_API_BACKUP10 = "37c44775839f48229e1dc15d3b4c0420"
NEWS_API_BACKUP11 = "b80bcc3bd14c42eb91fa7823e817a779"
NEWS_API_BACKUP12 = "002d9cfb7c7149ff90861eb1dd1dde71"
NEWS_API_BACKUP13 = "c0ea160ef66c4913a6b2f2eebde5891c"
NEWS_API_BACKUP14 = "32ac95834ff74a3ab446776d988c8ede"
NEWS_API_BACKUP15 = "72a07184dc6c4c3aa8b4aa6bba0d53bc"
NEWS_API_BACKUP16 = "8f076fcfb5354f9da926389003af9322"
NEWS_API_BACKUP17 = "d686aec4dd344cbaa8fa613434b9e713"
NEWS_API_BACKUP18 = "f9b9422f47fa43c68d29b2e3128d430b"
NEWS_API_BACKUP19 = "5535840de483424f8ca0a42e47305d8c"
OPENAI_API_KEY = os.environ.get("OPENAI_API")
ALPHA_VANTAGE_API_KEY = "XWG1TL31USASWISO"
FINNHUB_API_KEY = "d36pnjpr01qtvbtinv3gd36pnjpr01qtvbtinv40"

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
        # Core M&A
        "merger", "acquisition", "buyout", "stake", "takeover", "deal", "transaction",
        "investment", "invests", "backs", "funding", "financing", "raises", "capital raise",

        # Licensing & Partnerships
        "licensing", "collaboration", "alliance", "joint venture", "strategic partnership",

        # Healthcare-specific
        "drug approval", "FDA approval", "clinical trial", "phase 1", "phase 2", "phase 3",
        "biotech", "pharma", "life sciences", "medtech", "medical device"
    ],

    "tmt": [  # (Technology, Media, Telecom)
        # Core M&A / funding
        "merger", "acquisition", "acquire", "buys", "takeover", "buyout", "stake",
        "deal", "transaction", "investment", "invests", "funding", "financing", "capital raise",
        "venture capital", "private equity", "series A", "series B", "series C",
        "IPO", "listing", "SPAC",

        # Sector-specific
        "startup", "scale-up", "unicorn", "tech giant", "software", "AI", "cloud",
        "semiconductor", "chipmaker", "telecom", "5G", "streaming", "media rights"
    ],

    "energy": [
        # Core M&A / finance
        "merger", "acquisition", "buyout", "stake", "equity", "takeover", "deal",
        "transaction", "investment", "invests", "capital raise", "financing",

        # Partnerships / restructuring
        "joint venture", "partnership", 
        "divestiture", "asset purchase", "spinoff",

        # Energy-specific
        "oil & gas", "renewable", "solar", "nuclear", "LNG",
        "offshore", "power plant",  "decarbonization"
    ],

    "industrial": [
        # Core M&A
        "merger", "acquisition", "buyout", "stake", "takeover", "deal",
        "transaction", "investment", "invests", "capital raise",

        # Partnerships / projects
        "joint venture", "JV", "partnership", "strategic alliance",
        "plant expansion", "factory construction", "facility investment",
        "infrastructure project", "engineering contract", "supply chain deal",
        "logistics partnership", "defense contract", "aerospace order"
    ],

    "consumer": [
        # Core M&A / finance
        "merger", "acquisition", "buyout", "stake", "takeover", "deal",
        "transaction", "investment", "invests", "capital raise", "financing",

        # Consumer-specific growth
        "brand acquisition", "retail expansion", "store opening", "franchise deal",
        "product launch", "new collection", "e-commerce investment",
        "food & beverage", "luxury", "fashion", "consumer goods giant", "CPG"
    ],

    "_default": [
        "merger", "acquisition", "acquire", "buys", "takeover", "deal",
        "investment", "invests", "funding", "financing", "capital raise"
    ]
}

REGION_ANCHORS = {
    "Europe": [
        "Europe", "European Union", "EU", "Eurozone",
        "European Commission", "DG COMP", "ECB", "ESMA", "CMA", 
        "Euro Stoxx", "DAX", "CAC", "FTSE"
    ],
    "APAC": [
        "Asia Pacific", "APAC", "ASEAN", "Asean Bloc",
        "China", "Japan", "South Korea", "Australia", "New Zealand",
        "HKEX", "SGX", "Nikkei", "Hang Seng"
    ]
}
