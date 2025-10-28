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
                    Get cash transferred to your UPI ID
                  </Text>
                  <Text style={styles.rewardNote}>
                    ⚠️ Requires admin approval (24-48 hours)
                  </Text>
                </View>
                {selectedReward === 'upi_transfer' && (
                  <Ionicons name="checkmark-circle" size={24} color="#4CAF50" />
                )}
              </TouchableOpacity>

              {selectedReward === 'upi_transfer' && (
                <View style={styles.upiInputContainer}>
                  <Text style={styles.inputLabel}>Enter UPI ID *</Text>
                  <TextInput
                    style={styles.textInput}
                    placeholder="yourname@upi"
                    placeholderTextColor="#999"
                    value={upiId}
                    onChangeText={setUpiId}
                    autoCapitalize="none"
                    keyboardType="email-address"
                  />
                </View>
              )}

              <TouchableOpacity
                style={[
                  styles.rewardOption,
                  selectedReward === 'gift_coupon' && styles.selectedOption
                ]}
                onPress={() => handleRewardSelect('gift_coupon')}
              >
                <View style={styles.rewardIconContainer}>
                  <Ionicons name="gift" size={32} color="#FF1493" />
                </View>
                <View style={styles.rewardInfo}>
                  <Text style={styles.rewardTitle}>Get a Gift Coupon</Text>
                  <Text style={styles.rewardDescription}>
                    Instant coupon code for gifts & shopping
                  </Text>
                  <Text style={styles.rewardNote}>
                    ✅ Instant approval - no waiting!
                  </Text>
                </View>
                {selectedReward === 'gift_coupon' && (
                  <Ionicons name="checkmark-circle" size={24} color="#FF1493" />
                )}
              </TouchableOpacity>

              {/* Info Box */}
              <View style={styles.infoBox}>
                <Ionicons name="information-circle" size={20} color="#2196F3" />
                <Text style={styles.infoText}>
                  After redemption, 1000 points will be deducted and you'll keep the remainder. You can earn more points and redeem again!
                </Text>
              </View>
            </ScrollView>

            {/* Action Buttons */}
            <View style={styles.buttonContainer}>
              <TouchableOpacity
                style={styles.cancelButton}
                onPress={resetAndClose}
              >
                <Text style={styles.cancelButtonText}>Maybe Later</Text>
              </TouchableOpacity>

              <TouchableOpacity
                style={[
                  styles.redeemButton,
                  (!selectedReward || loading) && styles.redeemButtonDisabled
                ]}
                onPress={handleRedeem}
                disabled={!selectedReward || loading}
              >
                {loading ? (
                  <ActivityIndicator color="#fff" />
                ) : (
                  <>
                    <Ionicons name="gift" size={20} color="#fff" />
                    <Text style={styles.redeemButtonText}>Redeem Now</Text>
                  </>
                )}
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>

      {/* Confetti Animation */}
      {showConfetti && (
        <ConfettiCannon
          ref={confettiRef}
          count={200}
          origin={{ x: -10, y: 0 }}
          autoStart={true}
          fadeOut={true}
          explosionSpeed={350}
          fallSpeed={3000}
        />
      )}
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
  rewardOption: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    borderRadius: 16,
    borderWidth: 2,
    borderColor: '#E0E0E0',
    marginBottom: 16,
    backgroundColor: '#F9F9F9'
  },
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
