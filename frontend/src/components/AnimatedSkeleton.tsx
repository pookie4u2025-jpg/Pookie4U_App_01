import React, { useEffect } from 'react';
import { View, StyleSheet, ViewStyle } from 'react-native';
import Animated, { 
  useSharedValue, 
  useAnimatedStyle, 
  withRepeat,
  withSequence,
  withTiming,
  Easing,
  interpolate,
} from 'react-native-reanimated';
import { LinearGradient } from 'expo-linear-gradient';
import { useTheme } from '../contexts/ThemeContext';

interface AnimatedSkeletonProps {
  width?: number | string;
  height?: number;
  borderRadius?: number;
  style?: ViewStyle;
}

export const AnimatedSkeleton: React.FC<AnimatedSkeletonProps> = ({
  width = '100%',
  height = 20,
  borderRadius = 8,
  style,
}) => {
  const { theme, isDark } = useTheme();
  const shimmerTranslate = useSharedValue(-1);

  useEffect(() => {
    shimmerTranslate.value = withRepeat(
      withSequence(
        withTiming(1, {
          duration: 1500,
          easing: Easing.inOut(Easing.ease),
        })
      ),
      -1, // Infinite
      false
    );
  }, []);

  const animatedStyle = useAnimatedStyle(() => {
    const translateX = interpolate(
      shimmerTranslate.value,
      [-1, 1],
      [-300, 300]
    );

    return {
      transform: [{ translateX }],
    };
  });

  const baseColor = isDark ? 'rgba(255, 255, 255, 0.05)' : 'rgba(0, 0, 0, 0.05)';
  const highlightColor = isDark ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.08)';

  return (
    <View 
      style={[
        styles.skeleton,
        {
          width,
          height,
          borderRadius,
          backgroundColor: baseColor,
        },
        style,
      ]}
    >
      <Animated.View style={[StyleSheet.absoluteFill, animatedStyle]}>
        <LinearGradient
          colors={[baseColor, highlightColor, baseColor]}
          start={{ x: 0, y: 0 }}
          end={{ x: 1, y: 0 }}
          style={StyleSheet.absoluteFill}
        />
      </Animated.View>
    </View>
  );
};

/**
 * Skeleton Presets for common UI patterns
 */

export const SkeletonCard: React.FC = () => {
  return (
    <View style={styles.card}>
      <AnimatedSkeleton width="60%" height={24} style={{ marginBottom: 12 }} />
      <AnimatedSkeleton width="100%" height={16} style={{ marginBottom: 8 }} />
      <AnimatedSkeleton width="80%" height={16} style={{ marginBottom: 16 }} />
      <AnimatedSkeleton width={100} height={36} borderRadius={18} />
    </View>
  );
};

export const SkeletonList: React.FC<{ count?: number }> = ({ count = 3 }) => {
  return (
    <View>
      {Array.from({ length: count }).map((_, index) => (
        <View key={index} style={styles.listItem}>
          <AnimatedSkeleton width={50} height={50} borderRadius={25} />
          <View style={{ flex: 1, marginLeft: 16 }}>
            <AnimatedSkeleton width="70%" height={18} style={{ marginBottom: 8 }} />
            <AnimatedSkeleton width="50%" height={14} />
          </View>
        </View>
      ))}
    </View>
  );
};

const styles = StyleSheet.create({
  skeleton: {
    overflow: 'hidden',
  },
  card: {
    padding: 20,
    borderRadius: 16,
    marginBottom: 16,
  },
  listItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 12,
    paddingHorizontal: 16,
  },
});
