# Stripe Webhook Setup Guide

## Overview
This guide explains how to set up Stripe webhooks for the TMT Bot payment system to automatically activate user subscriptions when payments are completed.

## Prerequisites
- Stripe account with API keys configured
- Webhook endpoint accessible from the internet (for production)

## Step 1: Get Your Webhook Secret

1. Log into your Stripe Dashboard
2. Go to **Developers** > **Webhooks**
3. Click **Add endpoint**
4. Set the endpoint URL to: `https://yourdomain.com/webhook`
5. Select the following events:
   - `checkout.session.completed`
6. Click **Add endpoint**
7. Copy the **Signing secret** (starts with `whsec_`)

## Step 2: Configure Environment Variables

Add the webhook secret to your `.env` file:

```bash
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here
```

## Step 3: Test the Webhook

### Using Stripe CLI (Recommended for Development)

1. Install Stripe CLI: https://stripe.com/docs/stripe-cli
2. Login to your Stripe account:
   ```bash
   stripe login
   ```
3. Forward webhooks to your local server:
   ```bash
   stripe listen --forward-to localhost:5000/webhook
   ```
4. The CLI will provide a webhook signing secret for local testing

### Using Stripe Dashboard

1. Go to your webhook endpoint in the Stripe Dashboard
2. Click **Send test webhook**
3. Select `checkout.session.completed` event
4. Click **Send test webhook**

## Step 4: Verify Webhook Functionality

1. Make a test payment through your application
2. Check the webhook logs in your Stripe Dashboard
3. Verify that the user's subscription status is updated in your database
4. Check your application logs for webhook processing messages

## Security Considerations

- **Never expose your webhook secret** in client-side code
- **Always verify webhook signatures** (already implemented in the code)
- **Use HTTPS** for webhook endpoints in production
- **Monitor webhook failures** in your Stripe Dashboard

## Troubleshooting

### Common Issues

1. **Webhook signature verification fails**
   - Ensure the webhook secret is correctly set in your environment
   - Check that the webhook URL is accessible

2. **User subscription not updated**
   - Verify the user_id and plan are correctly passed in metadata
   - Check database connection and transaction handling

3. **Webhook not received**
   - Ensure your server is accessible from the internet
   - Check firewall settings
   - Verify the webhook URL is correct

### Debugging

The application now includes comprehensive debug logging for webhook processing. You'll see detailed logs with emojis for easy identification:

#### Log Output Examples

**Webhook Received:**
```
🔔 Webhook received from Stripe
📋 Request headers: {...}
📄 Payload length: 1234 characters
🔐 Signature header: t=1234567890,v1=abc123...
🔑 Webhook secret configured: Yes
✅ Webhook signature verified successfully
```

**Checkout Session Completed:**
```
💰 Processing checkout.session.completed event
🛒 Session ID: cs_test_abc123
💳 Payment status: paid
💰 Amount total: 2000
💱 Currency: usd
📋 Metadata: {'user_id': '123', 'plan': 'premium', 'username': 'john_doe'}
👤 User ID from metadata: 123
📦 Plan from metadata: premium
👤 Username from metadata: john_doe
✅ Found user: john_doe (ID: 123)
📊 Current premium status: none
⏰ Current expiration: None
✅ User john_doe upgraded from none to premium plan
⏰ New expiration: 2025-01-15 10:30:00
```

#### Testing Webhooks

Use the included test script to verify webhook functionality:

```bash
python test_webhook.py
```

This script will:
- Check webhook configuration
- Test endpoint accessibility
- Simulate webhook events
- Verify processing

#### Manual Testing

You can also test webhooks manually using Stripe CLI:

```bash
# Install Stripe CLI
stripe listen --forward-to localhost:5000/webhook

# In another terminal, trigger a test event
stripe trigger checkout.session.completed
```

## Production Deployment

For production deployment:

1. **Use a proper domain** for your webhook endpoint
2. **Set up SSL/TLS** (HTTPS is required)
3. **Configure proper error handling** and retry logic
4. **Monitor webhook delivery** in Stripe Dashboard
5. **Set up alerts** for webhook failures

## Webhook Events Handled

Currently, the application handles:
- `checkout.session.completed`: Activates user subscription when payment is successful

Future events that could be added:
- `invoice.payment_failed`: Handle failed recurring payments
- `customer.subscription.deleted`: Handle subscription cancellations
- `payment_intent.succeeded`: Alternative payment confirmation

