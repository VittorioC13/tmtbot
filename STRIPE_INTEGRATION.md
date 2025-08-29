# Stripe Integration for TMT Bot

## Overview

The TMT Bot application now uses Stripe for credit card payments, replacing the previous PayPal integration. This provides a more secure and reliable payment processing solution with automatic subscription activation.

## Features

- **Secure Credit Card Processing**: Stripe handles all payment data securely
- **Automatic Subscription Activation**: Webhooks automatically activate user subscriptions
- **Multiple Plan Support**: Basic ($4), Premium ($20), and Max ($50) plans
- **Success/Cancel Pages**: Proper user feedback for payment outcomes
- **Webhook Verification**: Secure webhook signature verification

## Configuration

### Environment Variables

Add the following to your `.env` file:

```bash
# Stripe Configuration
STRIPE_PUB=pk_test_your_public_key_here
STRIPE_SEC=sk_test_your_secret_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here
```

### Getting Stripe Keys

1. Create a Stripe account at https://stripe.com
2. Go to **Developers** > **API keys**
3. Copy your **Publishable key** and **Secret key**
4. For production, use the live keys instead of test keys

## API Endpoints

### Create Checkout Session
- **URL**: `/api/create-checkout-session`
- **Method**: `POST`
- **Authentication**: Required
- **Body**: `{"plan": "basic|premium|max"}`

### Stripe Webhook
- **URL**: `/webhook`
- **Method**: `POST`
- **Authentication**: None (verified by signature)
- **Purpose**: Handle payment completion events

### Payment Success
- **URL**: `/payment/success`
- **Method**: `GET`
- **Authentication**: Required
- **Purpose**: Success page after payment

### Payment Cancel
- **URL**: `/payment/cancel`
- **Method**: `GET`
- **Authentication**: Required
- **Purpose**: Cancellation page

## Payment Flow

1. **User selects a plan** on the payment page
2. **User chooses credit card payment** method
3. **Frontend calls** `/api/create-checkout-session` with plan details
4. **Backend creates** Stripe checkout session with metadata
5. **User is redirected** to Stripe's secure payment page
6. **User completes payment** on Stripe's page
7. **Stripe sends webhook** to `/webhook`
8. **Backend processes webhook** and activates user subscription
9. **User is redirected** to success page

## Plan Pricing

| Plan | Price (USD) | Price (CNY) | Features |
|------|-------------|-------------|----------|
| Basic | $4.00 | ¥28 | Single sector access |
| Premium | $20.00 | ¥140 | All sectors + AI chat |
| Max | $50.00 | ¥350 | Premium + mentorship |

## Security Features

- **Webhook Signature Verification**: All webhooks are verified using Stripe's signature
- **Metadata Validation**: User ID and plan are validated before subscription activation
- **HTTPS Required**: All webhook endpoints require HTTPS in production
- **No Sensitive Data**: Payment data never touches your servers

## Testing

### Test Cards

Use these test card numbers for testing:

- **Success**: `4242 4242 4242 4242`
- **Decline**: `4000 0000 0000 0002`
- **Requires Authentication**: `4000 0025 0000 3155`

### Test Script

Run the included test script to verify your configuration:

```bash
python test_stripe.py
```

## Webhook Setup

See `STRIPE_WEBHOOK_SETUP.md` for detailed webhook configuration instructions.

## Error Handling

The application handles various error scenarios:

- **Payment Declined**: User sees error message and can retry
- **Network Errors**: Proper error messages with retry options
- **Webhook Failures**: Logged for debugging, manual intervention may be needed
- **Invalid Plans**: 400 error returned for invalid plan selections

## Monitoring

### Stripe Dashboard

Monitor payments and webhooks in your Stripe Dashboard:
- **Payments**: https://dashboard.stripe.com/payments
- **Webhooks**: https://dashboard.stripe.com/webhooks
- **Logs**: https://dashboard.stripe.com/logs

### Application Logs

The application logs webhook processing:
- Successful subscription activations
- Webhook verification failures
- Database errors during subscription updates

## Migration from PayPal

The PayPal integration has been completely replaced with Stripe. The legacy `/api/verify-payment` endpoint is kept for compatibility but is no longer used in the frontend.

## Production Deployment

1. **Switch to Live Keys**: Use live Stripe keys instead of test keys
2. **Set Up Webhooks**: Configure webhook endpoint with live webhook secret
3. **Enable HTTPS**: Ensure your domain has valid SSL certificate
4. **Monitor Logs**: Set up monitoring for webhook failures
5. **Test Payments**: Verify the complete payment flow with real cards

## Support

For Stripe-related issues:
- **Stripe Documentation**: https://stripe.com/docs
- **Stripe Support**: https://support.stripe.com
- **Webhook Testing**: Use Stripe CLI for local development

