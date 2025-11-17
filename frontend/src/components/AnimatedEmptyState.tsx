import React, { useEffect } from 'react';
import { View, Text, StyleSheet } from 'react-native';
import Animated, { 
  useSharedValue, 
  useAnimatedStyle, 
  withSpring,
  withRepeat,
  withSequence,
  withDelay,
} from 'react-native-reanimated';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../contexts/ThemeContext';

interface AnimatedEmptyStateProps {
  icon: any;
  title: string;
  message: string;
  action?: React.ReactNode;
}

const AnimatedIcon = Animated.createAnimatedComponent(Ionicons);

export const AnimatedEmptyState: React.FC<AnimatedEmptyStateProps> = ({
  icon,
  title,
  message,
  action,
}) => {
  const { theme } = useTheme();
  const iconScale = useSharedValue(0.8);
  const iconRotate = useSharedValue(0);
  const textOpacity = useSharedValue(0);
  const textTranslateY = useSharedValue(20);

  useEffect(() => {
    // Icon entrance with bounce
    iconScale.value = withSpring(1, {
      damping: 10,
      stiffness: 100,
    });

    // Subtle floating animation
    iconScale.value = withDelay(
      500,
      withRepeat(
        withSequence(
          withSpring(1.05, { damping: 20, stiffness: 90 }),
          withSpring(1, { damping: 20, stiffness: 90 })
        ),
        -1, // Infinite
        true // Reverse
      )
    );

    // Text fade in
    textOpacity.value = withDelay(200, withSpring(1));
    textTranslateY.value = withDelay(200, withSpring(0));
  }, []);

  const iconAnimatedStyle = useAnimatedStyle(() => ({
    transform: [
      { scale: iconScale.value },
      { rotate: `${iconRotate.value}deg` }
    ],
  }));

  const textAnimatedStyle = useAnimatedStyle(() => ({
    opacity: textOpacity.value,
    transform: [{ translateY: textTranslateY.value }],
  }));

  return (
    <View style={styles.container}>
      <AnimatedIcon
        name={icon}
        size={80}
        color={theme.textSecondary}
        style={iconAnimatedStyle}
      />
      
      <Animated.View style={[styles.textContainer, textAnimatedStyle]}>
        <Text style={[styles.title, { color: theme.text }]}>{title}</Text>
        <Text style={[styles.message, { color: theme.textSecondary }]}>
          {message}
        </Text>
      </Animated.View>

      {action && (
        <Animated.View style={[{ marginTop: 24 }, textAnimatedStyle]}>
          {action}
        </Animated.View>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 32,
    paddingVertical: 64,
  },
  textContainer: {
    marginTop: 24,
    alignItems: 'center',
  },
  title: {
    fontSize: 24,
    fontWeight: '700',
    textAlign: 'center',
    marginBottom: 12,
  },
  message: {
    fontSize: 16,
    textAlign: 'center',
    lineHeight: 24,
  },
});
