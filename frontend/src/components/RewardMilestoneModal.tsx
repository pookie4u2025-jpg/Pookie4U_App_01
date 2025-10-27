import React, { useState, useRef } from 'react';
import {
  View,
  Text,
  Modal,
  TouchableOpacity,
  TextInput,
  StyleSheet,
  Alert,
  ActivityIndicator,
  ScrollView
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

type RewardType = 'upi_transfer' | 'gift_coupon';

export const RewardMilestoneModal: React.FC<RewardMilestoneModalProps> = ({
  visible,
  onClose,
  currentPoints,
  onRedeemSuccess
}) => {
  const [selectedReward, setSelectedReward] = useState<RewardType | null>(null);
  const [upiId, setUpiId] = useState('');
  const [loading, setLoading] = useState(false);
  const [showConfetti, setShowConfetti] = useState(false);
  const confettiRef = useRef<any>(null);
  const { token } = useAuthStore();

  const handleRewardSelect = (type: RewardType) => {
    setSelectedReward(type);
  };

  const handleRedeem = async () => {
    if (!selectedReward) {
      Alert.alert('Error', 'Please select a reward option');
      return;
    }

    if (selectedReward === 'upi_transfer' && !upiId.trim()) {
      Alert.alert('Error', 'Please enter your UPI ID');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(
        `${process.env.EXPO_PUBLIC_BACKEND_URL}/api/rewards/redeem`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({
            reward_type: selectedReward,
            upi_id: selectedReward === 'upi_transfer' ? upiId.trim() : undefined,
            amount: 100
          })
        }
      );

      const data = await response.json();

      if (response.ok && data.success) {
        // Trigger confetti
        setShowConfetti(true);
        setTimeout(() => setShowConfetti(false), 3000);

        // Show success message
        Alert.alert(
          '🎉 Congratulations!',
          data.message,
          [
            {
              text: 'OK',
              onPress: () => {
                onRedeemSuccess(data.remaining_points);
                resetAndClose();
              }
            }
          ]
        );
      } else {
        throw new Error(data.detail || 'Failed to redeem reward');
      }
    } catch (error: any) {
      console.error('Redemption error:', error);
      Alert.alert('Error', error.message || 'Failed to redeem reward');
    } finally {
      setLoading(false);
    }
  };

  const resetAndClose = () => {
    setSelectedReward(null);
    setUpiId('');
    onClose();
  };

  return (
    <>
      <Modal
        visible={visible}
        animationType="slide"
        transparent={true}
        onRequestClose={resetAndClose}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContainer}>
            {/* Celebration Header */}
            <View style={styles.header}>
              <View style={styles.trophy}>
                <Ionicons name="trophy" size={60} color="#FFD700" />
              </View>
              <Text style={styles.congratsText}>🎉 Congratulations! 🎉</Text>
              <Text style={styles.milestoneText}>
                You reached {currentPoints} points!
              </Text>
              <Text style={styles.subtitle}>
                Choose your prize 🎁
              </Text>
            </View>

            <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
              {/* Reward Options */}
              <TouchableOpacity
                style={[
                  styles.rewardOption,
                  selectedReward === 'upi_transfer' && styles.selectedOption
                ]}
                onPress={() => handleRewardSelect('upi_transfer')}
              >
                <View style={styles.rewardIconContainer}>
                  <Ionicons name="cash" size={32} color="#4CAF50" />
                </View>
                <View style={styles.rewardInfo}>
                  <Text style={styles.rewardTitle}>Redeem ₹100 via UPI</Text>
                  <Text style={styles.rewardDescription}>
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
