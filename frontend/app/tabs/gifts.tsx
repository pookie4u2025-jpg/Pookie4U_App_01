import React from 'react';
import { View, StyleSheet } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import GiftsContent from '../../src/screens/GiftsContent';
import GradientBackground from '../../src/components/GradientBackground';

export default function GiftsScreen() {
  return (
    <GradientBackground>
      <SafeAreaView style={styles.container} edges={['top', 'left', 'right']}>
        <View style={styles.spacer} />
        <GiftsContent />
      </SafeAreaView>
    </GradientBackground>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  spacer: {
    height: 8,
  },
});