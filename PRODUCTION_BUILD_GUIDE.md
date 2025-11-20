# 🚀 Pookie4u Production Build Guide

This guide will help you create a production-ready APK/AAB for Google Play Store.

---

## 📋 Prerequisites

- Expo account (create at https://expo.dev/signup)
- Google Play Console account (for publishing)
- Android package name: `com.pookie4u.app`

---

## 🔐 Step 1: Login to EAS

Run this command in your terminal:

```bash
cd /app/frontend
eas login
```

**What you'll need:**
- Your Expo account email
- Your Expo account password

---

## 🏗️ Step 2: Build for Android Production

### Option A: Build APK (For Testing)

```bash
eas build --platform android --profile preview
```

**What this creates:**
- APK file (Android Package)
- Can be installed directly on Android devices
- Good for testing before Play Store submission
- File size: ~50-100MB

### Option B: Build AAB (For Play Store)

```bash
eas build --platform android --profile production
```

**What this creates:**
- AAB file (Android App Bundle)
- Required for Google Play Store
- Optimized for different device configurations
- Smaller download size for users

---

## ⏱️ Build Process Timeline

1. **Upload** (~2-5 minutes)
   - Your code is uploaded to EAS servers

2. **Build** (~15-25 minutes)
   - EAS compiles your app
   - Generates signed APK/AAB

3. **Complete**
   - Download link provided
   - File stored for 30 days

**During the build, you can:**
- Close the terminal (build continues)
- Check status: `eas build:list`
- View online: https://expo.dev/accounts/pookie4u/projects/pookie4u-v1/builds

---

## 📦 Step 3: Download Your Build

Once the build completes, you'll get:

**Via Terminal:**
```
✅ Build finished successfully!
📦 Download: https://expo.dev/artifacts/eas/...
```

**Via Web:**
- Visit: https://expo.dev/accounts/pookie4u/projects/pookie4u-v1/builds
- Click on your build
- Download APK/AAB

---

## 🎯 Step 4: Test Your APK (Before Play Store)

### Install on Android Device:

1. **Download APK** to your Android phone
2. **Enable "Install Unknown Apps"**:
   - Settings → Security → Unknown Sources
   - Or: Settings → Apps → Browser → Install Unknown Apps
3. **Tap the APK file** to install
4. **Test all features**:
   - Login with Google (Emergent OAuth)
   - Profile creation
   - Task generation
   - Gamification features

---

## 📱 Step 5: Upload to Google Play Store

### 5.1 Create App in Play Console

1. Go to: https://play.google.com/console
2. Click **"Create app"**
3. Fill in details:
   - **App name**: Pookie4u
   - **Default language**: English (United States)
   - **App or game**: App
   - **Free or paid**: Free

### 5.2 Complete Store Listing

Required information:
- **App name**: Pookie4u
- **Short description**: (50 characters)
  "AI-powered relationship tasks for couples"
- **Full description**: (4000 characters max)
  ```
  Pookie4u helps couples strengthen their relationship through personalized, 
  AI-generated tasks and activities. Whether you live together, meet daily, 
  or are in a long-distance relationship, Pookie4u creates tailored 
  experiences just for you.

  KEY FEATURES:
  • Daily relationship tasks
  • Weekly challenges
  • Gamification with points and streaks
  • Profile customization
  • Progress tracking
  
  Perfect for couples who want to:
  ✨ Keep their relationship fresh and exciting
  ✨ Build stronger emotional connections
  ✨ Track their journey together
  ✨ Make relationship-building fun and rewarding
  ```

- **Screenshots**: (Required - at least 2)
  - Phone screenshots (1080x1920 or 1080x2340)
  - Take from your app running on device

- **Feature graphic**: (1024x500 pixels)
- **App icon**: (512x512 pixels) - Already at `assets/images/icon.png`

### 5.3 Upload AAB

1. In Play Console → **Production** → **Create new release**
2. Click **"Upload"**
3. Select your **AAB file** (from EAS build)
4. Add **Release notes**:
   ```
   Initial release of Pookie4u
   - Google OAuth login
   - Personalized relationship tasks
   - Gamification system
   - Profile management
   ```

### 5.4 Content Rating

1. Go to **"Content rating"**
2. Fill out questionnaire
3. Select appropriate rating

### 5.5 Set Up Pricing & Distribution

1. **Pricing**: Free
2. **Countries**: Select all or specific
3. **Content guidelines**: Accept

---

## 🔑 Step 6: Set Up Subscriptions (If Using RevenueCat)

### 6.1 Create Products in Play Console

1. Go to **Monetization** → **Products** → **Subscriptions**
2. Click **"Create subscription"**
3. Create products:

**Premium Monthly:**
- Product ID: `premium_monthly`
- Name: Premium Monthly
- Description: Monthly subscription to premium features
- Price: $9.99/month

**Premium Yearly:**
- Product ID: `premium_yearly`
- Name: Premium Yearly
- Description: Yearly subscription to premium features
- Price: $99.99/year

### 6.2 Configure in RevenueCat

1. Go to: https://app.revenuecat.com
2. Add Google Play product IDs
3. Map to RevenueCat entitlements

---

## 📊 Step 7: Submit for Review

1. **Review release**: Check all sections have green checkmarks
2. Click **"Start rollout to Production"**
3. **Review time**: Typically 3-7 days

**Status tracking:**
- Draft → In review → Approved → Published

---

## 🔄 Step 8: Future Updates

When you need to update the app:

### Update version in app.json:
```json
{
  "expo": {
    "version": "1.0.1",
    "android": {
      "versionCode": 2
    }
  }
}
```

### Build new version:
```bash
eas build --platform android --profile production
```

### Upload to Play Console:
- Production → Create new release
- Upload new AAB
- Add release notes
- Submit

---

## 🆘 Troubleshooting

### Build Fails

**Error: "Credentials not configured"**
```bash
eas credentials
```
Select Android → Set up credentials

**Error: "Build failed during compilation"**
- Check logs: `eas build:view [build-id]`
- Common issues: missing dependencies, incorrect versions

### APK Won't Install

- Enable "Install Unknown Apps" in Android settings
- Check if package name matches: `com.pookie4u.app`
- Try uninstalling old version first

### Play Store Rejection

Common reasons:
- Incomplete store listing
- Missing privacy policy
- Invalid screenshots
- Content policy violations

**Solution**: Address issues in rejection email and resubmit

---

## 📝 Important Notes

### Signing Keys
- EAS automatically manages signing keys
- Keys stored securely in Expo servers
- Same key used for all future builds

### Bundle Size
- AAB: ~30-50MB (optimized by Play Store)
- APK: ~50-100MB (contains all architectures)

### Testing Tracks
Play Console has multiple tracks:
- **Internal testing**: Up to 100 testers
- **Closed testing**: Limited users
- **Open testing**: Public beta
- **Production**: Live to all users

**Recommendation**: Start with internal testing!

---

## ✅ Checklist Before Submission

- [ ] App builds successfully
- [ ] Tested on physical Android device
- [ ] Google OAuth working
- [ ] All features functional
- [ ] Store listing complete (name, description, screenshots)
- [ ] Privacy policy created (required!)
- [ ] Content rating completed
- [ ] Pricing & distribution set
- [ ] App icon and graphics ready

---

## 🔗 Useful Links

- **EAS Build Dashboard**: https://expo.dev/accounts/pookie4u/projects/pookie4u-v1/builds
- **Google Play Console**: https://play.google.com/console
- **Expo Documentation**: https://docs.expo.dev/build/introduction/
- **Play Store Requirements**: https://support.google.com/googleplay/android-developer/

---

## 📞 Support

If you encounter issues:
1. Check build logs: `eas build:list`
2. View detailed logs online
3. Ask in this chat for help!

---

**Good luck with your production build! 🚀**
