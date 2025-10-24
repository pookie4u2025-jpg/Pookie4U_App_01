import React from 'react';
import { StyleSheet } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import MessagesContent from '../../src/screens/MessagesContent';
import GradientBackground from '../../src/components/GradientBackground';

export default function MessagesScreen() {
  return (
    <GradientBackground>
      <SafeAreaView style={styles.container} edges={['left', 'right']}>
        <MessagesContent />
      </SafeAreaView>
    </GradientBackground>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
});