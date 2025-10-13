import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  TextInput,
  Alert,
  KeyboardAvoidingView,
  Platform,
  Image,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import * as ImagePicker from 'expo-image-picker';
import { useAuthStore } from '../stores/useAuthStore';
import { useGameStore } from '../stores/useGameStore';
import { useAppStore } from '../stores/useAppStore';
import { useTheme } from '../contexts/ThemeContext';

export default function ProfileContent() {
  const { user, logout, updatePartnerProfile, updateRelationshipMode, updateProfileImage } = useAuthStore();
  const { totalPoints, currentLevel, currentStreak, longestStreak, tasksCompleted, badges, loadPersistedData } = useGameStore();
  const { resetOnboarding } = useAppStore();
  const { theme } = useTheme();

  const [editMode, setEditMode] = useState(false);
  const [profileImage, setProfileImage] = useState(user?.profile_image || null);
  const [showModeSelector, setShowModeSelector] = useState(false);
  const [partnerData, setPartnerData] = useState({
    name: user?.partner_profile?.name || '',
    birthday: user?.partner_profile?.birthday || '',
    anniversary: user?.partner_profile?.anniversary || '',
    favorite_color: user?.partner_profile?.favorite_color || '',
    favorite_food: user?.partner_profile?.favorite_food || '',
    favorite_flower: user?.partner_profile?.favorite_flower || '',
    favorite_brand: user?.partner_profile?.favorite_brand || '',
    favorite_perfume: user?.partner_profile?.favorite_perfume || '',
    dress_size: user?.partner_profile?.dress_size || '',
    top_size: user?.partner_profile?.top_size || '',
    jeans_size: user?.partner_profile?.jeans_size || '',
    ring_size: user?.partner_profile?.ring_size || '',
    additional_notes: user?.partner_profile?.additional_notes || '',
  });

  // Initialize game store data
  useEffect(() => {
    loadPersistedData();
  }, []);

  // Image picker function for gallery
  const pickImageFromGallery = async () => {
    const permissionResult = await ImagePicker.requestMediaLibraryPermissionsAsync();
    
    if (permissionResult.granted === false) {
      Alert.alert('Permission required', 'Permission to access camera roll is required!');
      return;
    }

    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      aspect: [1, 1],
      quality: 0.8,
      base64: true,
    });

    if (!result.canceled) {
      const imageBase64 = `data:image/jpeg;base64,${result.assets[0].base64}`;
      setProfileImage(imageBase64);
      await saveProfileImage(imageBase64);
    }
  };

  // Image picker function for camera
  const pickImageFromCamera = async () => {
    const permissionResult = await ImagePicker.requestCameraPermissionsAsync();
    
    if (permissionResult.granted === false) {
      Alert.alert('Permission required', 'Permission to access camera is required!');
      return;
    }

    const result = await ImagePicker.launchCameraAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      aspect: [1, 1],
      quality: 0.8,
      base64: true,
    });

    if (!result.canceled) {
      const imageBase64 = `data:image/jpeg;base64,${result.assets[0].base64}`;
      setProfileImage(imageBase64);
      await saveProfileImage(imageBase64);
    }
  };

  // Save profile image to backend
  const saveProfileImage = async (imageBase64) => {
    try {
      const success = await updateProfileImage(imageBase64);
      if (success) {
        Alert.alert('Success', 'Profile picture updated successfully!');
      } else {
        Alert.alert('Error', 'Failed to update profile picture. Please try again.');
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to update profile picture. Please try again.');
    }
  };

  // Show image selection options
  const showImagePicker = () => {
    Alert.alert(
      'Select Profile Picture',
      'Choose how you want to select your profile picture',
      [
        { text: 'Camera', onPress: pickImageFromCamera },
        { text: 'Gallery', onPress: pickImageFromGallery },
        { text: 'Cancel', style: 'cancel' },
      ]
    );
  };

  // Relationship mode options
  const RELATIONSHIP_MODES = [
    { value: 'SAME_HOME', label: 'Same Home', description: 'Living together' },
    { value: 'DAILY_IRL', label: 'Daily Meetup', description: 'Meet daily at work/study' },
    { value: 'LONG_DISTANCE', label: 'Long Distance', description: 'Different cities' },
  ];

  // Get user achievement tag
  const getUserTag = () => {
    if (totalPoints > 1000) return 'Romance Expert';
    if (longestStreak >= 30) return 'Consistency King';
    if (tasksCompleted >= 100) return 'Task Master';
    if (currentStreak >= 7) return 'Week Warrior';
    if (totalPoints > 500) return 'Golden Boyfriend';
    return 'Rising Star';
  };

  const handleModeChange = async (mode) => {
    // Check if the selected mode is the same as current mode
    if (user?.relationship_mode === mode) {
      // Same mode selected, just close the selector without any action
      setShowModeSelector(false);
      return;
    }

    // Different mode selected, update it
    const success = await updateRelationshipMode(mode);
    if (success) {
      setShowModeSelector(false);
      Alert.alert('Success', 'Relationship mode updated successfully! Your tasks and messages will now match your new relationship mode.');
    }
  };

  // Handle dismiss without selection (tap outside)
  const handleDismissSelector = () => {
    setShowModeSelector(false);
  };

  const handleSaveProfile = async () => {
    const success = await updatePartnerProfile(partnerData);
    if (success) {
      setEditMode(false);
      Alert.alert('Success', 'Partner profile updated successfully!');
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

  const getBadgeIcon = (badge: string) => {
    switch (badge) {
      case 'First 10 Tasks': return 'star';
      case 'Week Warrior': return 'flash';
      case 'Level 5 Master': return 'trophy';
      case 'Month Master': return 'calendar';
      case 'Half Century': return 'medal';
      case 'Task Master': return 'ribbon';
      default: return 'award';
    }
  };

  return (
    <View style={[styles.container, { backgroundColor: theme.background }]}>
      <KeyboardAvoidingView 
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.keyboardView}
      >
        <ScrollView style={styles.scrollView}>
          {/* User Profile Header */}
          <View style={[styles.profileHeader, { backgroundColor: theme.surface }]}>
            <TouchableOpacity style={[styles.avatarContainer, { backgroundColor: theme.primary + '20', borderColor: theme.primary }]} onPress={showImagePicker}>
              {profileImage ? (
                <Image source={{ uri: profileImage }} style={styles.avatarImage} />
              ) : (
                <Ionicons name="person" size={40} color={theme.primary} />
              )}
              <View style={[styles.cameraIcon, { backgroundColor: theme.primary }]}>
                <Ionicons name="camera" size={16} color="#fff" />
              </View>
            </TouchableOpacity>
            <Text style={[styles.userName, { color: theme.text }]}>{user?.name}</Text>
            <Text style={[styles.userEmail, { color: theme.textSecondary }]}>{user?.email}</Text>
            <View style={styles.userTagContainer}>
              <Text style={[styles.userTag, { backgroundColor: theme.primary }]}>{getUserTag()}</Text>
            </View>
            <TouchableOpacity 
              style={[styles.relationshipModeButton, { backgroundColor: theme.primary + '20' }]}
              onPress={() => setShowModeSelector(!showModeSelector)}
            >
              <Text style={[styles.relationshipMode, { color: theme.primary }]}>
                {user?.relationship_mode?.replace('_', ' ')} Mode
              </Text>
              <Ionicons name="chevron-down" size={16} color={theme.primary} />
            </TouchableOpacity>
            
            {/* Relationship Mode Selector */}
            {showModeSelector && (
              <TouchableOpacity 
                style={styles.selectorOverlay} 
                activeOpacity={1} 
                onPress={handleDismissSelector}
              >
                <View style={[styles.modeSelector, { backgroundColor: theme.surface }]}>
                  <View style={styles.selectorHeader}>
                    <Text style={[styles.selectorTitle, { color: theme.text }]}>Choose Relationship Mode</Text>
                    <TouchableOpacity onPress={handleDismissSelector} style={styles.dismissButton}>
                      <Ionicons name="close" size={20} color={theme.textSecondary} />
                    </TouchableOpacity>
                  </View>
                  {RELATIONSHIP_MODES.map((mode) => (
                    <TouchableOpacity
                      key={mode.value}
                      style={[
                        styles.modeOption,
                        { borderBottomColor: theme.border },
                        user?.relationship_mode === mode.value && { backgroundColor: theme.primary + '20' }
                      ]}
                      onPress={() => handleModeChange(mode.value)}
                    >
                      <View style={styles.modeOptionContent}>
                        <Text style={[
                          styles.modeLabel,
                          { color: theme.text },
                          user?.relationship_mode === mode.value && { color: theme.primary }
                        ]}>
                          {mode.label}
                        </Text>
                        <Text style={[styles.modeDescription, { color: theme.textSecondary }]}>{mode.description}</Text>
                      </View>
                      {user?.relationship_mode === mode.value && (
                        <Ionicons name="checkmark-circle" size={20} color={theme.primary} />
                      )}
                    </TouchableOpacity>
                  ))}
                </View>
              </TouchableOpacity>
            )}
          </View>

          {/* Stats Overview */}
          <View style={styles.statsContainer}>
            <View style={[styles.statCard, { backgroundColor: theme.surface }]}>
              <Ionicons name="star" size={24} color="#FFD700" />
              <Text style={[styles.statNumber, { color: theme.text }]}>{totalPoints}</Text>
              <Text style={[styles.statLabel, { color: theme.textSecondary }]}>Total Points</Text>
            </View>
            <View style={[styles.statCard, { backgroundColor: theme.surface }]}>
              <Ionicons name="trophy" size={24} color={theme.primary} />
              <Text style={[styles.statNumber, { color: theme.text }]}>Level {currentLevel}</Text>
              <Text style={[styles.statLabel, { color: theme.textSecondary }]}>Current Level</Text>
            </View>
            <View style={[styles.statCard, { backgroundColor: theme.surface }]}>
              <Ionicons name="flash" size={24} color="#FF4500" />
              <Text style={[styles.statNumber, { color: theme.text }]}>{currentStreak}</Text>
              <Text style={[styles.statLabel, { color: theme.textSecondary }]}>Current Streak</Text>
            </View>
          </View>

          {/* Achievement Stats */}
          <View style={styles.section}>
            <Text style={[styles.sectionTitle, { color: theme.text }]}>Your Achievements 🏆</Text>
            <View style={[styles.achievementCard, { backgroundColor: theme.surface }]}>
              <View style={styles.achievementRow}>
                <Text style={[styles.achievementLabel, { color: theme.textSecondary }]}>Tasks Completed:</Text>
                <Text style={[styles.achievementValue, { color: theme.primary }]}>{tasksCompleted}</Text>
              </View>
              <View style={styles.achievementRow}>
                <Text style={[styles.achievementLabel, { color: theme.textSecondary }]}>Longest Streak:</Text>
                <Text style={[styles.achievementValue, { color: theme.primary }]}>{longestStreak} days</Text>
              </View>
              <View style={styles.achievementRow}>
                <Text style={[styles.achievementLabel, { color: theme.textSecondary }]}>Badges Earned:</Text>
                <Text style={[styles.achievementValue, { color: theme.primary }]}>{badges.length}</Text>
              </View>
            </View>
          </View>

          {/* Badges */}
          {badges.length > 0 && (
            <View style={styles.section}>
              <Text style={[styles.sectionTitle, { color: theme.text }]}>Your Badges 🏅</Text>
              <View style={styles.badgesContainer}>
                {badges.map((badge, index) => (
                  <View key={index} style={[styles.badge, { backgroundColor: theme.surface }]}>
                    <Ionicons name={getBadgeIcon(badge)} size={20} color={theme.primary} />
                    <Text style={[styles.badgeText, { color: theme.text }]}>{badge}</Text>
                  </View>
                ))}
              </View>
            </View>
          )}

          {/* Partner Profile */}
          <View style={styles.section}>
            <View style={styles.sectionHeader}>
              <Text style={[styles.sectionTitle, { color: theme.text }]}>Partner's Profile 💕</Text>
              <TouchableOpacity
                style={styles.editButton}
                onPress={() => setEditMode(!editMode)}
              >
                <Ionicons name={editMode ? "close" : "pencil"} size={20} color={theme.primary} />
                <Text style={[styles.editButtonText, { color: theme.primary }]}>
                  {editMode ? 'Cancel' : 'Edit'}
                </Text>
              </TouchableOpacity>
            </View>

            <View style={[styles.partnerCard, { backgroundColor: theme.surface }]}>
              <View style={styles.inputRow}>
                <Text style={[styles.inputLabel, { color: theme.text }]}>Name:</Text>
                {editMode ? (
                  <TextInput
                    style={[styles.input, { backgroundColor: theme.background, color: theme.text, borderColor: theme.border }]}
                    value={partnerData.name}
                    onChangeText={(text) => setPartnerData({...partnerData, name: text})}
                    placeholder="Partner's name"
                    placeholderTextColor={theme.textSecondary}
                  />
                ) : (
                  <Text style={[styles.inputValue, { color: theme.textSecondary }]}>{partnerData.name || 'Not set'}</Text>
                )}
              </View>

              <View style={styles.inputRow}>
                <Text style={[styles.inputLabel, { color: theme.text }]}>Birthday:</Text>
                {editMode ? (
                  <TextInput
                    style={[styles.input, { backgroundColor: theme.background, color: theme.text, borderColor: theme.border }]}
                    value={partnerData.birthday}
                    onChangeText={(text) => setPartnerData({...partnerData, birthday: text})}
                    placeholder="DD/MM/YYYY"
                    placeholderTextColor={theme.textSecondary}
                  />
                ) : (
                  <Text style={[styles.inputValue, { color: theme.textSecondary }]}>{partnerData.birthday || 'Not set'}</Text>
                )}
              </View>

              <View style={styles.inputRow}>
                <Text style={[styles.inputLabel, { color: theme.text }]}>Anniversary:</Text>
                {editMode ? (
                  <TextInput
                    style={[styles.input, { backgroundColor: theme.background, color: theme.text, borderColor: theme.border }]}
                    value={partnerData.anniversary}
                    onChangeText={(text) => setPartnerData({...partnerData, anniversary: text})}
                    placeholder="DD/MM/YYYY"
                    placeholderTextColor={theme.textSecondary}
                  />
                ) : (
                  <Text style={[styles.inputValue, { color: theme.textSecondary }]}>{partnerData.anniversary || 'Not set'}</Text>
                )}
              </View>

              <View style={styles.inputRow}>
                <Text style={[styles.inputLabel, { color: theme.text }]}>Favorite Color:</Text>
                {editMode ? (
                  <TextInput
                    style={[styles.input, { backgroundColor: theme.background, color: theme.text, borderColor: theme.border }]}
                    value={partnerData.favorite_color}
                    onChangeText={(text) => setPartnerData({...partnerData, favorite_color: text})}
                    placeholder="e.g., Blue"
                    placeholderTextColor={theme.textSecondary}
                  />
                ) : (
                  <Text style={[styles.inputValue, { color: theme.textSecondary }]}>{partnerData.favorite_color || 'Not set'}</Text>
                )}
              </View>

              <View style={styles.inputRow}>
                <Text style={[styles.inputLabel, { color: theme.text }]}>Favorite Food:</Text>
                {editMode ? (
                  <TextInput
                    style={[styles.input, { backgroundColor: theme.background, color: theme.text, borderColor: theme.border }]}
                    value={partnerData.favorite_food}
                    onChangeText={(text) => setPartnerData({...partnerData, favorite_food: text})}
                    placeholder="e.g., Pizza"
                    placeholderTextColor={theme.textSecondary}
                  />
                ) : (
                  <Text style={[styles.inputValue, { color: theme.textSecondary }]}>{partnerData.favorite_food || 'Not set'}</Text>
                )}
              </View>

              <View style={styles.inputRow}>
                <Text style={[styles.inputLabel, { color: theme.text }]}>Favorite Flower:</Text>
                {editMode ? (
                  <TextInput
                    style={[styles.input, { backgroundColor: theme.background, color: theme.text, borderColor: theme.border }]}
                    value={partnerData.favorite_flower}
                    onChangeText={(text) => setPartnerData({...partnerData, favorite_flower: text})}
                    placeholder="e.g., Rose"
                    placeholderTextColor={theme.textSecondary}
                  />
                ) : (
                  <Text style={[styles.inputValue, { color: theme.textSecondary }]}>{partnerData.favorite_flower || 'Not set'}</Text>
                )}
              </View>

              <View style={styles.inputRow}>
                <Text style={[styles.inputLabel, { color: theme.text }]}>Favorite Brand:</Text>
                {editMode ? (
                  <TextInput
                    style={[styles.input, { backgroundColor: theme.background, color: theme.text, borderColor: theme.border }]}
                    value={partnerData.favorite_brand}
                    onChangeText={(text) => setPartnerData({...partnerData, favorite_brand: text})}
                    placeholder="e.g., Nike"
                    placeholderTextColor={theme.textSecondary}
                  />
                ) : (
                  <Text style={[styles.inputValue, { color: theme.textSecondary }]}>{partnerData.favorite_brand || 'Not set'}</Text>
                )}
              </View>

              <View style={styles.inputRow}>
                <Text style={[styles.inputLabel, { color: theme.text }]}>Perfume Preference:</Text>
                {editMode ? (
                  <TextInput
                    style={[styles.input, { backgroundColor: theme.background, color: theme.text, borderColor: theme.border }]}
                    value={partnerData.favorite_perfume}
                    onChangeText={(text) => setPartnerData({...partnerData, favorite_perfume: text})}
                    placeholder="e.g., Floral, Woody"
                    placeholderTextColor={theme.textSecondary}
                  />
                ) : (
                  <Text style={[styles.inputValue, { color: theme.textSecondary }]}>{partnerData.favorite_perfume || 'Not set'}</Text>
                )}
              </View>

              {/* Sizing Information */}
              <Text style={[styles.subSectionTitle, { color: theme.primary }]}>Sizing Information 👗</Text>

              <View style={styles.inputRow}>
                <Text style={[styles.inputLabel, { color: theme.text }]}>Dress Size:</Text>
                {editMode ? (
                  <TextInput
                    style={[styles.input, { backgroundColor: theme.background, color: theme.text, borderColor: theme.border }]}
                    value={partnerData.dress_size}
                    onChangeText={(text) => setPartnerData({...partnerData, dress_size: text})}
                    placeholder="e.g., S, M, L"
                    placeholderTextColor={theme.textSecondary}
                  />
                ) : (
                  <Text style={[styles.inputValue, { color: theme.textSecondary }]}>{partnerData.dress_size || 'Not set'}</Text>
                )}
              </View>

              <View style={styles.inputRow}>
                <Text style={[styles.inputLabel, { color: theme.text }]}>Top Size:</Text>
                {editMode ? (
                  <TextInput
                    style={[styles.input, { backgroundColor: theme.background, color: theme.text, borderColor: theme.border }]}
                    value={partnerData.top_size}
                    onChangeText={(text) => setPartnerData({...partnerData, top_size: text})}
                    placeholder="e.g., S, M, L"
                    placeholderTextColor={theme.textSecondary}
                  />
                ) : (
                  <Text style={[styles.inputValue, { color: theme.textSecondary }]}>{partnerData.top_size || 'Not set'}</Text>
                )}
              </View>

              <View style={styles.inputRow}>
                <Text style={[styles.inputLabel, { color: theme.text }]}>Jeans Size:</Text>
                {editMode ? (
                  <TextInput
                    style={[styles.input, { backgroundColor: theme.background, color: theme.text, borderColor: theme.border }]}
                    value={partnerData.jeans_size}
                    onChangeText={(text) => setPartnerData({...partnerData, jeans_size: text})}
                    placeholder="e.g., 28, 30, 32"
                    placeholderTextColor={theme.textSecondary}
                  />
                ) : (
                  <Text style={[styles.inputValue, { color: theme.textSecondary }]}>{partnerData.jeans_size || 'Not set'}</Text>
                )}
              </View>

              <View style={styles.inputRow}>
                <Text style={[styles.inputLabel, { color: theme.text }]}>Ring Size:</Text>
                {editMode ? (
                  <TextInput
                    style={[styles.input, { backgroundColor: theme.background, color: theme.text, borderColor: theme.border }]}
                    value={partnerData.ring_size}
                    onChangeText={(text) => setPartnerData({...partnerData, ring_size: text})}
                    placeholder="e.g., 6, 7, 8"
                    placeholderTextColor={theme.textSecondary}
                  />
                ) : (
                  <Text style={[styles.inputValue, { color: theme.textSecondary }]}>{partnerData.ring_size || 'Not set'}</Text>
                )}
              </View>

              <View style={styles.inputRow}>
                <Text style={[styles.inputLabel, { color: theme.text }]}>Additional Notes:</Text>
                {editMode ? (
                  <TextInput
                    style={[styles.input, styles.textArea, { backgroundColor: theme.background, color: theme.text, borderColor: theme.border }]}
                    value={partnerData.additional_notes}
                    onChangeText={(text) => setPartnerData({...partnerData, additional_notes: text})}
                    placeholder="Any additional notes about your partner"
                    placeholderTextColor={theme.textSecondary}
                    multiline
                  />
                ) : (
                  <Text style={[styles.inputValue, { color: theme.textSecondary }]}>{partnerData.additional_notes || 'No additional notes'}</Text>
                )}
              </View>

              {editMode && (
                <TouchableOpacity
                  style={[styles.saveButton, { backgroundColor: theme.primary }]}
                  onPress={handleSaveProfile}
                >
                  <Text style={styles.saveButtonText}>Save Changes</Text>
                </TouchableOpacity>
              )}
            </View>
          </View>

          {/* Account Actions */}
          <View style={styles.section}>
            <Text style={[styles.sectionTitle, { color: theme.text }]}>Account 👤</Text>
            <View style={[styles.actionsCard, { backgroundColor: theme.surface }]}>
              <TouchableOpacity 
                style={[styles.actionItem, { borderBottomColor: theme.border }]}
                onPress={() => {
                  Alert.alert(
                    'Reset Onboarding',
                    'This will reset your onboarding flow. Are you sure?',
                    [
                      { text: 'Cancel', style: 'cancel' },
                      { text: 'Reset', style: 'destructive', onPress: resetOnboarding },
                    ]
                  );
                }}
              >
                <Ionicons name="refresh" size={20} color="#2196F3" />
                <Text style={[styles.actionText, { color: '#2196F3' }]}>Reset Onboarding</Text>
              </TouchableOpacity>
              
              <TouchableOpacity style={[styles.actionItem, { borderBottomColor: theme.border }]} onPress={handleLogout}>
                <Ionicons name="log-out" size={20} color="#FF5722" />
                <Text style={[styles.actionText, { color: '#FF5722' }]}>Logout</Text>
              </TouchableOpacity>
            </View>
          </View>

          {/* App Info */}
          <View style={styles.footer}>
            <Text style={[styles.footerText, { color: theme.textSecondary }]}>Pookie4u v1.0.0</Text>
            <Text style={[styles.footerText, { color: theme.textSecondary }]}>Made with ❤️ for couples</Text>
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  keyboardView: {
    flex: 1,
  },
  scrollView: {
    flex: 1,
  },
  profileHeader: {
    alignItems: 'center',
    padding: 30,
    marginBottom: 10,
  },
  avatarContainer: {
    width: 80,
    height: 80,
    borderRadius: 40,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 15,
    position: 'relative',
    borderWidth: 2,
  },
  avatarImage: {
    width: 76,
    height: 76,
    borderRadius: 38,
  },
  cameraIcon: {
    position: 'absolute',
    bottom: 0,
    right: 0,
    borderRadius: 12,
    width: 24,
    height: 24,
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 2,
    borderColor: '#fff',
  },
  userName: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 5,
  },
  userEmail: {
    fontSize: 14,
    marginBottom: 10,
  },
  userTagContainer: {
    marginBottom: 10,
  },
  userTag: {
    fontSize: 12,
    color: '#fff',
    fontWeight: '600',
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 12,
  },
  relationshipModeButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 15,
    paddingVertical: 8,
    borderRadius: 20,
    gap: 5,
  },
  relationshipMode: {
    fontSize: 12,
    fontWeight: '600',
  },
  modeSelector: {
    position: 'absolute',
    top: 180,
    left: 20,
    right: 20,
    borderRadius: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
    zIndex: 1000,
  },
  modeOption: {
    padding: 15,
    borderBottomWidth: 1,
  },
  modeLabel: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 2,
  },
  modeDescription: {
    fontSize: 12,
  },
  
  // Selector overlay and improved UI
  selectorOverlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    zIndex: 999,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: 'rgba(0, 0, 0, 0.4)',
  },
  selectorHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  selectorTitle: {
    fontSize: 16,
    fontWeight: '600',
  },
  dismissButton: {
    padding: 4,
  },
  modeOptionContent: {
    flex: 1,
  },
  statsContainer: {
    flexDirection: 'row',
    paddingHorizontal: 20,
    marginBottom: 20,
    gap: 10,
  },
  statCard: {
    flex: 1,
    borderRadius: 15,
    padding: 20,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  statNumber: {
    fontSize: 18,
    fontWeight: 'bold',
    marginTop: 8,
    marginBottom: 4,
  },
  statLabel: {
    fontSize: 10,
    textAlign: 'center',
  },
  section: {
    marginHorizontal: 20,
    marginBottom: 20,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 15,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
  },
  subSectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    marginTop: 20,
    marginBottom: 10,
  },
  editButton: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 5,
  },
  editButtonText: {
    fontSize: 14,
    fontWeight: '600',
  },
  achievementCard: {
    borderRadius: 15,
    padding: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  achievementRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  achievementLabel: {
    fontSize: 16,
  },
  achievementValue: {
    fontSize: 16,
    fontWeight: 'bold',
  },
  badgesContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 10,
  },
  badge: {
    borderRadius: 20,
    paddingHorizontal: 12,
    paddingVertical: 8,
    flexDirection: 'row',
    alignItems: 'center',
    gap: 5,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  badgeText: {
    fontSize: 12,
    fontWeight: '600',
  },
  partnerCard: {
    borderRadius: 15,
    padding: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  inputRow: {
    marginBottom: 15,
  },
  inputLabel: {
    fontSize: 14,
    fontWeight: '600',
    marginBottom: 5,
  },
  input: {
    borderWidth: 1,
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
  },
  textArea: {
    height: 80,
    textAlignVertical: 'top',
  },
  inputValue: {
    fontSize: 16,
    paddingVertical: 8,
  },
  saveButton: {
    borderRadius: 10,
    padding: 15,
    alignItems: 'center',
    marginTop: 10,
  },
  saveButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  settingsCard: {
    borderRadius: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  settingItem: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 20,
    borderBottomWidth: 1,
  },
  settingText: {
    flex: 1,
    fontSize: 16,
    marginLeft: 15,
  },
  actionsCard: {
    borderRadius: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  actionItem: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 20,
    borderBottomWidth: 1,
  },
  actionText: {
    fontSize: 16,
    marginLeft: 15,
    fontWeight: '600',
  },
  footer: {
    alignItems: 'center',
    padding: 20,
    marginBottom: 20,
  },
  footerText: {
    fontSize: 12,
    marginBottom: 5,
  },
});