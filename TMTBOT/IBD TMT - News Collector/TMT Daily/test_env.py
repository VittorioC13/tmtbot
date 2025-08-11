from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Print the API keys
print("NEWS_API_KEY:", os.getenv('NEWS_API_KEY'))
print("Length of NEWS_API_KEY:", len(os.getenv('NEWS_API_KEY')) if os.getenv('NEWS_API_KEY') else 0) 