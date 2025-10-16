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
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';
import * as Haptics from 'expo-haptics';

const { width } = Dimensions.get('window');

export default function SubscriptionScreen() {
  const router = useRouter();
  const [selectedPlan, setSelectedPlan] = useState<'monthly' | 'sixmonth'>('sixmonth');

  const handleSelectPlan = (plan: 'monthly' | 'sixmonth') => {
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    setSelectedPlan(plan);
  };

  const handleSubscribe = () => {
    Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
    Alert.alert(
      'Coming Soon! 🚀',
      'Subscription payment integration is coming soon. You\'ll be notified when it\'s ready!',
      [
        {
          text: 'OK',
          onPress: () => router.push('/tabs'),
        },
      ]
    );
  };

  const handleSkip = () => {
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    router.push('/tabs');
  };

  return (
    <SafeAreaView style={styles.container}>
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

        {/* 14-Day Free Trial Badge */}
        <View style={styles.trialBadge}>
          <Ionicons name="gift-outline" size={20} color="#FF1493" />
          <Text style={styles.trialText}>14-Day Free Trial Included</Text>
        </View>

        {/* Subscription Plans */}
        <View style={styles.plansContainer}>
          {/* 6-Month Plan (Recommended) */}
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
          style={styles.subscribeButton}
          onPress={handleSubscribe}
          activeOpacity={0.8}
        >
          <Text style={styles.subscribeButtonText}>
            Start Free Trial
          </Text>
          <Text style={styles.subscribeButtonSubtext}>
            Cancel anytime • No charges during trial
          </Text>
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
  scrollContent: {
    flexGrow: 1,
    paddingHorizontal: 24,
    paddingTop: 20,
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
