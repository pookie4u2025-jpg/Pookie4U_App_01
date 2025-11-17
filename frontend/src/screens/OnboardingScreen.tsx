import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Alert,
  ScrollView,
  KeyboardAvoidingView,
  Platform,
  ActivityIndicator,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Picker } from '@react-native-picker/picker';
import { format } from 'date-fns';
import Animated, { 
  FadeInDown, 
  FadeOutUp, 
  useSharedValue, 
  useAnimatedStyle, 
  withSpring,
  withSequence,
  interpolateColor,
} from 'react-native-reanimated';
import { useAuthStore } from '../stores/useAuthStore';
import { useAppStore } from '../stores/useAppStore';
import SubscriptionOnboardingScreen from './SubscriptionOnboardingScreen';

const RELATIONSHIP_MODES = [
  { value: 'SAME_HOME', label: 'Same Home - We live together' },
  { value: 'DAILY_IRL', label: 'Daily IRL - We meet daily (work/study)' },
  { value: 'LONG_DISTANCE', label: 'Long Distance - We\'re in different cities' },
];

export default function OnboardingScreen() {
  const [step, setStep] = useState(1);
  const [showSubscription, setShowSubscription] = useState(false);
  const [partnerName, setPartnerName] = useState('');
  const [relationshipMode, setRelationshipMode] = useState('SAME_HOME');
  const [birthday, setBirthday] = useState('');
  const [anniversary, setAnniversary] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showSuccessAnimation, setShowSuccessAnimation] = useState(false);
  
  // Validation states
  const [partnerNameError, setPartnerNameError] = useState('');
  const [birthdayError, setBirthdayError] = useState('');
  const [anniversaryError, setAnniversaryError] = useState('');
  
  // Animated values
  const progressAnimation = useSharedValue(0);

  const { updatePartnerProfile, updateRelationshipMode } = useAuthStore();
  const { completeOnboarding } = useAppStore();
  
  // Update progress animation when step changes
  useEffect(() => {
    progressAnimation.value = withSpring((step / 4) * 100, {
      damping: 15,
      stiffness: 100,
    });
  }, [step]);

  // Validation functions
  const validatePartnerName = (name: string): boolean => {
    if (!name.trim()) {
      setPartnerNameError('Please enter your partner\'s name');
      return false;
    }
    if (name.trim().length < 2) {
      setPartnerNameError('Name should be at least 2 characters');
      return false;
    }
    setPartnerNameError('');
    return true;
  };
  
  const validateDate = (dateStr: string, fieldName: string): boolean => {
    if (!dateStr.trim()) {
      // Optional fields - no error for empty
      return true;
    }
    
    const parts = dateStr.trim().split('-');
    if (parts.length !== 3) {
      return false;
    }
    
    const day = parseInt(parts[0], 10);
    const month = parseInt(parts[1], 10);
    const year = parseInt(parts[2], 10);
    
    if (isNaN(day) || isNaN(month) || isNaN(year)) {
      return false;
    }
    
    if (day < 1 || day > 31 || month < 1 || month > 12 || year < 1900 || year > 2100) {
      return false;
    }
    
    return true;
  };
  
  const handleNext = () => {
    // Step 1: Partner Name validation
    if (step === 1) {
      if (!validatePartnerName(partnerName)) {
        return;
      }
    }
    
    // Step 3: Birthday validation
    if (step === 3 && birthday.trim()) {
      if (!validateDate(birthday, 'birthday')) {
        setBirthdayError('Please enter a valid date (DD-MM-YYYY)');
        return;
      }
      setBirthdayError('');
    }
    
    // Step 4: Anniversary validation
    if (step === 4 && anniversary.trim()) {
      if (!validateDate(anniversary, 'anniversary')) {
        setAnniversaryError('Please enter a valid date (DD-MM-YYYY)');
        return;
      }
      setAnniversaryError('');
    }
    
    if (step < 4) {
      setStep(step + 1);
    } else {
      // After step 4, save profile and show subscription screen
      saveProfileAndShowSubscription();
    }
  };
  
  const saveProfileAndShowSubscription = async () => {
    try {
      setIsLoading(true);
      
      // Update relationship mode
      await updateRelationshipMode(relationshipMode);

      // Parse dates with proper validation
      const parsedBirthday = parseDateString(birthday);
      const parsedAnniversary = parseDateString(anniversary);

      // Update partner profile
      const partnerProfile = {
        name: partnerName,
        birthday: parsedBirthday,
        anniversary: parsedAnniversary,
        favorite_color: '',
        favorite_food: '',
        favorite_flower: '',
        favorite_brand: '',
        dress_size: '',
        ring_size: '',
        perfume_preference: '',
        notes: '',
      };

      await updatePartnerProfile(partnerProfile);
      
      // Show success animation briefly
      setShowSuccessAnimation(true);
      await new Promise(resolve => setTimeout(resolve, 800));
      
      // Show subscription screen
      setShowSubscription(true);
    } catch (error) {
      console.error('Error saving profile:', error);
      Alert.alert('Error', 'Failed to save profile. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleSubscriptionChoice = async (subscriptionType: 'trial' | 'monthly' | 'half_yearly') => {
    try {
      const { token } = useAuthStore.getState();
      const backendUrl = process.env.EXPO_PUBLIC_BACKEND_URL;
      
      // Step 1: Activate subscription
      const response = await fetch(`${backendUrl}/api/subscription/start-mockup`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ subscription_type: subscriptionType }),
      });
      
      if (response.ok) {
        const data = await response.json();
        console.log('✅ Subscription activated:', data);
      } else {
        const errorText = await response.text();
        console.log('⚠️ Subscription error:', errorText);
        
        if (errorText.includes('Free trial already used') || errorText.includes('trial already used')) {
          console.log('Trial already used - continuing anyway');
        }
      }
      
      // Step 2: Mark onboarding as complete on backend (CRITICAL!)
      const completeResponse = await fetch(`${backendUrl}/api/user/complete-onboarding`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });
      
      if (completeResponse.ok) {
        const completeData = await completeResponse.json();
        console.log('✅ Onboarding completed on backend:', completeData);
        
        // Update local user state with profile_completed = true
        const currentUser = useAuthStore.getState().user;
        if (currentUser) {
          useAuthStore.setState({ 
            user: { ...currentUser, profile_completed: true } 
          });
        }
      }
      
    } catch (error) {
      console.error('❌ Error in onboarding:', error);
    } finally {
      // Complete onboarding in local state
      completeOnboarding();
    }
  };
  
  // Show subscription screen after profile setup
  if (showSubscription) {
    return <SubscriptionOnboardingScreen onComplete={handleSubscriptionChoice} />;
  }

  const parseDateString = (dateStr: string): string | undefined => {
    if (!dateStr || !dateStr.trim()) {
      return undefined;
    }

    try {
      // Expected format: DD-MM-YYYY
      const parts = dateStr.trim().split('-');
      
      if (parts.length !== 3) {
        console.warn('Invalid date format, expected DD-MM-YYYY');
        return undefined;
      }

      const day = parseInt(parts[0], 10);
      const month = parseInt(parts[1], 10);
      const year = parseInt(parts[2], 10);

      // Validate day, month, year
      if (isNaN(day) || isNaN(month) || isNaN(year)) {
        console.warn('Invalid date values');
        return undefined;
      }

      if (day < 1 || day > 31 || month < 1 || month > 12 || year < 1900 || year > 2100) {
        console.warn('Date values out of range');
        return undefined;
      }

      // Create date object (month is 0-indexed in JavaScript)
      const date = new Date(year, month - 1, day);

      // Verify the date is valid
      if (isNaN(date.getTime())) {
        console.warn('Invalid date created');
        return undefined;
      }

      return date.toISOString();
    } catch (error) {
      console.error('Error parsing date:', error);
      return undefined;
    }
  };

  const handleComplete = async () => {
    try {
      // Update relationship mode
      await updateRelationshipMode(relationshipMode);

      // Parse dates with proper validation
      const parsedBirthday = parseDateString(birthday);
      const parsedAnniversary = parseDateString(anniversary);

      // Update partner profile
      const partnerProfile = {
        name: partnerName,
        birthday: parsedBirthday,
        anniversary: parsedAnniversary,
        favorite_color: '',
        favorite_food: '',
        favorite_flower: '',
        favorite_brand: '',
        dress_size: '',
        ring_size: '',
        perfume_preference: '',
        notes: '',
      };

      await updatePartnerProfile(partnerProfile);
      completeOnboarding();
    } catch (error) {
      console.error('Error completing onboarding:', error);
      Alert.alert('Error', 'Failed to complete onboarding. Please try again.');
    }
  };

  const renderStep = () => {
    switch (step) {
      case 1:
        return (
          <Animated.View 
            entering={FadeInDown.duration(500).springify()}
            exiting={FadeOutUp.duration(300)}
            style={styles.stepContainer}
          >
            <Text style={styles.stepTitle}>What's your partner's name?</Text>
            <Text style={styles.stepSubtitle}>
              We'll use this to personalize your experience
            </Text>
            <TextInput
              style={[
                styles.input,
                partnerNameError ? styles.inputError : null,
              ]}
              placeholder="Partner's name"
              value={partnerName}
              onChangeText={(text) => {
                setPartnerName(text);
                if (text.trim().length >= 2) {
                  setPartnerNameError('');
                }
              }}
              onBlur={() => {
                if (partnerName.trim()) {
                  validatePartnerName(partnerName);
                }
              }}
              autoCapitalize="words"
              autoFocus
            />
            {partnerNameError ? (
              <Animated.Text 
                entering={FadeInDown.duration(300)}
                style={styles.errorText}
              >
                {partnerNameError}
              </Animated.Text>
            ) : null}
          </Animated.View>
        );

      case 2:
        return (
          <Animated.View 
            entering={FadeInDown.duration(500).springify()}
            exiting={FadeOutUp.duration(300)}
            style={styles.stepContainer}
          >
            <Text style={styles.stepTitle}>What's your relationship mode?</Text>
            <Text style={styles.stepSubtitle}>
              This helps us suggest the right tasks for you
            </Text>
            <View style={styles.relationshipModeContainer}>
              {RELATIONSHIP_MODES.map((mode, index) => (
                <Animated.View
                  key={mode.value}
                  entering={FadeInDown.duration(500).delay(index * 100).springify()}
                >
                  <TouchableOpacity
                    style={[
                      styles.relationshipModeButton,
                      relationshipMode === mode.value && styles.relationshipModeButtonSelected
                    ]}
                    onPress={() => setRelationshipMode(mode.value)}
                    activeOpacity={0.7}
                  >
                    <Text style={[
                      styles.relationshipModeText,
                      relationshipMode === mode.value && styles.relationshipModeTextSelected
                    ]}>
                      {mode.label}
                    </Text>
                  </TouchableOpacity>
                </Animated.View>
              ))}
            </View>
          </Animated.View>
        );

      case 3:
        return (
          <Animated.View 
            entering={FadeInDown.duration(500).springify()}
            exiting={FadeOutUp.duration(300)}
            style={styles.stepContainer}
          >
            <Text style={styles.stepTitle}>When is your partner's birthday?</Text>
            <Text style={styles.stepSubtitle}>
              Optional - We'll remind you of important dates
            </Text>
            <TextInput
              style={[
                styles.input,
                birthdayError ? styles.inputError : null,
              ]}
              placeholder="DD-MM-YYYY (e.g., 15-06-1995)"
              value={birthday}
              onChangeText={(text) => {
                setBirthday(text);
                if (birthdayError) {
                  setBirthdayError('');
                }
              }}
              onBlur={() => {
                if (birthday.trim() && !validateDate(birthday, 'birthday')) {
                  setBirthdayError('Please enter a valid date (DD-MM-YYYY)');
                }
              }}
              keyboardType="numeric"
              autoFocus
            />
            {birthdayError ? (
              <Animated.Text 
                entering={FadeInDown.duration(300)}
                style={styles.errorText}
              >
                {birthdayError}
              </Animated.Text>
            ) : null}
            <Text style={styles.helperText}>
              💡 You can skip this and add it later
            </Text>
          </Animated.View>
        );

      case 4:
        return (
          <Animated.View 
            entering={FadeInDown.duration(500).springify()}
            exiting={FadeOutUp.duration(300)}
            style={styles.stepContainer}
          >
            <Text style={styles.stepTitle}>When is your anniversary?</Text>
            <Text style={styles.stepSubtitle}>
              Optional - We'll help you celebrate special moments
            </Text>
            <TextInput
              style={[
                styles.input,
                anniversaryError ? styles.inputError : null,
              ]}
              placeholder="DD-MM-YYYY (e.g., 14-02-2020)"
              value={anniversary}
              onChangeText={(text) => {
                setAnniversary(text);
                if (anniversaryError) {
                  setAnniversaryError('');
                }
              }}
              onBlur={() => {
                if (anniversary.trim() && !validateDate(anniversary, 'anniversary')) {
                  setAnniversaryError('Please enter a valid date (DD-MM-YYYY)');
                }
              }}
              keyboardType="numeric"
              autoFocus
            />
            {anniversaryError ? (
              <Animated.Text 
                entering={FadeInDown.duration(300)}
                style={styles.errorText}
              >
                {anniversaryError}
              </Animated.Text>
            ) : null}
            <Text style={styles.helperText}>
              💡 You can skip this and add it later
            </Text>
          </Animated.View>
        );

      default:
        return null;
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <KeyboardAvoidingView 
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.keyboardView}
      >
        <ScrollView contentContainerStyle={styles.scrollContent}>
          <View style={styles.header}>
            <Text style={styles.title}>Let's Set Up Your Profile</Text>
            <View style={styles.progressBar}>
              <View style={[styles.progressFill, { width: `${(step / 4) * 100}%` }]} />
            </View>
            <Text style={styles.progressText}>Step {step} of 4</Text>
          </View>

          {renderStep()}

          <View style={styles.buttonContainer}>
            {step > 1 && (
              <Animated.View 
                entering={FadeInDown.duration(300)}
                style={{ flex: 1 }}
              >
                <TouchableOpacity
                  style={styles.backButton}
                  onPress={() => setStep(step - 1)}
                  disabled={isLoading}
                >
                  <Text style={styles.backButtonText}>Back</Text>
                </TouchableOpacity>
              </Animated.View>
            )}
            
            <Animated.View 
              entering={FadeInDown.duration(300).delay(100)}
              style={{ flex: step > 1 ? 2 : 1 }}
            >
              <TouchableOpacity
                style={[
                  styles.nextButton,
                  isLoading && styles.nextButtonDisabled,
                ]}
                onPress={handleNext}
                disabled={isLoading}
                activeOpacity={0.7}
              >
                {isLoading ? (
                  <View style={styles.loadingContainer}>
                    <ActivityIndicator color="#fff" size="small" />
                    <Text style={styles.nextButtonText}>  Saving...</Text>
                  </View>
                ) : showSuccessAnimation ? (
                  <Text style={styles.nextButtonText}>✓ Saved!</Text>
                ) : (
                  <Text style={styles.nextButtonText}>
                    {step === 4 ? 'Complete Setup' : 'Next'}
                  </Text>
                )}
              </TouchableOpacity>
            </Animated.View>
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
  scrollContent: {
    flexGrow: 1,
    padding: 20,
  },
  header: {
    alignItems: 'center',
    marginBottom: 40,
    marginTop: 20,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 20,
    textAlign: 'center',
  },
  progressBar: {
    width: '100%',
    height: 4,
    backgroundColor: '#e0e0e0',
    borderRadius: 2,
    marginBottom: 10,
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#FF69B4',
    borderRadius: 2,
  },
  progressText: {
    fontSize: 14,
    color: '#666',
  },
  stepContainer: {
    backgroundColor: '#fff',
    borderRadius: 15,
    padding: 25,
    marginBottom: 30,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 10,
    elevation: 5,
  },
  stepTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 10,
    textAlign: 'center',
  },
  stepSubtitle: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
    marginBottom: 20,
  },
  input: {
    borderWidth: 1,
    borderColor: '#e0e0e0',
    borderRadius: 10,
    padding: 15,
    fontSize: 16,
    backgroundColor: '#f9f9f9',
  },
  pickerContainer: {
    borderWidth: 1,
    borderColor: '#e0e0e0',
    borderRadius: 10,
    backgroundColor: '#f9f9f9',
  },
  picker: {
    height: 50,
  },
  relationshipModeContainer: {
    gap: 15,
  },
  relationshipModeButton: {
    backgroundColor: '#f9f9f9',
    borderWidth: 2,
    borderColor: '#e0e0e0',
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
  },
  relationshipModeButtonSelected: {
    backgroundColor: '#FF1493',
    borderColor: '#FF1493',
  },
  relationshipModeText: {
    fontSize: 16,
    fontWeight: '500',
    color: '#333333',
    textAlign: 'center',
  },
  relationshipModeTextSelected: {
    color: '#FFFFFF',
    fontWeight: '600',
  },
  buttonContainer: {
    flexDirection: 'row',
    gap: 15,
    marginTop: 'auto',
    paddingBottom: 20,
  },
  backButton: {
    flex: 1,
    backgroundColor: '#e0e0e0',
    borderRadius: 10,
    padding: 15,
    alignItems: 'center',
  },
  backButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#666',
  },
  nextButton: {
    flex: 2,
    backgroundColor: '#FF69B4',
    borderRadius: 10,
    padding: 15,
    alignItems: 'center',
  },
  nextButtonText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#fff',
  },
});