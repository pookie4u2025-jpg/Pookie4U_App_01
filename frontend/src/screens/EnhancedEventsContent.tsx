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
  ActivityIndicator,
  Dimensions,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useAuthStore } from '../stores/useAuthStore';
import { useTheme } from '../contexts/ThemeContext';
import { formatDate, formatCountdown, getDaysUntil } from '../utils/DateFormatter';
import * as Haptics from 'expo-haptics';

const { width } = Dimensions.get('window');

interface ReminderSettings {
  enabled: boolean;
  days_before: number;
  times_per_day: number;
  reminder_times: string[];
}

interface Event {
  id: string;
  name: string;
  date: string;
  category: string;
  type?: string;
  importance?: string;
  description: string;
  tips?: string[];
  tasks?: Array<{task: string, category: string, points: number}>;
  gift_suggestions?: string[];
  days_until?: number;
  is_upcoming?: boolean;
  auto_generated?: boolean;
  prefilled?: boolean;
  reminder_days?: number;
  cultural_significance?: string;
  traditional_colors?: string[];
  reminder_settings?: ReminderSettings;
  user_id?: string;
  created_at?: string;
  updated_at?: string;
}

interface EventSuggestion {
  category: string;
  suggestions: string[];
}

interface CalendarData {
  events: Event[];
  total_count: number;
  categories: Array<{id: string, name: string, color: string}>;
  upcoming_count: number;
  this_month_count: number;
}

