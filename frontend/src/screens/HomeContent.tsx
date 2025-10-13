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
import { Ionicons } from '@expo/vector-icons';
import { useAuthStore } from '../stores/useAuthStore';
import { useTaskStore } from '../stores/useTaskStore';
import { useGameStore } from '../stores/useGameStore';
import { useTheme } from '../contexts/ThemeContext';

const { width } = Dimensions.get('window');

interface Winner {
  id: string;
  user_name: string;
  prize_amount?: number;
  prize_type: string;
  week_number?: number;
  month?: string;
  tasks_completed: number;
  awarded_date: string;
  description: string;
}

interface UpcomingEvent {
  id: string;
  name: string;
  date: string;
  category: string;
  prefilled?: boolean;
  type?: string;
  description?: string;
  days_until?: number;
}

export default function HomeContent() {
  const { user, token } = useAuthStore();
  const { dailyTasks, weeklyTask, fetchDailyTasks, fetchWeeklyTask, completeTask } = useTaskStore();
  const { 
    totalPoints, 
    currentLevel, 
    currentStreak,
    badges,
    addExperience,
    loadPersistedData
  } = useGameStore();
  const { theme } = useTheme();

  const [refreshing, setRefreshing] = useState(false);
  const [activeTab, setActiveTab] = useState('tips');
  const [winners, setWinners] = useState<Winner[]>([]);
  const [upcomingEvents, setUpcomingEvents] = useState<UpcomingEvent[]>([]);
  const [eventsLoading, setEventsLoading] = useState(false);

  // Helper function to format event display
  const formatEventDate = (event: UpcomingEvent) => {
    const eventDate = new Date(event.date);
    const options: Intl.DateTimeFormatOptions = { 
      month: 'short', 
      day: 'numeric' 
    };
    const formattedDate = eventDate.toLocaleDateString('en-US', options);
    
    if (event.days_until === 0) {
      return 'Today';
    } else if (event.days_until === 1) {
      return 'Tomorrow';
    } else if (event.days_until <= 7) {
      return `${event.days_until} days`;
    } else {
      return formattedDate;
    }
  };

  useEffect(() => {
    // Initialize game store data
    loadPersistedData();
  }, []);

  useEffect(() => {
    if (token) {
      fetchDailyTasks(token);
      fetchWeeklyTask(token);
      fetchWinners();
      fetchUpcomingEvents();
    }
  }, [token]);

  const fetchWinners = async () => {
    try {
      const response = await fetch(`${process.env.EXPO_PUBLIC_BACKEND_URL}/api/winners`);
      const data = await response.json();
      if (response.ok) {
        setWinners(data.winners || []);
      }
    } catch (error) {
      console.error('Error fetching winners:', error);
    }
  };

  const fetchUpcomingEvents = async () => {
    if (!token) return;
    
    setEventsLoading(true);
    try {
      const response = await fetch(`${process.env.EXPO_PUBLIC_BACKEND_URL}/api/events?limit=5&offset=0`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      
      const data = await response.json();
      if (response.ok) {
        // Filter for upcoming events and calculate days until each event
        const now = new Date();
        const upcoming = data.events
          .map((event: any) => {
            const eventDate = new Date(event.date);
            const diffTime = eventDate.getTime() - now.getTime();
            const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
            
            return {
              id: event.id,
              name: event.name,
              date: event.date,
              category: event.category,
              prefilled: event.prefilled,
              type: event.type,
              description: event.description,
              days_until: diffDays
            };
          })
          .filter((event: UpcomingEvent) => event.days_until >= 0) // Only future events
          .slice(0, 5); // Limit to 5 upcoming events
        
        setUpcomingEvents(upcoming);
      } else {
        console.error('Error fetching events:', data);
      }
    } catch (error) {
      console.error('Error fetching upcoming events:', error);
    } finally {
      setEventsLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    if (token) {
      await Promise.all([
        fetchDailyTasks(token),
        fetchWeeklyTask(token),
        fetchWinners(),
        fetchUpcomingEvents()
      ]);
    }
    setRefreshing(false);
  };

  const handleCompleteTask = async (taskId: string, points: number) => {
    try {
      const success = await completeTask(taskId, token);
      if (success) {
        Alert.alert(
          '🎉 Task Completed!', 
          `Great job! You earned ${points} points.`,
          [{ text: 'Awesome!', style: 'default' }]
        );
        addExperience(points);
        // Refresh tasks
        await fetchDailyTasks(token);
        await fetchWeeklyTask(token);
      } else {
        Alert.alert('Error', 'Failed to complete task. Please try again.');
      }
    } catch (error) {
      Alert.alert('Error', 'Something went wrong. Please try again.');
    }
  };

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 17) return 'Good afternoon';
    return 'Good evening';
  };

  const experienceForNext = 100 - (totalPoints % 100);
  const levelProgress = ((totalPoints % 100) / 100) * 100;

  const renderTabContent = () => {
    switch (activeTab) {
      case 'tips':
        return (
          <View style={styles.tabContent}>
            <Text style={[styles.tabContentTitle, { color: theme.text }]}>💡 Daily Relationship Tips</Text>
            <Text style={[styles.tabContentText, { color: theme.textSecondary }]}>
              • Start each day with a loving message{'\n'}• Listen actively when your partner speaks{'\n'}• Express gratitude for small gestures{'\n'}• Plan surprise moments together{'\n'}• Share your feelings openly and honestly
            </Text>
          </View>
        );
      case 'events':
        return (
          <View style={styles.tabContent}>
            <Text style={[styles.tabContentTitle, { color: theme.text }]}>📅 Upcoming Events</Text>
            {eventsLoading ? (
              <Text style={[styles.tabContentText, { color: theme.textSecondary }]}>
                Loading upcoming events... 📅
              </Text>
            ) : upcomingEvents.length > 0 ? (
              <View>
                {upcomingEvents.map((event, index) => (
                  <View key={event.id} style={styles.eventItem}>
                    <View style={styles.eventMainInfo}>
                      <Text style={[styles.eventName, { color: theme.text }]}>
                        {event.prefilled ? '🎉' : '📝'} {event.name}
                      </Text>
                      <Text style={[styles.eventDate, { color: theme.primary }]}>
                        {formatEventDate(event)}
                      </Text>
                    </View>
                    {event.description && (
                      <Text style={[styles.eventDescription, { color: theme.textSecondary }]} numberOfLines={1}>
                        {event.description}
                      </Text>
                    )}
                  </View>
                ))}
                <TouchableOpacity 
                  style={[styles.viewAllButton, { borderColor: theme.primary }]}
                  onPress={() => {
                    // Navigate to events tab - you might need to implement this navigation
                    console.log('Navigate to events tab');
                  }}
                >
                  <Text style={[styles.viewAllText, { color: theme.primary }]}>View All Events</Text>
                </TouchableOpacity>
              </View>
            ) : (
              <Text style={[styles.tabContentText, { color: theme.textSecondary }]}>
                No upcoming events found.{'\n'}Add some events in the Events tab! 📅
              </Text>
            )}
          </View>
        );
      case 'winners':
        return (
          <View style={styles.tabContent}>
            <Text style={[styles.tabContentTitle, { color: theme.text }]}>🏆 Recent Winners</Text>
            {winners.length > 0 ? (
              <ScrollView style={styles.winnersContainer}>
                {winners.slice(0, 3).map((winner, index) => (
                  <View key={winner.id} style={[styles.winnerCard, { backgroundColor: theme.surface, borderLeftColor: theme.primary }]}>
                    <View style={[styles.winnerRank, { backgroundColor: theme.primary }]}>
                      <Text style={styles.winnerRankText}>{index + 1}</Text>
                    </View>
                    <View style={styles.winnerInfo}>
                      <Text style={[styles.winnerName, { color: theme.text }]}>{winner.user_name}</Text>
                      <Text style={[styles.winnerPrize, { color: theme.primary }]}>
                        {winner.prize_type === 'weekly_cash' 
                          ? `₹${winner.prize_amount} - Week ${winner.week_number}`
                          : `Couple Trip - ${winner.month}`
                        }
                      </Text>
                      <Text style={[styles.winnerTasks, { color: theme.textSecondary }]}>{winner.tasks_completed} tasks completed</Text>
                    </View>
                  </View>
                ))}
              </ScrollView>
            ) : (
              <Text style={[styles.tabContentText, { color: theme.textSecondary }]}>
                Loading recent winners... 🏆
              </Text>
            )}
          </View>
        );
      case 'rules':
        return (
          <View style={styles.tabContent}>
            <Text style={[styles.tabContentTitle, { color: theme.text }]}>📖 How It Works</Text>
            <Text style={[styles.tabContentText, { color: theme.textSecondary }]}>
              • Complete daily tasks to earn points{'\n'}• Weekly challenges give bonus points{'\n'}• Build streaks for multiplier bonuses{'\n'}• Level up to unlock new features{'\n'}• Share achievements with your partner
            </Text>
          </View>
        );
      case 'why':
        return (
          <View style={styles.tabContent}>
            <Text style={[styles.tabContentTitle, { color: theme.text }]}>❤️ Why This Matters</Text>
            <Text style={[styles.tabContentText, { color: theme.textSecondary }]}>
              • Strengthens emotional connection{'\n'}• Creates positive daily habits{'\n'}• Encourages thoughtful gestures{'\n'}• Builds lasting memories together{'\n'}• Makes love a daily practice, not just a feeling
            </Text>
          </View>
        );
      default:
        return null;
    }
  };

  return (
    <ScrollView
      style={[styles.scrollView, { backgroundColor: theme.background }]}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
    >
      {/* Header Greeting */}
      <View style={[styles.header, { backgroundColor: theme.surface }]}>
        <Text style={[styles.greeting, { color: theme.text }]}>{getGreeting()}, {user?.name || 'Loverboy'}! 💕</Text>
        <Text style={[styles.subtitle, { color: theme.textSecondary }]}>Let's make today special for your partner</Text>
      </View>

      {/* Stats Cards */}
      <View style={styles.statsContainer}>
        <View style={[styles.statCard, { backgroundColor: theme.surface }]}>
          <Ionicons name="star" size={24} color="#FFD700" />
          <Text style={[styles.statNumber, { color: theme.text }]}>{totalPoints}</Text>
          <Text style={[styles.statLabel, { color: theme.textSecondary }]}>Total Points</Text>
        </View>
        <View style={[styles.statCard, { backgroundColor: theme.surface }]}>
          <Ionicons name="trophy" size={24} color={theme.primary} />
          <Text style={[styles.statNumber, { color: theme.text }]}>Level {currentLevel}</Text>
          <Text style={[styles.statLabel, { color: theme.textSecondary }]}>Current Level</Text>
        </View>
        <View style={[styles.statCard, { backgroundColor: theme.surface }]}>
          <Ionicons name="flash" size={24} color="#FF4500" />
          <Text style={[styles.statNumber, { color: theme.text }]}>{currentStreak}</Text>
          <Text style={[styles.statLabel, { color: theme.textSecondary }]}>Day Streak</Text>
        </View>
      </View>

      {/* Progress Bar */}
      <View style={[styles.progressContainer, { backgroundColor: theme.surface }]}>
        <View style={styles.progressHeader}>
          <Text style={[styles.progressTitle, { color: theme.text }]}>Level {currentLevel} Progress</Text>
          <Text style={[styles.progressSubtitle, { color: theme.textSecondary }]}>{experienceForNext} points to next level</Text>
        </View>
        <View style={[styles.progressBarBackground, { backgroundColor: theme.border }]}>
          <View style={[styles.progressBarFill, { backgroundColor: theme.primary, width: `${levelProgress}%` }]} />
        </View>
      </View>

      {/* Today's Tasks */}
      <View style={styles.section}>
        <Text style={[styles.sectionTitle, { color: theme.text }]}>Today's Daily Tasks ✅</Text>
        <Text style={[styles.sectionSubtitle, { color: theme.textSecondary }]}>
          Complete these 3 daily tasks based on your relationship mode
        </Text>
        
        {dailyTasks.map((task, index) => (
          <View key={task.id} style={[styles.taskCard, { backgroundColor: theme.surface }]}>
            <View style={styles.taskContent}>
              <Text style={[styles.taskTitle, { color: theme.text }]}>{task.title}</Text>
              <Text style={[styles.taskCategory, { color: theme.primary }]}>{task.category}</Text>
              <Text style={[styles.taskPoints, { color: theme.success }]}>+{task.points} points</Text>
            </View>
            {task.completed ? (
              <View style={styles.completedButton}>
                <Ionicons name="checkmark-circle" size={24} color={theme.success} />
                <Text style={[styles.completedText, { color: theme.success }]}>Done!</Text>
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
        ))}
        
        {dailyTasks.length === 0 && (
          <View style={styles.noTasksContainer}>
            <Ionicons name="heart-outline" size={48} color={theme.border} />
            <Text style={[styles.noTasksText, { color: theme.textSecondary }]}>No tasks available</Text>
            <Text style={[styles.noTasksSubtext, { color: theme.border }]}>Pull down to refresh</Text>
          </View>
        )}
      </View>

      {/* Weekly Challenge */}
      {weeklyTask && (
        <View style={styles.section}>
          <Text style={[styles.sectionTitle, { color: theme.text }]}>This Week's Challenge 🔥</Text>
          
          <View style={[styles.weeklyCard, { backgroundColor: theme.surface }]}>
            <View style={styles.weeklyHeader}>
              <View style={[styles.weeklyBadge, { backgroundColor: theme.primary }]}>
                <Text style={styles.weeklyBadgeText}>WEEKLY</Text>
              </View>
              <Text style={[styles.weeklyPoints, { color: theme.success }]}>25 points</Text>
            </View>
            
            <Text style={[styles.weeklyTitle, { color: theme.text }]}>{weeklyTask.title}</Text>
            <Text style={[styles.weeklyCategory, { color: theme.textSecondary }]}>{weeklyTask.category}</Text>
            
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
                { backgroundColor: theme.surface, borderColor: theme.border },
                activeTab === tab.id && { backgroundColor: theme.primary }
              ]}
              onPress={() => setActiveTab(tab.id)}
            >
              <Ionicons 
                name={tab.icon as any} 
                size={18} 
                color={activeTab === tab.id ? '#fff' : theme.primary} 
              />
              <Text style={[
                styles.tabHeaderText,
                { color: theme.primary },
                activeTab === tab.id && { color: '#fff' }
              ]}>
                {tab.title}
              </Text>
            </TouchableOpacity>
          ))}
        </ScrollView>

        {/* Tab Content */}
        <View style={[styles.tabContentCard, { backgroundColor: theme.surface }]}>
          {renderTabContent()}
        </View>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  scrollView: {
    flex: 1,
  },
  header: {
    padding: 20,
    alignItems: 'center',
    marginBottom: 10,
  },
  greeting: {
    fontSize: 24,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 5,
  },
  subtitle: {
    fontSize: 16,
    textAlign: 'center',
  },
  statsContainer: {
    flexDirection: 'row',
    paddingHorizontal: 20,
    marginBottom: 20,
    gap: 10,
  },
  statCard: {
    flex: 1,
    borderRadius: 15,
    padding: 20,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  statNumber: {
    fontSize: 18,
    fontWeight: 'bold',
    marginTop: 8,
    marginBottom: 4,
  },
  statLabel: {
    fontSize: 12,
    textAlign: 'center',
  },
  progressContainer: {
    marginHorizontal: 20,
    borderRadius: 15,
    padding: 20,
    marginBottom: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  progressHeader: {
    marginBottom: 15,
  },
  progressTitle: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 5,
  },
  progressSubtitle: {
    fontSize: 14,
  },
  progressBarBackground: {
    height: 8,
    borderRadius: 4,
    overflow: 'hidden',
  },
  progressBarFill: {
    height: '100%',
    borderRadius: 4,
  },
  section: {
    marginHorizontal: 20,
    marginBottom: 25,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 8,
  },
  sectionSubtitle: {
    fontSize: 14,
    marginBottom: 15,
  },
  taskCard: {
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
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
    marginBottom: 4,
  },
  taskCategory: {
    fontSize: 12,
    fontWeight: '500',
    marginBottom: 2,
  },
  taskPoints: {
    fontSize: 12,
    fontWeight: '600',
  },
  completeButton: {
    borderRadius: 8,
    paddingHorizontal: 16,
    paddingVertical: 8,
  },
  completeButtonText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
  },
  completedButton: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  completedText: {
    fontSize: 14,
    fontWeight: '600',
  },
  noTasksContainer: {
    alignItems: 'center',
    paddingVertical: 40,
  },
  noTasksText: {
    fontSize: 16,
    marginTop: 10,
  },
  noTasksSubtext: {
    fontSize: 14,
    marginTop: 5,
  },
  weeklyCard: {
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
    fontSize: 14,
    fontWeight: 'bold',
  },
  weeklyTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 5,
  },
  weeklyCategory: {
    fontSize: 14,
    marginBottom: 15,
  },
  weeklyCompleted: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 15,
    borderRadius: 8,
    gap: 10,
  },
  weeklyCompletedText: {
    fontSize: 16,
    fontWeight: 'bold',
  },
  weeklyCompleteButton: {
    borderRadius: 8,
    padding: 15,
    alignItems: 'center',
  },
  weeklyCompleteButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  tabHeaderContainer: {
    marginBottom: 15,
  },
  tabHeaderContent: {
    paddingHorizontal: 0,
    gap: 10,
  },
  tabHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    borderRadius: 20,
    paddingHorizontal: 15,
    paddingVertical: 8,
    gap: 6,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
    borderWidth: 1,
  },
  tabHeaderText: {
    fontSize: 12,
    fontWeight: '600',
  },
  tabContentCard: {
    borderRadius: 12,
    padding: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  tabContent: {
    minHeight: 120,
  },
  tabContentTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 12,
  },
  tabContentText: {
    fontSize: 14,
    lineHeight: 22,
  },
  winnersContainer: {
    maxHeight: 200,
  },
  winnerCard: {
    flexDirection: 'row',
    alignItems: 'center',
    borderRadius: 8,
    padding: 12,
    marginBottom: 8,
    borderLeftWidth: 3,
  },
  winnerRank: {
    width: 30,
    height: 30,
    borderRadius: 15,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  winnerRankText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: 'bold',
  },
  winnerInfo: {
    flex: 1,
  },
  winnerName: {
    fontSize: 14,
    fontWeight: '600',
    marginBottom: 2,
  },
  winnerPrize: {
    fontSize: 12,
    fontWeight: '500',
    marginBottom: 2,
  },
  winnerTasks: {
    fontSize: 11,
  },
  
  // Event styles
  eventItem: {
    backgroundColor: 'rgba(255, 255, 255, 0.1)',
    borderRadius: 8,
    padding: 12,
    marginBottom: 8,
    borderLeftWidth: 3,
    borderLeftColor: '#FF1493',
  },
  eventMainInfo: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 4,
  },
  eventName: {
    flex: 1,
    fontSize: 14,
    fontWeight: '600',
    marginRight: 8,
  },
  eventDate: {
    fontSize: 12,
    fontWeight: '500',
    backgroundColor: 'rgba(255, 20, 147, 0.1)',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  eventDescription: {
    fontSize: 12,
    fontStyle: 'italic',
    marginTop: 2,
  },
  viewAllButton: {
    borderWidth: 1,
    borderRadius: 6,
    paddingVertical: 8,
    paddingHorizontal: 16,
    alignItems: 'center',
    marginTop: 12,
    borderStyle: 'dashed',
  },
  viewAllText: {
    fontSize: 12,
    fontWeight: '500',
  },
});