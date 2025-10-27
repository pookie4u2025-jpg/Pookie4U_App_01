import React, { useState } from 'react';
import {
  View,
  Text,
  Modal,
  TouchableOpacity,
  TextInput,
  StyleSheet,
  Alert,
  ActivityIndicator
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useAuthStore } from '../stores/useAuthStore';

interface ApplyReferralModalProps {
  visible: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export const ApplyReferralModal: React.FC<ApplyReferralModalProps> = ({
  visible,
  onClose,
  onSuccess
}) => {
  const [referralCode, setReferralCode] = useState('');
  const [loading, setLoading] = useState(false);
  const { token } = useAuthStore();

  const handleApply = async () => {
    if (!referralCode.trim()) {
      Alert.alert('Error', 'Please enter a referral code');
      return;
    }

    // Validate format POO-XXXXXX
    const codeRegex = /^POO-[A-Z0-9]{6}$/;
    if (!codeRegex.test(referralCode.trim().toUpperCase())) {
      Alert.alert('Invalid Code', 'Referral code must be in format: POO-XXXXXX');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(
        `${process.env.EXPO_PUBLIC_BACKEND_URL}/api/referral/apply`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({
            code: referralCode.trim().toUpperCase()
          })
        }
      );

      const data = await response.json();

      if (response.ok && data.success) {
        Alert.alert(
          '🎉 Success!',
          data.message,
          [
            {
              text: 'OK',
              onPress: () => {
                onSuccess();
                onClose();
              }
            }
          ]
        );
      } else {
        throw new Error(data.detail || 'Failed to apply referral code');
      }
    } catch (error: any) {
      console.error('Apply referral error:', error);
      Alert.alert('Error', error.message || 'Failed to apply referral code');
    } finally {
      setLoading(false);
    }
  };

  const handleSkip = () => {
    Alert.alert(
      'Skip Referral',
      'You can only apply a referral code once. Are you sure you want to skip?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Skip',
          style: 'destructive',
          onPress: onClose
        }
      ]
    );
  };

  return (
    <Modal
      visible={visible}
      animationType="slide"
      transparent={true}
      onRequestClose={handleSkip}
    >
      <View style={styles.modalOverlay}>
        <View style={styles.modalContainer}>
          <TouchableOpacity style={styles.skipButton} onPress={handleSkip}>
            <Text style={styles.skipText}>Skip</Text>
          </TouchableOpacity>

          <View style={styles.header}>
            <Ionicons name="gift" size={64} color="#FF1493" />
            <Text style={styles.title}>Got a Referral Code?</Text>
            <Text style={styles.subtitle}>
              Enter your friend's code and you both get 50 points! 🎉
            </Text>
          </View>

          <View style={styles.content}>
            <Text style={styles.label}>Referral Code</Text>
            <TextInput
              style={styles.input}
              placeholder="POO-XXXXXX"
              placeholderTextColor="#999"
              value={referralCode}
              onChangeText={(text) => setReferralCode(text.toUpperCase())}
              autoCapitalize="characters"
              maxLength={10}
              autoCorrect={false}
            />

            <View style={styles.infoBox}>
              <Ionicons name="information-circle" size={20} color="#2196F3" />
              <Text style={styles.infoText}>
                You can only apply a referral code within 24 hours of registration
              </Text>
            </View>

            <TouchableOpacity
              style={[styles.applyButton, loading && styles.applyButtonDisabled]}
              onPress={handleApply}
              disabled={loading}
            >
              {loading ? (
                <ActivityIndicator color="#fff" />
              ) : (
                <>
                  <Ionicons name="checkmark-circle" size={20} color="#fff" />
                  <Text style={styles.applyButtonText}>Apply Code</Text>
                </>
              )}
            </TouchableOpacity>
          </View>
        </View>
      </View>
    </Modal>
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
    maxWidth: 400,
    padding: 24
  },
  skipButton: {
    alignSelf: 'flex-end',
    padding: 8
  },
  skipText: {
    color: '#999',
    fontSize: 16
  },
  header: {
    alignItems: 'center',
    marginBottom: 24
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginTop: 16,
    marginBottom: 8,
    textAlign: 'center'
  },
  subtitle: {
    fontSize: 14,
    color: '#666',
    textAlign: 'center',
    lineHeight: 20
  },
  content: {
    width: '100%'
  },
  label: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 8
  },
  input: {
    borderWidth: 2,
    borderColor: '#FF1493',
    borderRadius: 12,
    padding: 16,
    fontSize: 18,
    color: '#333',
    textAlign: 'center',
    letterSpacing: 2,
    fontWeight: 'bold',
    marginBottom: 16
  },
  infoBox: {
    flexDirection: 'row',
    padding: 12,
    backgroundColor: '#E3F2FD',
    borderRadius: 12,
    marginBottom: 24
  },
  infoText: {
    fontSize: 12,
    color: '#1976D2',
    marginLeft: 8,
    flex: 1,
    lineHeight: 16
  },
  applyButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#FF1493',
    padding: 16,
    borderRadius: 12,
    gap: 8
  },
  applyButtonDisabled: {
    opacity: 0.6
  },
  applyButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold'
  }
});
