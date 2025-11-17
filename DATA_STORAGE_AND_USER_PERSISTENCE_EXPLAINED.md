# Data Storage & User Persistence - Complete Guide

## Overview
This document explains exactly where user data is saved, what data we keep, and how the app remembers users when they login again.

---

## 🗄️ **Data Storage Architecture**

### **Two-Tier Storage System:**

```
┌─────────────────────────────────────────┐
│         USER'S DEVICE (Frontend)        │
│                                         │
│  AsyncStorage (Local Storage)          │
│  - User session data                   │
│  - Authentication token                │
│  - Cached user info                    │
│  - Game progress (points, level)       │
│  - Tasks data                          │
│  - Offline queue                       │
└─────────────────────────────────────────┘
                   ↕️
         Internet Connection
                   ↕️
┌─────────────────────────────────────────┐
│      MONGODB ATLAS (Cloud Database)     │
│                                         │
│  Collections:                           │
│  - users (user accounts)               │
│  - user_sessions (login sessions)      │
│  - tasks (daily/weekly tasks)          │
│  - events (user events)                │
│  - messages (love messages)            │
│  - subscription_logs                   │
└─────────────────────────────────────────┘
```

---

## 📱 **Frontend Storage (User's Device)**

### **Location: AsyncStorage**
**Technology:** React Native AsyncStorage (persistent key-value storage)

### **What We Store Locally:**

#### **1. Authentication Data**
**Key:** `@pookie4u_auth_storage`

**Data Stored:**
```json
{
  "state": {
    "user": {
      "id": "uuid-here",
      "email": "user@example.com",
      "name": "John Doe",
      "relationship_mode": "couple",
      "partner_profile": { /* partner details */ },
      "total_points": 150,
      "current_level": 3,
      "current_streak": 5,
      "longest_streak": 10,
      "tasks_completed": 25,
      "badges": ["early_bird", "weekend_warrior"],
      "profile_completed": true,
      "created_at": "2025-01-15T10:30:00Z"
    },
    "token": "jwt-token-here",
    "isAuthenticated": true
  }
}
```

**Purpose:**
- Remember logged-in user
- Auto-login on app restart
- Show user info without fetching from server

**Lifetime:** Until user logs out or clears app data

---

#### **2. Game Data**
**Key:** `@pookie4u_game_data`

**Data Stored:**
```json
{
  "totalPoints": 150,
  "currentLevel": 3,
  "currentStreak": 5,
  "longestStreak": 10,
  "tasksCompleted": 25,
  "badges": ["early_bird", "weekend_warrior"],
  "lastActiveDate": "2025-11-17T00:00:00Z"
}
```

**Purpose:**
- Show points/level without network
- Track daily streaks
- Display badges earned

---

#### **3. Task Data**
**Key:** `task-store`

**Data Stored:**
```json
{
  "dailyTasks": [
    {
      "id": "task-1",
      "title": "Send a morning text",
      "points": 10,
      "completed": true,
      "category": "communication"
    },
    // ... more tasks
  ],
  "weeklyTask": { /* weekly task */ },
  "lastFetch": "2025-11-17T08:00:00Z"
}
```

**Purpose:**
- Show tasks offline
- Remember completed tasks
- Reduce API calls

---

#### **4. Offline Queue**
**Key:** `@pookie4u_offline_queue`

**Data Stored:**
```json
[
  {
    "id": "queue-1",
    "type": "COMPLETE_TASK",
    "payload": {
      "taskId": "task-123",
      "token": "jwt-token"
    },
    "timestamp": 1700124000000,
    "retryCount": 0
  }
]
```

**Purpose:**
- Save actions when offline
- Sync when back online
- No data loss

---

#### **5. Last Sync Time**
**Key:** `@pookie4u_last_sync`

**Data Stored:**
```json
"1700124523000"
```

**Purpose:**
- Know when last synced
- Show "synced X mins ago"

---

