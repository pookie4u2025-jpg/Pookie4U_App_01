import React, { useEffect } from 'react';
import { Modal, ModalProps, StyleSheet, TouchableWithoutFeedback, View, Dimensions } from 'react-native';
import Animated, { 
  useSharedValue, 
  useAnimatedStyle, 
  withSpring,
  withTiming,
  runOnJS,
  Easing
} from 'react-native-reanimated';
import { BlurView } from 'expo-blur';

const { height } = Dimensions.get('window');

interface AnimatedModalProps extends Omit<ModalProps, 'animationType'> {
  visible: boolean;
  onClose: () => void;
  children: React.ReactNode;
  animationType?: 'slide' | 'fade' | 'scale';
  backdropBlur?: boolean;
}

export const AnimatedModal: React.FC<AnimatedModalProps> = ({
  visible,
  onClose,
  children,
  animationType = 'slide',
  backdropBlur = true,
  ...modalProps
}) => {
  const backdropOpacity = useSharedValue(0);
  const translateY = useSharedValue(height);
  const scale = useSharedValue(0.9);
  const opacity = useSharedValue(0);

  useEffect(() => {
    if (visible) {
      // Show animations
      backdropOpacity.value = withTiming(1, {
        duration: 200,
        easing: Easing.out(Easing.ease),
      });

      if (animationType === 'slide') {
        translateY.value = withSpring(0, {
          damping: 25,
          stiffness: 250,
        });
        opacity.value = withTiming(1, { duration: 200 });
      } else if (animationType === 'scale') {
        scale.value = withSpring(1, {
          damping: 15,
          stiffness: 150,
        });
        opacity.value = withTiming(1, { duration: 200 });
      } else {
        opacity.value = withTiming(1, { duration: 300 });
      }
    } else {
      // Hide animations
      backdropOpacity.value = withTiming(0, {
        duration: 150,
        easing: Easing.in(Easing.ease),
      });

      if (animationType === 'slide') {
        translateY.value = withTiming(height, {
          duration: 250,
          easing: Easing.in(Easing.ease),
        });
        opacity.value = withTiming(0, { duration: 150 });
      } else if (animationType === 'scale') {
        scale.value = withTiming(0.9, { duration: 150 });
        opacity.value = withTiming(0, { duration: 150 });
      } else {
        opacity.value = withTiming(0, { duration: 200 });
      }
    }
  }, [visible, animationType]);

  const backdropStyle = useAnimatedStyle(() => ({
    opacity: backdropOpacity.value,
  }));

  const contentStyle = useAnimatedStyle(() => {
    if (animationType === 'slide') {
      return {
        transform: [{ translateY: translateY.value }],
        opacity: opacity.value,
      };
    } else if (animationType === 'scale') {
      return {
        transform: [{ scale: scale.value }],
        opacity: opacity.value,
      };
    }
    return {
      opacity: opacity.value,
    };
  });

  return (
    <Modal
      visible={visible}
      transparent
      statusBarTranslucent
      animationType="none"
      {...modalProps}
    >
      <View style={styles.container}>
        {/* Animated Backdrop */}
        <TouchableWithoutFeedback onPress={onClose}>
          <Animated.View style={[styles.backdrop, backdropStyle]}>
            {backdropBlur ? (
              <BlurView intensity={20} style={StyleSheet.absoluteFill} />
            ) : (
              <View style={styles.solidBackdrop} />
            )}
          </Animated.View>
        </TouchableWithoutFeedback>

        {/* Animated Content */}
        <Animated.View style={[styles.content, contentStyle]}>
          {children}
        </Animated.View>
      </View>
    </Modal>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  backdrop: {
    ...StyleSheet.absoluteFillObject,
  },
  solidBackdrop: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
  },
  content: {
    width: '90%',
    maxWidth: 400,
  },
});
