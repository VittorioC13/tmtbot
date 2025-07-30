# Payment Session Troubleshooting Guide

## Issue: "Failed to create payment session"

### Root Cause Analysis
The payment session creation is failing with a **401 Unauthorized** error, which indicates an authentication problem.

## 🔍 Diagnostic Steps

### 1. Check User Authentication
- Ensure you are logged in before attempting payment
- Check if your session is still valid
- Try logging out and logging back in

### 2. Test Authentication Status
Visit these endpoints to check your authentication:
- `https://tmt-api-git-main-xukun-cais-projects.vercel.app/dashboard` - Should show your dashboard if authenticated
- `https://tmt-api-git-main-xukun-cais-projects.vercel.app/login` - Login page

### 3. Browser Console Debugging
1. Open browser developer tools (F12)
2. Go to the Console tab
3. Try to create a payment session
4. Look for error messages in the console

### 4. Network Tab Analysis
1. Open browser developer tools (F12)
2. Go to the Network tab
3. Try to create a payment session
4. Check the request/response for the `/create-checkout-session` endpoint

## 🛠️ Solutions

### Solution 1: Clear Browser Data
1. Clear cookies and cache for the website
2. Log out and log back in
3. Try the payment again

### Solution 2: Check Session Configuration
The Flask session might be expiring. Check these settings:

```python
# In api/index.py
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)  # Add this line
```

### Solution 3: Verify Environment Variables
Ensure these environment variables are set in Vercel:
- `SECRET_KEY` - For session management
- `STRIPE_SECRET_KEY` - For Stripe API
- `DATABASE_URL` - For user authentication

### Solution 4: Test with Different Browser
1. Try using a different browser
2. Try in incognito/private mode
3. Disable browser extensions temporarily

## 🔧 Technical Debugging

### Run the Test Script
```bash
python api/test_payment.py
```

This will test:
- ✅ Health endpoint connectivity
- ✅ Stripe API configuration
- ❌ Payment session creation (expected to fail due to no auth)

### Check Vercel Logs
1. Go to Vercel Dashboard
2. Select your project
3. Go to Functions tab
4. Check for error logs related to authentication

### Manual Testing Steps
1. **Login**: `POST /login` with valid credentials
2. **Check Session**: Verify session cookie is set
3. **Create Payment**: `POST /create-checkout-session`
4. **Verify Response**: Should return session ID

## 🚨 Common Issues and Fixes

### Issue 1: Session Expired
**Symptoms**: 401 error after being logged in
**Fix**: 
- Clear browser cookies
- Log out and log back in
- Check if `SECRET_KEY` environment variable is set

### Issue 2: CORS Problems
**Symptoms**: Network errors in browser console
**Fix**: 
- Ensure proper headers are sent
- Check if request includes authentication cookies

### Issue 3: Database Connection
**Symptoms**: 500 errors or timeouts
**Fix**:
- Verify `DATABASE_URL` environment variable
- Check database connectivity from Vercel

### Issue 4: Stripe Configuration
**Symptoms**: Stripe API errors
**Fix**:
- Verify `STRIPE_SECRET_KEY` environment variable
- Check if Stripe account is active
- Ensure API keys are for the correct environment (test/live)

## 📋 Testing Checklist

- [ ] User can log in successfully
- [ ] Dashboard loads with user information
- [ ] Session persists across page refreshes
- [ ] Payment button is visible for non-paid users
- [ ] Clicking payment button shows "Processing..."
- [ ] No JavaScript errors in browser console
- [ ] Network request to `/create-checkout-session` is made
- [ ] Response contains session ID or clear error message
- [ ] Stripe checkout page loads (if session created)

## 🆘 Getting Help

If the issue persists:

1. **Check Vercel Logs**: Look for specific error messages
2. **Test Locally**: Run the app locally to isolate Vercel-specific issues
3. **Verify Environment**: Ensure all environment variables are set correctly
4. **Contact Support**: Provide specific error messages and steps to reproduce

## 🔄 Quick Fixes to Try

1. **Refresh the page** and try again
2. **Log out and log back in**
3. **Clear browser cache and cookies**
4. **Try a different browser**
5. **Check if you're already a paid user** (payment won't work if already paid)

## 📊 Error Code Reference

- **401 Unauthorized**: Authentication required - user not logged in
- **400 Bad Request**: Payment already completed or invalid request
- **500 Internal Server Error**: Server-side error (check logs)
- **Network Error**: Connection issues (check internet/Vercel status) 