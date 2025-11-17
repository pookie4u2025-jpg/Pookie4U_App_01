# Complete Google Play + RevenueCat Setup Guide for Auto-Renewal Subscriptions

## Phase 5: Auto-Renew Subscription Configuration

This guide will walk you through setting up auto-renewing subscriptions for Pookie4u using RevenueCat and Google Play Console.

---

## Prerequisites
- ✅ Google Play Console Developer Account ($25 one-time fee)
- ✅ RevenueCat Account (Free tier available)
- ✅ App Bundle (.aab) ready for upload
- ✅ Bank account for payouts

---

## Part 1: Google Play Console Setup

### Step 1: Create Subscription Products

1. **Navigate to Monetization**
   - Open [Google Play Console](https://play.google.com/console)
   - Select your app "Pookie4u"
   - Go to: **Monetize → Products → Subscriptions**

2. **Create Monthly Subscription**
   ```
   Product ID: pookie4u_monthly
   Name: Pookie4u Premium - Monthly
   Description: Monthly subscription to Pookie4u Premium features
   
   Base Plan:
   - Plan ID: monthly-base
   - Billing Period: 1 month
   - Price: ₹79 INR
   - Auto-renewing: YES ✓
   - Free Trial: 14 days
   ```

3. **Create Half-Yearly Subscription**
   ```
   Product ID: pookie4u_half_yearly
   Name: Pookie4u Premium - 6 Months
   Description: 6-month subscription to Pookie4u Premium (Save 25%)
   
   Base Plan:
   - Plan ID: half-yearly-base
   - Billing Period: 6 months
   - Price: ₹450 INR
   - Auto-renewing: YES ✓
   - Free Trial: 14 days
   ```

4. **Configure Free Trial (Important!)**
   - Both subscriptions should have the same 14-day trial
   - Trial period: **14 days**
   - Trial is **FREE** (₹0)
   - User is charged after trial ends if not cancelled
   - **Auto-renewal is enabled by default** ✓

5. **Set Subscription Features**
   For both subscriptions, add:
   - AI-generated daily tasks
   - Personalized romantic messages
   - Smart gift recommendations
   - Date planning assistance
   - Unlimited event reminders
   - Priority customer support

### Step 2: Configure Subscription Settings

1. **Grace Period** (Recommended)
   - Navigate to: **Subscription settings → Grace period**
   - Enable 3-day grace period
   - Allows users to fix payment issues without losing access

2. **Account Hold** (Recommended)
   - Enable account hold for 30 days
   - Preserves subscription status during payment failures

3. **Resubscribe** (Recommended)
   - Allow users to resubscribe with same benefits
   - Preserve user data for 90 days after cancellation

### Step 3: Set Up License Testing

1. **Add Test Accounts**
   - Go to: **Setup → License testing**
   - Add your Gmail accounts for testing
   - Test purchases will be free and immediate

2. **Enable Test Tracks**
   - Create "Internal Testing" track
   - Upload your app bundle
   - Add testers to verify subscription flow

---

## Part 2: RevenueCat Setup

### Step 1: Create RevenueCat Project

1. **Sign Up/Login**
   - Go to [RevenueCat Dashboard](https://app.revenuecat.com)
   - Create new project: "Pookie4u"

2. **Add Android App**
   - Click "Add App"
   - Platform: Android
   - Package Name: `com.pookie4u.app` (match your app.json)

### Step 2: Connect Google Play

1. **Create Service Account**
   In Google Cloud Console:
   ```
   1. Go to: https://console.cloud.google.com
   2. Create new project or select existing
   3. Enable "Google Play Android Developer API"
   4. Create Service Account:
      - Name: RevenueCat Service Account
      - Role: Service Account User
   5. Create JSON key → Download it
   ```

2. **Grant Permissions in Play Console**
   ```
   1. Go to Play Console → Setup → API access
   2. Link to Google Cloud project
   3. Find your service account
   4. Grant permissions:
      ✓ View financial data
      ✓ Manage orders and subscriptions
   ```

3. **Upload to RevenueCat**
   - RevenueCat Dashboard → App Settings → Google Play
   - Upload service account JSON key
   - Click "Save"

### Step 3: Create Products in RevenueCat

1. **Add Subscription Products**
   - Go to: **Products** section
   - Click "Add Product"

   **Monthly Subscription:**
   ```
   Identifier: pookie4u_monthly
   Type: Subscription
   Google Play Product ID: pookie4u_monthly
   ```

   **Half-Yearly Subscription:**
   ```
   Identifier: pookie4u_half_yearly
   Type: Subscription
   Google Play Product ID: pookie4u_half_yearly
   ```

2. **Create Offering (Package)**
   - Go to: **Offerings** section
   - Create "default" offering
   - Add packages:
     - Monthly: `$rc_monthly` → pookie4u_monthly
     - Half-Yearly: `$rc_half_yearly` → pookie4u_half_yearly
   - Set Half-Yearly as "Default" (recommended option)

### Step 4: Configure Webhooks (Optional but Recommended)

1. **Set Up Webhook Endpoint**
   - Your backend endpoint: `https://your-domain.com/api/revenuecat/webhook`
   - RevenueCat will send subscription events here

2. **Add Webhook URL in RevenueCat**
   - Dashboard → Integrations → Webhooks
   - Add your endpoint URL
   - RevenueCat will notify you of:
     - Initial purchases
     - Renewals
     - Cancellations
     - Billing issues

---

## Part 3: Frontend Integration (Already Done ✓)

Your app already has RevenueCat integrated! The configuration is in:

```javascript
// frontend/app/subscription.tsx
const apiKey = process.env.EXPO_PUBLIC_REVENUECAT_GOOGLE_API_KEY;
await Purchases.configure({ apiKey });
```

**What's Already Working:**
- ✅ RevenueCat SDK initialized
- ✅ Subscription screen UI ready
- ✅ Package display (Monthly ₹79, Half-Yearly ₹450)
- ✅ Trial information shown
- ✅ Purchase flow integrated

**You Need To:**
1. Update `.env` file with RevenueCat API key:
   ```
   EXPO_PUBLIC_REVENUECAT_GOOGLE_API_KEY=your_key_here
   ```

---

## Part 4: Testing Auto-Renewal Flow

### Test Scenario 1: Free Trial Signup
1. **User signs up with Google**
2. **Completes onboarding**
3. **Selects "Monthly - ₹79/month" or "6 Months - ₹450"**
4. **Confirms subscription**
5. **Google shows: "Free for 14 days, then ₹79/month"**
6. **Result:** Trial starts, no charge

### Test Scenario 2: Trial Expiry
1. **Wait 12 days** (or use Google Play test mode)
2. **User receives notification:** "Trial expires in 2 days"
3. **Day 14:** If not cancelled, **auto-renewal triggers**
4. **Google charges ₹79 (or ₹450)**
5. **Subscription status: Active**

### Test Scenario 3: Monthly Renewal
1. **After first payment**
2. **Wait 30 days**
3. **Auto-renewal triggers on day 30**
4. **Google charges ₹79**
5. **Subscription continues**

### Test Scenario 4: Cancellation
1. **User cancels in Google Play**
2. **Access continues until period ends**
3. **No future charges**
4. **Can resubscribe anytime**

---

## Part 5: Monitoring & Analytics

### RevenueCat Dashboard
- **Charts → Overview**
  - Active subscriptions count
  - Monthly Recurring Revenue (MRR)
  - Churn rate
  - Trial conversion rate

### Google Play Console
- **Monetization → Dashboard**
  - Subscription revenue
  - Active subscribers
  - Cancellation rate
  - Retention cohorts

---

## Part 6: Important Auto-Renewal Settings

### ✅ Ensure These Are Enabled:

1. **Auto-Renewing Subscription**: ON
   - Location: Play Console → Subscription → Base Plan
   - This is THE critical setting for auto-renewal

2. **Grace Period**: 3 days (Recommended)
   - Gives users time to fix payment issues
   - Prevents immediate cancellation

3. **Account Hold**: 30 days (Recommended)
   - Suspends access but preserves subscription
   - Better retention than immediate cancel

4. **Resubscribe**: Enabled
   - Allows users to come back easily
   - Preserves historical data

5. **Notifications to Users**:
   - Google sends these automatically:
     - Trial starting
     - Trial ending (2 days before)
     - Payment successful
     - Payment failed
     - Subscription renewed

---

## Part 7: Subscription Lifecycle

```
User Flow:
┌─────────────┐
│ Sign Up     │
│ (Google)    │
└──────┬──────┘
       │
       v
┌──────────────────┐
│ Choose Plan      │
│ • Monthly ₹79    │
│ • 6-Month ₹450   │
└──────┬───────────┘
       │
       v
┌──────────────────────┐
│ Start Free Trial     │
│ (14 days - ₹0)       │
└──────┬───────────────┘
       │
       v
┌──────────────────────┐
│ Day 12: Notification │
│ "Trial ends in 2 days"│
└──────┬───────────────┘
       │
   ┌───┴───┐
   │       │
   v       v
Cancel   Continue
   │       │
   │       v
   │   ┌─────────────┐
   │   │ Day 14:     │
   │   │ Auto-Charge │
   │   │ ₹79/₹450    │
   │   └──────┬──────┘
   │          │
   │          v
   │   ┌─────────────────┐
   │   │ Monthly Renewal │
   │   │ Auto-Charge     │
   │   │ Every 30 days   │
   │   └─────────────────┘
   │
   v
┌──────────────────┐
│ Trial Ends       │
│ No Charge        │
│ Can Resubscribe  │
└──────────────────┘
```

---

## Part 8: Troubleshooting

### Issue: Auto-Renewal Not Working
**Solution:**
1. Verify base plan has "Auto-renewing: YES"
2. Check subscription is "Active" not "Paused"
3. Ensure payment method is valid
4. Verify RevenueCat is receiving events

### Issue: Trial Not Showing
**Solution:**
1. In Play Console, verify trial period = 14 days
2. Check eligibility rules (one trial per user)
3. Test with new Google account

### Issue: RevenueCat Not Syncing
**Solution:**
1. Verify service account permissions
2. Check API is enabled in Cloud Console
3. Reupload service account JSON key
4. Wait 24 hours for initial sync

---

## Part 9: Production Checklist

Before launching:
- [ ] Subscriptions created in Play Console
- [ ] Auto-renewal ENABLED on both products
- [ ] Free trial configured (14 days)
- [ ] Prices set correctly (₹79, ₹450)
- [ ] RevenueCat connected to Play Console
- [ ] Products added to RevenueCat
- [ ] Offering created with packages
- [ ] RevenueCat API key added to frontend `.env`
- [ ] Tested trial signup flow
- [ ] Tested auto-renewal (Play Console test mode)
- [ ] Verified notifications are sent
- [ ] Webhooks configured (optional)
- [ ] Analytics tracking working
- [ ] Bank account for payouts linked

---

## Part 10: Revenue Projections

### Conservative Estimates (First 3 Months):

| Metric | Month 1 | Month 2 | Month 3 |
|--------|---------|---------|---------|
| **Downloads** | 1,000 | 2,500 | 5,000 |
| **Trial Starts** | 150 (15%) | 375 (15%) | 750 (15%) |
| **Conversions** | 30 (20%) | 75 (20%) | 150 (20%) |
| **Monthly Revenue** | ₹2,370 | ₹5,925 | ₹11,850 |
| **Yearly Run Rate** | ₹28,440 | ₹71,100 | ₹142,200 |

---

## Support & Resources

- **RevenueCat Docs**: https://docs.revenuecat.com
- **Google Play Subscriptions**: https://support.google.com/googleplay/android-developer/answer/140504
- **RevenueCat Community**: https://community.revenuecat.com
- **Google Play Support**: https://support.google.com/googleplay/android-developer

---

**Status**: Phase 5 Implementation Complete
**Next**: Phase 6 - Final Testing & Deployment
