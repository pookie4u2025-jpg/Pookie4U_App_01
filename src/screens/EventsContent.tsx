import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  RefreshControl,
  Modal,
  TextInput,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useAuthStore } from '../stores/useAuthStore';
import { useTheme } from '../contexts/ThemeContext';
import { formatDate, getCountdownText, parseDate, isValidDateFormat } from '../utils/DateFormatter';

interface Event {
  id: string;
  name: string;
  date: string;
  type: 'holiday' | 'personal';
  description?: string;
  recurring?: boolean;
  created_by?: string;
}

interface EventTip {
  id: string;
  tip: string;
  relationship_mode: string;
  event_type: string;
}

interface TaskSuggestion {
  id: string;
  title: string;
  description: string;
  relationship_mode: string;
  event_type: string;
  points: number;
}

export default function EventsContent() {
  const { token, user } = useAuthStore();
  const { theme } = useTheme();
  
  const [events, setEvents] = useState<Event[]>([]);
  const [refreshing, setRefreshing] = useState(false);
  const [selectedEvent, setSelectedEvent] = useState<Event | null>(null);
  const [showEventDetails, setShowEventDetails] = useState(false);
  const [showAddModal, setShowAddModal] = useState(false);
  const [eventTips, setEventTips] = useState<EventTip[]>([]);
  const [taskSuggestions, setTaskSuggestions] = useState<TaskSuggestion[]>([]);
  const [newEvent, setNewEvent] = useState({ name: '', date: '' });

  useEffect(() => {
    if (token) {
      fetchEvents();
      fetchEventTips();
      fetchTaskSuggestions();
    }
  }, [token]);

  const fetchEvents = async () => {
    try {
      const response = await fetch(`${process.env.EXPO_PUBLIC_BACKEND_URL}/api/events`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      const data = await response.json();
      if (response.ok) {
        // Combine pre-loaded and custom events
        const allEvents = [
          ...(data.pre_loaded_events || []),
          ...(data.custom_events || [])
        ];
        
        // Sort events by date (ascending - nearest first)
        const sortedEvents = allEvents.sort((a, b) => {
          const dateA = new Date(a.date);
          const dateB = new Date(b.date);
          return dateA.getTime() - dateB.getTime();
        });
        
        setEvents(sortedEvents);
      }
    } catch (error) {
      console.error('Error fetching events:', error);
    }
  };

  const fetchEventTips = async () => {
    // For now, use static tips - in a real app this would be from the backend
    const staticTips: EventTip[] = [
      {
        id: '1',
        tip: 'Plan a romantic dinner at home with candles and her favorite music',
        relationship_mode: 'SAME_HOME',
        event_type: 'holiday'
      },
      {
        id: '2',
        tip: 'Send a surprise delivery of flowers to her workplace',
        relationship_mode: 'DAILY_IRL',
        event_type: 'holiday'
      },
      {
        id: '3',
        tip: 'Schedule a video date with a virtual dinner experience',
        relationship_mode: 'LONG_DISTANCE',
        event_type: 'holiday'
      },
      {
        id: '4',
        tip: 'Create a photo album of your favorite memories together',
        relationship_mode: 'SAME_HOME',
        event_type: 'personal'
      },
      {
        id: '5',
        tip: 'Plan a surprise outing to celebrate your special day',
        relationship_mode: 'DAILY_IRL',
        event_type: 'personal'
      },
      {
        id: '6',
        tip: 'Send a care package with her favorite treats and a heartfelt letter',
        relationship_mode: 'LONG_DISTANCE',
        event_type: 'personal'
      }
    ];
    setEventTips(staticTips);
  };

  const fetchTaskSuggestions = async () => {
    // Static task suggestions - in real app this would be from backend
    const staticTasks: TaskSuggestion[] = [
      {
        id: '1',
        title: 'Write a Love Letter',
        description: 'Express your feelings in a handwritten letter',
        relationship_mode: 'SAME_HOME',
        event_type: 'holiday',
        points: 25
      },
      {
        id: '2',
        title: 'Plan a Surprise Date',
        description: 'Organize a special outing for the occasion',
        relationship_mode: 'DAILY_IRL',
        event_type: 'holiday',
        points: 30
      },
      {
        id: '3',
        title: 'Send Virtual Flowers',
        description: 'Order online flowers to be delivered',
        relationship_mode: 'LONG_DISTANCE',
        event_type: 'holiday',
        points: 20
      },
      {
        id: '4',
        title: 'Cook Her Favorite Meal',
        description: 'Prepare a special dinner together',
        relationship_mode: 'SAME_HOME',
        event_type: 'personal',
        points: 25
      },
      {
        id: '5',
        title: 'Create a Memory Video',
        description: 'Compile photos and videos of your journey together',
        relationship_mode: 'DAILY_IRL',
        event_type: 'personal',
        points: 35
      },
      {
        id: '6',
        title: 'Schedule a Video Call',
        description: 'Plan a special video date to celebrate',
        relationship_mode: 'LONG_DISTANCE',
        event_type: 'personal',
        points: 15
      }
    ];
    setTaskSuggestions(staticTasks);
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await Promise.all([
      fetchEvents(),
      fetchEventTips(),
      fetchTaskSuggestions()
    ]);
    setRefreshing(false);
  };

  const addCustomEvent = async () => {
    if (!newEvent.name || !newEvent.date) {
      Alert.alert('Error', 'Please fill in all fields');
      return;
    }

    if (!isValidDateFormat(newEvent.date)) {
      Alert.alert('Error', 'Please use DD/MM/YYYY format for the date');
      return;
    }

    const parsedDate = parseDate(newEvent.date);
    if (!parsedDate) {
      Alert.alert('Error', 'Invalid date format. Please use DD/MM/YYYY');
      return;
    }

    try {
      const response = await fetch(`${process.env.EXPO_PUBLIC_BACKEND_URL}/api/events/custom`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          name: newEvent.name,
          date: parsedDate.toISOString(),
          recurring: false,
        }),
      });

      if (response.ok) {
        setShowAddModal(false);
        setNewEvent({ name: '', date: '' });
        Alert.alert('Success', 'Event added successfully!');
        await fetchEvents();
      } else {
        Alert.alert('Error', 'Failed to add event');
      }
    } catch (error) {
      Alert.alert('Error', 'Something went wrong');
    }
  };

  const handleEventPress = (event: Event) => {
    setSelectedEvent(event);
    setShowEventDetails(true);
  };

  const getEventIcon = (type: string) => {
    switch (type) {
      case 'holiday': return 'calendar';
      case 'personal': return 'heart';
      default: return 'star';
    }
  };

  const getRelevantTips = (eventType: string): EventTip[] => {
    return eventTips.filter(tip => 
      tip.event_type === eventType && 
      (!tip.relationship_mode || tip.relationship_mode === user?.relationship_mode)
    );
  };

  const getRelevantTasks = (eventType: string): TaskSuggestion[] => {
    return taskSuggestions.filter(task => 
      task.event_type === eventType && 
      (!task.relationship_mode || task.relationship_mode === user?.relationship_mode)
    ).slice(0, 3); // Limit to 3 suggestions as specified
  };

  const renderEventDetails = () => {
    if (!selectedEvent) return null;

    const relevantTips = getRelevantTips(selectedEvent.type);
    const relevantTasks = getRelevantTasks(selectedEvent.type);

    return (
      <Modal
        visible={showEventDetails}
        animationType="slide"
        presentationStyle="pageSheet"
      >
        <View style={[styles.modalContainer, { backgroundColor: theme.background }]}>
          <View style={[styles.modalHeader, { backgroundColor: theme.surface, borderBottomColor: theme.border }]}>
            <Text style={[styles.modalTitle, { color: theme.text }]}>{selectedEvent.name}</Text>
            <TouchableOpacity
              style={styles.closeButton}
              onPress={() => setShowEventDetails(false)}
            >
              <Ionicons name="close" size={24} color={theme.text} />
            </TouchableOpacity>
          </View>
          
          <ScrollView style={styles.modalContent}>
            {/* Event Info */}
            <View style={[styles.eventInfoCard, { backgroundColor: theme.surface }]}>
              <View style={styles.eventInfoHeader}>
                <Ionicons name={getEventIcon(selectedEvent.type)} size={24} color={theme.primary} />
                <View style={styles.eventInfoText}>
                  <Text style={[styles.eventDate, { color: theme.text }]}>
                    {formatDate(selectedEvent.date)}
                  </Text>
                  <Text style={[styles.eventCountdown, { color: theme.primary }]}>
                    {getCountdownText(selectedEvent.date)}
                  </Text>
                </View>
              </View>
              {selectedEvent.description && (
                <Text style={[styles.eventDescription, { color: theme.textSecondary }]}>
                  {selectedEvent.description}
                </Text>
              )}
            </View>

            {/* Contextual Tips */}
            {relevantTips.length > 0 && (
              <View style={[styles.tipsSection, { backgroundColor: theme.surface }]}>
                <Text style={[styles.sectionTitle, { color: theme.text }]}>💡 Tips for This Event</Text>
                {relevantTips.map((tip, index) => (
                  <View key={tip.id} style={[styles.tipCard, { backgroundColor: theme.background }]}>
                    <Text style={[styles.tipText, { color: theme.textSecondary }]}>{tip.tip}</Text>
                  </View>
                ))}
              </View>
            )}

            {/* Task Suggestions */}
            {relevantTasks.length > 0 && (
              <View style={[styles.tasksSection, { backgroundColor: theme.surface }]}>
                <Text style={[styles.sectionTitle, { color: theme.text }]}>✅ Suggested Tasks</Text>
                {relevantTasks.map((task, index) => (
                  <View key={task.id} style={[styles.taskCard, { backgroundColor: theme.background, borderLeftColor: theme.primary }]}>
                    <View style={styles.taskHeader}>
                      <Text style={[styles.taskTitle, { color: theme.text }]}>{task.title}</Text>
                      <Text style={[styles.taskPoints, { color: theme.success }]}>+{task.points} pts</Text>
                    </View>
                    <Text style={[styles.taskDescription, { color: theme.textSecondary }]}>{task.description}</Text>
                  </View>
                ))}
              </View>
            )}
          </ScrollView>
        </View>
      </Modal>
    );
  };

  const renderAddEventModal = () => (
    <Modal
      visible={showAddModal}
      animationType="slide"
      presentationStyle="pageSheet"
    >
      <View style={[styles.modalContainer, { backgroundColor: theme.background }]}>
        <View style={[styles.modalHeader, { backgroundColor: theme.surface, borderBottomColor: theme.border }]}>
          <Text style={[styles.modalTitle, { color: theme.text }]}>Add Personal Event</Text>
          <TouchableOpacity
            style={styles.closeButton}
            onPress={() => setShowAddModal(false)}
          >
            <Ionicons name="close" size={24} color={theme.text} />
          </TouchableOpacity>
        </View>
        
        <View style={styles.modalContent}>
          <View style={styles.inputGroup}>
            <Text style={[styles.inputLabel, { color: theme.text }]}>Event Name</Text>
            <TextInput
              style={[styles.input, { backgroundColor: theme.surface, color: theme.text, borderColor: theme.border }]}
              placeholder="e.g., Anniversary, Birthday"
              placeholderTextColor={theme.textSecondary}
              value={newEvent.name}
              onChangeText={(text) => setNewEvent({ ...newEvent, name: text })}
            />
          </View>
          
          <View style={styles.inputGroup}>
            <Text style={[styles.inputLabel, { color: theme.text }]}>Date (DD/MM/YYYY)</Text>
            <TextInput
              style={[styles.input, { backgroundColor: theme.surface, color: theme.text, borderColor: theme.border }]}
              placeholder="e.g., 14/02/2025"
              placeholderTextColor={theme.textSecondary}
              value={newEvent.date}
              onChangeText={(text) => setNewEvent({ ...newEvent, date: text })}
            />
          </View>
          
          <TouchableOpacity
            style={[styles.saveButton, { backgroundColor: theme.primary }]}
            onPress={addCustomEvent}
          >
            <Text style={styles.saveButtonText}>Add Event</Text>
          </TouchableOpacity>
        </View>
      </View>
    </Modal>
  );

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
          <Text style={[styles.title, { color: theme.text }]}>Special Events 🎉</Text>
          <Text style={[styles.subtitle, { color: theme.textSecondary }]}>
            Never miss important dates and celebrations
          </Text>
          <TouchableOpacity
            style={[styles.addButton, { backgroundColor: theme.primary }]}
            onPress={() => setShowAddModal(true)}
          >
            <Ionicons name="add" size={20} color="#fff" />
            <Text style={styles.addButtonText}>Add Event</Text>
          </TouchableOpacity>
        </View>

        {/* Events List */}
        <View style={styles.eventsContainer}>
          {events.length > 0 ? (
            events.map((event) => (
              <TouchableOpacity
                key={event.id}
                style={[styles.eventCard, { backgroundColor: theme.surface }]}
                onPress={() => handleEventPress(event)}
              >
                <View style={styles.eventIcon}>
                  <Ionicons name={getEventIcon(event.type)} size={24} color={theme.primary} />
                </View>
                <View style={styles.eventContent}>
                  <Text style={[styles.eventName, { color: theme.text }]}>{event.name}</Text>
                  <Text style={[styles.eventDate, { color: theme.textSecondary }]}>
                    {formatDate(event.date)}
                  </Text>
                  <Text style={[styles.eventCountdown, { color: theme.primary }]}>
                    {getCountdownText(event.date)}
                  </Text>
                </View>
                <View style={styles.eventArrow}>
                  <Ionicons name="chevron-forward" size={20} color={theme.textSecondary} />
                </View>
              </TouchableOpacity>
            ))
          ) : (
            <View style={styles.emptyState}>
              <Ionicons name="calendar-outline" size={48} color={theme.border} />
              <Text style={[styles.emptyTitle, { color: theme.textSecondary }]}>No events found</Text>
              <Text style={[styles.emptySubtitle, { color: theme.border }]}>
                Add your personal events to get started
              </Text>
            </View>
          )}
        </View>
      </ScrollView>

      {renderEventDetails()}
      {renderAddEventModal()}
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
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 5,
  },
  subtitle: {
    fontSize: 16,
    textAlign: 'center',
    marginBottom: 20,
  },
  addButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 20,
    gap: 8,
  },
  addButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  eventsContainer: {
    paddingHorizontal: 20,
    paddingBottom: 20,
  },
  eventCard: {
    flexDirection: 'row',
    alignItems: 'center',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  eventIcon: {
    marginRight: 12,
  },
  eventContent: {
    flex: 1,
  },
  eventName: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 4,
  },
  eventDate: {
    fontSize: 14,
    marginBottom: 2,
  },
  eventCountdown: {
    fontSize: 12,
    fontWeight: '500',
  },
  eventArrow: {
    marginLeft: 12,
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
    textAlign: 'center',
  },
  modalContainer: {
    flex: 1,
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    borderBottomWidth: 1,
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: 'bold',
  },
  closeButton: {
    padding: 4,
  },
  modalContent: {
    flex: 1,
    padding: 20,
  },
  eventInfoCard: {
    borderRadius: 12,
    padding: 16,
    marginBottom: 20,
  },
  eventInfoHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  eventInfoText: {
    marginLeft: 12,
  },
  eventDescription: {
    fontSize: 14,
    lineHeight: 20,
  },
  tipsSection: {
    borderRadius: 12,
    padding: 16,
    marginBottom: 20,
  },
  tasksSection: {
    borderRadius: 12,
    padding: 16,
    marginBottom: 20,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 12,
  },
  tipCard: {
    borderRadius: 8,
    padding: 12,
    marginBottom: 8,
  },
  tipText: {
    fontSize: 14,
    lineHeight: 20,
  },
  taskCard: {
    borderRadius: 8,
    padding: 12,
    marginBottom: 8,
    borderLeftWidth: 3,
  },
  taskHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 4,
  },
  taskTitle: {
    fontSize: 14,
    fontWeight: '600',
  },
  taskPoints: {
    fontSize: 12,
    fontWeight: '600',
  },
  taskDescription: {
    fontSize: 12,
    lineHeight: 16,
  },
  inputGroup: {
    marginBottom: 20,
  },
  inputLabel: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 8,
  },
  input: {
    borderWidth: 1,
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
  },
  saveButton: {
    borderRadius: 8,
    padding: 15,
    alignItems: 'center',
    marginTop: 20,
  },
  saveButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
});