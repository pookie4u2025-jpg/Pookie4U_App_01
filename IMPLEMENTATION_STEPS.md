# Hybrid Subscription - Implementation Steps

## Step 1: Install RevenueCat SDK

```bash
cd /app/frontend
npx expo install react-native-purchases
```

## Step 2: Update app.json

Add the following to your `app.json`:

```json
{
  "expo": {
    "android": {
      "permissions": [
        "com.android.vending.BILLING"
      ]
    }
  }
}
```

## Step 3: Add Environment Variable

Add to `/app/frontend/.env`:

```bash
# RevenueCat Configuration (add this when you have the API key)
EXPO_PUBLIC_REVENUECAT_GOOGLE_API_KEY=
```

## Step 4: Google Play Console Setup

### Create ONLY 2 Products (NOT 3):

1. **Monthly Plan**
   - Subscription ID: `pookie4u_monthly_79`
   - Price: ₹79/month
   - Auto-renewable

2. **6-Month Plan**
   - Subscription ID: `pookie4u_6month_450`
   - Price: ₹450/6 months
   - Auto-renewable

**DO NOT create a trial product in Google Play** - we handle trials via backend!

## Step 5: RevenueCat Setup

1. Create RevenueCat account at revenuecat.com
2. Create project "Pookie4u"
3. Connect Google Play Console
4. Import the 2 products (monthly & 6-month)
5. Create entitlement "premium_access"
6. Attach both products to the entitlement
7. Create offering "default_offering" with 2 packages:
   - Package ID: `monthly`
   - Package ID: `6_month`

## Step 6: Backend - No Changes Needed!

Your backend already has:
- ✅ `/api/subscription/start-trial` - Working
- ✅ `/api/subscription/status` - Working
- ✅ Trial enforcement logic - Working

## Step 7: Update Frontend Files

I'll update the following files:
1. `/app/frontend/app/subscription.tsx` - Hybrid subscription screen
2. `/app/frontend/src/config/revenuecatConfig.ts` - Already created
3. `/app/frontend/app/_layout.tsx` - Initialize RevenueCat

## Step 8: Build Development APK

```bash
cd /app/frontend
eas build -p android --profile development
```

## Step 9: Testing

1. Install development APK on test device
2. Test free trial activation (no payment)
3. Wait for trial to expire or manually set expiration in database
4. Test paid subscription flow via Google Play

## Implementation Summary

### What We're Doing:

**Free Trial (Backend-Managed)**
- User clicks "14 Days Free Trial"
- Backend activates trial immediately
- No payment method required
- One-time per user (enforced by backend)

**Paid Plans (Google Play + RevenueCat)**
- User clicks "₹79/month" or "₹450/6-month"
- RevenueCat opens Google Play payment sheet
- User selects UPI/Card/Net Banking
- Payment processed by Google Play
- Subscription activated via RevenueCat webhook

### Files Updated:

1. ✅ RevenueCat config created
2. ⏳ Subscription screen (next)
3. ⏳ App layout initialization (next)
4. ⏳ Backend webhook handler (optional, for later)

## Next Steps

Ready to proceed with updating the subscription screen?
