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

interface AppState {
  // Onboarding and setup
  onboardingCompleted: boolean;
  currentOnboardingStep: number;
  
  // App settings
  notificationsEnabled: boolean;
  reminderTime: string;
  theme: 'light' | 'dark';
  
  // Actions
  completeOnboarding: () => void;
  setOnboardingStep: (step: number) => void;
  resetOnboarding: () => void;
  updateSettings: (settings: Partial<Pick<AppState, 'notificationsEnabled' | 'reminderTime' | 'theme'>>) => void;
}

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      onboardingCompleted: false,
      currentOnboardingStep: 0,
      notificationsEnabled: true,
      reminderTime: '09:00',
      theme: 'light',

      completeOnboarding: () => {
        set({ 
          onboardingCompleted: true,
          currentOnboardingStep: 0
        });
      },

      setOnboardingStep: (step: number) => {
        set({ currentOnboardingStep: step });
      },

      resetOnboarding: () => {
        set({ 
          onboardingCompleted: false,
          currentOnboardingStep: 0
        });
      },

      updateSettings: (settings) => {
        set(state => ({ ...state, ...settings }));
      },
    }),
    {
      name: 'app-store',
      storage: createJSONStorage(() => AsyncStorage),
    }
  )
);