## 🌐 **Backend Storage (MongoDB Atlas Cloud)**

### **Database:** `pookie4u` (cloud hosted)
**Access:** Via MongoDB Atlas (username: testuser)

---

### **Collection 1: users**
**Purpose:** Store all user accounts

**Document Structure:**
```json
{
  "_id": "e9985f80-969c-41a0-b6eb-2ddc8de4d659",
  "email": "piyushchawla704@gmail.com",
  "password_hash": "$2b$12$...", // Only for email users, null for Google
  "name": "Piyush Chawla",
  "relationship_mode": "couple",
  
  // Partner Information
  "partner_profile": {
    "name": "Katrina",
    "birthday": "1995-06-25",
    "anniversary": "2024-01-24",
    "favorite_color": "Pink",
    "favorite_food": "Italian",
    "favorite_flower": "Roses",
    "favorite_brand": "Chanel",
    "dress_size": "M",
    "ring_size": "7",
    "perfume_preference": "Floral",
    "notes": "Loves surprises"
  },
  
  // Gamification
  "total_points": 150,
  "current_level": 3,
  "current_streak": 5,
  "longest_streak": 10,
  "tasks_completed": 25,
  "badges": ["early_bird", "weekend_warrior"],
  
  // Subscription
  "subscription_type": "free_trial",
  "subscription_status": "active",
  "subscription_start_date": "2025-11-10T00:00:00Z",
  "subscription_end_date": "2025-11-24T00:00:00Z",
  "trial_used": false,
  
  // OAuth
  "oauth_provider": "google", // or null for email users
  "oauth_id": "google-user-id-here",
  "oauth_profile_pic": "https://lh3.googleusercontent.com/...",
  
  // Metadata
  "profile_completed": true,
  "mobile": "+1234567890",
  "created_at": "2025-11-10T10:30:00Z",
  "updated_at": "2025-11-17T08:45:00Z",
  "last_login": "2025-11-17T08:00:00Z"
}
```

**Key Fields:**
- `_id`: Unique user identifier (UUID)
- `email`: User's email (unique)
- `password_hash`: Hashed password (null for Google users)
- `oauth_provider`: "google" or null
- `partner_profile`: All partner details
- `total_points`, `current_level`: Gamification data
- `subscription_type`: "free_trial", "monthly", "sixmonth"

---

### **Collection 2: user_sessions**
**Purpose:** Store active login sessions

**Document Structure:**
```json
{
  "_id": ObjectId("..."),
  "user_id": "e9985f80-969c-41a0-b6eb-2ddc8de4d659",
  "session_token": "zTW_awGBO26tT2pO3wyzBf-dve23YRNWQbNkK9J2LJg",
  "created_at": "2025-11-17T08:00:00Z",
  "expires_at": "2025-12-17T08:00:00Z", // 30 days from creation
  "last_used": "2025-11-17T10:30:00Z",
  "device_info": {
    "platform": "iOS",
    "app_version": "1.0.0"
  }
}
```

**Purpose:**
- Validate user sessions
- Auto-logout after 30 days
- Track active devices
- Security (revoke sessions)

**Lifetime:** 30 days (auto-expires)

---

### **Collection 3: tasks**
**Purpose:** Store all generated tasks

**Document Structure:**
```json
{
  "_id": ObjectId("..."),
  "user_id": "e9985f80-969c-41a0-b6eb-2ddc8de4d659",
  "task_id": "task-daily-1",
  "type": "daily", // or "weekly"
  "title": "Send a morning text to your partner",
  "description": "Start the day with a sweet message",
  "category": "communication",
  "points": 10,
  "completed": true,
  "completed_at": "2025-11-17T09:00:00Z",
  "date": "2025-11-17",
  "created_at": "2025-11-17T00:00:00Z"
}
```

---

### **Collection 4: events**
**Purpose:** Store user-created events

