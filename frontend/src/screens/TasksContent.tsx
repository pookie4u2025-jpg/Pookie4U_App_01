import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  RefreshControl,
  ActivityIndicator,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useAuthStore } from '../stores/useAuthStore';
import { useTaskStore } from '../stores/useTaskStore';
import { useGameStore } from '../stores/useGameStore';
import { useTheme } from '../contexts/ThemeContext';

export default function TasksContent() {
  const { token, user } = useAuthStore();
  const { dailyTasks, weeklyTask, fetchDailyTasks, fetchWeeklyTask, completeTask: completeTaskAPI } = useTaskStore();
  const { completeTask: updateGameProgress } = useGameStore();
  const { theme } = useTheme();

  const [refreshing, setRefreshing] = useState(false);
  const [regenerating, setRegenerating] = useState({ daily: false, weekly: false });

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

  // Function to regenerate AI tasks for current relationship mode
  const regenerateTasks = async (taskType: 'daily' | 'weekly') => {
    if (!token) return;
    
    setRegenerating(prev => ({ ...prev, [taskType]: true }));
    
    try {
      if (taskType === 'daily') {
        await fetchDailyTasks(token, true); // Pass regenerate=true
      } else {
        await fetchWeeklyTask(token, true); // Pass regenerate=true
      }
      
      Alert.alert(
        '🤖 AI Tasks Generated!',
        `New ${taskType} tasks have been generated based on your relationship mode!`,
        [{ text: 'Great!', style: 'default' }]
      );
    } catch (error) {
      Alert.alert('Error', `Failed to regenerate ${taskType} tasks. Please try again.`);
    } finally {
      setRegenerating(prev => ({ ...prev, [taskType]: false }));
    }
  };

  // Get relationship mode display name
  const getRelationshipModeDisplay = (mode: string) => {
    switch (mode) {
      case 'SAME_HOME': return 'Living Together';
      case 'DAILY_IRL': return 'Daily Meetings';
      case 'LONG_DISTANCE': return 'Long Distance';
      default: return mode;
    }
  };

  // Get category icon
  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'Communication': return 'chatbubble-outline';
      case 'ThoughtfulGesture': return 'heart-outline';
      case 'MicroActivity': return 'flash-outline';
      case 'PhysicalActivity': return 'fitness-outline';
      case 'Activities': return 'game-controller-outline';
      case 'Thoughtful Gestures': return 'heart-outline';
      case 'Planning': return 'calendar-outline';
      case 'Intimacy': return 'people-outline';
      case 'Self-care': return 'leaf-outline';
      default: return 'star-outline';
    }
  };

  const handleCompleteTask = async (taskId: string, points: number) => {
    if (!token) return;
    
    const success = await completeTaskAPI(taskId, token);
    if (success) {
      // Update game progress (points, streak, badges)
      await updateGameProgress(points);
      
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
    <View style={[styles.container, { backgroundColor: theme.background }]}>
      <ScrollView
        style={styles.scrollView}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
      >
        {/* Daily Tasks Progress */}
        <View style={[styles.progressCard, { backgroundColor: theme.surface }]}>
          <Text style={[styles.progressTitle, { color: theme.text }]}>Today's Progress</Text>
          <View style={[styles.progressBar, { backgroundColor: theme.border }]}>
            <View style={[styles.progressFill, { backgroundColor: theme.primary }]} />
          </View>
          <Text style={[styles.progressText, { color: theme.textSecondary }]}>
            {completedDailyTasks} of {dailyTasks.length} daily tasks completed
          </Text>
        </View>

        {/* Daily Tasks */}
        <View style={styles.section}>
          <View style={styles.sectionHeader}>
            <View style={styles.sectionTitleContainer}>
              <Text style={[styles.sectionTitle, { color: theme.text }]}>🤖 AI Daily Tasks</Text>
              {user?.relationship_mode && (
                <View style={[styles.modeTag, { backgroundColor: theme.primary }]}>
                  <Text style={styles.modeTagText}>
                    {getRelationshipModeDisplay(user.relationship_mode)}
                  </Text>
                </View>
              )}
            </View>
            <TouchableOpacity
              style={[styles.regenerateButton, { backgroundColor: theme.surface }]}
              onPress={() => regenerateTasks('daily')}
              disabled={regenerating.daily}
            >
              {regenerating.daily ? (
                <ActivityIndicator size="small" color={theme.primary} />
              ) : (
                <Ionicons name="refresh" size={20} color={theme.primary} />
              )}
            </TouchableOpacity>
          </View>
          
          <Text style={[styles.sectionSubtitle, { color: theme.textSecondary }]}>
            AI-generated tasks personalized for your relationship mode
          </Text>
          
          {dailyTasks.map((task, index) => (
            <View key={task.id} style={[styles.taskCard, { backgroundColor: theme.surface }]}>
              <View style={styles.taskHeader}>
                <View style={[styles.taskNumber, { backgroundColor: theme.primary }]}>
                  <Text style={styles.taskNumberText}>{index + 1}</Text>
                </View>
                <View style={styles.taskContent}>
                  <Text style={[styles.taskTitle, { color: theme.text }]}>{task.title}</Text>
                  
                  {/* Task description */}
                  {task.description && (
                    <Text style={[styles.taskDescription, { color: theme.textSecondary }]}>
                      {task.description}
                    </Text>
                  )}
                  
                  {/* Enhanced category display with icon */}
                  <View style={styles.taskMeta}>
                    <View style={styles.categoryContainer}>
                      <Ionicons 
                        name={getCategoryIcon(task.category)} 
                        size={14} 
                        color={theme.primary} 
                      />
                      <Text style={[styles.taskCategory, { color: theme.textSecondary }]}>
                        {task.category}
                      </Text>
                    </View>
                    
                    {/* Physical task badge */}
                    {task.is_physical && (
                      <View style={[styles.physicalBadge, { backgroundColor: '#FF6B35' + '20' }]}>
                        <Text style={[styles.physicalBadgeText, { color: '#FF6B35' }]}>
                          💪 Physical
                        </Text>
                      </View>
                    )}
                    
                    {/* AI Generation badge */}
                    {task.generation_metadata && (
                      <View style={[styles.aibadge, { backgroundColor: theme.primary + '20' }]}>
                        <Text style={[styles.aiBadgeText, { color: theme.primary }]}>
                          AI ✨
                        </Text>
                      </View>
                    )}
                  </View>
                  
                  <View style={styles.taskPoints}>
                    <Ionicons name="star" size={14} color="#FFD700" />
                    <Text style={styles.pointsText}>{task.points} points</Text>
                    {task.estimated_time_minutes && (
                      <>
                        <Text style={[styles.dotSeparator, { color: theme.textSecondary }]}> • </Text>
                        <Ionicons name="time-outline" size={14} color={theme.textSecondary} />
                        <Text style={[styles.timeText, { color: theme.textSecondary }]}>
                          {task.estimated_time_minutes}min
                        </Text>
                      </>
                    )}
                    {task.difficulty && (
                      <>
                        <Text style={[styles.dotSeparator, { color: theme.textSecondary }]}> • </Text>
                        <Text style={[styles.difficultyText, { color: theme.textSecondary }]}>
                          {task.difficulty.replace('_', ' ')}
                        </Text>
                      </>
                    )}
                  </View>
                  
                  {/* Task tips */}
                  {task.tips && (
                    <Text style={[styles.taskTips, { color: theme.textSecondary }]}>
                      💡 {task.tips}
                    </Text>
                  )}
                </View>
                
                {task.completed ? (
                  <View style={styles.completedButton}>
                    <Ionicons name="checkmark-circle" size={24} color={theme.success} />
                    <Text style={[styles.completedText, { color: theme.success }]}>Done</Text>
                  </View>
                ) : (
                  <TouchableOpacity
                    style={[styles.completeButton, { backgroundColor: theme.primary }]}
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
        <View style={styles.section}>
          <View style={styles.sectionHeader}>
            <View style={styles.sectionTitleContainer}>
              <Text style={[styles.sectionTitle, { color: theme.text }]}>🤖 AI Weekly Challenge</Text>
              {user?.relationship_mode && (
                <View style={[styles.modeTag, { backgroundColor: theme.primary }]}>
                  <Text style={styles.modeTagText}>
                    {getRelationshipModeDisplay(user.relationship_mode)}
                  </Text>
                </View>
              )}
            </View>
            <TouchableOpacity
              style={[styles.regenerateButton, { backgroundColor: theme.surface }]}
              onPress={() => regenerateTasks('weekly')}
              disabled={regenerating.weekly}
            >
              {regenerating.weekly ? (
                <ActivityIndicator size="small" color={theme.primary} />
              ) : (
                <Ionicons name="refresh" size={20} color={theme.primary} />
              )}
            </TouchableOpacity>
          </View>
          
          {weeklyTask ? (
            <>
              <Text style={[styles.sectionSubtitle, { color: theme.textSecondary }]}>
                AI-generated weekly physical challenge for your relationship
              </Text>
              
              <View style={[styles.weeklyCard, { backgroundColor: theme.surface, borderLeftColor: theme.primary }]}>
              <View style={styles.weeklyHeader}>
                <View style={[styles.weeklyBadge, { backgroundColor: theme.primary }]}>
                  <Text style={styles.weeklyBadgeText}>WEEKLY</Text>
                </View>
                <View style={styles.weeklyPoints}>
                  <Ionicons name="star" size={16} color="#FFD700" />
                  <Text style={styles.weeklyPointsText}>25 points</Text>
                </View>
              </View>
              
              <Text style={[styles.weeklyTitle, { color: theme.text }]}>{weeklyTask.title}</Text>
              
              {/* Weekly task description */}
              {weeklyTask.description && (
                <Text style={[styles.weeklyDescription, { color: theme.textSecondary }]}>
                  {weeklyTask.description}
                </Text>
              )}
              
              <View style={styles.weeklyMeta}>
                <View style={styles.categoryContainer}>
                  <Ionicons 
                    name={getCategoryIcon(weeklyTask.category)} 
                    size={16} 
                    color={theme.primary} 
                  />
                  <Text style={[styles.weeklyCategory, { color: theme.textSecondary }]}>
                    {weeklyTask.category}
                  </Text>
                </View>
                
                {/* Physical badge for weekly task */}
                {weeklyTask.is_physical && (
                  <View style={[styles.physicalBadge, { backgroundColor: '#FF6B35' + '20' }]}>
                    <Text style={[styles.physicalBadgeText, { color: '#FF6B35' }]}>
                      💪 Physical
                    </Text>
                  </View>
                )}
                
                {/* AI Generation badge */}
                {weeklyTask.generation_metadata && (
                  <View style={[styles.aibadge, { backgroundColor: theme.primary + '20' }]}>
                    <Text style={[styles.aiBadgeText, { color: theme.primary }]}>
                      AI ✨
                    </Text>
                  </View>
                )}
              </View>
              
              {/* Weekly task metadata */}
              <View style={styles.weeklyTaskMeta}>
                {weeklyTask.estimated_time_minutes && (
                  <View style={styles.metaItem}>
                    <Ionicons name="time-outline" size={14} color={theme.textSecondary} />
                    <Text style={[styles.metaText, { color: theme.textSecondary }]}>
                      {weeklyTask.estimated_time_minutes}min
                    </Text>
                  </View>
                )}
                {weeklyTask.difficulty && (
                  <View style={styles.metaItem}>
                    <Text style={[styles.metaText, { color: theme.textSecondary }]}>
                      {weeklyTask.difficulty.replace('_', ' ')}
                    </Text>
                  </View>
                )}
              </View>
              
              {weeklyTask.completed ? (
                <View style={styles.weeklyCompleted}>
                  <Ionicons name="checkmark-circle" size={32} color={theme.success} />
                  <Text style={[styles.weeklyCompletedText, { color: theme.success }]}>Challenge Completed!</Text>
                </View>
              ) : (
                <TouchableOpacity
                  style={[styles.weeklyCompleteButton, { backgroundColor: theme.primary }]}
                  onPress={() => handleCompleteTask(weeklyTask.id, weeklyTask.points)}
                >
                  <Text style={styles.weeklyCompleteButtonText}>Complete Challenge</Text>
                </TouchableOpacity>
              )}
              </View>
            </>
        ) : (
          <View style={[styles.emptyCard, { backgroundColor: theme.surface }]}>
            <Ionicons name="calendar-outline" size={48} color={theme.textSecondary} />
            <Text style={[styles.emptyTitle, { color: theme.text }]}>No Weekly Challenge</Text>
            <Text style={[styles.emptyMessage, { color: theme.textSecondary }]}>
              Your weekly challenge will appear here. Complete daily tasks to unlock weekly challenges!
            </Text>
          </View>
        )}

        </View>

        {/* Task Tips */}
        <View style={styles.section}>
          <Text style={[styles.sectionTitle, { color: theme.text }]}>Task Tips 💡</Text>
          <View style={[styles.tipsCard, { backgroundColor: theme.surface }]}>
            <Text style={[styles.tip, { color: theme.textSecondary }]}>• Take photos while completing tasks to create memories</Text>
            <Text style={[styles.tip, { color: theme.textSecondary }]}>• Don't rush - quality time matters more than speed</Text>
            <Text style={[styles.tip, { color: theme.textSecondary }]}>• Personalize tasks based on your partner's preferences</Text>
            <Text style={[styles.tip, { color: theme.textSecondary }]}>• Complete at least one task daily to maintain your streak</Text>
          </View>
        </View>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  scrollView: {
    flex: 1,
  },
  progressCard: {
    margin: 20,
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
    marginBottom: 15,
  },
  progressBar: {
    height: 10,
    borderRadius: 5,
    marginBottom: 10,
  },
  progressFill: {
    height: '100%',
    borderRadius: 5,
  },
  progressText: {
    fontSize: 14,
    textAlign: 'center',
  },
  section: {
    marginHorizontal: 20,
    marginBottom: 20,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 5,
  },
  sectionSubtitle: {
    fontSize: 14,
    marginBottom: 15,
  },
  taskCard: {
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
    marginBottom: 4,
  },
  taskCategory: {
    fontSize: 12,
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
    fontWeight: '600',
    marginTop: 2,
  },
  weeklyCard: {
    borderRadius: 15,
    padding: 20,
    borderLeftWidth: 4,
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
    marginBottom: 5,
  },
  weeklyCategory: {
    fontSize: 14,
    marginBottom: 20,
  },
  weeklyCompleteButton: {
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
    marginTop: 8,
  },
  tipsCard: {
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
    marginBottom: 8,
    lineHeight: 20,
  },
  // New styles for AI task features
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 5,
  },
  sectionTitleContainer: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    flexWrap: 'wrap',
  },
  modeTag: {
    marginLeft: 8,
    borderRadius: 12,
    paddingHorizontal: 8,
    paddingVertical: 2,
  },
  modeTagText: {
    color: '#fff',
    fontSize: 10,
    fontWeight: '600',
  },
  regenerateButton: {
    width: 36,
    height: 36,
    borderRadius: 18,
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 1,
    borderColor: '#e0e0e0',
  },
  taskMeta: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 6,
  },
  categoryContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  aibadge: {
    borderRadius: 10,
    paddingHorizontal: 6,
    paddingVertical: 2,
  },
  aiBadgeText: {
    fontSize: 10,
    fontWeight: '600',
  },
  dotSeparator: {
    fontSize: 12,
  },
  timeText: {
    fontSize: 12,
    marginLeft: 4,
  },
  taskTips: {
    fontSize: 12,
    fontStyle: 'italic',
    marginTop: 6,
    paddingTop: 6,
    borderTopWidth: 1,
    borderTopColor: '#f0f0f0',
  },
  // New styles for enhanced task features
  taskDescription: {
    fontSize: 14,
    marginBottom: 6,
    lineHeight: 18,
  },
  physicalBadge: {
    borderRadius: 10,
    paddingHorizontal: 6,
    paddingVertical: 2,
    marginLeft: 4,
  },
  physicalBadgeText: {
    fontSize: 10,
    fontWeight: '600',
  },
  difficultyText: {
    fontSize: 12,
    marginLeft: 4,
  },
  weeklyDescription: {
    fontSize: 14,
    marginBottom: 10,
    lineHeight: 18,
  },
  weeklyMeta: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 10,
  },
  weeklyTaskMeta: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 15,
  },
  metaItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginRight: 15,
  },
  metaText: {
    fontSize: 12,
    marginLeft: 4,
  },
  emptyCard: {
    margin: 20,
    borderRadius: 15,
    padding: 30,
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: 150,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  emptyTitle: {
    fontSize: 18,
    fontWeight: '600',
    marginTop: 15,
    marginBottom: 8,
  },
  emptyMessage: {
    fontSize: 14,
    textAlign: 'center',
    lineHeight: 20,
    maxWidth: 250,
  },
});