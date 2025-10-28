import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  ScrollView,
  RefreshControl,
  TouchableOpacity,
  Image,
  StyleSheet,
  ActivityIndicator
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../contexts/ThemeContext';
import { useAuthStore } from '../stores/useAuthStore';

interface LeaderboardUser {
  rank: number;
  user_id: string;
  display_name: string;
  points: number;
  profile_image: string | null;
  city: string;
  tasks_completed: number;
  current_streak: number;
  member_since: string;
}

export default function LeaderboardContent() {
  const { theme } = useTheme();
  const { token } = useAuthStore();
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [timeframe, setTimeframe] = useState<'all_time' | 'weekly'>('all_time');
  const [leaderboard, setLeaderboard] = useState<LeaderboardUser[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchLeaderboard();
  }, [timeframe]);

  const fetchLeaderboard = async () => {
    try {
      setError(null);
      const response = await fetch(
        `${process.env.EXPO_PUBLIC_BACKEND_URL}/api/leaderboard?timeframe=${timeframe}&limit=20`,
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );

      if (response.ok) {
        const data = await response.json();
        setLeaderboard(data.leaderboard || []);
      } else {
        setError('Failed to load leaderboard');
      }
    } catch (err) {
      console.error('Error fetching leaderboard:', err);
      setError('Network error');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    fetchLeaderboard();
  };

  const getRankIcon = (rank: number) => {
    if (rank === 1) return { name: 'trophy', color: '#FFD700' };
    if (rank === 2) return { name: 'medal', color: '#C0C0C0' };
    if (rank === 3) return { name: 'medal', color: '#CD7F32' };
    return { name: 'ribbon', color: theme.textSecondary };
  };

  const getRankStyle = (rank: number) => {
    if (rank === 1) return styles.firstPlace;
    if (rank === 2) return styles.secondPlace;
    if (rank === 3) return styles.thirdPlace;
    return {};
  };

  if (loading) {
    return (
      <View style={[styles.container, { backgroundColor: theme.background }]}>
        <ActivityIndicator size="large" color={theme.primary} />
      </View>
    );
  }

  return (
    <View style={[styles.container, { backgroundColor: theme.background }]}>
      {/* Header */}
      <View style={[styles.header, { backgroundColor: theme.surface }]}>
        <View style={styles.headerTop}>
          <Ionicons name="trophy" size={32} color="#FFD700" />
          <Text style={[styles.headerTitle, { color: theme.text }]}>
            Top Lovers
          </Text>
          <Ionicons name="trophy" size={32} color="#FFD700" />
        </View>
        <Text style={[styles.headerSubtitle, { color: theme.textSecondary }]}>
          Compete & win amazing prizes! 🎁
        </Text>
      </View>

      {/* Timeframe Toggle */}
      <View style={styles.toggleContainer}>
        <TouchableOpacity
          style={[
            styles.toggleButton,
            { backgroundColor: theme.surface, borderColor: theme.border },
            timeframe === 'all_time' && { backgroundColor: theme.primary, borderColor: theme.primary }
          ]}
          onPress={() => setTimeframe('all_time')}
        >
          <Text style={[
            styles.toggleText,
            { color: theme.textSecondary },
            timeframe === 'all_time' && { color: '#fff', fontWeight: 'bold' }
          ]}>
            All Time
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[
            styles.toggleButton,
            { backgroundColor: theme.surface, borderColor: theme.border },
            timeframe === 'weekly' && { backgroundColor: theme.primary, borderColor: theme.primary }
          ]}
          onPress={() => setTimeframe('weekly')}
        >
          <Text style={[
            styles.toggleText,
            { color: theme.textSecondary },
            timeframe === 'weekly' && { color: '#fff', fontWeight: 'bold' }
          ]}>
            This Week
          </Text>
        </TouchableOpacity>
      </View>

      {/* Leaderboard List */}
      <ScrollView
        style={styles.scrollView}
        contentContainerStyle={styles.scrollContent}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={theme.primary} />
        }
      >
        {error ? (
          <View style={styles.errorContainer}>
            <Ionicons name="alert-circle" size={48} color={theme.error} />
            <Text style={[styles.errorText, { color: theme.error }]}>{error}</Text>
            <TouchableOpacity style={[styles.retryButton, { backgroundColor: theme.primary }]} onPress={fetchLeaderboard}>
              <Text style={styles.retryText}>Retry</Text>
            </TouchableOpacity>
          </View>
        ) : leaderboard.length === 0 ? (
          <View style={styles.emptyContainer}>
            <Ionicons name="people-outline" size={64} color={theme.textSecondary} />
            <Text style={[styles.emptyText, { color: theme.textSecondary }]}>
              No users on the leaderboard yet
            </Text>
            <Text style={[styles.emptySubtext, { color: theme.textSecondary }]}>
              Complete tasks to be the first!
            </Text>
          </View>
        ) : (
          leaderboard.map((user, index) => (
            <View
              key={user.user_id}
              style={[
                styles.userCard,
                { backgroundColor: theme.surface, borderColor: theme.border },
                getRankStyle(user.rank)
              ]}
            >
              {/* Rank Badge */}
              <View style={styles.rankBadge}>
                <Ionicons 
                  name={getRankIcon(user.rank).name as any} 
                  size={24} 
                  color={getRankIcon(user.rank).color} 
                />
                <Text style={[styles.rankText, { color: getRankIcon(user.rank).color }]}>
                  #{user.rank}
                </Text>
              </View>

              {/* Profile Image */}
              <View style={styles.profileImageContainer}>
                {user.profile_image ? (
                  <Image source={{ uri: user.profile_image }} style={styles.profileImage} />
                ) : (
                  <View style={[styles.profileImagePlaceholder, { backgroundColor: theme.primary + '30' }]}>
                    <Ionicons name="people" size={24} color={theme.primary} />
                  </View>
                )}
              </View>

              {/* User Info */}
              <View style={styles.userInfo}>
                <Text style={[styles.userName, { color: theme.text }]} numberOfLines={1}>
                  {user.display_name}
                </Text>
                <View style={styles.userStats}>
                  <View style={styles.statItem}>
                    <Ionicons name="location" size={12} color={theme.textSecondary} />
                    <Text style={[styles.statText, { color: theme.textSecondary }]}>
                      {user.city}
                    </Text>
                  </View>
                  {user.current_streak > 0 && (
                    <View style={styles.statItem}>
                      <Ionicons name="flame" size={12} color="#FF6B35" />
                      <Text style={[styles.statText, { color: theme.textSecondary }]}>
                        {user.current_streak} day streak
                      </Text>
                    </View>
                  )}
                </View>
              </View>

              {/* Points */}
              <View style={styles.pointsContainer}>
                <Text style={[styles.pointsValue, { color: '#FFD700' }]}>
                  {user.points}
                </Text>
                <Text style={[styles.pointsLabel, { color: theme.textSecondary }]}>
                  points
                </Text>
              </View>
            </View>
          ))
        )}

        {/* Motivational Text */}
        {leaderboard.length > 0 && (
          <View style={styles.motivationContainer}>
            <Text style={[styles.motivationText, { color: theme.textSecondary }]}>
              🏆 Complete tasks daily to climb the leaderboard!
            </Text>
            <Text style={[styles.motivationSubtext, { color: theme.textSecondary }]}>
              Top performers win weekly prizes 💰
            </Text>
          </View>
        )}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  header: {
    padding: 24,
    paddingTop: 16,
    borderBottomLeftRadius: 24,
    borderBottomRightRadius: 24,
    elevation: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  headerTop: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 12,
    marginBottom: 8,
  },
  headerTitle: {
    fontSize: 28,
    fontWeight: 'bold',
  },
  headerSubtitle: {
    fontSize: 14,
    textAlign: 'center',
  },
  toggleContainer: {
    flexDirection: 'row',
    padding: 20,
    gap: 12,
  },
  toggleButton: {
    flex: 1,
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderRadius: 12,
    borderWidth: 1,
    alignItems: 'center',
  },
  toggleText: {
    fontSize: 14,
    fontWeight: '600',
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    padding: 20,
    paddingTop: 0,
  },
  userCard: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    borderRadius: 16,
    marginBottom: 12,
    borderWidth: 1,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
  },
  firstPlace: {
    borderWidth: 2,
    borderColor: '#FFD700',
  },
  secondPlace: {
    borderWidth: 2,
    borderColor: '#C0C0C0',
  },
  thirdPlace: {
    borderWidth: 2,
    borderColor: '#CD7F32',
  },
  rankBadge: {
    alignItems: 'center',
    marginRight: 12,
    width: 40,
  },
  rankText: {
    fontSize: 12,
    fontWeight: 'bold',
    marginTop: 4,
  },
  profileImageContainer: {
    marginRight: 12,
  },
  profileImage: {
    width: 48,
    height: 48,
    borderRadius: 24,
  },
  profileImagePlaceholder: {
    width: 48,
    height: 48,
    borderRadius: 24,
    alignItems: 'center',
    justifyContent: 'center',
  },
  userInfo: {
    flex: 1,
  },
  userName: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 4,
  },
  userStats: {
    flexDirection: 'row',
    gap: 12,
  },
  statItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  statText: {
    fontSize: 12,
  },
  pointsContainer: {
    alignItems: 'flex-end',
  },
  pointsValue: {
    fontSize: 20,
    fontWeight: 'bold',
  },
  pointsLabel: {
    fontSize: 12,
  },
  errorContainer: {
    alignItems: 'center',
    padding: 40,
  },
  errorText: {
    fontSize: 16,
    marginTop: 16,
    marginBottom: 16,
  },
  retryButton: {
    paddingVertical: 12,
    paddingHorizontal: 24,
    borderRadius: 8,
  },
  retryText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
  },
  emptyContainer: {
    alignItems: 'center',
    padding: 40,
  },
  emptyText: {
    fontSize: 18,
    fontWeight: '600',
    marginTop: 16,
  },
  emptySubtext: {
    fontSize: 14,
    marginTop: 8,
  },
  motivationContainer: {
    alignItems: 'center',
    marginTop: 24,
    padding: 20,
  },
  motivationText: {
    fontSize: 14,
    textAlign: 'center',
    fontWeight: '600',
  },
  motivationSubtext: {
    fontSize: 12,
    textAlign: 'center',
    marginTop: 4,
  },
});
