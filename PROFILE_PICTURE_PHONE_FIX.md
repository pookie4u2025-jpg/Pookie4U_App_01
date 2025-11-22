# 🔧 Profile Picture & Phone Number Bug Fixes

## Issues Reported

1. ❌ **Profile picture showing Gmail picture** instead of custom uploaded picture
2. ❌ **Phone number not being remembered/saved** after entering in settings
3. ✅ **Partner details working correctly**

---

## Root Cause Analysis

### Issue 1: Profile Picture Override

**Problem:** Every time the user logged in with Google OAuth, the system was overwriting their custom profile picture with the Google profile picture.

**Root Causes:**
1. **Backend (`server.py` line 2296-2298)**: On every login, the session endpoint was blindly updating `profile_image` with the Google `picture`
2. **Frontend (`useAuthStore.ts` line 295)**: Was only checking `userData.picture` instead of prioritizing `userData.profile_image`

**Flow:**
```
User uploads custom picture → Saves successfully → User logs out
→ User logs in again → Backend overwrites profile_image with Google picture
→ Frontend displays Google picture ❌
```

### Issue 2: Phone Number Not Saving

**Problem:** Phone number field had a type mismatch between frontend and backend.

**Root Cause:**
- **Frontend (`ComprehensiveSettingsScreen.tsx`)**: Was using `phone` field
- **Frontend (`useAuthStore.ts` interface line 66)**: Declared as accepting only `name` and `email` (missing `phone`)
- **Frontend (`useAuthStore.ts` implementation line 475)**: Was accepting `mobile` instead of `phone`
- **Backend (`server.py` line 2722)**: Expects `phone` field
- Result: Phone number was never sent to backend due to type mismatch

---

## Fixes Implemented

### Fix 1: Profile Picture Preservation

#### Backend Change (`/app/backend/server.py` line 2295-2299)

**BEFORE:**
```python
# Always update picture if available from Google
if picture:
    update_data["picture"] = picture
    update_data["profile_image"] = picture  # Always overwrites!
```

**AFTER:**
```python
# Only update profile_image if user hasn't set a custom one
if picture:
    update_data["picture"] = picture
    # Don't override custom profile_image - only set if not exists
    if not existing_user.get("profile_image"):
        update_data["profile_image"] = picture
```

**Impact:** Custom profile pictures are now preserved across logins. Google picture is only used as a fallback if no custom picture exists.

#### Frontend Change (`/app/frontend/src/stores/useAuthStore.ts` line 296)

**BEFORE:**
```typescript
profile_image: userData.picture,  // Always uses Google picture
```

**AFTER:**
```typescript
// Use custom profile_image if exists, otherwise use Google picture
profile_image: userData.profile_image || userData.picture,
```

**Impact:** Frontend now prioritizes the saved `profile_image` over the Google `picture`.

### Fix 2: Phone Number Saving

#### Frontend Interface Fix (`/app/frontend/src/stores/useAuthStore.ts` line 66)

**BEFORE:**
```typescript
updateUserProfile: (profile: { name?: string; email?: string }) => Promise<boolean>;
```

**AFTER:**
```typescript
updateUserProfile: (profile: { name?: string; email?: string; phone?: string }) => Promise<boolean>;
```

#### Frontend Implementation Fix (`/app/frontend/src/stores/useAuthStore.ts` line 475)

**BEFORE:**
```typescript
updateUserProfile: async (profile: { name?: string; email?: string; mobile?: string }) => {
```

**AFTER:**
```typescript
updateUserProfile: async (profile: { name?: string; email?: string; phone?: string }) => {
```

**Impact:** Phone number is now correctly typed and sent to the backend API.

---

## Technical Details

### Files Modified:

1. **`/app/backend/server.py`**
   - Line 2295-2299: Conditional profile_image update
   - Prevents overwriting custom profile pictures

