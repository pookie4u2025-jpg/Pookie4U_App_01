# 🚀 Complete Setup Guide: RevenueCat + Google Play Billing

## ✅ Code Update Complete!

Your subscription screen has been updated with the hybrid flow:
- **Free Trial**: Managed by your backend (no payment required)
- **Paid Plans**: Managed by RevenueCat + Google Play Billing

---

## 📋 What's Been Done

### ✅ Frontend Updates
1. ✅ Installed `react-native-purchases` SDK
2. ✅ Created RevenueCat configuration file
3. ✅ Updated subscription screen with hybrid flow
4. ✅ Added RevenueCat initialization to app layout
5. ✅ Added environment variable placeholders

### ✅ Flow Implementation
- **Option 1**: Free Trial → No payment → 14 days access
- **Option 2**: Monthly (₹79) → Google Play payment → Instant access
- **Option 3**: 6-Month (₹450) → Google Play payment → Instant access

---

## 🎯 Next Steps: Setup RevenueCat & Google Play

Follow these steps in order to complete the setup:

---

## STEP 1: Create RevenueCat Account (10 minutes)

### 1.1 Sign Up
1. Go to https://www.revenuecat.com/
2. Click "Start for free"
3. Sign up with your email
4. Verify your email

### 1.2 Create Project
1. Click "Create new project"
2. Project name: **Pookie4u**
3. Select your region (India or closest)
4. Click "Create project"

### 1.3 Get Your API Keys
1. Go to "Project Settings" (gear icon)
2. Click "API Keys" tab
3. You'll see:
   - **Google Play Store** section
   - Public API Key (starts with `goog_`)
   
4. **SAVE THIS KEY** - You'll need it soon!

**📌 Keep this tab open - you'll return here after setting up Google Play Console**

---

## STEP 2: Setup Google Play Console (30 minutes)

### 2.1 Build & Upload APK

First, you need to upload an APK to enable billing:

```bash
# Navigate to frontend
cd /app/frontend

# Build development APK
eas build -p android --profile development
```

Wait for build to complete (15-20 minutes). Download the APK when ready.

### 2.2 Upload to Google Play Console

1. Log in to https://play.google.com/console/
2. Select your app (or create new app if needed)
3. Go to "Release" → "Internal testing"
4. Click "Create new release"
5. Upload your APK
6. Click "Review release" → "Start rollout"

**✅ This step enables billing for your app**

### 2.3 Create Subscription Products

#### Go to Monetization
1. In left sidebar: "Monetize" → "Subscriptions"
2. Click "Create subscription"

#### Product 1: Monthly Plan

**Base Details:**
- Subscription ID: `pookie4u_monthly_79`
- Name: `Premium Monthly`
- Description: `Monthly access to all premium features`

**Pricing:**
1. Click "Set price"
2. Select "India" as country
3. Enter price: `₹79.00`
4. Click "Apply prices"

**Base Plan:**
1. Base plan ID: `monthly`
2. Billing period: **1 month (P1M)**
3. Payment type: **Prepaid**
4. Auto-renew: **Yes**
5. Free trial: **None** (we handle this via backend!)

**Save and Activate** the product

---

#### Product 2: 6-Month Plan

**Base Details:**
- Subscription ID: `pookie4u_6month_450`
- Name: `Premium 6-Month`
- Description: `Six months of premium features at a discounted rate`

**Pricing:**
1. Click "Set price"
2. Select "India" as country
3. Enter price: `₹450.00`
4. Click "Apply prices"

**Base Plan:**
1. Base plan ID: `6month`
2. Billing period: **6 months (P6M)**
3. Payment type: **Prepaid**
4. Auto-renew: **Yes**
5. Free trial: **None**

**Save and Activate** the product

---

### 2.4 Connect Google Play to RevenueCat

#### Create Service Account

1. In Google Play Console, go to "Setup" → "API access"
2. Click "Create new service account"
3. This opens Google Cloud Console
4. Click "Create Service Account"
5. Name: `RevenueCat`
6. Click "Create and Continue"
7. Role: Select **"Pub/Sub Admin"**
8. Click "Continue" → "Done"

#### Download JSON Key

1. Find your new service account in the list
2. Click the email address
3. Go to "Keys" tab
4. Click "Add Key" → "Create new key"
5. Select **JSON** format
6. Click "Create"
7. **Save this JSON file securely**

#### Grant Permissions in Play Console

1. Return to Google Play Console → "API access"
2. Find your service account
3. Click "Grant access"
4. Under "Financial data", select:
   - ✅ View financial data
   - ✅ Manage orders and subscriptions
5. Click "Invite user" → "Send invitation"

#### Upload to RevenueCat

1. Return to RevenueCat dashboard
2. Go to "Project Settings" → "Service Credentials"
3. Click "Google Play Store" section
4. Click "Upload JSON"
5. Upload the JSON file you downloaded
6. Click "Save"

**✅ RevenueCat is now connected to Google Play!**

---

## STEP 3: Import Products to RevenueCat (5 minutes)

### 3.1 Import Products

1. In RevenueCat, go to "Products" tab
2. Click "+ Import from store"
3. Select "Google Play Store"
4. You should see both products:
   - `pookie4u_monthly_79`
   - `pookie4u_6month_450`
