# User Experience Flow - Complete Implementation Plan

## Overview
Implementation of 6 key features to create a seamless, production-ready user experience for the Pookie4u app.

---

## 🎯 Requirements

### 1. Prevent Duplicate Google Accounts
**Goal:** One Google account = One Pookie4u account
**Implementation:** Check google_id on signup

### 2. Remember User Data
**Goal:** Never ask twice for the same information
**Implementation:** Store & retrieve from MongoDB + AsyncStorage

### 3. Skip Onboarding for Existing Users
**Goal:** Returning users go straight to home
**Implementation:** Check profile_completed flag

### 4. Full Onboarding for New Users
**Goal:** Complete profile setup + subscription selection
**Implementation:** Multi-step onboarding flow

### 5. Free Trial Expiry Notification
**Goal:** Warn 2 days before trial ends
**Implementation:** Scheduled notification check

### 6. Auto-Renew Subscription
**Goal:** Seamless subscription renewal
**Implementation:** RevenueCat + Google Play default settings

---

## 📊 Implementation Status

### ✅ Already Implemented:

**1. Google ID Storage:**
- ✅ google_id saved in database
- ✅ Prevents duplicate linking
- ✅ Stored in oauth_providers.google.google_id

**2. User Data Storage:**
- ✅ All user details in MongoDB
- ✅ Partner profile saved
- ✅ Cached in AsyncStorage
- ✅ Auto-restored on login

**3. Profile Completion Flag:**
- ✅ profile_completed field exists
- ✅ Set to true after profile setup
- ✅ Returned in user object

---

## 🔧 What Needs to Be Added:

### Feature 1: Enhanced Duplicate Prevention ⏳

**Current State:**
- Prevents linking same Google to different accounts
- BUT: Doesn't check on initial signup

**What to Add:**
```python
# On Google OAuth login
1. Extract google_id from Google token
2. Check: Does user with this google_id already exist?
   - YES → Login to existing account
   - NO → Create new account
3. Return appropriate response
```

**Impact:** Prevents accidental duplicate accounts

---

### Feature 2: User Data Restoration ✅ COMPLETE

**Current State:**
- All data saved to MongoDB
- AsyncStorage caches data
- Auto-loads on app restart

**Already Working:**
- Name, email, mobile
- Partner details
- Profile picture (Google avatar)
- Points, level, streaks
- Subscription status

**No changes needed!**

---

### Feature 3: Smart Onboarding Flow ⏳

**Current State:**
- profile_completed flag exists
- Not used for routing decisions

**What to Add:**

**Frontend Flow:**
```
User logs in
  ↓
Check: profile_completed?
  ├─ YES → Navigate to Home
  └─ NO → Navigate to Onboarding
```

**Onboarding Steps:**
1. Welcome screen
2. Partner name
3. Partner birthday
4. Anniversary date
5. Relationship mode
6. Subscription selection
7. → Mark profile_completed = true
8. → Navigate to Home

---

### Feature 4: Subscription Selection in Onboarding ⏳

**Current State:**
- Subscription screen exists
- Not integrated into onboarding

**What to Add:**
- Make subscription selection mandatory for new users
- After profile setup → Show subscription options
- User MUST choose one of 3 plans before accessing app

---

### Feature 5: Trial Expiry Notification ⏳

**Requirement:** Notify 2 days before free trial ends

**Implementation Strategy:**

**Option A: Backend Scheduled Job (Recommended)**
```python
# Daily cron job
1. Find all users with:
   - subscription_type = "free_trial"
   - days_remaining = 2
2. Send push notification
3. Log notification sent
```

**Option B: Frontend Local Notification**
```typescript
// On app launch
1. Check subscription status
2. Calculate days remaining
3. If days_remaining <= 2:
   - Show in-app notification
   - Schedule local push notification
```

**Option C: Hybrid**
- Backend sends push notification
- Frontend shows in-app banner
- Email reminder (optional)

---

### Feature 6: Auto-Renew Subscription ✅ MOSTLY COMPLETE

**Current State:**
- RevenueCat SDK integrated
- Google Play Billing configured

**How Auto-Renew Works:**

**Google Play (Default):**
- All subscriptions auto-renew by default
- User must manually cancel
- Handled by Google, not our app

**RevenueCat:**
- Tracks subscription status
- Notifies app of renewals
- Webhooks for status changes

