import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  RefreshControl,
  Dimensions,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useAuthStore } from '../stores/useAuthStore';
import { useTaskStore } from '../stores/useTaskStore';
import { useGameStore } from '../stores/useGameStore';

const { width } = Dimensions.get('window');

export default function HomeScreen() {
  const { user, token } = useAuthStore();
  const { dailyTasks, weeklyTask, fetchDailyTasks, fetchWeeklyTask, completeTask } = useTaskStore();
  const { 
    totalPoints, 
    currentLevel, 
    currentStreak, 
    dailyTasksCompleted,
    addPoints,
    incrementStreak,
    incrementTasksCompleted,
    resetDailyProgress
  } = useGameStore();

  const [refreshing, setRefreshing] = useState(false);
  const [activeTab, setActiveTab] = useState('tips');

  useEffect(() => {
    if (token) {
      loadTasks();
      resetDailyProgress();
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
        'Great Job! 🎉',
        `You earned ${points} points! Keep up the amazing work!`,
        [{ text: 'Continue', style: 'default' }]
      );
    }
  };

  const completedDailyTasks = dailyTasks.filter(task => task.completed).length;
  const totalDailyTasks = dailyTasks.length;
  const dailyProgress = totalDailyTasks > 0 ? (completedDailyTasks / totalDailyTasks) * 100 : 0;

  const experienceForNext = 100 - (totalPoints % 100);
  const levelProgress = ((totalPoints % 100) / 100) * 100;

  const renderTabContent = () => {
    switch (activeTab) {
      case 'tips':
        return (
          <View style={styles.tabContent}>
            <Text style={styles.tabContentTitle}>💡 Daily Relationship Tips</Text>
            <Text style={styles.tabContentText}>
              • Start each day with a loving message{'\n'}• Listen actively when your partner speaks{'\n'}• Express gratitude for small gestures{'\n'}• Plan surprise moments together{'\n'}• Share your feelings openly and honestly
            </Text>
          </View>
        );
      case 'events':
        return (
          <View style={styles.tabContent}>
            <Text style={styles.tabContentTitle}>📅 Upcoming Events</Text>
            <Text style={styles.tabContentText}>
              • Valentine&apos;s Day Challenge - Feb 14{'\n'}• Monthly Date Night - Every 1st Friday{'\n'}• Anniversary Celebration - Coming Soon{'\n'}• Couples Workshop - Next Weekend{'\n'}• Love Letter Writing Session - Feb 20
            </Text>
          </View>
        );
      case 'winners':
        return (
          <View style={styles.tabContent}>
            <Text style={styles.tabContentTitle}>🏆 This Week&apos;s Winners</Text>
            <Text style={styles.tabContentText}>
              • Sarah & Mike - 2,450 points{'\n'}• Emma & James - 2,380 points{'\n'}• Lisa & David - 2,290 points{'\n'}• You could be next! Keep completing tasks{'\n'}• Weekly leaderboard resets every Sunday
            </Text>
          </View>
        );
      case 'rules':
        return (
          <View style={styles.tabContent}>
            <Text style={styles.tabContentTitle}>📖 How It Works</Text>
            <Text style={styles.tabContentText}>
              • Complete daily tasks to earn points{'\n'}• Weekly challenges give bonus points{'\n'}• Build streaks for multiplier bonuses{'\n'}• Level up to unlock new features{'\n'}• Share achievements with your partner
            </Text>
          </View>
        );
      case 'why':
        return (
          <View style={styles.tabContent}>
            <Text style={styles.tabContentTitle}>❤️ Why This Matters</Text>
            <Text style={styles.tabContentText}>
              • Strengthens emotional connection{'\n'}• Creates positive daily habits{'\n'}• Encourages thoughtful gestures{'\n'}• Builds lasting memories together{'\n'}• Makes love a daily practice, not just a feeling
            </Text>
          </View>
        );
      default:
        return null;
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView
        style={styles.scrollView}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
      >
        {/* Header Greeting */}
        <View style={styles.header}>
          <Text style={styles.greeting}>Good afternoon, {user?.name || 'Loverboy'}! 💕</Text>
          <Text style={styles.subtitle}>Let&apos;s make today special for your partner</Text>
        </View>

        {/* Stats Cards */}
        <View style={styles.statsContainer}>
          <View style={styles.statCard}>
            <View style={styles.statHeader}>
              <Ionicons name="star" size={20} color="#FFD700" />
              <Text style={styles.statValue}>{totalPoints}</Text>
            </View>
            <Text style={styles.statLabel}>POINTS</Text>
          </View>
          
          <View style={styles.statCard}>
            <View style={styles.statHeader}>
              <Ionicons name="trophy" size={20} color="#FF69B4" />
              <Text style={styles.statValue}>Lvl {currentLevel}</Text>
            </View>
            <Text style={styles.statLabel}>LEVEL</Text>
          </View>
          
          <View style={styles.statCard}>
            <View style={styles.statHeader}>
              <Ionicons name="flash" size={20} color="#FF4500" />
              <Text style={styles.statValue}>{currentStreak}</Text>
            </View>
            <Text style={styles.statLabel}>STREAK</Text>
          </View>
        </View>

        {/* Level Progress */}
        <View style={styles.progressCard}>
          <Text style={styles.progressTitle}>Your Progress 📈</Text>
          <View style={styles.progressBar}>
            <View style={[styles.progressFill, { width: `${levelProgress}%` }]} />
          </View>
          <Text style={styles.progressText}>
            {experienceForNext} points to Level {currentLevel + 1}
          </Text>
        </View>

        {/* Today's Tasks */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Today&apos;s Daily Tasks ✅</Text>
          <Text style={styles.sectionSubtitle}>
            Complete these 3 daily tasks based on your relationship mode
          </Text>
          
          <View style={styles.dailyProgress}>
            <Text style={styles.progressLabel}>DAILY TASK</Text>
            <Text style={styles.progressValue}>{completedDailyTasks}/3</Text>
          </View>
          
          {dailyTasks.map((task, index) => (
            <View key={task.id} style={styles.taskCard}>
              <View style={styles.taskContent}>
                <Text style={styles.taskTitle}>{task.title}</Text>
                <Text style={styles.taskCategory}>{task.category}</Text>
              </View>
              {task.completed ? (
                <View style={styles.completedButton}>
                  <Text style={styles.completedText}>✓ Completed</Text>
                </View>
              ) : (
                <TouchableOpacity
                  style={styles.completeButton}
                  onPress={() => handleCompleteTask(task.id, task.points)}
                >
                  <Text style={styles.completeButtonText}>Mark as Complete</Text>
                </TouchableOpacity>
              )}
            </View>
          ))}
        </View>

        {/* Weekly Challenge */}
        {weeklyTask && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>This Week&apos;s Challenge 🔥</Text>
            
            <View style={styles.weeklyCard}>
              <View style={styles.weeklyHeader}>
                <View style={styles.weeklyBadge}>
                  <Text style={styles.weeklyBadgeText}>WEEKLY</Text>
                </View>
                <Text style={styles.weeklyPoints}>25 points</Text>
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

        {/* Enhanced Features Tabs */}
        <View style={styles.section}>
          {/* Tab Headers */}
          <ScrollView 
            horizontal 
            showsHorizontalScrollIndicator={false}
            style={styles.tabHeaderContainer}
            contentContainerStyle={styles.tabHeaderContent}
          >
            {[
              { id: 'tips', title: 'Daily Tips', icon: 'bulb' },
              { id: 'events', title: 'Upcoming', icon: 'calendar' },
              { id: 'winners', title: 'Winners', icon: 'trophy' },
              { id: 'rules', title: 'Rules', icon: 'book' },
              { id: 'why', title: 'Why This', icon: 'heart' },
            ].map((tab) => (
              <TouchableOpacity
                key={tab.id}
                style={[
                  styles.tabHeader,
                  activeTab === tab.id && styles.activeTabHeader
                ]}
                onPress={() => setActiveTab(tab.id)}
              >
                <Ionicons 
                  name={tab.icon as any} 
                  size={18} 
                  color={activeTab === tab.id ? '#fff' : '#FF69B4'} 
                />
                <Text style={[
                  styles.tabHeaderText,
                  activeTab === tab.id && styles.activeTabHeaderText
                ]}>
                  {tab.title}
                </Text>
              </TouchableOpacity>
            ))}
          </ScrollView>

          {/* Tab Content */}
          <View style={styles.tabContentCard}>
            {renderTabContent()}
          </View>
        </View>

        {/* Quick Actions */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Quick Actions</Text>
          <View style={styles.quickActions}>
            <TouchableOpacity style={styles.actionButton}>
              <Ionicons name="gift" size={24} color="#FF69B4" />
              <Text style={styles.actionText}>Gift Ideas</Text>
            </TouchableOpacity>
            <TouchableOpacity style={styles.actionButton}>
              <Ionicons name="heart" size={24} color="#FF69B4" />
              <Text style={styles.actionText}>Love Messages</Text>
            </TouchableOpacity>
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
  header: {
    padding: 20,
    backgroundColor: '#fff',
    marginBottom: 10,
  },
  greeting: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 5,
  },
  subtitle: {
    fontSize: 14,
    color: '#666',
  },
  statsContainer: {
    flexDirection: 'row',
    paddingHorizontal: 20,
    marginBottom: 20,
    gap: 10,
  },
  statCard: {
    flex: 1,
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 15,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  statHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 5,
    gap: 5,
  },
  statValue: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
  },
  statLabel: {
    fontSize: 10,
    color: '#666',
    fontWeight: '600',
  },
  progressCard: {
    margin: 20,
    marginBottom: 10,
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  progressTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 15,
  },
  progressBar: {
    height: 8,
    backgroundColor: '#e0e0e0',
    borderRadius: 4,
    marginBottom: 10,
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#FF69B4',
    borderRadius: 4,
  },
  progressText: {
    fontSize: 14,
    color: '#666',
    textAlign: 'center',
  },
  section: {
    margin: 20,
    marginBottom: 10,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 5,
  },
  sectionSubtitle: {
    fontSize: 14,
    color: '#666',
    marginBottom: 15,
  },
  dailyProgress: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#fff',
    borderRadius: 8,
    padding: 15,
    marginBottom: 15,
  },
  progressLabel: {
    fontSize: 12,
    fontWeight: '600',
    color: '#666',
  },
  progressValue: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#FF69B4',
  },
  taskCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 15,
    marginBottom: 10,
    flexDirection: 'row',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
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
    backgroundColor: '#4CAF50',
    borderRadius: 20,
    paddingHorizontal: 15,
    paddingVertical: 8,
  },
  completedText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: '600',
  },
  weeklyTaskCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 20,
    flexDirection: 'row',
    alignItems: 'center',
    borderLeftWidth: 4,
    borderLeftColor: '#FF69B4',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  weeklyPoints: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#FF69B4',
    marginTop: 5,
  },
  quickActions: {
    flexDirection: 'row',
    gap: 15,
  },
  actionButton: {
    flex: 1,
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 20,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  actionText: {
    marginTop: 8,
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
  },
  // New Weekly Challenge Styles
  weeklyCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 20,
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
  weeklyTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 5,
  },
  weeklyCategory: {
    fontSize: 14,
    color: '#666',
    marginBottom: 15,
  },
  weeklyCompleted: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 15,
    backgroundColor: '#f0f8f0',
    borderRadius: 8,
  },
  weeklyCompletedText: {
    marginLeft: 8,
    fontSize: 16,
    fontWeight: 'bold',
    color: '#4CAF50',
  },
  weeklyCompleteButton: {
    backgroundColor: '#FF69B4',
    borderRadius: 8,
    padding: 15,
    alignItems: 'center',
  },
  weeklyCompleteButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  // Enhanced Features Tab Styles
  tabHeaderContainer: {
    marginBottom: 15,
  },
  tabHeaderContent: {
    paddingHorizontal: 20,
  },
  tabHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#fff',
    borderRadius: 20,
    paddingHorizontal: 15,
    paddingVertical: 8,
    marginRight: 10,
    borderWidth: 1,
    borderColor: '#FF69B4',
  },
  activeTabHeader: {
    backgroundColor: '#FF69B4',
  },
  tabHeaderText: {
    marginLeft: 5,
    fontSize: 14,
    fontWeight: '600',
    color: '#FF69B4',
  },
  activeTabHeaderText: {
    color: '#fff',
  },
  tabContentCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 20,
    marginHorizontal: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  tabContent: {
    minHeight: 150,
  },
  tabContentTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 15,
  },
  tabContentText: {
    fontSize: 14,
    color: '#666',
    lineHeight: 22,
  },
});