# 🎮 Google Play Console - Subscription Products Setup

## Prerequisites

- ✅ APK uploaded to Internal Testing track (see BUILD_AND_UPLOAD_APK_GUIDE.md)
- ✅ Google Play Console developer account
- ✅ App created in Play Console

---

## STEP 1: Create Subscription Products

### 1.1 Navigate to Subscriptions

1. Log in to https://play.google.com/console/
2. Select your app **"Pookie4u"**
3. In left sidebar, go to **"Monetize" → "Subscriptions"**
4. Click **"Create subscription"** button

---

## STEP 2: Create Product #1 - Monthly Plan (₹79)

### 2.1 Basic Details

**Subscription ID:** `pookie4u_monthly_79`
- ⚠️ This ID cannot be changed later!
- Must match exactly with RevenueCat configuration

**Name:** `Premium Monthly`

**Description:**
```
Get full access to all premium features including AI-powered relationship tasks, daily romantic messages, event reminders, and personalized gift suggestions. Subscription automatically renews monthly.
```

Click **"Continue"**

---

### 2.2 Set Base Plan

Click **"Add base plan"**

**Base plan ID:** `monthly`

**Billing period:** 
- Select **"Monthly"**
- Or select **"Custom"** and enter **"1 month"** (P1M)

**Grace period:** 
- Select **"3 days"** (recommended)
- This gives users time to fix payment issues

**Account hold:**
- Enable **"Yes"** (recommended)
- Helps recover failed payments

**Resubscribe:**
- Enable **"Yes"**
- Allows users to resubscribe if cancelled

**Auto-renewing:**
- Select **"Yes"**
- Subscription renews automatically

Click **"Continue"**

---

### 2.3 Add Offer (Free Trial)

⚠️ **IMPORTANT:** Skip this section! Click **"No thanks"** or **"Skip"**

**Why?** Your free trial is managed by your backend, not Google Play.

Click **"Continue"**

---

### 2.4 Set Pricing

1. Click **"Add price"**
2. Select **"India"** from country list
3. Enter price: **₹79.00**
4. Click **"Apply"**

**Optional:** Add other countries if needed
- Google will suggest prices in other currencies based on ₹79

Click **"Continue"**

---

### 2.5 Review and Activate

1. Review all details:
   - ✅ Subscription ID: `pookie4u_monthly_79`
   - ✅ Base plan: `monthly`
   - ✅ Billing period: 1 month
   - ✅ Price: ₹79.00
   - ✅ Auto-renewing: Yes

2. Click **"Activate"**

**✅ Monthly subscription product created!**

---

## STEP 3: Create Product #2 - 6-Month Plan (₹450)

### 3.1 Basic Details

Click **"Create subscription"** again

**Subscription ID:** `pookie4u_6month_450`
- ⚠️ This ID cannot be changed later!

**Name:** `Premium 6-Month`

**Description:**
```
Get 6 months of full premium access at a discounted rate. Save ₹24 compared to monthly plan! Includes all premium features: AI tasks, romantic messages, event reminders, and gift suggestions. Best value for committed couples.
```

Click **"Continue"**

---

### 3.2 Set Base Plan

Click **"Add base plan"**

**Base plan ID:** `6month`

**Billing period:** 
- Select **"Custom"**
- Enter **"6 months"** (P6M)
- OR select **"26 weeks"** (P26W) - both work

**Grace period:** 
- Select **"3 days"** (recommended)

**Account hold:**
- Enable **"Yes"** (recommended)

**Resubscribe:**
- Enable **"Yes"**

**Auto-renewing:**
- Select **"Yes"**

Click **"Continue"**

---

### 3.3 Add Offer (Free Trial)

⚠️ **IMPORTANT:** Skip this section! Click **"No thanks"** or **"Skip"**

Click **"Continue"**

---

### 3.4 Set Pricing

1. Click **"Add price"**
2. Select **"India"** from country list
3. Enter price: **₹450.00**
4. Click **"Apply"**

**Optional:** Add other countries if needed

Click **"Continue"**

---

### 3.5 Review and Activate

1. Review all details:
   - ✅ Subscription ID: `pookie4u_6month_450`
   - ✅ Base plan: `6month`
   - ✅ Billing period: 6 months
   - ✅ Price: ₹450.00
   - ✅ Auto-renewing: Yes

2. Click **"Activate"**

**✅ 6-Month subscription product created!**

---