export default function EnhancedEventsContent() {
  const { token, user, isAuthenticated } = useAuthStore();
  const { theme } = useTheme();
  
  // ALL HOOKS MUST BE CALLED BEFORE ANY EARLY RETURNS
  const [calendarData, setCalendarData] = useState<CalendarData>({
    events: [],
    total_count: 0,
    categories: [],
    upcoming_count: 0,
    this_month_count: 0
  });
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [showAllEvents, setShowAllEvents] = useState(false);
  const [loadingMore, setLoadingMore] = useState(false);
  const [currentOffset, setCurrentOffset] = useState(0);
  const [hasMoreEvents, setHasMoreEvents] = useState(true);
  const [editingEvent, setEditingEvent] = useState<Event | null>(null);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showAddModal, setShowAddModal] = useState(false);
  const [deletingEventId, setDeletingEventId] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedEvent, setSelectedEvent] = useState<Event | null>(null);
  const [eventDetailModal, setEventDetailModal] = useState(false);
  const [addCustomEventModal, setAddCustomEventModal] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [customEventModal, setCustomEventModal] = useState(false);
  const [suggestionModal, setSuggestionModal] = useState(false);
  
  // Custom event form states
  const [customEventName, setCustomEventName] = useState('');
  const [customEventDate, setCustomEventDate] = useState('');
  const [customEventDescription, setCustomEventDescription] = useState('');

  // New event form states (for modal)
  const [newEventName, setNewEventName] = useState('');
  const [newEventDate, setNewEventDate] = useState('');
  const [newEventCategory, setNewEventCategory] = useState('personal');
  const [newEventDescription, setNewEventDescription] = useState('');

  // Debug authentication state
  useEffect(() => {
    console.log('🔐 Auth Debug - isAuthenticated:', isAuthenticated);
    console.log('🔐 Auth Debug - token exists:', !!token);
    console.log('🔐 Auth Debug - user exists:', !!user);
    if (!token) {
      console.warn('⚠️ No authentication token available');
    }
  }, [token, user, isAuthenticated]);

  useEffect(() => {
    if (token && isAuthenticated && user) {
      console.log('🔐 Loading events - user authenticated');
      loadEvents();
    } else {
      console.log('🔐 Not loading events - authentication not complete', {
        hasToken: !!token,
        isAuthenticated,
        hasUser: !!user
      });
    }
  }, [token, isAuthenticated, user]);

  // Show login message if not authenticated (AFTER all hooks)
  if (!isAuthenticated || !token || !user) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.unauthenticatedContainer}>
          <Ionicons name="calendar-outline" size={64} color="#FF1493" />
          <Text style={styles.unauthenticatedTitle}>Please Sign In</Text>
          <Text style={styles.unauthenticatedMessage}>
            You need to be signed in to view your calendar events.
          </Text>
        </View>
      </SafeAreaView>
    );
  }

  const loadEvents = async (loadMore: boolean = false) => {
    if (!token || !isAuthenticated) {
      console.log('🔐 Skipping events load - not authenticated or no token');
      return;
    }
    
    if (!loadMore) {
      setLoading(true);
      setCurrentOffset(0);
    } else {
      setLoadingMore(true);
    }
    
    try {
      const apiUrl = process.env.EXPO_PUBLIC_BACKEND_URL || 'https://relationship-app-4.preview.emergentagent.com';
      const offset = loadMore ? currentOffset : 0;
      const limit = 20; // Load 20 events at a time
      
      const url = `${apiUrl}/api/events?limit=${limit}&offset=${offset}`;
      console.log('Loading events from:', url);
      
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });
      
      console.log('Events response status:', response.status);
      
      if (response.ok) {
        const data = await response.json();
        console.log('Events data received:', data);
        
        if (loadMore) {
          // Append new events to existing ones with deduplication
          const existingEventIds = new Set(prev.events.map(e => e.id));
          const newEvents = data.events.filter((e: Event) => !existingEventIds.has(e.id));
          
          setCalendarData(prev => ({
            ...data,
            events: [...prev.events, ...newEvents]
          }));
          setCurrentOffset(offset + limit);
        } else {
          // Replace all events (also deduplicate in case backend returns duplicates)
          const uniqueEvents = data.events.reduce((acc: Event[], event: Event) => {
            if (!acc.some(e => e.id === event.id)) {
              acc.push(event);
            }
            return acc;
          }, []);
          
          setCalendarData({
            ...data,
            events: uniqueEvents
          });
          setCurrentOffset(limit);
        }
        
        // Update hasMoreEvents based on pagination info
        if (data.pagination) {
          setHasMoreEvents(data.pagination.has_more);
        } else {
          setHasMoreEvents(false);
        }
      } else {
        const errorText = await response.text();
        console.error('Events API error:', response.status, errorText);
        Alert.alert('Error', `Failed to load calendar events (${response.status})`);
      }
    } catch (error) {
      console.error('Events loading error:', error);
      Alert.alert('Network Error', 'Failed to connect to the server. Please check your internet connection and try again.');
    } finally {
      setLoading(false);
      setLoadingMore(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadEvents();
    setRefreshing(false);
  };

  const calculateDaysUntil = (date: string): number => {
    const eventDate = new Date(date);
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    eventDate.setHours(0, 0, 0, 0);
    
    const diffTime = eventDate.getTime() - today.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
  };

  const formatDaysCountdown = (days: number): string => {
    if (days === 0) return 'Today';
    if (days === 1) return '1d';
    if (days < 0) return 'Past';
    return `${days}d`;
  };

  // Filter events based on search query
  const filterEventsBySearch = (events: Event[]): Event[] => {
    if (!searchQuery.trim()) return events;
    
    const query = searchQuery.toLowerCase().trim();
    return events.filter(event => 
      event.name.toLowerCase().includes(query) ||
      event.description.toLowerCase().includes(query) ||
      event.category.toLowerCase().includes(query) ||
      event.type?.toLowerCase().includes(query)
    );
  };

  const getPrefilledEvents = (): Event[] => {
    const prefilledEvents = calendarData.events.filter(event => {
      const days = calculateDaysUntil(event.date);
      // Show prefilled events (festivals, holidays, monthly check-ins, etc.)
      return days >= 0 && (
        event.prefilled === true || 
        event.category === 'relationship_maintenance' ||
        (event.prefilled === undefined && event.category !== 'custom' && 
         event.category !== 'personal_birthday' && 
         event.category !== 'personal_anniversary')
      );
    });
    
    const filteredEvents = filterEventsBySearch(prefilledEvents);
    return filteredEvents.slice(0, showAllEvents ? undefined : 3); // Show top 3 or all if expanded
  };

  const getCustomEvents = (): Event[] => {
    const customEvents = calendarData.events.filter(event => {
      // Show only custom events (user-created), anniversaries, and birthdays in Custom section
      return event.category === 'custom' || 
             event.category === 'personal_birthday' || 
             event.category === 'personal_anniversary';
    });
    
    return filterEventsBySearch(customEvents);
  };

  const handleEventPress = (event: Event) => {
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    setSelectedEvent(event);
    setEventDetailModal(true);
  };

  const handleAddCustomEvent = async () => {
    if (!customEventName.trim() || !customEventDate) {
      Alert.alert('Error', 'Please fill in all required fields');
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
          name: customEventName.trim(),
          date: customEventDate,
          description: customEventDescription.trim() || customEventName.trim(),
        }),
      });

      if (response.ok) {
        Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
        Alert.alert('Success!', 'Custom event added successfully');
        setCustomEventName('');
        setCustomEventDate('');
        setCustomEventDescription('');
        setAddCustomEventModal(false);
        await loadEvents(); // Reload events
      } else {
        Alert.alert('Error', 'Failed to create custom event');
      }
    } catch (error) {
      console.error('Add custom event error:', error);
      Alert.alert('Error', 'Failed to create event. Please try again.');
    }
  };

  const handleAddEvent = () => {
    setShowAddModal(true);
  };

  // Handle edit event
  const handleEditEvent = (event: Event) => {
    // Allow editing custom events, anniversaries, and birthdays
    if (event.category === 'custom' || 
        event.category === 'personal_birthday' || 
        event.category === 'personal_anniversary') {
      setEditingEvent(event);
      setShowEditModal(true);
    } else {
      Alert.alert('Cannot Edit', 'Only personal events can be edited. System festivals and holidays are read-only.');
    }
  };

  // Handle delete event
  const handleDeleteEvent = async (event: Event) => {
    // Allow deleting custom events, anniversaries, and birthdays
    if (!(event.category === 'custom' || 
          event.category === 'personal_birthday' || 
          event.category === 'personal_anniversary')) {
      Alert.alert('Cannot Delete', 'Only personal events can be deleted. System festivals and holidays are protected.');
      return;
    }

    Alert.alert(
      'Delete Event',
      `Are you sure you want to delete "${event.name}"? This action cannot be undone.`,
      [
        { text: 'Cancel', style: 'cancel' },
        { 
          text: 'Delete', 
          style: 'destructive',
          onPress: () => deleteEvent(event.id)
        }
      ]
    );
  };

  // Delete event from backend
  const deleteEvent = async (eventId: string) => {
    if (!token) return;
    
    setDeletingEventId(eventId);
    try {
      const apiUrl = process.env.EXPO_PUBLIC_BACKEND_URL || 'https://relationship-app-4.preview.emergentagent.com';
      const response = await fetch(`${apiUrl}/api/events/custom/${eventId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        // Remove event from local state
        setCalendarData(prev => ({
          ...prev,
          events: prev.events.filter(e => e.id !== eventId),
          total_count: prev.total_count - 1
        }));
        Alert.alert('Success', 'Event deleted successfully!');
      } else {
        const errorText = await response.text();
        console.error('Delete event error:', response.status, errorText);
        Alert.alert('Error', 'Failed to delete event. Please try again.');
      }
    } catch (error) {
      console.error('Delete event error:', error);
      Alert.alert('Network Error', 'Failed to connect to the server. Please check your internet connection.');
    } finally {
      setDeletingEventId(null);
    }
  };

  // Update event
  const updateEvent = async (eventId: string, updateData: any) => {
    if (!token) return;
    
    try {
      const apiUrl = process.env.EXPO_PUBLIC_BACKEND_URL || 'https://relationship-app-4.preview.emergentagent.com';
      const response = await fetch(`${apiUrl}/api/events/custom/${eventId}`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updateData),
      });

      if (response.ok) {
        const result = await response.json();
        // Update event in local state
        setCalendarData(prev => ({
          ...prev,
          events: prev.events.map(e => 
            e.id === eventId ? { ...e, ...result.event } : e
          )
        }));
        setShowEditModal(false);
        setEditingEvent(null);
        Alert.alert('Success', 'Event updated successfully!');
        
        // Reload events to get fresh data
        loadEvents(false);
      } else {
        const errorText = await response.text();
        console.error('Update event error:', response.status, errorText);
        Alert.alert('Error', 'Failed to update event. Please try again.');
      }
    } catch (error) {
      console.error('Update event error:', error);
      Alert.alert('Network Error', 'Failed to connect to the server. Please check your internet connection.');
    }
  };

  const handleAddSuggestion = (suggestion: string) => {
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
    // Pre-fill the custom event form with the suggestion
    setCustomEventName(suggestion);
    setAddCustomEventModal(true);
  };

  const createCustomEvent = async () => {
    if (!newEventName || !newEventDate) {
      Alert.alert('Error', 'Please fill in event name and date');
      return;
    }

    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
    try {
      const response = await fetch(`${process.env.EXPO_PUBLIC_BACKEND_URL}/api/events/custom`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          name: newEventName,
          date: newEventDate,
          category: newEventCategory,
          description: newEventDescription
        })
      });

      if (response.ok) {
        Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
        Alert.alert('Success', 'Custom event created successfully!');
        setCustomEventModal(false);
        setNewEventName('');
        setNewEventDate('');
        setNewEventDescription('');
        loadEvents(); // Refresh events
      } else {
        Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);
        Alert.alert('Error', 'Failed to create custom event');
      }
    } catch (error) {
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);
      Alert.alert('Error', 'Failed to create custom event');
    }
  };

  // Old functions removed - using new enhanced calendar implementation

  const getEventIcon = (category: string) => {
    switch (category.toLowerCase()) {
      case 'festival': return 'sparkles';
      case 'romantic': return 'heart';
      case 'celebration': return 'gift';
      case 'family': return 'people';
      case 'personal': return 'person';
      default: return 'calendar-outline';
    }
  };

  const getEventColor = (category: string, daysUntil: number) => {
    if (daysUntil < 0) return '#999'; // Past events
    if (daysUntil === 0) return theme.error; // Today
    if (daysUntil <= 7) return theme.warning; // This week
    
    switch (category.toLowerCase()) {
      case 'festival': return '#9C27B0';
      case 'romantic': return theme.primary;
      case 'celebration': return '#FF5722';
      case 'family': return '#2196F3';
      case 'personal': return theme.success;
      default: return theme.primary;
    }
  };

  const closeModal = () => {
    setModalVisible(false);
    setSelectedEvent(null);
  };

  const EventCard = ({ event }: { event: Event }) => {
    const daysUntil = getDaysUntil(event.date);
    const eventColor = getEventColor(event.category, daysUntil);
    
    return (
      <TouchableOpacity
        style={[styles.eventCard, { backgroundColor: theme.surface }]}
        onPress={() => handleEventPress(event)}
        activeOpacity={0.7}
      >
        <View style={styles.eventHeader}>
          <View style={[styles.eventIcon, { backgroundColor: eventColor + '20' }]}>
            <Ionicons name={getEventIcon(event.category)} size={24} color={eventColor} />
          </View>
          <View style={styles.eventInfo}>
            <Text style={[styles.eventName, { color: theme.text }]}>{event.name}</Text>
            <Text style={[styles.eventCategory, { color: theme.textSecondary }]}>
              {event.category}
            </Text>
          </View>
          <View style={styles.eventRight}>
            <Text style={[styles.eventDate, { color: theme.text }]}>
              {formatDate(event.date)}
            </Text>
            <Text style={[
              styles.countdown,
              { 
                color: eventColor,
                backgroundColor: eventColor + '20'
              }
            ]}>
              {formatCountdown(event.date)}
            </Text>
          </View>
        </View>
        
        {event.description && (
          <Text style={[styles.eventDescription, { color: theme.textSecondary }]} numberOfLines={2}>
            {event.description}
          </Text>
        )}
      </TouchableOpacity>
    );
  };

  return (
    <View style={[styles.container, { backgroundColor: theme.background }]}>
      <ScrollView
        style={styles.scrollContainer}
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={onRefresh}
            tintColor={theme.primary}
          />
        }
        showsVerticalScrollIndicator={false}
      >
        {/* Header */}
        <View style={styles.header}>
          <Text style={[styles.mainTitle, { color: theme.text }]}>
            Occasion Reminders
          </Text>
          <Text style={[styles.subtitle, { color: theme.textSecondary }]}>
            Never miss a special moment
          </Text>
        </View>

        {/* Search Bar */}
        <View style={[styles.searchContainer, { backgroundColor: theme.surface }]}>
          <View style={[styles.searchInputContainer, { backgroundColor: theme.background, borderColor: theme.border }]}>
            <Ionicons name="search" size={20} color={theme.textSecondary} style={styles.searchIcon} />
            <TextInput
              style={[styles.searchInput, { color: theme.text }]}
              placeholder="Search events..."
              placeholderTextColor={theme.textSecondary}
              value={searchQuery}
              onChangeText={setSearchQuery}
              autoCapitalize="none"
              autoCorrect={false}
            />
            {searchQuery.length > 0 && (
              <TouchableOpacity onPress={() => setSearchQuery('')} style={styles.clearButton}>
                <Ionicons name="close-circle" size={20} color={theme.textSecondary} />
              </TouchableOpacity>
            )}
          </View>
        </View>

        {/* Pre-filled Events Section */}
        <View style={styles.section}>
          <View style={styles.sectionHeader}>
            <Text style={[styles.sectionTitle, { color: theme.text }]}>
              Pre-Filled Events
            </Text>
            <TouchableOpacity
              style={styles.seeAllButton}
              onPress={() => {
                if (!showAllEvents && hasMoreEvents) {
                  loadEvents(false); // Load all events without pagination
                }
                setShowAllEvents(!showAllEvents);
              }}
            >
              <Text style={[styles.seeAllText, { color: theme.primary }]}>
                {showAllEvents ? 'Show Less' : `See All (${calendarData.total_count})`}
              </Text>
            </TouchableOpacity>
          </View>
          
          {loading && (
            <View style={styles.loadingContainer}>
              <ActivityIndicator size="small" color={theme.primary} />
              <Text style={[styles.loadingText, { color: theme.textSecondary }]}>
                Loading events...
              </Text>
            </View>
          )}
          
          {!loading && getPrefilledEvents().map((event) => (
            <TouchableOpacity
              key={event.id}
              style={[styles.eventCard, { backgroundColor: theme.surface }]}
              onPress={() => handleEventPress(event)}
              activeOpacity={0.8}
            >
              <View style={styles.eventContent}>
                <View style={styles.eventInfo}>
                  <Text style={[styles.eventName, { color: theme.text }]} numberOfLines={1}>
                    {event.name}
                  </Text>
                  <Text style={[styles.eventDescription, { color: theme.textSecondary }]} numberOfLines={1}>
                    {event.description}
                  </Text>
                </View>
                <View style={styles.eventRight}>
                  <View style={[styles.daysContainer, { backgroundColor: theme.primary + '20' }]}>
                    <Text style={[styles.daysText, { color: theme.primary }]}>
                      {formatDaysCountdown(calculateDaysUntil(event.date))}
                    </Text>
                  </View>
                  <Ionicons name="chevron-forward" size={20} color={theme.textSecondary} />
                </View>
              </View>
            </TouchableOpacity>
          ))}
          
          {/* Load More Button */}
          {showAllEvents && hasMoreEvents && !loading && (
            <TouchableOpacity
              style={[styles.loadMoreButton, { backgroundColor: theme.surface }]}
              onPress={() => loadEvents(true)}
              disabled={loadingMore}
            >
              {loadingMore ? (
                <ActivityIndicator size="small" color={theme.primary} />
              ) : (
                <Text style={[styles.loadMoreText, { color: theme.primary }]}>
                  Load More Events
                </Text>
              )}
            </TouchableOpacity>
          )}
        </View>

        {/* Custom Events Section */}
        <View style={styles.section}>
          <View style={styles.sectionHeader}>
            <Text style={[styles.sectionTitle, { color: theme.text }]}>
              Custom Events
            </Text>
            <View style={styles.customEventControls}>
              <TouchableOpacity
                style={[styles.controlButton, { backgroundColor: theme.surface }]}
                onPress={onRefresh}
              >
                <Ionicons name="refresh" size={20} color={theme.primary} />
              </TouchableOpacity>
              <TouchableOpacity
                style={[styles.controlButton, { backgroundColor: theme.surface }]}
                onPress={() => setAddCustomEventModal(true)}
              >
                <Ionicons name="add" size={20} color={theme.primary} />
              </TouchableOpacity>
            </View>
          </View>
          
          {getCustomEvents().length === 0 ? (
            <View style={[styles.emptyState, { backgroundColor: theme.surface }]}>
              <Text style={[styles.emptyStateTitle, { color: theme.text }]}>
                No custom events yet!
              </Text>
              <TouchableOpacity
                style={[styles.addFirstButton, { backgroundColor: theme.primary }]}
                onPress={() => setAddCustomEventModal(true)}
              >
                <Text style={styles.addFirstButtonText}>+ Add First Event</Text>
              </TouchableOpacity>
            </View>
          ) : (
            getCustomEvents().map((event) => (
              <TouchableOpacity
                key={event.id}
                style={[styles.eventCard, { backgroundColor: theme.surface }]}
                onPress={() => handleEventPress(event)}
                activeOpacity={0.8}
              >
                <View style={styles.eventContent}>
                  <View style={styles.eventInfo}>
                    <Text style={[styles.eventName, { color: theme.text }]} numberOfLines={1}>
                      {event.name}
                    </Text>
                    <Text style={[styles.eventDescription, { color: theme.textSecondary }]} numberOfLines={1}>
                      {event.description}
                    </Text>
                  </View>
                  <View style={styles.eventRight}>
                    <View style={[styles.daysContainer, { backgroundColor: theme.primary + '20' }]}>
                      <Text style={[styles.daysText, { color: theme.primary }]}>
                        {formatDaysCountdown(calculateDaysUntil(event.date))}
                      </Text>
                    </View>
                    <Ionicons name="chevron-forward" size={20} color={theme.textSecondary} />
                  </View>
                </View>
              </TouchableOpacity>
            ))
          )}
        </View>

        {/* Event Suggestions Section */}
        <View style={styles.section}>
          <Text style={[styles.sectionTitle, { color: theme.text }]}>
            Event Suggestions
          </Text>
          
          <View style={styles.suggestionsGrid}>
            {/* Pre-defined suggestions matching the design */}
            {[
              { icon: "heart", title: "Her Parents' Birthday", description: "Add reminder for her parents" },
              { icon: "gift", title: "Her Siblings' Birthday", description: "Special days for her family" },
              { icon: "people", title: "Best Friend's Birthday", description: "Important friendship dates" },
              { icon: "sparkles", title: "Family Anniversary", description: "Celebrate family milestones" },
            ].map((suggestion, index) => (
              <TouchableOpacity
                key={index}
                style={[styles.suggestionCard, { backgroundColor: theme.surface }]}
                onPress={() => handleAddSuggestion(suggestion.title)}
                activeOpacity={0.8}
              >
                <View style={styles.suggestionContent}>
                  <View style={[styles.suggestionIcon, { backgroundColor: theme.primary + '20' }]}>
                    <Ionicons name={suggestion.icon as any} size={24} color={theme.primary} />
                  </View>
                  <View style={styles.suggestionInfo}>
                    <Text style={[styles.suggestionTitle, { color: theme.text }]} numberOfLines={1}>
                      {suggestion.title}
                    </Text>
                    <Text style={[styles.suggestionDescription, { color: theme.textSecondary }]} numberOfLines={1}>
                      {suggestion.description}
                    </Text>
                  </View>
                  <TouchableOpacity
                    style={styles.suggestionAdd}
                    onPress={() => handleAddSuggestion(suggestion.title)}
                  >
                    <Ionicons name="add" size={20} color={theme.primary} />
                  </TouchableOpacity>
                </View>
              </TouchableOpacity>
            ))}
          </View>
        </View>
      </ScrollView>

      {/* Event Detail Modal */}
      <Modal
        visible={eventDetailModal}
        animationType="slide"
        presentationStyle="pageSheet"
        onRequestClose={() => setEventDetailModal(false)}
      >
        <SafeAreaView style={[styles.modalContainer, { backgroundColor: theme.background }]}>
          <View style={[styles.modalHeader, { backgroundColor: theme.surface }]}>
            <Text style={[styles.modalTitle, { color: theme.text }]}>Event Details</Text>
            <TouchableOpacity onPress={() => setEventDetailModal(false)}>
              <Ionicons name="close" size={28} color={theme.text} />
            </TouchableOpacity>
          </View>
          
          {selectedEvent && (
            <ScrollView style={styles.modalContent}>
              <View style={styles.eventDetailHeader}>
                <Text style={[styles.eventDetailName, { color: theme.text }]}>
                  {selectedEvent.name}
                </Text>
                <Text style={[styles.eventDetailDate, { color: theme.textSecondary }]}>
                  {new Date(selectedEvent.date).toLocaleDateString('en-US', {
                    weekday: 'long',
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric'
                  })}
                </Text>
                <Text style={[styles.eventDetailCountdown, { color: theme.primary }]}>
                  {formatDaysCountdown(calculateDaysUntil(selectedEvent.date))} until event
                </Text>
              </View>
              
              <Text style={[styles.eventDetailDescription, { color: theme.text }]}>
                {selectedEvent.description}
              </Text>
              
              {selectedEvent.tips && selectedEvent.tips.length > 0 && (
                <View style={styles.tipsSection}>
                  <Text style={[styles.sectionSubtitle, { color: theme.text }]}>💡 Tips & Ideas:</Text>
                  {selectedEvent.tips.map((tip, index) => (
                    <Text key={index} style={[styles.tipItem, { color: theme.textSecondary }]}>
                      • {tip}
                    </Text>
                  ))}
                </View>
              )}
              
              {selectedEvent.gift_suggestions && selectedEvent.gift_suggestions.length > 0 && (
                <View style={styles.giftsSection}>
                  <Text style={[styles.sectionSubtitle, { color: theme.text }]}>🎁 Gift Suggestions:</Text>
                  {selectedEvent.gift_suggestions.map((gift, index) => (
                    <Text key={index} style={[styles.giftItem, { color: theme.textSecondary }]}>
                      • {gift}
                    </Text>
                  ))}
                </View>
              )}
              
              {/* Edit and Delete Action Buttons */}
              {selectedEvent && (
                <View style={styles.actionButtonsContainer}>
                  {/* Show edit and delete for custom events, or show info message for system events */}
                  {(selectedEvent.category === 'custom' || 
                    selectedEvent.category === 'personal_birthday' || 
                    selectedEvent.category === 'personal_anniversary') ? (
                    <>
                      <TouchableOpacity
                        style={[styles.editButton, { backgroundColor: theme.primary }]}
                        onPress={() => handleEditEvent(selectedEvent)}
                        activeOpacity={0.8}
                      >
                        <Ionicons name="pencil" size={20} color="#fff" style={styles.buttonIcon} />
                        <Text style={styles.editButtonText}>Edit Event</Text>
                      </TouchableOpacity>
                      
                      <TouchableOpacity
                        style={[styles.deleteButton, { backgroundColor: '#FF3B30' }]}
                        onPress={() => handleDeleteEvent(selectedEvent)}
                        activeOpacity={0.8}
                        disabled={deletingEventId === selectedEvent.id}
                      >
                        {deletingEventId === selectedEvent.id ? (
                          <ActivityIndicator size="small" color="#fff" style={styles.buttonIcon} />
                        ) : (
                          <Ionicons name="trash" size={20} color="#fff" style={styles.buttonIcon} />
                        )}
                        <Text style={styles.deleteButtonText}>
                          {deletingEventId === selectedEvent.id ? 'Deleting...' : 'Delete Event'}
                        </Text>
                      </TouchableOpacity>
                    </>
                  ) : (
                    <View style={[styles.infoMessage, { backgroundColor: theme.surface }]}>
                      <Ionicons name="information-circle" size={20} color={theme.primary} style={styles.buttonIcon} />
                      <Text style={[styles.infoMessageText, { color: theme.textSecondary }]}>
                        System events cannot be edited or deleted
                      </Text>
                    </View>
                  )}
                </View>
              )}
            </ScrollView>
          )}
        </SafeAreaView>
      </Modal>

      {/* Add Custom Event Modal */}
      <Modal
        visible={addCustomEventModal}
        animationType="slide"
        presentationStyle="pageSheet"
        onRequestClose={() => setAddCustomEventModal(false)}
      >
        <SafeAreaView style={[styles.modalContainer, { backgroundColor: theme.background }]}>
          <View style={[styles.modalHeader, { backgroundColor: theme.surface }]}>
            <Text style={[styles.modalTitle, { color: theme.text }]}>Add Custom Event</Text>
            <TouchableOpacity onPress={() => setAddCustomEventModal(false)}>
              <Ionicons name="close" size={28} color={theme.text} />
            </TouchableOpacity>
          </View>
          
          <ScrollView style={styles.modalContent}>
            <View style={styles.formGroup}>
              <Text style={[styles.formLabel, { color: theme.text }]}>Event Name *</Text>
              <TextInput
                style={[styles.formInput, { backgroundColor: theme.surface, color: theme.text, borderColor: theme.primary }]}
                value={customEventName}
                onChangeText={setCustomEventName}
                placeholder="Enter event name"
                placeholderTextColor={theme.textSecondary}
              />
            </View>
            
            <View style={styles.formGroup}>
              <Text style={[styles.formLabel, { color: theme.text }]}>Date *</Text>
              <TextInput
                style={[styles.formInput, { backgroundColor: theme.surface, color: theme.text, borderColor: theme.primary }]}
                value={customEventDate}
                onChangeText={setCustomEventDate}
                placeholder="DD-MM-YYYY"
                placeholderTextColor={theme.textSecondary}
              />
            </View>
            
            <View style={styles.formGroup}>
              <Text style={[styles.formLabel, { color: theme.text }]}>Description</Text>
              <TextInput
                style={[
                  styles.formInput,
                  styles.textArea,
                  { backgroundColor: theme.surface, color: theme.text, borderColor: theme.primary }
                ]}
                value={customEventDescription}
                onChangeText={setCustomEventDescription}
                placeholder="Event description (optional)"
                placeholderTextColor={theme.textSecondary}
                multiline
                numberOfLines={3}
              />
            </View>
            
            <TouchableOpacity
              style={[styles.submitButton, { backgroundColor: theme.primary }]}
              onPress={handleAddCustomEvent}
            >
              <Text style={styles.submitButtonText}>Create Event</Text>
            </TouchableOpacity>
          </ScrollView>
        </SafeAreaView>
      </Modal>

      {/* Edit Event Modal */}
      <Modal
        visible={showEditModal}
        animationType="slide"
        presentationStyle="pageSheet"
        onRequestClose={() => {
          setShowEditModal(false);
          setEditingEvent(null);
        }}
      >
        <SafeAreaView style={[styles.modalContainer, { backgroundColor: theme.background }]}>
          <View style={[styles.modalHeader, { backgroundColor: theme.surface }]}>
            <Text style={[styles.modalTitle, { color: theme.text }]}>Edit Event</Text>
            <TouchableOpacity onPress={() => {
              setShowEditModal(false);
              setEditingEvent(null);
            }}>
              <Ionicons name="close" size={28} color={theme.text} />
            </TouchableOpacity>
          </View>
          
          {editingEvent && (
            <ScrollView style={styles.modalContent}>
              <View style={styles.formGroup}>
                <Text style={[styles.formLabel, { color: theme.text }]}>Event Name *</Text>
                <TextInput
                  style={[styles.formInput, { backgroundColor: theme.surface, color: theme.text, borderColor: theme.primary }]}
                  value={editingEvent.name}
                  onChangeText={(text) => setEditingEvent(prev => prev ? {...prev, name: text} : null)}
                  placeholder="Enter event name"
                  placeholderTextColor={theme.textSecondary}
                />
              </View>
              
              <View style={styles.formGroup}>
                <Text style={[styles.formLabel, { color: theme.text }]}>Date *</Text>
                <TextInput
                  style={[styles.formInput, { backgroundColor: theme.surface, color: theme.text, borderColor: theme.primary }]}
                  value={editingEvent.date}
                  onChangeText={(text) => setEditingEvent(prev => prev ? {...prev, date: text} : null)}
                  placeholder="DD-MM-YYYY"
                  placeholderTextColor={theme.textSecondary}
                />
              </View>
              
              <View style={styles.formGroup}>
                <Text style={[styles.formLabel, { color: theme.text }]}>Description</Text>
                <TextInput
                  style={[
                    styles.formInput,
                    styles.textArea,
                    { backgroundColor: theme.surface, color: theme.text, borderColor: theme.primary }
                  ]}
                  value={editingEvent.description || ''}
                  onChangeText={(text) => setEditingEvent(prev => prev ? {...prev, description: text} : null)}
                  placeholder="Event description (optional)"
                  placeholderTextColor={theme.textSecondary}
                  multiline
                  numberOfLines={3}
                />
              </View>

              {/* Reminder Settings Section */}
              <View style={styles.reminderSection}>
                <Text style={[styles.sectionSubtitle, { color: theme.text }]}>⏰ Reminder Settings</Text>
                
                <View style={styles.formGroup}>
                  <Text style={[styles.formLabel, { color: theme.text }]}>
                    Reminder starts (days before event)
                  </Text>
                  <TextInput
                    style={[styles.formInput, { backgroundColor: theme.surface, color: theme.text, borderColor: theme.primary }]}
                    value={editingEvent.reminder_settings?.days_before?.toString() || '10'}
                    onChangeText={(text) => {
                      const days = parseInt(text) || 10;
                      setEditingEvent(prev => prev ? {
                        ...prev,
                        reminder_settings: {
                          ...prev.reminder_settings,
                          days_before: days,
                          enabled: true,
                          times_per_day: prev.reminder_settings?.times_per_day || 2,
                          reminder_times: prev.reminder_settings?.reminder_times || ['10:00', '17:00']
                        }
                      } : null);
                    }}
                    keyboardType="numeric"
                    placeholder="10"
                    placeholderTextColor={theme.textSecondary}
                  />
                </View>

                <View style={styles.formGroup}>
                  <Text style={[styles.formLabel, { color: theme.text }]}>
                    Reminders per day
                  </Text>
                  <TextInput
                    style={[styles.formInput, { backgroundColor: theme.surface, color: theme.text, borderColor: theme.primary }]}
                    value={editingEvent.reminder_settings?.times_per_day?.toString() || '2'}
                    onChangeText={(text) => {
                      const times = parseInt(text) || 2;
                      setEditingEvent(prev => prev ? {
                        ...prev,
                        reminder_settings: {
                          ...prev.reminder_settings,
                          times_per_day: times,
                          enabled: true,
                          days_before: prev.reminder_settings?.days_before || 10,
                          reminder_times: prev.reminder_settings?.reminder_times || ['10:00', '17:00']
                        }
                      } : null);
                    }}
                    keyboardType="numeric"
                    placeholder="2"
                    placeholderTextColor={theme.textSecondary}
                  />
                </View>

                <View style={styles.formGroup}>
                  <Text style={[styles.formLabel, { color: theme.text }]}>
                    Reminder times (comma separated, 24-hour format)
                  </Text>
                  <TextInput
                    style={[styles.formInput, { backgroundColor: theme.surface, color: theme.text, borderColor: theme.primary }]}
                    value={editingEvent.reminder_settings?.reminder_times?.join(', ') || '10:00, 17:00'}
                    onChangeText={(text) => {
                      const times = text.split(',').map(t => t.trim()).filter(t => t.length > 0);
                      setEditingEvent(prev => prev ? {
                        ...prev,
                        reminder_settings: {
                          ...prev.reminder_settings,
                          reminder_times: times.length > 0 ? times : ['10:00', '17:00'],
                          enabled: true,
                          days_before: prev.reminder_settings?.days_before || 10,
                          times_per_day: prev.reminder_settings?.times_per_day || 2
                        }
                      } : null);
                    }}
                    placeholder="10:00, 17:00"
                    placeholderTextColor={theme.textSecondary}
                  />
                  <Text style={[styles.helpText, { color: theme.textSecondary }]}>
                    Example: 09:00, 14:00, 19:00 (for 3 times per day)
                  </Text>
                </View>
              </View>
              
              <TouchableOpacity
                style={[styles.submitButton, { backgroundColor: theme.primary }]}
                onPress={() => {
                  if (editingEvent && editingEvent.id) {
                    const updateData = {
                      name: editingEvent.name,
                      date: editingEvent.date,
                      description: editingEvent.description,
                      reminder_settings: editingEvent.reminder_settings
                    };
                    updateEvent(editingEvent.id, updateData);
                  }
                }}
              >
                <Text style={styles.submitButtonText}>Update Event</Text>
              </TouchableOpacity>
            </ScrollView>
          )}
        </SafeAreaView>
      </Modal>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  scrollContainer: {
    flex: 1,
  },
  
  // Header Styles
  header: {
    paddingHorizontal: 20,
    paddingTop: 20,
    paddingBottom: 10,
  },
  mainTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  subtitle: {
    fontSize: 16,
    opacity: 0.8,
  },
  
  // Search Bar Styles
  searchContainer: {
    paddingHorizontal: 20,
    paddingBottom: 16,
  },
  searchInputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    borderRadius: 12,
    borderWidth: 1,
    paddingHorizontal: 16,
    paddingVertical: 12,
  },
  searchIcon: {
    marginRight: 12,
  },
  searchInput: {
    flex: 1,
    fontSize: 16,
    paddingVertical: 0,
  },
  clearButton: {
    marginLeft: 8,
    padding: 4,
  },
  
  // Section Styles
  section: {
    marginBottom: 24,
    paddingHorizontal: 20,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: '700',
  },
  seeAllButton: {
    padding: 4,
  },
  seeAllText: {
    fontSize: 16,
    fontWeight: '600',
  },
  
  // Custom Event Controls
  customEventControls: {
    flexDirection: 'row',
    gap: 8,
  },
  controlButton: {
    width: 36,
    height: 36,
    borderRadius: 18,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#e0e0e0',
  },
  
  // Loading State
  loadingContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 20,
    gap: 10,
  },
  loadingText: {
    fontSize: 14,
  },
  
  // Event Card Styles
  eventCard: {
    borderRadius: 16,
    marginBottom: 12,
    padding: 16,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 3,
  },
  eventContent: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  eventHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  eventIcon: {
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  eventInfo: {
    flex: 1,
    marginRight: 12,
  },
  eventCategory: {
    fontSize: 12,
    textTransform: 'capitalize',
    opacity: 0.7,
  },
  eventDate: {
    fontSize: 14,
    fontWeight: '500',
  },
  countdown: {
    fontSize: 12,
    fontWeight: '600',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 8,
  },
  eventName: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 4,
  },
  eventDescription: {
    fontSize: 14,
    opacity: 0.7,
  },
  eventRight: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  daysContainer: {
    borderRadius: 12,
    paddingHorizontal: 8,
    paddingVertical: 4,
    minWidth: 36,
    alignItems: 'center',
  },
  daysText: {
    fontSize: 12,
    fontWeight: '700',
  },
  
  // Empty State
  emptyState: {
    padding: 32,
    borderRadius: 16,
    alignItems: 'center',
    marginBottom: 12,
  },
  emptyStateTitle: {
    fontSize: 18,
    fontWeight: '600',
    marginBottom: 16,
  },
  addFirstButton: {
    backgroundColor: '#FF69B4',
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 24,
  },
  addFirstButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  
  // Suggestions Grid
  suggestionsGrid: {
    gap: 12,
  },
  suggestionCard: {
    borderRadius: 16,
    padding: 16,
    elevation: 1,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
  },
  suggestionContent: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  suggestionIcon: {
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  suggestionInfo: {
    flex: 1,
  },
  suggestionTitle: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 2,
  },
  suggestionDescription: {
    fontSize: 14,
    opacity: 0.7,
  },
  suggestionAdd: {
    width: 32,
    height: 32,
    borderRadius: 16,
    justifyContent: 'center',
    alignItems: 'center',
  },
  
  // Modal Styles
  modalContainer: {
    flex: 1,
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: 'bold',
  },
  modalContent: {
    flex: 1,
    padding: 20,
  },
  
  // Event Detail Modal
  eventDetailHeader: {
    alignItems: 'center',
    marginBottom: 24,
  },
  eventDetailName: {
    fontSize: 24,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 8,
  },
  eventDetailDate: {
    fontSize: 16,
    marginBottom: 4,
    textAlign: 'center',
  },
  eventDetailCountdown: {
    fontSize: 18,
    fontWeight: '600',
    textAlign: 'center',
  },
  eventDetailDescription: {
    fontSize: 16,
    lineHeight: 24,
    textAlign: 'center',
    marginBottom: 24,
  },
  
  // Tips and Gifts Sections
  tipsSection: {
    marginBottom: 24,
  },
  giftsSection: {
    marginBottom: 24,
  },
  sectionSubtitle: {
    fontSize: 18,
    fontWeight: '600',
    marginBottom: 12,
  },
  tipItem: {
    fontSize: 14,
    lineHeight: 20,
    marginBottom: 8,
  },
  giftItem: {
    fontSize: 14,
    lineHeight: 20,
    marginBottom: 8,
  },
  
  // Form Styles
  formGroup: {
    marginBottom: 20,
  },
  formLabel: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 8,
  },
  formInput: {
    borderWidth: 2,
    borderRadius: 12,
    padding: 16,
    fontSize: 16,
  },
  textArea: {
    height: 100,
    textAlignVertical: 'top',
  },
  submitButton: {
    padding: 16,
    borderRadius: 12,
    alignItems: 'center',
    marginTop: 16,
  },
  submitButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  
  // Load More Button Styles
  loadMoreButton: {
    padding: 16,
    borderRadius: 12,
    alignItems: 'center',
    marginTop: 16,
    marginBottom: 8,
    borderWidth: 1,
    borderColor: '#e0e0e0',
  },
  loadMoreText: {
    fontSize: 16,
    fontWeight: '600',
  },
  
  // Action buttons in modal
  actionButtonsContainer: {
    marginTop: 24,
    paddingHorizontal: 16,
    paddingBottom: 16,
  },
  editButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 14,
    paddingHorizontal: 24,
    borderRadius: 12,
    marginBottom: 12,
  },
  deleteButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 14,
    paddingHorizontal: 24,
    borderRadius: 12,
    marginBottom: 12,
  },
  editButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
    marginLeft: 8,
  },
  deleteButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
    marginLeft: 8,
  },
  buttonIcon: {
    marginRight: 4,
  },
  infoMessage: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    borderRadius: 12,
    marginTop: 8,
  },
  infoMessageText: {
    fontSize: 14,
    marginLeft: 8,
    flex: 1,
  },
  
  // Reminder section styles
  reminderSection: {
    marginTop: 24,
    paddingTop: 16,
    borderTopWidth: 1,
    borderTopColor: '#e0e0e0',
  },
  helpText: {
    fontSize: 12,
    marginTop: 4,
    fontStyle: 'italic',
  },
  
  // Search functionality styles
  searchContainer: {
    paddingHorizontal: 16,
    paddingVertical: 12,
  },
  searchInputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    borderWidth: 1,
    borderRadius: 12,
    paddingHorizontal: 12,
    paddingVertical: 8,
  },
  searchIcon: {
    marginRight: 8,
  },
  searchInput: {
    flex: 1,
    fontSize: 16,
    paddingVertical: 4,
  },
  clearButton: {
    marginLeft: 8,
    padding: 4,
  },
  
  // Unauthenticated state styles
  unauthenticatedContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 32,
    backgroundColor: '#f8f9fa',
  },
  unauthenticatedTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1a1a1a',
    marginTop: 24,
    marginBottom: 12,
    textAlign: 'center',
  },
  unauthenticatedMessage: {
    fontSize: 16,
    color: '#666666',
    textAlign: 'center',
    lineHeight: 24,
  },
});