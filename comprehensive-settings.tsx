import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Switch,
  Alert,
  Platform,
  Linking,
  TextInput,
  Modal,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';
import { useTheme } from './src/contexts/ThemeContext';
import { useAuthStore } from './src/stores/useAuthStore';
import { useAppStore } from './src/stores/useAppStore';
import * as Haptics from 'expo-haptics';

export default function ComprehensiveSettingsScreen() {
  const router = useRouter();
  const { theme, isDark, toggleTheme } = useTheme();
  const { user, logout, updateUserProfile, updateRelationshipMode } = useAuthStore();
  const { resetOnboarding } = useAppStore();
  
  const [notificationsEnabled, setNotificationsEnabled] = useState(true);
  const [hapticEnabled, setHapticEnabled] = useState(true);
  const [showAccountModal, setShowAccountModal] = useState(false);
  const [showRelationshipModal, setShowRelationshipModal] = useState(false);
  const [editedName, setEditedName] = useState(user?.name || '');
  const [editedEmail, setEditedEmail] = useState(user?.email || '');

  // Relationship mode options
  const RELATIONSHIP_MODES = [
    { value: 'SAME_HOME', label: 'Same Home', description: 'Living together', icon: 'home' },
    { value: 'DAILY_IRL', label: 'Daily Meetup', description: 'Meet daily at work/study', icon: 'people' },
    { value: 'LONG_DISTANCE', label: 'Long Distance', description: 'Different cities', icon: 'airplane' },
  ];

  const handleBackPress = () => {
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    router.back();
  };

  const handleToggleTheme = () => {
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
    toggleTheme();
  };

  const handleToggleNotifications = () => {
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    setNotificationsEnabled(!notificationsEnabled);
  };

  const handleToggleHaptics = () => {
    if (hapticEnabled) {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    }
    setHapticEnabled(!hapticEnabled);
  };

  const handleSaveAccount = async () => {
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
    try {
      const success = await updateUserProfile({ 
        name: editedName, 
        email: editedEmail 
      });
      if (success) {
        setShowAccountModal(false);
        Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
        Alert.alert('Success', 'Account details updated successfully!');
      } else {
        Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);
        Alert.alert('Error', 'Failed to update account details');
      }
    } catch (error) {
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);
      Alert.alert('Error', 'Failed to update account details');
    }
  };

  const handleModeChange = async (mode: string) => {
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
    try {
      const success = await updateRelationshipMode(mode);
      if (success) {
        setShowRelationshipModal(false);
        Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
        Alert.alert('Success', 'Relationship mode updated successfully!');
      } else {
        Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);
        Alert.alert('Error', 'Failed to update relationship mode');
      }
    } catch (error) {
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);
      Alert.alert('Error', 'Failed to update relationship mode');
    }
  };

  const handleLogout = () => {
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
    Alert.alert(
      'Logout',
      'Are you sure you want to logout?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Logout',
          style: 'destructive',
          onPress: () => {
            Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
            logout();
          }
        },
      ]
    );
  };

  const handleResetOnboarding = () => {
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
    Alert.alert(
      'Reset Onboarding',
      'This will reset your onboarding flow. Are you sure?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Reset',
          style: 'destructive',
          onPress: () => {
            Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
            resetOnboarding();
          }
        },
      ]
    );
  };

  const openLink = async (url: string) => {
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    try {
      await Linking.openURL(url);
    } catch (error) {
      Alert.alert('Error', 'Unable to open link');
    }
  };

  const SettingItem = ({ 
    icon, 
    title, 
    subtitle, 
    onPress, 
    rightComponent, 
    showChevron = true,
    backgroundColor
  }: {
    icon: string;
    title: string;
    subtitle?: string;
    onPress?: () => void;
    rightComponent?: React.ReactNode;
    showChevron?: boolean;
    backgroundColor?: string;
  }) => (
    <TouchableOpacity
      style={[
        styles.settingItem,
        { 
          backgroundColor: backgroundColor || theme.surface,
          borderBottomColor: theme.border 
        }
      ]}
      onPress={onPress}
      activeOpacity={0.7}
    >
      <View style={styles.settingLeft}>
        <View style={[styles.iconContainer, { backgroundColor: theme.primary + '20' }]}>
          <Ionicons name={icon as any} size={20} color={theme.primary} />
        </View>
        <View style={styles.settingText}>
          <Text style={[styles.settingTitle, { color: theme.text }]}>{title}</Text>
          {subtitle && (
            <Text style={[styles.settingSubtitle, { color: theme.textSecondary }]}>
              {subtitle}
            </Text>
          )}
        </View>
      </View>
      <View style={styles.settingRight}>
        {rightComponent}
        {showChevron && !rightComponent && (
          <Ionicons name="chevron-forward" size={20} color={theme.textSecondary} />
        )}
      </View>
    </TouchableOpacity>
  );

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: theme.background }]}>
      {/* Header */}
      <View style={[styles.header, { backgroundColor: theme.surface, borderBottomColor: theme.border }]}>
        <TouchableOpacity
          style={styles.backButton}
          onPress={handleBackPress}
        >
          <Ionicons name="chevron-back" size={24} color={theme.text} />
        </TouchableOpacity>
        <Text style={[styles.headerTitle, { color: theme.text }]}>Settings</Text>
        <View style={styles.headerRight} />
      </View>

      <ScrollView style={styles.scrollView} showsVerticalScrollIndicator={false}>
        {/* Account Section */}
        <View style={styles.section}>
          <Text style={[styles.sectionHeader, { color: theme.textSecondary }]}>ACCOUNT</Text>
          
          <SettingItem
            icon="person"
            title="Account Information"
            subtitle={user?.email || 'Not logged in'}
            onPress={() => {
              setEditedName(user?.name || '');
              setEditedEmail(user?.email || '');
              setShowAccountModal(true);
            }}
          />
          
          <SettingItem
            icon="heart"
            title="Relationship Mode"
            subtitle={user?.relationship_mode?.replace('_', ' ') || 'Not set'}
            onPress={() => setShowRelationshipModal(true)}
          />
          
          <SettingItem
            icon="heart"
            title="Partner Profile"
            subtitle="Manage your partner's details"
            onPress={() => router.push('/tabs/profile')}
          />
          
          <SettingItem
            icon="diamond"
            title="Subscription"
            subtitle="₹99/month or ₹948/year - Premium features"
            onPress={() => Alert.alert('Subscription', 'Premium subscription: ₹99 per month or ₹948 per year. Get AI-generated tasks, advanced features, and priority support!')}
          />
        </View>

        {/* Preferences Section */}
        <View style={styles.section}>
          <Text style={[styles.sectionHeader, { color: theme.textSecondary }]}>PREFERENCES</Text>
          
          <SettingItem
            icon="moon"
            title="Dark Mode"
            subtitle={isDark ? 'Enabled' : 'Disabled'}
            rightComponent={
              <Switch
                value={isDark}
                onValueChange={handleToggleTheme}
                trackColor={{ false: theme.border, true: theme.primary + '40' }}
                thumbColor={isDark ? theme.primary : '#f4f3f4'}
              />
            }
            showChevron={false}
          />
          
          <SettingItem
            icon="notifications"
            title="Push Notifications"
            subtitle="Receive task reminders and updates"
            rightComponent={
              <Switch
                value={notificationsEnabled}
                onValueChange={handleToggleNotifications}
                trackColor={{ false: theme.border, true: theme.primary + '40' }}
                thumbColor={notificationsEnabled ? theme.primary : '#f4f3f4'}
              />
            }
            showChevron={false}
          />
          
          <SettingItem
            icon="phone-portrait"
            title="Haptic Feedback"
            subtitle="Enable vibrations for interactions"
            rightComponent={
              <Switch
                value={hapticEnabled}
                onValueChange={handleToggleHaptics}
                trackColor={{ false: theme.border, true: theme.primary + '40' }}
                thumbColor={hapticEnabled ? theme.primary : '#f4f3f4'}
              />
            }
            showChevron={false}
          />
          
          <SettingItem
            icon="language"
            title="Language"
            subtitle="English"
            onPress={() => Alert.alert('Language', 'Currently only English is supported')}
          />
          
          <SettingItem
            icon="calendar"
            title="Date Format"
            subtitle="DD/MM/YYYY"
            onPress={() => Alert.alert('Date Format', 'Using DD/MM/YYYY format as requested')}
          />
        </View>

        {/* App Section */}
        <View style={styles.section}>
          <Text style={[styles.sectionHeader, { color: theme.textSecondary }]}>APP</Text>
          
          <SettingItem
            icon="refresh"
            title="Reset Onboarding"
            subtitle="Go through the setup process again"
            onPress={handleResetOnboarding}
          />
          
          <SettingItem
            icon="help-circle"
            title="Help & Support"
            subtitle="Get help or contact support"
            onPress={() => Alert.alert('Support', 'For support, please email us at support@pookie4u.com')}
          />
          
          <SettingItem
            icon="document-text"
            title="Privacy Policy"
            subtitle="View our privacy policy"
            onPress={() => openLink('https://pookie4u.com/privacy')}
          />
          
          <SettingItem
            icon="document-text"
            title="Terms of Service"
            subtitle="View terms and conditions"
            onPress={() => openLink('https://pookie4u.com/terms')}
          />
        </View>

        {/* Danger Zone */}
        <View style={styles.section}>
          <Text style={[styles.sectionHeader, { color: theme.error }]}>DANGER ZONE</Text>
          
          <SettingItem
            icon="log-out"
            title="Logout"
            subtitle="Sign out of your account"
            onPress={handleLogout}
            backgroundColor={theme.error + '10'}
            showChevron={false}
          />
        </View>

        {/* App Info */}
        <View style={[styles.appInfo, { borderTopColor: theme.border }]}>
          <Text style={[styles.appInfoText, { color: theme.textSecondary }]}>
            Pookie4u v1.0.0
          </Text>
          <Text style={[styles.appInfoText, { color: theme.textSecondary }]}>
            Made with ❤️ for couples
          </Text>
        </View>
      </ScrollView>

      {/* Account Edit Modal */}
      <Modal
        visible={showAccountModal}
        animationType="slide"
        presentationStyle="pageSheet"
        onRequestClose={() => setShowAccountModal(false)}
      >
        <SafeAreaView style={[styles.modalContainer, { backgroundColor: theme.background }]}>
          <View style={[styles.modalHeader, { backgroundColor: theme.surface, borderBottomColor: theme.border }]}>
            <TouchableOpacity 
              style={styles.closeButton} 
              onPress={() => setShowAccountModal(false)}
            >
              <Ionicons name="close" size={24} color={theme.text} />
            </TouchableOpacity>
            <Text style={[styles.modalTitle, { color: theme.text }]}>Edit Account</Text>
            <TouchableOpacity style={styles.saveButton} onPress={handleSaveAccount}>
              <Text style={[styles.saveButtonText, { color: theme.primary }]}>Save</Text>
            </TouchableOpacity>
          </View>

          <View style={styles.modalContent}>
            <View style={[styles.inputContainer, { backgroundColor: theme.surface }]}>
              <Text style={[styles.inputLabel, { color: theme.text }]}>Name</Text>
              <TextInput
                style={[styles.textInput, { color: theme.text, borderColor: theme.border }]}
                value={editedName}
                onChangeText={setEditedName}
                placeholder="Your name"
                placeholderTextColor={theme.textSecondary}
              />
            </View>

            <View style={[styles.inputContainer, { backgroundColor: theme.surface }]}>
              <Text style={[styles.inputLabel, { color: theme.text }]}>Email</Text>
              <TextInput
                style={[styles.textInput, { color: theme.text, borderColor: theme.border }]}
                value={editedEmail}
                onChangeText={setEditedEmail}
                placeholder="Your email"
                placeholderTextColor={theme.textSecondary}
                keyboardType="email-address"
                autoCapitalize="none"
              />
            </View>
          </View>
        </SafeAreaView>
      </Modal>

      {/* Relationship Mode Modal */}
      <Modal
        visible={showRelationshipModal}
        animationType="slide"
        presentationStyle="pageSheet"
        onRequestClose={() => setShowRelationshipModal(false)}
      >
        <SafeAreaView style={[styles.modalContainer, { backgroundColor: theme.background }]}>
          <View style={[styles.modalHeader, { backgroundColor: theme.surface, borderBottomColor: theme.border }]}>
            <TouchableOpacity 
              style={styles.closeButton} 
              onPress={() => setShowRelationshipModal(false)}
            >
              <Ionicons name="close" size={24} color={theme.text} />
            </TouchableOpacity>
            <Text style={[styles.modalTitle, { color: theme.text }]}>Relationship Mode</Text>
            <View style={styles.headerRight} />
          </View>

          <View style={styles.modalContent}>
            {RELATIONSHIP_MODES.map((mode) => (
              <TouchableOpacity
                key={mode.value}
                style={[
                  styles.relationshipOption,
                  { 
                    backgroundColor: theme.surface,
                    borderColor: user?.relationship_mode === mode.value ? theme.primary : theme.border
                  }
                ]}
                onPress={() => handleModeChange(mode.value)}
              >
                <View style={[styles.relationshipIcon, { backgroundColor: theme.primary + '20' }]}>
                  <Ionicons name={mode.icon as any} size={24} color={theme.primary} />
                </View>
                <View style={styles.relationshipText}>
                  <Text style={[styles.relationshipLabel, { color: theme.text }]}>
                    {mode.label}
                  </Text>
                  <Text style={[styles.relationshipDescription, { color: theme.textSecondary }]}>
                    {mode.description}
                  </Text>
                </View>
                {user?.relationship_mode === mode.value && (
                  <Ionicons name="checkmark-circle" size={24} color={theme.primary} />
                )}
              </TouchableOpacity>
            ))}
          </View>
        </SafeAreaView>
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
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingVertical: 12,
    paddingTop: Platform.OS === 'ios' ? 12 : 20,
    borderBottomWidth: 1,
  },
  backButton: {
    width: 40,
    height: 40,
    alignItems: 'center',
    justifyContent: 'center',
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: 'bold',
  },
  headerRight: {
    width: 40,
  },
  scrollView: {
    flex: 1,
  },
  section: {
    marginTop: 24,
  },
  sectionHeader: {
    fontSize: 13,
    fontWeight: '600',
    marginLeft: 20,
    marginBottom: 8,
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  settingItem: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: 16,
    paddingHorizontal: 20,
    borderBottomWidth: StyleSheet.hairlineWidth,
  },
  settingLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  iconContainer: {
    width: 32,
    height: 32,
    borderRadius: 8,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 12,
  },
  settingText: {
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
  settingRight: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  appInfo: {
    alignItems: 'center',
    paddingTop: 24,
    paddingBottom: 40,
    marginTop: 24,
    borderTopWidth: StyleSheet.hairlineWidth,
    marginHorizontal: 20,
  },
  appInfoText: {
    fontSize: 12,
    marginBottom: 4,
  },
  modalContainer: {
    flex: 1,
  },
  modalHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderBottomWidth: 1,
  },
  closeButton: {
    width: 40,
    height: 40,
    alignItems: 'center',
    justifyContent: 'center',
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: 'bold',
  },
  saveButton: {
    paddingHorizontal: 16,
    paddingVertical: 8,
  },
  saveButtonText: {
    fontSize: 16,
    fontWeight: '600',
  },
  modalContent: {
    flex: 1,
    padding: 20,
  },
  inputContainer: {
    marginBottom: 20,
    borderRadius: 12,
    padding: 16,
  },
  inputLabel: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 8,
  },
  textInput: {
    borderWidth: 1,
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
  },
  relationshipOption: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    marginBottom: 12,
    borderRadius: 12,
    borderWidth: 2,
  },
  relationshipIcon: {
    width: 48,
    height: 48,
    borderRadius: 24,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 16,
  },
  relationshipText: {
    flex: 1,
  },
  relationshipLabel: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 2,
  },
  relationshipDescription: {
    fontSize: 14,
  },
});