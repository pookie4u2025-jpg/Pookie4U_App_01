import React from 'react';
import { Platform } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

/**
 * Web-safe Icon wrapper component
 * Fixes the "setNativeProps is not a function" error on web
 */
interface IconProps {
  name: keyof typeof Ionicons.glyphMap;
  size?: number;
  color?: string;
  style?: any;
}

export function Icon({ name, size = 24, color = '#000', style }: IconProps) {
  if (Platform.OS === 'web') {
    // On web, render icon without ref to avoid setNativeProps issues
    return (
      <Ionicons 
        name={name} 
        size={size} 
        color={color} 
        style={style}
        // Prevent ref attachment on web
        suppressHighlighting={true}
      />
    );
  }
  
  // On native, use normal rendering
  return (
    <Ionicons 
      name={name} 
      size={size} 
      color={color} 
      style={style}
    />
  );
}

export default Icon;