**What to Verify:**
- Google Play Console subscriptions set to auto-renew (default)
- RevenueCat webhook configured (optional)
- App checks subscription status regularly

**Status:** Already working by default!

---

## 📋 Detailed User Flows

### Flow 1: New User (First Time)

```
1. User opens app
   ↓
2. Clicks "Continue with Google"
   ↓
3. Google OAuth popup
   ↓
4. Backend checks: google_id exists?
   - NO → New user
   ↓
5. Backend creates user:
   - email, name, google_id
   - profile_completed = FALSE
   ↓
6. Frontend receives: profile_completed = false
   ↓
7. Navigate to Onboarding Flow:
   
   Step 1: "Let's set up your profile"
   Step 2: "What's your partner's name?" [Input]
   Step 3: "Partner's birthday?" [Date Picker]
   Step 4: "Your anniversary?" [Date Picker]
   Step 5: "Relationship mode?" [Dropdown]
   
   Step 6: "Choose your plan"
   ├─ 14-day Free Trial (highlighted)
   ├─ Monthly ($4.99/month)
   └─ 6-Month ($24.99/6 months)
   
   [User selects plan]
   ↓
8. Backend updates:
   - partner_profile = {...}
   - profile_completed = TRUE
   - subscription_type = chosen plan
   ↓
9. Navigate to Home
   ↓
10. ✅ User ready to use app!
```

---

### Flow 2: Returning User

```
1. User opens app
   ↓
2. AsyncStorage has session_token
   ↓
3. Backend validates session
   ↓
4. Returns user data:
   - profile_completed = TRUE
   - partner_profile = {...}
   - subscription_status = active
   ↓
5. Frontend checks: profile_completed?
   - YES → Navigate directly to Home
   ↓
6. ✅ User sees home page immediately!
   (No questions asked)
```

---

### Flow 3: Duplicate Google Account Attempt

```
1. User A logs in with john@gmail.com (Google)
   ↓
2. Account created with google_id = "123456"
   ↓
3. User A logs out
   ↓
4. User A tries to create "new" account
   ↓
5. Clicks "Continue with Google"
   ↓
6. Selects john@gmail.com again
   ↓
7. Backend checks: google_id "123456" exists?
   - YES → Existing user found
   ↓
8. Backend logs in to existing account
   ↓
9. Frontend shows: "Welcome back!"
   ↓
10. Navigate to Home with existing data
   ↓
11. ✅ No duplicate account created!
```

---

### Flow 4: Free Trial Expiry Notification

```
Day 1: User starts 14-day free trial
   ↓
Day 12: 2 days before expiry
   ↓
Backend Cron Job:
   - Checks users with subscription_end_date = today + 2 days
   - Finds our user
   ↓
Send Notification:
   📱 Push: "Your free trial ends in 2 days!"
   📧 Email: "Upgrade to premium to keep using Pookie4u"
   ↓
User opens app:
   - Sees in-app banner
   - "Trial expires in 2 days - Choose a plan"
   ↓
User clicks "Upgrade Now"
   ↓
Navigate to subscription screen
   ↓
User chooses monthly or 6-month plan
   ↓
Payment processed
   ↓
✅ Subscription active! No interruption
```

---

### Flow 5: Auto-Renew (Monthly)

```
Day 1: User subscribes to monthly plan ($4.99)
   ↓
Day 30: Subscription renewal date
   ↓
Google Play automatically:
   - Charges $4.99 to saved payment method
   - Extends subscription for another 30 days
   ↓
RevenueCat receives webhook:
   - subscription_renewed event
   ↓
Backend (optional):
   - Updates subscription_end_date
   - Increments renewal_count
   ↓
User continues using app:
   - No interruption
   - No action needed
   ↓
✅ Seamless renewal!
```

---

## 🔧 Code Changes Needed

### Backend Changes:

**File:** `/app/backend/server.py`

**1. Enhanced Google OAuth Signup:**
```python
# In OAuth callback endpoint
async def handle_google_oauth():
    google_id = user_info.get("sub")
    email = user_info.get("email")
    
    # Check for existing account with this google_id
    existing_user = await db.users.find_one({
        "oauth_providers.google.google_id": google_id
    })
    
    if existing_user:
        # Login to existing account
        return login_existing_user(existing_user)
    else:
        # Create new account
        return create_new_user(google_id, email)
```

