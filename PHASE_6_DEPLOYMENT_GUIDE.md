# Phase 6: Final Testing & Deployment Guide

## Overview
Complete guide for building production APK/AAB and deploying Pookie4u to Google Play Store.

---

## Production Build Process

### Prerequisites
- Expo account configured
- EAS CLI installed
- All environment variables set
- Backend deployed and tested

### Build Commands

**Production Build (App Bundle for Play Store)**:
```bash
cd /app/frontend
eas build --platform android --profile production
```

**Preview Build (APK for Testing)**:
```bash
cd /app/frontend
eas build --platform android --profile preview
```

---

## Post-Build Steps

1. **Download Build**
   - EAS provides download link after completion
   - Test APK on physical device before Play Store submission

2. **Upload to Play Store**
   - Go to Google Play Console
   - Create new release
   - Upload .aab file
   - Complete store listing

3. **Setup Cron Job**
   - Configure trial expiry checker
   - Use cron-job.org or GitHub Actions
   - Schedule: Daily at 10:00 AM
   - Endpoint: POST /api/admin/check-trial-expiry

4. **Configure RevenueCat**
   - Follow GOOGLE_PLAY_REVENUECAT_SETUP_COMPLETE_GUIDE.md
   - Create subscription products
   - Link Google Play Console
   - Test subscription flow

---

## Monitoring

- Health endpoint: GET /health
- Backend logs: `sudo supervisorctl tail -f backend`
- Database: MongoDB Atlas dashboard
- Revenue: RevenueCat dashboard
- Crashes: Sentry.io

---

## Support Resources

- Expo Build Docs: https://docs.expo.dev/build/
- Play Console: https://play.google.com/console
- RevenueCat: https://app.revenuecat.com

---

**Build Status**: Ready to Execute
**Estimated Time**: 15-20 minutes
