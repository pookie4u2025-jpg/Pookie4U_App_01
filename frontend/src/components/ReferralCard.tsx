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
import { useGameStore } from '../stores/useGameStore';

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
  const { totalPoints } = useGameStore(); // Get task points from game store

  useEffect(() => {
    if (token && user) {
      fetchReferralCode();
      fetchUserPoints();
    } else {
      // No valid auth, show default data
      setReferralData({
        code: 'N/A',
        referrals_count: 0,
        points_earned: 0
      });
      setCurrentPoints(totalPoints);
      setLoading(false);
    }
  }, [token, user]);

  const fetchUserPoints = async () => {
    try {
      // Fetch user profile to get total_points which includes task completion points
      const response = await fetch(
        `${process.env.EXPO_PUBLIC_BACKEND_URL}/api/user/profile`,
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );

      if (response.ok) {
        const data = await response.json();
        // total_points includes both task and referral points
        const totalUserPoints = data.total_points || 0;
        setCurrentPoints(totalUserPoints);
        
        // Check if eligible for milestone (1000 points)
        if (totalUserPoints >= 1000) {
          setTimeout(() => setShowMilestoneModal(true), 1000);
        }
      } else if (response.status === 401) {
        console.log('Auth token expired or invalid');
        setCurrentPoints(totalPoints);
      } else {
        console.log('Failed to fetch user points, using game store points');
        setCurrentPoints(totalPoints);
      }
    } catch (error) {
      console.error('Error fetching user points:', error);
      // Fallback to game store points
      setCurrentPoints(totalPoints);
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

      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          setReferralData(data);
        } else {
          setReferralData({
            code: 'N/A',
            referrals_count: 0,
            points_earned: 0
          });
        }
      } else if (response.status === 401) {
        console.log('Auth token expired or invalid for referral code');
        setReferralData({
          code: 'AUTH_ERROR',
          referrals_count: 0,
          points_earned: 0
        });
      } else {
        console.log('Referral endpoint failed, using defaults');
        setReferralData({
          code: 'N/A',
          referrals_count: 0,
          points_earned: 0
        });
      }
    } catch (error) {
      console.error('Error fetching referral code:', error);
      setReferralData({
        code: 'ERROR',
        referrals_count: 0,
        points_earned: 0
      });
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

        {/* Current Points Progress */}
        <View style={[styles.progressContainer, { backgroundColor: theme.background }]}>
          <View style={styles.progressHeader}>
            <Text style={[styles.progressLabel, { color: theme.textSecondary }]}>
              Your Points
            </Text>
            <Text style={[styles.progressPoints, { color: '#FFD700' }]}>
              {currentPoints} / 1000
            </Text>
          </View>
          <View style={styles.progressBarContainer}>
            <View 
              style={[
                styles.progressBar, 
                { width: `${Math.min((currentPoints / 1000) * 100, 100)}%` }
              ]} 
            />
          </View>
          {currentPoints >= 1000 && (
            <TouchableOpacity 
              style={styles.redeemBanner}
              onPress={() => setShowMilestoneModal(true)}
            >
              <Ionicons name="trophy" size={20} color="#FFD700" />
              <Text style={styles.redeemBannerText}>
                🎉 You can redeem a reward! Tap here
              </Text>
            </TouchableOpacity>
          )}
        </View>

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

      {/* Reward Milestone Modal */}
      <RewardMilestoneModal
        visible={showMilestoneModal}
        onClose={() => setShowMilestoneModal(false)}
        currentPoints={currentPoints}
        onRedeemSuccess={(remainingPoints) => {
          setCurrentPoints(remainingPoints);
          checkMilestone();
        }}
      />
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
  progressContainer: {
    padding: 16,
    borderRadius: 12,
    marginBottom: 16
  },
  progressHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8
  },
  progressLabel: {
    fontSize: 14,
    fontWeight: '600'
  },
  progressPoints: {
    fontSize: 18,
    fontWeight: 'bold'
  },
  progressBarContainer: {
    height: 8,
    backgroundColor: '#E0E0E0',
    borderRadius: 4,
    overflow: 'hidden'
  },
  progressBar: {
    height: '100%',
    backgroundColor: '#FFD700',
    borderRadius: 4
  },
  redeemBanner: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 12,
    padding: 12,
    backgroundColor: '#FFF8DC',
    borderRadius: 8,
    gap: 8
  },
  redeemBannerText: {
    fontSize: 14,
    color: '#FF8C00',
    fontWeight: 'bold'
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
