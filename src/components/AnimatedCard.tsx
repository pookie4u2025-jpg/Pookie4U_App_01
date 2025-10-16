import React from 'react';
import { View, StyleSheet, ViewStyle } from 'react-native';
import Animated, { 
  useAnimatedStyle, 
  useSharedValue, 
  withSpring, 
  runOnJS
} from 'react-native-reanimated';
import { Gesture, GestureDetector } from 'react-native-gesture-handler';

interface AnimatedCardProps {
  children: React.ReactNode;
  style?: ViewStyle;
  onPress?: () => void;
  delay?: number;
}

export const AnimatedCard: React.FC<AnimatedCardProps> = ({ 
  children, 
  style, 
  onPress,
  delay = 0 
}) => {
  const scale = useSharedValue(0);
  const opacity = useSharedValue(0);
  const pressed = useSharedValue(1);

  React.useEffect(() => {
    setTimeout(() => {
      scale.value = withSpring(1, { damping: 15, stiffness: 150 });
      opacity.value = withSpring(1);
    }, delay);
  }, [delay]);

  const tap = onPress ? Gesture.Tap()
    .onBegin(() => {
      pressed.value = withSpring(0.95);
    })
    .onFinalize(() => {
      pressed.value = withSpring(1);
      if (onPress) {
        runOnJS(onPress)();
      }
    }) : undefined;

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [
      { scale: scale.value * pressed.value },
    ],
    opacity: opacity.value,
  }));

  const CardContent = (
    <Animated.View style={[styles.card, style, animatedStyle]}>
      {children}
    </Animated.View>
  );

  if (tap) {
    return (
      <GestureDetector gesture={tap}>
        {CardContent}
      </GestureDetector>
    );
  }

  return CardContent;
};

const styles = StyleSheet.create({
  card: {
    backgroundColor: '#fff',
    borderRadius: 20,
    padding: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.12,
    shadowRadius: 24,
    elevation: 8,
  },
});