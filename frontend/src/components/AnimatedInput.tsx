import React, { useState } from 'react';
import { TextInput, StyleSheet, TextInputProps, ViewStyle } from 'react-native';
import Animated, { 
  useAnimatedStyle, 
  useSharedValue, 
  withSpring,
  withTiming,
  Easing
} from 'react-native-reanimated';
import { useTheme } from '../context/ThemeContext';

interface AnimatedInputProps extends TextInputProps {
  containerStyle?: ViewStyle;
}

export const AnimatedInput: React.FC<AnimatedInputProps> = ({ 
  containerStyle, 
  style,
  ...props 
}) => {
  const { theme } = useTheme();
  const [isFocused, setIsFocused] = useState(false);
  const scale = useSharedValue(1);
  const borderWidth = useSharedValue(1);

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ scale: scale.value }],
    borderWidth: borderWidth.value,
    borderColor: isFocused ? theme.primary : theme.border,
  }));

  const handleFocus = (e: any) => {
    setIsFocused(true);
    scale.value = withSpring(1.01, {
      damping: 15,
      stiffness: 150,
    });
    borderWidth.value = withTiming(2, {
      duration: 200,
      easing: Easing.out(Easing.ease),
    });
    props.onFocus?.(e);
  };

  const handleBlur = (e: any) => {
    setIsFocused(false);
    scale.value = withSpring(1);
    borderWidth.value = withTiming(1, {
      duration: 200,
      easing: Easing.out(Easing.ease),
    });
    props.onBlur?.(e);
  };

  return (
    <Animated.View style={[styles.container, containerStyle, animatedStyle]}>
      <TextInput
        {...props}
        style={[
          styles.input,
          { 
            color: theme.text,
            backgroundColor: theme.surface,
          },
          style
        ]}
        placeholderTextColor={theme.textSecondary}
        onFocus={handleFocus}
        onBlur={handleBlur}
      />
    </Animated.View>
  );
};

const styles = StyleSheet.create({
  container: {
    borderRadius: 12,
    overflow: 'hidden',
  },
  input: {
    paddingVertical: 14,
    paddingHorizontal: 16,
    fontSize: 16,
    borderRadius: 12,
  },
});