**2. Profile Completion Endpoint:**
```python
@api_router.post("/user/complete-profile")
async def complete_profile(
    partner_profile: dict,
    subscription_type: str,
    current_user: dict
):
    await db.users.update_one(
        {"_id": current_user["_id"]},
        {"$set": {
            "partner_profile": partner_profile,
            "profile_completed": True,
            "subscription_type": subscription_type,
            "updated_at": datetime.utcnow()
        }}
    )
    return {"success": True}
```

**3. Trial Expiry Notification Cron:**
```python
# Scheduled task (run daily)
async def check_trial_expiry():
    two_days_from_now = datetime.utcnow() + timedelta(days=2)
    
    users_expiring = await db.users.find({
        "subscription_type": "free_trial",
        "subscription_end_date": {
            "$gte": two_days_from_now.replace(hour=0, minute=0),
            "$lt": two_days_from_now.replace(hour=23, minute=59)
        }
    }).to_list()
    
    for user in users_expiring:
        send_push_notification(
            user_id=user["_id"],
            title="Trial Expiring Soon!",
            body="Your free trial ends in 2 days. Choose a plan to continue."
        )
```

---

### Frontend Changes:

**File:** `/app/frontend/src/screens/AuthScreen.tsx`

**Add Navigation Logic:**
```typescript
// After successful login
const handleLoginSuccess = (userData) => {
  if (userData.profile_completed) {
    router.replace('/(tabs)/home');
  } else {
    router.replace('/onboarding');
  }
};
```

**File:** `/app/frontend/app/onboarding.tsx` (NEW)

**Create Onboarding Flow:**
```typescript
// Multi-step onboarding
const steps = [
  'partner_name',
  'partner_birthday',
  'anniversary',
  'relationship_mode',
  'subscription_selection'
];

// Collect data, then call:
await completeProfile(partnerData, subscriptionType);
router.replace('/(tabs)/home');
```

---

## 📊 Summary Table

| Feature | Status | Backend | Frontend | Effort |
|---------|--------|---------|----------|--------|
| 1. Duplicate Prevention | ⏳ Partial | Update OAuth | None | 30 min |
| 2. User Data Storage | ✅ Complete | Working | Working | 0 min |
| 3. Skip Onboarding | ⏳ Needed | API ready | Add check | 15 min |
| 4. New User Onboarding | ⏳ Needed | Add endpoint | Create screens | 2 hours |
| 5. Trial Notification | ⏳ Needed | Add cron | Add banner | 1 hour |
| 6. Auto-Renew | ✅ Complete | RevenueCat | Working | 0 min |

**Total Effort:** ~3.5-4 hours

---

## 🚀 Implementation Priority

### Phase 1: Critical (Must Have)
1. ✅ Duplicate prevention enhancement
2. ✅ Smart routing (profile_completed check)
3. ⏳ Basic onboarding flow

### Phase 2: Important (Should Have)
4. ⏳ Trial expiry notification
5. ✅ Auto-renew verification

### Phase 3: Nice to Have
6. Enhanced onboarding UI
7. Email notifications
8. Analytics tracking

---

## ✅ Testing Checklist

### Test 1: Duplicate Prevention
- [ ] Login with Google account A
- [ ] Logout
- [ ] Try to login again with same Google account
- [ ] Should login to existing account (not create new)

### Test 2: Data Persistence
- [ ] Fill profile details
- [ ] Close app
- [ ] Reopen app
- [ ] All data should be present

### Test 3: Smart Routing
- [ ] New user → Should see onboarding
- [ ] Existing user → Should go to home
- [ ] No questions for returning users

### Test 4: Onboarding Flow
- [ ] New user completes all steps
- [ ] Selects subscription
- [ ] profile_completed set to true
- [ ] Navigates to home

### Test 5: Trial Notification
- [ ] User on day 12 of trial
- [ ] Should receive notification
- [ ] In-app banner appears
- [ ] Can upgrade from banner

### Test 6: Auto-Renew
- [ ] Subscribe to monthly plan
- [ ] Wait 30 days (or test in sandbox)
- [ ] Subscription renews automatically
- [ ] No interruption

---

**Last Updated:** November 2025  
**Status:** Implementation Plan Complete  
**Next Step:** Begin Phase 1 implementation