2. **`/app/frontend/src/stores/useAuthStore.ts`**
   - Line 66: Added `phone` to interface
   - Line 296: Prioritize `profile_image` over `picture`
   - Line 475: Changed `mobile` parameter to `phone`

### Data Flow (After Fix):

#### Profile Picture:
```
1. User uploads custom picture
   → POST /api/user/profile-image { profile_image: base64 }
   → Saved to DB: { profile_image: "data:image/jpeg;base64,..." }

2. User logs out and logs in again
   → GET /api/auth/emergent/session-data
   → Backend checks: if profile_image exists, don't overwrite
   → Returns: { profile_image: "data:image/jpeg;base64,..." }
   → Frontend uses profile_image (custom) instead of picture (Google)
   ✅ Custom picture preserved!
```

#### Phone Number:
```
1. User enters phone in settings: "1234567890"
   → handleSaveAccountDetails() called
   → updateUserProfile({ phone: "1234567890" })
   → PUT /api/user/profile { "phone": "1234567890" }
   → Backend saves to DB: { phone: "1234567890" }
   ✅ Phone number saved!

2. User logs out and logs in again
   → GET /api/auth/emergent/session-data
   → Returns: { phone: "1234567890" }
   → Frontend stores in user state
   → Settings screen displays saved phone number
   ✅ Phone number remembered!
```

---

## Testing Instructions

### Test 1: Profile Picture Preservation

1. **Upload Custom Picture:**
   - Open settings → Edit Account
   - Upload a custom profile picture
   - Click Save
   - ✅ Verify picture appears in settings

2. **Test Persistence:**
   - Log out of the app
   - Log in again with Google
   - Navigate to settings
   - ✅ Verify your custom picture is still there (not Gmail picture)

3. **Expected Result:**
   - Your custom profile picture should persist across logins
   - Gmail picture should only appear if you never uploaded a custom one

### Test 2: Phone Number Saving

1. **Save Phone Number:**
   - Open settings → Edit Account
   - Enter phone number (e.g., "1234567890")
   - Click Save
   - ✅ Verify success message appears

2. **Test Persistence:**
   - Close and reopen the app (or refresh browser)
   - Open settings → Edit Account
   - ✅ Verify phone number is still there

3. **Test Across Sessions:**
   - Log out
   - Log in again
   - Open settings → Edit Account
   - ✅ Verify phone number is remembered

---

## Backend API Reference

### Profile Image Update
```http
PUT /api/user/profile-image
Authorization: Bearer {token}
Content-Type: application/json

{
  "profile_image": "data:image/jpeg;base64,/9j/4AAQSkZJRg..."
}
```

### Profile Update (Including Phone)
```http
PUT /api/user/profile
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "1234567890"
}
```

---

## Rollback Instructions

If issues arise, you can revert these changes:

```bash
cd /app

# Revert backend changes
git checkout backend/server.py

# Revert frontend changes
git checkout frontend/src/stores/useAuthStore.ts

# Restart services
sudo supervisorctl restart backend expo
```

---

## Impact Summary

| Issue | Before | After | Status |
|-------|--------|-------|--------|
| **Profile Picture** | Overwritten on every login | Preserved across logins | ✅ FIXED |
| **Phone Number** | Not saved (type mismatch) | Saved and persisted | ✅ FIXED |
| **Partner Details** | Working correctly | Still working | ✅ WORKING |

---

## Additional Notes

### Why Profile Picture Was Overwriting:

The backend was designed to "always update" the profile picture from Google OAuth to ensure users have a picture. However, this didn't account for users who uploaded custom pictures. The fix adds a conditional check: only use Google picture if no custom picture exists.

### Why Phone Number Wasn't Saving:

The frontend component was passing `phone`, but the store interface and implementation were expecting `mobile`. This mismatch caused the phone number to be ignored in the API request. Standardizing on `phone` (which matches the backend) fixed the issue.

---

**Both issues are now resolved! Test the app and verify the fixes work as expected.** ✅

**Test URL:** https://bug-buster-22.preview.emergentagent.com
