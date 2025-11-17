/**
 * OfflineManager - Centralized offline support system
 * Handles network detection, action queuing, and data synchronization
 */

import NetInfo, { NetInfoState } from '@react-native-community/netinfo';
import AsyncStorage from '@react-native-async-storage/async-storage';

const QUEUE_STORAGE_KEY = '@pookie4u_offline_queue';
const LAST_SYNC_KEY = '@pookie4u_last_sync';

export interface QueuedAction {
  id: string;
  type: 'COMPLETE_TASK' | 'UPDATE_PROFILE' | 'CREATE_EVENT' | 'DELETE_EVENT';
  payload: any;
  timestamp: number;
  retryCount: number;
}

export interface OfflineState {
  isConnected: boolean;
  isInternetReachable: boolean | null;
  lastSyncTime: number | null;
}

class OfflineManagerClass {
  private isOnline: boolean = true;
  private listeners: ((isOnline: boolean) => void)[] = [];
  private queue: QueuedAction[] = [];
  private syncInProgress: boolean = false;
  private unsubscribeNetInfo: (() => void) | null = null;

  constructor() {
    this.initialize();
  }

  /**
   * Initialize network monitoring
   */
  async initialize() {
    // Load queued actions from storage
    await this.loadQueue();

    // Subscribe to network changes
    this.unsubscribeNetInfo = NetInfo.addEventListener((state: NetInfoState) => {
      const wasOnline = this.isOnline;
      this.isOnline = state.isConnected === true && state.isInternetReachable !== false;

      console.log('📡 Network state changed:', {
        isConnected: state.isConnected,
        isInternetReachable: state.isInternetReachable,
        isOnline: this.isOnline,
      });

      // Notify listeners
      this.notifyListeners(this.isOnline);

      // If we just came back online, sync
      if (!wasOnline && this.isOnline) {
        console.log('✅ Back online! Starting sync...');
        this.syncQueue();
      }
    });

    // Get initial network state
    const initialState = await NetInfo.fetch();
    this.isOnline = initialState.isConnected === true && initialState.isInternetReachable !== false;
    this.notifyListeners(this.isOnline);
  }

  /**
   * Clean up subscriptions
   */
  cleanup() {
    if (this.unsubscribeNetInfo) {
      this.unsubscribeNetInfo();
    }
  }

  /**
   * Check if currently online
   */
  getIsOnline(): boolean {
    return this.isOnline;
  }

  /**
   * Subscribe to online/offline state changes
   */
  subscribe(listener: (isOnline: boolean) => void) {
    this.listeners.push(listener);
    // Immediately call with current state
    listener(this.isOnline);

    // Return unsubscribe function
    return () => {
      this.listeners = this.listeners.filter(l => l !== listener);
    };
  }

  /**
   * Notify all listeners of state change
   */
  private notifyListeners(isOnline: boolean) {
    this.listeners.forEach(listener => {
      try {
        listener(isOnline);
      } catch (error) {
        console.error('Error in offline listener:', error);
      }
    });
  }

