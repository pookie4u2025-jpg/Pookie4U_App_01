# 📱 Build Development APK with Google OAuth Support

This guide will help you build a development APK that has full Google OAuth functionality.

## Prerequisites

1. **Expo Account**: You need an Expo account
2. **EAS CLI**: Already installed ✅
3. **Google OAuth Credentials**: Already configured ✅

## Step-by-Step Build Process

### Step 1: Login to Expo Account

```bash
cd /app/frontend
eas login
```

Enter your Expo credentials when prompted.

### Step 2: Configure the Project

The project is already configured with:
- ✅ `eas.json` - Build configuration
- ✅ `app.json` - App metadata
- ✅ Android package: `com.pookie4u.app`
- ✅ Google OAuth credentials in `.env`

### Step 3: Build Development APK

Run this command to start the build:

```bash
cd /app/frontend
eas build --profile development --platform android
```

**What happens:**
1. EAS will ask if you want to create a new project - say **Yes**
2. It will generate Android keystore automatically
3. Build will happen on Expo's cloud servers
4. Takes approximately 15-20 minutes

### Step 4: Install the APK

Once the build completes:

1. **Download the APK**:
   - EAS will provide a download link
   - Or visit: https://expo.dev/accounts/YOUR_ACCOUNT/projects/pookie4u-v1/builds

2. **Install on your device**:
   - Transfer APK to your Android device
   - Enable "Install from Unknown Sources" in Settings
   - Tap the APK file to install

3. **Open the app**:
   - Launch Pookie4u from your app drawer
   - Google OAuth will work perfectly! 🎉

## Google Console Configuration

Make sure your Google OAuth redirect URIs include:

### For Development Build:
```
com.pookie4u.app:/oauthredirect
```

### How to Add:
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project
3. Go to "APIs & Services" → "Credentials"
4. Click on your OAuth 2.0 Client ID
5. Under "Authorized redirect URIs", add:
   - `com.pookie4u.app:/oauthredirect`
6. Save changes

## Testing Google OAuth

After installing the development build:

1. Open the app
2. Click "Sign in with Google"
3. Browser will open with Google sign-in
4. Sign in with your Google account
5. App will receive the OAuth token
6. You'll be logged in successfully! ✅

## Troubleshooting

### Build Fails
- Check your Expo account has available builds
- Ensure you're logged in: `eas whoami`
- Try: `eas build:configure`

### Google OAuth Still Fails
- Verify redirect URI in Google Console
- Check that package name matches: `com.pookie4u.app`
- Ensure Client ID is correct in `.env`

### App Won't Install
- Enable "Unknown Sources" in Android Settings
- Check you have enough storage space
- Try uninstalling any previous version

## Next Steps

After successful build:
1. Test all features including Google OAuth
2. Share APK with friends for testing
3. When ready for production, build with: `eas build --profile production --platform android`

## Need Help?

If you encounter issues:
1. Check build logs on Expo dashboard
2. Verify Google Console configuration
3. Ensure `.env` has correct credentials

---

**Build Command Reference:**
```bash
# Development build (what you need now)
eas build --profile development --platform android

# Preview build (for testing, smaller size)
eas build --profile preview --platform android

# Production build (for Play Store)
eas build --profile production --platform android
```
