import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  Share,
  Linking,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import Animated, { FadeInUp } from 'react-native-reanimated';

import { AnimatedCard } from '../components/AnimatedCard';
import { useAuthStore } from '../stores/useAuthStore';
import { useAppStore } from '../stores/useAppStore';

const THEME_OPTIONS = [
  { value: 'auto', label: 'Auto', icon: 'phone-portrait' },
  { value: 'light', label: 'Light', icon: 'sunny' },
  { value: 'dark', label: 'Dark', icon: 'moon' },
];

export default function SettingsScreen() {
  const { user, logout } = useAuthStore();
  const { theme, updateSettings } = useAppStore();
  const [selectedTheme, setSelectedTheme] = useState(theme || 'light');

  const handleShare = async () => {
    try {
      await Share.share({
        message: 'Check out Pookie4u - The relationship app that helps couples strengthen their bond through daily romantic tasks! Download now and win real prizes! 💕',
        url: 'https://pookie4u.app',
      });
    } catch (error) {
      console.error('Error sharing:', error);
    }
  };

  const handleLogout = () => {
    Alert.alert(
      'Logout',
      'Are you sure you want to logout?',
      [
        { text: 'Cancel', style: 'cancel' },
        { text: 'Logout', style: 'destructive', onPress: logout },
      ]
    );
  };

  const handleThemeChange = (newTheme) => {
    setSelectedTheme(newTheme);
    updateSettings({ theme: newTheme });
  };

  const renderSettingItem = ({ icon, title, subtitle, onPress, delay = 0 }) => (
    <Animated.View entering={FadeInUp.delay(delay).springify()}>
      <TouchableOpacity style={styles.settingItem} onPress={onPress}>
        <View style={styles.settingIcon}>
          <Ionicons name={icon} size={22} color="#FF69B4" />
        </View>
        <View style={styles.settingContent}>
          <Text style={styles.settingTitle}>{title}</Text>
          {subtitle && <Text style={styles.settingSubtitle}>{subtitle}</Text>}
        </View>
        <Ionicons name="chevron-forward" size={20} color="#ccc" />
      </TouchableOpacity>
    </Animated.View>
  );

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Settings ⚙️</Text>
      </View>

      <ScrollView style={styles.scrollView} showsVerticalScrollIndicator={false}>
        {/* User Info Section */}
        <Animated.View entering={FadeInUp.delay(100).springify()}>
          <AnimatedCard style={styles.section} delay={100}>
            <Text style={styles.sectionTitle}>Account Information</Text>
            
            <View style={styles.userInfo}>
              <View style={styles.userInfoItem}>
                <Text style={styles.userInfoLabel}>Name:</Text>
                <Text style={styles.userInfoValue}>{user?.name || 'Not set'}</Text>
              </View>
              <View style={styles.userInfoItem}>
                <Text style={styles.userInfoLabel}>Email:</Text>
                <Text style={styles.userInfoValue}>{user?.email || 'Not set'}</Text>
              </View>
              <View style={styles.userInfoItem}>
                <Text style={styles.userInfoLabel}>Phone:</Text>
                <Text style={styles.userInfoValue}>Not provided</Text>
              </View>
            </View>
          </AnimatedCard>
        </Animated.View>

        {/* Theme Section */}
        <Animated.View entering={FadeInUp.delay(200).springify()}>
          <AnimatedCard style={styles.section} delay={200}>
            <Text style={styles.sectionTitle}>Appearance</Text>
            
            <View style={styles.themeOptions}>
              {THEME_OPTIONS.map((option) => (
                <TouchableOpacity
                  key={option.value}
                  style={[
                    styles.themeOption,
                    selectedTheme === option.value && styles.selectedThemeOption
                  ]}
                  onPress={() => handleThemeChange(option.value)}
                >
                  <Ionicons 
                    name={option.icon} 
                    size={20} 
                    color={selectedTheme === option.value ? '#fff' : '#FF69B4'} 
                  />
                  <Text style={[
                    styles.themeOptionText,
                    selectedTheme === option.value && styles.selectedThemeOptionText
                  ]}>
                    {option.label}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>
          </AnimatedCard>
        </Animated.View>

        {/* Subscription Section */}
        <Animated.View entering={FadeInUp.delay(300).springify()}>
          <AnimatedCard style={styles.section} delay={300}>
            <Text style={styles.sectionTitle}>Subscription</Text>
            
            <View style={styles.subscriptionInfo}>
              <View style={styles.subscriptionStatus}>
                <Ionicons name="time" size={24} color="#FF9800" />
                <View style={styles.subscriptionDetails}>
                  <Text style={styles.subscriptionStatusText}>Free Trial - 14 days left</Text>
                  <Text style={styles.subscriptionPrice}>₹79/month after trial</Text>
                </View>
              </View>
            </View>
          </AnimatedCard>
        </Animated.View>

        {/* App Actions */}
        <Animated.View entering={FadeInUp.delay(400).springify()}>
          <AnimatedCard style={styles.section} delay={400}>
            <Text style={styles.sectionTitle}>Share & Support</Text>
            
            {renderSettingItem({
              icon: 'share',
              title: 'Share App',
              subtitle: 'Invite friends to join Pookie4u',
              onPress: handleShare,
              delay: 450
            })}

            {renderSettingItem({
              icon: 'help-circle',
              title: 'Help & Support',
              subtitle: 'Contact us for help',
              onPress: () => Linking.openURL('mailto:support@pookie4u.app'),
              delay: 500
            })}
          </AnimatedCard>
        </Animated.View>

        {/* Privacy & Legal */}
        <Animated.View entering={FadeInUp.delay(500).springify()}>
          <AnimatedCard style={styles.section} delay={500}>
            <Text style={styles.sectionTitle}>Privacy & Legal</Text>
            
            {renderSettingItem({
              icon: 'shield-checkmark',
              title: 'Privacy Policy',
              subtitle: 'How we protect your data',
              onPress: () => Linking.openURL('https://pookie4u.app/privacy'),
              delay: 550
            })}

            {renderSettingItem({
              icon: 'document-text',
              title: 'Terms of Service',
              subtitle: 'App usage terms',
              onPress: () => Linking.openURL('https://pookie4u.app/terms'),
              delay: 600
            })}
          </AnimatedCard>
        </Animated.View>

        {/* Logout */}
        <Animated.View entering={FadeInUp.delay(600).springify()}>
          <AnimatedCard style={styles.section} delay={600}>
            {renderSettingItem({
              icon: 'log-out',
              title: 'Logout',
              subtitle: 'Sign out of your account',
              onPress: handleLogout,
              delay: 650
            })}
          </AnimatedCard>
        </Animated.View>

        <View style={{ height: 50 }} />
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8f9fa',
  },
  header: {
    padding: 20,
    backgroundColor: '#fff',
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
  },
  scrollView: {
    flex: 1,
  },
  section: {
    margin: 20,
    marginBottom: 10,
    padding: 20,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 15,
  },
  userInfo: {
    gap: 12,
  },
  userInfoItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 8,
  },
  userInfoLabel: {
    fontSize: 14,
    color: '#666',
    fontWeight: '600',
  },
  userInfoValue: {
    fontSize: 14,
    color: '#333',
    fontWeight: '500',
  },
  themeOptions: {
    flexDirection: 'row',
    gap: 10,
  },
  themeOption: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 12,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#e0e0e0',
    gap: 8,
  },
  selectedThemeOption: {
    backgroundColor: '#FF69B4',
    borderColor: '#FF69B4',
  },
  themeOptionText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
  },
  selectedThemeOptionText: {
    color: '#fff',
  },
  subscriptionInfo: {
    gap: 15,
  },
  subscriptionStatus: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  subscriptionDetails: {
    flex: 1,
  },
  subscriptionStatusText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 4,
  },
  subscriptionPrice: {
    fontSize: 14,
    color: '#666',
  },
  settingItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 15,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  settingIcon: {
    width: 40,
    alignItems: 'center',
    marginRight: 15,
  },
  settingContent: {
    flex: 1,
  },
  settingTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 2,
  },
  settingSubtitle: {
    fontSize: 12,
    color: '#666',
  },
});