  /**
   * Queue an action to be executed when online
   */
  async queueAction(action: Omit<QueuedAction, 'id' | 'timestamp' | 'retryCount'>): Promise<void> {
    const queuedAction: QueuedAction = {
      ...action,
      id: `${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      timestamp: Date.now(),
      retryCount: 0,
    };

    this.queue.push(queuedAction);
    await this.saveQueue();

    console.log(`📥 Action queued: ${action.type}`, queuedAction);

    // If online, try to sync immediately
    if (this.isOnline) {
      this.syncQueue();
    }
  }

  /**
   * Get current queue
   */
  getQueue(): QueuedAction[] {
    return [...this.queue];
  }

  /**
   * Get queue size
   */
  getQueueSize(): number {
    return this.queue.length;
  }

  /**
   * Clear the queue (for testing or reset)
   */
  async clearQueue(): Promise<void> {
    this.queue = [];
    await AsyncStorage.removeItem(QUEUE_STORAGE_KEY);
    console.log('🗑️ Queue cleared');
  }

  /**
   * Load queue from AsyncStorage
   */
  private async loadQueue(): Promise<void> {
    try {
      const stored = await AsyncStorage.getItem(QUEUE_STORAGE_KEY);
      if (stored) {
        this.queue = JSON.parse(stored);
        console.log(`📦 Loaded ${this.queue.length} queued actions from storage`);
      }
    } catch (error) {
      console.error('Failed to load queue:', error);
      this.queue = [];
    }
  }

  /**
   * Save queue to AsyncStorage
   */
  private async saveQueue(): Promise<void> {
    try {
      await AsyncStorage.setItem(QUEUE_STORAGE_KEY, JSON.stringify(this.queue));
    } catch (error) {
      console.error('Failed to save queue:', error);
    }
  }

  /**
   * Sync queued actions with backend
   */
  async syncQueue(): Promise<void> {
    if (this.syncInProgress) {
      console.log('⏳ Sync already in progress');
      return;
    }

    if (!this.isOnline) {
      console.log('📴 Offline, cannot sync');
      return;
    }

    if (this.queue.length === 0) {
      console.log('✅ Queue is empty, nothing to sync');
      return;
    }

    this.syncInProgress = true;
    console.log(`🔄 Starting sync of ${this.queue.length} actions...`);

    const actionsToSync = [...this.queue];
    const failedActions: QueuedAction[] = [];

    for (const action of actionsToSync) {
      try {
        await this.executeAction(action);
        console.log(`✅ Synced action: ${action.type}`, action.id);

        // Remove from queue
        this.queue = this.queue.filter(a => a.id !== action.id);
      } catch (error) {
        console.error(`❌ Failed to sync action: ${action.type}`, error);

        // Increment retry count
        action.retryCount++;

        // If retried too many times (5), drop it
        if (action.retryCount >= 5) {
          console.warn(`⚠️ Dropping action after 5 retries: ${action.type}`, action.id);
          this.queue = this.queue.filter(a => a.id !== action.id);
        } else {
          failedActions.push(action);
        }
      }
    }

    // Save updated queue
    await this.saveQueue();

    // Update last sync time
    await AsyncStorage.setItem(LAST_SYNC_KEY, Date.now().toString());

    this.syncInProgress = false;
    console.log(`🔄 Sync complete. ${this.queue.length} actions remaining`);
  }

  /**
   * Execute a queued action
   */
  private async executeAction(action: QueuedAction): Promise<void> {
    const BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL || '';

    switch (action.type) {
      case 'COMPLETE_TASK': {
        const { taskId, token } = action.payload;
        const response = await fetch(`${BACKEND_URL}/api/tasks/complete`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
          },
          body: JSON.stringify({ task_id: taskId }),
        });

        if (!response.ok) {
          throw new Error(`Failed to complete task: ${response.status}`);
        }
        break;
      }

      case 'UPDATE_PROFILE': {
        const { updates, token } = action.payload;
        const response = await fetch(`${BACKEND_URL}/api/user/profile`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
          },
          body: JSON.stringify(updates),
        });

        if (!response.ok) {
          throw new Error(`Failed to update profile: ${response.status}`);
        }
        break;
      }

      case 'CREATE_EVENT': {
        const { event, token } = action.payload;
        const response = await fetch(`${BACKEND_URL}/api/events`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
          },
          body: JSON.stringify(event),
        });

        if (!response.ok) {
          throw new Error(`Failed to create event: ${response.status}`);
        }
        break;
      }

      case 'DELETE_EVENT': {
        const { eventId, token } = action.payload;
        const response = await fetch(`${BACKEND_URL}/api/events/${eventId}`, {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });

        if (!response.ok) {
          throw new Error(`Failed to delete event: ${response.status}`);
        }
        break;
      }

      default:
        console.warn(`Unknown action type: ${(action as any).type}`);
    }
  }

  /**
   * Get last sync time
   */
  async getLastSyncTime(): Promise<number | null> {
    try {
      const stored = await AsyncStorage.getItem(LAST_SYNC_KEY);
      return stored ? parseInt(stored, 10) : null;
    } catch (error) {
      console.error('Failed to get last sync time:', error);
      return null;
    }
  }

  /**
   * Force a sync (for manual refresh)
   */
  async forceSync(): Promise<void> {
    if (!this.isOnline) {
      throw new Error('Cannot sync while offline');
    }
    await this.syncQueue();
  }
}

// Export singleton instance
export const OfflineManager = new OfflineManagerClass();
