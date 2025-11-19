# Step-by-Step Account Setup Guide
## Google Play Console + RevenueCat

---

## STEP 1: Google Play Console Account Setup

### Prerequisites
- ✅ Google Account (Gmail)
- ✅ $25 USD (one-time registration fee)
- ✅ Valid payment method (Credit/Debit card)
- ✅ Developer identity verification

### Account Creation Process (15-30 minutes)

#### 1.1 Navigate to Google Play Console
```
URL: https://play.google.com/console/signup
```

#### 1.2 Sign In
- Use your Google Account
- Accept Developer Distribution Agreement

#### 1.3 Account Type Selection
**Choose:** Developer Account (Individual)
- Unless you're registering as an Organization

#### 1.4 Complete Developer Profile

**Required Information:**
```
Developer Name: [Your Name or Studio Name]
- This will be visible to users on Play Store
- Example: "Pookie4u" or "Your Name"

Email Address: [Your Gmail]
- For important communications from Google

Phone Number: [Your Number]
- For account security and verification

Country: India (or your location)
```

#### 1.5 Pay Registration Fee
- **Amount:** $25 USD (one-time, lifetime access)
- **Payment Methods:** Credit Card, Debit Card
- **Note:** This fee is non-refundable

#### 1.6 Identity Verification
Google may require:
- Government-issued ID (Passport, Driver's License, Aadhaar)
- Selfie verification
- Processing time: 1-3 business days

#### 1.7 Account Approval
- Wait for email confirmation
- Typically takes: 1-48 hours
- **Status Check:** https://play.google.com/console

---

## STEP 2: RevenueCat Account Setup

### Prerequisites
- ✅ Email address
- ✅ Company/App name
- ✅ Google Play Console access (can link later)

### Account Creation Process (10-15 minutes)

#### 2.1 Navigate to RevenueCat
```
URL: https://www.revenuecat.com/
```

#### 2.2 Sign Up
- Click "Get Started Free" or "Sign Up"
- Use your email (preferably same as Google Play)

#### 2.3 Choose Plan
**Select:** Free Plan
- ✅ Free up to $10,000 in tracked revenue/month
- ✅ Perfect for launch and early growth
- ✅ No credit card required

#### 2.4 Create Organization
```
Organization Name: Pookie4u
Website (optional): [Your website if any]
```

#### 2.5 Create Project
```
Project Name: Pookie4u Production
App Name: Pookie4u
```

#### 2.6 Add App Platform
- Click "Add App"
- **Platform:** Android
- **Package Name:** `com.pookie4u.app`
  (Must match your app.json exactly!)

---

## STEP 3: Link RevenueCat to Google Play Console

### Prerequisites
- ✅ Google Play Console account active
- ✅ RevenueCat account created
- ✅ App added to RevenueCat

### Connection Process (20-30 minutes)

#### 3.1 Create Google Cloud Service Account

**Step A: Go to Google Cloud Console**
```
URL: https://console.cloud.google.com
```

**Step B: Create New Project**
```
Project Name: Pookie4u
Project ID: pookie4u-[random] (auto-generated)
Click "Create"
```

**Step C: Enable Google Play Android Developer API**
1. Search for "Google Play Android Developer API"
2. Click "Enable"
3. Wait for activation

**Step D: Create Service Account**
1. Navigate to: IAM & Admin → Service Accounts
2. Click "+ CREATE SERVICE ACCOUNT"
3. Fill details:
   ```
   Service account name: revenuecat-service
   Service account ID: revenuecat-service (auto-generated)
   Description: RevenueCat integration for Pookie4u
   ```
4. Click "Create and Continue"
5. Grant Role: **Service Account User**
6. Click "Continue" → "Done"

**Step E: Create JSON Key**
1. Click on the newly created service account
2. Go to "Keys" tab
3. Click "Add Key" → "Create New Key"
4. Choose: **JSON**
5. Click "Create"
6. **File downloads automatically - Save it securely!**
   - File name: `pookie4u-xxxxx.json`
   - **NEVER share this file publicly**

#### 3.2 Link Service Account to Google Play Console

**Step A: Go to Play Console**
```
URL: https://play.google.com/console
```

**Step B: Navigate to API Access**
1. Go to: Setup → API access
2. Scroll to "Service accounts"
3. Click "Link" on your project

**Step C: Grant Permissions**
1. Find your service account: `revenuecat-service@...`
2. Click "Grant Access"
3. Select permissions:
   - ✅ View financial data
   - ✅ Manage orders and subscriptions
4. Click "Invite User" → "Send Invitation"

#### 3.3 Upload to RevenueCat

**Step A: Go to RevenueCat Dashboard**
```
URL: https://app.revenuecat.com
```

**Step B: Configure Play Store**
1. Select your project: "Pookie4u Production"
2. Go to: Project Settings → Google Play
3. Click "Add Credentials"

**Step C: Upload Service Account JSON**
1. Choose the downloaded `.json` file
2. Click "Upload"
3. Wait for validation: "✓ Successfully connected"

---

## STEP 4: Create Subscription Products in Google Play

### Prerequisites
- ✅ Google Play Console access
- ✅ App created (we'll do this together)

### Create App Placeholder (5 minutes)

#### 4.1 Create App in Play Console
1. Go to: https://play.google.com/console
2. Click "Create app"
3. Fill details:
   ```
   App name: Pookie4u
   Default language: English (India)
   App or game: App
   Free or paid: Free
   ```
4. Accept declarations
5. Click "Create app"

### Create Subscription Products (15-20 minutes)

#### 4.2 Navigate to Subscriptions
```
Path: Monetize → Products → Subscriptions
```

#### 4.3 Create Monthly Subscription

**Click "Create subscription"**

**Base Details:**
```
Product ID: pookie4u_monthly
(IMPORTANT: This MUST match exactly!)

Name: Pookie4u Premium - Monthly

Description:
Monthly subscription to Pookie4u Premium features. 
Strengthen your relationship with AI-powered daily tasks, 
romantic messages, and smart gift recommendations.
```

**Base Plan:**
```
Plan ID: monthly-base

Billing period: 1 month (Monthly)

Price: ₹79 INR
(Will ask for price points by country - use ₹79 for India)

Auto-renewing: YES ✓ (CRITICAL!)

Free Trial:
- Eligibility: New subscribers only
- Duration: 14 days
- Price: ₹0
```

**Benefits (Optional but Recommended):**
- AI-generated daily tasks
- Personalized romantic messages  
- Smart gift recommendations
- Date planning assistance
- Unlimited event reminders

Click "Activate" when done

#### 4.4 Create Half-Yearly Subscription

**Click "Create subscription" again**

**Base Details:**
```
Product ID: pookie4u_half_yearly
(IMPORTANT: This MUST match exactly!)

Name: Pookie4u Premium - 6 Months

Description:
6-month subscription to Pookie4u Premium (Save 25%!). 
Strengthen your relationship with AI-powered daily tasks, 
romantic messages, and smart gift recommendations.
```

**Base Plan:**
```
Plan ID: half-yearly-base

Billing period: 6 months (P6M)

Price: ₹450 INR
(Monthly equivalent: ₹75 - Save ₹4/month!)

Auto-renewing: YES ✓ (CRITICAL!)

Free Trial:
- Eligibility: New subscribers only
- Duration: 14 days
- Price: ₹0
```

**Benefits:** (Same as monthly)

Click "Activate" when done

---

## STEP 5: Configure Subscription Products in RevenueCat

### Prerequisites
- ✅ Subscription products created in Play Console
- ✅ Products are "Active"

### Add Products to RevenueCat (10 minutes)

#### 5.1 Navigate to Products
```
RevenueCat Dashboard → Products
```

#### 5.2 Add Monthly Subscription

**Click "+ New"**
```
Identifier: pookie4u_monthly
Type: Subscription
Store: Google Play Store
Product Identifier: pookie4u_monthly
```
Click "Add"

#### 5.3 Add Half-Yearly Subscription

**Click "+ New"**
```
Identifier: pookie4u_half_yearly
Type: Subscription
Store: Google Play Store
Product Identifier: pookie4u_half_yearly
```
Click "Add"

---

## STEP 6: Create Offering in RevenueCat

### What is an Offering?
- Groups products together
- Allows A/B testing different pricing
- Makes it easy to change products without app updates

### Create Offering (5 minutes)

#### 6.1 Navigate to Offerings
```
RevenueCat Dashboard → Offerings
```

#### 6.2 Create Default Offering

**Click "+ New Offering"**
```
Identifier: default
Description: Pookie4u Premium Plans
```

#### 6.3 Add Packages

**Package 1: Monthly**
```
Identifier: $rc_monthly
Product: pookie4u_monthly
Position: 1
```

**Package 2: Half-Yearly (Recommended)**
```
Identifier: $rc_half_yearly
Product: pookie4u_half_yearly
Position: 0 (displays first - recommended option)
```

Click "Save"

---

## STEP 7: Get RevenueCat API Key

### Get Public SDK Key (2 minutes)

#### 7.1 Navigate to API Keys
```
RevenueCat Dashboard → Project Settings → API Keys
```

#### 7.2 Copy Public Key
- Find: "Google Play Public SDK Key"
- Format: `goog_xxxxxxxxxxxxxxxxxx`
- Click "Copy"

#### 7.3 Add to App Environment
**Open:** `/app/frontend/.env`

**Add line:**
```
EXPO_PUBLIC_REVENUECAT_GOOGLE_API_KEY=goog_xxxxxxxxxxxxxxxxxx
```

**Save the file**

---

## VERIFICATION CHECKLIST

### Google Play Console
- [ ] Account created and verified
- [ ] $25 registration fee paid
- [ ] Developer profile complete
- [ ] App created: "Pookie4u"
- [ ] Monthly subscription created (pookie4u_monthly)
- [ ] Half-yearly subscription created (pookie4u_half_yearly)
- [ ] Both subscriptions set to auto-renew
- [ ] 14-day free trial configured
- [ ] Prices set correctly (₹79, ₹450)

### RevenueCat
- [ ] Account created (free plan)
- [ ] Project created: "Pookie4u Production"
- [ ] App added (com.pookie4u.app)
- [ ] Google Cloud service account created
- [ ] Service account JSON uploaded to RevenueCat
- [ ] Play Console permissions granted
- [ ] Products added (monthly, half-yearly)
- [ ] Offering created with packages
- [ ] API key copied and added to .env

---

## TROUBLESHOOTING

### Issue: "Product not found" in RevenueCat
**Solution:**
- Verify Product IDs match EXACTLY:
  - Play Console: `pookie4u_monthly`
  - RevenueCat: `pookie4u_monthly`
- Check subscription is "Active" in Play Console

### Issue: "Invalid credentials" when linking
**Solution:**
- Regenerate service account JSON key
- Ensure permissions granted in Play Console
- Wait 5 minutes for permissions to propagate

### Issue: "App not found" in RevenueCat
**Solution:**
- Verify package name matches: `com.pookie4u.app`
- Check in app.json: `"package": "com.pookie4u.app"`

---

## NEXT STEPS AFTER SETUP

Once all accounts are configured:

1. **Restart Backend**
   ```bash
   sudo supervisorctl restart backend expo
   ```

2. **Test Subscription Flow**
   - Open app
   - Navigate to subscription screen
   - Verify products load
   - Test purchase (use test account)

3. **Verify in RevenueCat Dashboard**
   - Check if test purchase appears
   - Verify subscription status

4. **Continue with Launch Preparation**
   - Create privacy policy
   - Capture screenshots
   - Final testing
   - Build production APK

---

## ESTIMATED TIME

| Step | Time | Status |
|------|------|--------|
| Google Play Console signup | 30 min | ⏳ |
| Identity verification wait | 1-48 hrs | ⏳ |
| RevenueCat account | 10 min | ⏳ |
| Service account setup | 30 min | ⏳ |
| Create subscriptions | 20 min | ⏳ |
| Configure RevenueCat | 15 min | ⏳ |
| **Total Active Time** | **~2 hours** | |
| **Total with waiting** | **1-2 days** | |

---

## COSTS SUMMARY

| Item | Cost | Frequency |
|------|------|-----------|
| Google Play Developer | $25 | One-time |
| RevenueCat Free Plan | $0 | Monthly* |
| Google Cloud | $0 | Free tier |
| **Total to Start** | **$25** | |

*RevenueCat free up to $10k MRR, then $0.01 per subscriber

---

## SUPPORT RESOURCES

- **Google Play Console Help:** https://support.google.com/googleplay/android-developer
- **RevenueCat Docs:** https://docs.revenuecat.com/docs/google-play-store
- **RevenueCat Support:** https://community.revenuecat.com

---

**Ready to proceed?** Follow the steps above in order. Each step builds on the previous one.

**Questions?** Let me know which step you're on and I can provide more detailed guidance!

**Status:** Waiting for account creation to proceed with integration 🚀
