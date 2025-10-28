import React, { useState, useRef, useEffect } from 'react';
import {
  View,
  Text,
  Modal,
  TouchableOpacity,
  StyleSheet,
  Alert,
  ScrollView,
  Clipboard
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import ConfettiCannon from 'react-native-confetti-cannon';
import { useAuthStore } from '../stores/useAuthStore';

interface RewardMilestoneModalProps {
  visible: boolean;
  onClose: () => void;
  currentPoints: number;
  onRedeemSuccess: (remainingPoints: number) => void;
}

export const RewardMilestoneModal: React.FC<RewardMilestoneModalProps> = ({
  visible,
  onClose,
  currentPoints,
  onRedeemSuccess
}) => {
  const [newCoupons, setNewCoupons] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const confettiRef = useRef<any>(null);
  const { token } = useAuthStore();

  useEffect(() => {
    if (visible) {
      fetchNewCoupons();
    }
  }, [visible]);

  const fetchNewCoupons = async () => {
    try {
      setLoading(true);
      const response = await fetch(
        `${process.env.EXPO_PUBLIC_BACKEND_URL}/api/rewards/check-milestone`,
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );

      if (response.ok) {
        const data = await response.json();
        if (data.new_coupons && data.new_coupons.length > 0) {
          setNewCoupons(data.new_coupons);
        } else {
          // No new coupons, fetch recent ones
          fetchRecentCoupons();
        }
      }
    } catch (error) {
      console.error('Error fetching coupons:', error);
      Alert.alert('Error', 'Failed to load coupons');
    } finally {
      setLoading(false);
    }
  };

  const fetchRecentCoupons = async () => {
    try {
      const response = await fetch(
        `${process.env.EXPO_PUBLIC_BACKEND_URL}/api/rewards/history`,
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );

      if (response.ok) {
        const data = await response.json();
        // Show last 3 coupons
        const recent = data.rewards.slice(0, 3).map((r: any) => ({
          coupon_code: r.coupon_code,
          milestone: r.milestone_number
        }));
        setNewCoupons(recent);
      }
    } catch (error) {
      console.error('Error fetching reward history:', error);
    }
  };

  const handleCopyCoupon = async (couponCode: string) => {
    await Clipboard.setString(couponCode);
    Alert.alert('Copied!', 'Coupon code copied to clipboard 📋');
  };

  const handleClose = () => {

  return (
    <>
      <Modal
        visible={visible}
        animationType="slide"
        transparent={true}
        onRequestClose={handleClose}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContainer}>
            {/* Celebration Header */}
            <View style={styles.header}>
              <View style={styles.trophy}>
                <Ionicons name="trophy" size={60} color="#FFD700" />
              </View>
              <Text style={styles.congratsText}>🎉 Milestone Reached! 🎉</Text>
              <Text style={styles.milestoneText}>
                {Math.floor(currentPoints / 1000)} Gift Coupon{Math.floor(currentPoints / 1000) !== 1 ? 's' : ''} Earned!
              </Text>
              <Text style={styles.subtitle}>
                Your Total Points: {currentPoints} 💎
              </Text>
            </View>

            <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
              {loading ? (
                <View style={styles.loadingContainer}>
                  <Text style={styles.loadingText}>Loading your rewards...</Text>
                </View>
              ) : newCoupons.length > 0 ? (
                <>
                  <Text style={styles.sectionTitle}>Your Gift Coupons:</Text>
                  {newCoupons.map((coupon, index) => (
                    <View key={index} style={styles.couponCard}>
                      <View style={styles.couponHeader}>
                        <Ionicons name="gift" size={24} color="#FF1493" />
                        <Text style={styles.couponMilestone}>
                          Milestone #{coupon.milestone}
                        </Text>
                      </View>
                      <View style={styles.couponCodeContainer}>
                        <Text style={styles.couponCode}>{coupon.coupon_code}</Text>
                        <TouchableOpacity
                          style={styles.copyButton}
                          onPress={() => handleCopyCoupon(coupon.coupon_code)}
                        >
                          <Ionicons name="copy" size={20} color="#FF1493" />
                        </TouchableOpacity>
                      </View>
                      <Text style={styles.couponNote}>
                        Use this code for special gifts! 🎁
                      </Text>
                    </View>
                  ))}
                </>
              ) : (
                <Text style={styles.noCouponsText}>No coupons available yet</Text>
              )}

              <View style={styles.infoBox}>
                <Ionicons name="information-circle" size={24} color="#2196F3" />
                <Text style={styles.infoText}>
                  Keep earning points! Every 1000 points = 1 new gift coupon automatically 🎉
                </Text>
              </View>
            </ScrollView>

            {/* Close Button */}
            <TouchableOpacity
              style={styles.closeButton}
              onPress={handleClose}
            >
              <Text style={styles.closeButtonText}>Got it!</Text>
            </TouchableOpacity>
          </View>
        </View>
      </Modal>

      {/* Confetti Animation */}
      <ConfettiCannon
        ref={confettiRef}
        count={200}
        origin={{ x: -10, y: 0 }}
        autoStart={visible}
        fadeOut={true}
      />
    </>
  );
};

const styles = StyleSheet.create({
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.7)',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20
  },
  modalContainer: {
    backgroundColor: '#fff',
    borderRadius: 24,
    width: '100%',
    maxWidth: 500,
    maxHeight: '90%',
    overflow: 'hidden'
  },
  header: {
    alignItems: 'center',
    padding: 24,
    backgroundColor: '#FFF8DC'
  },
  trophy: {
    marginBottom: 16
  },
  congratsText: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    textAlign: 'center',
    marginBottom: 8
  },
  milestoneText: {
    fontSize: 18,
    color: '#666',
    textAlign: 'center',
    marginBottom: 8
  },
  subtitle: {
    fontSize: 16,
    color: '#FF1493',
    fontWeight: '600'
  },
  content: {
    padding: 20
  },
  loadingContainer: {
    padding: 40,
    alignItems: 'center'
  },
  loadingText: {
    fontSize: 16,
    color: '#666',
    marginTop: 10
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 16
  },
  couponCard: {
    backgroundColor: '#FFF8DC',
    borderRadius: 16,
    padding: 16,
    marginBottom: 12,
    borderWidth: 2,
    borderColor: '#FFD700'
  },
  couponHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12
  },
  couponMilestone: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#FF1493',
    marginLeft: 8
  },
  couponCodeContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#fff',
    padding: 12,
    borderRadius: 8,
    marginBottom: 8
  },
  couponCode: {
    flex: 1,
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    fontFamily: 'monospace'
  },
  copyButton: {
    padding: 8
  },
  couponNote: {
    fontSize: 12,
    color: '#666',
    fontStyle: 'italic'
  },
  noCouponsText: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
    padding: 40
  },
  infoBox: {
    flexDirection: 'row',
    backgroundColor: '#E3F2FD',
    padding: 16,
    borderRadius: 12,
    marginTop: 16,
    gap: 12
  },
  infoText: {
    flex: 1,
    fontSize: 14,
    color: '#1976D2',
    lineHeight: 20
  },
  closeButton: {
    backgroundColor: '#FF1493',
    margin: 20,
    padding: 16,
    borderRadius: 12,
    alignItems: 'center'
  },
  closeButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold'
  }
});
  selectedOption: {
    borderColor: '#FF1493',
    backgroundColor: '#FFE4F1'
  },
  rewardIconContainer: {
    marginRight: 16
  },
  rewardInfo: {
    flex: 1
  },
  rewardTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 4
  },
  rewardDescription: {
    fontSize: 14,
    color: '#666',
    marginBottom: 4
  },
  rewardNote: {
    fontSize: 12,
    color: '#999',
    fontStyle: 'italic'
  },
  upiInputContainer: {
    marginBottom: 16,
    marginTop: -8
  },
  inputLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
    marginBottom: 8
  },
  textInput: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 12,
    padding: 12,
    fontSize: 16,
    color: '#333',
    backgroundColor: '#fff'
  },
  infoBox: {
    flexDirection: 'row',
    padding: 16,
    backgroundColor: '#E3F2FD',
    borderRadius: 12,
    marginTop: 8
  },
  infoText: {
    fontSize: 13,
    color: '#1976D2',
    marginLeft: 8,
    flex: 1,
    lineHeight: 18
  },
  buttonContainer: {
    flexDirection: 'row',
    padding: 20,
    gap: 12,
    borderTopWidth: 1,
    borderTopColor: '#f0f0f0'
  },
  cancelButton: {
    flex: 1,
    padding: 16,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#ddd',
    alignItems: 'center'
  },
  cancelButtonText: {
    fontSize: 16,
    color: '#666',
    fontWeight: '600'
  },
  redeemButton: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 16,
    borderRadius: 12,
    backgroundColor: '#FF1493',
    gap: 8
  },
  redeemButtonDisabled: {
    opacity: 0.5
  },
  redeemButtonText: {
    fontSize: 16,
    color: '#fff',
    fontWeight: 'bold'
  }
});
