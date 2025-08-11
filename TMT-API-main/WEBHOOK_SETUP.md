# Webhook Setup Guide for Vercel Deployment

## Overview
This guide explains how to configure Stripe webhooks to work with your Flask application deployed on Vercel at `https://tmt-api-git-main-xukun-cais-projects.vercel.app`.

## 1. Stripe Dashboard Configuration

### Step 1: Access Stripe Dashboard
1. Go to [Stripe Dashboard](https://dashboard.stripe.com/)
2. Navigate to **Developers** → **Webhooks**

### Step 2: Create Webhook Endpoint
1. Click **Add endpoint**
2. Set the endpoint URL to: `https://tmt-api-git-main-xukun-cais-projects.vercel.app/webhook`
3. Select events to listen for:
   - `checkout.session.completed`
   - `payment_intent.succeeded` (optional)
   - `payment_intent.payment_failed` (optional)

### Step 3: Get Webhook Secret
1. After creating the webhook, click on it to view details
2. Click **Reveal** next to the signing secret
3. Copy the webhook secret (starts with `whsec_`)

## 2. Vercel Environment Variables

### Step 1: Access Vercel Dashboard
1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Find your project: `tmt-api`
3. Go to **Settings** → **Environment Variables**

### Step 2: Add Environment Variables
Add these environment variables:

```
STRIPE_SECRET_KEY=sk_test_51Ri9SyFSHePhJarRDO1vrS4Ca8T8pRqsvkluFVE8sP4nc5qwiGal62fcWZAU9JeUbatWjzEZ6MQigXxOUvHwmXwJ00vr1eTfnk
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here
SECRET_KEY=your_secure_secret_key_here
DATABASE_URL=postgresql://postgres.raxegckgsveacgflvwbd:wdsjkdmmhaq@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres
VERCEL_URL=https://tmt-api-git-main-xukun-cais-projects.vercel.app
```

### Step 3: Redeploy
1. After adding environment variables, redeploy your application
2. Go to **Deployments** → **Redeploy** (latest deployment)

## 3. Testing Webhook Functionality

### Method 1: Use the Test Script
```bash
python api/test_webhook.py
```

### Method 2: Manual Testing
1. Go to your Stripe Dashboard → Webhooks
2. Click on your webhook endpoint
3. Click **Send test webhook**
4. Select `checkout.session.completed` event
5. Click **Send test webhook**

### Method 3: Check Vercel Logs
1. Go to Vercel Dashboard → Your Project
2. Click on the latest deployment
3. Go to **Functions** tab
4. Check the logs for webhook activity

## 4. Troubleshooting

### Common Issues:

#### Issue 1: Webhook not receiving events
- **Solution**: Check if the webhook URL is correct
- **Solution**: Verify the webhook is active in Stripe Dashboard
- **Solution**: Check Vercel deployment status

#### Issue 2: Database connection errors
- **Solution**: Verify DATABASE_URL environment variable
- **Solution**: Check if database is accessible from Vercel
- **Solution**: Ensure database connection pooling is configured

#### Issue 3: Signature verification failed
- **Solution**: Verify STRIPE_WEBHOOK_SECRET environment variable
- **Solution**: Check if webhook secret matches Stripe Dashboard
- **Solution**: Ensure webhook endpoint is using HTTPS

#### Issue 4: Cold start delays
- **Solution**: This is normal for serverless functions
- **Solution**: Consider using Vercel Pro for better performance
- **Solution**: Implement webhook retry logic in Stripe

## 5. Monitoring Webhooks

### Vercel Logs
- Function logs are available in Vercel Dashboard
- Check for webhook-related log messages
- Monitor for database connection issues

### Stripe Dashboard
- Webhook delivery attempts are logged
- Failed deliveries are retried automatically
- Check webhook endpoint status regularly

## 6. Production Considerations

### Security
- Use environment variables for all secrets
- Never commit API keys to version control
- Use HTTPS for all webhook endpoints

### Reliability
- Implement proper error handling
- Use database connection pooling
- Consider webhook retry mechanisms

### Performance
- Keep webhook handlers lightweight
- Use async processing for heavy operations
- Monitor function execution times

## 7. Webhook Events to Monitor

### Essential Events:
- `checkout.session.completed` - Payment successful
- `payment_intent.succeeded` - Payment confirmed
- `payment_intent.payment_failed` - Payment failed

### Optional Events:
- `customer.subscription.created` - For subscriptions
- `customer.subscription.updated` - For subscription changes
- `customer.subscription.deleted` - For subscription cancellations

## 8. Testing Checklist

- [ ] Webhook endpoint is accessible
- [ ] Environment variables are set correctly
- [ ] Database connection works
- [ ] Stripe signature verification passes
- [ ] Payment status updates correctly
- [ ] Error handling works properly
- [ ] Logs are being generated
- [ ] Webhook retries work (if needed)

## Support

If you encounter issues:
1. Check Vercel function logs
2. Verify Stripe webhook configuration
3. Test with the provided test script
4. Ensure all environment variables are set correctly 