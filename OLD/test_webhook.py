import requests
import json
import time

# Test webhook for local development
def test_webhook():
    # Your Flask server URL
    webhook_url = "http://localhost:5000/webhook"
    
    # Sample webhook event data (checkout.session.completed)
    webhook_data = {
        "id": "evt_test_webhook",
        "object": "event",
        "api_version": "2020-08-27",
        "created": int(time.time()),
        "data": {
            "object": {
                "id": "cs_test_session",
                "object": "checkout.session",
                "metadata": {
                    "user_id": "1"  # Replace with actual user ID
                },
                "payment_status": "paid",
                "status": "complete"
            }
        },
        "livemode": False,
        "pending_webhooks": 1,
        "request": {
            "id": "req_test",
            "idempotency_key": None
        },
        "type": "checkout.session.completed"
    }
    
    # Headers that Stripe would send
    headers = {
        "Content-Type": "application/json",
        "Stripe-Signature": "test_signature"  # In real scenario, this would be verified
    }
    
    try:
        response = requests.post(webhook_url, json=webhook_data, headers=headers)
        print(f"Webhook Response Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Webhook test successful!")
        else:
            print("❌ Webhook test failed!")
            
    except Exception as e:
        print(f"❌ Error testing webhook: {e}")

if __name__ == "__main__":
    print("Testing Stripe webhook...")
    test_webhook() 