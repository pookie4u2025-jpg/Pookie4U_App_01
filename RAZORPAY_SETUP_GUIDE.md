# 💳 Razorpay Subscription Setup Guide for Pookie4u

Complete guide to integrate Razorpay payment gateway for your subscription plans (₹79/month and ₹450/6-month).

---

## 📋 Part 1: Create Razorpay Account

### Step 1: Sign Up for Razorpay

1. **Go to Razorpay Website:**
   - Visit: https://razorpay.com/

2. **Click "Sign Up"**
   - Usually in the top-right corner

3. **Fill in Your Details:**
   ```
   Business Email: [Your email]
   Mobile Number: [Your Indian mobile number]
   Password: [Create a strong password]
   ```

4. **Verify Your Email:**
   - Check your email inbox
   - Click the verification link
   - Your account is now created!

5. **Complete KYC (For Live Mode Later):**
   - You can skip this for now
   - Only needed when you want to accept real payments
   - Test mode works without KYC

---

## 🔑 Part 2: Get Your Test API Keys

### Step 1: Login to Razorpay Dashboard

1. Go to: https://dashboard.razorpay.com/
2. Login with your credentials
3. You'll see the Razorpay Dashboard

### Step 2: Switch to Test Mode

1. Look at the top-right corner
2. You'll see a toggle: **"Test Mode"** / **"Live Mode"**
3. Make sure it's switched to **"Test Mode"**
4. The toggle should show **"Test Mode"** in blue/green color

### Step 3: Get API Keys

1. **In the left sidebar, click on "Settings"**
2. **Click on "API Keys"** (under "Settings")
3. You'll see:
   ```
   Test Key ID: rzp_test_XXXXXXXXXXXX
   Test Key Secret: Click "Generate Test Key" if not visible
   ```

4. **Copy Both Keys:**
   - Test Key ID: `rzp_test_XXXXXXXXXXXX`
   - Test Key Secret: `XXXXXXXXXXXXXXXX` (click "Regenerate Test Keys" if needed)

5. **IMPORTANT:** Keep these keys secure!

---

## 🎯 Part 3: Create Subscription Plans

### Option A: Using Razorpay Dashboard (Recommended)

1. **Go to Dashboard:** https://dashboard.razorpay.com/
2. **Make sure you're in Test Mode**
3. **Click on "Subscriptions"** in the left sidebar
4. **Click on "Plans"** → **"Create Plan"**

### Create Plan 1: Monthly Plan (₹79/month)

```
Plan Name: Pookie4u Monthly
Billing Cycle: Monthly
Billing Amount: ₹79
Billing Currency: INR
Description: Monthly subscription to Pookie4u with 14-day free trial
Free Trial: 14 days (optional, configure after creation)
```

Click **"Create Plan"** → Copy the **Plan ID** (starts with `plan_`)

### Create Plan 2: 6-Month Plan (₹450)

```
Plan Name: Pookie4u 6-Month
Billing Cycle: Every 6 months
Billing Amount: ₹450
Billing Currency: INR
Description: 6-month subscription to Pookie4u with 14-day free trial
Free Trial: 14 days (optional)
```

Click **"Create Plan"** → Copy the **Plan ID** (starts with `plan_`)

### Save Your Plan IDs:
- Monthly Plan ID: `plan_XXXXXXXXXXXX`
- 6-Month Plan ID: `plan_XXXXXXXXXXXX`

---

## 💻 Part 4: Integration Details

### What You'll Need to Provide Me:

Once you complete the above steps, share these with me:

```
1. Razorpay Test Key ID: rzp_test_XXXXXXXXXXXX
2. Razorpay Test Key Secret: XXXXXXXXXXXXXXXX
3. Monthly Plan ID: plan_XXXXXXXXXXXX
4. 6-Month Plan ID: plan_XXXXXXXXXXXX
```

---

## 🔧 Part 5: What I'll Implement

Once you provide the keys, I'll:

