from newsapi import NewsApiClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize NewsAPI client
newsapi = NewsApiClient(api_key=os.getenv('NEWS_API_KEY'))

# Try to get some news
try:
    response = newsapi.get_top_headlines(language='en', country='us')
    print("API Key is working!")
    print(f"Status: {response['status']}")
    print(f"Total Results: {response['totalResults']}")
except Exception as e:
    print(f"Error: {str(e)}") 