import React, { useEffect } from 'react';
import { View, Text, ActivityIndicator } from 'react-native';
import { Redirect } from 'expo-router';
import { useAuthStore } from '../src/stores/useAuthStore';
import { useAppStore } from '../src/stores/useAppStore';
import AuthScreen from '../src/screens/AuthScreen';
import OnboardingScreen from '../src/screens/OnboardingScreen';

export default function Index() {
  const { isAuthenticated, initialized, validateSession } = useAuthStore();
  const { onboardingCompleted } = useAppStore();

  useEffect(() => {
    if (!initialized) {
      validateSession();
    }
  }, [initialized, validateSession]);

  // Show loading screen while validating session
  if (!initialized) {
    return (
      <View style={{ 
        flex: 1, 
        justifyContent: 'center', 
        alignItems: 'center', 
        backgroundColor: '#F7D7DA' 
      }}>
        <ActivityIndicator size="large" color="#FF1493" />
        <Text style={{ 
          marginTop: 16, 
          fontSize: 16, 
          color: '#666666',
          textAlign: 'center'
        }}>
          Loading Pookie4u...
        </Text>
      </View>
    );
  }

  if (!isAuthenticated) {
    return <AuthScreen />;
  }

  if (!onboardingCompleted) {
    return <OnboardingScreen />;
  }

  // Use Redirect component instead of router.replace
  return <Redirect href="/tabs" />;
}