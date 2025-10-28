# 🔔 Pookie4u Notification System - Complete Guide

## Overview
The Pookie4u app uses **Expo Push Notifications** to send real-time alerts for events, tasks, streaks, and rewards. The system consists of backend services, frontend managers, and user preference controls.

---

## 🏗️ Architecture

### Components
1. **Backend**: `push_notification_service.py` - Sends notifications via Expo SDK
2. **Frontend**: `NotificationManager.ts` - Handles permissions, tokens, and preferences
3. **Database**: MongoDB stores push tokens and user preferences
4. **Expo Push Service**: Apple/Google notification delivery infrastructure

---

## 📱 How It Works

### Step 1: User Registration & Token Setup
```
1. User installs app and grants notification permissions
2. Frontend requests Expo Push Token from Expo servers
3. Token is sent to backend via POST /api/notifications/register
4. Backend stores token in user's MongoDB document
5. Token is linked to user account for targeted notifications
```

**Frontend Flow:**
```typescript
// NotificationManager.ts
registerForPushNotifications(authToken)
  → getPermissionsAsync()
  → requestPermissionsAsync()
  → getExpoPushTokenAsync()
  → sendTokenToBackend()
```

**Backend Storage:**
```python
# User document updated with:
{
  "push_token": "ExponentPushToken[xxxxxxxxxxxxxx]",
  "push_token_updated_at": "2025-10-28T12:00:00Z",
  "notification_preferences": { ... }
}
```

---

## 🎯 Notification Types

### 1. **Event Reminders** 🎉
**Triggers:**
- 10 days before event
- 3 days before event
- 1 day before event
- Day of event

**Template:**
```python
send_event_reminder(
    push_token="ExponentPushToken[...]",
    event_name="Anniversary",
    days_until=3,
    event_date="2025-11-01"
)
```

**Notification:**
- **Title**: "⏰ Anniversary in 3 days"
- **Body**: "Coming up soon: Anniversary"
- **Category**: `event_reminder`
- **Priority**: High (if ≤1 day), Default (otherwise)

**User Preferences:**
- `upcoming_events_10_days` - 10-day reminders
- `upcoming_events_3_days` - 3-day reminders
- `upcoming_events_1_day` - 1-day reminders

---

### 2. **Daily Tasks** 💕
**Triggers:**
- Every morning when new daily tasks are generated
- Task completion reminders

**Template:**
```python
send_daily_tasks_notification(
    push_token="ExponentPushToken[...]",
    task_count=3
)
```

**Notification:**
- **Title**: "💕 New Daily Tasks!"
- **Body**: "3 new relationship tasks are waiting for you!"
- **Category**: `new_tasks`
- **Priority**: Default

**User Preference:**
- `new_tasks` - Enable/disable task notifications

---

### 3. **Streak Warnings** ⚡
**Triggers:**
- When user hasn't completed tasks and streak is at risk
- Usually sent in evening (e.g., 8-10 PM)

**Template:**
```python
send_streak_warning(
    push_token="ExponentPushToken[...]",
    streak_count=15,
    hours_remaining=6
)
```

**Notification:**
- **Title**: "⚡ Don't lose your 15-day streak!"
- **Body**: "Complete a task in the next 6 hours to keep your streak alive!"
- **Category**: `streak_ending`
- **Priority**: High

**User Preference:**
- `streak_ending` - Enable/disable streak reminders

---

### 4. **Love Messages** ❤️
**Triggers:**
- Daily love message delivery
- Part of relationship engagement features

**Template:**
```python
send_love_message_notification(
    push_token="ExponentPushToken[...]",
    message_preview="You make every day brighter..."
)
```

**Notification:**
- **Title**: "❤️ New Love Message"
- **Body**: "You make every day brighter..." (50 char preview)
- **Category**: `daily_love_message`
- **Priority**: Default

**User Preference:**
- `daily_love_message` - Enable/disable love messages

---

### 5. **Gift Ideas** 🎁
**Triggers:**
- When new gift suggestions are available
- Before special occasions

**Template:**
```python
send_gift_idea_notification(
    push_token="ExponentPushToken[...]",
    occasion="Valentine's Day"
)
```

**Notification:**
- **Title**: "🎁 Perfect Gift Idea!"
- **Body**: "We found the perfect gift for Valentine's Day!"
- **Category**: `gift_ideas`
- **Priority**: Default

**User Preference:**
- `gift_ideas` - Enable/disable gift notifications

