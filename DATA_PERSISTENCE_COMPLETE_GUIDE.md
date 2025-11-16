# Complete Data Persistence & Restoration Guide

## Overview

All user data in Pookie4u is persistently stored in MongoDB and automatically restored when users log back in. This ensures a seamless experience across app sessions and devices.

## ✅ What Gets Saved

### 1. User Profile Data
- **Email** - User's email address
- **Name** - User's display name
- **Profile Image** - Base64 encoded profile picture
- **Relationship Mode** - SAME_HOME, LONG_DISTANCE, etc.
- **Created At / Updated At** - Timestamps

### 2. Partner Profile Data
- **Partner Name**
- **Birthday**
- **Anniversary Date**
- **Favorite Color**
- **Favorite Food**
- **Favorite Flower**
- **Favorite Brand**
- **Dress Size**
- **Ring Size**
- **Top/Jeans Size**
- **Perfume Preference**
- **Additional Notes**

### 3. Gamification Stats
- **Total Points** - Accumulated points
- **Current Level** - User's level (based on points)
- **Current Streak** - Consecutive days active
- **Longest Streak** - All-time longest streak
- **Tasks Completed** - Total completed tasks
- **Badges Earned** - Array of achievement badges

### 4. Subscription Data
- **Subscription Type** - Free trial, monthly, yearly
- **Subscription Status** - Active, inactive, expired
- **Trial Started** - Boolean
- **Start/End Dates** - Subscription period

### 5. Other Data
- **Profile Completed** - Onboarding status
- **Referral Code** - Unique code for sharing
- **Push Notification Token** - For notifications

## 🔄 Data Synchronization Flow

### On User Registration

```typescript
1. User registers → Backend creates user in MongoDB
2. Token issued → Stored in AsyncStorage
3. Profile fetched → User data loaded
4. Game data reset → Fresh start for new user
5. Push notifications registered
```

**Backend Storage:**
```json
{
  "_id": "user_id",
  "email": "user@example.com",
  "name": "John Doe",
  "total_points": 0,
  "current_level": 1,
  "current_streak": 0,
  "longest_streak": 0,
  "tasks_completed": 0,
  "badges": [],
  "profile_image": null,
  "partner_profile": {},
  "created_at": "2025-11-16T06:00:00Z"
}
```

### On User Login

```typescript
1. User enters credentials
2. Backend validates → Issues token
3. Frontend stores token → AsyncStorage
4. Profile fetched → GET /api/user/profile
5. User data loaded → Auth store updated
6. Game data synced → From backend to game store
7. Push notifications registered
```

**Code Flow:**
```typescript
// useAuthStore.ts - login()
login: async (email, password) => {
  // 1. Authenticate
  const response = await fetch('/api/auth/login', {...});
  const { access_token } = await response.json();
  
  // 2. Store token
  set({ token: access_token, isAuthenticated: true });
  
  // 3. Fetch profile
  await get().fetchProfile();
  
  // 4. Sync game data
  const currentUser = get().user;
  if (currentUser) {
    const gameStore = useGameStore.getState();
    await gameStore.syncFromBackend({
      total_points: currentUser.total_points,
      current_level: currentUser.current_level,
      current_streak: currentUser.current_streak,
      longest_streak: currentUser.longest_streak,
      tasks_completed: currentUser.tasks_completed,
      badges: currentUser.badges,
    });
  }
}
```

### On App Restart (Existing Session)

```typescript
1. App starts → Check AsyncStorage for token
2. Token found → Validate session
3. Session validation → GET /api/user/profile
4. Profile validated → User data loaded
5. Game data synced → Automatic sync from backend
6. User taken to home screen
```

**Code Flow:**
```typescript
// useAuthStore.ts - validateSession()
validateSession: async () => {
  const { token } = get();
  
  // 1. Fetch profile with token
  const response = await fetch('/api/user/profile', {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  
  // 2. Update user data
  const user = await response.json();
  set({ user, isAuthenticated: true });
  
  // 3. Sync game data
  const gameStore = useGameStore.getState();
  await gameStore.syncFromBackend({
    total_points: user.total_points,
    current_level: user.current_level,
    current_streak: user.current_streak,
    longest_streak: user.longest_streak,
    tasks_completed: user.tasks_completed,
    badges: user.badges,
  });
}
```

### On Task Completion

```typescript
1. User completes task → POST /api/tasks/complete
2. Backend updates user stats → MongoDB
3. Backend returns updated stats
4. Frontend syncs immediately → Game store updated
5. Both AsyncStorage and memory updated
```

