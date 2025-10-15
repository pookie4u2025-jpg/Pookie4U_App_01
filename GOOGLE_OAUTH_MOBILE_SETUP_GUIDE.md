# 📱 Google OAuth Setup Guide for Android & iOS Mobile Apps

## Complete Guide for Pookie4u Native Apps

This guide covers setting up Google OAuth for **production Android and iOS apps** (standalone builds), not just Expo Go testing.

---

## 📋 Overview

For mobile apps, you need **3 separate OAuth Client IDs**:
1. **Web Client ID** - For server-side token validation
2. **Android Client ID** - For Android app
3. **iOS Client ID** - For iOS app

---

## 🎯 PART 1: Google Cloud Console Setup

### Step 1: Create Google Cloud Project

1. **Go to Google Cloud Console:**
   - Visit: https://console.cloud.google.com/

2. **Create new project:**
   - Click "Select a project" dropdown at the top
   - Click "NEW PROJECT"
   - **Project name:** Pookie4u
   - Click "CREATE"
   - Wait for creation, then select your project

### Step 2: Enable Required APIs

1. **Navigate to APIs & Services:**
   - Left sidebar → "APIs & Services" → "Library"

2. **Enable Google+ API:**
   - Search for "Google+ API"
   - Click on it → Click "ENABLE"

### Step 3: Configure OAuth Consent Screen

1. **Go to OAuth consent screen:**
   - Left sidebar → "OAuth consent screen"

2. **User Type:**
   - Select **"External"** (unless you have Google Workspace organization)
   - Click "CREATE"

3. **App Information (Screen 1):**
   ```
   App name: Pookie4u
   User support email: [Your email]
   App logo: [Upload your Pookie4u logo - optional]
   Application home page: [Your website - optional for now]
   Application privacy policy: [Your privacy policy URL - optional for now]
   Application terms of service: [Your terms URL - optional for now]
   Authorized domains: [Leave empty for now]
   Developer contact email: [Your email]
   ```
   - Click "SAVE AND CONTINUE"

4. **Scopes (Screen 2):**
   - Click "ADD OR REMOVE SCOPES"
   - Select these scopes:
     - `../auth/userinfo.email`
     - `../auth/userinfo.profile`
     - `openid`
   - Click "UPDATE"
   - Click "SAVE AND CONTINUE"

5. **Test Users (Screen 3):**
   - Click "+ ADD USERS"
   - Add your email address and any test users
   - Click "ADD"
   - Click "SAVE AND CONTINUE"

6. **Summary (Screen 4):**
   - Review your settings
   - Click "BACK TO DASHBOARD"

---

## 🌐 PART 2: Create OAuth Client IDs

### Client ID #1: Web Application (Required)

This is used by your backend to validate tokens.

1. **Create Web Client:**
   - Go to "Credentials" (left sidebar)
   - Click "+ CREATE CREDENTIALS"
   - Select "OAuth client ID"
   - **Application type:** Web application
   - **Name:** Pookie4u Web

2. **Authorized JavaScript origins:**
   ```
   https://auth.expo.io
   http://localhost:3000
   https://romance-inspect.preview.emergentagent.com
   ```

3. **Authorized redirect URIs:**
   ```
   https://auth.expo.io/@anonymous/frontend
   https://auth.expo.io/@your-expo-username/pookie4u
   http://localhost:3000
   https://romance-inspect.preview.emergentagent.com/auth/callback
   ```

4. **Create and Save:**
   - Click "CREATE"
   - **COPY AND SAVE:**
     - ✅ **Client ID** (ends with `.apps.googleusercontent.com`)
     - ✅ **Client Secret**
   - Keep these safe! You'll need them.

---

### Client ID #2: Android Application

#### Step 2.1: Get Your SHA-1 Certificate Fingerprint

**For Development (Debug keystore):**

