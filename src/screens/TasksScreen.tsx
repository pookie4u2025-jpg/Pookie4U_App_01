import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  RefreshControl,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useAuthStore } from '../stores/useAuthStore';
import { useTaskStore } from '../stores/useTaskStore';
import { useGameStore } from '../stores/useGameStore';

export default function TasksScreen() {
  const { token } = useAuthStore();
  const { dailyTasks, weeklyTask, fetchDailyTasks, fetchWeeklyTask, completeTask } = useTaskStore();
  const { addPoints, incrementStreak, incrementTasksCompleted } = useGameStore();

  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    if (token) {
      loadTasks();
    }
  }, [token]);

  const loadTasks = async () => {
    if (!token) return;
    await fetchDailyTasks(token);
    await fetchWeeklyTask(token);
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadTasks();
    setRefreshing(false);
  };

  const handleCompleteTask = async (taskId: string, points: number) => {
    if (!token) return;
    
    const success = await completeTask(taskId, token);
    if (success) {
      addPoints(points);
      incrementTasksCompleted();
      incrementStreak();
      
      Alert.alert(
        'Task Completed! 🎉',
        `You earned ${points} points! Great job on strengthening your relationship!`,
        [{ text: 'Amazing!', style: 'default' }]
      );
    }
  };

  const completedDailyTasks = dailyTasks.filter(task => task.completed).length;
  const dailyProgress = dailyTasks.length > 0 ? (completedDailyTasks / dailyTasks.length) * 100 : 0;

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView
        style={styles.scrollView}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
      >
        {/* Daily Tasks Progress */}
        <View style={styles.progressCard}>
          <Text style={styles.progressTitle}>Today's Progress</Text>
          <View style={styles.progressBar}>
            <View style={[styles.progressFill, { width: `${dailyProgress}%` }]} />
          </View>
          <Text style={styles.progressText}>
            {completedDailyTasks} of {dailyTasks.length} daily tasks completed
          </Text>
        </View>

        {/* Daily Tasks */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Today's Daily Tasks ✅</Text>
          <Text style={styles.sectionSubtitle}>
            Complete these 3 daily tasks to earn points and maintain your streak
          </Text>
          
          {dailyTasks.map((task, index) => (
            <View key={task.id} style={styles.taskCard}>
              <View style={styles.taskHeader}>
                <View style={styles.taskNumber}>
                  <Text style={styles.taskNumberText}>{index + 1}</Text>
                </View>
                <View style={styles.taskContent}>
                  <Text style={styles.taskTitle}>{task.title}</Text>
                  <Text style={styles.taskCategory}>{task.category}</Text>
                  <View style={styles.taskPoints}>
                    <Ionicons name="star" size={14} color="#FFD700" />
                    <Text style={styles.pointsText}>{task.points} points</Text>
                  </View>
                </View>
                {task.completed ? (
                  <View style={styles.completedButton}>
                    <Ionicons name="checkmark-circle" size={24} color="#4CAF50" />
                    <Text style={styles.completedText}>Done</Text>
                  </View>
                ) : (
                  <TouchableOpacity
                    style={styles.completeButton}
                    onPress={() => handleCompleteTask(task.id, task.points)}
                  >
                    <Text style={styles.completeButtonText}>Complete</Text>
                  </TouchableOpacity>
                )}
              </View>
            </View>
          ))}
        </View>

        {/* Weekly Challenge */}
        {weeklyTask && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>This Week's Challenge 🔥</Text>
            <Text style={styles.sectionSubtitle}>
              Complete this special challenge for extra points!
            </Text>
            
            <View style={styles.weeklyCard}>
              <View style={styles.weeklyHeader}>
                <View style={styles.weeklyBadge}>
                  <Text style={styles.weeklyBadgeText}>WEEKLY</Text>
                </View>
                <View style={styles.weeklyPoints}>
                  <Ionicons name="star" size={16} color="#FFD700" />
                  <Text style={styles.weeklyPointsText}>25 points</Text>
                </View>
              </View>
              
              <Text style={styles.weeklyTitle}>{weeklyTask.title}</Text>
              <Text style={styles.weeklyCategory}>{weeklyTask.category}</Text>
              
              {weeklyTask.completed ? (
                <View style={styles.weeklyCompleted}>
                  <Ionicons name="checkmark-circle" size={32} color="#4CAF50" />
                  <Text style={styles.weeklyCompletedText}>Challenge Completed!</Text>
                </View>
              ) : (
                <TouchableOpacity
                  style={styles.weeklyCompleteButton}
                  onPress={() => handleCompleteTask(weeklyTask.id, weeklyTask.points)}
                >
                  <Text style={styles.weeklyCompleteButtonText}>Complete Challenge</Text>
                </TouchableOpacity>
              )}
            </View>
          </View>
        )}

        {/* Task Tips */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Task Tips 💡</Text>
          <View style={styles.tipsCard}>
            <Text style={styles.tip}>• Take photos while completing tasks to create memories</Text>
            <Text style={styles.tip}>• Don't rush - quality time matters more than speed</Text>
            <Text style={styles.tip}>• Personalize tasks based on your partner's preferences</Text>
            <Text style={styles.tip}>• Complete at least one task daily to maintain your streak</Text>
          </View>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8f9fa',
  },
  scrollView: {
    flex: 1,
  },
  progressCard: {
    margin: 20,
    backgroundColor: '#fff',
    borderRadius: 15,
    padding: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  progressTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 15,
  },
  progressBar: {
    height: 10,
    backgroundColor: '#e0e0e0',
    borderRadius: 5,
    marginBottom: 10,
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#FF69B4',
    borderRadius: 5,
  },
  progressText: {
    fontSize: 14,
    color: '#666',
    textAlign: 'center',
  },
  section: {
    marginHorizontal: 20,
    marginBottom: 20,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 5,
  },
  sectionSubtitle: {
    fontSize: 14,
    color: '#666',
    marginBottom: 15,
  },
  taskCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 15,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  taskHeader: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  taskNumber: {
    width: 30,
    height: 30,
    borderRadius: 15,
    backgroundColor: '#FF69B4',
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 15,
  },
  taskNumberText: {
    color: '#fff',
    fontWeight: 'bold',
    fontSize: 14,
  },
  taskContent: {
    flex: 1,
  },
  taskTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 4,
  },
  taskCategory: {
    fontSize: 12,
    color: '#666',
    marginBottom: 4,
  },
  taskPoints: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  pointsText: {
    fontSize: 12,
    color: '#FFD700',
    fontWeight: '600',
    marginLeft: 4,
  },
  completeButton: {
    backgroundColor: '#FF69B4',
    borderRadius: 20,
    paddingHorizontal: 15,
    paddingVertical: 8,
  },
  completeButtonText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: '600',
  },
  completedButton: {
    alignItems: 'center',
  },
  completedText: {
    fontSize: 10,
    color: '#4CAF50',
    fontWeight: '600',
    marginTop: 2,
  },
  weeklyCard: {
    backgroundColor: '#fff',
    borderRadius: 15,
    padding: 20,
    borderLeftWidth: 4,
    borderLeftColor: '#FF69B4',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  weeklyHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 15,
  },
  weeklyBadge: {
    backgroundColor: '#FF69B4',
    borderRadius: 12,
    paddingHorizontal: 8,
    paddingVertical: 4,
  },
  weeklyBadgeText: {
    color: '#fff',
    fontSize: 10,
    fontWeight: 'bold',
  },
  weeklyPoints: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  weeklyPointsText: {
    fontSize: 14,
    color: '#FFD700',
    fontWeight: 'bold',
    marginLeft: 4,
  },
  weeklyTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 5,
  },
  weeklyCategory: {
    fontSize: 14,
    color: '#666',
    marginBottom: 20,
  },
  weeklyCompleteButton: {
    backgroundColor: '#FF69B4',
    borderRadius: 25,
    paddingVertical: 12,
    alignItems: 'center',
  },
  weeklyCompleteButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  weeklyCompleted: {
    alignItems: 'center',
    paddingVertical: 10,
  },
  weeklyCompletedText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#4CAF50',
    marginTop: 8,
  },
  tipsCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  tip: {
    fontSize: 14,
    color: '#666',
    marginBottom: 8,
    lineHeight: 20,
  },
});