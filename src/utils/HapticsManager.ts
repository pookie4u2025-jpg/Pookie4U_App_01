import * as Haptics from 'expo-haptics';
import { Audio } from 'expo-av';
import { Platform } from 'react-native';

export enum HapticType {
  LIGHT = 'light',
  MEDIUM = 'medium',
  HEAVY = 'heavy',
  SUCCESS = 'success',
  WARNING = 'warning',
  ERROR = 'error',
}

export enum SoundType {
  TASK_COMPLETE = 'task_complete',
  LEVEL_UP = 'level_up',
  ACHIEVEMENT = 'achievement',
  NOTIFICATION = 'notification',
  ERROR = 'error',
}

class HapticsManager {
  private soundEnabled: boolean = true;
  private hapticsEnabled: boolean = true;
  private sounds: { [key in SoundType]?: Audio.Sound } = {};

  constructor() {
    this.loadSounds();
  }

  private async loadSounds() {
    try {
      // Load sound files (using system sounds or custom ones)
      // For now, we'll use haptics as the primary feedback
      await Audio.setAudioModeAsync({
        allowsRecordingIOS: false,
        staysActiveInBackground: false,
        playsInSilentModeIOS: false,
        shouldDuckAndroid: true,
        playThroughEarpieceAndroid: false,
      });
    } catch (error) {
      console.warn('Failed to load sounds:', error);
    }
  }

  setSoundEnabled(enabled: boolean) {
    this.soundEnabled = enabled;
  }

  setHapticsEnabled(enabled: boolean) {
    this.hapticsEnabled = enabled;
  }

  async playHaptic(type: HapticType) {
    if (!this.hapticsEnabled) return;

    try {
      switch (type) {
        case HapticType.LIGHT:
          await Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
          break;
        case HapticType.MEDIUM:
          await Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
          break;
        case HapticType.HEAVY:
          await Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Heavy);
          break;
        case HapticType.SUCCESS:
          await Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
          break;
        case HapticType.WARNING:
          await Haptics.notificationAsync(Haptics.NotificationFeedbackType.Warning);
          break;
        case HapticType.ERROR:
          await Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);
          break;
      }
    } catch (error) {
      console.warn('Haptics not available:', error);
    }
  }

  async playSound(type: SoundType) {
    if (!this.soundEnabled) return;

    // Check if device is in silent mode
    try {
      const audioMode = await Audio.getStatusAsync();
      // For now, we'll skip sound implementation and focus on haptics
      // In a real app, you'd load and play sound files here
    } catch (error) {
      console.warn('Sound playback failed:', error);
    }
  }

  async playFeedback(type: HapticType, soundType?: SoundType) {
    // Play haptics first (immediate response)
    await this.playHaptic(type);
    
    // Then play sound if provided and enabled
    if (soundType) {
      await this.playSound(soundType);
    }
  }

  // Convenience methods for common interactions
  async buttonPress() {
    await this.playHaptic(HapticType.LIGHT);
  }

  async taskComplete() {
    await this.playFeedback(HapticType.SUCCESS, SoundType.TASK_COMPLETE);
  }

  async levelUp() {
    await this.playFeedback(HapticType.HEAVY, SoundType.LEVEL_UP);
  }

  async achievement() {
    await this.playFeedback(HapticType.SUCCESS, SoundType.ACHIEVEMENT);
  }

  async error() {
    await this.playFeedback(HapticType.ERROR, SoundType.ERROR);
  }

  async warning() {
    await this.playFeedback(HapticType.WARNING);
  }
}

// Singleton instance
export const hapticsManager = new HapticsManager();

// Utility functions for easy use
export const playHaptic = (type: HapticType) => hapticsManager.playHaptic(type);
export const playFeedback = (haptic: HapticType, sound?: SoundType) => 
  hapticsManager.playFeedback(haptic, sound);

// Common feedback functions
export const buttonPress = () => hapticsManager.buttonPress();
export const taskComplete = () => hapticsManager.taskComplete();
export const levelUp = () => hapticsManager.levelUp();
export const achievement = () => hapticsManager.achievement();
export const errorFeedback = () => hapticsManager.error();
export const warningFeedback = () => hapticsManager.warning();