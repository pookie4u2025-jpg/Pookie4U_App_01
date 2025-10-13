import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
// Import AsyncStorage conditionally to avoid SSR issues
let AsyncStorage: any = null;
try {
  AsyncStorage = require('@react-native-async-storage/async-storage').default;
} catch (error) {
  // AsyncStorage not available (e.g., during SSR)
  console.log('AsyncStorage not available during initialization');
}

const BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL || '';

interface Task {
  id: string;
  title: string;
  description?: string;
  category: string;
  points: number;
  completed: boolean;
  completed_at?: string;
  is_physical?: boolean;
  estimated_time_minutes?: number;
  difficulty?: string;
  tips?: string;
  generation_metadata?: any;
}

interface TaskState {
  dailyTasks: Task[];
  weeklyTask: Task | null;
  loading: boolean;
  error: string | null;
  
  // Actions
  fetchDailyTasks: (token: string, regenerate?: boolean) => Promise<void>;
  fetchWeeklyTask: (token: string, regenerate?: boolean) => Promise<void>;
  completeTask: (taskId: string, token: string) => Promise<boolean>;
  clearError: () => void;
}

export const useTaskStore = create<TaskState>()(
  persist(
    (set, get) => ({
      dailyTasks: [],
      weeklyTask: null,
      loading: false,
      error: null,

      fetchDailyTasks: async (token: string, regenerate: boolean = false) => {
        set({ loading: true, error: null });
        try {
          const url = regenerate ? `${BACKEND_URL}/api/tasks/daily?regenerate=true` : `${BACKEND_URL}/api/tasks/daily`;
          const response = await fetch(url, {
            headers: {
              'Authorization': `Bearer ${token}`,
            },
          });

          if (!response.ok) {
            throw new Error('Failed to fetch daily tasks');
          }

          const data = await response.json();
          set({ 
            dailyTasks: data.tasks || [],
            loading: false,
            error: null
          });
        } catch (error) {
          set({ 
            loading: false, 
            error: error instanceof Error ? error.message : 'Failed to fetch daily tasks'
          });
        }
      },

      fetchWeeklyTask: async (token: string, regenerate: boolean = false) => {
        set({ loading: true, error: null });
        try {
          const url = regenerate ? `${BACKEND_URL}/api/tasks/weekly?regenerate=true` : `${BACKEND_URL}/api/tasks/weekly`;
          const response = await fetch(url, {
            headers: {
              'Authorization': `Bearer ${token}`,
            },
          });

          if (!response.ok) {
            throw new Error('Failed to fetch weekly task');
          }

          const data = await response.json();
          // Backend returns tasks array, we need the first (and only) weekly task
          const weeklyTask = data.tasks && data.tasks.length > 0 ? data.tasks[0] : null;
          set({ 
            weeklyTask: weeklyTask,
            loading: false,
            error: null
          });
        } catch (error) {
          set({ 
            loading: false, 
            error: error instanceof Error ? error.message : 'Failed to fetch weekly task'
          });
        }
      },

      completeTask: async (taskId: string, token: string) => {
        try {
          const response = await fetch(`${BACKEND_URL}/api/tasks/complete`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${token}`,
            },
            body: JSON.stringify({ task_id: taskId }),
          });

          if (!response.ok) {
            throw new Error('Failed to complete task');
          }

          const data = await response.json();

          // Update local state
          set(state => {
            const updatedDailyTasks = state.dailyTasks.map(task =>
              task.id === taskId 
                ? { ...task, completed: true, completed_at: new Date().toISOString() }
                : task
            );

            const updatedWeeklyTask = state.weeklyTask && state.weeklyTask.id === taskId
              ? { ...state.weeklyTask, completed: true, completed_at: new Date().toISOString() }
              : state.weeklyTask;

            return {
              dailyTasks: updatedDailyTasks,
              weeklyTask: updatedWeeklyTask,
            };
          });

          return true;
        } catch (error) {
          set({ error: error instanceof Error ? error.message : 'Failed to complete task' });
          return false;
        }
      },

      clearError: () => {
        set({ error: null });
      },
    }),
    {
      name: 'task-store',
      storage: createJSONStorage(() => AsyncStorage),
      partialize: (state) => ({
        dailyTasks: state.dailyTasks,
        weeklyTask: state.weeklyTask,
      }),
    }
  )
);