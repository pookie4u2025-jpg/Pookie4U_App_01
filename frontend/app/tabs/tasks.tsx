import React from 'react';
import { View, StyleSheet } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import TasksContent from '../../src/screens/TasksContent';
import GradientBackground from '../../src/components/GradientBackground';

export default function TasksScreen() {
  return (
    <GradientBackground>
      <SafeAreaView style={styles.container} edges={['top', 'left', 'right']}>
        <View style={styles.spacer} />
        <TasksContent />
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