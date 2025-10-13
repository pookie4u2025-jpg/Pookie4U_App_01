import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  Clipboard,
  RefreshControl,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useAuthStore } from '../stores/useAuthStore';
import { useTheme } from '../contexts/ThemeContext';

// Define message categories
const messageCategories = [
  { id: 'good_morning', title: 'Good Morning', icon: 'sunny', color: '#FFD700' },
  { id: 'good_night', title: 'Good Night', icon: 'moon', color: '#6B73FF' },
  { id: 'love_confession', title: 'Love Confession', icon: 'heart', color: '#FF69B4' },
  { id: 'apology', title: 'Apology', icon: 'flower', color: '#FF6B6B' },
  { id: 'funny_hinglish', title: 'Funny Hinglish', icon: 'happy', color: '#4ECDC4' },
];

interface DailyMessage {
  id: string;
  text: string;
  category: string;
  relationship_mode: string;
  generated_at: string;
  metadata: {
    source: string;
    rotation_seed: number;
    day_of_month: number;
    category_index: number;
    message_index: number;
  };
}

export default function MessagesContent() {
  const { token, user } = useAuthStore();
  const { theme } = useTheme();
  
  const [dailyMessages, setDailyMessages] = useState<DailyMessage[]>([]);
  const [selectedCategory, setSelectedCategory] = useState('good_morning');
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (token && user && user.relationship_mode) {
      fetchDailyMessages();
    }
  }, [token, user]);

  const fetchDailyMessages = async () => {
    if (!user?.relationship_mode) {
      setError('No relationship mode set. Please update your profile.');
      return;
    }

    setLoading(true);
    setError(null);
    
    try {
      console.log('Fetching messages for relationship mode:', user.relationship_mode);
      
      const response = await fetch(
        `${process.env.EXPO_PUBLIC_BACKEND_URL}/api/messages/daily/${user.relationship_mode}`,
        {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );

      const data = await response.json();
      
      if (response.ok && data.messages) {
        console.log('Successfully fetched daily messages:', data.messages.length);
        setDailyMessages(data.messages);
      } else {
        const errorMsg = data.detail || 'Failed to fetch messages';
        console.error('API Error:', errorMsg);
        setError(errorMsg);
      }
    } catch (error) {
      console.error('Error fetching daily messages:', error);
      setError('Network error. Please check your connection.');
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await fetchDailyMessages();
    setRefreshing(false);
  };

  const copyToClipboard = (message: string) => {
    Clipboard.setString(message);
    Alert.alert('Copied! 💕', 'Message copied to clipboard. Send it to your partner!', [
      { text: 'OK', style: 'default' }
    ]);
  };

  const getCurrentCategoryMessages = (): DailyMessage[] => {
    return dailyMessages.filter(msg => msg.category === selectedCategory);
  };

  const getRelationshipModeTitle = (): string => {
    switch (user?.relationship_mode) {
      case 'SAME_HOME':
        return 'Same Home';
      case 'DAILY_IRL':
        return 'Daily Meetup';
      case 'LONG_DISTANCE':
        return 'Long Distance';
      default:
        return 'Unknown';
    }
  };

  const currentCategoryData = messageCategories.find(cat => cat.id === selectedCategory);

  return (
    <View style={[styles.container, { backgroundColor: theme.background }]}>
      <ScrollView
        style={styles.scrollView}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
      >
        {/* Header */}
        <View style={[styles.header, { backgroundColor: theme.surface }]}>
          <Text style={[styles.title, { color: theme.text }]}>Love Messages 💌</Text>
          <Text style={[styles.subtitle, { color: theme.textSecondary }]}>
            Personalized messages for {getRelationshipModeTitle()} couples
          </Text>
        </View>

        {/* Loading State */}
        {loading && (
          <View style={[styles.loadingContainer, { backgroundColor: theme.surface }]}>
            <Text style={[styles.loadingText, { color: theme.text }]}>Loading your messages...</Text>
          </View>
        )}

        {/* Error State */}
        {error && (
          <View style={[styles.errorContainer, { backgroundColor: theme.surface }]}>
            <Ionicons name="alert-circle" size={24} color="#FF6B6B" />
            <Text style={[styles.errorText, { color: theme.text }]}>{error}</Text>
            <TouchableOpacity
              style={[styles.retryButton, { backgroundColor: theme.primary }]}
              onPress={fetchDailyMessages}
            >
              <Text style={styles.retryButtonText}>Retry</Text>
            </TouchableOpacity>
          </View>
        )}

        {/* Daily Messages Info */}
        {dailyMessages.length > 0 && (
          <View style={[styles.dailyMessagesInfo, { backgroundColor: theme.surface }]}>
            <View style={styles.dailyMessagesHeader}>
              <Ionicons name="star" size={20} color="#FFD700" />
              <Text style={[styles.dailyMessagesTitle, { color: theme.text }]}>
                Today's {getRelationshipModeTitle()} Messages
              </Text>
            </View>
            <Text style={[styles.dailyMessagesSubtitle, { color: theme.textSecondary }]}>
              3 personalized messages that rotate monthly • {new Date().toLocaleDateString()}
            </Text>
          </View>
        )}

        {/* Categories */}
        <View style={[styles.categoriesContainer, { backgroundColor: theme.surface }]}>
          <Text style={[styles.categoriesTitle, { color: theme.text }]}>Choose a Category</Text>
          <ScrollView 
            horizontal 
            showsHorizontalScrollIndicator={false}
            style={styles.categoriesScroll}
          >
            {messageCategories.map((category) => (
              <TouchableOpacity
                key={category.id}
                style={[
                  styles.categoryButton,
                  { backgroundColor: theme.background, borderColor: category.color },
                  selectedCategory === category.id && { 
                    backgroundColor: category.color,
                    borderColor: category.color 
                  }
                ]}
                onPress={() => setSelectedCategory(category.id)}
              >
                <Ionicons 
                  name={category.icon as any} 
                  size={20} 
                  color={selectedCategory === category.id ? '#fff' : category.color} 
                />
                <Text style={[
                  styles.categoryButtonText,
                  { color: selectedCategory === category.id ? '#fff' : theme.text }
                ]}>
                  {category.title}
                </Text>
              </TouchableOpacity>
            ))}
          </ScrollView>
        </View>

        {/* Current Category Messages */}
        {!loading && !error && dailyMessages.length > 0 && (
          <View style={styles.section}>
            <Text style={[styles.sectionTitle, { color: theme.text }]}>
              {currentCategoryData?.title} Messages
            </Text>
            <Text style={[styles.sectionSubtitle, { color: theme.textSecondary }]}>
              3 daily messages to choose from • Tap any message to copy
            </Text>
            
            {getCurrentCategoryMessages().length > 0 ? (
              getCurrentCategoryMessages().map((message, index) => (
                <TouchableOpacity
                  key={message.id}
                  style={[styles.messageCard, { 
                    backgroundColor: theme.surface,
                    borderColor: currentCategoryData?.color || theme.border,
                    borderWidth: 1,
                    borderLeftWidth: 4,
                    borderLeftColor: currentCategoryData?.color || theme.primary
                  }]}
                  onPress={() => copyToClipboard(message.text)}
                >
                  <View style={styles.messageContent}>
                    <View style={styles.messageHeader}>
                      <View style={styles.categoryIcon}>
                        <Ionicons 
                          name={currentCategoryData?.icon as any} 
                          size={20} 
                          color={currentCategoryData?.color} 
                        />
                      </View>
                      <Text style={[styles.messageNumber, { color: currentCategoryData?.color }]}>
                        Option {index + 1}
                      </Text>
                    </View>
                    <Text style={[styles.messageText, { color: theme.text }]}>
                      "{message.text}"
                    </Text>
                    <View style={styles.messageMetadata}>
                      <Text style={[styles.metadataText, { color: theme.textSecondary }]}>
                        {getRelationshipModeTitle()} Mode • Message {message.metadata.message_index}
                      </Text>
                    </View>
                  </View>
                  <View style={styles.messageActions}>
                    <Ionicons name="copy-outline" size={18} color={theme.primary} />
                  </View>
                </TouchableOpacity>
              ))
            ) : (
              <View style={styles.emptyMessageCard}>
                <Text style={[styles.emptyMessageText, { color: theme.textSecondary }]}>
                  No messages available for {currentCategoryData?.title}
                </Text>
                <Text style={[styles.emptyMessageHint, { color: theme.border }]}>
                  Try another category or refresh
                </Text>
              </View>
            )}
          </View>
        )}

        {/* All Daily Messages Preview */}
        {!loading && !error && dailyMessages.length > 0 && (
          <View style={[styles.allMessagesSection, { backgroundColor: theme.surface }]}>
            <Text style={[styles.sectionTitle, { color: theme.text }]}>All Today's Messages</Text>
            <Text style={[styles.sectionSubtitle, { color: theme.textSecondary }]}>
              Preview of all 3 daily messages for {getRelationshipModeTitle()} mode
            </Text>
            {dailyMessages.map((message, index) => {
              const categoryData = messageCategories.find(cat => cat.id === message.category);
              return (
                <TouchableOpacity
                  key={message.id}
                  style={[styles.previewMessageCard, { backgroundColor: theme.background }]}
                  onPress={() => copyToClipboard(message.text)}
                >
                  <View style={styles.previewMessageHeader}>
                    <Ionicons 
                      name={categoryData?.icon as any} 
                      size={16} 
                      color={categoryData?.color} 
                    />
                    <Text style={[styles.previewCategoryTitle, { color: categoryData?.color }]}>
                      {categoryData?.title}
                    </Text>
                  </View>
                  <Text style={[styles.previewMessageText, { color: theme.text }]}>
                    "{message.text}"
                  </Text>
                </TouchableOpacity>
              );
            })}
          </View>
        )}

        {/* Tips */}
        <View style={[styles.tipsSection, { backgroundColor: theme.surface }]}>
          <Text style={[styles.sectionTitle, { color: theme.text }]}>💡 Message Tips</Text>
          <View style={styles.tipsContent}>
            <Text style={[styles.tipsText, { color: theme.textSecondary }]}>
              • Your messages are personalized for {getRelationshipModeTitle()} relationships{'\n'}
              • Messages rotate monthly - same messages daily within each month{'\n'}
              • Send messages at the right time of day for maximum impact{'\n'}
              • Add your partner's name to make messages more personal{'\n'}
              • Mix different categories throughout the day{'\n'}
              • Copy and send via your favorite messaging app
            </Text>
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
  header: {
    padding: 20,
    alignItems: 'center',
    marginBottom: 10,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 5,
  },
  subtitle: {
    fontSize: 16,
    textAlign: 'center',
  },
  
  // Loading and Error States
  loadingContainer: {
    padding: 20,
    alignItems: 'center',
    marginHorizontal: 20,
    marginBottom: 20,
    borderRadius: 12,
  },
  loadingText: {
    fontSize: 16,
    marginTop: 10,
  },
  errorContainer: {
    padding: 20,
    alignItems: 'center',
    marginHorizontal: 20,
    marginBottom: 20,
    borderRadius: 12,
  },
  errorText: {
    fontSize: 16,
    marginTop: 10,
    textAlign: 'center',
  },
  retryButton: {
    paddingVertical: 10,
    paddingHorizontal: 20,
    borderRadius: 8,
    marginTop: 10,
  },
  retryButtonText: {
    color: '#fff',
    fontWeight: 'bold',
  },
  
  // Daily Messages Info
  dailyMessagesInfo: {
    marginHorizontal: 20,
    borderRadius: 12,
    padding: 16,
    marginBottom: 20,
  },
  dailyMessagesHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  dailyMessagesTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginLeft: 8,
  },
  dailyMessagesSubtitle: {
    fontSize: 14,
    lineHeight: 20,
  },
  
  // Categories
  categoriesContainer: {
    paddingVertical: 15,
    paddingHorizontal: 20,
    marginBottom: 10,
  },
  categoriesTitle: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 10,
  },
  categoriesScroll: {
    marginHorizontal: -20,
    paddingHorizontal: 20,
  },
  categoryButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 10,
    paddingHorizontal: 16,
    marginRight: 10,
    borderRadius: 20,
    borderWidth: 1,
  },
  categoryButtonText: {
    marginLeft: 6,
    fontSize: 14,
    fontWeight: '500',
  },
  
  // Section
  section: {
    paddingHorizontal: 20,
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
  
  // Message Card
  messageCard: {
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    flexDirection: 'row',
    alignItems: 'flex-start',
  },
  messageContent: {
    flex: 1,
  },
  messageHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  messageNumber: {
    fontSize: 14,
    fontWeight: '600',
    marginLeft: 8,
  },
  categoryIcon: {
    marginBottom: 8,
  },
  messageText: {
    fontSize: 16,
    lineHeight: 24,
    fontStyle: 'italic',
    marginBottom: 8,
  },
  messageMetadata: {
    marginTop: 4,
  },
  metadataText: {
    fontSize: 12,
  },
  messageActions: {
    paddingLeft: 12,
    justifyContent: 'center',
  },
  
  // Empty States
  emptyMessageCard: {
    padding: 20,
    alignItems: 'center',
  },
  emptyMessageText: {
    fontSize: 16,
    textAlign: 'center',
    marginBottom: 4,
  },
  emptyMessageHint: {
    fontSize: 14,
    textAlign: 'center',
  },
  
  // All Messages Section
  allMessagesSection: {
    margin: 20,
    borderRadius: 12,
    padding: 16,
  },
  previewMessageCard: {
    borderRadius: 8,
    padding: 12,
    marginBottom: 8,
  },
  previewMessageHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 6,
  },
  previewCategoryTitle: {
    fontSize: 12,
    fontWeight: '600',
    marginLeft: 6,
  },
  previewMessageText: {
    fontSize: 14,
    lineHeight: 20,
    fontStyle: 'italic',
  },
  
  // Tips Section
  tipsSection: {
    margin: 20,
    borderRadius: 12,
    padding: 16,
  },
  tipsContent: {
    marginTop: 8,
  },
  tipsText: {
    fontSize: 14,
    lineHeight: 22,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  dailyMessageHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
    gap: 8,
  },
  dailyMessageTitle: {
    fontSize: 16,
    fontWeight: '600',
  },
  dailyMessageContent: {
    borderRadius: 8,
    padding: 12,
  },
  dailyMessageText: {
    fontSize: 16,
    lineHeight: 24,
    fontStyle: 'italic',
    marginBottom: 8,
  },
  dailyMessageFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  dailyMessageNote: {
    fontSize: 12,
  },
  emptyState: {
    alignItems: 'center',
    paddingVertical: 40,
  },
  emptyTitle: {
    fontSize: 16,
    marginTop: 10,
  },
  emptySubtitle: {
    fontSize: 14,
    marginTop: 5,
  },
});