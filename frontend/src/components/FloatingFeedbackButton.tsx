import React, { useState } from 'react';
import { TouchableOpacity, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { FeedbackModal } from './FeedbackModal';

export const FloatingFeedbackButton: React.FC = () => {
  const [modalVisible, setModalVisible] = useState(false);

  return (
    <>
      <TouchableOpacity
        style={styles.floatingButton}
        onPress={() => setModalVisible(true)}
        activeOpacity={0.8}
      >
        <Ionicons name="chatbox-ellipses" size={28} color="#fff" />
      </TouchableOpacity>

      <FeedbackModal
        visible={modalVisible}
        onClose={() => setModalVisible(false)}
      />
    </>
  );
};

const styles = StyleSheet.create({
  floatingButton: {
    position: 'absolute',
    bottom: 80,
    right: 20,
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: '#FF1493',
    justifyContent: 'center',
    alignItems: 'center',
    elevation: 8,
    shadowColor: '#FF1493',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    zIndex: 999
  }
});
