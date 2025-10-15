import { useEffect } from 'react';
import { 
  useSharedValue, 
  useAnimatedStyle, 
  withSpring, 
  withTiming,
  withSequence,
  withDelay,
  Easing,
  interpolate,
  runOnJS
} from 'react-native-reanimated';

// Subtle spring configuration
export const subtleSpring = {
  damping: 20,
  stiffness: 300,
  mass: 0.5,
};

// Smooth timing configuration
export const smoothTiming = {
  duration: 200,
  easing: Easing.out(Easing.cubic),
};

// Fade timing
export const fadeTiming = {
  duration: 300,
  easing: Easing.inOut(Easing.ease),
};

// Slide timing
export const slideTiming = {
  duration: 250,
  easing: Easing.out(Easing.ease),
};

// Button press animation hook
export const useButtonPressAnimation = () => {
  const scale = useSharedValue(1);

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ scale: scale.value }],
  }));

  const onPressIn = () => {
    scale.value = withSpring(0.96, subtleSpring);
  };

  const onPressOut = () => {
    scale.value = withSpring(1, subtleSpring);
  };

  return { animatedStyle, onPressIn, onPressOut };
};

// Fade in animation hook
export const useFadeInAnimation = (delay = 0) => {
  const opacity = useSharedValue(0);

  useEffect(() => {
    opacity.value = withDelay(
      delay,
      withTiming(1, fadeTiming)
    );
  }, []);

  const animatedStyle = useAnimatedStyle(() => ({
    opacity: opacity.value,
  }));

  return animatedStyle;
};

// Slide up animation hook
export const useSlideUpAnimation = (delay = 0) => {
  const translateY = useSharedValue(30);
  const opacity = useSharedValue(0);

  useEffect(() => {
    translateY.value = withDelay(
      delay,
      withTiming(0, slideTiming)
    );
    opacity.value = withDelay(
      delay,
      withTiming(1, fadeTiming)
    );
  }, []);

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ translateY: translateY.value }],
    opacity: opacity.value,
  }));

  return animatedStyle;
};

// Card animation hook (staggered)
export const useCardAnimation = (index: number) => {
  const scale = useSharedValue(0.9);
  const opacity = useSharedValue(0);

  useEffect(() => {
    const delay = index * 50; // 50ms stagger
    scale.value = withDelay(
      delay,
      withSpring(1, subtleSpring)
    );
    opacity.value = withDelay(
      delay,
      withTiming(1, fadeTiming)
    );
  }, [index]);

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ scale: scale.value }],
    opacity: opacity.value,
  }));

  return animatedStyle;
};

// Bounce animation (for success feedback)
export const useBounceAnimation = (trigger: boolean) => {
  const scale = useSharedValue(1);

  useEffect(() => {
    if (trigger) {
      scale.value = withSequence(
        withSpring(1.1, { damping: 8, stiffness: 200 }),
        withSpring(1, subtleSpring)
      );
    }
  }, [trigger]);

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ scale: scale.value }],
  }));

  return animatedStyle;
};

// Tab switch animation
export const useTabAnimation = (isActive: boolean) => {
  const scale = useSharedValue(isActive ? 1 : 0.9);
  const opacity = useSharedValue(isActive ? 1 : 0.6);

  useEffect(() => {
    scale.value = withSpring(isActive ? 1 : 0.9, subtleSpring);
    opacity.value = withTiming(isActive ? 1 : 0.6, smoothTiming);
  }, [isActive]);

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ scale: scale.value }],
    opacity: opacity.value,
  }));

  return animatedStyle;
};

// Modal slide animation
export const useModalAnimation = (visible: boolean) => {
  const translateY = useSharedValue(visible ? 0 : 1000);
  const opacity = useSharedValue(visible ? 1 : 0);

  useEffect(() => {
    if (visible) {
      translateY.value = withSpring(0, {
        damping: 25,
        stiffness: 250,
      });
      opacity.value = withTiming(1, fadeTiming);
    } else {
      translateY.value = withTiming(1000, slideTiming);
      opacity.value = withTiming(0, fadeTiming);
    }
  }, [visible]);

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ translateY: translateY.value }],
    opacity: opacity.value,
  }));

  return animatedStyle;
};

// Progress animation
export const useProgressAnimation = (progress: number) => {
  const animatedProgress = useSharedValue(0);

  useEffect(() => {
    animatedProgress.value = withSpring(progress, subtleSpring);
  }, [progress]);

  const animatedStyle = useAnimatedStyle(() => ({
    width: `${animatedProgress.value}%`,
  }));

  return animatedStyle;
};

// Shake animation (for errors)
export const useShakeAnimation = (trigger: boolean) => {
  const translateX = useSharedValue(0);

  useEffect(() => {
    if (trigger) {
      translateX.value = withSequence(
        withTiming(-10, { duration: 50 }),
        withTiming(10, { duration: 50 }),
        withTiming(-10, { duration: 50 }),
        withTiming(10, { duration: 50 }),
        withTiming(0, { duration: 50 })
      );
    }
  }, [trigger]);

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ translateX: translateX.value }],
  }));

  return animatedStyle;
};

// Rotate animation
export const useRotateAnimation = (rotating: boolean) => {
  const rotation = useSharedValue(0);

  useEffect(() => {
    if (rotating) {
      rotation.value = withSequence(
        withTiming(360, { duration: 1000, easing: Easing.linear })
      );
    } else {
      rotation.value = 0;
    }
  }, [rotating]);

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ rotate: `${rotation.value}deg` }],
  }));

  return animatedStyle;
};

// Pulse animation (subtle)
export const usePulseAnimation = (active: boolean) => {
  const scale = useSharedValue(1);

  useEffect(() => {
    if (active) {
      scale.value = withSequence(
        withSpring(1.02, subtleSpring),
        withSpring(1, subtleSpring)
      );
    }
  }, [active]);

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ scale: scale.value }],
  }));

  return animatedStyle;
};