### Backend Implementation:
1. Install Razorpay Python SDK
2. Create subscription API endpoints:
   - `POST /api/subscriptions/create` - Create Razorpay order
   - `POST /api/subscriptions/verify` - Verify payment
   - `GET /api/subscriptions/status` - Check subscription status
   - `POST /api/subscriptions/cancel` - Cancel subscription

### Frontend Implementation:
1. Install Razorpay React Native SDK
2. Update Subscription Screen with:
   - Razorpay payment button
   - Payment flow integration
   - Success/failure handling
   - Subscription status display

### Features:
- ✅ 14-day free trial
- ✅ Automatic subscription renewal
- ✅ Cancellation option
- ✅ Payment history
- ✅ Test card support (for testing)

---

## 🧪 Part 6: Testing Payments

### Test Cards (Use in Test Mode):

**Successful Payment:**
```
Card Number: 4111 1111 1111 1111
CVV: Any 3 digits
Expiry: Any future date
Name: Any name
```

**Failed Payment:**
```
Card Number: 4000 0000 0000 0002
CVV: Any 3 digits
Expiry: Any future date
```

**Other Test Cards:**
- Razorpay provides many test cards for different scenarios
- See: https://razorpay.com/docs/payments/payments/test-card-details/

---

## 📱 Part 7: User Flow

1. User opens app → Goes to Subscription screen
2. User selects plan (Monthly or 6-Month)
3. User clicks "Start Free Trial"
4. Razorpay payment sheet opens
5. User enters test card details
6. Payment succeeds
7. Subscription activated with 14-day trial
8. User gets full access to app features

---

## 🔐 Security Notes

### Test Mode vs Live Mode:

**Test Mode (Current):**
- Uses test API keys (`rzp_test_`)
- No real money transactions
- Test cards only
- Perfect for development

**Live Mode (Later):**
- Uses live API keys (`rzp_live_`)
- Real money transactions
- Requires KYC verification
- For production deployment

---

## 📊 Webhook Setup (I'll Handle This)

Razorpay will send webhooks for:
- `subscription.charged` - Subscription renewed
- `subscription.cancelled` - Subscription cancelled
- `subscription.completed` - Trial ended
- `payment.failed` - Payment failed

I'll create webhook endpoints to handle these automatically.

---

## 💰 Pricing Structure

**Your Plans:**
- Monthly: ₹79/month (14-day free trial)
- 6-Month: ₹450/6 months (₹75/month, saves ₹24)

**Razorpay Charges:**
- 2% per transaction + GST
- For ₹79: You receive ~₹77
- For ₹450: You receive ~₹440

---

## 🚀 Quick Start Checklist

- [ ] Create Razorpay account
- [ ] Verify email
- [ ] Login to dashboard
- [ ] Switch to Test Mode
- [ ] Generate API keys (Key ID + Key Secret)
- [ ] Create Monthly plan (₹79)
- [ ] Create 6-Month plan (₹450)
- [ ] Copy all IDs
- [ ] Share with me for integration

---

## 🆘 Need Help?

### Common Issues:

**Can't see API Keys:**
- Make sure you're in Test Mode
- Go to Settings → API Keys
- Click "Regenerate Test Keys" if needed

**Can't create plans:**
- Make sure you're in Test Mode
- Go to Subscriptions → Plans
- If option is disabled, contact Razorpay support

**Verification email not received:**
- Check spam folder
- Resend verification email
- Try a different email

---

## 📞 Razorpay Support:

- Website: https://razorpay.com/support/
- Email: support@razorpay.com
- Phone: +91-080-68727374
- Chat: Available on dashboard

---

## ✅ Next Steps:

1. **Create your Razorpay account** (5 minutes)
2. **Get your API keys** (2 minutes)
3. **Create subscription plans** (3 minutes)
4. **Share the keys with me**
5. **I'll integrate everything** (30 minutes)
6. **Test with test cards**
7. **Ready to launch!** 🎉

---

**Once you have the keys, share them with me and I'll complete the integration!**
