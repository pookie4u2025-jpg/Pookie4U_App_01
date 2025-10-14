import React, { useState } from 'react';
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
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Picker } from '@react-native-picker/picker';
import { format } from 'date-fns';
import { useAuthStore } from '../stores/useAuthStore';
import { useAppStore } from '../stores/useAppStore';

const RELATIONSHIP_MODES = [
  { value: 'SAME_HOME', label: 'Same Home - We live together' },
  { value: 'DAILY_IRL', label: 'Daily IRL - We meet daily (work/study)' },
  { value: 'LONG_DISTANCE', label: 'Long Distance - We\'re in different cities' },
];

export default function OnboardingScreen() {
  const [step, setStep] = useState(1);
  const [partnerName, setPartnerName] = useState('');
  const [relationshipMode, setRelationshipMode] = useState('SAME_HOME');
  const [birthday, setBirthday] = useState('');
  const [anniversary, setAnniversary] = useState('');

  const { updatePartnerProfile, updateRelationshipMode } = useAuthStore();
  const { completeOnboarding } = useAppStore();

  const handleNext = () => {
    if (step === 1 && !partnerName.trim()) {
      Alert.alert('Required', 'Please enter your partner\'s name');
      return;
    }
    if (step < 4) {
      setStep(step + 1);
    } else {
      handleComplete();
    }
  };

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
          <View style={styles.stepContainer}>
            <Text style={styles.stepTitle}>What's your partner's name?</Text>
            <Text style={styles.stepSubtitle}>
              We'll use this to personalize your experience
            </Text>
            <TextInput
              style={styles.input}
              placeholder="Partner's name"
              value={partnerName}
              onChangeText={setPartnerName}
              autoCapitalize="words"
            />
          </View>
        );

      case 2:
        return (
          <View style={styles.stepContainer}>
            <Text style={styles.stepTitle}>What's your relationship mode?</Text>
            <Text style={styles.stepSubtitle}>
              This helps us suggest the right tasks for you
            </Text>
            <View style={styles.relationshipModeContainer}>
              {RELATIONSHIP_MODES.map((mode) => (
                <TouchableOpacity
                  key={mode.value}
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
              ))}
            </View>
          </View>
        );

      case 3:
        return (
          <View style={styles.stepContainer}>
            <Text style={styles.stepTitle}>When is your partner's birthday?</Text>
            <Text style={styles.stepSubtitle}>
              Optional - We'll remind you of important dates
            </Text>
            <TextInput
              style={styles.input}
              placeholder="DD-MM-YYYY (e.g., 15-06-1995)"
              value={birthday}
              onChangeText={setBirthday}
            />
          </View>
        );

      case 4:
        return (
          <View style={styles.stepContainer}>
            <Text style={styles.stepTitle}>When is your anniversary?</Text>
            <Text style={styles.stepSubtitle}>
              Optional - We'll help you celebrate special moments
            </Text>
            <TextInput
              style={styles.input}
              placeholder="DD-MM-YYYY (e.g., 14-02-2020)"
              value={anniversary}
              onChangeText={setAnniversary}
            />
          </View>
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
              <TouchableOpacity
                style={styles.backButton}
                onPress={() => setStep(step - 1)}
              >
                <Text style={styles.backButtonText}>Back</Text>
              </TouchableOpacity>
            )}
            
            <TouchableOpacity
              style={styles.nextButton}
              onPress={handleNext}
            >
              <Text style={styles.nextButtonText}>
                {step === 4 ? 'Complete Setup' : 'Next'}
              </Text>
            </TouchableOpacity>
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