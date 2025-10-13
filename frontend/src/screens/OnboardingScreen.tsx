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

  const handleComplete = async () => {
    // Update relationship mode
    await updateRelationshipMode(relationshipMode);

    // Update partner profile
    const partnerProfile = {
      name: partnerName,
      birthday: birthday ? new Date(birthday).toISOString() : undefined,
      anniversary: anniversary ? new Date(anniversary).toISOString() : undefined,
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
              placeholder="YYYY-MM-DD (e.g., 1995-06-15)"
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
              placeholder="YYYY-MM-DD (e.g., 2020-02-14)"
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