```bash
# Navigate to your project
cd /app/frontend

# Generate debug SHA-1 (works with Expo)
keytool -list -v -keystore ~/.android/debug.keystore -alias androiddebugkey -storepass android -keypass android

# Copy the SHA1 fingerprint from the output
# It looks like: AB:CD:EF:12:34:56:78:90:AB:CD:EF:12:34:56:78:90:AB:CD:EF:12
```

**For Production (Upload keystore):**

When you build a production Android app, you'll need to generate a production keystore:

```bash
# Generate production keystore
keytool -genkey -v -keystore pookie4u-upload-key.keystore -alias pookie4u-key -keyalg RSA -keysize 2048 -validity 10000

# Get SHA-1 from production keystore
keytool -list -v -keystore pookie4u-upload-key.keystore -alias pookie4u-key

# SAVE THIS KEYSTORE FILE SECURELY! You need it for all future updates.
```

#### Step 2.2: Create Android OAuth Client

1. **In Google Cloud Console:**
   - Go to "Credentials"
   - Click "+ CREATE CREDENTIALS" → "OAuth client ID"
   - **Application type:** Android

2. **Configure Android Client:**
   ```
   Name: Pookie4u Android
   Package name: com.yourcompany.pookie4u
   SHA-1 certificate fingerprint: [Paste your SHA-1 from above]
   ```

3. **Package Name Note:**
   - Use the same package name you'll set in `app.json`
   - Common format: `com.yourcompany.pookie4u`
   - Must be unique and match your app.json exactly

