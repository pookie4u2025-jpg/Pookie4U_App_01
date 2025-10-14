import React, { useState } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  ScrollView,
  SafeAreaView,
  Image,
  Alert,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { router } from 'expo-router';

const SubscriptionScreen = () => {
  const [selectedPlan, setSelectedPlan] = useState<'monthly' | 'yearly'>('monthly');

  const handleStartSubscription = (plan: 'monthly' | 'yearly' | 'trial') => {
    if (plan === 'trial') {
      Alert.alert('Free Trial Started! 🎉', 'You now have access to all premium features for 14 days.');
    } else {
      Alert.alert('Subscription Started! 💳', `You've subscribed to the ${plan} plan.`);
    }
    // Navigate to main app after subscription
    router.replace('/tabs');
  };

  const handleSkip = () => {
    router.replace('/tabs');
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.content} showsVerticalScrollIndicator={false}>
        {/* Header */}
        <View style={styles.header}>
          <TouchableOpacity style={styles.skipButton} onPress={handleSkip}>
            <Text style={styles.skipButtonText}>Skip</Text>
          </TouchableOpacity>
          
          <Image 
            source={require('../../assets/images/p4u-logo-new.png')}
            style={styles.logo}
            resizeMode="contain"
          />
          
          <Text style={styles.title}>Unlock Premium</Text>
          <Text style={styles.subtitle}>Take your relationship to the next level</Text>
        </View>

        {/* Benefits */}
        <View style={styles.benefitsContainer}>
          <View style={styles.benefitItem}>
            <View style={styles.benefitIcon}>
              <Ionicons name="heart" size={24} color="#FF1493" />
            </View>
            <View style={styles.benefitText}>
              <Text style={styles.benefitTitle}>Romantic Tasks & Challenges</Text>
              <Text style={styles.benefitDescription}>AI-powered activities to strengthen your bond</Text>
            </View>
          </View>

          <View style={styles.benefitItem}>
            <View style={styles.benefitIcon}>
              <Ionicons name="gift" size={24} color="#FF1493" />
            </View>
            <View style={styles.benefitText}>
              <Text style={styles.benefitTitle}>₹1000 Cash Prize</Text>
              <Text style={styles.benefitDescription}>Monthly rewards for completing challenges</Text>
            </View>
          </View>

          <View style={styles.benefitItem}>
            <View style={styles.benefitIcon}>
              <Ionicons name="airplane" size={24} color="#FF1493" />
            </View>
            <View style={styles.benefitText}>
              <Text style={styles.benefitTitle}>Couple Trip Giveaway</Text>
              <Text style={styles.benefitDescription}>Win romantic getaways and experiences</Text>
            </View>
          </View>

          <View style={styles.benefitItem}>
            <View style={styles.benefitIcon}>
              <Ionicons name="bulb" size={24} color="#FF1493" />
            </View>
            <View style={styles.benefitText}>
              <Text style={styles.benefitTitle}>AI Insights</Text>
              <Text style={styles.benefitDescription}>Personalized relationship insights and tips</Text>
            </View>
          </View>

          <View style={styles.benefitItem}>
            <View style={styles.benefitIcon}>
              <Ionicons name="notifications" size={24} color="#FF1493" />
            </View>
            <View style={styles.benefitText}>
              <Text style={styles.benefitTitle}>Smart Reminders</Text>
              <Text style={styles.benefitDescription}>Never miss important dates and activities</Text>
            </View>
          </View>
        </View>

        {/* Pricing Plans */}
        <View style={styles.pricingContainer}>
          <Text style={styles.pricingTitle}>Choose Your Plan</Text>
          
          {/* Monthly Plan */}
          <TouchableOpacity
            style={[styles.planCard, selectedPlan === 'monthly' && styles.planCardSelected]}
            onPress={() => setSelectedPlan('monthly')}
            activeOpacity={0.8}
          >
            <View style={styles.planHeader}>
              <Text style={styles.planName}>Monthly</Text>
              <Text style={styles.planPrice}>₹79/month</Text>
            </View>
            <Text style={styles.planDescription}>Full access to all premium features</Text>
          </TouchableOpacity>

          {/* Yearly Plan */}
          <TouchableOpacity
            style={[styles.planCard, selectedPlan === 'yearly' && styles.planCardSelected]}
            onPress={() => setSelectedPlan('yearly')}
            activeOpacity={0.8}
          >
            <View style={styles.planHeader}>
              <Text style={styles.planName}>Yearly</Text>
              <View style={styles.yearlyPriceContainer}>
                <Text style={styles.planPrice}>₹948/year</Text>
                <View style={styles.saveBadge}>
                  <Text style={styles.saveText}>Save 50%</Text>
                </View>
              </View>
            </View>
            <Text style={styles.planDescription}>Best value - 2 months free!</Text>
          </TouchableOpacity>
        </View>

        {/* Action Buttons */}
        <View style={styles.buttonsContainer}>
          <TouchableOpacity
            style={styles.primaryButton}
            onPress={() => handleStartSubscription(selectedPlan)}
            activeOpacity={0.8}
          >
            <Text style={styles.primaryButtonText}>
              Start {selectedPlan === 'monthly' ? 'Monthly' : 'Yearly'} – ₹{selectedPlan === 'monthly' ? '79' : '948'}
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.trialButton}
            onPress={() => handleStartSubscription('trial')}
            activeOpacity={0.8}
          >
            <Text style={styles.trialButtonText}>Start 14-Day Free Trial</Text>
          </TouchableOpacity>

          <Text style={styles.disclaimer}>
            Cancel anytime. Terms and conditions apply.
          </Text>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FFFFFF',
  },
  content: {
    flexGrow: 1,
    paddingHorizontal: 24,
    paddingTop: 20,
    paddingBottom: 40,
  },
  
  // Header
  header: {
    alignItems: 'center',
    marginBottom: 40,
  },
  skipButton: {
    alignSelf: 'flex-end',
    paddingVertical: 8,
    paddingHorizontal: 16,
  },
  skipButtonText: {
    fontSize: 16,
    color: '#666666',
    fontWeight: '500',
  },
  logo: {
    width: 80,
    height: 80,
    marginBottom: 20,
  },
  title: {
    fontSize: 32,
    fontWeight: '700',
    color: '#1A1A1A',
    textAlign: 'center',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: '#666666',
    textAlign: 'center',
  },

  // Benefits
  benefitsContainer: {
    marginBottom: 40,
  },
  benefitItem: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 20,
  },
  benefitIcon: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: '#FFF0F5',
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 16,
  },
  benefitText: {
    flex: 1,
  },
  benefitTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1A1A1A',
    marginBottom: 4,
  },
  benefitDescription: {
    fontSize: 14,
    color: '#666666',
    lineHeight: 20,
  },

  // Pricing
  pricingContainer: {
    marginBottom: 40,
  },
  pricingTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: '#1A1A1A',
    textAlign: 'center',
    marginBottom: 24,
  },
  planCard: {
    backgroundColor: '#F8F9FA',
    borderRadius: 16,
    padding: 20,
    marginBottom: 12,
    borderWidth: 2,
    borderColor: 'transparent',
  },
  planCardSelected: {
    backgroundColor: '#FFF0F5',
    borderColor: '#FF1493',
  },
  planHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  planName: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1A1A1A',
  },
  planPrice: {
    fontSize: 18,
    fontWeight: '700',
    color: '#FF1493',
  },
  yearlyPriceContainer: {
    alignItems: 'flex-end',
  },
  saveBadge: {
    backgroundColor: '#FF1493',
    borderRadius: 12,
    paddingHorizontal: 8,
    paddingVertical: 4,
    marginTop: 4,
  },
  saveText: {
    fontSize: 12,
    color: '#FFFFFF',
    fontWeight: '600',
  },
  planDescription: {
    fontSize: 14,
    color: '#666666',
  },

  // Buttons
  buttonsContainer: {
    marginTop: 'auto',
  },
  primaryButton: {
    backgroundColor: '#FF1493',
    borderRadius: 12,
    paddingVertical: 16,
    alignItems: 'center',
    marginBottom: 12,
  },
  primaryButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
  trialButton: {
    backgroundColor: '#F8F9FA',
    borderRadius: 12,
    paddingVertical: 16,
    alignItems: 'center',
    borderWidth: 2,
    borderColor: '#FF1493',
    marginBottom: 20,
  },
  trialButtonText: {
    color: '#FF1493',
    fontSize: 16,
    fontWeight: '600',
  },
  disclaimer: {
    fontSize: 12,
    color: '#999999',
    textAlign: 'center',
    lineHeight: 18,
  },
});

export default SubscriptionScreen;