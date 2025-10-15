import React, { useState } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  ScrollView,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';
import * as Haptics from 'expo-haptics';

interface SubscriptionOnboardingScreenProps {
  onComplete: (subscriptionType: 'trial' | 'monthly' | 'half_yearly' | 'skip') => void;
}

export default function SubscriptionOnboardingScreen({ onComplete }: SubscriptionOnboardingScreenProps) {
  const [loading, setLoading] = useState(false);

  const handleSubscriptionChoice = async (type: 'trial' | 'monthly' | 'half_yearly' | 'skip') => {
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
    
    if (type === 'skip') {
      Alert.alert(
        'Start Free Trial?',
        'You can start your 14-day free trial anytime from your profile.',
        [
          { text: 'Cancel', style: 'cancel' },
          { 
            text: 'Continue', 
            onPress: () => onComplete(type),
            style: 'default'
          },
        ]
      );
      return;
    }

    setLoading(true);
    onComplete(type);
    setLoading(false);
  };

  return (
    <SafeAreaView style={styles.container}>
      <LinearGradient
        colors={['#FF1493', '#FF69B4', '#FFB6C1']}
        style={styles.gradient}
      >
        <ScrollView 
          contentContainerStyle={styles.scrollContent}
          showsVerticalScrollIndicator={false}
        >
          {/* Header */}
          <View style={styles.header}>
            <Ionicons name="heart" size={48} color="#FFF" />
            <Text style={styles.title}>Choose Your Plan</Text>
            <Text style={styles.subtitle}>
              Unlock premium features to strengthen your relationship
            </Text>
          </View>

          {/* Free Trial Card - Highlighted */}
          <TouchableOpacity
            style={[styles.planCard, styles.highlightedCard]}
            onPress={() => handleSubscriptionChoice('trial')}
            disabled={loading}
            activeOpacity={0.8}
          >
            <View style={styles.recommendedBadge}>
              <Text style={styles.recommendedText}>RECOMMENDED</Text>
            </View>
            <View style={styles.planHeader}>
              <Ionicons name="gift-outline" size={32} color="#FF1493" />
              <Text style={styles.planName}>14-Day Free Trial</Text>
            </View>
            <Text style={styles.planPrice}>₹0</Text>
            <Text style={styles.planPeriod}>First 14 days free</Text>
            <Text style={styles.planDescription}>
              Try all premium features risk-free. Cancel anytime before trial ends.
            </Text>
            <View style={styles.featuresContainer}>
              <FeatureItem text="AI-powered personalized messages" />
              <FeatureItem text="Smart gift recommendations" />
              <FeatureItem text="AI date planner" />
              <FeatureItem text="Unlimited relationship tasks" />
              <FeatureItem text="Event reminders & calendar" />
              <FeatureItem text="Gamification & rewards" />
            </View>
            <View style={styles.ctaButton}>
              <Text style={styles.ctaButtonText}>Start Free Trial</Text>
              <Ionicons name="arrow-forward" size={20} color="#FFF" />
            </View>
          </TouchableOpacity>

          {/* Monthly Plan */}
          <TouchableOpacity
            style={styles.planCard}
            onPress={() => handleSubscriptionChoice('monthly')}
            disabled={loading}
            activeOpacity={0.8}
          >
            <View style={styles.planHeader}>
              <Ionicons name="calendar-outline" size={28} color="#666" />
              <Text style={styles.planNameSecondary}>Monthly Plan</Text>
            </View>
            <Text style={styles.planPrice}>₹79</Text>
            <Text style={styles.planPeriod}>per month</Text>
            <Text style={styles.planDescription}>
              Full access to all premium features. Billed monthly.
            </Text>
            <View style={styles.secondaryButton}>
              <Text style={styles.secondaryButtonText}>Subscribe Now</Text>
            </View>
          </TouchableOpacity>

          {/* Half-Yearly Plan - Best Value */}
          <TouchableOpacity
            style={styles.planCard}
            onPress={() => handleSubscriptionChoice('half_yearly')}
            disabled={loading}
            activeOpacity={0.8}
          >
            <View style={styles.valueBadge}>
              <Text style={styles.valueText}>BEST VALUE</Text>
            </View>
            <View style={styles.planHeader}>
              <Ionicons name="sparkles-outline" size={28} color="#666" />
              <Text style={styles.planNameSecondary}>6-Month Plan</Text>
            </View>
            <Text style={styles.planPrice}>₹450</Text>
            <Text style={styles.planPeriod}>₹75/month • Save ₹24</Text>
            <Text style={styles.planDescription}>
              Best value! Get 6 months of premium features at a discounted rate.
            </Text>
            <View style={styles.secondaryButton}>
              <Text style={styles.secondaryButtonText}>Subscribe Now</Text>
            </View>
          </TouchableOpacity>

          {/* Skip Button */}
          <TouchableOpacity
            style={styles.skipButton}
            onPress={() => handleSubscriptionChoice('skip')}
            disabled={loading}
            activeOpacity={0.7}
          >
            <Text style={styles.skipButtonText}>
              I'll decide later
            </Text>
          </TouchableOpacity>

          {loading && (
            <View style={styles.loadingOverlay}>
              <ActivityIndicator size="large" color="#FF1493" />
            </View>
          )}
        </ScrollView>
      </LinearGradient>
    </SafeAreaView>
  );
}