5. Select both checkboxes
6. Click "Import products"

### 3.2 Create Entitlement

1. Go to "Entitlements" tab
2. Click "+ New"
3. Identifier: `premium_access`
4. Display name: `Premium Access`
5. Description: `Full access to all premium features`
6. Click "Save"

### 3.3 Attach Products to Entitlement

1. Click on your "premium_access" entitlement
2. Click "Attach products"
3. Select both:
   - `pookie4u_monthly_79`
   - `pookie4u_6month_450`
4. Click "Attach"

### 3.4 Create Offering

1. Go to "Offerings" tab
2. Click "+ New"
3. Identifier: `default`
4. Display name: `Default Offering`
5. Description: `Standard subscription options`
6. Click "Create"

### 3.5 Add Packages to Offering

Click on your "default" offering, then add packages:

**Package 1: Monthly**
- Package ID: `monthly`
- Product: Select `pookie4u_monthly_79`
- Click "Add"

**Package 2: 6-Month**
- Package ID: `6_month`
- Product: Select `pookie4u_6month_450`
- Click "Add"

**Set as Current Offering:**
- Toggle "Set as current offering" to ON

**✅ RevenueCat configuration complete!**

---

## STEP 4: Add API Key to Your App (2 minutes)

### 4.1 Get Your Public API Key

1. In RevenueCat, go to "Project Settings" → "API Keys"
2. Find the "Google Play Store" section
3. Copy the **Public API Key** (starts with `goog_`)

### 4.2 Add to Environment Variables

Open `/app/frontend/.env` and add:

```bash
# RevenueCat Configuration
EXPO_PUBLIC_REVENUECAT_GOOGLE_API_KEY=goog_YOUR_KEY_HERE
```

**Replace `goog_YOUR_KEY_HERE` with your actual key from RevenueCat!**

---

## STEP 5: Restart Frontend & Test (5 minutes)

### 5.1 Restart Frontend

```bash
sudo supervisorctl restart expo
```

### 5.2 Test in Development

The free trial should work immediately (no payment required).

For paid subscriptions, you need to:
1. Build a signed APK
2. Install on test device
3. Test with sandbox payment

---

## 🧪 Testing Guide

### Test Free Trial (Works Now!)

1. Open your app
2. Navigate to subscription screen
3. Select "14 Days Free Trial"
4. Tap "Start Free Trial"
5. ✅ Should activate immediately without payment

### Test Paid Subscriptions (Requires APK on Device)

You'll need to build and test on a real Android device:

#### Build Signed APK
```bash
cd /app/frontend
eas build -p android --profile production
```

#### Setup Test Account
1. Go to Google Play Console → "Setup" → "License testing"
2. Add your test email address
3. Save changes

#### Test on Device
1. Install APK on Android device
2. Sign in with test email
3. Navigate to subscription screen
4. Select "Monthly" or "6-Month" plan
5. Tap "Subscribe Now"
6. Google Play payment sheet should open
7. Select payment method (sandbox mode - won't charge)
8. Complete test purchase
9. ✅ Should show "Subscription Activated!"

---

## 📊 Monitoring & Analytics

### RevenueCat Dashboard

After setup, you can monitor:
- Active subscriptions
- Revenue metrics
- Subscription retention
- Churn rates
- Trial conversions

Access at: https://app.revenuecat.com/

---

## 🔧 Troubleshooting

### Issue: "No offerings available"

**Solution:**
1. Verify products are created in Google Play Console
2. Verify products are imported in RevenueCat
3. Verify products are attached to entitlement
4. Verify offering is set as "current"
5. Check API key is correct in `.env`

### Issue: "Purchase failed"

**Solution:**
1. Verify you're using a test account
2. Verify test account is added in Play Console license testing
3. Verify APK is uploaded to internal testing track
4. Try clearing Google Play Store cache

### Issue: "Free trial already used"

**Expected behavior** - Trial is one-time per user. This is correct!

---

## 💡 Important Notes

### Do NOT Create Trial Product in Google Play

- ❌ Don't create `pookie4u_trial_14d` in Google Play
- ✅ Trial is handled 100% by your backend
- ✅ Only create monthly and 6-month products

### Pricing & Commission

- Google Play charges 15% commission (first $1M revenue)
- 30% commission after $1M annually
- Users see prices in INR (₹)
- Google handles currency conversion

### Auto-Renewal

- Subscriptions auto-renew unless cancelled
- Users can cancel anytime from Google Play Store app
- Access continues until end of billing period

---

## 🎉 You're All Set!

Once you complete all 5 steps:
1. ✅ Free trial works via backend (no payment)
2. ✅ Paid subscriptions work via Google Play (UPI/Cards/Net Banking)
3. ✅ All three options visible to users
4. ✅ Clean, native mobile payment experience

---

## 📞 Need Help?

- **RevenueCat Docs**: https://www.revenuecat.com/docs/getting-started
- **Google Play Billing**: https://developer.android.com/google/play/billing
- **RevenueCat Community**: https://community.revenuecat.com/

---

**Ready to go live?** Follow this guide step-by-step and you'll have a fully functional subscription system with native mobile payments!
