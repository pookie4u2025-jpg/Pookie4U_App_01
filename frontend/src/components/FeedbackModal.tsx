import React, { useState } from 'react';
import {
  View,
  Text,
  Modal,
  TouchableOpacity,
  TextInput,
  ScrollView,
  StyleSheet,
  Alert,
  Image,
  ActivityIndicator,
  Platform
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import * as ImagePicker from 'expo-image-picker';
import { useAuthStore } from '../stores/useAuthStore';

interface FeedbackModalProps {
  visible: boolean;
  onClose: () => void;
}

type FeedbackType = 'bug' | 'feature' | 'general';

export const FeedbackModal: React.FC<FeedbackModalProps> = ({ visible, onClose }) => {
  const [activeTab, setActiveTab] = useState<FeedbackType>('bug');
  const [message, setMessage] = useState('');
  const [email, setEmail] = useState('');
  const [images, setImages] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  
  const { token } = useAuthStore();

  const tabs: { id: FeedbackType; label: string; icon: string }[] = [
    { id: 'bug', label: 'Bug Report', icon: 'bug' },
    { id: 'feature', label: 'Feature Request', icon: 'bulb' },
    { id: 'general', label: 'General Feedback', icon: 'chatbubbles' }
  ];

  const pickImage = async () => {
    if (images.length >= 3) {
      Alert.alert('Limit Reached', 'You can upload maximum 3 screenshots');
      return;
    }

    const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (status !== 'granted') {
      Alert.alert('Permission Required', 'Please grant photo library access');
      return;
    }

    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      quality: 0.7,
      base64: true
    });

    if (!result.canceled && result.assets[0].base64) {
      setImages([...images, `data:image/jpeg;base64,${result.assets[0].base64}`]);
    }
  };

  const removeImage = (index: number) => {
    setImages(images.filter((_, i) => i !== index));
  };

  const handleSubmit = async () => {
    if (message.trim().length < 10) {
      Alert.alert('Error', 'Please write at least 10 characters');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`${process.env.EXPO_PUBLIC_BACKEND_URL}/api/feedback`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          type: activeTab,
          message: message.trim(),
          email: email.trim() || undefined,
          images
        })
      });

      const data = await response.json();

      if (response.ok && data.success) {
        Alert.alert(
          'Thank You! ❤️',
          'Thanks for helping make Pookie4U better ❤️',
          [{ text: 'OK', onPress: resetAndClose }]
        );
      } else {
        throw new Error(data.detail || 'Failed to submit feedback');
      }
    } catch (error) {
      console.error('Feedback submission error:', error);
      Alert.alert('Error', 'Failed to submit feedback. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const resetAndClose = () => {
    setMessage('');
    setEmail('');
    setImages([]);
    setActiveTab('bug');
    onClose();
  };

  const getPlaceholder = () => {
    switch (activeTab) {
      case 'bug':
        return 'Describe the bug you encountered...\n\nSteps to reproduce:\n1. \n2. \n3. ';
      case 'feature':
        return 'Describe the feature you\'d like to see...\n\nWhy would this be useful?';
      case 'general':
        return 'Share your thoughts, suggestions, or feedback...';
    }
  };

  return (
    <Modal
      visible={visible}
      animationType="slide"
      transparent={true}
      onRequestClose={onClose}
    >
      <View style={styles.modalOverlay}>
        <View style={styles.modalContainer}>
          {/* Header */}
          <View style={styles.header}>
            <Text style={styles.headerTitle}>Feedback & Suggestions</Text>
            <TouchableOpacity onPress={onClose} style={styles.closeButton}>
              <Ionicons name="close" size={24} color="#333" />
            </TouchableOpacity>
          </View>

          {/* Tabs */}
          <View style={styles.tabsContainer}>
            {tabs.map((tab) => (
              <TouchableOpacity
                key={tab.id}
                style={[styles.tab, activeTab === tab.id && styles.activeTab]}
                onPress={() => setActiveTab(tab.id)}
              >
                <Ionicons
                  name={tab.icon as any}
                  size={20}
                  color={activeTab === tab.id ? '#FF1493' : '#999'}
                />
                <Text style={[styles.tabText, activeTab === tab.id && styles.activeTabText]}>
                  {tab.label}
                </Text>
              </TouchableOpacity>
            ))}
          </View>

          <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
            {/* Message Input */}
            <Text style={styles.label}>Message *</Text>
            <TextInput
              style={styles.textArea}
              placeholder={getPlaceholder()}
              placeholderTextColor="#999"
              value={message}
              onChangeText={setMessage}
              multiline
              numberOfLines={8}
              maxLength={1000}
            />
            <Text style={styles.charCount}>{message.length}/1000</Text>

            {/* Email Input */}
            <Text style={styles.label}>Contact Email (Optional)</Text>
            <TextInput
              style={styles.input}
              placeholder="your.email@example.com"
              placeholderTextColor="#999"
              value={email}
              onChangeText={setEmail}
              keyboardType="email-address"
              autoCapitalize="none"
            />

            {/* Image Upload */}
            <Text style={styles.label}>Screenshots (Max 3)</Text>
            <View style={styles.imagesContainer}>
              {images.map((uri, index) => (
                <View key={index} style={styles.imageWrapper}>
                  <Image source={{ uri }} style={styles.image} />
                  <TouchableOpacity
                    style={styles.removeImageButton}
                    onPress={() => removeImage(index)}
                  >
                    <Ionicons name="close-circle" size={24} color="#FF1493" />
                  </TouchableOpacity>
                </View>
              ))}
              {images.length < 3 && (
                <TouchableOpacity style={styles.addImageButton} onPress={pickImage}>
                  <Ionicons name="add" size={32} color="#999" />
                  <Text style={styles.addImageText}>Add Image</Text>
                </TouchableOpacity>
              )}
            </View>
          </ScrollView>

          {/* Submit Button */}
          <TouchableOpacity
            style={[styles.submitButton, loading && styles.submitButtonDisabled]}
            onPress={handleSubmit}
            disabled={loading}
          >
            {loading ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <>
                <Ionicons name="paper-plane" size={20} color="#fff" />
                <Text style={styles.submitButtonText}>Submit Feedback</Text>
              </>
            )}
          </TouchableOpacity>
        </View>
      </View>
    </Modal>
  );
};

