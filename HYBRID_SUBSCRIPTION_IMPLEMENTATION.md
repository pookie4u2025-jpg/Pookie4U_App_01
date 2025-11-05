# Hybrid Subscription Implementation Plan

## Overview

This implementation combines:
- **Backend-Managed Free Trial**: 14 days, no payment required
- **Google Play Billing**: For paid subscriptions (₹79/month and ₹450/6-month)

## User Flows

### Flow 1: Free Trial → Paid Subscription

1. User taps "14 Days Free Trial" → Backend activates trial immediately (no payment)
2. User gets premium access for 14 days
3. After 14 days, app shows "Trial expired, select a plan"
4. User selects ₹79/month or ₹450/6-month → Google Play payment sheet opens
5. User completes payment → Subscription activated

### Flow 2: Direct Paid Subscription

1. User taps "₹79/month" or "₹450/6-month"
2. Google Play payment sheet opens immediately
3. User selects payment method (UPI/Cards/Net Banking)
4. Payment confirmed → Subscription activated instantly

## Implementation Steps

### Phase 1: Backend Trial Management
- Update subscription endpoints to handle backend trials
- Add trial eligibility checking (one-time per user)
- Create trial activation endpoint (no payment required)
- Add trial expiration checking logic

### Phase 2: Google Play Integration (Paid Plans Only)
- Install RevenueCat SDK
- Configure only 2 products in Google Play (monthly & 6-month)
- Remove trial product from Google Play Console
- Update frontend to use RevenueCat for paid plans only

### Phase 3: Frontend Implementation
- Show 3 options: Trial (backend), Monthly (Google Play), 6-Month (Google Play)
- Handle trial activation via backend API
- Handle paid subscriptions via RevenueCat
- Show trial expiration screen with paid plan options

### Phase 4: Testing
- Test trial activation (no payment)
- Test trial expiration → paid subscription flow
- Test direct paid subscription purchases
- Test subscription renewals

## Technical Architecture

```
┌─────────────────────────────────────────┐
│         Frontend (React Native)         │
│  - Shows 3 subscription options         │
│  - Handles trial via Backend API        │
│  - Handles paid via RevenueCat          │
└─────────────────────────────────────────┘
              │              │
              │              │
        Trial │              │ Paid Plans
              ▼              ▼
    ┌──────────────┐  ┌──────────────┐
    │   Backend    │  │  RevenueCat  │
    │   FastAPI    │  │  + Google    │
    │   MongoDB    │  │  Play Store  │
    └──────────────┘  └──────────────┘
```

## Benefits

✅ True no-payment-method trial (no Google account billing required)
✅ Seamless Google Play payments for paid subscriptions
✅ Full control over trial eligibility and enforcement
✅ Native UPI support via Google Play
✅ Automatic subscription renewal via Google Play
✅ Clean separation of free vs paid flows

## Next Steps

1. Update backend trial endpoints
2. Create Google Play products (2 only: monthly & 6-month)
3. Implement frontend subscription screen
4. Test complete flows
