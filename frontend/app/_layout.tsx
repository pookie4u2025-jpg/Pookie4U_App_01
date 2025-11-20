import React, { useEffect } from 'react';
import { StatusBar } from 'expo-status-bar';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { Stack } from 'expo-router';
import { GestureHandlerRootView } from 'react-native-gesture-handler';
import { ThemeProvider } from '../src/contexts/ThemeContext';
import { initializeRevenueCat } from '../src/config/revenuecatConfig';
import { OfflineIndicator } from '../src/components/OfflineIndicator';
import { OfflineManager } from '../src/utils/OfflineManager';
import { ToastProvider } from '../src/utils/ToastManager';
import { initializeWebPolyfills } from '../src/utils/webPolyfills';

// Import stores to initialize them
import '../src/stores/useAuthStore';
import '../src/stores/useAppStore';
import '../src/stores/useGameStore';

// Initialize web polyfills BEFORE anything else
initializeWebPolyfills();

export default function RootLayout() {
  useEffect(() => {
    // Initialize RevenueCat when app starts
    initializeRevenueCat();
    
    // Initialize OfflineManager
    OfflineManager.initialize();
    
    return () => {
      // Cleanup on unmount
      OfflineManager.cleanup();
    };
  }, []);

  return (
    <GestureHandlerRootView style={{ flex: 1 }}>
      <ThemeProvider>
        <SafeAreaProvider>
          <ToastProvider>
            <StatusBar style="dark" translucent={false} backgroundColor="transparent" />
            <OfflineIndicator />
            <Stack screenOptions={{ headerShown: false }}>
              <Stack.Screen name="index" />
              <Stack.Screen name="tabs" options={{ headerShown: false }} />
              <Stack.Screen name="comprehensive-settings" />
            </Stack>
          </ToastProvider>
        </SafeAreaProvider>
      </ThemeProvider>
    </GestureHandlerRootView>
  );
}