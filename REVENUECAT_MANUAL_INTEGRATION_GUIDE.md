# RevenueCat Manual Integration Guide for Pookie4u

## Background

The `react-native-purchases` package (RevenueCat SDK v9.6.2) cannot be automatically integrated via Expo config plugins due to compatibility issues with the current Expo SDK version. This guide explains how to proceed with the build and subscription implementation.

## Issue Summary

- **Problem**: The RevenueCat plugin throws `SyntaxError: Unexpected token 'typeof'` during `expo prebuild`
- **Root Cause**: The plugin export format is incompatible with Expo's plugin loader in SDK 54
- **Solution**: Remove the plugin from `app.json` and manually configure native dependencies post-build

## Current Status

✅ **Completed:**
- RevenueCat package installed (`react-native-purchases@^9.6.2`)
- Frontend code implemented with RevenueCat SDK calls
- Google Play Billing permission added to `app.json`
- RevenueCat API key configured in `.env`

❌ **Removed from app.json:**
- `"react-native-purchases"` plugin (to allow build to proceed)

## Build Configuration

### app.json (Current)
```json
{
  "expo": {
    "plugins": [
      "expo-router",
      "expo-font",
      "expo-web-browser"
    ],
    "android": {
      "permissions": [
        "NOTIFICATIONS",
        "INTERNET",
        "ACCESS_NETWORK_STATE",
        "com.android.vending.BILLING"
      ]
    }
  }
}
```

## Option 1: EAS Build with Managed Workflow (Recommended)

Since you're using EAS Build, the native modules will be automatically linked during the cloud build process.

### Steps:

1. **Verify the current configuration is committed:**
   ```bash
   git status
   ```

2. **Build via EAS:**
   ```bash
   cd frontend
   eas build --platform android --profile production
   ```

3. **EAS will automatically:**
   - Run `expo prebuild` (which will succeed now)
   - Link `react-native-purchases` native module via autolinking
   - Include Google Play Billing libraries
   - Generate the APK with all dependencies

## Option 2: Local Build with Development Client

If you need to build locally for testing:

### Steps:

1. **Prebuild the native project:**
   ```bash
   cd frontend
   expo prebuild --clean --platform android
   ```

2. **Verify native linking:**
   Check that `react-native-purchases` is linked:
   ```bash
   grep -r "react-native-purchases" android/app/build.gradle
   ```

3. **Build locally:**
   ```bash
   cd android
   ./gradlew assembleRelease
   ```

## Verifying RevenueCat Integration

After building, verify the integration works:

### 1. Check Purchases SDK Initialization

In `frontend/app/_layout.tsx`:
```typescript
import Purchases from 'react-native-purchases';

useEffect(() => {
  if (Platform.OS === 'android') {
    Purchases.configure({
      apiKey: process.env.EXPO_PUBLIC_REVENUECAT_GOOGLE_API_KEY!
    });
  }
}, []);
```

### 2. Test Subscription Screen

The subscription screen (`frontend/app/subscription.tsx`) should:
- Display "Coming Soon" for paid plans (current implementation)
- Show the 14-day free trial option
- Not crash when attempting to fetch offerings

### 3. Check Logs

Look for RevenueCat initialization in logs:
```bash
adb logcat | grep -i "revenuecat\|purchases"
```

## Post-Build Configuration

After a successful build, you'll need to:

### 1. Google Play Console Setup

1. Upload your APK/AAB to Google Play Console (Internal Testing)
2. Create In-App Products:
   - Navigate to: Monetize > Products > Subscriptions
   - Create subscription products matching your tiers:
     - **Monthly**: `pookie4u_monthly` - $9.99/month
     - **Yearly**: `pookie4u_yearly` - $99.99/year

### 2. Link RevenueCat with Google Play

1. Go to RevenueCat Dashboard
2. Navigate to your Android app settings
3. Add Google Play credentials:
   - Service account JSON (from Google Cloud Console)
   - Link the subscription products

### 3. Enable Subscription Features in Frontend

Once everything is configured, update `frontend/app/subscription.tsx`:

Replace:
```typescript
{/* Coming Soon - Payment integration pending */}
```

With actual purchase flow:
```typescript
const handlePurchase = async (packageId: string) => {
  try {
    const offerings = await Purchases.getOfferings();
    if (offerings.current) {
      const purchasePackage = offerings.current.availablePackages.find(
        pkg => pkg.identifier === packageId
      );
      if (purchasePackage) {
        await Purchases.purchasePackage(purchasePackage);
        // Handle successful purchase
      }
    }
  } catch (error) {
    console.error('Purchase failed:', error);
  }
};
```

## Testing Checklist

- [ ] APK builds successfully via EAS
- [ ] App installs on Android device
- [ ] Subscription screen loads without crashing
- [ ] RevenueCat SDK initializes (check logs)
- [ ] Free trial activation works
- [ ] Google Play products appear (after Play Console setup)
- [ ] Test purchase flow (use test account)

## Troubleshooting

### Build Still Fails

If prebuild fails even after removing the plugin:
1. Clear Expo cache: `expo start -c`
2. Clear EAS cache: Build with `--clear-cache` flag
3. Check for other missing assets

### RevenueCat Not Working Post-Build

1. **Verify API Key**: Check `.env` file has correct key
2. **Check Package Name**: Must match Google Play Console
   - Current: `com.pookie4u.app`
3. **Billing Permission**: Verify in `app.json` android permissions
4. **Service Account**: Ensure RevenueCat has valid Google credentials

### Subscription Products Not Loading

1. **Check RevenueCat Dashboard**: Ensure offerings are configured
2. **Verify Product IDs**: Must match Google Play product IDs exactly
3. **Test Mode**: Use RevenueCat test mode for development
4. **Network**: Ensure device has internet connection

## Alternative Approach: Use expo-in-app-purchases

If RevenueCat continues to cause issues, you can use Expo's built-in module:

```bash
npx expo install expo-in-app-purchases
```

This has native Expo support and doesn't require custom plugins.

## Support

For RevenueCat-specific issues:
- [RevenueCat Docs](https://docs.revenuecat.com/docs/reactnative)
- [GitHub Issues](https://github.com/RevenueCat/react-native-purchases/issues)

For Expo build issues:
- [Expo EAS Build Docs](https://docs.expo.dev/build/introduction/)

## Next Steps

1. ✅ Commit current changes (DONE)
2. 🔄 Build APK via EAS (IN PROGRESS)
3. ⏳ Test on real device
4. ⏳ Configure Google Play Console products
5. ⏳ Link RevenueCat with Play Console
6. ⏳ Enable live subscription purchases

---

**Note**: The app will build and run successfully without the RevenueCat plugin in `app.json`. The native module will still be linked via React Native's autolinking during the EAS build process.
