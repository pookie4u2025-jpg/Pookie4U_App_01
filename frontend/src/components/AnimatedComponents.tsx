import React from 'react';
import { ViewStyle } from 'react-native';
import Animated, { FadeIn, FadeInDown, FadeInUp, SlideInLeft, SlideInRight, ZoomIn } from 'react-native-reanimated';

interface AnimatedViewProps {
  children: React.ReactNode;
  style?: ViewStyle;
  delay?: number;
}

/**
 * FadeInView - Simple fade in animation
 */
export const FadeInView: React.FC<AnimatedViewProps> = ({ children, style, delay = 0 }) => {
  return (
    <Animated.View entering={FadeIn.delay(delay).duration(300)} style={style}>
      {children}
    </Animated.View>
  );
};

/**
 * SlideInView - Slide in from bottom with fade
 */
export const SlideInView: React.FC<AnimatedViewProps> = ({ children, style, delay = 0 }) => {
  return (
    <Animated.View entering={FadeInDown.delay(delay).duration(400).springify()} style={style}>
      {children}
    </Animated.View>
  );
};

/**
 * SlideUpView - Slide in from top with fade
 */
export const SlideUpView: React.FC<AnimatedViewProps> = ({ children, style, delay = 0 }) => {
  return (
    <Animated.View entering={FadeInUp.delay(delay).duration(400).springify()} style={style}>
      {children}
    </Animated.View>
  );
};

/**
 * SlideFromLeftView - Slide in from left
 */
export const SlideFromLeftView: React.FC<AnimatedViewProps> = ({ children, style, delay = 0 }) => {
  return (
    <Animated.View entering={SlideInLeft.delay(delay).duration(400).springify()} style={style}>
      {children}
    </Animated.View>
  );
};

/**
 * SlideFromRightView - Slide in from right
 */
export const SlideFromRightView: React.FC<AnimatedViewProps> = ({ children, style, delay = 0 }) => {
  return (
    <Animated.View entering={SlideInRight.delay(delay).duration(400).springify()} style={style}>
      {children}
    </Animated.View>
  );
};

/**
 * ScaleInView - Scale up with fade
 */
export const ScaleInView: React.FC<AnimatedViewProps> = ({ children, style, delay = 0 }) => {
  return (
    <Animated.View entering={ZoomIn.delay(delay).duration(300).springify()} style={style}>
      {children}
    </Animated.View>
  );
};

/**
 * StaggeredListItem - For list items with staggered animation
 */
interface StaggeredListItemProps extends AnimatedViewProps {
  index: number;
  staggerDelay?: number;
}

export const StaggeredListItem: React.FC<StaggeredListItemProps> = ({ 
  children, 
  style, 
  index, 
  staggerDelay = 50 
}) => {
  return (
    <Animated.View 
      entering={FadeInDown.delay(index * staggerDelay).duration(400).springify()} 
      style={style}
    >
      {children}
    </Animated.View>
  );
};