**Document Structure:**
```json
{
  "_id": ObjectId("..."),
  "user_id": "e9985f80-969c-41a0-b6eb-2ddc8de4d659",
  "event_id": "anniversary_2026",
  "name": "Our Anniversary",
  "date": "2026-01-24",
  "category": "personal_anniversary",
  "importance": "high",
  "reminder_days": 21,
  "created_at": "2025-11-10T10:30:00Z"
}
```

---

### **Collection 5: subscription_logs**
**Purpose:** Track subscription history

**Document Structure:**
```json
{
  "_id": ObjectId("..."),
  "user_id": "e9985f80-969c-41a0-b6eb-2ddc8de4d659",
  "action": "trial_started",
  "subscription_type": "free_trial",
  "timestamp": "2025-11-10T10:30:00Z",
  "details": {
    "trial_days": 14,
    "start_date": "2025-11-10",
    "end_date": "2025-11-24"
  }
}
```

---

## 🔐 **Authentication & Session Management**

### **How Login Works:**

#### **1. User Logs In (Google or Email)**
```
User → Login → Backend validates credentials
  ↓
Backend creates:
  - JWT token (short-lived, 1 hour)
  - Session token (long-lived, 30 days)
  ↓
Backend stores in database:
  - user_sessions collection (with session_token)
  ↓
Backend returns to frontend:
  - session_token
  - user data
```

#### **2. Frontend Saves to AsyncStorage**
```javascript
// Saved automatically by Zustand persist middleware
AsyncStorage.setItem('@pookie4u_auth_storage', JSON.stringify({
  user: { /* user data */ },
  token: "session-token-here",
  isAuthenticated: true
}));
```

#### **3. App Remembers User**
```
User closes app
  ↓
User reopens app
  ↓
Frontend checks AsyncStorage
  ↓
Finds saved session_token
  ↓
Validates with backend
  ↓
✅ Auto-logged in!
```

---

## 🔄 **How App Remembers Users**

### **Auto-Login Flow:**

**Step 1: App Launches**
```javascript
// In useAuthStore.ts
useEffect(() => {
  validateSession(); // Check if session still valid
}, []);
```

**Step 2: Load from AsyncStorage**
```javascript
// Zustand persist middleware automatically loads:
const savedData = AsyncStorage.getItem('@pookie4u_auth_storage');
// Restores: user, token, isAuthenticated
```

**Step 3: Validate with Backend**
```javascript
// GET /api/user/profile
// Headers: { Authorization: Bearer <session_token> }

// Backend checks:
1. Does session exist in user_sessions?
2. Is session expired? (30 days check)
3. Does user still exist?

// If all valid:
return user data + session valid

// If invalid:
return 401 Unauthorized → logout user
```

**Step 4: Update UI**
```javascript
if (sessionValid) {
  setUser(userData);
  setIsAuthenticated(true);
  navigateToHome();
} else {
  logout();
  navigateToLogin();
}
```

---

## 📊 **Data Lifecycle**

### **New User (Google Login):**
```
1. User clicks "Continue with Google"
   ↓
2. Google OAuth returns: email, name, google_id
   ↓
3. Backend checks: Does user exist?
   - NO → Create new user in MongoDB
   - YES → Load existing user
   ↓
4. Backend creates session_token
   ↓
5. Session saved to user_sessions collection
   ↓
6. Frontend receives: token + user data
   ↓
7. Frontend saves to AsyncStorage
   ↓
8. User logged in ✅
```

**Data Created:**
- MongoDB: 1 user document, 1 session document
- AsyncStorage: auth data, game data, empty tasks

---

### **Returning User:**
```
1. User opens app
   ↓
2. Frontend checks AsyncStorage
   ↓
3. Finds session_token
   ↓
4. Sends to backend: GET /api/user/profile
   ↓
5. Backend validates session
   ↓
6. Returns fresh user data
   ↓
7. Frontend updates local cache
   ↓
8. User auto-logged in ✅
```

**Data Used:**
- AsyncStorage: Cached session_token
- MongoDB: Validate session, fetch latest data