4. **Create:**
   - Click "CREATE"
   - **SAVE the Android Client ID** (you'll need it)

---

### Client ID #3: iOS Application

#### Step 3.1: Determine Your iOS Bundle Identifier

Your bundle identifier should be:
```
com.yourcompany.pookie4u
```
(Same as Android package name but for iOS)

#### Step 3.2: Create iOS OAuth Client

1. **In Google Cloud Console:**
   - Go to "Credentials"
   - Click "+ CREATE CREDENTIALS" → "OAuth client ID"
   - **Application type:** iOS

2. **Configure iOS Client:**
   ```
   Name: Pookie4u iOS
   Bundle ID: com.yourcompany.pookie4u
   App Store ID: [Leave empty for now, add later when published]
   ```

3. **Create:**
   - Click "CREATE"
   - **SAVE the iOS Client ID** (you'll need it)

---

## 🔧 PART 3: Configure Your Expo App

### Step 1: Update app.json

Edit `/app/frontend/app.json`:

```json
{
  "expo": {
    "name": "Pookie4u",
    "slug": "pookie4u",
    "version": "1.0.0",
    "scheme": "pookie4u",
    "owner": "your-expo-username",
    "platforms": ["ios", "android"],
    
    "android": {
      "package": "com.yourcompany.pookie4u",
      "versionCode": 1,
      "adaptiveIcon": {
        "foregroundImage": "./assets/images/pookie4u-logo.png",
        "backgroundColor": "#ffffff"
      },
      "permissions": [
        "INTERNET",
        "ACCESS_NETWORK_STATE"
      ],
      "googleServicesFile": "./google-services.json"
    },
    
    "ios": {
      "bundleIdentifier": "com.yourcompany.pookie4u",
      "buildNumber": "1.0.0",
      "supportsTablet": true,
      "infoPlist": {
        "CFBundleURLTypes": [
          {
            "CFBundleURLSchemes": ["pookie4u"]
          }
        ]
      }
    },
    
    "extra": {
      "eas": {
        "projectId": "your-project-id"
      }
    }
  }
}
```

**Important:**
- Replace `your-expo-username` with your actual Expo username
- Replace `com.yourcompany.pookie4u` with your chosen package name/bundle ID
- Keep it consistent across Android and iOS

### Step 2: Update Environment Variables

#### Backend (.env):
```bash
nano /app/backend/.env
```

Add:
```env
# Web Client ID and Secret (from Step 2, Client #1)
GOOGLE_CLIENT_ID=YOUR_WEB_CLIENT_ID.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=YOUR_WEB_CLIENT_SECRET

# Android Client ID (from Step 2, Client #2)
GOOGLE_ANDROID_CLIENT_ID=YOUR_ANDROID_CLIENT_ID.apps.googleusercontent.com

# iOS Client ID (from Step 2, Client #3)
GOOGLE_IOS_CLIENT_ID=YOUR_IOS_CLIENT_ID.apps.googleusercontent.com
```

#### Frontend (.env):
```bash
nano /app/frontend/.env
```

Add:
```env
# Web Client ID (same as backend)
EXPO_PUBLIC_GOOGLE_CLIENT_ID=YOUR_WEB_CLIENT_ID.apps.googleusercontent.com
EXPO_PUBLIC_GOOGLE_CLIENT_SECRET=YOUR_WEB_CLIENT_SECRET

# Platform-specific Client IDs
EXPO_PUBLIC_GOOGLE_ANDROID_CLIENT_ID=YOUR_ANDROID_CLIENT_ID.apps.googleusercontent.com
EXPO_PUBLIC_GOOGLE_IOS_CLIENT_ID=YOUR_IOS_CLIENT_ID.apps.googleusercontent.com
```

### Step 3: Update GoogleOAuthService.ts

Edit `/app/frontend/src/services/GoogleOAuthService.ts`:

Find the configuration section and update it to use platform-specific client IDs:

```typescript
import { Platform } from 'react-native';
import Constants from 'expo-constants';

// Get platform-specific client ID
const getClientId = () => {
  if (Platform.OS === 'android') {
    return Constants.expoConfig?.extra?.EXPO_PUBLIC_GOOGLE_ANDROID_CLIENT_ID || 
           process.env.EXPO_PUBLIC_GOOGLE_ANDROID_CLIENT_ID;
  } else if (Platform.OS === 'ios') {
    return Constants.expoConfig?.extra?.EXPO_PUBLIC_GOOGLE_IOS_CLIENT_ID || 
           process.env.EXPO_PUBLIC_GOOGLE_IOS_CLIENT_ID;
  }
  // Web fallback
  return Constants.expoConfig?.extra?.EXPO_PUBLIC_GOOGLE_CLIENT_ID || 
         process.env.EXPO_PUBLIC_GOOGLE_CLIENT_ID;
};
```

---

## 📱 PART 4: Build and Test

### For Expo Go Development Testing:

```bash
# Restart services
sudo supervisorctl restart backend
sudo supervisorctl restart expo

# Test in Expo Go app
# Note: OAuth might have limitations in Expo Go
```

### For Production/Standalone Builds:

#### Build Android APK:
```bash
# Install EAS CLI if not already installed
npm install -g eas-cli

# Login to Expo
eas login

# Configure EAS
cd /app/frontend
eas build:configure

# Build Android
eas build --platform android --profile preview
```

#### Build iOS App:
```bash
# Build iOS (requires Apple Developer account)
eas build --platform ios --profile preview
```

#### Test the builds:
- Download the APK/IPA
- Install on your device
- Test Google Sign-In
- Should open native Google sign-in flow

---

## ✅ Verification Checklist

After setup, verify:

- [ ] Web Client ID created with correct redirect URIs
- [ ] Android Client ID created with correct package name and SHA-1
- [ ] iOS Client ID created with correct bundle identifier
- [ ] All Client IDs added to backend .env
- [ ] All Client IDs added to frontend .env
- [ ] app.json updated with correct package names
- [ ] OAuth consent screen configured
- [ ] Test users added (for testing mode)
- [ ] Services restarted

---

## 🧪 Testing Flow

### Test on Android:
1. Build and install Android APK
2. Open app → Click "Sign in with Google"
3. Should show native Google account picker
4. Select account → Grant permissions
5. Should redirect back to app and sign in successfully

### Test on iOS:
1. Build and install iOS app (via TestFlight or direct install)
2. Open app → Click "Sign in with Google"
3. Should show native Google sign-in
4. Complete authentication
5. Should return to app signed in

---

## 🚨 Common Issues & Solutions

### Issue: "Error 10: Developer Error"
**Solution:** SHA-1 fingerprint doesn't match or package name is wrong
- Verify SHA-1 fingerprint is correct
- Ensure package name in app.json matches Google Console
- Make sure you're using the right keystore (debug vs production)

### Issue: "redirect_uri_mismatch"
**Solution:** Redirect URI not authorized
- Add the exact redirect URI from error message to Google Console
- For mobile: Use `com.yourcompany.pookie4u:/oauth2redirect/google`

### Issue: "The app is not configured to use Google Sign-In"
**Solution:** Client IDs don't match
- Verify you're using the correct client ID for the platform
- Check that environment variables are loaded correctly

### Issue: OAuth works in Expo Go but not in standalone build
**Solution:** Different client IDs needed
- Expo Go uses web client ID
- Standalone apps need platform-specific client IDs
- Make sure you created all 3 client IDs

---

## 🔐 Security Best Practices

1. **Protect Your Keystores:**
   - Never commit keystore files to git
   - Store production keystore securely (you need it for all future updates)
   - Back up keystores in a secure location

2. **Protect Client Secrets:**
   - Never commit .env files with real secrets
   - Use environment variables in production
   - Rotate secrets if compromised

3. **OAuth Consent Screen:**
   - Keep app name and details updated
   - Provide privacy policy when publishing
   - Submit for verification if using sensitive scopes

4. **Test Users:**
   - Keep test user list updated
   - Remove test users before publishing (switch to production mode)

---

## 📊 Summary: What You Need

| Item | Where to Get | Where to Add |
|------|--------------|--------------|
| Web Client ID | Google Console → Web OAuth | Backend & Frontend .env |
| Web Client Secret | Google Console → Web OAuth | Backend & Frontend .env |
| Android Client ID | Google Console → Android OAuth | Frontend .env |
| iOS Client ID | Google Console → iOS OAuth | Frontend .env |
| SHA-1 Fingerprint | keytool command | Google Console → Android OAuth |
| Package Name | Choose unique name | app.json + Google Console |
| Bundle Identifier | Same as package name | app.json + Google Console |

---

## 🚀 Production Deployment

When ready for production:

1. **Publish OAuth Consent Screen:**
   - Go to OAuth consent screen
   - Click "PUBLISH APP"
   - May require verification for sensitive scopes

2. **Generate Production Keystores:**
   - Create production Android keystore
   - Update SHA-1 in Google Console
   - Configure iOS certificates in Apple Developer

3. **Update Redirect URIs:**
   - Add production domain URLs
   - Update authorized domains

4. **Build Production Apps:**
   ```bash
   eas build --platform android --profile production
   eas build --platform ios --profile production
   ```

5. **Submit to Stores:**
   - Google Play Store (Android)
   - Apple App Store (iOS)

---

## 📞 Need Help?

- **Google Console Issues:** https://console.cloud.google.com/support
- **Expo EAS Build:** https://docs.expo.dev/build/setup/
- **OAuth Debugging:** Check logs in Expo console and Google Cloud Console

---

## ✨ Quick Start Commands

```bash
# 1. Update environment files
nano /app/backend/.env
nano /app/frontend/.env

# 2. Update app.json
nano /app/frontend/app.json

# 3. Restart services
sudo supervisorctl restart backend
sudo supervisorctl restart expo

# 4. Build for testing
cd /app/frontend
eas build --platform android --profile preview

# 5. Test on device
# Download APK and install
```

---

**Your app is now configured for Google OAuth on Android and iOS! 🎉**

Follow this guide step by step, and you'll have fully functional Google authentication on both platforms.
