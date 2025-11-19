# Production Build & Upload Instructions

## What We're Building
- **Build Type:** App Bundle (.aab) - Required for Google Play
- **Version:** 1.0.0 (versionCode: 1)
- **Package:** com.pookie4u.app
- **Platform:** Android

---

## STEP 1: Trigger Production Build

### Option A: Using EAS Build (Recommended)

**Requirements:**
- Expo account (free)
- EAS CLI installed
- Internet connection

**Commands to run:**
```bash
cd /app/frontend

# Login to Expo (if not logged in)
eas login

# Trigger production build
eas build --platform android --profile production
```

**What happens:**
1. EAS uploads your app code to Expo servers
2. Build starts in the cloud (takes 15-20 minutes)
3. You get a download link when complete
4. Download the `.aab` file

---

## STEP 2: What the Build Includes

✅ **All Features:**
- Complete gamification system (streaks, points, levels)
- 270 relationship-specific tasks
- Subscription system (RevenueCat ready)
- Google OAuth authentication
- Offline support
- Push notifications infrastructure
- MongoDB Atlas connection
- All UI/UX enhancements

✅ **Configured Subscriptions:**
- Product IDs: `pookie4u_monthly`, `pookie4u_half_yearly`
- Billing permissions included
- RevenueCat SDK integrated

---

## STEP 3: Upload to Google Play Console

### After Build Completes:

**A. Download the .aab file**
- EAS provides a download link
- File name: `build-xxxxx.aab`
- Size: ~50-80 MB typically

**B. Go to Play Console**
```
URL: https://play.google.com/console
Navigate to: Pookie4u app → Production → Releases
```

**C. Create New Release**
1. Click "Create new release"
2. Upload the `.aab` file
3. Fill in release notes:
   ```
   Initial release of Pookie4u v1.0.0
   
   Features:
   • AI-powered relationship tasks tailored to your lifestyle
   • Daily streak tracking with gamification
   • 20 levels of progression with unlockable features
   • Romantic message generation
   • Smart gift recommendations
   • Event reminders (birthdays, anniversaries)
   • 14-day free trial with monthly and half-yearly plans
   
   Built with love for couples who want to strengthen their relationship!
   ```
4. Click "Save"

---

## STEP 4: After Upload - Create Subscriptions

**Now you can create subscriptions!**

Once the APK/AAB is uploaded, Google Play will allow you to:
- Navigate to: Monetize → Products → Subscriptions
- Click "Create subscription"
- Follow the instructions I provided earlier:
  - Monthly: `pookie4u_monthly` (₹79)
  - Half-Yearly: `pookie4u_half_yearly` (₹450)
  - Both with 14-day free trial
  - Both set to auto-renew

---

## STEP 5: Complete Store Listing

Before you can publish, Play Console requires:

### Required Assets:
1. **Screenshots (4-8 required)**
   - Size: 1080x1920 or 1080x2340 pixels
   - Show: Home screen, Tasks, Profile, Gamification

2. **Feature Graphic**
   - Size: 1024x500 pixels
   - Hero image for Play Store

3. **App Icon**
   - Already configured: 512x512
   - Should be in: `/app/frontend/assets/images/icon.png`

4. **Privacy Policy URL**
   - Must host a privacy policy
   - Can use GitHub Pages (free)

5. **App Description**
   ```
   Short description (80 chars):
   Strengthen your relationship with AI-powered daily tasks and gamification.
   
   Full description:
   [See GOOGLE_PLAY_REVENUECAT_SETUP_COMPLETE_GUIDE.md for full text]
   ```

6. **Content Rating**
   - Complete questionnaire
   - Category: Dating/Relationships
   - Age: 18+

---

## STEP 6: Testing Track (Optional but Recommended)

Before production release:

**Create Internal Testing Track:**
1. Go to: Testing → Internal testing
2. Create email list of testers
3. Upload the same `.aab` file
4. Testers get app link to install
5. Test subscription flow, features, etc.
6. Collect feedback
7. Fix any issues
8. Then move to production

---

## Build Status Monitoring

**Check build progress:**
```bash
eas build:list

# Or view in browser:
https://expo.dev/accounts/pookie4u/projects/pookie4u-v1/builds
```

**Build typically takes:**
- Queue time: 0-5 minutes
- Build time: 15-20 minutes
- **Total:** 15-25 minutes

---

## If Build Fails

**Common issues:**

1. **"Unauthorized"**
   - Solution: Run `eas login` again

2. **"Invalid credentials"**
   - Solution: EAS will generate signing keys automatically
   - Just confirm when prompted

3. **"Package name conflict"**
   - Solution: Package name `com.pookie4u.app` should be unique
   - If not, change in `app.json`

4. **"Dependency error"**
   - Solution: Run `cd /app/frontend && yarn install`
   - Then retry build

---

## Alternative: Build APK for Testing

If you want to test before uploading to Play Store:

```bash
cd /app/frontend
eas build --platform android --profile preview
```

This creates an `.apk` file you can:
- Install directly on Android devices
- Test the app without Play Store
- Share with beta testers

---

## Timeline After Upload

1. **Upload .aab:** 5 minutes
2. **Create subscriptions:** 20 minutes (following guide)
3. **Complete store listing:** 1-2 hours
4. **Submit for review:** 1 click
5. **Google review:** 1-7 days (typically 1-3 days)
6. **App published:** Automatic after approval

---

## What Happens During Build

EAS Build process:
1. ✅ Validates app.json configuration
2. ✅ Installs dependencies
3. ✅ Generates Android signing keys (first build)
4. ✅ Compiles React Native code
5. ✅ Bundles JavaScript
6. ✅ Optimizes assets
7. ✅ Creates App Bundle (.aab)
8. ✅ Signs the bundle
9. ✅ Uploads to EAS servers
10. ✅ Provides download link

---

## Post-Build Checklist

After successful build:
- [ ] Downloaded .aab file
- [ ] Uploaded to Play Console
- [ ] Created both subscriptions
- [ ] Configured 14-day free trial
- [ ] Set auto-renewal to YES
- [ ] Added screenshots (4-8 images)
- [ ] Added feature graphic
- [ ] Created privacy policy
- [ ] Completed store listing
- [ ] Filled content rating
- [ ] Submitted for review

---

## Ready to Build?

**Commands Summary:**
```bash
# Navigate to frontend
cd /app/frontend

# Login to Expo
eas login

# Build production App Bundle
eas build --platform android --profile production

# Monitor build
eas build:list
```

**Build will start immediately and take ~15-20 minutes**

**You'll get:**
- Build URL to monitor progress
- Download link when complete
- .aab file ready for Play Store

---

## Need Help?

**Build issues:** Check EAS dashboard for logs
**Upload issues:** Refer to Play Console help
**Subscription issues:** Follow STEP_BY_STEP_ACCOUNT_SETUP_GUIDE.md

---

**Status:** Ready to build! 🚀
**Next:** Run the build command and wait for completion
**Then:** Upload to Play Console and create subscriptions
