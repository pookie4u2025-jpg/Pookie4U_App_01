# 📱 EAS Build Guide - Native App Creation

## Overview

This guide will help you build native Android and iOS apps using Expo Application Services (EAS). You'll get installable APK/IPA files that work without Expo Go.

---

## ✅ Prerequisites (Already Configured!)

- ✅ EAS CLI installed (v16.27.0)
- ✅ EAS project configured (Project ID: bd5adfc7-3d1d-45f3-b969-d121b9df8c7e)
- ✅ App bundle ID set: `com.pookie4u.app`
- ✅ Build profiles configured (development, preview, production)

---

## 🚀 Quick Start - Build Your App Now

### Step 1: Login to Expo Account

You need to be logged into your Expo account to build:

```bash
cd /app/frontend
eas login
```

**Enter your Expo credentials:**
- Email: [Your Expo account email]
- Password: [Your Expo account password]

**Don't have an Expo account?**
- Create one at: https://expo.dev/signup
- It's free for personal projects!

---

### Step 2: Build Preview APK for Android (Recommended for Testing)

This builds an APK you can install directly on Android devices:

```bash
cd /app/frontend
eas build --platform android --profile preview
```

**What happens:**
1. ✅ Code is uploaded to EAS servers
2. ✅ Android APK is built in the cloud (~10-15 minutes)
3. ✅ You get a download link for the APK
4. ✅ Install APK on any Android phone!

**Build output:**
- File: `Pookie4u-1.0.0.apk` (or similar)
- Size: ~50-80 MB
- Install: Download on phone and tap to install

---

### Step 3: Build for iOS (Optional - Requires Apple Developer Account)

**For iOS Simulator (Mac only):**
```bash
eas build --platform ios --profile preview
```

**For iOS Device (Requires Apple Developer account - $99/year):**
```bash
eas build --platform ios --profile production
```

**Note:** iOS builds are more complex:
- Need Apple Developer Program membership ($99/year)
- Need certificates and provisioning profiles
- Simulator builds work without Apple account (Mac only)

---

## 📋 Build Profiles Explained

### 1. **Preview** (Recommended for Testing)
```bash
eas build --platform android --profile preview
```

**Best for:**
- ✅ Quick testing on real devices
- ✅ Sharing with beta testers
- ✅ Internal distribution
- ✅ No Google Play required

**Output:** APK file you can install directly

---

### 2. **Production** (For App Stores)
```bash
eas build --platform android --profile production
```

**Best for:**
- ✅ Publishing to Google Play Store
- ✅ Publishing to Apple App Store
- ✅ Official releases

**Output:** AAB (Android App Bundle) for Google Play

---

### 3. **Development** (Advanced - Custom Dev Client)
```bash
eas build --platform android --profile development
```

**Best for:**
- Advanced debugging
- Custom native modules testing
- Not needed for most cases

---

## 🎯 Recommended First Build

**For immediate testing on Android:**

```bash
cd /app/frontend

# Login (if not already logged in)
eas login

# Build preview APK
eas build --platform android --profile preview
```

**Timeline:**
- Upload: 1-2 minutes
- Build: 10-15 minutes
- Download: 1-2 minutes

**Total time: ~15-20 minutes**

---

## 📱 Installing the Built App

### Android Installation

1. **Download APK** from EAS build link
2. **Transfer to phone** (via email, cloud drive, or direct download)
3. **Enable "Install from Unknown Sources"** in phone settings
4. **Tap APK file** to install
5. **Open Pookie4u app** from app drawer
6. **Test all features!** ✅

### iOS Installation (TestFlight)

