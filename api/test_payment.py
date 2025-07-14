#!/usr/bin/env python3
"""
Test script to debug payment session creation
"""
import requests
import json

def test_payment_session():
    """Test the payment session creation endpoint"""
    payment_url = "https://tmt-api-git-main-xukun-cais-projects.vercel.app/create-checkout-session"
    
    # Test headers
    headers = {
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest'
    }
    
    try:
        print("Testing payment session creation...")
        response = requests.post(payment_url, headers=headers)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        try:
            data = response.json()
            print(f"Response Data: {json.dumps(data, indent=2)}")
        except json.JSONDecodeError:
            print(f"Raw Response: {response.text}")
        
        return response.status_code
    except Exception as e:
        print(f"Error testing payment: {e}")
        return None

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

def test_stripe_config():
    """Test Stripe configuration"""
    import stripe
    
    # Test with the same key from the frontend
    stripe.api_key = "sk_test_51Ri9SyFSHePhJarRDO1vrS4Ca8T8pRqsvkluFVE8sP4nc5qwiGal62fcWZAU9JeUbatWjzEZ6MQigXxOUvHwmXwJ00vr1eTfnk"
    
    try:
        # Test creating a simple checkout session
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': 'Test Product',
                        'description': 'Test product for validation',
                    },
                    'unit_amount': 1000,
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url='https://example.com/success',
            cancel_url='https://example.com/cancel',
        )
        print(f"✅ Stripe test session created: {session.id}")
        return True
    except Exception as e:
        print(f"❌ Stripe configuration error: {e}")
        return False

if __name__ == "__main__":
    print("Payment Session Debug Test")
    print("=" * 50)
    
    # Test 1: Health endpoint
    print("1. Testing health endpoint...")
    health_ok = test_health_endpoint()
    
    # Test 2: Stripe configuration
    print("\n2. Testing Stripe configuration...")
    stripe_ok = test_stripe_config()
    
    # Test 3: Payment session creation
    print("\n3. Testing payment session creation...")
    payment_status = test_payment_session()
    
    print("\n" + "=" * 50)
    print("Test Results:")
    print(f"Health endpoint: {'✅ PASS' if health_ok else '❌ FAIL'}")
    print(f"Stripe config: {'✅ PASS' if stripe_ok else '❌ FAIL'}")
    print(f"Payment session: {'✅ PASS' if payment_status == 200 else f'❌ FAIL (Status: {payment_status})'}")
    
    if health_ok and stripe_ok and payment_status == 200:
        print("\n🎉 All tests passed! Payment should be working.")
    else:
        print("\n⚠️  Some tests failed. Check the specific errors above.")
        
        if not stripe_ok:
            print("\n💡 Stripe configuration issue detected. Check your API keys.")
        if payment_status != 200:
            print("\n💡 Payment session creation issue. Check server logs and configuration.") 