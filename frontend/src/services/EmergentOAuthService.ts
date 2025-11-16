import * as WebBrowser from 'expo-web-browser';
import * as Linking from 'expo-linking';
import { Platform } from 'react-native';

// Complete the auth session when browser closes (only on native)
try {
  if (Platform.OS !== 'web') {
    WebBrowser.maybeCompleteAuthSession();
  }
} catch (error) {
  console.log('⚠️ Could not complete auth session:', error);
}

export interface EmergentOAuthResult {
  type: 'success' | 'error' | 'dismiss';
  sessionToken?: string;
  user?: any;
  error?: string;
}

class EmergentOAuthService {
  private readonly emergentAuthUrl = 'https://auth.emergentagent.com/';
  private readonly emergentSessionDataUrl = 'https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data';

  /**
   * Get the redirect URL for after authentication
   * This should point to your app's main route (home/dashboard)
   */
  private getRedirectUrl(): string {
    try {
      // Use Expo's linking to create a deep link back to the app
      // This will be something like: exp://192.168.x.x:3000 or your-app://
      const redirectUrl = Linking.createURL('/');
      console.log('🔗 Emergent OAuth Redirect URL:', redirectUrl);
      return redirectUrl;
    } catch (error) {
      console.log('⚠️ Error creating redirect URL:', error);
      // Fallback for web or when Linking fails
      if (Platform.OS === 'web' && typeof window !== 'undefined') {
        try {
          const webUrl = window.location.origin;
          console.log('🌐 Using web origin as redirect:', webUrl);
          return webUrl;
        } catch (webError) {
          console.log('⚠️ Could not access window.location:', webError);
        }
      }
      // Final fallback
      return 'https://pookie-connect.preview.emergentagent.com';
    }
  }

  /**
   * Start Emergent OAuth flow
   * Opens browser to Emergent auth page
   */
  async signIn(): Promise<EmergentOAuthResult> {
    try {
      console.log('🔐 Starting Emergent OAuth flow...');

      const redirectUrl = this.getRedirectUrl();
      const emergentAuthUrl = `${this.emergentAuthUrl}?redirect=${encodeURIComponent(redirectUrl)}`;

      console.log('🚀 Opening auth URL:', emergentAuthUrl);

      // Open browser for OAuth
      const result = await WebBrowser.openAuthSessionAsync(
        emergentAuthUrl,
        redirectUrl
      );

      console.log('📋 OAuth Result:', result);

      if (result.type === 'success') {
        // Extract session_id from the URL fragment
        const url = result.url;
        console.log('✅ OAuth success, URL:', url);

        // Parse session_id from URL fragment (#session_id=xxx)
        const sessionId = this.extractSessionId(url);

        if (sessionId) {
          console.log('🎫 Session ID found, exchanging for session data...');
          
          // Exchange session_id for user data and session_token
          const sessionData = await this.exchangeSessionId(sessionId);
          
          return {
            type: 'success',
            sessionToken: sessionData.session_token,
            user: sessionData.user,
          };
        } else {
          console.error('❌ No session_id found in URL');
          return {
            type: 'error',
            error: 'No session ID received from authentication',
          };
        }
      } else if (result.type === 'dismiss' || result.type === 'cancel') {
        console.log('⚠️ OAuth dismissed/cancelled by user');
        return {
          type: 'dismiss',
        };
      } else {
        console.error('❌ OAuth error:', result);
        return {
          type: 'error',
          error: 'Authentication failed',
        };
      }
    } catch (error) {
      console.error('❌ Emergent OAuth Error:', error);
      return {
        type: 'error',
        error: error instanceof Error ? error.message : 'Unknown error occurred',
      };
    }
  }

  /**
   * Extract session_id from URL fragment
   * URL format: your-app://#session_id=xxx
   */
  private extractSessionId(url: string): string | null {
    try {
      // Check if URL has a fragment (#)
      if (url.includes('#session_id=')) {
        const fragment = url.split('#')[1];
        const params = new URLSearchParams(fragment);
        return params.get('session_id');
      }

      // Also try query parameter format
      if (url.includes('?session_id=') || url.includes('&session_id=')) {
        const urlObj = new URL(url);
        return urlObj.searchParams.get('session_id');
      }

      return null;
    } catch (error) {
      console.error('Error extracting session_id:', error);
      return null;
    }
  }

  /**
   * Exchange session_id for session_token and user data
   * Calls backend which in turn calls Emergent's session data endpoint
   */
  private async exchangeSessionId(sessionId: string): Promise<any> {
    try {
      const backendUrl = process.env.EXPO_PUBLIC_BACKEND_URL || '';

      console.log('📡 Calling backend session data endpoint...');

      const response = await fetch(`${backendUrl}/api/auth/emergent/session-data`, {
        method: 'GET',
        headers: {
          'X-Session-ID': sessionId,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Session validation failed');
      }

      const data = await response.json();
      console.log('✅ Session data received from backend');

      return data;
    } catch (error) {
      console.error('Session exchange error:', error);
      throw error;
    }
  }

  /**
   * Check if user has an existing session
   * This can be called on app startup
   */
  async checkExistingSession(sessionToken: string): Promise<any> {
    try {
      const backendUrl = process.env.EXPO_PUBLIC_BACKEND_URL || '';

      const response = await fetch(`${backendUrl}/api/auth/me`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${sessionToken}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        return null;
      }

      return await response.json();
    } catch (error) {
      console.error('Check session error:', error);
      return null;
    }
  }

  /**
   * Logout user by deleting session
   */
  async logout(sessionToken: string): Promise<boolean> {
    try {
      const backendUrl = process.env.EXPO_PUBLIC_BACKEND_URL || '';

      const response = await fetch(`${backendUrl}/api/auth/logout`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${sessionToken}`,
          'Content-Type': 'application/json',
        },
      });

      return response.ok;
    } catch (error) {
      console.error('Logout error:', error);
      return false;
    }
  }
}

// Export singleton instance
export const emergentOAuthService = new EmergentOAuthService();

// Hook for React components
export const useEmergentOAuth = () => {
  const signIn = async (): Promise<EmergentOAuthResult> => {
    return await emergentOAuthService.signIn();
  };

  const checkExistingSession = async (sessionToken: string) => {
    return await emergentOAuthService.checkExistingSession(sessionToken);
  };

  const logout = async (sessionToken: string) => {
    return await emergentOAuthService.logout(sessionToken);
  };

  return {
    signIn,
    checkExistingSession,
    logout,
  };
};

export default emergentOAuthService;
