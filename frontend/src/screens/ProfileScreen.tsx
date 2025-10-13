import React, { useState } from 'react';
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
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import * as ImagePicker from 'expo-image-picker';
import { useAuthStore } from '../stores/useAuthStore';
import { useGameStore } from '../stores/useGameStore';
import { useAppStore } from '../stores/useAppStore';

export default function ProfileScreen() {
  const { user, logout, updatePartnerProfile, updateRelationshipMode, updateProfileImage } = useAuthStore();
  const { totalPoints, currentLevel, currentStreak, longestStreak, tasksCompleted, badges } = useGameStore();
  const { resetOnboarding } = useAppStore();

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
    const success = await updateRelationshipMode(mode);
    if (success) {
      setShowModeSelector(false);
      Alert.alert('Success', 'Relationship mode updated successfully!');
    }
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
    <SafeAreaView style={styles.container}>
      <KeyboardAvoidingView 
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.keyboardView}
      >
        <ScrollView style={styles.scrollView}>
          {/* User Profile Header */}
          <View style={styles.profileHeader}>
            <TouchableOpacity style={styles.avatarContainer} onPress={showImagePicker}>
              {profileImage ? (
                <Image source={{ uri: profileImage }} style={styles.avatarImage} />
              ) : (
                <Ionicons name="person" size={40} color="#FF69B4" />
              )}
              <View style={styles.cameraIcon}>
                <Ionicons name="camera" size={16} color="#fff" />
              </View>
            </TouchableOpacity>
            <Text style={styles.userName}>{user?.name}</Text>
            <Text style={styles.userEmail}>{user?.email}</Text>
            <View style={styles.userTagContainer}>
              <Text style={styles.userTag}>{getUserTag()}</Text>
            </View>
            <TouchableOpacity 
              style={styles.relationshipModeButton}
              onPress={() => setShowModeSelector(!showModeSelector)}
            >
              <Text style={styles.relationshipMode}>
                {user?.relationship_mode?.replace('_', ' ')} Mode
              </Text>
              <Ionicons name="chevron-down" size={16} color="#FF69B4" />
            </TouchableOpacity>
            
            {/* Relationship Mode Selector */}
            {showModeSelector && (
              <View style={styles.modeSelector}>
                {RELATIONSHIP_MODES.map((mode) => (
                  <TouchableOpacity
                    key={mode.value}
                    style={[
                      styles.modeOption,
                      user?.relationship_mode === mode.value && styles.selectedMode
                    ]}
                    onPress={() => handleModeChange(mode.value)}
                  >
                    <Text style={[
                      styles.modeLabel,
                      user?.relationship_mode === mode.value && styles.selectedModeText
                    ]}>
                      {mode.label}
                    </Text>
                    <Text style={styles.modeDescription}>{mode.description}</Text>
                  </TouchableOpacity>
                ))}
              </View>
            )}
          </View>

          {/* Stats Overview */}
          <View style={styles.statsContainer}>
            <View style={styles.statCard}>
              <Ionicons name="star" size={24} color="#FFD700" />
              <Text style={styles.statNumber}>{totalPoints}</Text>
              <Text style={styles.statLabel}>Total Points</Text>
            </View>
            <View style={styles.statCard}>
              <Ionicons name="trophy" size={24} color="#FF69B4" />
              <Text style={styles.statNumber}>Level {currentLevel}</Text>
              <Text style={styles.statLabel}>Current Level</Text>
            </View>
            <View style={styles.statCard}>
              <Ionicons name="flash" size={24} color="#FF4500" />
              <Text style={styles.statNumber}>{currentStreak}</Text>
              <Text style={styles.statLabel}>Current Streak</Text>
            </View>
          </View>

          {/* Achievement Stats */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Your Achievements 🏆</Text>
            <View style={styles.achievementCard}>
              <View style={styles.achievementRow}>
                <Text style={styles.achievementLabel}>Tasks Completed:</Text>
                <Text style={styles.achievementValue}>{tasksCompleted}</Text>
              </View>
              <View style={styles.achievementRow}>
                <Text style={styles.achievementLabel}>Longest Streak:</Text>
                <Text style={styles.achievementValue}>{longestStreak} days</Text>
              </View>
              <View style={styles.achievementRow}>
                <Text style={styles.achievementLabel}>Badges Earned:</Text>
                <Text style={styles.achievementValue}>{badges.length}</Text>
              </View>
            </View>
          </View>

          {/* Badges */}
          {badges.length > 0 && (
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>Your Badges 🏅</Text>
              <View style={styles.badgesContainer}>
                {badges.map((badge, index) => (
                  <View key={index} style={styles.badge}>
                    <Ionicons name={getBadgeIcon(badge)} size={20} color="#FF69B4" />
                    <Text style={styles.badgeText}>{badge}</Text>
                  </View>
                ))}
              </View>
            </View>
          )}

          {/* Partner Profile */}
          <View style={styles.section}>
            <View style={styles.sectionHeader}>
              <Text style={styles.sectionTitle}>Partner's Profile 💕</Text>
              <TouchableOpacity
                style={styles.editButton}
                onPress={() => setEditMode(!editMode)}
              >
                <Ionicons name={editMode ? "close" : "pencil"} size={20} color="#FF69B4" />
                <Text style={styles.editButtonText}>
                  {editMode ? 'Cancel' : 'Edit'}
                </Text>
              </TouchableOpacity>
            </View>

            <View style={styles.partnerCard}>
              <View style={styles.inputRow}>
                <Text style={styles.inputLabel}>Name:</Text>
                {editMode ? (
                  <TextInput
                    style={styles.input}
                    value={partnerData.name}
                    onChangeText={(text) => setPartnerData({...partnerData, name: text})}
                    placeholder="Partner's name"
                  />
                ) : (
                  <Text style={styles.inputValue}>{partnerData.name || 'Not set'}</Text>
                )}
              </View>

              <View style={styles.inputRow}>
                <Text style={styles.inputLabel}>Birthday:</Text>
                {editMode ? (
                  <TextInput
                    style={styles.input}
                    value={partnerData.birthday}
                    onChangeText={(text) => setPartnerData({...partnerData, birthday: text})}
                    placeholder="YYYY-MM-DD"
                  />
                ) : (
                  <Text style={styles.inputValue}>{partnerData.birthday || 'Not set'}</Text>
                )}
              </View>

              <View style={styles.inputRow}>
                <Text style={styles.inputLabel}>Anniversary:</Text>
                {editMode ? (
                  <TextInput
                    style={styles.input}
                    value={partnerData.anniversary}
                    onChangeText={(text) => setPartnerData({...partnerData, anniversary: text})}
                    placeholder="YYYY-MM-DD"
                  />
                ) : (
                  <Text style={styles.inputValue}>{partnerData.anniversary || 'Not set'}</Text>
                )}
              </View>

              <View style={styles.inputRow}>
                <Text style={styles.inputLabel}>Favorite Color:</Text>
                {editMode ? (
                  <TextInput
                    style={styles.input}
                    value={partnerData.favorite_color}
                    onChangeText={(text) => setPartnerData({...partnerData, favorite_color: text})}
                    placeholder="e.g., Blue"
                  />
                ) : (
                  <Text style={styles.inputValue}>{partnerData.favorite_color || 'Not set'}</Text>
                )}
              </View>

              <View style={styles.inputRow}>
                <Text style={styles.inputLabel}>Favorite Food:</Text>
                {editMode ? (
                  <TextInput
                    style={styles.input}
                    value={partnerData.favorite_food}
                    onChangeText={(text) => setPartnerData({...partnerData, favorite_food: text})}
                    placeholder="e.g., Pizza"
                  />
                ) : (
                  <Text style={styles.inputValue}>{partnerData.favorite_food || 'Not set'}</Text>
                )}
              </View>

              <View style={styles.inputRow}>
                <Text style={styles.inputLabel}>Favorite Food:</Text>
                {editMode ? (
                  <TextInput
                    style={styles.input}
                    value={partnerData.favorite_food}
                    onChangeText={(text) => setPartnerData({...partnerData, favorite_food: text})}
                    placeholder="e.g., Pizza"
                  />
                ) : (
                  <Text style={styles.inputValue}>{partnerData.favorite_food || 'Not set'}</Text>
                )}
              </View>

              <View style={styles.inputRow}>
                <Text style={styles.inputLabel}>Favorite Flower:</Text>
                {editMode ? (
                  <TextInput
                    style={styles.input}
                    value={partnerData.favorite_flower}
                    onChangeText={(text) => setPartnerData({...partnerData, favorite_flower: text})}
                    placeholder="e.g., Rose"
                  />
                ) : (
                  <Text style={styles.inputValue}>{partnerData.favorite_flower || 'Not set'}</Text>
                )}
              </View>

              <View style={styles.inputRow}>
                <Text style={styles.inputLabel}>Favorite Brand:</Text>
                {editMode ? (
                  <TextInput
                    style={styles.input}
                    value={partnerData.favorite_brand}
                    onChangeText={(text) => setPartnerData({...partnerData, favorite_brand: text})}
                    placeholder="e.g., Nike"
                  />
                ) : (
                  <Text style={styles.inputValue}>{partnerData.favorite_brand || 'Not set'}</Text>
                )}
              </View>

              <View style={styles.inputRow}>
                <Text style={styles.inputLabel}>Perfume Preference:</Text>
                {editMode ? (
                  <TextInput
                    style={styles.input}
                    value={partnerData.favorite_perfume}
                    onChangeText={(text) => setPartnerData({...partnerData, favorite_perfume: text})}
                    placeholder="e.g., Floral, Woody"
                  />
                ) : (
                  <Text style={styles.inputValue}>{partnerData.favorite_perfume || 'Not set'}</Text>
                )}
              </View>

              {/* Sizing Information */}
              <Text style={styles.subSectionTitle}>Sizing Information 👗</Text>

              <View style={styles.inputRow}>
                <Text style={styles.inputLabel}>Dress Size:</Text>
                {editMode ? (
                  <TextInput
                    style={styles.input}
                    value={partnerData.dress_size}
                    onChangeText={(text) => setPartnerData({...partnerData, dress_size: text})}
                    placeholder="e.g., S, M, L"
                  />
                ) : (
                  <Text style={styles.inputValue}>{partnerData.dress_size || 'Not set'}</Text>
                )}
              </View>

              <View style={styles.inputRow}>
                <Text style={styles.inputLabel}>Top Size:</Text>
                {editMode ? (
                  <TextInput
                    style={styles.input}
                    value={partnerData.top_size}
                    onChangeText={(text) => setPartnerData({...partnerData, top_size: text})}
                    placeholder="e.g., S, M, L"
                  />
                ) : (
                  <Text style={styles.inputValue}>{partnerData.top_size || 'Not set'}</Text>
                )}
              </View>

              <View style={styles.inputRow}>
                <Text style={styles.inputLabel}>Jeans Size:</Text>
                {editMode ? (
                  <TextInput
                    style={styles.input}
                    value={partnerData.jeans_size}
                    onChangeText={(text) => setPartnerData({...partnerData, jeans_size: text})}
                    placeholder="e.g., 28, 30, 32"
                  />
                ) : (
                  <Text style={styles.inputValue}>{partnerData.jeans_size || 'Not set'}</Text>
                )}
              </View>

              <View style={styles.inputRow}>
                <Text style={styles.inputLabel}>Ring Size:</Text>
                {editMode ? (
                  <TextInput
                    style={styles.input}
                    value={partnerData.ring_size}
                    onChangeText={(text) => setPartnerData({...partnerData, ring_size: text})}
                    placeholder="e.g., 6, 7, 8"
                  />
                ) : (
                  <Text style={styles.inputValue}>{partnerData.ring_size || 'Not set'}</Text>
                )}
              </View>

              <View style={styles.inputRow}>
                <Text style={styles.inputLabel}>Additional Notes:</Text>
                {editMode ? (
                  <TextInput
                    style={[styles.input, styles.textArea]}
                    value={partnerData.additional_notes}
                    onChangeText={(text) => setPartnerData({...partnerData, additional_notes: text})}
                    placeholder="Any additional notes about your partner"
                    multiline
                  />
                ) : (
                  <Text style={styles.inputValue}>{partnerData.additional_notes || 'No additional notes'}</Text>
                )}
              </View>

              {editMode && (
                <TouchableOpacity
                  style={styles.saveButton}
                  onPress={handleSaveProfile}
                >
                  <Text style={styles.saveButtonText}>Save Changes</Text>
                </TouchableOpacity>
              )}
            </View>
          </View>

          {/* App Settings */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>App Settings ⚙️</Text>
            <View style={styles.settingsCard}>
              <TouchableOpacity style={styles.settingItem}>
                <Ionicons name="notifications" size={20} color="#666" />
                <Text style={styles.settingText}>Notifications</Text>
                <Ionicons name="chevron-forward" size={20} color="#ccc" />
              </TouchableOpacity>
              
              <TouchableOpacity style={styles.settingItem}>
                <Ionicons name="moon" size={20} color="#666" />
                <Text style={styles.settingText}>Dark Mode</Text>
                <Ionicons name="chevron-forward" size={20} color="#ccc" />
              </TouchableOpacity>
              
              <TouchableOpacity style={styles.settingItem}>
                <Ionicons name="language" size={20} color="#666" />
                <Text style={styles.settingText}>Language</Text>
                <Ionicons name="chevron-forward" size={20} color="#ccc" />
              </TouchableOpacity>
            </View>
          </View>

          {/* Account Actions */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Account 👤</Text>
            <View style={styles.actionsCard}>
              <TouchableOpacity 
                style={styles.actionItem}
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
              
              <TouchableOpacity style={styles.actionItem} onPress={handleLogout}>
                <Ionicons name="log-out" size={20} color="#FF5722" />
                <Text style={[styles.actionText, { color: '#FF5722' }]}>Logout</Text>
              </TouchableOpacity>
            </View>
          </View>

          {/* App Info */}
          <View style={styles.footer}>
            <Text style={styles.footerText}>Pookie4u v1.0.0</Text>
            <Text style={styles.footerText}>Made with ❤️ for couples</Text>
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8f9fa',
  },
  keyboardView: {
    flex: 1,
  },
  scrollView: {
    flex: 1,
  },
  profileHeader: {
    backgroundColor: '#fff',
    alignItems: 'center',
    padding: 30,
    marginBottom: 10,
  },
  avatarContainer: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: '#FFF0F7',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 15,
    position: 'relative',
    borderWidth: 2,
    borderColor: '#FF69B4',
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
    backgroundColor: '#FF69B4',
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
    color: '#333',
    marginBottom: 5,
  },
  userEmail: {
    fontSize: 14,
    color: '#666',
    marginBottom: 10,
  },
  userTagContainer: {
    marginBottom: 10,
  },
  userTag: {
    fontSize: 12,
    color: '#fff',
    fontWeight: '600',
    backgroundColor: '#FF69B4',
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 12,
  },
  relationshipModeButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFF0F7',
    paddingHorizontal: 15,
    paddingVertical: 8,
    borderRadius: 20,
    gap: 5,
  },
  relationshipMode: {
    fontSize: 12,
    color: '#FF69B4',
    fontWeight: '600',
  },
  modeSelector: {
    position: 'absolute',
    top: 180,
    left: 20,
    right: 20,
    backgroundColor: '#fff',
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
    borderBottomColor: '#f0f0f0',
  },
  selectedMode: {
    backgroundColor: '#FFF0F7',
  },
  modeLabel: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 2,
  },
  selectedModeText: {
    color: '#FF69B4',
  },
  modeDescription: {
    fontSize: 12,
    color: '#666',
  },
  statsContainer: {
    flexDirection: 'row',
    paddingHorizontal: 20,
    marginBottom: 20,
    gap: 10,
  },
  statCard: {
    flex: 1,
    backgroundColor: '#fff',
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
    color: '#333',
    marginTop: 8,
    marginBottom: 4,
  },
  statLabel: {
    fontSize: 10,
    color: '#666',
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
    color: '#333',
  },
  subSectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#FF69B4',
    marginTop: 20,
    marginBottom: 10,
  },
  editButton: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 5,
  },
  editButtonText: {
    color: '#FF69B4',
    fontSize: 14,
    fontWeight: '600',
  },
  achievementCard: {
    backgroundColor: '#fff',
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
    color: '#666',
  },
  achievementValue: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#FF69B4',
  },
  badgesContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 10,
  },
  badge: {
    backgroundColor: '#fff',
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
    color: '#333',
    fontWeight: '600',
  },
  partnerCard: {
    backgroundColor: '#fff',
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
    color: '#333',
    marginBottom: 5,
  },
  input: {
    borderWidth: 1,
    borderColor: '#e0e0e0',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
    backgroundColor: '#f9f9f9',
  },
  textArea: {
    height: 80,
    textAlignVertical: 'top',
  },
  inputValue: {
    fontSize: 16,
    color: '#666',
    paddingVertical: 8,
  },
  saveButton: {
    backgroundColor: '#FF69B4',
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
    backgroundColor: '#fff',
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
    borderBottomColor: '#f0f0f0',
  },
  settingText: {
    flex: 1,
    fontSize: 16,
    color: '#333',
    marginLeft: 15,
  },
  actionsCard: {
    backgroundColor: '#fff',
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
    borderBottomColor: '#f0f0f0',
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
    color: '#999',
    marginBottom: 5,
  },
});