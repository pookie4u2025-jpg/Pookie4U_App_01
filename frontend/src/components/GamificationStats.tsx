import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ActivityIndicator,
} from 'react-native';
import Animated, { FadeInDown, useSharedValue, useAnimatedStyle, withSpring } from 'react-native-reanimated';
import { Ionicons } from '@expo/vector-icons';
import { useAuthStore } from '../stores/useAuthStore';
import { useTheme } from '../contexts/ThemeContext';

interface GamificationData {
  points: {
    total: number;
    available: number;
    spent: number;
  };
  level: {
    current: number;
    name: string;
    unlock: string;
    next_level: number | null;
    next_level_name: string | null;
    next_level_unlock: string | null;
    points_to_next: number;
    progress_percentage: number;
  };
  streak: {
    current: number;
    longest: number;
    daily_tasks_today: number;
    tasks_total: number;
  };
  prize_eligibility: {
    weekly_draw: boolean;
    monthly_draw: boolean;
    days_to_weekly: number;
    days_to_monthly: number;
  };
}

export default function GamificationStats() {
  const { token } = useAuthStore();
  const { theme } = useTheme();
  const [data, setData] = useState<GamificationData | null>(null);
  const [loading, setLoading] = useState(true);
  
  // Animated values
  const progressWidth = useSharedValue(0);

  useEffect(() => {
    fetchGamificationStats();
  }, [token]);

  useEffect(() => {
    if (data) {
      progressWidth.value = withSpring(data.level.progress_percentage, {
        damping: 15,
        stiffness: 100,
      });
    }
  }, [data]);

  const fetchGamificationStats = async () => {
    if (!token) return;
    
    try {
      const response = await fetch(
        `${process.env.EXPO_PUBLIC_BACKEND_URL}/api/gamification/stats`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        }
      );
      
      const result = await response.json();
      if (response.ok && result.success) {
        setData(result);
      }
    } catch (error) {
      console.error('Error fetching gamification stats:', error);
    } finally {
      setLoading(false);
    }
  };

  const animatedProgressStyle = useAnimatedStyle(() => {
    return {
      width: `${progressWidth.value}%`,
    };
  });

  if (loading) {
    return (
      <View style={[styles.loadingContainer, { backgroundColor: theme.surface }]}>
        <ActivityIndicator size="large" color={theme.primary} />
      </View>
    );
  }

  if (!data) {
    return null;
  }

  const { points, level, streak, prize_eligibility } = data;

  return (
    <View style={styles.container}>
      {/* Streak Display - Prominent */}
      <Animated.View 
        entering={FadeInDown.duration(400)}
        style={[styles.streakCard, { backgroundColor: theme.surface }]}
      >
        <View style={styles.streakContent}>
          <View style={styles.streakLeft}>
            <Text style={[styles.streakEmoji, { fontSize: 48 }]}>🔥</Text>
            <View style={styles.streakInfo}>
              <Text style={[styles.streakNumber, { color: theme.text }]}>
                {streak.current} Days
              </Text>
              <Text style={[styles.streakLabel, { color: theme.textSecondary }]}>
                Current Streak
              </Text>
              <Text style={[styles.streakSubtext, { color: theme.border }]}>
                {streak.daily_tasks_today}/3 tasks today
              </Text>
            </View>
          </View>
          
          <View style={styles.streakRight}>
            <View style={[styles.streakBadge, { backgroundColor: theme.primary + '20', borderColor: theme.primary }]}>
              <Text style={[styles.streakBadgeText, { color: theme.primary }]}>
                Longest: {streak.longest}
              </Text>
            </View>
            
            {/* Prize Eligibility Indicators */}
            {prize_eligibility.weekly_draw && (
              <View style={[styles.eligibilityBadge, { backgroundColor: '#FFD700' + '20' }]}>
                <Ionicons name="trophy" size={12} color="#FFD700" />
                <Text style={styles.eligibilityText}>Weekly Draw</Text>
              </View>
            )}
            {prize_eligibility.monthly_draw && (
              <View style={[styles.eligibilityBadge, { backgroundColor: '#FF4500' + '20' }]}>
                <Ionicons name="airplane" size={12} color="#FF4500" />
                <Text style={styles.eligibilityText}>Monthly Draw</Text>
              </View>
            )}
            
            {/* Days to eligibility */}
            {!prize_eligibility.weekly_draw && prize_eligibility.days_to_weekly > 0 && (
              <Text style={[styles.daysToEligibility, { color: theme.textSecondary }]}>
                {prize_eligibility.days_to_weekly} days to weekly draw
              </Text>
            )}
          </View>
        </View>
      </Animated.View>

      {/* Level & Points Display */}
      <View style={styles.statsRow}>
        <Animated.View 
          entering={FadeInDown.delay(100).duration(400)}
          style={[styles.statCard, { backgroundColor: theme.surface }]}
        >
          <Ionicons name="trophy" size={28} color={theme.primary} />
          <Text style={[styles.statNumber, { color: theme.text }]}>
            Level {level.current}
          </Text>
          <Text style={[styles.statLabel, { color: theme.textSecondary }]} numberOfLines={1}>
            {level.name}
          </Text>
        </Animated.View>

        <Animated.View 
          entering={FadeInDown.delay(200).duration(400)}
          style={[styles.statCard, { backgroundColor: theme.surface }]}
        >
          <Ionicons name="star" size={28} color="#FFD700" />
          <Text style={[styles.statNumber, { color: theme.text }]}>
            {points.available.toLocaleString()}
          </Text>
          <Text style={[styles.statLabel, { color: theme.textSecondary }]}>
            Available Points
          </Text>
        </Animated.View>
      </View>

      {/* Level Progress Bar */}
      <Animated.View 
        entering={FadeInDown.delay(300).duration(400)}
        style={[styles.progressCard, { backgroundColor: theme.surface }]}
      >
        <View style={styles.progressHeader}>
          <Text style={[styles.progressTitle, { color: theme.text }]}>
            {level.next_level ? `Level ${level.next_level}` : 'Max Level'}
          </Text>
          <Text style={[styles.progressPoints, { color: theme.primary }]}>
            {level.points_to_next > 0 
              ? `${level.points_to_next.toLocaleString()} points to go`
              : 'Max Level Reached!'
            }
          </Text>
        </View>
        
        <View style={[styles.progressBarBg, { backgroundColor: theme.border + '30' }]}>
          <Animated.View 
            style={[
              styles.progressBarFill, 
              { backgroundColor: theme.primary },
              animatedProgressStyle
            ]} 
          />
        </View>
        
        {level.next_level_unlock && (
          <View style={styles.unlockPreview}>
            <Ionicons name="lock-open" size={16} color={theme.textSecondary} />
            <Text style={[styles.unlockText, { color: theme.textSecondary }]}>
              Next: {level.next_level_unlock}
            </Text>
          </View>
        )}
      </Animated.View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    padding: 16,
    gap: 12,
  },
  loadingContainer: {
    padding: 40,
    borderRadius: 16,
    margin: 16,
    alignItems: 'center',
    justifyContent: 'center',
  },
  streakCard: {
    borderRadius: 16,
    padding: 20,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  streakContent: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  streakLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 16,
  },
  streakEmoji: {
    fontSize: 48,
  },
  streakInfo: {
    gap: 4,
  },
  streakNumber: {
    fontSize: 32,
    fontWeight: 'bold',
  },
  streakLabel: {
    fontSize: 14,
  },
  streakSubtext: {
    fontSize: 12,
    marginTop: 4,
  },
  streakRight: {
    alignItems: 'flex-end',
    gap: 8,
  },
  streakBadge: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 12,
    borderWidth: 1,
  },
  streakBadgeText: {
    fontSize: 12,
    fontWeight: '600',
  },
  eligibilityBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 8,
  },
  eligibilityText: {
    fontSize: 10,
    fontWeight: '600',
    color: '#333',
  },
  daysToEligibility: {
    fontSize: 11,
    fontStyle: 'italic',
  },
  statsRow: {
    flexDirection: 'row',
    gap: 12,
  },
  statCard: {
    flex: 1,
    borderRadius: 16,
    padding: 16,
    alignItems: 'center',
    gap: 8,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  statNumber: {
    fontSize: 24,
    fontWeight: 'bold',
  },
  statLabel: {
    fontSize: 12,
    textAlign: 'center',
  },
  progressCard: {
    borderRadius: 16,
    padding: 16,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  progressHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  progressTitle: {
    fontSize: 16,
    fontWeight: '600',
  },
  progressPoints: {
    fontSize: 13,
    fontWeight: '500',
  },
  progressBarBg: {
    height: 8,
    borderRadius: 4,
    overflow: 'hidden',
  },
  progressBarFill: {
    height: '100%',
    borderRadius: 4,
  },
  unlockPreview: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    marginTop: 10,
  },
  unlockText: {
    fontSize: 12,
    fontStyle: 'italic',
  },
});
