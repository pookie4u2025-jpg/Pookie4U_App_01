import * as AppleAuthentication from 'expo-apple-authentication';
import Constants from 'expo-constants';

export interface AppleOAuthCredential {
  identityToken: string;
  authorizationCode: string;
  user: string;
  email?: string;
  fullName?: {
    givenName?: string;
    familyName?: string;
  };
}

export interface AppleOAuthConfig {
  backendUrl?: string;
}

export class AppleOAuthService {
  private backendUrl: string;

  constructor(config: AppleOAuthConfig = {}) {
    this.backendUrl = config.backendUrl || Constants.expoConfig?.extra?.backendUrl || 'http://localhost:8001';
  }

  /**
   * Check if Apple Sign-In is available on this device
   */
  async isAvailable(): Promise<boolean> {
    try {
      return await AppleAuthentication.isAvailableAsync();
    } catch (error) {
      console.warn('Error checking Apple Sign-In availability:', error);
      return false;
    }
  }

  /**
   * Initiate Apple Sign-In flow
   */
  async signIn(): Promise<AppleOAuthCredential> {
    try {
      // Check if Apple Sign-In is available
      const available = await this.isAvailable();
      if (!available) {
        throw new Error('Apple Sign-In is not available on this device');
      }

      // Start Apple Sign-In flow
      const credential = await AppleAuthentication.signInAsync({
        requestedScopes: [
          AppleAuthentication.AppleAuthenticationScope.FULL_NAME,
          AppleAuthentication.AppleAuthenticationScope.EMAIL,
        ],
      });

      // Validate required fields
      if (!credential.identityToken || !credential.authorizationCode || !credential.user) {
        throw new Error('Incomplete credentials received from Apple');
      }

      return {
        identityToken: credential.identityToken,
        authorizationCode: credential.authorizationCode,
        user: credential.user,
        email: credential.email || undefined,
        fullName: credential.fullName ? {
          givenName: credential.fullName.givenName || undefined,
          familyName: credential.fullName.familyName || undefined,
        } : undefined,
      };

    } catch (error) {
      if (error.code === 'ERR_REQUEST_CANCELED') {
        throw new Error('Sign-in was cancelled by user');
      } else if (error.code === 'ERR_REQUEST_FAILED') {
        throw new Error('Apple Sign-In request failed');
      } else {
        throw new Error(`Apple Sign-In failed: ${error.message || 'Unknown error'}`);
      }
    }
  }

  /**
   * Send Apple credentials to backend for verification and session creation
   */
  async authenticateWithBackend(credential: AppleOAuthCredential): Promise<{
    success: boolean;
    sessionToken?: string;
    user?: any;
    message?: string;
  }> {
    try {
      const response = await fetch(`${this.backendUrl}/api/auth/apple/signin`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(credential),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || data.message || 'Authentication failed');
      }

      return data;

    } catch (error) {
      if (error instanceof TypeError && error.message.includes('Network request failed')) {
        throw new Error('Unable to connect to authentication server');
      }
      throw error;
    }
  }

  /**
   * Complete Apple OAuth flow (sign in + backend authentication)
   */
  async completeOAuthFlow(): Promise<{
    success: boolean;
    sessionToken?: string;
    user?: any;
    message?: string;
    isNewUser?: boolean;
  }> {
    try {
      console.log('🍎 Starting Apple OAuth flow...');

      // Step 1: Get credentials from Apple
      const credential = await this.signIn();
      console.log('✅ Apple credentials obtained');

      // Step 2: Send to backend for verification
      const backendResponse = await this.authenticateWithBackend(credential);
      console.log('✅ Backend authentication completed');

      return {
        ...backendResponse,
        isNewUser: credential.email !== null, // Apple only provides email on first sign-in
      };

    } catch (error) {
      console.error('❌ Apple OAuth flow failed:', error);
      throw error;
    }
  }

  /**
   * Get the current authentication state (for checking if Apple Sign-In is configured)
   */
  async getAuthenticationState(): Promise<{
    isAvailable: boolean;
    isConfigured: boolean;
  }> {
    const isAvailable = await this.isAvailable();
    
    // In production, you might check for proper App ID configuration
    // For now, we assume it's configured if it's available
    const isConfigured = isAvailable;

    return {
      isAvailable,
      isConfigured,
    };
  }
}

// Export singleton instance
export const appleOAuthService = new AppleOAuthService();

// Export hook for React components
export const useAppleOAuth = () => {
  return {
    signIn: () => appleOAuthService.signIn(),
    completeOAuthFlow: () => appleOAuthService.completeOAuthFlow(),
    isAvailable: () => appleOAuthService.isAvailable(),
    getAuthenticationState: () => appleOAuthService.getAuthenticationState(),
  };
};