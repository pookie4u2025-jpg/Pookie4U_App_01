# 📦 Build & Upload APK Guide for Google Play Console

## Prerequisites

- ✅ Expo account (create at https://expo.dev/signup)
- ✅ Google Play Console developer account ($25 one-time fee)
- ✅ Project source code on your local computer

---

## STEP 1: Install EAS CLI (One-time Setup)

Open terminal/command prompt and run:

```bash
npm install -g eas-cli
```

**Verify installation:**
```bash
eas --version
```

---

## STEP 2: Login to Expo

```bash
eas login
```

Enter your Expo credentials when prompted.

**Verify you're logged in:**
```bash
eas whoami
```

---

## STEP 3: Navigate to Your Project

```bash
cd /path/to/your/pookie4u/frontend
```

Replace `/path/to/your/pookie4u/frontend` with your actual project path.

---

## STEP 4: Build APK for Internal Testing

Run this command:

```bash
npx eas build -p android --profile preview
```

**What happens:**
1. EAS will ask if you want to configure the project (if first time) → Select **YES**
2. It will ask about credentials → Select **"Generate new keystore"**
3. Build will start in the cloud
4. You'll get a build URL to monitor progress

**Build time:** Usually 15-20 minutes

**Monitor your build:**
- You'll see a URL like: `https://expo.dev/accounts/[your-account]/projects/pookie4u-v1/builds/[build-id]`
- Open this in your browser to watch progress
- You'll get email notification when done

---

## STEP 5: Download Your APK

Once build completes:

1. Go to the build URL from previous step
2. Click **"Download"** button
3. Save the APK file (e.g., `pookie4u-preview.apk`)

**Alternative download via CLI:**
```bash
eas build:list
```

Copy the build ID, then:
```bash
eas build:download [BUILD_ID]
```

---

## STEP 6: Upload to Google Play Console

### 6.1 Access Google Play Console

1. Go to: https://play.google.com/console/
2. Sign in with your Google account
3. If you don't have a developer account:
   - Click "Create account"
   - Pay $25 one-time registration fee
   - Complete registration

### 6.2 Create New App (If First Time)

1. Click **"Create app"**
2. Fill in details:
   - **App name:** Pookie4u
   - **Default language:** English (or your preference)
   - **App or game:** App
   - **Free or paid:** Free
3. Accept declarations
4. Click **"Create app"**

### 6.3 Complete App Setup (Required Before Upload)

Before you can upload an APK, you need to complete:

**A. Privacy Policy**
1. Go to "App content" → "Privacy policy"
2. Enter your privacy policy URL
3. Save

**B. App Access**
1. Go to "App content" → "App access"
2. Select "All or some functionality is restricted"
3. Provide test credentials if needed
4. Save

**C. Ads Declaration**
1. Go to "App content" → "Ads"
2. Select whether your app contains ads
3. Save

**D. Target Audience**
1. Go to "App content" → "Target audience and content"
2. Select age groups
3. Save

**E. Content Rating**
1. Go to "App content" → "Content rating"
2. Fill out questionnaire
3. Submit

### 6.4 Upload APK to Internal Testing

1. In left sidebar, go to **"Release" → "Testing" → "Internal testing"**
2. Click **"Create new release"**
3. Click **"Upload"** button
4. Drag and drop your APK file or click to browse
5. Wait for upload to complete (may take a few minutes)
6. Add **Release notes** (optional):
   ```
   Initial release for subscription testing
   - Free 14-day trial
   - Monthly subscription (₹79)
   - 6-month subscription (₹450)
   ```
7. Click **"Save"**
8. Click **"Review release"**
9. Click **"Start rollout to Internal testing"**
10. Confirm rollout

**✅ Your APK is now uploaded and billing is enabled!**

---

## STEP 7: Verify Upload

1. Go to "Release" → "Testing" → "Internal testing"
2. You should see your release listed
3. Status should show "Available"

---

## 🎯 What's Next?

After uploading APK:
1. ✅ Billing is now enabled for your app
2. ✅ You can create subscription products
3. ✅ You can configure RevenueCat integration
4. ✅ You can start testing subscriptions

---

## 🔧 Troubleshooting

### Build Failed: "Invalid credentials"

**Solution:** Run `eas logout` then `eas login` again

### Build Failed: "Build failed with error"

**Solution:** Check build logs at the build URL. Common issues:
- Missing dependencies → Run `yarn install` locally first
- Configuration errors → Check `app.json` and `eas.json`

### Upload Failed: "App not found"

**Solution:** Make sure you've created the app in Google Play Console first

### Upload Failed: "Version code conflict"

**Solution:** You need to increment version in `app.json`:
```json
"version": "1.0.1"  // Increment this
```

Then rebuild.

---

## 📝 Important Notes

### Package Name Must Match

Ensure your package name in `app.json` matches what you entered in:
- ✅ Google Play Console
- ✅ RevenueCat dashboard

**Your package name:** `com.pookie4u.app`

### Keystore Security

EAS will generate and store your signing keystore securely. You don't need to manage it manually.

### Build Types

- **Preview build:** Creates APK (good for testing, what we're using)
- **Production build:** Creates AAB (required for Play Store production release)

---

## 🚀 Quick Command Reference

```bash
# Login to Expo
eas login

# Check who's logged in
eas whoami

# Build preview APK
npx eas build -p android --profile preview

# Build production AAB (for later)
npx eas build -p android --profile production

# List all builds
eas build:list

# Download specific build
eas build:download [BUILD_ID]

# Logout
eas logout
```

---

## ⏰ Timeline

- **EAS Build:** 15-20 minutes
- **Upload to Play Console:** 5-10 minutes
- **Google Play processing:** 5-15 minutes
- **Total:** ~30-45 minutes

---

## 💡 Tips

1. **Build during off-peak hours** for faster builds
2. **Keep terminal open** during build to see progress
3. **Save your build URL** for easy access
4. **Test APK locally** before uploading (optional)
5. **Take screenshots** for Play Store listing while testing

---

## ✅ Checklist

Before starting:
- [ ] Expo account created and verified
- [ ] EAS CLI installed (`npm install -g eas-cli`)
- [ ] Logged in to EAS (`eas login`)
- [ ] In project directory
- [ ] Google Play Console account ready

During build:
- [ ] Build command executed
- [ ] Build URL saved
- [ ] Monitoring build progress
- [ ] APK downloaded when complete

After build:
- [ ] App created in Play Console
- [ ] App content sections completed
- [ ] APK uploaded to internal testing
- [ ] Release rolled out

---

**Good luck with your build! 🎉**

Once you complete this, return to continue with creating subscription products in Google Play Console!