## STEP 4: Verify Both Products

Go back to **"Monetize" → "Subscriptions"**

You should see both products listed:
- ✅ `pookie4u_monthly_79` - Status: Active
- ✅ `pookie4u_6month_450` - Status: Active

---

## STEP 5: Connect Google Play to RevenueCat

### 5.1 Create Service Account

1. In Google Play Console, go to **"Setup" → "API access"**
2. Click **"Create new service account"**
3. Click the link to **Google Cloud Console** (opens in new tab)

**In Google Cloud Console:**
4. Click **"+ Create Service Account"**
5. **Service account name:** `RevenueCat`
6. **Service account ID:** (auto-filled) `revenuecat`
7. Click **"Create and Continue"**
8. **Select role:** Search for and select **"Pub/Sub Admin"**
9. Click **"Continue"**
10. Click **"Done"**

---

### 5.2 Create JSON Key

1. Find your newly created service account in the list
2. Click on the **email address** (looks like `revenuecat@your-project.iam.gserviceaccount.com`)
3. Go to **"Keys"** tab
4. Click **"Add Key" → "Create new key"**
5. Select **"JSON"** format
6. Click **"Create"**
7. **JSON file downloads automatically** - save it securely!

⚠️ **IMPORTANT:** Keep this JSON file safe - it's your credential!

---

### 5.3 Grant Permissions in Play Console

1. Return to Google Play Console → "Setup" → "API access"
2. Find your service account in the list
3. Click **"Grant access"** or **"Manage Play Console permissions"**
4. Under **"Financial data"**, check:
   - ✅ **View financial data, orders, and subscription details**
   - ✅ **Manage orders and subscriptions**
5. Under **"App information"**, check:
   - ✅ **View app information and download bulk reports**
6. Click **"Invite user"**
7. Click **"Send invitation"**

---

### 5.4 Upload JSON to RevenueCat

1. Go to RevenueCat dashboard: https://app.revenuecat.com/
2. Select your project **"POOKIE4U"**
3. Go to **"Project Settings"** (gear icon)
4. Click **"Service Credentials"** tab
5. Find **"Google Play Store"** section
6. Click **"Upload JSON"** or drag and drop your JSON file
7. Click **"Save"**

**✅ Google Play is now connected to RevenueCat!**

---

## STEP 6: Import Products to RevenueCat

### 6.1 Import Products

1. In RevenueCat dashboard, go to **"Products"** tab
2. Click **"+ Import from store"** or **"Add products"**
3. Select **"Google Play Store"**
4. You should see your products:
   - ☑️ `pookie4u_monthly_79`
   - ☑️ `pookie4u_6month_450`
5. **Select both checkboxes**
6. Click **"Import"** or **"Add products"**

**✅ Products imported successfully!**

---

### 6.2 Create Entitlement

1. Go to **"Entitlements"** tab
2. Click **"+ New entitlement"** or **"Create entitlement"**
3. **Identifier:** `premium_access`
4. **Display name:** `Premium Access`
5. **Description:** `Full access to all premium features`
6. Click **"Save"** or **"Create"**

---

### 6.3 Attach Products to Entitlement

1. Click on your **"premium_access"** entitlement
2. Click **"Attach products"** or **"+ Add product"**
3. Select both products:
   - ☑️ `pookie4u_monthly_79`
   - ☑️ `pookie4u_6month_450`
4. Click **"Attach"** or **"Save"**

**✅ Products attached to entitlement!**

---

## STEP 7: Create Offering

### 7.1 Create Default Offering

1. Go to **"Offerings"** tab
2. Click **"+ New offering"** or **"Create offering"**
3. **Identifier:** `default`
4. **Display name:** `Default Offering`
5. **Description:** `Standard subscription options for Pookie4u`
6. Click **"Create"**

---

### 7.2 Add Packages to Offering

Click on your **"default"** offering, then:

**Package 1: Monthly**
1. Click **"+ Add package"**
2. **Package identifier:** `monthly`
3. **Product:** Select `pookie4u_monthly_79`
4. **Package type:** Custom
5. Click **"Add"** or **"Save"**

**Package 2: 6-Month**
1. Click **"+ Add package"** again
2. **Package identifier:** `6_month`
3. **Product:** Select `pookie4u_6month_450`
4. **Package type:** Custom
5. Click **"Add"** or **"Save"**

---

### 7.3 Set as Current Offering

