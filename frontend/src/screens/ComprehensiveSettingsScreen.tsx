import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Switch,
  Alert,
  Share,
  Linking,
  Platform,
  Modal,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';
import { useAuthStore } from '../stores/useAuthStore';
import { useTheme } from '../contexts/ThemeContext';

interface SettingSection {
  id: string;
  title: string;
  icon: string;
  items: SettingItem[];
}

interface SettingItem {
  id: string;
  title: string;
  subtitle?: string;
  type: 'toggle' | 'navigation' | 'action';
  value?: boolean;
  onPress?: () => void;
}

export default function ComprehensiveSettingsScreen() {
  const { user, logout, updateRelationshipMode } = useAuthStore();
  const { theme, isDark, toggleTheme, setThemeMode, themeMode } = useTheme();
  const router = useRouter();
  
  // Settings state
  const [notifications, setNotifications] = useState(true);
  const [soundEnabled, setSoundEnabled] = useState(true);
  const [hapticsEnabled, setHapticsEnabled] = useState(true);
  const [showRelationshipModeSelector, setShowRelationshipModeSelector] = useState(false);

  // Relationship mode options (same as in ProfileContent)
  const RELATIONSHIP_MODES = [
    { value: 'SAME_HOME', label: 'Same Home', description: 'Living together' },
    { value: 'DAILY_IRL', label: 'Daily Meetup', description: 'Meet daily at work/study' },
    { value: 'LONG_DISTANCE', label: 'Long Distance', description: 'Different cities' },
  ];

  const handleSubscriptionManagement = () => {
    router.push('/subscription');
  };

  const handleCancelSubscription = () => {
    Alert.alert(
      'Cancel Subscription',
      'Are you sure you want to cancel your subscription? You will lose access to premium features at the end of your billing period.',
      [
        { text: 'Keep Subscription', style: 'cancel' },
        { text: 'Cancel', style: 'destructive', onPress: () => {
          Alert.alert('Success', 'Subscription cancelled. You will retain access until 25/12/2024.');
        }}
      ]
    );
  };

  const handleUpgradePlan = () => {
    Alert.alert(
      'Switch to 6-Month Plan',
      'Save money with our 6-month plan!\n\n6-Month Plan: ₹450 (₹75/month)\nMonthly Plan: ₹79/month\n\nSave ₹24 every 6 months!',
      [
        { text: 'Switch to 6-Month Plan (₹450)', onPress: () => {
          Alert.alert('Success', 'Switched to 6-Month plan! You save ₹24 every 6 months.');
        }},
        { text: 'Keep Monthly Plan', style: 'cancel' }
      ]
    );
  };

  const handleNotificationSettings = () => {
    Alert.alert(
      'Notification Settings',
      'Configure your notification preferences:',
      [
        { text: 'Daily Reminders: ON', onPress: () => {} },
        { text: 'Weekly Challenges: ON', onPress: () => {} },
        { text: 'Achievement Alerts: ON', onPress: () => {} },
        { text: 'Event Reminders: ON', onPress: () => {} },
        { text: 'Winner Announcements: ON', onPress: () => {} },
        { text: 'Done', style: 'default' }
      ]
    );
  };

  const handleThemeChange = () => {
    Alert.alert(
      'Theme Settings',
      'Choose your preferred theme:',
      [
        { text: 'System Default', onPress: () => setThemeMode('system') },
        { text: 'Light Mode', onPress: () => setThemeMode('light') },
        { text: 'Dark Mode', onPress: () => setThemeMode('dark') },
        { text: 'Cancel', style: 'cancel' }
      ]
    );
  };

  const handleShareApp = async () => {
    try {
      await Share.share({
        message: 'Strengthen your relationship with Pookie4u! Daily romantic tasks, rewards & more. Download now: https://pookie4u.app',
        title: 'Pookie4u - Relationship Goals App'
      });
    } catch (error) {
      Alert.alert('Error', 'Could not share the app');
    }
  };

  const handlePrivacyPolicy = () => {
    Linking.openURL('https://pookie4u.com/privacy-policy');
  };

  const handleTermsOfService = () => {
    Linking.openURL('https://pookie4u.com/terms-of-service');
  };

  const handleCookiePolicy = () => {
    Linking.openURL('https://pookie4u.com/cookie-policy');
  };

  const handleLicense = () => {
    Alert.alert(
      'License Information',
      'Pookie4u v1.0.0\n\nMIT License\n\nCopyright (c) 2024 Pookie4u\n\nBuilt with love for couples everywhere! ❤️',
      [{ text: 'OK' }]
    );
  };

  const handleHelpSupport = () => {
    Alert.alert(
      'Help & Support',
      'Need help? Contact us:',
      [
        { text: 'Email Support', onPress: () => Linking.openURL('mailto:support@pookie4u.com') },
        { text: 'FAQ', onPress: () => Linking.openURL('https://pookie4u.com/faq') },
        { text: 'Live Chat', onPress: () => Alert.alert('Coming Soon', 'Live chat will be available in the next update!') },
        { text: 'Cancel', style: 'cancel' }
      ]
    );
  };

  const handleLogout = () => {
    Alert.alert(
      'Logout',
      'Are you sure you want to logout?',
      [
        { text: 'Cancel', style: 'cancel' },
        { text: 'Logout', style: 'destructive', onPress: () => {
          logout();
          router.replace('/');
        }}
      ]
    );
  };

  const handleEditAccount = () => {
    Alert.alert(
      'Edit Account',
      'Account editing will be available in the next update.',
      [{ text: 'OK' }]
    );
  };

  const handleRelationshipModePress = () => {
    setShowRelationshipModeSelector(true);
  };

  const handleRelationshipModeSelect = async (mode: string) => {
    try {
      await updateRelationshipMode(mode);
      setShowRelationshipModeSelector(false);
      Alert.alert('Success', 'Relationship mode updated successfully!');
    } catch (error) {
      Alert.alert('Error', 'Failed to update relationship mode. Please try again.');
    }
  };

  const settingSections: SettingSection[] = [
    {
      id: 'account',
      title: 'Account',
      icon: 'person-circle',
      items: [
        {
          id: 'profile_info',
          title: 'Account Details',
          subtitle: `${user?.name} • ${user?.email}`,
          type: 'navigation',
          onPress: handleEditAccount
        },
        {
          id: 'relationship_mode',
          title: 'Relationship Mode',
          subtitle: user?.relationship_mode?.replace('_', ' '),
          type: 'navigation',
          onPress: handleRelationshipModePress
        }
      ]
    },
    {
      id: 'preferences',
      title: 'Preferences',
      icon: 'settings',
      items: [
        {
          id: 'theme',
          title: 'Theme',
          subtitle: `${themeMode === 'system' ? 'System Default' : themeMode === 'dark' ? 'Dark Mode' : 'Light Mode'}`,
          type: 'navigation',
          onPress: handleThemeChange
        },
        {
          id: 'notifications',
          title: 'Notifications',
          subtitle: 'Push notifications for tasks & events',
          type: 'toggle',
          value: notifications,
          onPress: () => {
            setNotifications(!notifications);
            handleNotificationSettings();
          }
        },
        {
          id: 'sound',
          title: 'Sound Effects',
          subtitle: 'Task completion sounds',
          type: 'toggle',
          value: soundEnabled,
          onPress: () => setSoundEnabled(!soundEnabled)
        },
        {
          id: 'haptics',
          title: 'Haptic Feedback',
          subtitle: 'Vibration for interactions',
          type: 'toggle',
          value: hapticsEnabled,
          onPress: () => setHapticsEnabled(!hapticsEnabled)
        }
      ]
    },
    {
      id: 'subscription',
      title: 'Subscription',
      icon: 'diamond',
      items: [
        {
          id: 'manage_subscription',
          title: 'Manage Subscription',
          subtitle: 'Monthly Plan - ₹79/month',
          type: 'navigation',
          onPress: handleSubscriptionManagement
        }
      ]
    },
    {
      id: 'social',
      title: 'Social',
      icon: 'share',
      items: [
        {
          id: 'share_app',
          title: 'Share App',
          subtitle: 'Invite friends to join Pookie4u',
          type: 'action',
          onPress: handleShareApp
        }
      ]
    },
    {
      id: 'support',
      title: 'Help & Support',
      icon: 'help-circle',
      items: [
        {
          id: 'help_support',
          title: 'Help & Support',
          subtitle: 'Contact us for assistance',
          type: 'navigation',
          onPress: handleHelpSupport
        }
      ]
    },
    {
      id: 'privacy',
      title: 'Privacy',
      icon: 'shield-checkmark',
      items: [
        {
          id: 'privacy_policy',
          title: 'Privacy Policy',
          subtitle: 'How we protect your data',
          type: 'navigation',
          onPress: handlePrivacyPolicy
        },
        {
          id: 'cookie_policy',
          title: 'Cookie Policy',
          subtitle: 'Cookie usage information',
          type: 'navigation',
          onPress: handleCookiePolicy
        }
      ]
    },
    {
      id: 'legal',
      title: 'Legal',
      icon: 'document-text',
      items: [
        {
          id: 'terms_of_service',
          title: 'Terms of Service',
          subtitle: 'App usage terms',
          type: 'navigation',
          onPress: handleTermsOfService
        },
        {
          id: 'license',
          title: 'License',
          subtitle: 'Open source licenses',
          type: 'navigation',
          onPress: handleLicense
        }
      ]
    }
  ];

  const renderSettingItem = (item: SettingItem) => {
    return (
      <TouchableOpacity
        key={item.id}
        style={[styles.settingItem, { borderBottomColor: theme.border }]}
        onPress={item.onPress}
      >
        <View style={styles.settingInfo}>
          <Text style={[styles.settingTitle, { color: theme.text }]}>{item.title}</Text>
          {item.subtitle && (
            <Text style={[styles.settingSubtitle, { color: theme.textSecondary }]}>{item.subtitle}</Text>
          )}
        </View>
        
        <View style={styles.settingAction}>
          {item.type === 'toggle' ? (
            <Switch
              value={item.value}
              onValueChange={item.onPress}
              trackColor={{ false: theme.border, true: theme.primary }}
              thumbColor={item.value ? '#fff' : '#fff'}
            />
          ) : (
            <Ionicons name="chevron-forward" size={20} color={theme.textSecondary} />
          )}
        </View>
      </TouchableOpacity>
    );
  };

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: theme.background }]}>
      {/* Header with Back Navigation */}
      <View style={[styles.header, { backgroundColor: theme.surface, borderBottomColor: theme.border }]}>
        <TouchableOpacity 
          style={styles.backButton}
          onPress={() => router.back()}
        >
          <Ionicons 
            name={Platform.OS === 'ios' ? 'chevron-back' : 'arrow-back'} 
            size={24} 
            color={theme.primary} 
          />
        </TouchableOpacity>
        <Text style={[styles.title, { color: theme.text }]}>Settings</Text>
        <View style={styles.headerSpacer} />
      </View>

      <ScrollView style={styles.scrollView}>
        {settingSections.map((section) => (
          <View key={section.id} style={[styles.section, { backgroundColor: theme.surface }]}>
            <View style={[styles.sectionHeader, { borderBottomColor: theme.border }]}>
              <Ionicons name={section.icon as any} size={20} color={theme.primary} />
              <Text style={[styles.sectionTitle, { color: theme.text }]}>{section.title}</Text>
            </View>
            
            <View style={styles.sectionContent}>
              {section.items.map((item) => renderSettingItem(item))}
            </View>
          </View>
        ))}

        {/* Logout Button */}
        <View style={styles.logoutSection}>
          <TouchableOpacity 
            style={[styles.logoutButton, { backgroundColor: theme.error }]} 
            onPress={handleLogout}
          >
            <Ionicons name="log-out" size={20} color="#fff" />
            <Text style={styles.logoutText}>Logout</Text>
          </TouchableOpacity>
        </View>

        {/* App Version */}
        <View style={styles.versionSection}>
          <Text style={[styles.versionText, { color: theme.textSecondary }]}>Pookie4u v1.0.0</Text>
          <Text style={[styles.versionSubtext, { color: theme.border }]}>Made with ❤️ for couples</Text>
        </View>
      </ScrollView>

      {/* Relationship Mode Selection Modal */}
      <Modal
        visible={showRelationshipModeSelector}
        transparent={true}
        animationType="slide"
        onRequestClose={() => setShowRelationshipModeSelector(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={[styles.modalContent, { backgroundColor: theme.surface }]}>
            <View style={[styles.modalHeader, { borderBottomColor: theme.border }]}>
              <Text style={[styles.modalTitle, { color: theme.text }]}>Select Relationship Mode</Text>
              <TouchableOpacity
                onPress={() => setShowRelationshipModeSelector(false)}
                style={styles.modalCloseButton}
              >
                <Ionicons name="close" size={24} color={theme.textSecondary} />
              </TouchableOpacity>
            </View>
            
            <ScrollView style={styles.modalScrollView}>
              {RELATIONSHIP_MODES.map((mode) => (
                <TouchableOpacity
                  key={mode.value}
                  style={[
                    styles.relationshipModeOption,
                    { borderBottomColor: theme.border },
                    user?.relationship_mode === mode.value && { backgroundColor: theme.primary + '20' }
                  ]}
                  onPress={() => handleRelationshipModeSelect(mode.value)}
                >
                  <View style={styles.relationshipModeInfo}>
                    <Text style={[styles.relationshipModeLabel, { color: theme.text }]}>
                      {mode.label}
                    </Text>
                    <Text style={[styles.relationshipModeDescription, { color: theme.textSecondary }]}>
                      {mode.description}
                    </Text>
                  </View>
                  {user?.relationship_mode === mode.value && (
                    <Ionicons name="checkmark-circle" size={24} color={theme.primary} />
                  )}
                </TouchableOpacity>
              ))}
            </ScrollView>
          </View>
        </View>
      </Modal>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 15,
    borderBottomWidth: 1,
  },
  backButton: {
    padding: 4,
  },
  title: {
    fontSize: 20,
    fontWeight: 'bold',
    marginLeft: 16,
  },
  headerSpacer: {
    flex: 1,
  },
  scrollView: {
    flex: 1,
  },
  section: {
    marginTop: 20,
    marginHorizontal: 20,
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  sectionHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    borderBottomWidth: 1,
    gap: 10,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
  },
  sectionContent: {
    padding: 0,
  },
  settingItem: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    borderBottomWidth: 1,
  },
  settingInfo: {
    flex: 1,
  },
  settingTitle: {
    fontSize: 16,
    fontWeight: '500',
    marginBottom: 2,
  },
  settingSubtitle: {
    fontSize: 14,
  },
  settingAction: {
    marginLeft: 12,
  },
  logoutSection: {
    margin: 20,
    marginTop: 30,
  },
  logoutButton: {
    borderRadius: 12,
    padding: 16,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
  },
  logoutText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  versionSection: {
    alignItems: 'center',
    padding: 20,
    marginBottom: 20,
  },
  versionText: {
    fontSize: 14,
    marginBottom: 5,
  },
  versionSubtext: {
    fontSize: 12,
  },
  // Modal styles
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'flex-end',
  },
  modalContent: {
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    maxHeight: '80%',
  },
  modalHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: 20,
    borderBottomWidth: 1,
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: 'bold',
  },
  modalCloseButton: {
    padding: 4,
  },
  modalScrollView: {
    maxHeight: 400,
  },
  relationshipModeOption: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    borderBottomWidth: 1,
  },
  relationshipModeInfo: {
    flex: 1,
  },
  relationshipModeLabel: {
    fontSize: 16,
    fontWeight: '500',
    marginBottom: 4,
  },
  relationshipModeDescription: {
    fontSize: 14,
  },
});