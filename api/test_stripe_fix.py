#!/usr/bin/env python3
"""
Test script to verify Stripe checkout session creation fix
"""
import stripe

def test_stripe_checkout_creation():
    """Test creating a Stripe checkout session without customer_email"""
    
    # Use the same Stripe key
    stripe.api_key = "sk_test_51Ri9SyFSHePhJarRDO1vrS4Ca8T8pRqsvkluFVE8sP4nc5qwiGal62fcWZAU9JeUbatWjzEZ6MQigXxOUvHwmXwJ00vr1eTfnk"
    
    try:
        print("Testing Stripe checkout session creation...")
        
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': 'TMT Daily Brief Premium',
                        'description': 'Access to all TMT Daily Brief reports and premium features',
                    },
                    'unit_amount': 1000,
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url='https://tmt-api-git-main-xukun-cais-projects.vercel.app/success',
            cancel_url='https://tmt-api-git-main-xukun-cais-projects.vercel.app/cancel',
            metadata={"user_id": "test_user"},
        )
        
        print(f"✅ Success! Checkout session created: {session.id}")
        print(f"Session URL: {session.url}")
        return True
        
    except stripe.error.StripeError as e:
        print(f"❌ Stripe error: {e}")
        return False
    except Exception as e:
        print(f"❌ General error: {e}")
        return False

if __name__ == "__main__":
    print("Stripe Checkout Session Fix Test")
    print("=" * 40)
    
    success = test_stripe_checkout_creation()
    
    if success:
        print("\n🎉 Fix successful! Payment session creation should now work.")
        print("Deploy the updated code and try the payment again.")
    else:
        print("\n⚠️  Fix may need additional adjustments.")
        print("Check the specific error message above.") 