import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  ScrollView,
  RefreshControl,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
  Alert,
  Clipboard
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../contexts/ThemeContext';
import { useAuthStore } from '../stores/useAuthStore';

interface RewardItem {
  _id: string;
  reward_type: string;
  coupon_code: string;
  milestone_number: number;
  points_at_redemption: number;
  status: string;
  created_at: string;
}

export default function RewardHistoryContent() {
  const { theme } = useTheme();
  const { token } = useAuthStore();
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [rewards, setRewards] = useState<RewardItem[]>([]);
  const [filteredRewards, setFilteredRewards] = useState<RewardItem[]>([]);
  const [totalRedemptions, setTotalRedemptions] = useState(0);
  const [currentPoints, setCurrentPoints] = useState(0);
  const [cyclesCompleted, setCyclesCompleted] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [filterStatus, setFilterStatus] = useState<string>('all');

  useEffect(() => {
    fetchRewardHistory();
  }, []);

  useEffect(() => {
    applyFilters();
  }, [filterStatus, rewards]);

  const fetchRewardHistory = async () => {
    try {
      setError(null);
      const response = await fetch(
        `${process.env.EXPO_PUBLIC_BACKEND_URL}/api/rewards/history`,
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );

      if (response.ok) {
        const data = await response.json();
        setRewards(data.rewards || []);
        setTotalRedemptions(data.total_redemptions || 0);
        setCurrentPoints(data.current_points || 0);
        setCyclesCompleted(data.cycles_completed || 0);
      } else {
        setError('Failed to load reward history');
      }
    } catch (err) {
      console.error('Error fetching reward history:', err);
      setError('Network error');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const applyFilters = () => {
    if (filterStatus === 'all') {
      setFilteredRewards(rewards);
    } else {
      setFilteredRewards(rewards.filter(r => r.status === filterStatus));
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    fetchRewardHistory();
  };

  const handleCopyCoupon = async (couponCode: string) => {
    await Clipboard.setString(couponCode);
    Alert.alert('Copied!', 'Coupon code copied to clipboard 📋');
  };

  const exportData = () => {
    if (rewards.length === 0) {
      Alert.alert('No Data', 'No rewards to export');
      return;
    }

    // Format data as CSV
    const csvHeader = 'Milestone,Coupon Code,Points,Status,Date\n';
    const csvRows = rewards.map(r => 
      `${r.milestone_number},${r.coupon_code},${r.points_at_redemption},${r.status},${new Date(r.created_at).toLocaleDateString()}`
    ).join('\n');
    
    const csvContent = csvHeader + csvRows;
    
    Alert.alert(
      'Export Data',
      `Total Rewards: ${rewards.length}\n\nCopy to clipboard?`,
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Copy',
          onPress: async () => {
            await Clipboard.setString(csvContent);
            Alert.alert('Exported!', 'Reward data copied to clipboard');
          }
        }
      ]
    );
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'approved': return '#4CAF50';
      case 'pending': return '#FF9800';
      case 'rejected': return '#F44336';
      default: return theme.textSecondary;
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'approved': return 'checkmark-circle';
      case 'pending': return 'time';
      case 'rejected': return 'close-circle';
      default: return 'help-circle';
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-IN', { 
      day: '2-digit', 
      month: 'short', 
      year: 'numeric' 
    });
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
          <Ionicons name="gift" size={32} color="#FF1493" />
          <Text style={[styles.headerTitle, { color: theme.text }]}>
            Reward History
          </Text>
        </View>
        
        {/* Stats */}
        <View style={styles.statsContainer}>
          <View style={styles.statBox}>
            <Text style={[styles.statValue, { color: '#FFD700' }]}>{currentPoints}</Text>
            <Text style={[styles.statLabel, { color: theme.textSecondary }]}>Current Points</Text>
          </View>
          <View style={[styles.statDivider, { backgroundColor: theme.border }]} />
          <View style={styles.statBox}>
            <Text style={[styles.statValue, { color: '#FF1493' }]}>{totalRedemptions}</Text>
            <Text style={[styles.statLabel, { color: theme.textSecondary }]}>Total Coupons</Text>
          </View>
          <View style={[styles.statDivider, { backgroundColor: theme.border }]} />
          <View style={styles.statBox}>
            <Text style={[styles.statValue, { color: '#4CAF50' }]}>{cyclesCompleted}</Text>
            <Text style={[styles.statLabel, { color: theme.textSecondary }]}>Milestones</Text>
          </View>
        </View>
      </View>

      {/* Filter Chips */}
      <View style={styles.filterContainer}>
        <ScrollView horizontal showsHorizontalScrollIndicator={false}>
          {['all', 'approved', 'pending'].map((status) => (
            <TouchableOpacity
              key={status}
              style={[
                styles.filterChip,
                { backgroundColor: theme.surface, borderColor: theme.border },
                filterStatus === status && { backgroundColor: theme.primary, borderColor: theme.primary }
              ]}
              onPress={() => setFilterStatus(status)}
            >
              <Text style={[
                styles.filterText,
                { color: theme.textSecondary },
                filterStatus === status && { color: '#fff', fontWeight: 'bold' }
              ]}>
                {status.charAt(0).toUpperCase() + status.slice(1)}
              </Text>
            </TouchableOpacity>
          ))}
        </ScrollView>

        <TouchableOpacity 
          style={[styles.exportButton, { backgroundColor: theme.primary }]}
          onPress={exportData}
        >
          <Ionicons name="download" size={16} color="#fff" />
        </TouchableOpacity>
      </View>

      {/* Rewards List */}
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
            <TouchableOpacity style={[styles.retryButton, { backgroundColor: theme.primary }]} onPress={fetchRewardHistory}>
              <Text style={styles.retryText}>Retry</Text>
            </TouchableOpacity>
          </View>
        ) : filteredRewards.length === 0 ? (
          <View style={styles.emptyContainer}>
            <Ionicons name="gift-outline" size={64} color={theme.textSecondary} />
            <Text style={[styles.emptyText, { color: theme.textSecondary }]}>
              {filterStatus === 'all' ? 'No rewards yet' : `No ${filterStatus} rewards`}
            </Text>
            <Text style={[styles.emptySubtext, { color: theme.textSecondary }]}>
              Earn 1000 points to get your first gift coupon!
            </Text>
          </View>
        ) : (
          filteredRewards.map((reward) => (
            <View
              key={reward._id}
              style={[
                styles.rewardCard,
                { backgroundColor: theme.surface, borderColor: theme.border }
              ]}
            >
              {/* Milestone Badge */}
              <View style={styles.cardHeader}>
                <View style={[styles.milestoneBadge, { backgroundColor: theme.primary + '20' }]}>
                  <Ionicons name="trophy" size={20} color={theme.primary} />
                  <Text style={[styles.milestoneText, { color: theme.primary }]}>
                    Milestone #{reward.milestone_number}
                  </Text>
                </View>
                <View style={[styles.statusBadge, { backgroundColor: getStatusColor(reward.status) + '20' }]}>
                  <Ionicons 
                    name={getStatusIcon(reward.status) as any} 
                    size={16} 
                    color={getStatusColor(reward.status)} 
                  />
                  <Text style={[styles.statusText, { color: getStatusColor(reward.status) }]}>
                    {reward.status.charAt(0).toUpperCase() + reward.status.slice(1)}
                  </Text>
                </View>
              </View>

              {/* Coupon Code */}
              <View style={[styles.couponContainer, { backgroundColor: theme.background }]}>
                <Text style={[styles.couponLabel, { color: theme.textSecondary }]}>Coupon Code:</Text>
                <View style={styles.couponCodeRow}>
                  <Text style={[styles.couponCode, { color: theme.text }]}>
                    {reward.coupon_code}
                  </Text>
                  <TouchableOpacity 
                    style={styles.copyIcon}
                    onPress={() => handleCopyCoupon(reward.coupon_code)}
                  >
                    <Ionicons name="copy" size={20} color={theme.primary} />
                  </TouchableOpacity>
                </View>
              </View>

              {/* Details */}
              <View style={styles.detailsContainer}>
                <View style={styles.detailRow}>
                  <Ionicons name="calendar" size={16} color={theme.textSecondary} />
                  <Text style={[styles.detailText, { color: theme.textSecondary }]}>
                    {formatDate(reward.created_at)}
                  </Text>
                </View>
                <View style={styles.detailRow}>
                  <Ionicons name="trophy" size={16} color="#FFD700" />
                  <Text style={[styles.detailText, { color: theme.textSecondary }]}>
                    {reward.points_at_redemption} points
                  </Text>
                </View>
              </View>
            </View>
          ))
        )}

        {filteredRewards.length > 0 && (
          <View style={styles.bottomInfo}>
            <Text style={[styles.bottomText, { color: theme.textSecondary }]}>
              🎁 Keep earning points for more coupons!
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
    marginBottom: 20,
  },
  headerTitle: {
    fontSize: 28,
    fontWeight: 'bold',
  },
  statsContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-around',
  },
  statBox: {
    alignItems: 'center',
    flex: 1,
  },
  statValue: {
    fontSize: 24,
    fontWeight: 'bold',
  },
  statLabel: {
    fontSize: 12,
    marginTop: 4,
  },
  statDivider: {
    width: 1,
    height: 40,
  },
  filterContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 16,
    paddingLeft: 20,
    gap: 12,
  },
  filterChip: {
    paddingVertical: 8,
    paddingHorizontal: 16,
    borderRadius: 20,
    borderWidth: 1,
    marginRight: 8,
  },
  filterText: {
    fontSize: 14,
    fontWeight: '600',
  },
  exportButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 20,
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    padding: 20,
    paddingTop: 0,
  },
  rewardCard: {
    borderRadius: 16,
    padding: 16,
    marginBottom: 16,
    borderWidth: 1,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  milestoneBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    paddingVertical: 6,
    paddingHorizontal: 12,
    borderRadius: 12,
  },
  milestoneText: {
    fontSize: 12,
    fontWeight: '600',
  },
  statusBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    paddingVertical: 6,
    paddingHorizontal: 12,
    borderRadius: 12,
  },
  statusText: {
    fontSize: 12,
    fontWeight: '600',
  },
  couponContainer: {
    padding: 12,
    borderRadius: 12,
    marginBottom: 12,
  },
  couponLabel: {
    fontSize: 12,
    marginBottom: 4,
  },
  couponCodeRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  couponCode: {
    fontSize: 16,
    fontWeight: 'bold',
    fontFamily: 'monospace',
    flex: 1,
  },
  copyIcon: {
    padding: 4,
  },
  detailsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  detailRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
  },
  detailText: {
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
    textAlign: 'center',
  },
  bottomInfo: {
    alignItems: 'center',
    marginTop: 24,
    padding: 20,
  },
  bottomText: {
    fontSize: 14,
    textAlign: 'center',
  },
});
