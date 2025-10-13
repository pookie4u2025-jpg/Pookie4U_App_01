import React, { useState, useCallback, useEffect } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Alert,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
  ActivityIndicator,
  Pressable,
  Dimensions,
  StatusBar,
  SafeAreaView,
  Image,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';
import * as Haptics from 'expo-haptics';
import { useAuthStore } from '../stores/useAuthStore';
import { useTheme } from '../contexts/ThemeContext';
import { useGoogleOAuth } from '../services/GoogleOAuthService';

const { width, height } = Dimensions.get('window');

export default function AuthScreen() {
  const [currentScreen, setCurrentScreen] = useState<'welcome' | 'login' | 'register' | 'signup-options'>('welcome');
  const [registrationMethod, setRegistrationMethod] = useState<'email' | null>(null);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [name, setName] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const { login, register, loading, error, clearError, loginWithOAuth } = useAuthStore();
  const { theme } = useTheme();
  const { completeOAuthFlow, initialize: initializeGoogleOAuth, isConfigured } = useGoogleOAuth();

  // Initialize Google OAuth when component mounts
  useEffect(() => {
    // For now, Google OAuth is not configured until user provides credentials
    // This will be updated once the user provides their Google Client ID
    const googleClientId = process.env.EXPO_PUBLIC_GOOGLE_CLIENT_ID || '';
    
    if (googleClientId) {
      initializeGoogleOAuth({
        clientId: googleClientId,
      });
      console.log('✅ Google OAuth initialized with client ID');
    } else {
      console.log('⚠️ Google OAuth credentials not configured');
    }
  }, [initializeGoogleOAuth]);

  // Navigate between screens with haptic feedback
  const navigateToScreen = useCallback((screen: 'welcome' | 'login' | 'register' | 'signup-options', method?: 'email' | 'mobile') => {
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    setCurrentScreen(screen);
    if (method) {
      setRegistrationMethod(method);
    } else if (screen === 'login') {
      setRegistrationMethod(null); // Reset to show options
    }
    clearError();
  }, [clearError]);

  // Enhanced authentication handlers optimized for mobile UX
  const handleLogin = useCallback(async () => {
    if (!email?.trim() || !password) {
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);
      Alert.alert('Missing Information', 'Please fill in all fields to continue.');
      return;
    }
    
    try {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
      await login(email.trim().toLowerCase(), password);
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
    } catch (error) {
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);
      console.error('Login failed:', error);
    }
  }, [email, password, login]);

  const handleRegister = useCallback(async () => {
    if (!name?.trim() || !email?.trim() || !password || !confirmPassword) {
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);
      Alert.alert('Missing Information', 'Please fill in all fields to create your account.');
      return;
    }
    
    if (password !== confirmPassword) {
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);
      Alert.alert('Password Mismatch', 'Please make sure your passwords match.');
      return;
    }
    
    if (password.length < 6) {
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);
      Alert.alert('Weak Password', 'Password must be at least 6 characters long.');
      return;
    }
    
    try {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
      await register(name.trim(), email.trim().toLowerCase(), password);
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
    } catch (error) {
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);
      console.error('Registration failed:', error);
    }
  }, [name, email, password, confirmPassword, register]);

  // Removed mobile/OTP functions - keeping only Email + Google OAuth

  const handleVerifyOTP = useCallback(async () => {
    if (!otp || otp.length !== 6) {
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);
      Alert.alert('Invalid OTP', 'Please enter the complete 6-digit verification code.');
      return;
    }
    
    try {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
      // Mock OTP verification - in production, verify with backend
      console.log('Verifying OTP:', otp);
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
      Alert.alert('Verified! ✅', 'Your phone number has been successfully verified.');
    } catch (error) {
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);
      Alert.alert('Verification Failed', 'Invalid OTP. Please check and try again.');
      console.error('Verify OTP failed:', error);
    }
  }, [otp]);

  const handleGoogleSignIn = useCallback(async () => {
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
    
    // Check if Google OAuth is configured
    if (!isConfigured) {
      Alert.alert(
        'Google Sign-In Setup Required 🔧',
        'Google OAuth credentials are not configured. Please contact the developer to enable Google Sign-In.',
        [{ text: 'OK', style: 'default' }]
      );
      return;
    }

    try {
      console.log('🚀 Starting Google OAuth flow...');
      
      // Start OAuth flow and get backend response
      const oauthData = await completeOAuthFlow();
      
      console.log('✅ OAuth flow completed, authenticating with app...');
      
      // Login with OAuth data
      const success = await loginWithOAuth(oauthData);
      
      if (success) {
        Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
        console.log('✅ Google Sign-In successful!');
        
        if (oauthData.is_new_user) {
          Alert.alert(
            'Welcome to Pookie4u! 🎉',
            'Your Google account has been successfully linked. Let\'s set up your profile!',
            [{ text: 'Get Started', style: 'default' }]
          );
        }
      } else {
        throw new Error('Failed to authenticate with app after OAuth');
      }
      
    } catch (error) {
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);
      console.error('❌ Google Sign-In error:', error);
      
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
      
      Alert.alert(
        'Sign-In Failed',
        `We couldn't sign you in with Google: ${errorMessage}`,
        [
          { text: 'Try Again', style: 'default' },
          { text: 'Cancel', style: 'cancel' }
        ]
      );
    }
  }, [isConfigured, completeOAuthFlow, loginWithOAuth]);

  const handleAppleSignIn = async () => {
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
    
    try {
      console.log('🍎 Starting Apple Sign-In flow...');
      
      Alert.alert(
        'Apple Sign-In Setup Required 🍎',
        'Apple Sign-In integration is ready but requires:\n\n' +
        '1. Apple Developer Account ($99/year)\n' +
        '2. App ID configuration in Apple Developer Portal\n' +
        '3. Backend Apple OAuth implementation\n\n' +
        'Check the AUTHENTICATION_SETUP_GUIDE.md file for detailed setup instructions.',
        [
          { text: 'View Guide', onPress: () => console.log('📖 Open /app/AUTHENTICATION_SETUP_GUIDE.md for complete setup instructions') },
          { text: 'OK', style: 'default' }
        ]
      );
      
    } catch (error) {
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);
      console.error('❌ Apple Sign-In error:', error);
      
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
      
      Alert.alert(
        'Sign-In Failed',
        `We couldn't sign you in with Apple: ${errorMessage}`,
        [
          { text: 'Try Again', style: 'default' },
          { text: 'Cancel', style: 'cancel' }
        ]
      );
    }
  };

  // Removed handleAuthMethodSwitch - using handleRegistrationMethodSwitch instead

  const handleRegistrationMethodSwitch = (method: 'email' | null) => {
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    setRegistrationMethod(method);
    setEmail('');
    setPassword('');
    setConfirmPassword('');
    clearError();
  };

  // Clean handlers - using individual functions for better mobile UX

  // Note: Using the handler functions declared above to avoid duplicates

  // Render different screens based on current state
  const renderWelcomeScreen = () => (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="transparent" translucent />
      <LinearGradient
        colors={['#FFB6C1', '#FF91A4', '#FF69B4', '#FF1493']}
        start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 1 }}
        style={styles.gradientContainer}
      >
        <SafeAreaView style={styles.container}>
          {/* App Branding - Centered and Prominent */}
          <View style={styles.splashBrandingContainer}>
            <View style={styles.logoContainer}>
              <Image 
                source={require('../../assets/images/logos/p4u-long-logo.png')}
                style={styles.splashLogo}
                resizeMode="contain"
              />
            </View>
            <Text style={styles.splashTagline}>Strengthen your bond with gamified love</Text>
          </View>

          {/* Action Buttons */}
          <View style={styles.splashButtonContainer}>
            <TouchableOpacity
              style={[styles.splashPrimaryButton, { shadowColor: '#FFFFFF' }]}
              onPress={() => navigateToScreen('signup-options')}
              activeOpacity={0.8}
            >
              <Text style={styles.splashPrimaryButtonText}>Create Account</Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={styles.splashSecondaryButton}
              onPress={() => navigateToScreen('login')}
              activeOpacity={0.8}
            >
              <Text style={styles.splashSecondaryButtonText}>Sign In</Text>
            </TouchableOpacity>
          </View>
        </SafeAreaView>
      </LinearGradient>
    </SafeAreaView>
  );

  // Sign-up Options Screen
  const renderSignupOptionsScreen = () => (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="dark-content" backgroundColor="transparent" translucent />
      <View style={styles.cleanContainer}>
        {/* Back Button */}
        <TouchableOpacity
          style={styles.cleanBackButton}
          onPress={() => navigateToScreen('welcome')}
          activeOpacity={0.7}
        >
          <Ionicons name="arrow-back" size={24} color="#333333" />
        </TouchableOpacity>

        {/* Header */}
        <View style={styles.cleanHeader}>
          <Image 
            source={require('../../assets/images/p4u-logo.png')}
            style={styles.shortLogo}
            resizeMode="contain"
          />
          <Text style={styles.cleanTitle}>Create your account</Text>
          <Text style={styles.cleanSubtitle}>Choose how you'd like to sign up</Text>
        </View>

        {/* Sign Up Options - Email + Google Only */}
        <View style={styles.cleanOptionsContainer}>
          {/* Email Address */}
          <TouchableOpacity
            style={styles.cleanOption}
            onPress={() => navigateToScreen('register', 'email')}
            activeOpacity={0.7}
          >
            <View style={styles.cleanOptionIconContainer}>
              <Ionicons name="mail" size={24} color="#FF1493" />
            </View>
            <View style={styles.cleanOptionContent}>
              <Text style={styles.cleanOptionTitle}>Email Address</Text>
              <Text style={styles.cleanOptionDescription}>Create account with email</Text>
            </View>
            <Ionicons name="chevron-forward" size={20} color="#999999" />
          </TouchableOpacity>

          {/* Google Account */}
          <TouchableOpacity
            style={styles.cleanOption}
            onPress={handleGoogleSignIn}
            activeOpacity={0.7}
          >
            <View style={styles.cleanOptionIconContainer}>
              <Ionicons name="logo-google" size={24} color="#4285F4" />
            </View>
            <View style={styles.cleanOptionContent}>
              <Text style={styles.cleanOptionTitle}>Google Account</Text>
              <Text style={styles.cleanOptionDescription}>Continue with Google</Text>
            </View>
            <Ionicons name="chevron-forward" size={20} color="#999999" />
          </TouchableOpacity>
        </View>

        {/* Bottom Link - Fixed at bottom */}
        <View style={styles.cleanBottomContainer}>
          <View style={styles.cleanAlternativeLogin}>
            <Text style={styles.cleanAlternativeText}>Already have an account? </Text>
            <TouchableOpacity onPress={() => navigateToScreen('login')}>
              <Text style={styles.cleanAlternativeLink}>Sign In</Text>
            </TouchableOpacity>
          </View>
        </View>
      </View>
    </SafeAreaView>
  );

  const renderLoginScreen = () => (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="dark-content" backgroundColor="transparent" translucent />
      <KeyboardAvoidingView 
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.cleanContainer}
      >
        <ScrollView 
          contentContainerStyle={styles.cleanScrollContent}
          keyboardShouldPersistTaps="handled"
          showsVerticalScrollIndicator={false}
        >
          {/* Back Button */}
          <TouchableOpacity
            style={styles.cleanBackButton}
            onPress={() => {
              if (registrationMethod === 'email' || registrationMethod === 'mobile') {
                setRegistrationMethod(null);
                setEmail('');
                setPassword('');
                setMobile('');
                setOtp('');
                setShowOtpInput(false);
                clearError();
              } else {
                navigateToScreen('welcome');
              }
            }}
            activeOpacity={0.7}
          >
            <Ionicons name="arrow-back" size={24} color="#333333" />
          </TouchableOpacity>

          {/* Header */}
          <View style={styles.cleanHeader}>
            <Image 
              source={require('../../assets/images/p4u-logo.png')}
              style={styles.shortLogo}
              resizeMode="contain"
            />
            <Text style={styles.cleanTitle}>
              {registrationMethod === 'email' ? 'Sign in with Email' : 
               registrationMethod === 'mobile' ? 'Sign in with Phone' : 'Welcome back!'}
            </Text>
            <Text style={styles.cleanSubtitle}>
              {registrationMethod === 'email' ? 'Enter your email and password' :
               registrationMethod === 'mobile' ? 'Enter your phone number' : 'Choose how you\'d like to sign in'}
            </Text>
          </View>

          {/* Error Display */}
          {error && (
            <View style={styles.cleanErrorContainer}>
              <Ionicons name="alert-circle-outline" size={20} color="#FF4444" />
              <Text style={styles.cleanErrorText}>
                {typeof error === 'string' ? error : error.message || error.detail || 'An error occurred'}
              </Text>
            </View>
          )}

          {/* Email Login Form */}
          {registrationMethod === 'email' && (
            <View style={styles.cleanFormContainer}>
              <View style={styles.cleanInputContainer}>
                <TextInput
                  style={styles.cleanInput}
                  placeholder="Email address"
                  placeholderTextColor="#999999"
                  value={email}
                  onChangeText={setEmail}
                  keyboardType="email-address"
                  autoCapitalize="none"
                  autoCorrect={false}
                />
              </View>

              <View style={styles.cleanInputContainer}>
                <TextInput
                  style={styles.cleanInput}
                  placeholder="Password"
                  placeholderTextColor="#999999"
                  value={password}
                  onChangeText={setPassword}
                  secureTextEntry={!showPassword}
                />
                <TouchableOpacity
                  style={styles.cleanPasswordToggle}
                  onPress={() => setShowPassword(!showPassword)}
                  activeOpacity={0.7}
                >
                  <Ionicons 
                    name={showPassword ? "eye-off-outline" : "eye-outline"} 
                    size={20} 
                    color="#999999" 
                  />
                </TouchableOpacity>
              </View>

              <TouchableOpacity
                style={[styles.cleanSubmitButton, loading && styles.cleanSubmitButtonDisabled]}
                onPress={handleLogin}
                disabled={loading}
                activeOpacity={0.8}
              >
                {loading ? (
                  <ActivityIndicator color="#FFFFFF" />
                ) : (
                  <Text style={styles.cleanSubmitButtonText}>Sign In</Text>
                )}
              </TouchableOpacity>

              {/* Alternative Sign In Method */}
              <View style={styles.cleanDivider}>
                <View style={styles.cleanDividerLine} />
                <Text style={styles.cleanDividerText}>or continue with</Text>
                <View style={styles.cleanDividerLine} />
              </View>

              <TouchableOpacity
                style={styles.cleanMethodSwitchButton}
                onPress={handleGoogleSignIn}
                activeOpacity={0.7}
              >
                <Ionicons name="logo-google" size={20} color="#4285F4" />
                <Text style={styles.cleanMethodSwitchText}>Continue with Google</Text>
              </TouchableOpacity>
            </View>
          )}

          {/* Removed mobile login - keeping only Email + Google OAuth */}

          {/* Sign In Method Selection */}
          {registrationMethod !== 'email' && (
            <View style={styles.cleanOptionsContainer}>
              {/* Email Address */}
              <TouchableOpacity
                style={styles.cleanOption}
                onPress={() => setRegistrationMethod('email')}
                activeOpacity={0.7}
              >
                <View style={styles.cleanOptionIconContainer}>
                  <Ionicons name="mail" size={24} color="#FF1493" />
                </View>
                <View style={styles.cleanOptionContent}>
                  <Text style={styles.cleanOptionTitle}>Email Address</Text>
                  <Text style={styles.cleanOptionDescription}>Sign in with your email</Text>
                </View>
                <Ionicons name="chevron-forward" size={20} color="#999999" />
              </TouchableOpacity>

              {/* Google Account */}
              <TouchableOpacity
                style={styles.cleanOption}
                onPress={handleGoogleSignIn}
                activeOpacity={0.7}
              >
                <View style={styles.cleanOptionIconContainer}>
                  <Ionicons name="logo-google" size={24} color="#4285F4" />
                </View>
                <View style={styles.cleanOptionContent}>
                  <Text style={styles.cleanOptionTitle}>Google Account</Text>
                  <Text style={styles.cleanOptionDescription}>Continue with Google</Text>
                </View>
                <Ionicons name="chevron-forward" size={20} color="#999999" />
              </TouchableOpacity>
            </View>
          )}

          {/* Bottom Link - Fixed at bottom */}
          <View style={styles.cleanBottomContainer}>
            <View style={styles.cleanAlternativeLogin}>
              <Text style={styles.cleanAlternativeText}>Don't have an account? </Text>
              <TouchableOpacity onPress={() => navigateToScreen('signup-options')}>
                <Text style={styles.cleanAlternativeLink}>Sign Up</Text>
              </TouchableOpacity>
            </View>
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );

  const renderRegisterScreen = () => (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="transparent" translucent />
      <LinearGradient
        colors={['#F7D7DA', '#F2C2C7', '#F0B8BE']}
        start={{ x: 0, y: 0 }}
        end={{ x: 0, y: 1 }}
        style={styles.gradientContainer}
      >
        <KeyboardAvoidingView 
          behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
          style={styles.keyboardView}
        >
          <ScrollView 
            contentContainerStyle={styles.scrollContent}
            keyboardShouldPersistTaps="handled"
            showsVerticalScrollIndicator={false}
          >
            {/* Back Button */}
            <TouchableOpacity
              style={styles.backButton}
              onPress={() => navigateToScreen('welcome')}
              activeOpacity={0.7}
            >
              <Ionicons name="arrow-back" size={24} color="#fff" />
            </TouchableOpacity>

            {/* Create Account Form */}
            <View style={styles.formContainer}>
              <Text style={styles.screenTitle}>
                {registrationMethod === 'mobile' ? 'Sign up with Mobile' : 'Sign up with Email'}
              </Text>

              {/* Error Display */}
              {error && (
                <View style={styles.errorContainer}>
                  <Ionicons name="alert-circle-outline" size={20} color="#FFE5E5" />
                  <Text style={styles.errorText}>
                    {typeof error === 'string' ? error : error.message || error.detail || 'An error occurred'}
                  </Text>
                </View>
              )}

              {/* Email Registration */}
              {registrationMethod === 'email' && (
                <View style={styles.formSection}>
                  <View style={styles.inputContainer}>
                    <TextInput
                      style={styles.input}
                      placeholder="Full Name"
                      placeholderTextColor="rgba(255,255,255,0.7)"
                      value={name}
                      onChangeText={setName}
                      autoCapitalize="words"
                    />
                  </View>

                  <View style={styles.inputContainer}>
                    <TextInput
                      style={styles.input}
                      placeholder="Email address"
                      placeholderTextColor="rgba(255,255,255,0.7)"
                      value={email}
                      onChangeText={setEmail}
                      keyboardType="email-address"
                      autoCapitalize="none"
                    />
                  </View>

                  <View style={styles.inputContainer}>
                    <TextInput
                      style={styles.input}
                      placeholder="Password"
                      placeholderTextColor="rgba(255,255,255,0.7)"
                      value={password}
                      onChangeText={setPassword}
                      secureTextEntry
                    />
                  </View>

                  <View style={styles.inputContainer}>
                    <TextInput
                      style={styles.input}
                      placeholder="Confirm Password"
                      placeholderTextColor="rgba(255,255,255,0.7)"
                      value={confirmPassword}
                      onChangeText={setConfirmPassword}
                      secureTextEntry
                    />
                  </View>

                  <TouchableOpacity
                    style={[styles.submitButton, loading && styles.submitButtonDisabled]}
                    onPress={handleRegister}
                    disabled={loading}
                    activeOpacity={0.8}
                  >
                    {loading ? (
                      <ActivityIndicator color="#FF69B4" />
                    ) : (
                      <Text style={styles.submitButtonText}>Create Account</Text>
                    )}
                  </TouchableOpacity>
                </View>
              )}

              {/* Mobile Registration */}
              {registrationMethod === 'mobile' && (
                <View style={styles.formSection}>
                  <Text style={styles.sectionTitle}>Sign up with phone number</Text>
                  
                  <View style={styles.inputContainer}>
                    <TextInput
                      style={styles.input}
                      placeholder="Full Name"
                      placeholderTextColor="rgba(255,255,255,0.7)"
                      value={name}
                      onChangeText={setName}
                      autoCapitalize="words"
                    />
                  </View>
                  
                  {!showOtpInput ? (
                    <>
                      <View style={styles.inputContainer}>
                        <TextInput
                          style={styles.input}
                          placeholder="Mobile Number (+91XXXXXXXXXX)"
                          placeholderTextColor="rgba(255,255,255,0.7)"
                          value={mobile}
                          onChangeText={setMobile}
                          keyboardType="phone-pad"
                        />
                      </View>

                      <TouchableOpacity
                        style={[styles.submitButton, loading && styles.submitButtonDisabled]}
                        onPress={handleSendOTP}
                        disabled={loading}
                        activeOpacity={0.8}
                      >
                        {loading ? (
                          <ActivityIndicator color="#FF69B4" />
                        ) : (
                          <Text style={styles.submitButtonText}>Send OTP</Text>
                        )}
                      </TouchableOpacity>
                    </>
                  ) : (
                    <>
                      <View style={styles.inputContainer}>
                        <TextInput
                          style={styles.input}
                          placeholder="Enter 6-digit OTP"
                          placeholderTextColor="rgba(255,255,255,0.7)"
                          value={otp}
                          onChangeText={setOtp}
                          keyboardType="numeric"
                          maxLength={6}
                        />
                      </View>

                      <TouchableOpacity
                        style={[styles.submitButton, loading && styles.submitButtonDisabled]}
                        onPress={handleMobileRegister}
                        disabled={loading}
                        activeOpacity={0.8}
                      >
                        {loading ? (
                          <ActivityIndicator color="#FF69B4" />
                        ) : (
                          <Text style={styles.submitButtonText}>Verify & Create Account</Text>
                        )}
                      </TouchableOpacity>

                      <TouchableOpacity
                        style={styles.backToMobileButton}
                        onPress={() => setShowOtpInput(false)}
                        activeOpacity={0.7}
                      >
                        <Text style={styles.backToMobileText}>← Back to mobile input</Text>
                      </TouchableOpacity>
                    </>
                  )}
                </View>
              )}

              {/* Toggle Registration Method */}
              {registrationMethod === 'mobile' && (
                <TouchableOpacity
                  style={styles.toggleMethodButton}
                  onPress={() => handleRegistrationMethodSwitch('email')}
                  activeOpacity={0.7}
                >
                  <Text style={styles.toggleMethodText}>Use email instead</Text>
                </TouchableOpacity>
              )}

              {registrationMethod === 'email' && (
                <TouchableOpacity
                  style={styles.toggleMethodButton}
                  onPress={() => handleRegistrationMethodSwitch('mobile')}
                  activeOpacity={0.7}
                >
                  <Text style={styles.toggleMethodText}>Use phone number instead</Text>
                </TouchableOpacity>
              )}

              {/* Already have account */}
              <TouchableOpacity
                style={styles.switchToLoginButton}
                onPress={() => navigateToScreen('login')}
                activeOpacity={0.7}
              >
                <Text style={styles.switchToLoginText}>Already have an account? Sign in</Text>
              </TouchableOpacity>
            </View>
          </ScrollView>
        </KeyboardAvoidingView>
      </LinearGradient>
    </SafeAreaView>
  );

  // Main render method
  return (
    <>
      {currentScreen === 'welcome' && renderWelcomeScreen()}
      {currentScreen === 'signup-options' && renderSignupOptionsScreen()}
      {currentScreen === 'login' && renderLoginScreen()}
      {currentScreen === 'register' && renderRegisterScreen()}
    </>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  gradientContainer: {
    flex: 1,
  },
  content: {
    flex: 1,
    paddingHorizontal: 32,
    paddingTop: 80,
    paddingBottom: 50,
    justifyContent: 'space-between',
  },
  keyboardView: {
    flex: 1,
  },
  scrollContainer: {
    flex: 1,
  },
  scrollContent: {
    flexGrow: 1,
    paddingHorizontal: 32,
    paddingBottom: 50,
  },
  
  // Logo Styles
  longLogo: {
    width: width * 0.8, // 80% of screen width
    height: 120,
    marginBottom: 20,
  },
  shortLogo: {
    width: 80,
    height: 80,
    marginBottom: 20,
  },

  // Splash Screen Styles
  splashBrandingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 40,
  },
  logoContainer: {
    backgroundColor: 'rgba(255, 255, 255, 0.1)',
    borderRadius: 30,
    padding: 30,
    marginBottom: 40,
    shadowColor: '#FFFFFF',
    shadowOffset: {
      width: 0,
      height: 4,
    },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 8,
  },
  splashLogo: {
    width: width * 0.7, // 70% of screen width
    height: 100,
  },
  splashTagline: {
    fontSize: 18,
    fontWeight: '400',
    color: '#FFFFFF',
    textAlign: 'center',
    marginTop: 20,
    opacity: 0.95,
    letterSpacing: 0.5,
    lineHeight: 24,
  },

  // Splash Screen Button Container
  splashButtonContainer: {
    paddingHorizontal: 40,
    paddingBottom: 60,
  },
  splashPrimaryButton: {
    backgroundColor: '#FFFFFF',
    borderRadius: 25,
    paddingVertical: 16,
    paddingHorizontal: 40,
    marginBottom: 16,
    shadowOffset: {
      width: 0,
      height: 3,
    },
    shadowOpacity: 0.3,
    shadowRadius: 6,
    elevation: 6,
  },
  splashPrimaryButtonText: {
    color: '#FF1493',
    fontSize: 18,
    fontWeight: '700',
    textAlign: 'center',
    letterSpacing: 0.5,
  },
  splashSecondaryButton: {
    backgroundColor: 'transparent',
    borderWidth: 2,
    borderColor: '#FFFFFF',
    borderRadius: 25,
    paddingVertical: 16,
    paddingHorizontal: 40,
  },
  splashSecondaryButtonText: {
    color: '#FFFFFF',
    fontSize: 18,
    fontWeight: '600',
    textAlign: 'center',
    letterSpacing: 0.5,
  },

  // Welcome Screen Styles (Legacy)
  brandingContainer: {
    alignItems: 'center',
    marginTop: 60,
  },
  appName: {
    fontSize: 48,
    fontWeight: 'bold',
    color: '#FFFFFF',
    textAlign: 'center',
    marginBottom: 8,
    fontFamily: Platform.OS === 'ios' ? 'System' : 'Roboto',
  },
  tagline: {
    fontSize: 16,
    color: 'rgba(255,255,255,0.9)',
    textAlign: 'center',
    paddingHorizontal: 20,
  },
  legalText: {
    fontSize: 13,
    color: 'rgba(255,255,255,0.8)',
    textAlign: 'center',
    lineHeight: 18,
    paddingHorizontal: 16,
  },
  legalLink: {
    textDecorationLine: 'underline',
  },
  actionButtons: {
    width: '100%',
  },
  primaryButton: {
    backgroundColor: '#FFFFFF',
    borderRadius: 30,
    paddingVertical: 18,
    alignItems: 'center',
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  primaryButtonText: {
    color: '#FF69B4',
    fontSize: 18,
    fontWeight: '600',
  },
  secondaryButton: {
    backgroundColor: 'transparent',
    borderRadius: 30,
    paddingVertical: 18,
    alignItems: 'center',
    borderWidth: 2,
    borderColor: '#FFFFFF',
  },
  secondaryButtonText: {
    color: '#FFFFFF',
    fontSize: 18,
    fontWeight: '600',
  },
  troubleButton: {
    alignItems: 'center',
    paddingVertical: 12,
  },
  troubleText: {
    color: 'rgba(255,255,255,0.9)',
    fontSize: 16,
    textDecorationLine: 'underline',
  },

  // Login/Register Screen Styles
  backButton: {
    position: 'absolute',
    top: 60,
    left: 32,
    width: 44,
    height: 44,
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 1000,
  },
  formContainer: {
    flex: 1,
    paddingTop: 120,
    paddingHorizontal: 32,
  },
  screenTitle: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#FFFFFF',
    textAlign: 'center',
    marginBottom: 40,
  },
  errorContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(255, 255, 255, 0.15)',
    padding: 12,
    borderRadius: 12,
    marginBottom: 20,
  },
  errorText: {
    color: '#FFE5E5',
    fontSize: 14,
    marginLeft: 8,
    flex: 1,
  },
  
  // OAuth Buttons
  oauthButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    borderRadius: 30,
    paddingVertical: 16,
    paddingHorizontal: 20,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 1,
    },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  oauthButtonText: {
    color: '#333333',
    fontSize: 16,
    fontWeight: '500',
    marginLeft: 12,
    flex: 1,
    textAlign: 'center',
  },

  // Form Section
  formSection: {
    marginTop: 30,
  },
  sectionTitle: {
    fontSize: 16,
    color: 'rgba(255,255,255,0.9)',
    textAlign: 'center',
    marginBottom: 20,
  },
  inputContainer: {
    backgroundColor: 'rgba(255,255,255,0.15)',
    borderRadius: 12,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.3)',
  },
  input: {
    fontSize: 16,
    color: '#FFFFFF',
    paddingVertical: 18,
    paddingHorizontal: 20,
  },
  submitButton: {
    backgroundColor: '#FFFFFF',
    borderRadius: 30,
    paddingVertical: 18,
    alignItems: 'center',
    marginTop: 10,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  submitButtonDisabled: {
    opacity: 0.6,
  },
  submitButtonText: {
    color: '#FF69B4',
    fontSize: 16,
    fontWeight: '600',
  },

  // Additional Button Styles
  backToMobileButton: {
    alignItems: 'center',
    paddingVertical: 16,
  },
  backToMobileText: {
    color: 'rgba(255,255,255,0.9)',
    fontSize: 14,
    textDecorationLine: 'underline',
  },
  toggleMethodButton: {
    alignItems: 'center',
    paddingVertical: 20,
  },
  toggleMethodText: {
    color: 'rgba(255,255,255,0.9)',
    fontSize: 16,
    textDecorationLine: 'underline',
  },
  switchToLoginButton: {
    alignItems: 'center',
    paddingVertical: 20,
    marginTop: 20,
  },
  switchToLoginText: {
    color: 'rgba(255,255,255,0.9)',
    fontSize: 16,
    textDecorationLine: 'underline',
  },
  alternativeLink: {
    color: '#FFFFFF',
    fontWeight: '600',
    textDecorationLine: 'underline',
  },
  
  // Scroll container
  scrollContainer: {
    flex: 1,
  },
  scrollContent: {
    flexGrow: 1,
    paddingBottom: 40,
  },

  // Clean Design Styles
  cleanContainer: {
    flex: 1,
    backgroundColor: '#FFFFFF',
    paddingHorizontal: 24,
  },
  cleanBackButton: {
    position: 'absolute',
    top: 60,
    left: 20,
    zIndex: 10,
    padding: 12,
    borderRadius: 24,
    backgroundColor: '#F5F5F5',
  },
  cleanHeader: {
    alignItems: 'center',
    marginTop: 120,
    marginBottom: 40,
    paddingHorizontal: 20,
  },
  cleanTitle: {
    fontSize: 32,
    fontWeight: '700',
    color: '#1A1A1A',
    textAlign: 'center',
    marginBottom: 12,
  },
  cleanSubtitle: {
    fontSize: 16,
    color: '#666666',
    textAlign: 'center',
    lineHeight: 22,
  },
  cleanOptionsContainer: {
    flex: 1,
    paddingTop: 20,
  },
  cleanOption: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 20,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 3,
    borderWidth: 1,
    borderColor: '#F0F0F0',
  },
  cleanOptionIconContainer: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: '#F8F9FA',
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 16,
  },
  cleanOptionContent: {
    flex: 1,
  },
  cleanOptionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1A1A1A',
    marginBottom: 4,
  },
  cleanOptionDescription: {
    fontSize: 14,
    color: '#666666',
    lineHeight: 18,
  },
  cleanBottomContainer: {
    paddingVertical: 30,
    alignItems: 'center',
  },
  cleanAlternativeLogin: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  cleanAlternativeText: {
    fontSize: 16,
    color: '#666666',
  },
  cleanAlternativeLink: {
    fontSize: 16,
    color: '#FF1493',
    fontWeight: '600',
  },
  
  // Clean Error Styles
  cleanErrorContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFF5F5',
    borderRadius: 12,
    padding: 16,
    marginHorizontal: 20,
    marginBottom: 20,
    borderWidth: 1,
    borderColor: '#FFCDD2',
  },
  cleanErrorText: {
    flex: 1,
    fontSize: 14,
    color: '#FF4444',
    marginLeft: 8,
    lineHeight: 18,
  },

  // Clean Form Styles
  cleanScrollContent: {
    flexGrow: 1,
    paddingBottom: 40,
  },
  cleanFormContainer: {
    flex: 1,
    paddingHorizontal: 20,
    paddingTop: 20,
  },
  cleanInputContainer: {
    backgroundColor: '#F8F9FA',
    borderRadius: 12,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: '#E9ECEF',
    flexDirection: 'row',
    alignItems: 'center',
  },
  cleanInput: {
    flex: 1,
    fontSize: 16,
    color: '#1A1A1A',
    paddingVertical: 18,
    paddingHorizontal: 20,
  },
  cleanPasswordToggle: {
    padding: 18,
  },
  cleanSubmitButton: {
    backgroundColor: '#FF1493',
    borderRadius: 12,
    paddingVertical: 18,
    alignItems: 'center',
    marginTop: 10,
    shadowColor: '#FF1493',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.2,
    shadowRadius: 4,
    elevation: 3,
  },
  cleanSubmitButtonDisabled: {
    opacity: 0.6,
  },
  cleanSubmitButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
  cleanDivider: {
    flexDirection: 'row',
    alignItems: 'center',
    marginVertical: 30,
  },
  cleanDividerLine: {
    flex: 1,
    height: 1,
    backgroundColor: '#E9ECEF',
  },
  cleanDividerText: {
    marginHorizontal: 16,
    fontSize: 14,
    color: '#666666',
  },
  cleanMethodSwitchButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#F8F9FA',
    borderRadius: 12,
    paddingVertical: 16,
    paddingHorizontal: 20,
    borderWidth: 1,
    borderColor: '#E9ECEF',
  },
  cleanMethodSwitchText: {
    marginLeft: 8,
    fontSize: 16,
    color: '#FF1493',
    fontWeight: '500',
  },
  cleanBackToMobileButton: {
    alignItems: 'center',
    paddingVertical: 16,
  },
  cleanBackToMobileText: {
    color: '#666666',
    fontSize: 14,
    textDecorationLine: 'underline',
  },

  // Signup Options Screen Styles
  backButton: {
    position: 'absolute',
    top: 60,
    left: 20,
    zIndex: 10,
    padding: 8,
    borderRadius: 20,
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
  },
  signupHeader: {
    alignItems: 'center',
    marginTop: 120,
    marginBottom: 40,
  },
  signupTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#FFFFFF',
    textAlign: 'center',
    marginBottom: 8,
  },
  signupSubtitle: {
    fontSize: 16,
    color: '#FFFFFF',
    textAlign: 'center',
    opacity: 0.9,
  },
  signupOptionsContainer: {
    flex: 1,
    justifyContent: 'center',
  },
  signupOptions: {
    paddingHorizontal: 20,
    paddingVertical: 20,
  },
  signupOption: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(255, 255, 255, 0.1)',
    borderRadius: 16,
    padding: 20,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.2)',
  },
  signupOptionIcon: {
    width: 50,
    height: 50,
    borderRadius: 25,
    backgroundColor: '#FFFFFF',
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 16,
  },
  signupOptionContent: {
    flex: 1,
  },
  signupOptionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#FFFFFF',
    marginBottom: 4,
  },
  signupOptionDescription: {
    fontSize: 14,
    color: '#FFFFFF',
    opacity: 0.8,
  },
  bottomSection: {
    paddingHorizontal: 20,
    paddingBottom: 40,
    paddingTop: 20,
  },
  alternativeLogin: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
  },
  alternativeText: {
    color: '#FFFFFF',
    fontSize: 16,
  },

  // Splash Screen Styles
  splashBrandingContainer: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: 40,
  },
  logoContainer: {
    alignItems: 'center',
    marginBottom: 30,
  },
  splashLogo: {
    width: width * 0.85, // 85% of screen width for prominence
    height: 140,
    marginBottom: 20,
  },
  splashTagline: {
    fontSize: 18,
    color: '#FFFFFF',
    textAlign: 'center',
    fontWeight: '500',
    letterSpacing: 0.5,
    opacity: 0.95,
  },
  splashButtonContainer: {
    width: '100%',
    paddingHorizontal: 40,
    paddingBottom: 60,
  },
  splashPrimaryButton: {
    backgroundColor: '#FFFFFF',
    borderRadius: 25,
    paddingVertical: 18,
    alignItems: 'center',
    marginBottom: 16,
    shadowOffset: {
      width: 0,
      height: 4,
    },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 6,
  },
  splashPrimaryButtonText: {
    color: '#FF1493',
    fontSize: 18,
    fontWeight: '700',
    letterSpacing: 0.5,
  },
  splashSecondaryButton: {
    backgroundColor: 'transparent',
    borderRadius: 25,
    paddingVertical: 18,
    alignItems: 'center',
    borderWidth: 2,
    borderColor: '#FFFFFF',
  },
  splashSecondaryButtonText: {
    color: '#FFFFFF',
    fontSize: 18,
    fontWeight: '600',
    letterSpacing: 0.5,
  },
});