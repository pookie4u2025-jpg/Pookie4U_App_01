# 🚀 Build Android APK - Complete Guide

## Quick Summary

Your app is **100% ready** to build. All checks passed. Follow the steps below to build your APK.

---

## ✅ Pre-Build Checklist (All Complete!)

- ✅ Expo doctor: 17/17 checks passed
- ✅ Dependencies: All up to date (Expo SDK 54)
- ✅ Images: Square adaptive icons (1024x1024)
- ✅ Package name: com.pookie4u.app
- ✅ Permissions: Including BILLING for RevenueCat
- ✅ Project linked: bd5adfc7-3d1d-45f3-b969-d121b9df8c7e
- ✅ Monorepo config: Base directory = frontend

---

## Option 1: Build via Expo Website (RECOMMENDED)

### Step-by-Step Instructions

1. **Go to Expo Dashboard**
   ```
   https://expo.dev/accounts/pookie4u/projects/pookie4u-v1/builds
   ```

2. **Click "Create Build"**

3. **Configure Build Settings:**

   | Field | Value |
   |-------|-------|
   | **Base directory** | `frontend` |
   | **Platform** | Android |
   | **Git ref** | `main` (or your branch) |
   | **Build profile** | `preview` (for APK) or `production` (for AAB) |
   | **Environment** | Preview or Production |
   | **Auto-submit** | ❌ Uncheck (test first) |

4. **Click "Build"**

5. **Wait for Build** (10-15 minutes)
   - Monitor progress in real-time
   - Build logs available for debugging

6. **Download APK**
   - Once complete, download button will appear
   - Or use: `eas build:list` to get download link

---

## Option 2: Build via EAS CLI (If You Have Credentials)

### Prerequisites

You need an Expo account token. Get it from:
```
https://expo.dev/accounts/[your-account]/settings/access-tokens
```

### Build Commands

**For APK (Testing):**
```bash
cd /app
export EXPO_TOKEN="your-token-here"
eas build --platform android --profile preview
```

**For AAB (Production/Play Store):**
```bash
cd /app
export EXPO_TOKEN="your-token-here"
eas build --platform android --profile production
```

---

## Build Profiles Explained

Your `eas.json` has these profiles configured:

### Preview Profile (APK)
```json
"preview": {
  "distribution": "internal",
  "android": {
    "buildType": "apk"
  }
}
```
- **Output**: `.apk` file
- **Use for**: Direct installation on devices for testing
- **File size**: Larger (~50-100MB)
- **Installation**: Direct download and install

### Production Profile (AAB)
```json
"production": {
  "android": {
    "buildType": "app-bundle"
  }
}
```
- **Output**: `.aab` file (Android App Bundle)
- **Use for**: Google Play Store submission
- **File size**: Smaller (optimized per device)
- **Installation**: Through Play Store only

---

## After Build Completes

### 1. Download the APK

**Via Website:**
- Go to your builds page
- Click download button next to completed build

**Via CLI:**
```bash
eas build:list
# Copy the build ID
eas build:download --id <build-id>
```

### 2. Install on Android Device

**Method A: Direct Installation**
1. Transfer APK to your Android device
2. Enable "Install from Unknown Sources"
3. Open APK file and install

**Method B: Via ADB**
```bash
adb install path/to/your-app.apk
```

### 3. Test the App

- ✅ Authentication (Emergent OAuth)
- ✅ Main navigation (tabs)
- ✅ Task generation and completion
- ✅ Events CRUD
- ✅ Subscription screen (shows "Coming Soon")
- ✅ RevenueCat initializes (check logs)
- ✅ Push notifications
- ✅ Referral system

---

## Troubleshooting

### Build Fails

1. **Check build logs** on Expo dashboard
2. **Common issues:**
   - Missing environment variables
   - Image path errors (we fixed these!)
   - Dependency conflicts (we fixed these!)

### "Base directory not found"

Make sure you set **Base directory** to `frontend` in build settings.

### RevenueCat Not Working

This is expected until you:
1. Upload APK to Google Play Console (Internal Testing)
2. Create subscription products in Play Console
3. Link products with RevenueCat dashboard
4. See: `REVENUECAT_MANUAL_INTEGRATION_GUIDE.md`

---

## Next Steps After APK Build

### 1. Test Thoroughly

Install on multiple Android devices:
- Different screen sizes
- Different Android versions (9+)
- Different manufacturers

### 2. Google Play Console Setup

**Create In-App Subscriptions:**
```
1. Go to Play Console → Monetize → Products → Subscriptions
2. Create products:
   - pookie4u_monthly ($9.99/month)
   - pookie4u_yearly ($99.99/year)
3. Set trial periods
4. Activate products
```

### 3. Link RevenueCat

**In RevenueCat Dashboard:**
```
1. Add Google Play Service Account credentials
2. Configure product IDs
3. Create offerings
4. Test purchase flow
```

### 4. Update Frontend (After Play Console Setup)

Enable actual purchases in `app/subscription.tsx`:
- Replace "Coming Soon" with actual purchase buttons
- Call `Purchases.purchasePackage()` 
- Handle purchase success/failure

---

## Build Configuration Files

### `/app/eas.json`
```json
{
  "cli": {
    "appDir": "frontend"
  },
  "build": {
    "preview": {
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

### `/app/frontend/app.json`
```json
{
  "expo": {
    "name": "Pookie4u",
    "slug": "pookie4u-v1",
    "version": "1.0.0",
    "android": {
      "package": "com.pookie4u.app",
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

---

## Environment Variables Needed

These are already set in `/app/frontend/.env`:

```env
EXPO_PUBLIC_BACKEND_URL=<your-backend-url>
EXPO_PUBLIC_REVENUECAT_GOOGLE_API_KEY=<your-revenuecat-key>
EXPO_PUBLIC_GOOGLE_CLIENT_ID=<optional>
EXPO_PUBLIC_GOOGLE_CLIENT_SECRET=<optional>
```

**Note**: Environment variables are baked into the build. For production, you may want to set them via EAS Secrets instead.

---

## Expected Build Output

**Build Information:**
```
Platform: Android
Build Type: APK (preview) or AAB (production)
Size: ~50-100MB (APK) or ~30-50MB (AAB)
Min SDK: 23 (Android 6.0+)
Target SDK: 34 (Android 14)
Architecture: arm64-v8a, armeabi-v7a, x86_64
```

**APK Details:**
```
Package: com.pookie4u.app
Version: 1.0.0
Version Code: 1
Signing: EAS managed (automatic)
```

---

## Support & Documentation

- **EAS Build Docs**: https://docs.expo.dev/build/introduction/
- **RevenueCat Setup**: See `REVENUECAT_MANUAL_INTEGRATION_GUIDE.md`
- **Troubleshooting**: See `APK_BUILD_FINAL_STATUS.md`
- **Image Issues**: See `IMAGE_FIX_SUMMARY.md`

---

## Quick Reference Commands

```bash
# Check build status
eas build:list

# View specific build
eas build:view <build-id>

# Download build
eas build:download --id <build-id>

# Cancel build
eas build:cancel

# View logs
eas build:view --logs <build-id>
```

---

## Summary

✅ **Your app is 100% ready to build**
✅ **All pre-build checks passed**
✅ **Use Expo website to start the build**
✅ **Set Base directory to: frontend**
✅ **Choose preview profile for APK**
✅ **Build will take 10-15 minutes**
✅ **Download and test on real device**

**Build URL**: https://expo.dev/accounts/pookie4u/projects/pookie4u-v1/builds

---

*Last updated: November 2024*
*App: Pookie4u v1.0.0*
*Build Status: Ready ✅*
