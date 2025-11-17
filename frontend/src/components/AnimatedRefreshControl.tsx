import React, { useEffect } from 'react';
import { RefreshControl, RefreshControlProps } from 'react-native';
import Animated, { 
  useSharedValue, 
  useAnimatedStyle, 
  withRepeat,
  withTiming,
  Easing,
  interpolate,
} from 'react-native-reanimated';
import { useTheme } from '../contexts/ThemeContext';

interface AnimatedRefreshControlProps extends Omit<RefreshControlProps, 'colors' | 'tintColor'> {
  refreshing: boolean;
  onRefresh: () => void;
}

/**
 * Enhanced RefreshControl with better theming
 * Uses platform-specific colors and animations
 */
export const AnimatedRefreshControl: React.FC<AnimatedRefreshControlProps> = ({
  refreshing,
  onRefresh,
  ...props
}) => {
  const { theme } = useTheme();

  return (
    <RefreshControl
      refreshing={refreshing}
      onRefresh={onRefresh}
      tintColor={theme.primary}
      colors={[theme.primary, theme.secondary]}
      progressBackgroundColor={theme.surface}
      {...props}
    />
  );
};

/**
 * Custom Animated Refresh Indicator
 * Can be used for custom pull-to-refresh implementations
 */
export const CustomRefreshIndicator: React.FC<{ refreshing: boolean }> = ({ refreshing }) => {
  const { theme } = useTheme();
  const rotation = useSharedValue(0);
  const scale = useSharedValue(0.8);

  useEffect(() => {
    if (refreshing) {
      rotation.value = withRepeat(
        withTiming(360, {
          duration: 1000,
          easing: Easing.linear,
        }),
        -1, // Infinite
        false
      );
      scale.value = withTiming(1, { duration: 200 });
    } else {
      rotation.value = 0;
      scale.value = withTiming(0.8, { duration: 200 });
    }
  }, [refreshing]);

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [
      { rotate: `${rotation.value}deg` },
      { scale: scale.value }
    ],
  }));

  return (
    <Animated.View style={[{ width: 40, height: 40 }, animatedStyle]}>
      {/* Add your custom refresh indicator here */}
    </Animated.View>
  );
};
