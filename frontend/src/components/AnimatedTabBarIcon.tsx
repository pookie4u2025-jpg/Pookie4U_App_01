import React, { useEffect } from 'react';
import { Ionicons } from '@expo/vector-icons';
import Animated, { 
  useSharedValue, 
  useAnimatedStyle, 
  withSpring,
  withSequence,
  withTiming,
} from 'react-native-reanimated';
import * as Haptics from 'expo-haptics';

interface AnimatedTabBarIconProps {
  name: any;
  color: string;
  size: number;
  focused: boolean;
}

const AnimatedIcon = Animated.createAnimatedComponent(Ionicons);

export const AnimatedTabBarIcon: React.FC<AnimatedTabBarIconProps> = ({ 
  name, 
  color, 
  size, 
  focused 
}) => {
  const scale = useSharedValue(1);
  const translateY = useSharedValue(0);

  useEffect(() => {
    if (focused) {
      // Haptic feedback on tab change
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
      
      // Bounce animation when tab becomes active
      scale.value = withSequence(
        withSpring(1.2, { damping: 8, stiffness: 200 }),
        withSpring(1, { damping: 12, stiffness: 150 })
      );
      
      // Slight upward movement
      translateY.value = withSequence(
        withTiming(-3, { duration: 150 }),
        withTiming(0, { duration: 150 })
      );
    } else {
      // Scale down when inactive
      scale.value = withSpring(0.9, { damping: 15, stiffness: 150 });
      translateY.value = withTiming(0, { duration: 200 });
    }
  }, [focused]);

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [
      { scale: scale.value },
      { translateY: translateY.value }
    ],
  }));

  return (
    <AnimatedIcon 
      name={name} 
      size={size} 
      color={color} 
      style={animatedStyle}
    />
  );
};
