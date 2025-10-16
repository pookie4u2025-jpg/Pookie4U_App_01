import * as Notifications from 'expo-notifications';
import * as Device from 'expo-device';
import Constants from 'expo-constants';
import { Platform } from 'react-native';
// Import AsyncStorage conditionally to avoid SSR issues
let AsyncStorage: any = null;
try {
  AsyncStorage = require('@react-native-async-storage/async-storage').default;
} catch (error) {
  // AsyncStorage not available (e.g., during SSR)
  console.log('AsyncStorage not available during initialization');
}

// Notification categories as required
export enum NotificationCategory {
  STREAK_ENDING = 'streak_ending',
  DAILY_LOVE_MESSAGE = 'daily_love_message',
  NEW_TASKS = 'new_tasks',
  GIFT_IDEAS = 'gift_ideas',
  UPCOMING_EVENTS_10_DAYS = 'upcoming_events_10_days',
  UPCOMING_EVENTS_3_DAYS = 'upcoming_events_3_days',
  UPCOMING_EVENTS_1_DAY = 'upcoming_events_1_day',
  WEEKLY_WINNER = 'weekly_winner',
  MONTHLY_WINNER = 'monthly_winner',
  APP_UPDATE = 'app_update',
}

export interface NotificationPreferences {
  [NotificationCategory.STREAK_ENDING]: boolean;
  [NotificationCategory.DAILY_LOVE_MESSAGE]: boolean;
  [NotificationCategory.NEW_TASKS]: boolean;
  [NotificationCategory.GIFT_IDEAS]: boolean;
  [NotificationCategory.UPCOMING_EVENTS_10_DAYS]: boolean;
  [NotificationCategory.UPCOMING_EVENTS_3_DAYS]: boolean;
  [NotificationCategory.UPCOMING_EVENTS_1_DAY]: boolean;
  [NotificationCategory.WEEKLY_WINNER]: boolean;
  [NotificationCategory.MONTHLY_WINNER]: boolean;
  [NotificationCategory.APP_UPDATE]: boolean;
}

// Default notification preferences (all enabled)
const DEFAULT_PREFERENCES: NotificationPreferences = {
  [NotificationCategory.STREAK_ENDING]: true,
  [NotificationCategory.DAILY_LOVE_MESSAGE]: true,
  [NotificationCategory.NEW_TASKS]: true,
  [NotificationCategory.GIFT_IDEAS]: true,
  [NotificationCategory.UPCOMING_EVENTS_10_DAYS]: true,
  [NotificationCategory.UPCOMING_EVENTS_3_DAYS]: true,
  [NotificationCategory.UPCOMING_EVENTS_1_DAY]: true,
  [NotificationCategory.WEEKLY_WINNER]: true,
  [NotificationCategory.MONTHLY_WINNER]: true,
  [NotificationCategory.APP_UPDATE]: true,
};

class NotificationManager {
  private preferences: NotificationPreferences = DEFAULT_PREFERENCES;
  private expoPushToken: string | null = null;

  constructor() {
    this.setupNotifications();
    this.loadPreferences();
  }

  private async setupNotifications() {
    // Configure notification behavior
    Notifications.setNotificationHandler({
      handleNotification: async () => ({
        shouldShowAlert: true,
        shouldPlaySound: true,
        shouldSetBadge: false,
      }),
    });

    if (Platform.OS === 'android') {
      await Notifications.setNotificationChannelAsync('default', {
        name: 'default',
        importance: Notifications.AndroidImportance.MAX,
        vibrationPattern: [0, 250, 250, 250],
        lightColor: '#FF69B4',
      });

      // Create channels for different notification types
      await this.createNotificationChannels();
    }
  }

  private async createNotificationChannels() {
    const channels = [
      {
        id: 'streak_ending',
        name: 'Streak Reminders',
        importance: Notifications.AndroidImportance.HIGH,
        description: 'Notifications when your streak is about to end',
      },
      {
        id: 'daily_messages',
        name: 'Daily Love Messages',
        importance: Notifications.AndroidImportance.DEFAULT,
        description: 'Daily romantic messages for your partner',
      },
      {
        id: 'tasks',
        name: 'Task Notifications',
        importance: Notifications.AndroidImportance.DEFAULT,
        description: 'New tasks and reminders',
      },
      {
        id: 'events',
        name: 'Event Reminders',
        importance: Notifications.AndroidImportance.HIGH,
        description: 'Upcoming event notifications',
      },
      {
        id: 'winners',
        name: 'Winner Announcements',
        importance: Notifications.AndroidImportance.DEFAULT,
        description: 'Weekly and monthly winner announcements',
      },
      {
        id: 'app_updates',
        name: 'App Updates',
        importance: Notifications.AndroidImportance.LOW,
        description: 'App update notifications',
      },
    ];

    for (const channel of channels) {
      await Notifications.setNotificationChannelAsync(channel.id, {
        name: channel.name,
        importance: channel.importance,
        description: channel.description,
        vibrationPattern: [0, 250, 250, 250],
        lightColor: '#FF69B4',
      });
    }
  }