1. Find the toggle **"Current offering"** or **"Make current"**
2. Turn it **ON** ✅
3. Click **"Save"** if needed

**✅ Offering is now active!**

---

## STEP 8: Setup License Testing

### 8.1 Add Test Account

1. In Google Play Console, go to **"Setup" → "License testing"**
2. Under **"License testers"**, click **"Add license testers"**
3. Enter email addresses of test accounts (comma-separated):
   ```
   your-test-email@gmail.com
   ```
4. Click **"Save"**

### 8.2 Set Test Response

1. Under **"License test response"**, select:
   - **"RESPOND_NORMALLY"** (recommended)
   - This allows testing without actual charges

**✅ Test accounts configured!**

---

## ✅ Setup Complete Checklist

### Google Play Console:
- [ ] Monthly subscription created (`pookie4u_monthly_79`)
- [ ] 6-Month subscription created (`pookie4u_6month_450`)
- [ ] Both products activated
- [ ] Service account created
- [ ] JSON key downloaded
- [ ] Permissions granted to service account
- [ ] Test accounts added

### RevenueCat:
- [ ] JSON uploaded to RevenueCat
- [ ] Products imported
- [ ] Entitlement created (`premium_access`)
- [ ] Products attached to entitlement
- [ ] Offering created (`default`)
- [ ] Packages added to offering
- [ ] Offering set as current

---

## 🧪 Testing Your Setup

### Test in Development

Once everything is set up:

1. **Build development APK** (if not already done)
2. **Install on test device** signed in with test account
3. **Open your app**
4. **Navigate to subscription screen**
5. **Try selecting "Monthly" plan**
6. **Google Play payment sheet should open**
7. **Complete test purchase** (won't be charged in test mode)
8. **Verify "Subscription Activated" message**

### What Should Happen:

**Free Trial:**
- ✅ Activates instantly without payment
- ✅ No Google Play interaction
- ✅ Managed 100% by your backend

**Paid Plans:**
- ✅ Opens Google Play payment sheet
- ✅ Shows ₹79 or ₹450
- ✅ Allows UPI/Card/Net Banking selection
- ✅ Activates immediately after payment
- ✅ Shows in RevenueCat dashboard

---

## 🔧 Troubleshooting

### "Product not found" Error

**Cause:** Products not imported or offering not current

**Solution:**
1. Verify products show in RevenueCat "Products" tab
2. Verify offering is set as "current"
3. Wait 5-10 minutes for cache to clear
4. Restart app

### "Unable to purchase" Error

**Cause:** App not properly connected to Google Play

**Solution:**
1. Verify APK is uploaded to internal testing
2. Verify JSON credentials uploaded to RevenueCat
3. Verify service account has proper permissions
4. Check package name matches everywhere

### "Item unavailable in your country"

**Cause:** Price not set for user's country

**Solution:**
1. Go to Google Play Console → Subscriptions
2. Edit product → Pricing
3. Add user's country with price
4. Save and wait for sync

### Free Trial Shows Payment

**Cause:** Accidentally created trial in Google Play

**Solution:**
1. Edit subscription in Play Console
2. Remove trial offer
3. Free trial should only be via your backend!

---

## 📊 Monitor Your Subscriptions

### RevenueCat Dashboard

Access: https://app.revenuecat.com/

Monitor:
- **Active subscribers**
- **Revenue metrics**
- **Trial conversions**
- **Churn rates**
- **Subscription events**

### Google Play Console

Access: https://play.google.com/console/

Monitor:
- **Subscription retention**
- **Acquisition reports**
- **Revenue and subscriptions**
- **Cancellation insights**

---

## 🎉 You're All Set!

Once completed:
- ✅ Two subscription products active
- ✅ RevenueCat fully configured
- ✅ App ready for subscription testing
- ✅ Native UPI/Google Pay support enabled
- ✅ Free trial managed by backend

**Your users can now:**
1. Start 14-day free trial (no payment)
2. Subscribe monthly at ₹79
3. Subscribe for 6 months at ₹450
4. Pay via UPI, cards, or net banking
5. Manage subscriptions from Play Store

---

## 📞 Need Help?

- **RevenueCat Docs:** https://www.revenuecat.com/docs
- **Google Play Billing:** https://developer.android.com/google/play/billing
- **RevenueCat Community:** https://community.revenuecat.com
- **Play Console Support:** https://support.google.com/googleplay/android-developer

---

**Good luck with your subscription setup! 🚀**
