import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  TextInput,
  Modal,
  RefreshControl,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { format, parseISO, differenceInDays, isToday, isTomorrow } from 'date-fns';
import { useAuthStore } from '../stores/useAuthStore';

const BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL || '';

interface Event {
  id: string;
  name: string;
  date: string;
  type: string;
  recurring?: boolean;
}

export default function EventsScreen() {
  const { token } = useAuthStore();
  const [preLoadedEvents, setPreLoadedEvents] = useState<Event[]>([]);
  const [customEvents, setCustomEvents] = useState<Event[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [newEventName, setNewEventName] = useState('');
  const [newEventDate, setNewEventDate] = useState('');

  useEffect(() => {
    fetchEvents();
  }, []);

  const fetchEvents = async () => {
    if (!token) return;
    setLoading(true);
    try {
      const response = await fetch(`${BACKEND_URL}/api/events`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      const data = await response.json();
      setPreLoadedEvents(data.pre_loaded_events || []);
      setCustomEvents(data.custom_events || []);
    } catch (error) {
      console.error('Failed to fetch events:', error);
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = async () => {
    await fetchEvents();
  };

  const createCustomEvent = async () => {
    if (!newEventName.trim() || !newEventDate.trim()) {
      Alert.alert('Error', 'Please fill in all fields');
      return;
    }

    if (!token) return;

    try {
      const response = await fetch(`${BACKEND_URL}/api/events/custom`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          name: newEventName,
          date: new Date(newEventDate).toISOString(),
          recurring: false,
        }),
      });

      if (response.ok) {
        Alert.alert('Success', 'Custom event created successfully!');
        setModalVisible(false);
        setNewEventName('');
        setNewEventDate('');
        await fetchEvents();
      } else {
        throw new Error('Failed to create event');
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to create custom event');
    }
  };

  const getEventIcon = (type: string) => {
    switch (type) {
      case 'holiday': return 'calendar';
      case 'personal': return 'heart';
      default: return 'star';
    }
  };

  const getEventColor = (type: string) => {
    switch (type) {
      case 'holiday': return '#4CAF50';
      case 'personal': return '#FF69B4';
      default: return '#2196F3';
    }
  };

  const getDaysUntil = (dateString: string) => {
    const eventDate = parseISO(dateString);
    const today = new Date();
    const days = differenceInDays(eventDate, today);
    
    if (isToday(eventDate)) return 'Today';
    if (isTomorrow(eventDate)) return 'Tomorrow';
    if (days > 0) return `${days} days`;
    return `${Math.abs(days)} days ago`;
  };

  const sortedEvents = [...preLoadedEvents, ...customEvents].sort((a, b) => {
    const dateA = parseISO(a.date);
    const dateB = parseISO(b.date);
    return dateA.getTime() - dateB.getTime();
  });

  const upcomingEvents = sortedEvents.filter(event => {
    const eventDate = parseISO(event.date);
    const today = new Date();
    return differenceInDays(eventDate, today) >= 0;
  });

  const pastEvents = sortedEvents.filter(event => {
    const eventDate = parseISO(event.date);
    const today = new Date();
    return differenceInDays(eventDate, today) < 0;
  });

  const renderEvent = (event: Event) => (
    <View key={event.id} style={styles.eventCard}>
      <View style={[styles.eventIcon, { backgroundColor: getEventColor(event.type) }]}>
        <Ionicons name={getEventIcon(event.type)} size={24} color="#fff" />
      </View>
      <View style={styles.eventContent}>
        <Text style={styles.eventName}>{event.name}</Text>
        <Text style={styles.eventDate}>
          {format(parseISO(event.date), 'MMMM dd, yyyy')}
        </Text>
        <Text style={[styles.eventCountdown, { color: getEventColor(event.type) }]}>
          {getDaysUntil(event.date)}
        </Text>
      </View>
      {event.type === 'personal' && (
        <View style={styles.personalBadge}>
          <Text style={styles.personalBadgeText}>Personal</Text>
        </View>
      )}
    </View>
  );

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
          <Text style={styles.headerTitle}>Events & Reminders 📅</Text>
          <Text style={styles.headerSubtitle}>
            Never miss an important date in your relationship
          </Text>
        </View>

        {/* Add Event Button */}
        <View style={styles.addEventContainer}>
          <TouchableOpacity
            style={styles.addEventButton}
            onPress={() => setModalVisible(true)}
          >
            <Ionicons name="add" size={24} color="#fff" />
            <Text style={styles.addEventButtonText}>Add First Event</Text>
          </TouchableOpacity>
        </View>

        {/* Upcoming Events */}
        {upcomingEvents.length > 0 && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Upcoming Events 🎉</Text>
            {upcomingEvents.map(renderEvent)}
          </View>
        )}

        {/* Past Events */}
        {pastEvents.length > 0 && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Past Events 📝</Text>
            {pastEvents.slice(0, 5).map(renderEvent)}
          </View>
        )}

        {/* Event Suggestions */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Event Suggestions 💡</Text>
          <View style={styles.suggestionsCard}>
            <View style={styles.suggestion}>
              <Ionicons name="heart" size={20} color="#FF69B4" />
              <Text style={styles.suggestionText}>Her Parents' Birthday</Text>
            </View>
            <View style={styles.suggestion}>
              <Ionicons name="calendar" size={20} color="#FF69B4" />
              <Text style={styles.suggestionText}>Her Siblings' Birthday</Text>
            </View>
            <View style={styles.suggestion}>
              <Ionicons name="star" size={20} color="#FF69B4" />
              <Text style={styles.suggestionText}>Her Work Anniversary</Text>
            </View>
            <View style={styles.suggestion}>
              <Ionicons name="school" size={20} color="#FF69B4" />
              <Text style={styles.suggestionText}>Her Graduation Day</Text>
            </View>
            <View style={styles.suggestion}>
              <Ionicons name="car" size={20} color="#FF69B4" />
              <Text style={styles.suggestionText}>Death Anniversary</Text>
            </View>
          </View>
        </View>

        {/* Event Tips */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Event Tips 📋</Text>
          <View style={styles.tipsCard}>
            <Text style={styles.tip}>• Plan celebrations 1-2 weeks in advance</Text>
            <Text style={styles.tip}>• Set reminders 3 days before important dates</Text>
            <Text style={styles.tip}>• Consider her family's important dates too</Text>
            <Text style={styles.tip}>• Create new traditions for your relationship</Text>
            <Text style={styles.tip}>• Document celebrations with photos and memories</Text>
          </View>
        </View>
      </ScrollView>

      {/* Add Event Modal */}
      <Modal
        animationType="slide"
        transparent={true}
        visible={modalVisible}
        onRequestClose={() => setModalVisible(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>Add Custom Event</Text>
              <TouchableOpacity
                style={styles.closeButton}
                onPress={() => setModalVisible(false)}
              >
                <Ionicons name="close" size={24} color="#666" />
              </TouchableOpacity>
            </View>

            <TextInput
              style={styles.input}
              placeholder="Event name (e.g., Our First Kiss)"
              value={newEventName}
              onChangeText={setNewEventName}
            />

            <TextInput
              style={styles.input}
              placeholder="Date (YYYY-MM-DD)"
              value={newEventDate}
              onChangeText={setNewEventDate}
            />

            <TouchableOpacity
              style={styles.createButton}
              onPress={createCustomEvent}
            >
              <Text style={styles.createButtonText}>Create Event</Text>
            </TouchableOpacity>
          </View>
        </View>
      </Modal>
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
  addEventContainer: {
    paddingHorizontal: 20,
    marginBottom: 20,
  },
  addEventButton: {
    backgroundColor: '#FF69B4',
    borderRadius: 15,
    padding: 15,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 10,
  },
  addEventButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  section: {
    marginHorizontal: 20,
    marginBottom: 20,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 15,
  },
  eventCard: {
    backgroundColor: '#fff',
    borderRadius: 15,
    padding: 20,
    marginBottom: 12,
    flexDirection: 'row',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  eventIcon: {
    width: 50,
    height: 50,
    borderRadius: 25,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 15,
  },
  eventContent: {
    flex: 1,
  },
  eventName: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 4,
  },
  eventDate: {
    fontSize: 14,
    color: '#666',
    marginBottom: 4,
  },
  eventCountdown: {
    fontSize: 12,
    fontWeight: '600',
  },
  personalBadge: {
    backgroundColor: '#FF69B4',
    borderRadius: 10,
    paddingHorizontal: 8,
    paddingVertical: 4,
  },
  personalBadgeText: {
    color: '#fff',
    fontSize: 10,
    fontWeight: 'bold',
  },
  suggestionsCard: {
    backgroundColor: '#fff',
    borderRadius: 15,
    padding: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  suggestion: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 15,
  },
  suggestionText: {
    flex: 1,
    fontSize: 14,
    color: '#666',
    marginLeft: 12,
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
    fontSize: 14,
    color: '#666',
    marginBottom: 8,
    lineHeight: 20,
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  modalContent: {
    backgroundColor: '#fff',
    borderRadius: 20,
    padding: 20,
    width: '90%',
    maxWidth: 400,
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 20,
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
  },
  closeButton: {
    padding: 5,
  },
  input: {
    borderWidth: 1,
    borderColor: '#e0e0e0',
    borderRadius: 10,
    padding: 15,
    fontSize: 16,
    marginBottom: 15,
    backgroundColor: '#f9f9f9',
  },
  createButton: {
    backgroundColor: '#FF69B4',
    borderRadius: 10,
    padding: 15,
    alignItems: 'center',
  },
  createButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
});