const styles = StyleSheet.create({
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'flex-end'
  },
  modalContainer: {
    backgroundColor: '#fff',
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    maxHeight: '90%',
    paddingBottom: Platform.OS === 'ios' ? 34 : 16
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0'
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333'
  },
  closeButton: {
    padding: 8
  },
  tabsContainer: {
    flexDirection: 'row',
    paddingHorizontal: 16,
    paddingVertical: 12,
    gap: 8
  },
  tab: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 12,
    borderRadius: 12,
    backgroundColor: '#f8f8f8',
    gap: 6
  },
  activeTab: {
    backgroundColor: '#FFE4F1'
  },
  tabText: {
    fontSize: 12,
    color: '#999',
    fontWeight: '600'
  },
  activeTabText: {
    color: '#FF1493'
  },
  content: {
    padding: 16
  },
  label: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 8,
    marginTop: 8
  },
  input: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 12,
    padding: 12,
    fontSize: 16,
    color: '#333',
    backgroundColor: '#f8f8f8'
  },
  textArea: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 12,
    padding: 12,
    fontSize: 16,
    color: '#333',
    backgroundColor: '#f8f8f8',
    minHeight: 150,
    textAlignVertical: 'top'
  },
  charCount: {
    fontSize: 12,
    color: '#999',
    textAlign: 'right',
    marginTop: 4
  },
  imagesContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12,
    marginTop: 8
  },
  imageWrapper: {
    position: 'relative',
    width: 100,
    height: 100
  },
  image: {
    width: 100,
    height: 100,
    borderRadius: 12,
    backgroundColor: '#f0f0f0'
  },
  removeImageButton: {
    position: 'absolute',
    top: -8,
    right: -8,
    backgroundColor: '#fff',
    borderRadius: 12
  },
  addImageButton: {
    width: 100,
    height: 100,
    borderRadius: 12,
    borderWidth: 2,
    borderColor: '#ddd',
    borderStyle: 'dashed',
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f8f8f8'
  },
  addImageText: {
    fontSize: 12,
    color: '#999',
    marginTop: 4
  },
  submitButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#FF1493',
    margin: 16,
    padding: 16,
    borderRadius: 12,
    gap: 8
  },
  submitButtonDisabled: {
    opacity: 0.6
  },
  submitButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold'
  }
});
