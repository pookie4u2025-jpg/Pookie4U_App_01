# 🚀 Complete APK Build & Google Play Billing Setup Guide

## Overview
This guide will walk you through:
1. Building your APK via Expo
2. Setting up Google Play Console
3. Creating subscription products (₹79/month & ₹450/6-month)
4. Connecting RevenueCat for billing
5. Testing the complete flow

---

## PART 1: Build APK via Expo Website (15-20 minutes)

### Step 1: Access Expo Dashboard

**Go to:**
```
https://expo.dev/accounts/pookie4u/projects/pookie4u-v1/builds
```

### Step 2: Create New Build

1. Click **"Create a build"** button (top right)

2. **Configure the build:**
   - **Platform:** Select **Android** 📱
   - **Profile:** Select **preview** (creates APK)
   - **Git branch:** Select **main** or latest commit

3. Click **"Build"** button

### Step 3: Monitor Build Progress

- Build will take **15-20 minutes**
- You can watch live logs on the build page
- You'll get email notification when complete

**Build URL format:**
```
https://expo.dev/accounts/pookie4u/projects/pookie4u-v1/builds/[BUILD-ID]
```

### Step 4: Download APK

Once build shows **"Finished"** status:
1. Click **"Download"** button
2. Save file: `pookie4u-preview.apk` (~50-100 MB)

**✅ You now have your APK!**

---

## PART 2: Google Play Console Setup (30 minutes)

### Step 1: Upload APK to Internal Testing

1. **Log in:** https://play.google.com/console/
2. **Select your app** (or create new one)
3. Navigate to: **"Release" → "Testing" → "Internal testing"**
4. Click **"Create new release"**
5. **Upload your APK** (drag & drop or browse)
6. Add release notes (optional)
7. Click **"Review release"** → **"Start rollout"**

**✅ Billing is now enabled for your app!**

### Step 2: Complete Required App Content

Before creating subscriptions, you need:

**A. Privacy Policy**
- Go to: "App content" → "Privacy policy"
- Enter your privacy policy URL
- Save

**B. App Access**
- Go to: "App content" → "App access"
- Select access type
- Save

**C. Target Audience**
- Go to: "App content" → "Target audience"
- Select age groups
- Save

**D. Content Rating**
- Go to: "App content" → "Content rating"
- Complete questionnaire
- Submit

---

## PART 3: Create Subscription Products (20 minutes)

### Product 1: Monthly Plan (₹79)

**Navigate to:** "Monetize" → "Subscriptions" → "Create subscription"

**Step 1: Basic Details**
```
Subscription ID: pookie4u_monthly_79
Name: Premium Monthly
Description: Monthly access to all premium features including AI-powered relationship tasks, daily romantic messages, event reminders, and personalized gift suggestions.
```

**Step 2: Base Plan**
```
Base plan ID: monthly
Billing period: 1 month (P1M)
Grace period: 3 days (recommended)
Account hold: Yes
Auto-renewing: Yes
```

**Step 3: Skip Free Trial**
- Click "No thanks" or "Skip"
- Your backend handles the 14-day trial!

**Step 4: Set Pricing**
```
Country: India
Price: ₹79.00
```

**Step 5: Activate**
- Review all details
- Click **"Activate"**

**✅ Monthly subscription created!**

---

### Product 2: 6-Month Plan (₹450)

**Click "Create subscription" again**

**Step 1: Basic Details**
```
Subscription ID: pookie4u_6month_450
Name: Premium 6-Month
Description: Get 6 months of full premium access at a discounted rate. Save ₹24 compared to monthly plan! Includes all premium features.
```

**Step 2: Base Plan**
```
Base plan ID: 6month
Billing period: 6 months (P6M) or 26 weeks (P26W)
Grace period: 3 days
Account hold: Yes
Auto-renewing: Yes
```

**Step 3: Skip Free Trial**
- Click "No thanks"

**Step 4: Set Pricing**
```
Country: India
Price: ₹450.00
```

**Step 5: Activate**
- Review and activate

**✅ 6-Month subscription created!**

---

## PART 4: Connect Google Play to RevenueCat (20 minutes)

### Step 1: Create Service Account

**In Google Play Console:**
1. Go to: **"Setup" → "API access"**
2. Click **"Create new service account"**
3. Opens Google Cloud Console (new tab)

**In Google Cloud Console:**
4. Click **"+ Create Service Account"**
5. Name: `RevenueCat`
6. Click "Create and Continue"
7. Role: Select **"Pub/Sub Admin"**
8. Click "Continue" → "Done"

### Step 2: Download JSON Key

1. Find your service account in the list
2. Click on the email address
3. Go to **"Keys"** tab
4. Click **"Add Key" → "Create new key"**
5. Select **JSON** format
6. Click **"Create"**
7. **Save the JSON file securely!**

### Step 3: Grant Permissions in Play Console

**Back in Google Play Console:**
1. Go to: "Setup" → "API access"
2. Find your service account
3. Click **"Grant access"**
4. Select permissions:
   - ✅ View financial data, orders, and subscription details
   - ✅ Manage orders and subscriptions
5. Click "Invite user" → "Send invitation"

### Step 4: Upload JSON to RevenueCat

1. **Go to:** https://app.revenuecat.com/
2. Select project: **"POOKIE4U"**
3. Go to: **"Project Settings" → "Service Credentials"**
4. Find **"Google Play Store"** section
5. Click **"Upload JSON"**
6. Upload your downloaded JSON file
7. Click **"Save"**

**✅ Google Play connected to RevenueCat!**

