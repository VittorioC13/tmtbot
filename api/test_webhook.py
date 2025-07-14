#!/usr/bin/env python3
"""
Test script to verify webhook functionality on Vercel
"""
import requests
import json

def test_webhook_endpoint():
    """Test the webhook endpoint"""
    webhook_url = "https://tmt-api-git-main-xukun-cais-projects.vercel.app/webhook"
    
    # Test data (this won't pass signature verification, but tests connectivity)
    test_payload = {
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "metadata": {
                    "user_id": "1"
                }
            }
        }
    }
    
    headers = {
        'Content-Type': 'application/json',
        'Stripe-Signature': 'test_signature'
    }
    
    try:
        response = requests.post(webhook_url, json=test_payload, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        return response.status_code == 400  # Expected to fail due to invalid signature
    except Exception as e:
        print(f"Error testing webhook: {e}")
        return False

def test_health_endpoint():
    """Test the health endpoint"""
    health_url = "https://tmt-api-git-main-xukun-cais-projects.vercel.app/health"
    
    try:
        response = requests.get(health_url)
        print(f"Health Status Code: {response.status_code}")
        print(f"Health Response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error testing health endpoint: {e}")
        return False

if __name__ == "__main__":
    print("Testing webhook functionality...")
    print("=" * 50)
    
    # Test health endpoint first
    print("1. Testing health endpoint...")
    health_ok = test_health_endpoint()
    
    print("\n2. Testing webhook endpoint...")
    webhook_ok = test_webhook_endpoint()
    
    print("\n" + "=" * 50)
    print("Test Results:")
    print(f"Health endpoint: {'✅ PASS' if health_ok else '❌ FAIL'}")
    print(f"Webhook endpoint: {'✅ PASS' if webhook_ok else '❌ FAIL'}")
    
    if health_ok and webhook_ok:
        print("\n🎉 All tests passed! Your webhook should be working.")
    else:
        print("\n⚠️  Some tests failed. Check your deployment and configuration.") 