# RevenueCat + Google Play Billing Setup Guide

## Quick Start Summary

This guide provides step-by-step instructions for setting up RevenueCat with Google Play Billing for the Pookie4u mobile app.

## Prerequisites

✅ **You Have:**
- Google Play Console developer account
- Existing Expo React Native app
- FastAPI backend + MongoDB

✅ **You Need:**
- RevenueCat account (free - create at revenuecat.com)
- ~2-3 hours for complete setup

## Subscription Plans to Implement

| Plan | Duration | Price | Type |
|------|----------|-------|------|
| Free Trial | 14 days | ₹0 | One-time only |
| Monthly | 1 month | ₹79 | Auto-renewable |
| 6-Month | 6 months | ₹450 | Auto-renewable |

---

## Phase 1: Account Setup (30 minutes)

### Step 1: Create RevenueCat Account
1. Go to https://www.revenuecat.com/
2. Sign up for free account
3. Create new project called "Pookie4u"
4. Select your region
5. **Save your API keys** (you'll need them later)

### Step 2: Build & Upload to Google Play
```bash
# Create a signed APK
cd /app/frontend
eas build -p android --profile development
```

1. Download the APK after build completes
2. Log into Google Play Console
3. Navigate to your app → "Release" → "Internal testing"
4. Click "Create new release"
5. Upload the APK
6. This enables billing for your app

---

## Phase 2: Google Play Console Configuration (45 minutes)

### Create Subscription Products

#### Product 1: Free Trial
- **Subscription ID**: `pookie4u_trial_14d`
- **Title**: "14 Day Free Trial"
- **Description**: "Get full access to Pookie4u for 14 days with no charge"
- **Base Plan ID**: `trial_14d_baseline`
- **Billing period**: Custom (14 days)
- **Price**: ₹0
- **Renewal**: Auto-renewing
- **Status**: Active

#### Product 2: Monthly
- **Subscription ID**: `pookie4u_monthly_79`
- **Title**: "Monthly Premium"
- **Description**: "Monthly access to all premium features"
- **Base Plan ID**: `monthly_baseline`
- **Billing period**: Monthly (1 month)
- **Price**: ₹79
- **Renewal**: Auto-renewing
- **Status**: Active

#### Product 3: 6-Month
- **Subscription ID**: `pookie4u_6month_450`
- **Title**: "6-Month Premium"
- **Description**: "Six months of premium features at a discounted rate"
- **Base Plan ID**: `6month_baseline`
- **Billing period**: Custom (6 months / 26 weeks)
- **Price**: ₹450
- **Renewal**: Auto-renewing
- **Status**: Active

### Connect Google Play to RevenueCat

1. In Google Play Console, go to "Setup" → "API access"
2. Create a service account and download JSON key
3. In RevenueCat dashboard, go to "Project Settings" → "Service Credentials"
4. Upload the Google Play JSON key file
5. RevenueCat will now be able to access your products

### Import Products into RevenueCat

1. In RevenueCat, go to "Product Catalog" → "Products"
2. Click "+ New" → "Import Products"
3. Select all three subscription products
4. Click "Import"

### Create Entitlement

1. Go to "Product Catalog" → "Entitlements"
2. Click "+ New entitlement"
3. Name: `premium_access`
4. Description: "Full access to all premium features"
5. Click "Create"
6. Attach all three products to this entitlement

### Create Offering

1. Go to "Product Catalog" → "Offerings"
2. Click "+ New"
3. Identifier: `default_offering`
4. Description: "Our standard subscription options"
5. Add packages:
   - Package 1: Identifier `trial_14d`, Product: trial
   - Package 2: Identifier `monthly`, Product: monthly
   - Package 3: Identifier `6_month`, Product: 6-month
6. Save offering

---

## Phase 3: Frontend Implementation (1 hour)

### Install Dependencies

```bash
cd /app/frontend
npx expo install react-native-purchases react-native-purchases-ui expo-dev-client
```

### Update app.json

Add RevenueCat plugin to your `app.json`:

```json
{
  "expo": {
    "plugins": [
      [
        "react-native-purchases",
        {
          "api_key": "YOUR_REVENUECAT_API_KEY_HERE"
        }
      ]
    ],
    "android": {
      "permissions": [
        "com.android.vending.BILLING"
      ]
    }
  }
}
```

### Create RevenueCat Configuration

File: `/app/frontend/src/config/revenuecatConfig.ts`

```typescript
import Purchases, { LOG_LEVEL } from 'react-native-purchases';
import { Platform } from 'react-native';

export const initializeRevenueCat = async () => {
  try {
    Purchases.setLogLevel(LOG_LEVEL.VERBOSE);

    if (Platform.OS === 'android') {
      await Purchases.configure({
        apiKey: process.env.EXPO_PUBLIC_REVENUECAT_GOOGLE_API_KEY!,
      });
    }

    console.log('RevenueCat initialized successfully');
  } catch (error) {
    console.error('Error initializing RevenueCat:', error);
  }
};
```

### Create Subscription Store

File: `/app/frontend/src/stores/useRevenueCatStore.ts`

```typescript
import { create } from 'zustand';
import Purchases, { CustomerInfo } from 'react-native-purchases';

interface RevenueCatStore {
  customerInfo: CustomerInfo | null;
  isLoading: boolean;
  hasPremiumAccess: boolean;
  
  fetchCustomerInfo: () => Promise<void>;
  checkPremiumAccess: () => boolean;
}

export const useRevenueCatStore = create<RevenueCatStore>((set, get) => ({
  customerInfo: null,
  isLoading: false,
  hasPremiumAccess: false,

  fetchCustomerInfo: async () => {
    set({ isLoading: true });
    try {
      const customerInfo = await Purchases.getCustomerInfo();
      const hasPremium = typeof customerInfo.entitlements.active['premium_access'] !== 'undefined';
      set({ customerInfo, hasPremiumAccess: hasPremium, isLoading: false });
    } catch (error) {
      set({ isLoading: false });
    }
  },

  checkPremiumAccess: () => {
    const { customerInfo } = get();
    if (!customerInfo) return false;
    return typeof customerInfo.entitlements.active['premium_access'] !== 'undefined';
  },
}));
```

### Update Your Subscription Screen

Replace the current subscription.tsx with RevenueCat implementation:

```typescript
// File: /app/frontend/app/subscription.tsx
import React, { useEffect, useState } from 'react';
import { View, Text, TouchableOpacity, Alert } from 'react-native';
import Purchases, { Package } from 'react-native-purchases';

export default function SubscriptionScreen() {
  const [packages, setPackages] = useState<Package[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchOfferings();
  }, []);

  const fetchOfferings = async () => {
    try {
      const offerings = await Purchases.getOfferings();
      if (offerings.current) {
        setPackages(offerings.current.availablePackages);
      }
    } catch (error) {
      console.error('Error fetching offerings:', error);
    }
  };

  const handlePurchase = async (pkg: Package) => {
    try {
      setLoading(true);
      const { customerInfo } = await Purchases.purchasePackage(pkg);
      
      if (typeof customerInfo.entitlements.active['premium_access'] !== 'undefined') {
        Alert.alert('Success', 'Subscription activated!');
      }
    } catch (error) {
      Alert.alert('Error', 'Purchase failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <View>
      {packages.map((pkg) => (
        <TouchableOpacity
          key={pkg.identifier}
          onPress={() => handlePurchase(pkg)}
        >
          <Text>{pkg.product.title}</Text>
          <Text>{pkg.product.priceString}</Text>
        </TouchableOpacity>
      ))}
    </View>
  );
}
```

### Initialize RevenueCat on App Start

Update your app entry point to initialize RevenueCat:

```typescript
// File: /app/frontend/app/_layout.tsx
import { useEffect } from 'react';
import { initializeRevenueCat } from '../src/config/revenuecatConfig';

export default function RootLayout() {
  useEffect(() => {
    initializeRevenueCat();
  }, []);

  // Rest of your layout code
}
```

---

## Phase 4: Backend Integration (45 minutes)

### Create Webhook Handler

File: `/app/backend/webhooks.py`

```python
from fastapi import FastAPI, Request, HTTPException, Header
import hmac
import hashlib
import json
from datetime import datetime
from typing import Optional

REVENUECAT_WEBHOOK_SECRET = "your_webhook_secret"

app = FastAPI()

@app.post("/api/webhooks/revenuecat")
async def receive_revenuecat_webhook(
    request: Request,
    x_revenuecat_signature: Optional[str] = Header(None)
):
    body = await request.body()
    
    # Verify signature
    if not verify_webhook_signature(body, x_revenuecat_signature):
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    payload = json.loads(body)
    event_type = payload.get('event', {}).get('type')
    app_user_id = payload.get('event', {}).get('app_user_id')
    
    if event_type == "INITIAL_PURCHASE":
        await handle_initial_purchase(payload)
    elif event_type == "RENEWAL":
        await handle_renewal(payload)
    elif event_type == "CANCELLATION":
        await handle_cancellation(payload)
    
    return {"status": "ok"}

def verify_webhook_signature(body: bytes, signature: Optional[str]) -> bool:
    if not signature:
        return False
    
    expected = hmac.new(
        REVENUECAT_WEBHOOK_SECRET.encode(),
        body,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected)

async def handle_initial_purchase(payload: dict):
    event = payload['event']
    user_id = event['app_user_id']
    product_id = event['product_id']
    expires_at = datetime.fromtimestamp(event['expiration_at_ms'] / 1000)
    
    # Update MongoDB
    await db.users.update_one(
        {"revenue_cat_id": user_id},
        {
            "$set": {
                "subscription_status": {
                    "is_active": True,
                    "plan_type": get_plan_type(product_id),
                    "expires_at": expires_at,
                    "auto_renews": True,
                }
            }
        }
    )

def get_plan_type(product_id: str) -> str:
    mapping = {
        "pookie4u_trial_14d": "trial",
        "pookie4u_monthly_79": "monthly",
        "pookie4u_6month_450": "6_month",
    }
    return mapping.get(product_id, "unknown")
```

### Configure Webhook in RevenueCat

1. Log into RevenueCat dashboard
2. Go to "Integrations" → "Webhooks"
3. Click "Add new configuration"
4. **Webhook URL**: `https://your-api-domain.com/api/webhooks/revenuecat`
5. **Authorization Header**: Create a secure random token
6. Save the token as `REVENUECAT_WEBHOOK_SECRET` in your backend .env
7. Click "Save"

### Add Environment Variables

File: `/app/backend/.env`

```bash
# RevenueCat Configuration
REVENUECAT_WEBHOOK_SECRET=your_secure_webhook_secret_here
REVENUECAT_API_KEY=your_private_api_key_here
```

File: `/app/frontend/.env`

```bash
# RevenueCat Configuration
EXPO_PUBLIC_REVENUECAT_GOOGLE_API_KEY=goog_your_public_google_api_key
```

---

## Phase 5: Testing (30 minutes)

### Set Up Test User

1. In Google Play Console, go to "Setup" → "License testing"
2. Add your test email address
3. Sign in to your Android device with this email

### Test Purchase Flow

1. Build and install development APK on test device
2. Open app and navigate to subscription screen
3. Tap on Free Trial option
4. Complete test purchase
5. Verify "Premium access granted" message
6. Check backend logs for webhook events

### Test Cancellation

1. In Google Play Store app on device
2. Go to "Manage subscriptions"
3. Find Pookie4u subscription
4. Cancel subscription
5. Verify webhook received in backend
6. Verify app still shows premium until expiration

---

## Deployment Checklist

Before going to production:

- [ ] All three products created in Google Play Console
- [ ] Products imported into RevenueCat
- [ ] Entitlement created and products attached
- [ ] Offering created with all packages
- [ ] Webhook configured with secure secret
- [ ] Production API keys added to .env files
- [ ] Backend deployed and publicly accessible via HTTPS
- [ ] Tested all purchase scenarios in sandbox
- [ ] Tested webhook events in sandbox
- [ ] MongoDB indexes created on `revenue_cat_id` field

---

## Important Notes

⚠️ **Security:**
- Never commit API keys to git
- Always verify webhook signatures
- Use HTTPS for all webhook endpoints

⚠️ **Testing:**
- Google Play sandbox subscriptions renew much faster (monthly = 5 minutes)
- Use test accounts for all development testing
- Test trial period enforcement

⚠️ **Trial Enforcement:**
- Track trial usage per user ID in MongoDB
- One trial per user ID (not per device)
- Check trial status before showing trial option

---

## Next Steps

1. **Create RevenueCat account** → Get API keys
2. **Build & upload APK** → Enable billing
3. **Create products** → Google Play Console
4. **Import products** → RevenueCat
5. **Install SDK** → Frontend
6. **Setup webhooks** → Backend
7. **Test thoroughly** → Sandbox environment
8. **Deploy** → Production

---

## Support Resources

- RevenueCat Docs: https://www.revenuecat.com/docs
- Google Play Billing: https://developer.android.com/google/play/billing
- RevenueCat Community: https://community.revenuecat.com

---

**Need Help?**
If you encounter issues, check the comprehensive playbook in the files I provided with detailed code examples and troubleshooting steps.
