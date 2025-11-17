import React, { useState } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  ScrollView,
  SafeAreaView,
  Image,
  Dimensions,
  Alert,
  ActivityIndicator,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';
import * as Haptics from 'expo-haptics';
import Purchases, { PurchasesError, PurchasesPackage } from 'react-native-purchases';
import { useAuthStore } from '../src/stores/useAuthStore';
import { useTheme } from '../src/contexts/ThemeContext';

const { width } = Dimensions.get('window');
const BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL || '';

type PlanType = 'trial' | 'monthly' | 'sixmonth';

export default function SubscriptionScreen() {
  const router = useRouter();
  const { user, token } = useAuthStore();
  const { theme } = useTheme();
  const [selectedPlan, setSelectedPlan] = useState<PlanType>('trial');
  const [loading, setLoading] = useState(false);
  const [trialAlreadyUsed, setTrialAlreadyUsed] = useState(false);
  const [subscriptionData, setSubscriptionData] = useState<any>(null);
  const [loadingStatus, setLoadingStatus] = useState(true);
  const [revenueCatPackages, setRevenueCatPackages] = useState<PurchasesPackage[]>([]);
  const [revenueCatConfigured, setRevenueCatConfigured] = useState(false);

  // Fetch subscription status and RevenueCat offerings on mount
  React.useEffect(() => {
    fetchSubscriptionStatus();
    fetchRevenueCatOfferings();
  }, []);

  const fetchSubscriptionStatus = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/subscription/status`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setSubscriptionData(data.subscription);
        setTrialAlreadyUsed(data.subscription.trial_already_used || false);
        
        // Auto-select monthly if trial already used
        if (data.subscription.trial_already_used) {
          setSelectedPlan('monthly');
        }
      }
    } catch (error) {
      console.error('Error fetching subscription status:', error);
    } finally {
      setLoadingStatus(false);
    }
  };

  const fetchRevenueCatOfferings = async () => {
    try {
      console.log('🔍 Fetching RevenueCat offerings...');
      const offerings = await Purchases.getOfferings();
      
      if (offerings.current && offerings.current.availablePackages.length > 0) {
        setRevenueCatPackages(offerings.current.availablePackages);
        setRevenueCatConfigured(true);
        console.log('✅ RevenueCat packages loaded:', offerings.current.availablePackages.length);
      } else {
        console.log('⚠️ No RevenueCat offerings available');
        setRevenueCatConfigured(false);
      }
    } catch (error) {
      console.log('⚠️ RevenueCat not configured or error:', error);
      setRevenueCatConfigured(false);
    }
  };

  const handleSelectPlan = (plan: PlanType) => {
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    setSelectedPlan(plan);
  };

  const handleFreeTrial = async () => {
    console.log('🎁 Starting backend-managed free trial (no payment required)');
    
    if (!user || !token) {
      Alert.alert('Error', 'Please log in to continue');
      return;
    }

    setLoading(true);
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);

    try {
      const response = await fetch(`${BACKEND_URL}/api/subscription/start-trial`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      console.log('📥 Trial response status:', response.status);

      if (!response.ok) {
        const errorData = await response.json();
        
        // Check if trial was already used
        if (errorData.detail && errorData.detail.includes('already used')) {
          setTrialAlreadyUsed(true);
          setSelectedPlan('monthly');
          Alert.alert(
            'Trial Already Used',
            'You have already used your 14-day free trial. Please select a paid plan to continue enjoying premium features.',
            [{ text: 'OK' }]
          );
          return;
        }
        
        throw new Error(errorData.detail || 'Failed to start trial');
      }

      const data = await response.json();
      
      if (data.success) {
        Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
        Alert.alert(
          '🎉 Free Trial Activated!',
          'Enjoy 14 days of premium features for free. No payment required!',
          [
            {
              text: 'Get Started',
              onPress: () => router.push('/(tabs)'),
            },
          ]
        );
      } else {
        throw new Error(data.message || 'Failed to activate trial');
      }
    } catch (error) {
      console.error('❌ Trial activation error:', error);
      const errorMessage = error instanceof Error ? error.message : 'Failed to activate trial';
      Alert.alert('Error', errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handlePaidSubscription = async () => {
    console.log('💳 Initiating Google Play payment for paid subscription');
    
    if (!user || !token) {
      Alert.alert('Error', 'Please log in to continue');
      return;
    }

    if (!revenueCatConfigured) {
      Alert.alert(
        'Payment Setup Incomplete',
        'Payment system is still being configured. Please try the free trial for now or contact support.',
        [{ text: 'OK' }]
      );
      return;
    }

    // Find the selected package
    const selectedPackage = revenueCatPackages.find(pkg => {
      if (selectedPlan === 'monthly') {
        return pkg.identifier.includes('monthly');
      } else if (selectedPlan === 'sixmonth') {
        return pkg.identifier.includes('6_month') || pkg.identifier.includes('sixmonth');
      }
      return false;
    });

    if (!selectedPackage) {
      Alert.alert('Error', 'Selected plan not available');
      return;
    }

    setLoading(true);
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);

    try {
      console.log('🔐 Attempting to purchase package:', selectedPackage.identifier);
      
      // Identify user to RevenueCat before purchase
      if (user.id) {
        await Purchases.logIn(user.id);
        console.log('✅ User identified to RevenueCat');
      }

      // Purchase the package - This opens Google Play payment sheet
      const { customerInfo } = await Purchases.purchasePackage(selectedPackage);
      
      console.log('✅ Purchase successful');
      
      // Check if premium access is granted
      if (typeof customerInfo.entitlements.active['premium_access'] !== 'undefined') {
        Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
        Alert.alert(
          '🎉 Subscription Activated!',
          'Your premium subscription is now active. Enjoy all features!',
          [
            {
              text: 'Get Started',
              onPress: () => router.push('/(tabs)'),
            },
          ]
        );
      } else {
        throw new Error('Purchase completed but premium access not granted');
      }
      
    } catch (error) {
      setLoading(false);
      
      if (error instanceof PurchasesError) {
        console.error('❌ RevenueCat purchase error:', error.code, error.message);
        
        // Handle different error types
        if (error.code === 'PurchaseCancelledError') {
          console.log('User cancelled the purchase');
          // Don't show error alert for cancellations
          return;
        } else if (error.code === 'StoreProblemError') {
          Alert.alert(
            'Payment Issue',
            'There was a problem with the Google Play Store. Please try again later.',
            [{ text: 'OK' }]
          );
        } else {
          Alert.alert(
            'Purchase Failed',
            `Unable to complete purchase: ${error.message}`,
            [{ text: 'OK' }]
          );
        }
      } else {
        console.error('❌ Unexpected purchase error:', error);
        Alert.alert('Error', 'Failed to complete purchase. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleContinue = () => {
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
    
    if (selectedPlan === 'trial') {
      handleFreeTrial();
    } else {
      handlePaidSubscription();
    }
  };

  const handleSkip = () => {
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    // Use router.back() to properly navigate back in the stack
    if (router.canGoBack()) {
      router.back();
    } else {
      // Fallback to home if no history
      router.replace('/(tabs)/home');
    }
  };

  // Get pricing from RevenueCat packages
  const getPackagePrice = (planType: 'monthly' | 'sixmonth'): string => {
    const pkg = revenueCatPackages.find(p => {
      if (planType === 'monthly') {
        return p.identifier.includes('monthly');
      } else {
        return p.identifier.includes('6_month') || p.identifier.includes('sixmonth');
      }
    });
    return pkg?.product.priceString || (planType === 'monthly' ? '₹79' : '₹450');
  };

  if (loadingStatus) {
    return (
      <SafeAreaView style={[styles.container, { backgroundColor: theme.background }]}>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color={theme.primary} />
          <Text style={[styles.loadingText, { color: theme.text }]}>Loading subscription options...</Text>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: theme.background }]}>
      {/* Back Button */}
      <TouchableOpacity
        style={[styles.backButton, { backgroundColor: theme.surface }]}
        onPress={handleSkip}
        activeOpacity={0.7}
      >
        <Ionicons name="arrow-back" size={24} color={theme.text} />
      </TouchableOpacity>
      
      <ScrollView 
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        {/* Header with Logo */}
        <View style={styles.header}>
          <Image 
            source={require('../assets/images/logos/p4u-short-logo.png')}
            style={styles.logo}
            resizeMode="contain"
          />
          <Text style={[styles.title, { color: theme.text }]}>Choose Your Plan</Text>
          <Text style={[styles.subtitle, { color: theme.textSecondary }]}>
            Unlock premium features and strengthen your relationship
          </Text>
        </View>

        {/* Current Subscription Status */}
        {subscriptionData?.is_active && (
          <View style={styles.currentSubCard}>
            <View style={styles.currentSubHeader}>
              <Ionicons name="checkmark-circle" size={24} color="#4CAF50" />
              <Text style={styles.currentSubTitle}>Active Subscription</Text>
            </View>
            <Text style={styles.currentSubPlan}>
              {subscriptionData.type === 'monthly' ? 'Premium Monthly' : 
               subscriptionData.type === 'half_yearly' ? 'Premium 6-Month' : 
               'Free Trial'}
            </Text>
            {subscriptionData.days_remaining && (
              <Text style={styles.daysRemaining}>
                {subscriptionData.days_remaining} days remaining
              </Text>
            )}
          </View>
        )}

        {/* Subscription Plans */}
        <View style={styles.plansContainer}>
          {/* Free Trial Plan - Only show if not already used */}
          {!trialAlreadyUsed && !subscriptionData?.is_active && (
            <TouchableOpacity
              style={[
                styles.planCard,
                selectedPlan === 'trial' && styles.planCardSelected,
              ]}
              onPress={() => handleSelectPlan('trial')}
              activeOpacity={0.7}
            >
              <View style={styles.planHeader}>
                <View style={styles.planHeaderLeft}>
                  <View style={[
                    styles.radioButton,
                    selectedPlan === 'trial' && styles.radioButtonSelected,
                  ]}>
                    {selectedPlan === 'trial' && (
                      <View style={styles.radioButtonInner} />
                    )}
                  </View>
                  <Text style={styles.planTitle}>14 Days Free Trial</Text>
                </View>
                <View style={styles.recommendedBadge}>
                  <Text style={styles.recommendedText}>RECOMMENDED</Text>
                </View>
              </View>
              
              <View style={styles.planPricing}>
                <Text style={styles.planPrice}>₹0</Text>
                <Text style={styles.planPeriod}>for 14 days</Text>
              </View>
              
              <View style={styles.savingsBadge}>
                <Text style={styles.savingsText}>No payment required</Text>
              </View>
              <Text style={styles.featureNote}>⚠️ One-time offer only</Text>
            </TouchableOpacity>
          )}

          {/* Trial Used Banner */}
          {trialAlreadyUsed && !subscriptionData?.is_active && (
            <View style={styles.trialUsedBanner}>
              <Ionicons name="information-circle" size={24} color="#FF9800" />
              <Text style={styles.trialUsedText}>
                You've already used your 14-day free trial. Select a paid plan below.
              </Text>
            </View>
          )}

          {/* Monthly Plan */}
          <TouchableOpacity
            style={[
              styles.planCard,
              selectedPlan === 'monthly' && styles.planCardSelected,
            ]}
            onPress={() => handleSelectPlan('monthly')}
            activeOpacity={0.7}
          >
            <View style={styles.planHeader}>
              <View style={styles.planHeaderLeft}>
                <View style={[
                  styles.radioButton,
                  selectedPlan === 'monthly' && styles.radioButtonSelected,
                ]}>
                  {selectedPlan === 'monthly' && (
                    <View style={styles.radioButtonInner} />
                  )}
                </View>
                <Text style={styles.planTitle}>Monthly Plan</Text>
              </View>
            </View>
            
            <View style={styles.planPricing}>
              <Text style={styles.planPrice}>{getPackagePrice('monthly')}</Text>
              <Text style={styles.planPeriod}>per month</Text>
            </View>
            
            <Text style={styles.featureNote}>✓ Auto-renewable subscription</Text>
          </TouchableOpacity>

          {/* 6-Month Plan */}
          <TouchableOpacity
            style={[
              styles.planCard,
              selectedPlan === 'sixmonth' && styles.planCardSelected,
            ]}
            onPress={() => handleSelectPlan('sixmonth')}
            activeOpacity={0.7}
          >
            <View style={styles.planHeader}>
              <View style={styles.planHeaderLeft}>
                <View style={[
                  styles.radioButton,
                  selectedPlan === 'sixmonth' && styles.radioButtonSelected,
                ]}>
                  {selectedPlan === 'sixmonth' && (
                    <View style={styles.radioButtonInner} />
                  )}
                </View>
                <Text style={styles.planTitle}>6-Month Plan</Text>
              </View>
              <View style={styles.recommendedBadge}>
                <Text style={styles.recommendedText}>BEST VALUE</Text>
              </View>
            </View>
            
            <View style={styles.planPricing}>
              <Text style={styles.planPrice}>{getPackagePrice('sixmonth')}</Text>
              <Text style={styles.planPeriod}>for 6 months</Text>
            </View>
            
            <View style={styles.savingsBadge}>
              <Text style={styles.savingsText}>Save ₹24 • ₹75/month</Text>
            </View>
            <Text style={styles.featureNote}>✓ Auto-renewable subscription</Text>
          </TouchableOpacity>
        </View>

        {/* Features List */}
        <View style={styles.featuresContainer}>
          <Text style={styles.featuresTitle}>What you'll get:</Text>
          
          <View style={styles.feature}>
            <Ionicons name="checkmark-circle" size={24} color="#10B981" />
            <Text style={styles.featureText}>AI-powered relationship tasks</Text>
          </View>

          <View style={styles.feature}>
            <Ionicons name="checkmark-circle" size={24} color="#10B981" />
            <Text style={styles.featureText}>Daily romantic messages</Text>
          </View>

          <View style={styles.feature}>
            <Ionicons name="checkmark-circle" size={24} color="#10B981" />
            <Text style={styles.featureText}>Event reminders & countdowns</Text>
          </View>

          <View style={styles.feature}>
            <Ionicons name="checkmark-circle" size={24} color="#10B981" />
            <Text style={styles.featureText}>Personalized gift suggestions</Text>
          </View>

          <View style={styles.feature}>
            <Ionicons name="checkmark-circle" size={24} color="#10B981" />
            <Text style={styles.featureText}>Gamification & rewards</Text>
          </View>
        </View>

        {/* Continue Button */}
        <TouchableOpacity
          style={[styles.subscribeButton, loading && styles.subscribeButtonDisabled]}
          onPress={handleContinue}
          activeOpacity={0.8}
          disabled={loading}
        >
          {loading ? (
            <ActivityIndicator color="#FFFFFF" size="small" />
          ) : (
            <>
              <Text style={styles.subscribeButtonText}>
                {selectedPlan === 'trial' ? 'Start Free Trial' : 'Subscribe Now'}
              </Text>
              <Text style={styles.subscribeButtonSubtext}>
                {selectedPlan === 'trial' 
                  ? 'No payment required • 14 days free'
                  : 'Secure payment via Google Play'
                }
              </Text>
            </>
          )}
        </TouchableOpacity>

        {/* Skip Button */}
        <TouchableOpacity
          style={styles.skipButton}
          onPress={handleSkip}
          activeOpacity={0.7}
        >
          <Text style={styles.skipButtonText}>Maybe Later</Text>
        </TouchableOpacity>

        {/* Terms */}
        <Text style={styles.termsText}>
          By subscribing, you agree to our Terms of Service and Privacy Policy.
          {selectedPlan !== 'trial' && ' Subscription auto-renews unless cancelled 24 hours before period ends.'}
        </Text>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FFFFFF',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    marginTop: 16,
    fontSize: 16,
    color: '#666',
  },
  backButton: {
    position: 'absolute',
    top: 50,
    left: 20,
    zIndex: 10,
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#F5F5F5',
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  scrollContent: {
    flexGrow: 1,
    paddingHorizontal: 24,
    paddingTop: 60,
    paddingBottom: 40,
  },
  header: {
    alignItems: 'center',
    marginBottom: 24,
  },
  logo: {
    width: 80,
    height: 80,
    marginBottom: 16,
  },
  title: {
    fontSize: 28,
    fontWeight: '700',
    color: '#1A1A1A',
    textAlign: 'center',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: '#666666',
    textAlign: 'center',
    lineHeight: 22,
  },
  currentSubCard: {
    backgroundColor: '#E8F5E9',
    padding: 16,
    borderRadius: 12,
    borderWidth: 2,
    borderColor: '#4CAF50',
    marginBottom: 24,
  },
  currentSubHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    marginBottom: 8,
  },
  currentSubTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#4CAF50',
  },
  currentSubPlan: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 4,
  },
  daysRemaining: {
    fontSize: 14,
    color: '#666',
  },
  trialUsedBanner: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFF3E0',
    padding: 16,
    borderRadius: 12,
    gap: 12,
    marginBottom: 16,
  },
  trialUsedText: {
    flex: 1,
    fontSize: 14,
    color: '#F57C00',
    fontWeight: '500',
  },
  plansContainer: {
    marginBottom: 32,
  },
  planCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 20,
    marginBottom: 16,
    borderWidth: 2,
    borderColor: '#E9ECEF',
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.05,
    shadowRadius: 8,
    elevation: 2,
  },
  planCardSelected: {
    borderColor: '#FF1493',
    backgroundColor: '#FFF5FA',
  },
  planHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  planHeaderLeft: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  radioButton: {
    width: 24,
    height: 24,
    borderRadius: 12,
    borderWidth: 2,
    borderColor: '#D1D5DB',
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 12,
  },
  radioButtonSelected: {
    borderColor: '#FF1493',
  },
  radioButtonInner: {
    width: 12,
    height: 12,
    borderRadius: 6,
    backgroundColor: '#FF1493',
  },
  planTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: '#1A1A1A',
  },
  recommendedBadge: {
    backgroundColor: '#10B981',
    borderRadius: 8,
    paddingVertical: 4,
    paddingHorizontal: 10,
  },
  recommendedText: {
    fontSize: 12,
    fontWeight: '700',
    color: '#FFFFFF',
    letterSpacing: 0.5,
  },
  planPricing: {
    flexDirection: 'row',
    alignItems: 'baseline',
    marginBottom: 8,
  },
  planPrice: {
    fontSize: 36,
    fontWeight: '700',
    color: '#1A1A1A',
    marginRight: 8,
  },
  planPeriod: {
    fontSize: 16,
    color: '#666666',
  },
  savingsBadge: {
    backgroundColor: '#FFF7ED',
    borderRadius: 8,
    paddingVertical: 6,
    paddingHorizontal: 12,
    alignSelf: 'flex-start',
    marginBottom: 8,
  },
  savingsText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#F59E0B',
  },
  featureNote: {
    fontSize: 12,
    color: '#666',
    marginTop: 4,
  },
  featuresContainer: {
    marginBottom: 32,
  },
  featuresTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1A1A1A',
    marginBottom: 16,
  },
  feature: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  featureText: {
    fontSize: 16,
    color: '#374151',
    marginLeft: 12,
    flex: 1,
  },
  subscribeButton: {
    backgroundColor: '#FF1493',
    borderRadius: 16,
    paddingVertical: 18,
    paddingHorizontal: 32,
    alignItems: 'center',
    marginBottom: 16,
    shadowColor: '#FF1493',
    shadowOffset: {
      width: 0,
      height: 4,
    },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 4,
  },
  subscribeButtonDisabled: {
    backgroundColor: '#CCCCCC',
    shadowOpacity: 0.1,
  },
  subscribeButtonText: {
    fontSize: 18,
    fontWeight: '700',
    color: '#FFFFFF',
    marginBottom: 4,
  },
  subscribeButtonSubtext: {
    fontSize: 13,
    color: '#FFFFFF',
    opacity: 0.9,
  },
  skipButton: {
    paddingVertical: 16,
    alignItems: 'center',
    marginBottom: 24,
  },
  skipButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#666666',
  },
  termsText: {
    fontSize: 12,
    color: '#9CA3AF',
    textAlign: 'center',
    lineHeight: 18,
  },
});
