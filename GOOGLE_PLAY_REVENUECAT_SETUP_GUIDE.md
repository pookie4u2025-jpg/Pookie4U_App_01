# Google Play Console & RevenueCat Setup Guide

## Overview
This guide will help you set up subscription products in Google Play Console and link them to RevenueCat for in-app purchases in the Pookie4u app.

---

## 📋 Prerequisites

**What You Need:**
1. ✅ Google Play Console account (https://play.google.com/console)
2. ✅ RevenueCat account (https://app.revenuecat.com)
3. ✅ Your app's APK/AAB file (we'll build this after setup)
4. ✅ Google Play Developer fee paid ($25 one-time)

**Current App Status:**
- ✅ RevenueCat SDK integrated in app
- ✅ RevenueCat API key configured
- ✅ Free trial logic implemented (14 days)
- ✅ Subscription screens ready

---

## Part 1: Google Play Console Setup

### Step 1: Create App in Play Console

1. Go to https://play.google.com/console
2. Click **"Create app"**
3. Fill in app details:
   - **App name**: Pookie4u (or your preferred name)
   - **Default language**: English (United States)
   - **App or game**: App
   - **Free or paid**: Free (subscriptions handled separately)
4. Accept declarations and click **"Create app"**

---

### Step 2: Set Up In-App Products (Subscriptions)

1. In your app dashboard, go to **"Monetize" → "Products" → "Subscriptions"**
2. Click **"Create subscription"**

**Recommended Subscription Plans:**

#### **Option A: Single Subscription (Simplest)**

**Product ID**: `pookie4u_premium_monthly`
- **Name**: Premium Membership
- **Description**: Unlock all features, unlimited tasks, and AI-powered recommendations
- **Price**: $4.99/month (or your pricing)
- **Free trial**: 14 days ✅
- **Billing period**: 1 month
- **Grace period**: 3 days (optional)

#### **Option B: Multiple Tiers (Recommended)**

**1. Monthly Plan**
- **Product ID**: `pookie4u_premium_monthly`
- **Name**: Premium Monthly
- **Price**: $4.99/month
- **Free trial**: 14 days

**2. Annual Plan (Discounted)**
- **Product ID**: `pookie4u_premium_yearly`
- **Name**: Premium Yearly
- **Price**: $49.99/year (save ~16%)
- **Free trial**: 14 days

**3. Lifetime (One-time)**
- **Product ID**: `pookie4u_premium_lifetime`
- **Name**: Premium Lifetime
- **Price**: $99.99 (one-time)
- **Free trial**: N/A (one-time purchase)

---

### Step 3: Configure Subscription Details

For each subscription:

1. **Subscription benefits** (what users get):
   - Unlimited daily and weekly tasks
   - AI-powered task recommendations
   - Advanced gift suggestions
   - Event reminders and notifications
   - Priority support
   - No ads

2. **Pricing**:
   - Set your base country pricing (USD recommended)
   - Google auto-converts to other countries

3. **Free trial** (if applicable):
   - Duration: 14 days
   - Eligible: New subscribers only

4. **Billing period**:
   - Monthly: 1 month
   - Yearly: 1 year

5. **Grace period**:
   - Recommended: 3 days
   - Helps reduce accidental cancellations

6. **Save the subscription**

---

### Step 4: Get Service Account Credentials

**Why?** RevenueCat needs these to validate subscriptions.

1. In Play Console, go to **"Setup" → "API access"**
2. If first time: Click **"Choose a project to link"** → **"Create new project"**
3. Once project linked, click **"Create new service account"**
4. Click **"Google Cloud Platform"** link (opens in new tab)
5. In Google Cloud Console:
   - Click **"+ CREATE SERVICE ACCOUNT"**
   - **Name**: `revenuecat-service-account`
   - **Description**: Service account for RevenueCat integration
   - Click **"Create and Continue"**
   - **Role**: Select **"Service Account User"**
   - Click **"Continue"** → **"Done"**
6. Back in the service accounts list:
   - Find your new service account
   - Click on it → **"Keys"** tab
   - Click **"Add Key" → "Create new key"**
   - **Key type**: JSON
   - Click **"Create"**
   - **SAVE THE JSON FILE** (you'll need this for RevenueCat)

7. Back in Play Console → API Access:
   - Find your service account
   - Click **"Grant access"**
   - Under "App permissions", select your app
   - Under "Account permissions", enable:
     - ✅ View financial data
     - ✅ Manage orders and subscriptions
   - Click **"Invite user"** → **"Send invitation"**

---

## Part 2: RevenueCat Setup

### Step 1: Log into RevenueCat

1. Go to https://app.revenuecat.com
2. Log in with your account
3. Select your project (or create new one)

---

### Step 2: Add Google Play Service Account

1. In RevenueCat dashboard, go to **"Project Settings"**
2. Click **"Integrations"** → **"Google Play Store"**
3. Upload the JSON file you downloaded from Google Cloud
4. Click **"Save"**

---

### Step 3: Configure Products in RevenueCat

1. Go to **"Products"** in the left sidebar
2. Click **"+ New"**

**For Each Subscription:**

**Monthly Plan:**
- **Identifier**: `pookie4u_premium_monthly`
- **Display name**: Premium Monthly
- **Product ID (Google)**: `pookie4u_premium_monthly`
- **Duration**: 1 month
- Click **"Add"**

**Yearly Plan:**
- **Identifier**: `pookie4u_premium_yearly`
- **Display name**: Premium Yearly
- **Product ID (Google)**: `pookie4u_premium_yearly`
- **Duration**: 1 year
- Click **"Add"**

---

### Step 4: Create Offering

**What's an Offering?** A collection of products you want to show users.

1. Go to **"Offerings"** → **"+ New Offering"**
2. **Offering identifier**: `default`
3. **Display name**: Default Offering
4. Under "Packages", click **"+ Add Package"**:
   - **Monthly Package**:
     - **Identifier**: `monthly`
     - **Product**: Select `pookie4u_premium_monthly`
   - **Annual Package**:
     - **Identifier**: `annual`
     - **Product**: Select `pookie4u_premium_yearly`
5. Set one as **"Default"** (usually monthly)
6. Click **"Save"**

---

### Step 5: Enable Test Mode

**For Testing Before Launch:**

1. In RevenueCat → **"Project Settings" → "Entitlements"**
2. Create entitlement:
   - **Identifier**: `premium`
   - **Products**: Add both monthly and yearly
3. Go to **"Customers"** → **"+ New"**
4. Add test email addresses
5. Grant them test entitlements

---

## Part 3: Update App Code (Already Done!)

**Good News:** Your app is already configured! ✅

**Current Implementation:**
```typescript
// frontend/src/config/revenuecatConfig.ts
RevenueCat API Key: Already set ✅
Entitlement ID: 'premium' ✅
```

**What's Working:**
- Free trial logic (14 days) ✅
- Subscription screens ✅
- Purchase flow UI ✅
- Subscription status checking ✅

---

## Part 4: Testing Subscriptions

### Before Publishing:

**Test Purchases (Sandbox):**

1. In Google Play Console → **"Setup" → "License testing"**
2. Add test email addresses (Gmail accounts)
3. Install app on device with test account
4. Make test purchases (won't be charged)
5. Verify in RevenueCat dashboard

**Test Scenarios:**
- ✅ Purchase subscription
- ✅ Free trial starts
- ✅ Cancel subscription
- ✅ Restore purchases
- ✅ Subscription expires

---

## Part 5: Go Live Checklist

### Before Publishing to Production:

1. **Google Play Console:**
   - [ ] All subscriptions created and active
   - [ ] Service account configured
   - [ ] Test purchases verified
   - [ ] App content rating completed
   - [ ] Store listing complete (screenshots, description)

2. **RevenueCat:**
   - [ ] Products configured
   - [ ] Offerings created
   - [ ] Google Play integration active
   - [ ] Test mode disabled (for production)

3. **App:**
   - [ ] RevenueCat API key correct
   - [ ] Subscription screens tested
   - [ ] Purchase flow works
   - [ ] Restore purchases works

4. **Build & Upload:**
   - [ ] Build production APK/AAB with EAS
   - [ ] Upload to Play Console
   - [ ] Submit for review

---

## Subscription Product IDs Summary

**Use These IDs Consistently:**

| Product | Google Play Product ID | RevenueCat Identifier | Price |
|---------|----------------------|---------------------|-------|
| Monthly | `pookie4u_premium_monthly` | `pookie4u_premium_monthly` | $4.99 |
| Yearly | `pookie4u_premium_yearly` | `pookie4u_premium_yearly` | $49.99 |
| Lifetime | `pookie4u_premium_lifetime` | `pookie4u_premium_lifetime` | $99.99 |

**Entitlement ID:** `premium` (in RevenueCat)

---

## Common Issues & Solutions

### Issue 1: "Product not found"
**Solution:** Wait 24 hours after creating products in Play Console

### Issue 2: "Unable to purchase"
**Solution:** Check service account permissions in Play Console

### Issue 3: "Subscription not active"
**Solution:** Verify RevenueCat webhook is receiving events

### Issue 4: Test purchases fail
**Solution:** Ensure test email is added to license testing in Play Console

---

## Revenue Estimates

**Pricing Strategy:**

**Conservative (1% conversion):**
- 1,000 users → 10 paying subscribers
- Monthly revenue: $49.90/month

**Average (3% conversion):**
- 1,000 users → 30 paying subscribers
- Monthly revenue: $149.70/month

**Optimistic (5% conversion):**
- 1,000 users → 50 paying subscribers
- Monthly revenue: $249.50/month

**With Yearly Plans (assume 30% choose yearly):**
- Increases LTV by ~40%
- Better revenue stability

---

## Next Steps

1. **Create Google Play Console app listing**
2. **Set up subscription products** (use IDs above)
3. **Configure service account** and upload JSON to RevenueCat
4. **Create offerings in RevenueCat**
5. **Test with sandbox account**
6. **Build production APK/AAB**
7. **Upload and submit for review**

---

## Support Links

- **Google Play Console**: https://play.google.com/console
- **RevenueCat Dashboard**: https://app.revenuecat.com
- **RevenueCat Docs**: https://docs.revenuecat.com
- **Play Billing Docs**: https://developer.android.com/google/play/billing

---

**Setup Time Estimate:** 1-2 hours
**Cost:** $25 (Google Play one-time fee)
**Revenue Potential:** $150-500/month (at 1,000 users)

Good luck with your monetization! 🚀💰
