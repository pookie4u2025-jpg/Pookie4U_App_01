import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, Dimensions } from 'react-native';
import Animated, { 
  useSharedValue, 
  useAnimatedStyle, 
  withSpring,
  withTiming,
  Easing,
} from 'react-native-reanimated';
import { Ionicons } from '@expo/vector-icons';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { OfflineManager } from '../utils/OfflineManager';
import { useTheme } from '../contexts/ThemeContext';

const { width } = Dimensions.get('window');

export const OfflineIndicator: React.FC = () => {
  const { theme } = useTheme();
  const insets = useSafeAreaInsets();
  const [isOnline, setIsOnline] = useState(true);
  const [queueSize, setQueueSize] = useState(0);

  const translateY = useSharedValue(-100);
  const opacity = useSharedValue(0);

  useEffect(() => {
    // Subscribe to online/offline state
    const unsubscribe = OfflineManager.subscribe((online) => {
      setIsOnline(online);
      
      if (!online) {
        // Show indicator
        translateY.value = withSpring(0, {
          damping: 20,
          stiffness: 200,
        });
        opacity.value = withTiming(1, { duration: 300 });
      } else {
        // Hide indicator after showing "Back online" briefly
        setTimeout(() => {
          translateY.value = withTiming(-100, {
            duration: 400,
            easing: Easing.in(Easing.ease),
          });
          opacity.value = withTiming(0, { duration: 300 });
        }, 2000);
      }
    });

    // Update queue size periodically
    const interval = setInterval(() => {
      setQueueSize(OfflineManager.getQueueSize());
    }, 1000);

    return () => {
      unsubscribe();
      clearInterval(interval);
    };
  }, []);

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ translateY: translateY.value }],
    opacity: opacity.value,
  }));

  const backgroundColor = isOnline ? '#4CAF50' : '#FF6B35';
  const iconName = isOnline ? 'cloud-done' : 'cloud-offline';
  const message = isOnline 
    ? 'Back online! Syncing...' 
    : `You're offline${queueSize > 0 ? ` · ${queueSize} pending` : ''}`;

  return (
    <Animated.View 
      style={[
        styles.container, 
        { 
          backgroundColor, 
          top: insets.top,
        },
        animatedStyle
      ]}
    >
      <Ionicons name={iconName} size={16} color="#FFFFFF" />
      <Text style={styles.text}>{message}</Text>
    </Animated.View>
  );
};

const styles = StyleSheet.create({
  container: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 8,
    paddingHorizontal: 16,
    gap: 8,
    zIndex: 9999,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 4,
    elevation: 8,
  },
  text: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: '600',
  },
});
