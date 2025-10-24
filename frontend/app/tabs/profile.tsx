import React from 'react';
import { StyleSheet } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import ProfileContent from '../../src/screens/ProfileContent';
import GradientBackground from '../../src/components/GradientBackground';

export default function ProfileScreen() {
  return (
    <GradientBackground>
      <SafeAreaView style={styles.container} edges={['left', 'right']}>
        <ProfileContent />
      </SafeAreaView>
    </GradientBackground>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
});