**Backend Update:**
```python
# server.py - complete_task()
new_total_points = current_user.get("total_points", 0) + points_earned
new_tasks_completed = current_user.get("tasks_completed", 0) + 1
new_current_streak = calculate_streak(current_user)

# Update in MongoDB
users_collection.update_one(
    {"_id": current_user["_id"]},
    {"$set": {
        "total_points": new_total_points,
        "tasks_completed": new_tasks_completed,
        "current_streak": new_current_streak,
        "longest_streak": max(new_current_streak, longest_streak)
    }}
)
```

**Frontend Sync:**
```typescript
// TasksContent.tsx
const result = await fetch('/api/tasks/complete', {...});
const data = await result.json();

// Sync game store with backend response
const gameStore = useGameStore.getState();
await gameStore.syncTaskCompletion({
  total_points: data.total_points,
  new_level: data.new_level,
  current_streak: data.current_streak,
  longest_streak: data.longest_streak,
  tasks_completed: data.tasks_completed,
  badges: data.badges,
});
```

### On Profile Update

```typescript
1. User updates profile → PUT /api/user/profile-image
2. Backend saves to MongoDB
3. Frontend updates local state
4. AsyncStorage updated via persist middleware
```

## 🗄️ Storage Layers

### Layer 1: MongoDB (Backend - Source of Truth)
- **Purpose**: Permanent storage, source of truth
- **Data**: All user data, permanently saved
- **Access**: Via API endpoints
- **Persistence**: Forever (unless user deletes account)

### Layer 2: AsyncStorage (Frontend - Cache)
- **Purpose**: Offline access, quick load
- **Data**: Auth token, user profile, game stats
- **Access**: Zustand persist middleware
- **Persistence**: Until app uninstall or manual clear

### Layer 3: Memory (Zustand Stores)
- **Purpose**: Runtime state management
- **Data**: Current session data
- **Access**: Direct store access
- **Persistence**: Only while app is running

## 📊 Data Flow Diagram

```
                    USER ACTIONS
                         │
                         ▼
    ┌────────────────────────────────────────┐
    │         FRONTEND (React Native)         │
    ├────────────────────────────────────────┤
    │                                          │
    │  ┌─────────────┐      ┌──────────────┐ │
    │  │ Auth Store  │◄────►│  Game Store  │ │
    │  └─────────────┘      └──────────────┘ │
    │         │                      │         │
    │         ▼                      ▼         │
    │  ┌──────────────────────────────────┐  │
    │  │      AsyncStorage (Cache)         │  │
    │  └──────────────────────────────────┘  │
    │         │                                │
    └─────────┼────────────────────────────────┘
              │
              │ API Calls (HTTP/HTTPS)
              │
              ▼
    ┌─────────────────────────────────────────┐
    │         BACKEND (FastAPI)                │
    ├─────────────────────────────────────────┤
    │                                           │
    │  ┌────────────────────────────────────┐ │
    │  │    MongoDB Database (Permanent)     │ │
    │  │  • Users Collection                 │ │
    │  │  • Tasks Collection                 │ │
    │  │  • Events Collection                │ │
    │  │  • Referrals Collection             │ │
    │  └────────────────────────────────────┘ │
    │                                           │
    └───────────────────────────────────────────┘
```

## 🔐 Data Restoration Scenarios

### Scenario 1: User Logs Out and Logs Back In
1. Logout clears AsyncStorage and memory
2. Login fetches fresh data from MongoDB
3. All stats restored exactly as before
4. ✅ **Result**: Complete data restoration

### Scenario 2: App Crashes or Force Quit
1. AsyncStorage persists (not affected)
2. App restart validates session
3. Data loaded from AsyncStorage (fast)
4. Background sync with MongoDB
5. ✅ **Result**: Instant load with data integrity

### Scenario 3: App Uninstall and Reinstall
1. AsyncStorage cleared (device storage wiped)
2. User must login again
3. Login fetches from MongoDB
4. All data restored
5. ✅ **Result**: Complete recovery from backend

### Scenario 4: Switch Devices
1. Login on new device
2. Fetch profile from MongoDB
3. All data synced to new device
4. ✅ **Result**: Seamless cross-device experience

### Scenario 5: Network Issues During Sync
1. AsyncStorage has cached data (offline mode)
2. App uses cached data
3. When network returns, sync with backend
4. ✅ **Result**: Graceful offline handling

## 🛡️ Data Integrity Measures

### 1. Dual Storage Strategy
- Backend is always source of truth
- Frontend cache for performance
- Regular sync ensures consistency

