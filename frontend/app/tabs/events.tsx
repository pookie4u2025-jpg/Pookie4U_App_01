import React from 'react';
import { StyleSheet } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import EnhancedEventsContent from '../../src/screens/EnhancedEventsContent';
import GradientBackground from '../../src/components/GradientBackground';

export default function EventsScreen() {
  return (
    <GradientBackground>
      <SafeAreaView style={styles.container} edges={['left', 'right']}>
        <EnhancedEventsContent />
      </SafeAreaView>
    </GradientBackground>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
});