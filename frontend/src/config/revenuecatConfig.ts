import Purchases, { LOG_LEVEL } from 'react-native-purchases';
import { Platform } from 'react-native';

export const initializeRevenueCat = async () => {
  try {
    // Set log level for debugging during development
    Purchases.setLogLevel(LOG_LEVEL.VERBOSE);

    // Configure based on platform
    if (Platform.OS === 'android') {
      // Use your Google Play API key from RevenueCat dashboard
      const apiKey = process.env.EXPO_PUBLIC_REVENUECAT_GOOGLE_API_KEY;
      
      if (!apiKey) {
        console.warn('⚠️ RevenueCat API key not found in environment variables');
        return;
      }

      await Purchases.configure({
        apiKey: apiKey,
      });

      console.log('✅ RevenueCat initialized successfully');
    } else if (Platform.OS === 'ios') {
      // For future iOS implementation
      const apiKey = process.env.EXPO_PUBLIC_REVENUECAT_APPLE_API_KEY;
      
      if (apiKey) {
        await Purchases.configure({
          apiKey: apiKey,
        });
        console.log('✅ RevenueCat initialized successfully for iOS');
      }
    }
  } catch (error) {
    console.error('❌ Error initializing RevenueCat:', error);
  }
};

export default initializeRevenueCat;
