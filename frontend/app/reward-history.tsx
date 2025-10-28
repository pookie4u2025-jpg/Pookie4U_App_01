import React from 'react';
import { SafeAreaView, View } from 'react-native';
import RewardHistoryContent from '../src/screens/RewardHistoryContent';

export default function RewardHistoryScreen() {
  return (
    <SafeAreaView style={{ flex: 1 }} edges={['top', 'left', 'right', 'bottom']}>
      <RewardHistoryContent />
    </SafeAreaView>
  );
}
