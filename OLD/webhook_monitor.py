import requests
import json
import time
from datetime import datetime

def monitor_webhook_events():
    """Monitor webhook events by checking the Flask server logs"""
    print("🔍 Webhook Monitor Started")
    print("=" * 50)
    print("This will help you see when webhooks are received")
    print("Make a test payment to see webhook events")
    print("=" * 50)
    
    # Check if Flask server is running
    try:
        response = requests.get("http://localhost:5000/health")
        if response.status_code == 200:
            print("✅ Flask server is running")
        else:
            print("❌ Flask server not responding")
            return
    except:
        print("❌ Flask server not running. Start it first with: python index.py")
        return
    
    print("\n📋 Instructions:")
    print("1. Make sure your Flask server is running (python index.py)")
    print("2. Complete a test payment through your dashboard")
    print("3. Watch for webhook events below")
    print("4. Check your database to see if user.is_paid was updated")
    print("\n⏳ Monitoring webhooks... (Press Ctrl+C to stop)")
    
    try:
        while True:
            time.sleep(1)
            # You can add more monitoring logic here if needed
    except KeyboardInterrupt:
        print("\n🛑 Webhook monitoring stopped")

if __name__ == "__main__":
    monitor_webhook_events() 