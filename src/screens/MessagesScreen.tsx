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
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useAuthStore } from '../stores/useAuthStore';

const BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL || '';

const MESSAGE_CATEGORIES = [
  { key: 'good_morning', label: 'Good Morning', icon: 'sunny' },
  { key: 'good_night', label: 'Good Night', icon: 'moon' },
  { key: 'love_confession', label: 'Love Confession', icon: 'heart' },
  { key: 'apology', label: 'Apology', icon: 'sad' },
  { key: 'funny_hinglish', label: 'Funny Hinglish', icon: 'happy' },
];

export default function MessagesScreen() {
  const { token } = useAuthStore();
  const [messages, setMessages] = useState<{[key: string]: string[]}>({});
  const [selectedCategory, setSelectedCategory] = useState('good_morning');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchMessages(selectedCategory);
  }, [selectedCategory]);

  const fetchMessages = async (category: string) => {
    setLoading(true);
    try {
      const response = await fetch(`${BACKEND_URL}/api/messages/${category}`);
      const data = await response.json();
      setMessages(prev => ({
        ...prev,
        [category]: data.messages || []
      }));
    } catch (error) {
      console.error('Failed to fetch messages:', error);
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = async () => {
    await fetchMessages(selectedCategory);
  };

  const copyToClipboard = async (message: string) => {
    try {
      await Clipboard.setString(message);
      Alert.alert('Copied!', 'Message copied to clipboard. You can now paste it in WhatsApp or any messaging app!');
    } catch (error) {
      Alert.alert('Error', 'Failed to copy message');
    }
  };

  const currentMessages = messages[selectedCategory] || [];

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView
        style={styles.scrollView}
        refreshControl={
          <RefreshControl refreshing={loading} onRefresh={onRefresh} />
        }
      >
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.headerTitle}>Romantic Messages 💕</Text>
          <Text style={styles.headerSubtitle}>
            Copy these pre-written messages to send to your partner
          </Text>
        </View>

        {/* Category Tabs */}
        <ScrollView 
          horizontal 
          showsHorizontalScrollIndicator={false}
          style={styles.categoriesContainer}
          contentContainerStyle={styles.categoriesContent}
        >
          {MESSAGE_CATEGORIES.map((category) => (
            <TouchableOpacity
              key={category.key}
              style={[
                styles.categoryTab,
                selectedCategory === category.key && styles.categoryTabActive
              ]}
              onPress={() => setSelectedCategory(category.key)}
            >
              <Ionicons 
                name={category.icon} 
                size={20} 
                color={selectedCategory === category.key ? '#fff' : '#FF69B4'} 
              />
              <Text style={[
                styles.categoryTabText,
                selectedCategory === category.key && styles.categoryTabTextActive
              ]}>
                {category.label}
              </Text>
            </TouchableOpacity>
          ))}
        </ScrollView>

        {/* Messages */}
        <View style={styles.messagesContainer}>
          {currentMessages.map((message, index) => (
            <View key={index} style={styles.messageCard}>
              <Text style={styles.messageText}>{message}</Text>
              <TouchableOpacity
                style={styles.copyButton}
                onPress={() => copyToClipboard(message)}
              >
                <Ionicons name="copy" size={16} color="#FF69B4" />
                <Text style={styles.copyButtonText}>Copy</Text>
              </TouchableOpacity>
            </View>
          ))}
        </View>

        {/* Message Tips */}
        <View style={styles.tipsSection}>
          <Text style={styles.tipsTitle}>Message Tips 📱</Text>
          <View style={styles.tipsCard}>
            <View style={styles.tip}>
              <Ionicons name="time" size={16} color="#FF69B4" />
              <Text style={styles.tipText}>
                Send good morning messages to start their day with a smile
              </Text>
            </View>
            <View style={styles.tip}>
              <Ionicons name="heart" size={16} color="#FF69B4" />
              <Text style={styles.tipText}>
                Personalize messages by adding their name or inside jokes
              </Text>
            </View>
            <View style={styles.tip}>
              <Ionicons name="happy" size={16} color="#FF69B4" />
              <Text style={styles.tipText}>
                Use funny Hinglish messages to make them laugh
              </Text>
            </View>
            <View style={styles.tip}>
              <Ionicons name="chatbubble" size={16} color="#FF69B4" />
              <Text style={styles.tipText}>
                Don't overuse - quality over quantity in messaging
              </Text>
            </View>
          </View>
        </View>

        {/* Usage Instructions */}
        <View style={styles.instructionsSection}>
          <Text style={styles.instructionsTitle}>How to Use 📋</Text>
          <View style={styles.instructionsCard}>
            <View style={styles.instruction}>
              <View style={styles.stepNumber}>
                <Text style={styles.stepNumberText}>1</Text>
              </View>
              <Text style={styles.instructionText}>
                Choose a message category from the tabs above
              </Text>
            </View>
            <View style={styles.instruction}>
              <View style={styles.stepNumber}>
                <Text style={styles.stepNumberText}>2</Text>
              </View>
              <Text style={styles.instructionText}>
                Tap "Copy" on any message you like
              </Text>
            </View>
            <View style={styles.instruction}>
              <View style={styles.stepNumber}>
                <Text style={styles.stepNumberText}>3</Text>
              </View>
              <Text style={styles.instructionText}>
                Open WhatsApp/SMS and paste the message to your partner
              </Text>
            </View>
            <View style={styles.instruction}>
              <View style={styles.stepNumber}>
                <Text style={styles.stepNumberText}>4</Text>
              </View>
              <Text style={styles.instructionText}>
                Add personal touches to make it more special!
              </Text>
            </View>
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
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 5,
  },
  headerSubtitle: {
    fontSize: 14,
    color: '#666',
  },
  categoriesContainer: {
    marginBottom: 20,
  },
  categoriesContent: {
    paddingHorizontal: 20,
    gap: 10,
  },
  categoryTab: {
    backgroundColor: '#fff',
    borderRadius: 25,
    paddingHorizontal: 16,
    paddingVertical: 10,
    borderWidth: 1,
    borderColor: '#FF69B4',
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  categoryTabActive: {
    backgroundColor: '#FF69B4',
    borderColor: '#FF69B4',
  },
  categoryTabText: {
    fontSize: 14,
    color: '#FF69B4',
    fontWeight: '600',
  },
  categoryTabTextActive: {
    color: '#fff',
  },
  messagesContainer: {
    paddingHorizontal: 20,
    gap: 15,
  },
  messageCard: {
    backgroundColor: '#fff',
    borderRadius: 15,
    padding: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  messageText: {
    fontSize: 16,
    color: '#333',
    lineHeight: 24,
    marginBottom: 15,
  },
  copyButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFF0F7',
    borderRadius: 20,
    paddingHorizontal: 12,
    paddingVertical: 6,
    alignSelf: 'flex-end',
    gap: 5,
  },
  copyButtonText: {
    fontSize: 14,
    color: '#FF69B4',
    fontWeight: '600',
  },
  tipsSection: {
    margin: 20,
  },
  tipsTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 15,
  },
  tipsCard: {
    backgroundColor: '#fff',
    borderRadius: 15,
    padding: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  tip: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 15,
  },
  tipText: {
    flex: 1,
    fontSize: 14,
    color: '#666',
    marginLeft: 10,
    lineHeight: 20,
  },
  instructionsSection: {
    margin: 20,
    marginTop: 0,
  },
  instructionsTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 15,
  },
  instructionsCard: {
    backgroundColor: '#fff',
    borderRadius: 15,
    padding: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  instruction: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 15,
  },
  stepNumber: {
    width: 24,
    height: 24,
    borderRadius: 12,
    backgroundColor: '#FF69B4',
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 12,
  },
  stepNumberText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: 'bold',
  },
  instructionText: {
    flex: 1,
    fontSize: 14,
    color: '#666',
    lineHeight: 20,
  },
});