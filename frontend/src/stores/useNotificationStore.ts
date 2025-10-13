import { create } from 'zustand';
import * as Notifications from 'expo-notifications';
import { Platform } from 'react-native';

// Configure notifications
Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: false,
  }),
});

interface NotificationState {
  permissionGranted: boolean;
  notifications: any[];
  
  // Actions
  requestPermission: () => Promise<boolean>;
  scheduleEventNotification: (notification: EventNotification) => Promise<void>;
  scheduleTaskReminder: (time: string) => Promise<void>;
  cancelNotification: (id: string) => Promise<void>;
  cancelAllNotifications: () => Promise<void>;
}

interface EventNotification {
  title: string;
  body: string;
  date: Date;
  eventId: string;
}

export const useNotificationStore = create<NotificationState>((set, get) => ({
  permissionGranted: false,
  notifications: [],

  requestPermission: async () => {
    try {
      const { status: existingStatus } = await Notifications.getPermissionsAsync();
      let finalStatus = existingStatus;
      
      if (existingStatus !== 'granted') {
        const { status } = await Notifications.requestPermissionsAsync();
        finalStatus = status;
      }
      
      const granted = finalStatus === 'granted';
      set({ permissionGranted: granted });
      
      if (granted && Platform.OS === 'android') {
        await Notifications.setNotificationChannelAsync('default', {
          name: 'default',
          importance: Notifications.AndroidImportance.MAX,
          vibrationPattern: [0, 250, 250, 250],
          lightColor: '#FF69B4',
        });
      }
      
      return granted;
    } catch (error) {
      console.error('Permission error:', error);
      return false;
    }
  },

  scheduleEventNotification: async ({ title, body, date, eventId }) => {
    const { permissionGranted } = get();
    
    if (!permissionGranted) {
      const granted = await get().requestPermission();
      if (!granted) return;
    }

    try {
      const id = await Notifications.scheduleNotificationAsync({
        content: {
          title,
          body,
          sound: 'default',
          data: { eventId, type: 'event_reminder' },
        },
        trigger: { date },
      });

      set(state => ({
        notifications: [...state.notifications, { id, eventId, date, title }]
      }));
    } catch (error) {
      console.error('Error scheduling notification:', error);
    }
  },

  scheduleTaskReminder: async (time: string) => {
    const { permissionGranted } = get();
    
    if (!permissionGranted) {
      const granted = await get().requestPermission();
      if (!granted) return;
    }

    try {
      // Parse time (HH:MM format)
      const [hours, minutes] = time.split(':').map(Number);
      
      const id = await Notifications.scheduleNotificationAsync({
        content: {
          title: 'Daily Love Tasks 💕',
          body: 'Time to complete your daily romantic tasks!',
          sound: 'default',
          data: { type: 'daily_reminder' },
        },
        trigger: {
          hour: hours,
          minute: minutes,
          repeats: true,
        },
      });

      set(state => ({
        notifications: [...state.notifications, { id, type: 'daily_reminder', time }]
      }));
    } catch (error) {
      console.error('Error scheduling daily reminder:', error);
    }
  },

  cancelNotification: async (id: string) => {
    try {
      await Notifications.cancelScheduledNotificationAsync(id);
      set(state => ({
        notifications: state.notifications.filter(notif => notif.id !== id)
      }));
    } catch (error) {
      console.error('Error canceling notification:', error);
    }
  },

  cancelAllNotifications: async () => {
    try {
      await Notifications.cancelAllScheduledNotificationsAsync();
      set({ notifications: [] });
    } catch (error) {
      console.error('Error canceling all notifications:', error);
    }
  },
}));