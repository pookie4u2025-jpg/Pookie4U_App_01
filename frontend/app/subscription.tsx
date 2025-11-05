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

const { width } = Dimensions.get('window');
const BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL || '';

type PlanType = 'trial' | 'monthly' | 'sixmonth';

export default function SubscriptionScreen() {
  const router = useRouter();
  const { user, token } = useAuthStore();
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
      }
    } catch (error) {
      console.error('Error fetching subscription status:', error);
    } finally {
      setLoadingStatus(false);
    }
  };

  const handleSelectPlan = (plan: 'monthly' | 'sixmonth') => {
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    setSelectedPlan(plan);
  };

  const handleFreeTrial = async () => {
    console.log('🎁 Starting free trial without payment');
    
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
          setSelectedPlan('sixmonth'); // Auto-select 6-month plan
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
      
      // Don't show alert if we already handled the "already used" case
      if (!errorMessage.includes('already used')) {
        Alert.alert('Error', errorMessage);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleSubscribe = async () => {
    console.log('🔐 Subscription - Checking auth status:');
    console.log('  User:', user ? 'Present' : 'Missing');
    console.log('  Token:', token ? `Present (${token.substring(0, 20)}...)` : 'Missing');
    
    if (!user || !token) {
      Alert.alert('Error', 'Please log in to continue');
      return;
    }

    // Payment gateway integration coming soon
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
    Alert.alert(
      '🚀 Coming Soon',
      'Payment integration is currently being set up. You can still enjoy the free trial! Premium payment options will be available soon.',
      [
        {
          text: 'Start Free Trial',
          onPress: () => handleFreeTrial(),
        },
        {
          text: 'OK',
          style: 'cancel'
        }
      ]
    );
  };

  const handleContinue = () => {
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
    
    if (selectedPlan === 'trial') {
      handleFreeTrial();
    } else {
      handleSubscribe();
    }
  };

  const handleSkip = () => {
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    router.push('/tabs');
  };

  return (
    <SafeAreaView style={styles.container}>
      {/* Back Button */}
      <TouchableOpacity
        style={styles.backButton}
        onPress={handleSkip}
        activeOpacity={0.7}
      >
        <Ionicons name="arrow-back" size={24} color="#1A1A1A" />
      </TouchableOpacity>
      
      <ScrollView 
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        {/* Header with Logo */}
        <View style={styles.header}>
          <Image 
            source={require('../assets/images/p4u-logo-new.png')}
            style={styles.logo}
            resizeMode="contain"
          />
          <Text style={styles.title}>Upgrade to Premium</Text>
          <Text style={styles.subtitle}>
            Unlock all features and strengthen your relationship
          </Text>
        </View>

        {/* Header Info */}
        <View style={styles.headerInfo}>
          {subscriptionData?.is_active ? (
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
              {subscriptionData.renewal_date_display && (
                <>
                  <Text style={styles.renewalText}>
                    {subscriptionData.auto_renewal_enabled ? 'Renews on:' : 'Expires on:'} {subscriptionData.renewal_date_display}
                  </Text>
                  {subscriptionData.auto_renewal_enabled && (
                    <View style={styles.autoRenewalBadge}>
                      <Ionicons name="sync" size={16} color="#2196F3" />
                      <Text style={styles.autoRenewalText}>Auto-Renewal Enabled</Text>
                    </View>
                  )}
                </>
              )}
            </View>
          ) : (
            <Text style={styles.infoText}>
              {trialAlreadyUsed 
                ? 'Choose a plan to continue enjoying premium features' 
                : 'Choose your plan and start your premium experience'}
            </Text>
          )}
        </View>

        {/* Subscription Plans */}
        <View style={styles.plansContainer}>
          {/* Free Trial Plan - Only show if not already used */}
          {!trialAlreadyUsed && !subscriptionData?.is_active && (
            <TouchableOpacity
              style={[
                styles.planCard,
                selectedPlan === 'trial' && styles.planCardSelected,
              ]}
              onPress={() => handleSelectPlan('trial' as any)}
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
                  <Text style={styles.planTitle}>Free Trial</Text>
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
              <Text style={styles.oneTimeOnly}>⚠️ One-time offer only</Text>
            </TouchableOpacity>
          )}

          {/* Show message if trial was already used */}
          {trialAlreadyUsed && !subscriptionData?.is_active && (
            <View style={styles.trialUsedBanner}>
              <Ionicons name="information-circle" size={24} color="#FF9800" />
              <Text style={styles.trialUsedText}>
                You've already used your 14-day free trial. Select a paid plan below.
              </Text>
            </View>
          )}

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
                <Text style={styles.planTitle}>6 Months</Text>
              </View>
              <View style={styles.recommendedBadge}>
                <Text style={styles.recommendedText}>BEST VALUE</Text>
              </View>
            </View>
            
            <View style={styles.planPricing}>
              <Text style={styles.planPrice}>₹450</Text>
              <Text style={styles.planPeriod}>for 6 months</Text>
            </View>
            
            <View style={styles.savingsBadge}>
              <Text style={styles.savingsText}>Save ₹24 • ₹75/month</Text>
            </View>
          </TouchableOpacity>

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
                <Text style={styles.planTitle}>Monthly</Text>
              </View>
            </View>
            
            <View style={styles.planPricing}>
              <Text style={styles.planPrice}>₹79</Text>
              <Text style={styles.planPeriod}>per month</Text>
            </View>
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

          <View style={styles.feature}>
            <Ionicons name="checkmark-circle" size={24} color="#10B981" />
            <Text style={styles.featureText}>Unlimited custom events</Text>
          </View>

          <View style={styles.feature}>
            <Ionicons name="checkmark-circle" size={24} color="#10B981" />
            <Text style={styles.featureText}>Ad-free experience</Text>
          </View>
        </View>

        {/* Subscribe Button */}
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
                  : 'Cancel anytime • No charges during trial'
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
          Subscription auto-renews unless cancelled 24 hours before period ends.
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
  headerInfo: {
    alignItems: 'center',
    marginBottom: 24,
    paddingHorizontal: 20,
  },
  infoText: {
    fontSize: 14,
    color: '#666',
    textAlign: 'center',
    lineHeight: 20,
  },
  currentSubCard: {
    backgroundColor: '#E8F5E9',
    padding: 16,
    borderRadius: 12,
    borderWidth: 2,
    borderColor: '#4CAF50',
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
    marginBottom: 8,
  },
  renewalText: {
    fontSize: 14,
    color: '#666',
    marginBottom: 8,
  },
  autoRenewalBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    backgroundColor: '#E3F2FD',
    paddingVertical: 6,
    paddingHorizontal: 12,
    borderRadius: 8,
    alignSelf: 'flex-start',
  },
  autoRenewalText: {
    fontSize: 12,
    color: '#2196F3',
    fontWeight: '600',
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
  oneTimeOnly: {
    fontSize: 12,
    color: '#F57C00',
    textAlign: 'center',
    marginTop: 8,
    fontWeight: '600',
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
  trialBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#FFF0F7',
    borderRadius: 20,
    paddingVertical: 12,
    paddingHorizontal: 20,
    marginBottom: 24,
    borderWidth: 1,
    borderColor: '#FFD6EB',
  },
  trialText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#FF1493',
    marginLeft: 8,
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
  },
  savingsText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#F59E0B',
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