### 2. Sync Points
- **Login**: Full profile sync
- **Session validation**: Profile sync
- **Task completion**: Immediate sync
- **Profile update**: Immediate sync
- **Page navigation**: Background sync

### 3. Conflict Resolution
- Backend data always wins
- Frontend accepts backend state
- No client-side data generation

### 4. Error Handling
```typescript
// Network error - keep local data
catch (error) {
  console.log('Network error - using cached data');
  // Don't clear local state
}

// Auth error - clear everything
catch (error) {
  if (error.status === 401) {
    console.log('Token invalid - logging out');
    get().logout(); // Clear all data
  }
}
```

## 📱 Implementation Details

### Auth Store Persistence (useAuthStore.ts)

```typescript
export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      // ... store logic ...
    }),
    {
      name: 'auth-store',
      storage: createJSONStorage(() => AsyncStorage),
      partialize: (state) => ({
        user: state.user,           // Full user profile
        token: state.token,         // Auth token
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);
```

### Game Store Persistence (useGameStore.ts)

```typescript
const useGameStore = create<GameState>((set, get) => ({
  // ... store logic ...
  
  // Sync from backend
  syncFromBackend: async (userData: any) => {
    const syncedData = {
      totalPoints: userData.total_points,
      currentLevel: userData.current_level,
      currentStreak: userData.current_streak,
      longestStreak: userData.longest_streak,
      tasksCompleted: userData.tasks_completed,
      badges: userData.badges,
      lastActiveDate: new Date().toISOString(),
    };
    
    set(syncedData);
    await get().persistData(syncedData); // Save to AsyncStorage
  },
}));
```

### Backend User Schema

```python
# MongoDB user document
{
    "_id": ObjectId("..."),
    "email": "user@example.com",
    "password": "hashed_password",
    "name": "John Doe",
    "relationship_mode": "LONG_DISTANCE",
    "partner_profile": {
        "name": "Jane Doe",
        "birthday": "1995-06-25",
        "anniversary": "2024-01-25",
        "favorite_color": "Blue",
        # ... other fields ...
    },
    "total_points": 45,
    "current_level": 1,
    "current_streak": 1,
    "longest_streak": 1,
    "tasks_completed": 5,
    "badges": [],
    "profile_image": "base64_string",
    "profile_completed": True,
    "subscription_type": "trial",
    "subscription_status": "active",
    "trial_started": True,
    "created_at": datetime(...),
    "updated_at": datetime(...),
}
```

## 🔧 Maintenance & Monitoring

### Logging

```typescript
// All sync operations log:
console.log('📥 Syncing game data from backend');
console.log('✅ Game data synced:', syncedData);
console.log('⚠️ Failed to sync:', error);
```

### Health Checks

- Session validation on app start
- Profile fetch success/failure tracking
- Sync operation monitoring

### Data Recovery

If data appears missing:
1. Check backend logs
2. Verify user exists in MongoDB
3. Check token validity
4. Force re-login to re-sync

## ✅ Testing Data Persistence

### Test 1: Login Persistence
1. Login to app
2. Complete some tasks (points increase)
3. Close app
4. Reopen app
5. **Expected**: All data restored, points unchanged

### Test 2: Cross-Device Sync
1. Login on Device A
2. Complete tasks
3. Login on Device B with same account
4. **Expected**: All stats match Device A

### Test 3: Offline Mode
1. Use app with good network
2. Turn off network
3. App should still show data from cache
4. Turn network back on
5. **Expected**: Data syncs with backend

### Test 4: Logout/Login
1. Complete tasks (earn points)
2. Logout
3. Login again
4. **Expected**: All progress restored

## 🎯 Summary

**Data Saved in Backend (MongoDB):**
- ✅ User profile (name, email, image)
- ✅ Partner details (all fields)
- ✅ Points and level
- ✅ Streaks (current and longest)
- ✅ Tasks completed count
- ✅ Badges earned
- ✅ Subscription status
- ✅ All timestamps

**Data Synced on:**
- ✅ Registration
- ✅ Login
- ✅ App start (session validation)
- ✅ Task completion
- ✅ Profile update
- ✅ Profile page load

**Storage Locations:**
- 🗄️ **MongoDB** (permanent, source of truth)
- 💾 **AsyncStorage** (cache, offline access)
- 🧠 **Memory** (runtime, performance)

**User Experience:**
- 🚀 Fast app startup (cached data)
- 🔄 Automatic background sync
- 📱 Cross-device consistency
- 🌐 Works offline
- 💪 Never lose progress

---

**Status**: ✅ Fully Implemented
**Last Updated**: November 16, 2025
**Version**: 1.0.0