  // Register for push notifications
  async registerForPushNotifications(authToken?: string): Promise<string | null> {
    if (!Device.isDevice) {
      console.warn('Push notifications require a physical device');
      return null;
    }

    const { status: existingStatus } = await Notifications.getPermissionsAsync();
    let finalStatus = existingStatus;

    if (existingStatus !== 'granted') {
      const { status } = await Notifications.requestPermissionsAsync();
      finalStatus = status;
    }

    if (finalStatus !== 'granted') {
      console.warn('Failed to get push token for push notification');
      return null;
    }

    try {
      const token = await Notifications.getExpoPushTokenAsync({
        projectId: Constants.expoConfig?.extra?.eas?.projectId,
      });
      this.expoPushToken = token.data;
      
      // Send token to backend if auth token provided
      if (authToken) {
        await this.sendTokenToBackend(token.data, authToken);
      }
      
      return token.data;
    } catch (error) {
      console.error('Error getting push token:', error);
      return null;
    }
  }
  
  // Send push token to backend
  private async sendTokenToBackend(pushToken: string, authToken: string): Promise<void> {
    try {
      const backendUrl = process.env.EXPO_PUBLIC_BACKEND_URL;
      const response = await fetch(`${backendUrl}/api/notifications/register`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          push_token: pushToken,
          device_info: {
            platform: Platform.OS,
            device_name: Device.deviceName || 'Unknown',
            os_version: Device.osVersion || 'Unknown',
          },
        }),
      });
      
      if (response.ok) {
        console.log('✅ Push token registered with backend');
      } else {
        console.error('Failed to register push token with backend:', await response.text());
      }
    } catch (error) {
      console.error('Error sending token to backend:', error);
    }
  }

  // Load notification preferences from storage
  private async loadPreferences() {
    try {
      if (!AsyncStorage) {
        console.log('AsyncStorage not available, using default preferences');
        return;
      }
      const stored = await AsyncStorage.getItem('@notification_preferences');
      if (stored) {
        this.preferences = { ...DEFAULT_PREFERENCES, ...JSON.parse(stored) };
      }
    } catch (error) {
      console.warn('Failed to load notification preferences:', error);
    }
  }

  // Save notification preferences to storage
  async savePreferences(preferences: Partial<NotificationPreferences>) {
    try {
      this.preferences = { ...this.preferences, ...preferences };
      if (!AsyncStorage) {
        console.log('AsyncStorage not available, preferences not saved');
        return;
      }
      await AsyncStorage.setItem('@notification_preferences', JSON.stringify(this.preferences));
    } catch (error) {
      console.warn('Failed to save notification preferences:', error);
    }
  }

  // Get current preferences
  getPreferences(): NotificationPreferences {
    return { ...this.preferences };
  }

  // Check if a category is enabled
  isCategoryEnabled(category: NotificationCategory): boolean {
    return this.preferences[category] ?? true;
  }

  // Schedule local notification
  async scheduleNotification(
    category: NotificationCategory,
    title: string,
    body: string,
    trigger?: Notifications.NotificationTriggerInput,
    data?: any
  ) {
    if (!this.isCategoryEnabled(category)) {
      return null;
    }

    try {
      const channelId = this.getCategoryChannelId(category);
      
      return await Notifications.scheduleNotificationAsync({
        content: {
          title,
          body,
          data: { category, ...data },
          sound: true,
          priority: Notifications.AndroidNotificationPriority.HIGH,
          categoryIdentifier: channelId,
        },
        trigger: trigger || null,
      });
    } catch (error) {
      console.error('Failed to schedule notification:', error);
      return null;
    }
  }

  // Get channel ID for category
  private getCategoryChannelId(category: NotificationCategory): string {
    switch (category) {
      case NotificationCategory.STREAK_ENDING:
        return 'streak_ending';
      case NotificationCategory.DAILY_LOVE_MESSAGE:
        return 'daily_messages';
      case NotificationCategory.NEW_TASKS:
        return 'tasks';
      case NotificationCategory.GIFT_IDEAS:
        return 'tasks';
      case NotificationCategory.UPCOMING_EVENTS_10_DAYS:
      case NotificationCategory.UPCOMING_EVENTS_3_DAYS:
      case NotificationCategory.UPCOMING_EVENTS_1_DAY:
        return 'events';
      case NotificationCategory.WEEKLY_WINNER:
      case NotificationCategory.MONTHLY_WINNER:
        return 'winners';
      case NotificationCategory.APP_UPDATE:
        return 'app_updates';
      default:
        return 'default';
    }
  }

  // Cancel all scheduled notifications for a category
  async cancelNotificationsByCategory(category: NotificationCategory) {
    const scheduled = await Notifications.getAllScheduledNotificationsAsync();
    const toCancel = scheduled.filter(
      notification => notification.content.data?.category === category
    );

    for (const notification of toCancel) {
      await Notifications.cancelScheduledNotificationAsync(notification.identifier);
    }
  }

  // Specific notification scheduling methods

  // Schedule streak ending reminder (when streak is about to end)
  async scheduleStreakEndingReminder(streakDays: number, hoursLeft: number) {
    const title = 'Don\'t lose your streak! 🔥';
    const body = `Your ${streakDays}-day streak ends in ${hoursLeft} hours. Complete a task to keep it going!`;
    
    return this.scheduleNotification(
      NotificationCategory.STREAK_ENDING,
      title,
      body,
      { seconds: hoursLeft * 3600 }
    );
  }

  // Schedule daily love message notification
  async scheduleDailyLoveMessage(message: string, time: Date) {
    const title = 'Daily Love Message 💕';
    const body = message;
    
    return this.scheduleNotification(
      NotificationCategory.DAILY_LOVE_MESSAGE,
      title,
      body,
      { date: time },
      { messageText: message }
    );
  }

  // Schedule new tasks notification
  async scheduleNewTasksNotification(taskCount: number) {
    const title = 'New Tasks Available! ✅';
    const body = `${taskCount} new romantic tasks are waiting for you!`;
    
    return this.scheduleNotification(
      NotificationCategory.NEW_TASKS,
      title,
      body
    );
  }

  // Schedule event reminder
  async scheduleEventReminder(eventName: string, daysUntil: number) {
    const title = `Upcoming Event 📅`;
    const body = `${eventName} is in ${daysUntil} day${daysUntil !== 1 ? 's' : ''}!`;
    
    const category = daysUntil >= 10 
      ? NotificationCategory.UPCOMING_EVENTS_10_DAYS
      : daysUntil >= 3 
      ? NotificationCategory.UPCOMING_EVENTS_3_DAYS
      : NotificationCategory.UPCOMING_EVENTS_1_DAY;
    
    return this.scheduleNotification(
      category,
      title,
      body,
      { seconds: daysUntil * 24 * 3600 },
      { eventName, daysUntil }
    );
  }

  // Schedule winner announcement
  async scheduleWinnerAnnouncement(isWeekly: boolean, winnerName: string, prize: string) {
    const period = isWeekly ? 'Weekly' : 'Monthly';
    const title = `${period} Winner Announced! 🏆`;
    const body = `Congratulations to ${winnerName} for winning ${prize}!`;
    
    return this.scheduleNotification(
      isWeekly ? NotificationCategory.WEEKLY_WINNER : NotificationCategory.MONTHLY_WINNER,
      title,
      body,
      null,
      { winnerName, prize, isWeekly }
    );
  }

  // Schedule app update notification
  async scheduleAppUpdateNotification(version: string) {
    const title = 'App Update Available 📲';
    const body = `Pookie4u v${version} is now available with new features!`;
    
    return this.scheduleNotification(
      NotificationCategory.APP_UPDATE,
      title,
      body,
      null,
      { version }
    );
  }

  // Get expo push token for server-side notifications
  getExpoPushToken(): string | null {
    return this.expoPushToken;
  }

  // Clear all notifications
  async clearAllNotifications() {
    await Notifications.cancelAllScheduledNotificationsAsync();
    await Notifications.dismissAllNotificationsAsync();
  }
}

// Singleton instance
export const notificationManager = new NotificationManager();

// Utility functions for easy use
export const registerForNotifications = () => notificationManager.registerForPushNotifications();
export const scheduleNotification = (category: NotificationCategory, title: string, body: string, trigger?: any, data?: any) =>
  notificationManager.scheduleNotification(category, title, body, trigger, data);

// Common notification functions
export const scheduleStreakReminder = (streakDays: number, hoursLeft: number) =>
  notificationManager.scheduleStreakEndingReminder(streakDays, hoursLeft);

export const scheduleDailyMessage = (message: string, time: Date) =>
  notificationManager.scheduleDailyLoveMessage(message, time);

export const scheduleTaskNotification = (taskCount: number) =>
  notificationManager.scheduleNewTasksNotification(taskCount);

export const scheduleEventReminder = (eventName: string, daysUntil: number) =>
  notificationManager.scheduleEventReminder(eventName, daysUntil);

export const announceWinner = (isWeekly: boolean, winnerName: string, prize: string) =>
  notificationManager.scheduleWinnerAnnouncement(isWeekly, winnerName, prize);

export const notifyAppUpdate = (version: string) =>
  notificationManager.scheduleAppUpdateNotification(version);