---

## 🔒 **Security Measures**

### **1. Session Expiry**
- Sessions expire after 30 days
- Old sessions auto-deleted
- Forces re-login for security

### **2. Token Validation**
- Every API call validates token
- Invalid token → 401 error → logout
- Prevents unauthorized access

### **3. Password Hashing**
- Passwords never stored in plain text
- Bcrypt hashing (strong encryption)
- Google users: no password stored

### **4. Secure Storage**
- AsyncStorage encrypted on device
- HTTPS for all network calls
- MongoDB Atlas: encrypted at rest

---

## 📱 **What Happens When...**

### **User Logs Out:**
```
1. User clicks logout
   ↓
2. Frontend clears AsyncStorage
   ↓
3. Backend deletes session from user_sessions
   ↓
4. User redirected to login screen
   ↓
5. All local data wiped ✅
```

### **User Uninstalls App:**
```
1. App uninstalled
   ↓
2. AsyncStorage cleared (OS does this)
   ↓
3. MongoDB data remains (permanent)
   ↓
4. User reinstalls → can login again
   ↓
5. All data restored from MongoDB ✅
```

### **User Switches Devices:**
```
1. Login on Device 2
   ↓
2. New session created
   ↓
3. Device 1 session still valid
   ↓
4. Both devices logged in ✅
   ↓
5. Data synced to both via MongoDB
```

---

## 🗂️ **Complete Data Inventory**

### **What We Store Permanently (MongoDB):**
✅ User account (email, name)
✅ Partner profile (birthday, preferences)
✅ Points, level, streaks, badges
✅ Task completion history
✅ Events created by user
✅ Subscription status
✅ Login sessions (30 days)

### **What We Store Temporarily (AsyncStorage):**
✅ Session token (until logout)
✅ User profile (until logout)
✅ Cached tasks (1 day)
✅ Game stats (synced daily)
✅ Offline queue (until synced)

### **What We DON'T Store:**
❌ Passwords (Google users)
❌ Credit card details (handled by Google/RevenueCat)
❌ Private messages content
❌ Location data
❌ Device identifiers (optional)

---

## 🔍 **Data Flow Example**

### **User Completes a Task:**
```
1. User taps "Complete Task" (offline)
   ↓
2. Frontend:
   - Updates local task state (AsyncStorage)
   - Shows success message
   - Queues action in offline queue
   ↓
3. User comes online
   ↓
4. Frontend sends: POST /api/tasks/complete
   ↓
5. Backend:
   - Updates task in tasks collection
   - Updates user points in users collection
   - Returns new point total
   ↓
6. Frontend:
   - Updates local cache
   - Shows points animation
   - Removes from offline queue
   ↓
7. Data synced everywhere ✅
```

---

## 📊 **Storage Sizes**

### **Per User:**
- **MongoDB**: ~50 KB per user
  - User document: ~10 KB
  - Tasks: ~20 KB
  - Events: ~10 KB
  - Sessions: ~5 KB
  
- **AsyncStorage**: ~100 KB per user
  - Auth data: ~20 KB
  - Game data: ~5 KB
  - Tasks cache: ~50 KB
  - Offline queue: ~25 KB

**Total per user:** ~150 KB

---

## ✅ **Summary**

### **Where Data is Saved:**
1. **MongoDB Atlas** (cloud) - Permanent storage
2. **AsyncStorage** (device) - Temporary cache

### **What Makes App Remember User:**
1. **Session Token** saved in AsyncStorage
2. **30-day validity** in MongoDB
3. **Auto-validation** on app launch

### **Login Persistence:**
- Works for 30 days without re-login
- Survives app restarts
- Survives phone restarts
- Cleared on logout only

---

**Last Updated**: November 2025  
**Database**: MongoDB Atlas  
**Frontend Storage**: AsyncStorage  
**Session Lifetime**: 30 days  
**Production Status**: ✅ Live