---

### 6. **Weekly Winners** 🏆
**Triggers:**
- End of each week for top performers
- Leaderboard updates

**Template:**
```python
send_weekly_winner_notification(
    push_token="ExponentPushToken[...]",
    points=1250,
    rank=3
)
```

**Notification:**
- **Title**: "🏆 You're a Weekly Winner!"
- **Body**: "Congratulations! You earned 1250 points this week! Rank #3"
- **Category**: `weekly_winner`
- **Priority**: High

**User Preference:**
- `weekly_winner` - Enable/disable winner announcements

---

### 7. **Subscription Alerts** ⏰
**Triggers:**
- 7 days before subscription expires
- 3 days before subscription expires
- 1 day before subscription expires

**Template:**
```python
send_subscription_expiring_notification(
    push_token="ExponentPushToken[...]",
    days_remaining=3,
    subscription_type="Premium Monthly"
)
```

**Notification:**
- **Title**: "⏰ Subscription Expiring Soon"
- **Body**: "Your Premium Monthly subscription expires in 3 days"
- **Category**: `subscription`
- **Priority**: High (if ≤3 days), Default (otherwise)

---

### 8. **Milestone Rewards** 🎉
**Triggers:**
- When user reaches 1000 points
- Every 1000 points thereafter (continuous cycles)

**Template:**
```python
send_milestone_reached_notification(
    push_token="ExponentPushToken[...]",
    points=1000,
    cycle_number=2
)
```

**Notification:**
- **Title**: "🎉 You reached 1000 points! (Cycle 2)"
- **Body**: "Claim your reward! You've earned a special gift coupon!"
- **Category**: `milestone_reward`
- **Priority**: High

---

### 9. **Referral Success** 🤝
**Triggers:**
- When referred user completes registration
- Both referrer and referee get notified

**Template:**
```python
send_referral_success_notification(
    push_token="ExponentPushToken[...]",
    referral_name="John",
    points_earned=50
)
```

**Notification:**
- **Title**: "🤝 Referral Success!"
- **Body**: "John joined using your code! You earned 50 points!"
- **Category**: `referral`
- **Priority**: Default

---

## 🔧 API Endpoints

### 1. Register Push Token
```http
POST /api/notifications/register
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json

{
  "push_token": "ExponentPushToken[xxxxxxxxxxxxxx]",
  "device_info": {
    "platform": "ios",
    "device_name": "iPhone 14",
    "os_version": "17.0"
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "Push token registered successfully",
  "modified_count": 1
}
```

---

### 2. Send Test Notification
```http
POST /api/notifications/test
Authorization: Bearer <JWT_TOKEN>
```

**Response:**
```json
{
  "success": true,
  "message": "Test notification sent successfully"
}
```

---

### 3. Get Notification Preferences
```http
GET /api/notifications/preferences
Authorization: Bearer <JWT_TOKEN>
```

**Response:**
```json
{
  "success": true,
  "preferences": {
    "streak_ending": true,
    "daily_love_message": true,
    "new_tasks": true,
    "gift_ideas": true,
    "upcoming_events_10_days": true,
    "upcoming_events_3_days": true,
    "upcoming_events_1_day": true,
    "weekly_winner": true,
    "monthly_winner": false,
    "app_update": true
  }
}
```

---

### 4. Update Notification Preferences
```http
PUT /api/notifications/preferences
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json

{
  "streak_ending": false,
  "daily_love_message": true,
  "new_tasks": true
}
```

**Response:**
```json
{
  "success": true,
  "message": "Notification preferences updated successfully"
}
```

---

## 📲 Frontend Implementation

### Registering for Notifications
```typescript
// In app initialization or after login
import { NotificationManager } from '../utils/NotificationManager';

const notificationManager = NotificationManager.getInstance();
const token = await notificationManager.registerForPushNotifications(authToken);

if (token) {
  console.log('✅ Notifications enabled');
} else {
  console.warn('⚠️ Notifications not available');
}
```

### Handling Received Notifications
```typescript
// Set up notification listener
useEffect(() => {
  const subscription = Notifications.addNotificationReceivedListener(notification => {
    console.log('Notification received:', notification);
    const { type } = notification.request.content.data;
    
    switch (type) {
      case 'event_reminder':
        // Navigate to Events tab
        break;
      case 'daily_tasks':
        // Navigate to Tasks tab
        break;
      case 'streak_warning':
        // Show streak alert
        break;
      // ... handle other types
    }
  });

  return () => subscription.remove();
}, []);
```

