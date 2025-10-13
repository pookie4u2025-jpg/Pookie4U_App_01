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

      logout: () => {
        set({
          user: null,
          token: null,
          isAuthenticated: false,
          loading: false,
          error: null,
          initialized: true, // Keep initialized as true after logout
        });
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
        if (!token) return false;

        try {
          const response = await fetch(`${BACKEND_URL}/api/user/profile`, {
            method: 'PUT',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${token}`,
            },
            body: JSON.stringify(profile),
          });

          if (!response.ok) {
            throw new Error('Failed to update user profile');
          }

          // Update local state
          set(state => ({
            user: state.user ? {
              ...state.user,
              ...profile
            } : null
          }));

          return true;
        } catch (error) {
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
        
        // If no token or not authenticated, mark as initialized and return
        if (!token || !isAuthenticated) {
          set({ initialized: true, isAuthenticated: false });
          return;
        }

        try {
          // Try to fetch profile to validate the token
          const response = await fetch(`${BACKEND_URL}/api/user/profile`, {
            headers: {
              'Authorization': `Bearer ${token}`,
            },
          });

          if (response.ok) {
            // Token is valid, fetch and update user profile
            const user = await response.json();
            set({ 
              user, 
              initialized: true, 
              isAuthenticated: true,
              error: null 
            });
          } else if (response.status === 401 || response.status === 403) {
            // Token is invalid or expired, clear auth state
            console.log('Token validation failed, clearing auth state');
            set({
              user: null,
              token: null,
              isAuthenticated: false,
              initialized: true,
              error: null
            });
          } else {
            // Other error, keep current state but mark as initialized
            console.log('Profile fetch failed with status:', response.status);
            set({ initialized: true });
          }
        } catch (error) {
          console.error('Session validation error:', error);
          // Network error, keep current state but mark as initialized
          set({ initialized: true });
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
    }
  )
);