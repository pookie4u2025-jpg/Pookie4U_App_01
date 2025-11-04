import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import { notificationManager } from '../utils/NotificationManager';
import { useGameStore } from './useGameStore';

// Import AsyncStorage conditionally to avoid SSR issues
let AsyncStorage: any = null;
try {
  AsyncStorage = require('@react-native-async-storage/async-storage').default;
} catch (error) {
  // AsyncStorage not available (e.g., during SSR)
  console.log('AsyncStorage not available during initialization');
}

const BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL || '';

interface User {
  id: string;
  email: string;
  name: string;
  relationship_mode: string;
  partner_profile: PartnerProfile;
  total_points: number;
  current_level: number;
  current_streak: number;
  longest_streak: number;
  tasks_completed: number;
  badges: string[];
  profile_completed: boolean;
  profile_image?: string; // base64 encoded image
  created_at: string;
  updated_at: string;
}

interface PartnerProfile {
  name: string;
  birthday?: string;
  anniversary?: string;
  favorite_color: string;
  favorite_food: string;
  favorite_flower: string;
  favorite_brand: string;
  dress_size: string;
  ring_size: string;
  perfume_preference: string;
  notes: string;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  loading: boolean;
  error: string | null;
  initialized: boolean;
  
  // Actions
  login: (email: string, password: string) => Promise<boolean>;
  register: (email: string, password: string, name: string) => Promise<boolean>;
  loginWithOAuth: (oauthData: any) => Promise<boolean>;
  loginWithEmergentOAuth: (sessionToken: string, userData: any) => Promise<boolean>;
  logout: () => void;
  updateProfile: (profile: Partial<User>) => void;
  updateUserProfile: (profile: { name?: string; email?: string }) => Promise<boolean>;
  fetchProfile: () => Promise<void>;
  updatePartnerProfile: (partner: PartnerProfile) => Promise<boolean>;
  updateRelationshipMode: (mode: string) => Promise<boolean>;
  updateProfileImage: (imageBase64: string) => Promise<boolean>;
  clearError: () => void;
  validateSession: () => Promise<void>;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      loading: false,
      error: null,
      initialized: false,

