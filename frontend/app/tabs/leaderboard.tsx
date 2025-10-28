import React from 'react';
import { SafeAreaView, View } from 'react-native';
import LeaderboardContent from '../../src/screens/LeaderboardContent';

export default function LeaderboardScreen() {
  return (
    <SafeAreaView style={{ flex: 1 }} edges={['left', 'right']}>
      {/* Invisible spacer to maintain consistent spacing */}
      <View style={{ height: 8 }} />
      <LeaderboardContent />
    </SafeAreaView>
  );
}