---

## PART 5: Import Products to RevenueCat (10 minutes)

### Step 1: Import Products

1. In RevenueCat, go to **"Products"** tab
2. Click **"+ Import from store"**
3. Select **"Google Play Store"**
4. You should see:
   - ☑️ `pookie4u_monthly_79`
   - ☑️ `pookie4u_6month_450`
5. Select both
6. Click **"Import"**

**✅ Products imported!**

### Step 2: Verify Entitlement

1. Go to **"Entitlements"** tab
2. You should see: **"premium_access"** (already created)
3. Click on it
4. Verify both products are attached:
   - ✅ `pookie4u_monthly_79`
   - ✅ `pookie4u_6month_450`

### Step 3: Verify Offering

1. Go to **"Offerings"** tab
2. You should see: **"default"** (already created)
3. Click on it
4. Verify packages:
   - ✅ Package: `monthly` → Product: `pookie4u_monthly_79`
   - ✅ Package: `6_month` → Product: `pookie4u_6month_450`
5. Verify **"Current offering"** toggle is ON

**✅ RevenueCat fully configured!**

---

## PART 6: Setup Testing (10 minutes)

### Step 1: Add Test Account

**In Google Play Console:**
1. Go to: **"Setup" → "License testing"**
2. Add your test email address
3. Click **"Save"**

**License test response:** Select **"RESPOND_NORMALLY"**

### Step 2: Install APK on Test Device

1. Transfer APK to your Android phone
2. Enable **"Install from unknown sources"**
3. Open APK file and install
4. Sign in with your test email

### Step 3: Test Subscription Flow

**Test Free Trial:**
1. Open app → Navigate to subscription screen
2. Tap **"14 Days Free Trial"**
3. Should activate instantly (no payment)
4. ✅ Verify premium access granted

**Test Paid Subscription:**
1. Go to subscription screen
2. Tap **"₹79/month"** or **"₹450/6-month"**
3. Google Play payment sheet should open
4. Select payment method (UPI/Card/Net Banking)
5. Complete test purchase (won't charge in test mode)
6. ✅ Verify subscription activated

---

## 🎉 Complete Setup Checklist

### Google Play Console ✅
- [ ] APK uploaded to internal testing
- [ ] App content sections completed
- [ ] Monthly subscription created (`pookie4u_monthly_79`)
- [ ] 6-Month subscription created (`pookie4u_6month_450`)
- [ ] Service account created
- [ ] JSON key downloaded
- [ ] Permissions granted
- [ ] Test account added

### RevenueCat ✅
- [ ] JSON uploaded
- [ ] Products imported
- [ ] Entitlement verified (`premium_access`)
- [ ] Offering verified (`default`)
- [ ] API key added to app (already done: `goog_KSbdtDTiaRVbYFhZaizivhPdEVy`)

### Testing ✅
- [ ] APK installed on test device
- [ ] Free trial tested
- [ ] Paid subscription tested
- [ ] UPI payment tested

---

## 📊 Your Current App Configuration

**Already Configured in Your App:**
- ✅ RevenueCat SDK installed (`react-native-purchases`)
- ✅ RevenueCat API key configured
- ✅ Hybrid subscription flow implemented
- ✅ Free trial: Backend-managed (14 days)
- ✅ Paid plans: Google Play Billing via RevenueCat
- ✅ Subscription UI ready

**Package Name:**
```
com.pookie4u.app
```

**RevenueCat API Key:**
```
goog_KSbdtDTiaRVbYFhZaizivhPdEVy
```

---

## 🔧 Troubleshooting

### Issue: "Product not found"
**Solution:** Products not synced yet
- Wait 5-10 minutes after import
- Restart app
- Check products in RevenueCat dashboard

### Issue: "Unable to purchase"
**Solution:** Billing not enabled
- Verify APK uploaded to internal testing
- Verify service account has permissions
- Check JSON uploaded correctly

### Issue: Free trial requires payment
**Solution:** Trial in Google Play instead of backend
- Free trial should NOT be in Google Play products
- Backend handles trial automatically

### Issue: Price not showing
**Solution:** Country not configured
- Add India pricing in Google Play Console
- Wait for sync to RevenueCat

---

## 💡 Important Notes

### DO NOT Create Trial in Google Play!
- ❌ Don't create `pookie4u_trial_14d` in Google Play
- ✅ Backend handles free trial automatically
- ✅ Only create 2 products: monthly & 6-month

### Pricing & Commission
- Google Play charges 15% commission (first $1M)
- 30% after $1M annually
- Users see prices in INR (₹)

### Testing Limitations
- Test purchases won't be charged
- Sandbox subscriptions renew faster (monthly = 5 mins)
- Use only test accounts for development

---

## 🎯 Timeline Summary

| Step | Duration |
|------|----------|
| Build APK | 15-20 min |
| Upload to Play Console | 5-10 min |
| Create subscriptions | 20 min |
| Connect RevenueCat | 20 min |
| Import & verify | 10 min |
| Testing setup | 10 min |
| **Total** | **~1.5-2 hours** |

---

## 📞 Next Steps After Setup

Once everything is working:

1. **Monitor Dashboard:**
   - RevenueCat: Track subscriptions
   - Google Play: Monitor revenue

2. **Build Production APK:**
   - Use `production` profile instead of `preview`
   - Creates AAB for Play Store release

3. **Submit to Play Store:**
   - Complete store listing
   - Add screenshots
   - Submit for review

---

**Ready to start? Begin with Part 1: Build APK via Expo!** 🚀