      login: async (email: string, password: string) => {
        set({ loading: true, error: null });
        try {
          const response = await fetch(`${BACKEND_URL}/api/auth/login`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password }),
          });

          const data = await response.json();
          
          if (!response.ok) {
            throw new Error(data.detail || 'Login failed');
          }

          set({ 
            token: data.access_token,
            isAuthenticated: true,
            loading: false,
            error: null,
            initialized: true
          });

          // Fetch user profile
          await get().fetchProfile();
          
          // OLD USER: Sync game data from backend
          const currentUser = get().user;
          if (currentUser) {
            console.log('👤 Existing user logged in - syncing game data from backend');
            try {
              const gameStore = useGameStore.getState();
              await gameStore.syncFromBackend(currentUser);
              console.log('✅ Game data synced successfully for existing user');
            } catch (error) {
              console.error('⚠️ Failed to sync game data:', error);
            }
          }
          
          // Register for push notifications after successful login
          try {
            const pushToken = await notificationManager.registerForPushNotifications(data.access_token);
            if (pushToken) {
              console.log('✅ Push notifications registered successfully');
            }
          } catch (error) {
            console.error('Failed to register push notifications:', error);
            // Don't fail login if push notification registration fails
          }
          
          return true;
        } catch (error) {
          set({ 
            loading: false, 
            error: error instanceof Error ? error.message : 'Login failed',
            isAuthenticated: false,
            token: null
          });
          return false;
        }
      },

      register: async (email: string, password: string, name: string) => {
        set({ loading: true, error: null });
        try {
          const response = await fetch(`${BACKEND_URL}/api/auth/register`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password, name }),
          });

          const data = await response.json();
          
          if (!response.ok) {
            throw new Error(data.detail || 'Registration failed');
          }

          set({ 
            token: data.access_token,
            isAuthenticated: true,
            loading: false,
            error: null,
            initialized: true
          });

          // Fetch user profile
          await get().fetchProfile();
          
          // For NEW users, reset game data to ensure clean start
          console.log('🆕 New user registered - resetting game data to initial values');
          try {
            const gameStore = useGameStore.getState();
            await gameStore.resetGameData();
            console.log('✅ Game data reset successful for new user');
          } catch (error) {
            console.error('⚠️ Failed to reset game data:', error);
            // Continue anyway - not critical for auth
          }
          
          // Register for push notifications after successful registration
          try {
            const pushToken = await notificationManager.registerForPushNotifications(data.access_token);
            if (pushToken) {
              console.log('✅ Push notifications registered successfully');
            }
          } catch (error) {
            console.error('Failed to register push notifications:', error);
            // Don't fail registration if push notification registration fails
          }
          
          return true;
        } catch (error) {
          set({ 
            loading: false, 
            error: error instanceof Error ? error.message : 'Registration failed',
            isAuthenticated: false,
            token: null
          });
          return false;
        }
      },

      loginWithOAuth: async (oauthData: any) => {
        set({ loading: true, error: null });
        try {
          const { access_token, user, is_new_user } = oauthData;
          
          if (!access_token || !user) {
            throw new Error('Invalid OAuth response from server');
          }

          // Store token and user data
          const userData = {
            id: user.id,
            email: user.email,
            name: user.name,
            relationship_mode: user.relationship_mode,
            partner_profile: user.partner_profile || {},
            total_points: user.total_points || 0,
            current_level: user.current_level || 1,
            current_streak: user.current_streak || 0,
            longest_streak: user.longest_streak || 0,
            tasks_completed: user.tasks_completed || 0,
            badges: user.badges || [],
            profile_completed: user.profile_completed || false,
            profile_image: user.profile_image,
            created_at: user.created_at || new Date().toISOString(),
            updated_at: user.updated_at || new Date().toISOString(),
          };

          set({
            user: userData,
            token: access_token,
            isAuthenticated: true,
            loading: false,
            error: null,
            initialized: true,
          });

          // Register for push notifications after successful OAuth login
          try {
            const pushToken = await notificationManager.registerForPushNotifications(access_token);
            if (pushToken) {
              console.log('✅ Push notifications registered successfully');
            }
          } catch (error) {
            console.error('Failed to register push notifications:', error);
            // Don't fail OAuth login if push notification registration fails
          }

          return true;
        } catch (error) {
          set({ 
            loading: false, 
            error: error instanceof Error ? error.message : 'OAuth login failed',
            isAuthenticated: false,
            token: null
          });
          return false;
        }
      },

      loginWithEmergentOAuth: async (sessionToken: string, userData: any) => {
        set({ loading: true, error: null });
        try {
          console.log('🔐 Logging in with Emergent OAuth...');
          
          if (!sessionToken || !userData) {
            throw new Error('Invalid Emergent OAuth data');
          }

          // Store session token and user data
          const userProfile = {
            id: userData.id,
            email: userData.email,
            name: userData.name,
            relationship_mode: userData.relationship_mode || 'SAME_HOME',
            partner_profile: userData.partner_profile || {},
            total_points: userData.total_points || 0,
            current_level: userData.current_level || 1,
            current_streak: userData.current_streak || 0,
            longest_streak: userData.longest_streak || 0,
            tasks_completed: userData.tasks_completed || 0,
            badges: userData.badges || [],
            profile_completed: userData.profile_completed || false,
            profile_image: userData.picture,
            created_at: userData.created_at || new Date().toISOString(),
            updated_at: userData.updated_at || new Date().toISOString(),
          };

          set({
            user: userProfile,
            token: sessionToken, // Store session_token as token
            isAuthenticated: true,
            loading: false,
            error: null,
            initialized: true,
          });

          console.log('✅ Emergent OAuth login successful');

          // Handle game data based on user type
          const gameStore = useGameStore.getState();
          
          if (!userProfile.profile_completed) {
            // NEW USER: Reset game data to ensure clean start
            console.log('🆕 New user detected - resetting game data to initial values');
            try {
              await gameStore.resetGameData();
              console.log('✅ Game data reset successful for new user');
            } catch (error) {
              console.error('⚠️ Failed to reset game data:', error);
            }
          } else {
            // OLD USER: Sync existing data from backend
            console.log('👤 Existing user detected - syncing game data from backend');
            try {
              await gameStore.syncFromBackend(userData);
              console.log('✅ Game data synced successfully for existing user');
            } catch (error) {
              console.error('⚠️ Failed to sync game data:', error);
            }
          }

          // Register for push notifications after successful login
          try {
            const pushToken = await notificationManager.registerForPushNotifications(sessionToken);
            if (pushToken) {
              console.log('✅ Push notifications registered successfully');
            }
          } catch (error) {
            console.error('Failed to register push notifications:', error);
            // Don't fail login if push notification registration fails
          }

          return true;
        } catch (error) {
          console.error('❌ Emergent OAuth login error:', error);
          set({ 
            loading: false, 
            error: error instanceof Error ? error.message : 'Emergent OAuth login failed',
            isAuthenticated: false,
            token: null
          });
          return false;
        }
      },

      logout: () => {
        console.log('🚪 Logging out user...');
        
        // Clear auth state
        set({
          user: null,
          token: null,
          isAuthenticated: false,
          loading: false,
          error: null,
          initialized: true, // Keep initialized as true after logout
        });
        
        // Clear onboarding state so user can see onboarding again if they're a new user next time
        const { resetOnboarding } = require('./useAppStore').useAppStore.getState();
        resetOnboarding();
        
        console.log('✅ Logout complete');
      },

      fetchProfile: async () => {
        const { token } = get();
        if (!token) {
          console.log('No token available for profile fetch');
          return;
        }

        try {
          const response = await fetch(`${BACKEND_URL}/api/user/profile`, {
            headers: {
              'Authorization': `Bearer ${token}`,
            },
          });

          if (!response.ok) {
            if (response.status === 401 || response.status === 403) {
              // Token is invalid or expired, clear auth state
              console.log('Token invalid, clearing auth state');
              get().logout();
              return;
            }
            throw new Error(`Failed to fetch profile: ${response.status}`);
          }

          const user = await response.json();
          set({ user, error: null });
          
          // Check if partner profile exists and complete onboarding if it does
          if (user.partner_profile && user.partner_profile.name) {
            console.log('✅ Partner profile exists, marking onboarding as completed');
            const { completeOnboarding } = require('./useAppStore').useAppStore.getState();
            completeOnboarding();
          } else {
            console.log('⚠️ No partner profile found, onboarding needed');
          }
        } catch (error) {
          console.error('Failed to fetch profile:', error);
          
          // If it's a network error, don't clear the auth state
          if (error instanceof TypeError && error.message.includes('Failed to fetch')) {
            console.log('Network error when fetching profile');
            set({ error: 'Network error. Please check your connection.' });
          } else {
            set({ error: 'Failed to fetch profile' });
          }
        }
      },

      updateProfile: (profile: Partial<User>) => {
        set(state => ({
          user: state.user ? { ...state.user, ...profile } : null
        }));
      },

      updatePartnerProfile: async (partner: PartnerProfile) => {
        const { token } = get();
        if (!token) return false;

        try {
          const response = await fetch(`${BACKEND_URL}/api/user/partner-profile`, {
            method: 'PUT',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${token}`,
            },
            body: JSON.stringify(partner),
          });

          if (!response.ok) {
            throw new Error('Failed to update partner profile');
          }

          // Update local state
          set(state => ({
            user: state.user ? {
              ...state.user,
              partner_profile: partner,
              profile_completed: true
            } : null
          }));

          return true;
        } catch (error) {
          set({ error: 'Failed to update partner profile' });
          return false;
        }
      },

      updateUserProfile: async (profile: { name?: string; email?: string }) => {
        const { token } = get();
        if (!token) {
          console.log('❌ No token available for profile update');
          return false;
        }

        try {
          console.log('📤 Updating user profile:', profile);
          const response = await fetch(`${BACKEND_URL}/api/user/profile`, {
            method: 'PUT',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${token}`,
            },
            body: JSON.stringify(profile),
          });

          console.log('📥 Profile update response status:', response.status);

          if (!response.ok) {
            const errorText = await response.text();
            console.error('❌ Profile update failed:', response.status, errorText);
            
            // Handle 401 authentication error
            if (response.status === 401 || response.status === 403) {
              console.log('❌ Token expired, user needs to re-login');
              set({ error: 'Session expired. Please log in again.' });
              // Don't auto-logout here, let the user know
            }
            
            throw new Error(`Failed to update user profile: ${response.status}`);
          }

          const result = await response.json();
          console.log('✅ Profile updated successfully:', result);

          // Update local state
          set(state => ({
            user: state.user ? {
              ...state.user,
              ...profile
            } : null
          }));

          return true;
        } catch (error) {
          console.error('❌ Profile update error:', error);
          set({ error: 'Failed to update user profile' });
          return false;
        }
      },

      updateRelationshipMode: async (mode: string) => {
        const { token } = get();
        if (!token) return false;

        try {
          console.log('Updating relationship mode to:', mode);
          console.log('Backend URL:', BACKEND_URL);
          
          const response = await fetch(`${BACKEND_URL}/api/user/relationship-mode`, {
            method: 'PUT',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${token}`,
            },
            body: JSON.stringify({ mode }),
          });

          console.log('Response status:', response.status);
          const responseText = await response.text();
          console.log('Response text:', responseText);
          
          if (!response.ok) {
            throw new Error(`Failed to update relationship mode: ${response.status} - ${responseText}`);
          }

          // Try to parse JSON only if response is ok and has content
          if (responseText.trim()) {
            try {
              const responseData = JSON.parse(responseText);
              console.log('Parsed response data:', responseData);
            } catch (parseError) {
              console.error('JSON Parse Error:', parseError, 'Response:', responseText);
              throw new Error('Invalid JSON response from server');
            }
          }

          // Update local state
          set(state => ({
            user: state.user ? {
              ...state.user,
              relationship_mode: mode
            } : null
          }));

          return true;
        } catch (error) {
          set({ error: 'Failed to update relationship mode' });
          return false;
        }
      },

      updateProfileImage: async (imageBase64: string) => {
        const { token } = get();
        if (!token) return false;

        try {
          const response = await fetch(`${BACKEND_URL}/api/user/profile-image`, {
            method: 'PUT',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${token}`,
            },
            body: JSON.stringify({ profile_image: imageBase64 }),
          });

          if (!response.ok) {
            throw new Error('Failed to update profile image');
          }

          // Update local state
          set(state => ({
            user: state.user ? {
              ...state.user,
              profile_image: imageBase64
            } : null
          }));

          return true;
        } catch (error) {
          set({ error: 'Failed to update profile image' });
          return false;
        }
      },

      clearError: () => {
        set({ error: null });
      },

      validateSession: async () => {
        const { token, isAuthenticated } = get();
        
        console.log('🔐 Validating session...', { hasToken: !!token, isAuthenticated });
        
        // If no token or not authenticated, mark as initialized and return
        if (!token || !isAuthenticated) {
          console.log('⚠️ No token or not authenticated, clearing state');
          set({ initialized: true, isAuthenticated: false });
          return;
        }

        try {
          console.log('📡 Fetching profile to validate token...');
          // Try to fetch profile to validate the token
          const response = await fetch(`${BACKEND_URL}/api/user/profile`, {
            headers: {
              'Authorization': `Bearer ${token}`,
            },
            timeout: 5000, // 5 second timeout
          });

          if (response.ok) {
            // Token is valid, fetch and update user profile
            const user = await response.json();
            console.log('✅ Session valid, user authenticated');
            set({ 
              user, 
              initialized: true, 
              isAuthenticated: true,
              error: null 
            });
          } else if (response.status === 401 || response.status === 403) {
            // Token is invalid or expired, clear auth state
            console.log('❌ Token validation failed (401/403), clearing auth state');
            set({
              user: null,
              token: null,
              isAuthenticated: false,
              initialized: true,
              error: null
            });
          } else {
            // Other error, KEEP current auth state (don't logout on server errors)
            console.log('⚠️ Profile fetch failed with status:', response.status, '- Keeping auth state');
            set({ initialized: true }); // Keep user logged in
          }
        } catch (error) {
          console.error('⚠️ Session validation error (network issue?):', error);
          // Network error, KEEP current auth state (don't logout on network errors)
          // This ensures users stay logged in even with poor connectivity
          console.log('🔄 Network error - Keeping user logged in');
          set({ initialized: true }); // Keep user logged in
        }
      },
    }),
    {
      name: 'auth-store',
      storage: createJSONStorage(() => AsyncStorage),
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated,
      }),
      onRehydrateStorage: () => {
        console.log('🔄 Rehydrating auth store from storage...');
        return (state, error) => {
          if (error) {
            console.error('❌ Failed to rehydrate auth store:', error);
          } else if (state) {
            console.log('✅ Auth store rehydrated:', {
              hasUser: !!state.user,
              hasToken: !!state.token,
              isAuthenticated: state.isAuthenticated,
            });
          }
        };
      },
    }
  )
);