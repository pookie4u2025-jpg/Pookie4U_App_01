import React, { useState, useEffect, useRef } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Share,
  Alert,
  ActivityIndicator,
  Clipboard,
  ScrollView
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import ConfettiCannon from 'react-native-confetti-cannon';
import { useAuthStore } from '../stores/useAuthStore';
import { RewardMilestoneModal } from './RewardMilestoneModal';

interface ReferralData {
  code: string;
  referrals_count: number;
  points_earned: number;
}

interface ReferralCardProps {
  theme: any;
}

export const ReferralCard: React.FC<ReferralCardProps> = ({ theme }) => {
  const [referralData, setReferralData] = useState<ReferralData | null>(null);
  const [loading, setLoading] = useState(true);
  const [showConfetti, setShowConfetti] = useState(false);
  const [currentPoints, setCurrentPoints] = useState(0);
  const [showMilestoneModal, setShowMilestoneModal] = useState(false);
  const confettiRef = useRef<any>(null);
  const { token, user } = useAuthStore();

  useEffect(() => {
    fetchReferralCode();
    checkMilestone();
  }, []);

  const checkMilestone = async () => {
    try {
      const response = await fetch(
        `${process.env.EXPO_PUBLIC_BACKEND_URL}/api/rewards/check-milestone`,
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );

      const data = await response.json();
      if (response.ok && data.success) {
        setCurrentPoints(data.current_points);
        // Auto-show milestone modal if eligible
        if (data.eligible && data.current_points >= 1000) {
          setTimeout(() => setShowMilestoneModal(true), 1000);
        }
      }
    } catch (error) {
      console.error('Error checking milestone:', error);
    }
  };

  const fetchReferralCode = async () => {
    try {
      setLoading(true);
      const response = await fetch(
        `${process.env.EXPO_PUBLIC_BACKEND_URL}/api/referral/my-code`,
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );

      const data = await response.json();
      if (response.ok && data.success) {
        setReferralData(data);
      }
    } catch (error) {
      console.error('Error fetching referral code:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCopyCode = async () => {
    if (referralData?.code) {
      await Clipboard.setString(referralData.code);
      Alert.alert('Copied!', 'Referral code copied to clipboard 📋');
    }
  };

  const handleShare = async () => {
    try {
      const message = `Join me on Pookie4U - the best app for couples! 💕\n\nUse my referral code: ${referralData?.code}\n\nWe'll both get 50 points when you sign up! 🎁`;
      
      await Share.share({
        message,
        title: 'Join Pookie4U'
      });
    } catch (error) {
      console.error('Error sharing:', error);
    }
  };

  if (loading) {
    return (
      <View style={[styles.card, { backgroundColor: theme.surface }]}>
        <ActivityIndicator size="small" color={theme.primary} />
      </View>
    );
  }

  return (
    <>
      <View style={[styles.card, { backgroundColor: theme.surface }]}>
        <View style={styles.header}>
          <View style={styles.titleContainer}>
            <Ionicons name="gift" size={24} color="#FFD700" />
            <Text style={[styles.title, { color: theme.text }]}>
              Invite & Earn
            </Text>
          </View>
          <View style={[styles.badge, { backgroundColor: theme.primary + '20' }]}>
            <Text style={[styles.badgeText, { color: theme.primary }]}>
              50 pts each
            </Text>
          </View>
        </View>

        <Text style={[styles.description, { color: theme.textSecondary }]}>
          Invite friends and you both earn 50 points!
        </Text>

        {/* Referral Code Display */}
        <View style={[styles.codeContainer, { backgroundColor: theme.background }]}>
          <View>
            <Text style={[styles.codeLabel, { color: theme.textSecondary }]}>
              Your Referral Code
            </Text>
            <Text style={[styles.code, { color: theme.primary }]}>
              {referralData?.code || 'Loading...'}
            </Text>
          </View>
          <TouchableOpacity
            style={[styles.copyButton, { backgroundColor: theme.primary }]}
            onPress={handleCopyCode}
          >
            <Ionicons name="copy" size={20} color="#fff" />
          </TouchableOpacity>
        </View>

        {/* Stats */}
        <View style={styles.statsContainer}>
          <View style={styles.statItem}>
            <Text style={[styles.statValue, { color: theme.text }]}>
              {referralData?.referrals_count || 0}
            </Text>
            <Text style={[styles.statLabel, { color: theme.textSecondary }]}>
              Referrals
            </Text>
          </View>
          <View style={[styles.divider, { backgroundColor: theme.border }]} />
          <View style={styles.statItem}>
            <Text style={[styles.statValue, { color: '#FFD700' }]}>
              {referralData?.points_earned || 0}
            </Text>
            <Text style={[styles.statLabel, { color: theme.textSecondary }]}>
              Points Earned
            </Text>
          </View>
        </View>

        {/* Share Button */}
        <TouchableOpacity
          style={[styles.shareButton, { backgroundColor: theme.primary }]}
          onPress={handleShare}
        >
          <Ionicons name="share-social" size={20} color="#fff" />
          <Text style={styles.shareButtonText}>Share with Friends</Text>
        </TouchableOpacity>

        {/* How it Works */}
        <View style={styles.howItWorks}>
          <Text style={[styles.howItWorksTitle, { color: theme.text }]}>
            How it works:
          </Text>
          <View style={styles.step}>
            <Ionicons name="share-social-outline" size={16} color={theme.primary} />
            <Text style={[styles.stepText, { color: theme.textSecondary }]}>
              Share your unique code with friends
            </Text>
          </View>
          <View style={styles.step}>
            <Ionicons name="person-add-outline" size={16} color={theme.primary} />
            <Text style={[styles.stepText, { color: theme.textSecondary }]}>
              They sign up using your code
            </Text>
          </View>
          <View style={styles.step}>
            <Ionicons name="star-outline" size={16} color={theme.primary} />
            <Text style={[styles.stepText, { color: theme.textSecondary }]}>
              You both get 50 points instantly!
            </Text>
          </View>
        </View>
      </View>

      {/* Confetti Animation */}
      {showConfetti && (
        <ConfettiCannon
          ref={confettiRef}
          count={200}
          origin={{ x: -10, y: 0 }}
          autoStart={true}
          fadeOut={true}
          onAnimationEnd={() => setShowConfetti(false)}
        />
      )}
    </>
  );
};

const styles = StyleSheet.create({
  card: {
    borderRadius: 16,
    padding: 20,
    margin: 16,
    marginTop: 0,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8
  },
  titleContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8
  },
  title: {
    fontSize: 20,
    fontWeight: 'bold'
  },
  badge: {
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 12
  },
  badgeText: {
    fontSize: 12,
    fontWeight: 'bold'
  },
  description: {
    fontSize: 14,
    marginBottom: 16,
    lineHeight: 20
  },
  codeContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    borderRadius: 12,
    marginBottom: 16
  },
  codeLabel: {
    fontSize: 12,
    marginBottom: 4
  },
  code: {
    fontSize: 24,
    fontWeight: 'bold',
    letterSpacing: 2
  },
  copyButton: {
    width: 44,
    height: 44,
    borderRadius: 22,
    justifyContent: 'center',
    alignItems: 'center'
  },
  statsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginBottom: 16
  },
  statItem: {
    alignItems: 'center',
    flex: 1
  },
  statValue: {
    fontSize: 28,
    fontWeight: 'bold'
  },
  statLabel: {
    fontSize: 12,
    marginTop: 4
  },
  divider: {
    width: 1,
    height: '100%'
  },
  shareButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 16,
    borderRadius: 12,
    gap: 8,
    marginBottom: 16
  },
  shareButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold'
  },
  howItWorks: {
    marginTop: 8
  },
  howItWorksTitle: {
    fontSize: 14,
    fontWeight: 'bold',
    marginBottom: 12
  },
  step: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    marginBottom: 8
  },
  stepText: {
    fontSize: 13,
    flex: 1
  }
});