### Managing Preferences
```typescript
// Update specific preference
await notificationManager.savePreferences({
  streak_ending: false,
  daily_love_message: true,
});

// Get current preferences
const prefs = notificationManager.getPreferences();
console.log('Current preferences:', prefs);
```

---

## 🎨 Notification Channels (Android)

Android organizes notifications into channels, allowing users to control each type independently:

| Channel ID | Name | Importance | Use Case |
|------------|------|------------|----------|
| `streak_ending` | Streak Reminders | HIGH | Critical streak warnings |
| `daily_messages` | Daily Love Messages | DEFAULT | Romance messages |
| `tasks` | Task Notifications | DEFAULT | Task reminders |
| `events` | Event Reminders | HIGH | Upcoming events |
| `winners` | Winner Announcements | DEFAULT | Leaderboard updates |
| `app_updates` | App Updates | LOW | Non-critical updates |

---

## 🚀 Scheduled Notifications (Future Enhancement)

### Current Implementation:
- Backend sends notifications in real-time via Expo Push Service
- No local scheduled notifications

### Potential Improvements:
1. **Local Scheduling**: Schedule event reminders locally on device
2. **Background Tasks**: Use Expo Background Fetch for periodic checks
3. **Time Zone Support**: Send notifications at optimal user local time
4. **Smart Timing**: ML-based notification timing based on user engagement

---

## 🔒 Security & Privacy

### Token Security:
- Push tokens are encrypted in transit (HTTPS)
- Stored securely in MongoDB with user authentication
- Tokens expire and refresh automatically

### User Control:
- Fine-grained preference controls (10 categories)
- Can disable all notifications via device settings
- Can toggle individual notification types in app settings

### Privacy:
- Notifications contain minimal personal data
- No sensitive information in notification bodies
- Deep links require authentication

---

## 🐛 Troubleshooting

### Notifications Not Received:
1. **Check token registration**: POST /api/notifications/test
2. **Verify permissions**: Device Settings → Pookie4u → Notifications
3. **Check preferences**: User may have disabled specific categories
4. **Validate token format**: Must start with `ExponentPushToken[`
5. **Device limitations**: Simulators don't support push notifications

### Common Issues:
- **"Device not registered"**: Token expired, user needs to re-authenticate
- **"Invalid token format"**: Token not properly stored, re-register needed
- **"Push server error"**: Expo service issue, retry later
- **Silent notifications**: User disabled notification sounds in device settings

---

## 📊 Monitoring & Analytics

### Backend Logging:
```python
logger.info(f"Push notification sent: {title} to user {user_id}")
logger.error(f"Push notification failed: {error_message}")
```

### Success Tracking:
- Monitor delivery receipts from Expo
- Track token registration rates
- Analyze notification engagement (opens, dismissals)

### Metrics to Track:
- Notification delivery success rate
- User engagement per notification type
- Opt-out rates by category
- Average time to notification action

---

## 🎯 Best Practices

### Do's:
✅ Request permissions at appropriate time (after login)
✅ Provide clear value proposition before asking
✅ Allow granular control over notification types
✅ Respect user preferences and quiet hours
✅ Test notifications thoroughly on physical devices
✅ Handle token refresh gracefully

### Don'ts:
❌ Spam users with too many notifications
❌ Send notifications without user consent
❌ Include sensitive data in notification body
❌ Ignore user preference settings
❌ Test only on simulators (they don't support push)
❌ Assume notifications will always be delivered

---

## 🔄 Notification Flow Summary

```
┌─────────────┐
│   Backend   │
│  Triggers   │
│  Event      │
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│ Push Notification   │
│ Service             │
│ (push_notification_ │
│  service.py)        │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Expo Push Service   │
│ (Apple/Google)      │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  User Device        │
│  Notification       │
│  Manager            │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  User sees          │
│  notification and   │
│  can interact       │
└─────────────────────┘
```

---

## 📝 Summary

The Pookie4u notification system provides:
- **9 notification types** for different app features
- **10 user preference controls** for customization
- **Real-time delivery** via Expo Push Service
- **Cross-platform support** (iOS & Android)
- **Secure token management** with MongoDB storage
- **Comprehensive API** for backend integration

This system enhances user engagement by delivering timely, relevant notifications while respecting user preferences and privacy.
