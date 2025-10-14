import * as AuthSession from 'expo-auth-session';
import * as WebBrowser from 'expo-web-browser';
import { Platform } from 'react-native';

// Complete the auth session when browser closes
WebBrowser.maybeCompleteAuthSession();

// Google OAuth configuration
const GOOGLE_CLIENT_ID = ''; // This will be set when user provides credentials
const GOOGLE_CLIENT_SECRET = ''; // This will be set when user provides credentials

// Discovery endpoint for Google OAuth
const discovery = {
  authorizationEndpoint: 'https://accounts.google.com/o/oauth2/v2/auth',
  tokenEndpoint: 'https://oauth2.googleapis.com/token',
  revocationEndpoint: 'https://oauth2.googleapis.com/revoke',
};

export interface GoogleOAuthConfig {
  clientId: string;
  clientSecret?: string;
}

export interface GoogleOAuthResult {
  type: 'success' | 'error' | 'dismiss';
  idToken?: string;
  accessToken?: string;
  error?: string;
}

class GoogleOAuthService {
  private config: GoogleOAuthConfig | null = null;
  private authRequest: AuthSession.AuthRequest | null = null;

  /**
   * Initialize Google OAuth with configuration
   */
  initialize(config: GoogleOAuthConfig) {
    this.config = config;
  }

  /**
   * Create authentication request
   */
  private async createAuthRequest(): Promise<AuthSession.AuthRequest> {
    if (!this.config) {
      throw new Error('Google OAuth not initialized. Call initialize() first.');
    }

    // IMPORTANT: Use Expo's auth proxy to get an HTTPS redirect URI
    // Google OAuth only accepts http/https, not exp://
    const redirectUri = AuthSession.makeRedirectUri({
      native: 'exp://pookie-couples.ngrok.io/--/redirect',
      useProxy: true, // This creates an https://auth.expo.io URL
    });

    console.log('OAuth Redirect URI:', redirectUri);
    console.log('Platform:', Platform.OS);

    // Create auth request - Use Code flow (not IdToken) to avoid PKCE issues
    const request = new AuthSession.AuthRequest({
      clientId: this.config.clientId,
      scopes: ['openid', 'profile', 'email'],
      responseType: AuthSession.ResponseType.Code, // Changed from IdToken to Code
      redirectUri,
      usePKCE: false, // Explicitly disable PKCE to avoid the error
      // Additional parameters for better UX
      extraParams: {
        access_type: 'offline',
        prompt: 'select_account', // Always show account selector
      },
    });

    return request;
  }

  /**
   * Start Google OAuth flow
   */
  async signIn(): Promise<GoogleOAuthResult> {
    try {
      if (!this.config) {
        return {
          type: 'error',
          error: 'Google OAuth not initialized. Call initialize() first.',
        };
      }

      console.log('🔐 Creating auth request...');
      
      // Create auth request
      this.authRequest = await this.createAuthRequest();

      console.log('🚀 Prompting user for OAuth...');

      // Start the authentication flow using promptAsync
      const result = await this.authRequest.promptAsync(discovery);

      console.log('📋 OAuth Result:', result);

      if (result.type === 'success') {
        // With Code flow, we get an authorization code instead of direct tokens
        const { code } = result.params;
        
        console.log('✅ OAuth success, authorization code present:', !!code);
        
        if (code) {
          // Exchange authorization code for tokens
          const tokenResult = await AuthSession.exchangeCodeAsync(
            {
              clientId: this.config.clientId,
              code,
              redirectUri: this.authRequest.redirectUri,
              extraParams: {
                client_secret: this.config.clientSecret || '',
              },
            },
            discovery
          );

          console.log('🎫 Token exchange successful');

          return {
            type: 'success',
            idToken: tokenResult.idToken || undefined,
            accessToken: tokenResult.accessToken,
          };
        } else {
          return {
            type: 'error',
            error: 'No authorization code received from Google',
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
      console.error('❌ Google OAuth Error:', error);
      return {
        type: 'error',
        error: error instanceof Error ? error.message : 'Unknown error occurred',
      };
    }
  }

  /**
   * Exchange ID token with backend
   */
  async authenticateWithBackend(idToken: string, accessToken?: string): Promise<any> {
    try {
      const backendUrl = process.env.EXPO_PUBLIC_BACKEND_URL || '';
      
      const response = await fetch(`${backendUrl}/api/auth/oauth/google`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          provider: 'google',
          id_token: idToken,
          access_token: accessToken,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Backend authentication failed');
      }

      return await response.json();
    } catch (error) {
      console.error('Backend OAuth Error:', error);
      throw error;
    }
  }

  /**
   * Complete OAuth flow (sign in + backend authentication)
   */
  async completeOAuthFlow(): Promise<any> {
    const oauthResult = await this.signIn();

    if (oauthResult.type === 'success' && oauthResult.idToken) {
      return await this.authenticateWithBackend(
        oauthResult.idToken,
        oauthResult.accessToken
      );
    } else {
      throw new Error(oauthResult.error || 'OAuth flow failed');
    }
  }

  /**
   * Check if Google OAuth is configured
   */
  isConfigured(): boolean {
    return this.config !== null && !!this.config.clientId;
  }

  /**
   * Get current configuration
   */
  getConfig(): GoogleOAuthConfig | null {
    return this.config;
  }
}

// Export singleton instance
export const googleOAuthService = new GoogleOAuthService();

// Hook for React components
export const useGoogleOAuth = () => {
  const signIn = async (): Promise<GoogleOAuthResult> => {
    return await googleOAuthService.signIn();
  };

  const authenticateWithBackend = async (idToken: string, accessToken?: string) => {
    return await googleOAuthService.authenticateWithBackend(idToken, accessToken);
  };

  const completeOAuthFlow = async () => {
    return await googleOAuthService.completeOAuthFlow();
  };

  return {
    signIn,
    authenticateWithBackend,
    completeOAuthFlow,
    isConfigured: googleOAuthService.isConfigured(),
    initialize: googleOAuthService.initialize.bind(googleOAuthService),
  };
};

export default googleOAuthService;