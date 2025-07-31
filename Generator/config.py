import os

# API Keys Configuration - Get from environment variables or use defaults
NEWS_API_KEY = os.getenv("NEWS_API", "your_news_api_key_here")
OPENAI_API_KEY = os.getenv("OPENAI_API", "your_openai_api_key_here")

# Email Configuration
EMAIL_USER = os.getenv("EMAIL_USER", "lingcheng783@gmail.com")
EMAIL_PASS = os.getenv("EMAIL_PASS", "your_email_password_here")

# News Categories
CATEGORIES = [
    "mergers and acquisitions",
    "energy",
    "oil and gas",
    "renewable energy",
    "utilities"
]

# Time Settings
NEWS_LOOKBACK_DAYS = 7  # Number of days to look back for news 