interface FeatureItemProps {
  text: string;
}

function FeatureItem({ text }: FeatureItemProps) {
  return (
    <View style={styles.featureItem}>
      <Ionicons name="checkmark-circle" size={20} color="#FF1493" />
      <Text style={styles.featureText}>{text}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FF1493',
  },
  gradient: {
    flex: 1,
  },
  scrollContent: {
    padding: 20,
    paddingBottom: 40,
  },
  header: {
    alignItems: 'center',
    marginBottom: 32,
    marginTop: 20,
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#FFF',
    marginTop: 16,
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: '#FFF',
    textAlign: 'center',
    opacity: 0.9,
  },
  planCard: {
    backgroundColor: '#FFF',
    borderRadius: 16,
    padding: 24,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 12,
    elevation: 5,
  },
  highlightedCard: {
    borderWidth: 3,
    borderColor: '#FF1493',
    transform: [{ scale: 1.02 }],
  },
  recommendedBadge: {
    position: 'absolute',
    top: -12,
    right: 20,
    backgroundColor: '#FF1493',
    paddingHorizontal: 16,
    paddingVertical: 6,
    borderRadius: 20,
  },
  recommendedText: {
    color: '#FFF',
    fontWeight: 'bold',
    fontSize: 12,
    letterSpacing: 1,
  },
  valueBadge: {
    position: 'absolute',
    top: -12,
    right: 20,
    backgroundColor: '#FFA500',
    paddingHorizontal: 16,
    paddingVertical: 6,
    borderRadius: 20,
  },
  valueText: {
    color: '#FFF',
    fontWeight: 'bold',
    fontSize: 12,
    letterSpacing: 1,
  },
  planHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  planName: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#FF1493',
    marginLeft: 12,
  },
  planNameSecondary: {
    fontSize: 22,
    fontWeight: 'bold',
    color: '#333',
    marginLeft: 12,
  },
  planPrice: {
    fontSize: 48,
    fontWeight: 'bold',
    color: '#333',
    marginTop: 8,
  },
  planPeriod: {
    fontSize: 16,
    color: '#666',
    marginBottom: 12,
  },
  planDescription: {
    fontSize: 14,
    color: '#666',
    lineHeight: 20,
    marginBottom: 16,
  },
  featuresContainer: {
    marginTop: 8,
    marginBottom: 20,
  },
  featureItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 10,
  },
  featureText: {
    fontSize: 14,
    color: '#333',
    marginLeft: 10,
    flex: 1,
  },
  ctaButton: {
    backgroundColor: '#FF1493',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 16,
    borderRadius: 12,
    gap: 8,
  },
  ctaButtonText: {
    color: '#FFF',
    fontSize: 18,
    fontWeight: 'bold',
  },
  secondaryButton: {
    backgroundColor: '#F3F4F6',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 14,
    borderRadius: 12,
    marginTop: 8,
  },
  secondaryButtonText: {
    color: '#333',
    fontSize: 16,
    fontWeight: '600',
  },
  skipButton: {
    alignItems: 'center',
    paddingVertical: 16,
    marginTop: 8,
  },
  skipButtonText: {
    color: '#FFF',
    fontSize: 16,
    opacity: 0.8,
  },
  loadingOverlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0,0,0,0.3)',
    justifyContent: 'center',
    alignItems: 'center',
  },
});