1. **Download IPA** from EAS build
2. **Submit to TestFlight** (Apple's beta testing platform)
3. **Invite testers** via email
4. **Install via TestFlight app** on iPhone
5. **Test on real devices!** ✅

---

## 🔧 Build Configuration Details

Your current configuration (`/app/frontend/eas.json`):

```json
{
  "build": {
    "preview": {
      "distribution": "internal",
      "android": {
        "buildType": "apk"
      }
    },
    "production": {
      "android": {
        "buildType": "app-bundle"
      }
    }
  }
}
```

**What this means:**
- **Preview builds** → APK (installable directly)
- **Production builds** → AAB (for Google Play Store)

---

## 🌐 Backend API Configuration

**IMPORTANT:** Before building, ensure your app points to the **production backend**, not localhost.

### Current Backend URL

Check `/app/frontend/.env`:
```bash
cat /app/frontend/.env | grep EXPO_PUBLIC_API_URL
```

**For production builds, you'll need to:**

1. **Deploy backend to production** (see `/app/DEPLOYMENT_GUIDE.md`)
2. **Update `.env` with production URL:**
   ```
   EXPO_PUBLIC_API_URL=https://your-production-api.com
   ```
3. **Rebuild the app** with new URL

**For testing preview builds, you can use:**
- Production backend URL (recommended)
- Or keep development URL if accessible

---

## 📊 Build Monitoring

### Check Build Status

```bash
# View all builds
eas build:list

# View specific build
eas build:view [build-id]
```

### Build Dashboard

View builds in browser:
- https://expo.dev/accounts/pookie4u/projects/pookie4u-v1/builds

---

## ⚡ Quick Commands Reference

```bash
# Login to Expo
eas login

# Check who's logged in
eas whoami

# Build Android APK (preview)
eas build --platform android --profile preview

# Build Android AAB (production)
eas build --platform android --profile production

# Build iOS (simulator)
eas build --platform ios --profile preview

# List all builds
eas build:list

# View specific build
eas build:view [build-id]

# Cancel running build
eas build:cancel [build-id]
```

---

## 🐛 Troubleshooting

### Issue: "Not logged in"

**Solution:**
```bash
eas login
```

### Issue: "Project not configured"

**Solution:**
```bash
eas build:configure
```

### Issue: Build fails with "Missing credentials"

**For Android:**
- EAS auto-generates Android keystore (first time)
- Accept default options when prompted

**For iOS:**
- Need Apple Developer account
- Run: `eas credentials`
- Follow prompts to configure

### Issue: "Build takes too long"

**Normal build times:**
- Android: 10-15 minutes
- iOS: 15-25 minutes

**If stuck for >30 minutes:**
- Check build logs on expo.dev
- Cancel and retry: `eas build:cancel [build-id]`

---

## 🎉 Success Checklist

After successful build:

- [ ] Download APK/IPA from build link
- [ ] Install on physical device
- [ ] Test Google OAuth login
- [ ] Test profile picture persistence
- [ ] Test phone number saving
- [ ] Test all major features
- [ ] Share with beta testers
- [ ] Collect feedback
- [ ] Ready for app store submission!

---

## 📤 Submitting to App Stores (Next Steps)

### Google Play Store

```bash
# Build production AAB
eas build --platform android --profile production

# Submit to Google Play
eas submit --platform android
```

**Requirements:**
- Google Play Developer account ($25 one-time fee)
- App description, screenshots, privacy policy
- Content rating questionnaire

### Apple App Store

```bash
# Build production IPA
eas build --platform ios --profile production

# Submit to App Store
eas submit --platform ios
```

**Requirements:**
- Apple Developer Program ($99/year)
- App description, screenshots, privacy policy
- App Review Guidelines compliance

---

## 💡 Pro Tips

1. **Test preview builds first** before production
2. **Keep build logs** for debugging
3. **Use semantic versioning** (1.0.0, 1.0.1, etc.)
4. **Test on multiple devices** before store submission
5. **Update backend URL** for production builds
6. **Enable auto-updates** with EAS Update for quick fixes

---

## 🆘 Need Help?

**EAS Documentation:**
- https://docs.expo.dev/build/introduction/

**Expo Discord:**
- https://chat.expo.dev/

**EAS Dashboard:**
- https://expo.dev/

---

## 🚀 Ready to Build?

Run this now:

```bash
cd /app/frontend
eas login
eas build --platform android --profile preview
```

Then wait ~15 minutes for your APK download link! 🎉

---

**Your app is ready to be built into native Android and iOS apps!**
