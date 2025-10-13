# 🔐 Complete Authentication Setup Guide for Pookie4u

This guide will walk you through setting up all authentication methods for your Pookie4u relationship app.

## 📱 Current Authentication Status

✅ **Email/Password Authentication** - Ready (No setup needed)
✅ **Mobile/OTP Authentication** - UI Ready (SMS service needed)
⚠️ **Google OAuth** - Implemented (Needs configuration)
❌ **Apple OAuth** - Needs implementation

---

## 🚀 Google OAuth Setup

### Step 1: Create Google Cloud Project

1. **Go to Google Cloud Console**
   - Visit: https://console.cloud.google.com/
   - Sign in with your Google account

2. **Create New Project**
   - Click "Select a project" → "New Project"
   - Project name: `Pookie4u-Auth` (or your preferred name)
   - Click "Create"

3. **Enable Google+ API**
   - Go to "APIs & Services" → "Library"
   - Search for "Google+ API" 
   - Click "Enable"

### Step 2: Create OAuth 2.0 Credentials

1. **Configure OAuth Consent Screen**
   - Go to "APIs & Services" → "OAuth consent screen"
   - Choose "External" user type
   - Fill required fields:
     - App name: `Pookie4u`
     - User support email: Your email
     - Developer contact: Your email
   - Click "Save and Continue"

2. **Create OAuth 2.0 Client ID**
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "OAuth 2.0 Client ID"
   - Application type: "Web application"
   - Name: `Pookie4u Web Client`
   - **Authorized redirect URIs**: Add these URLs:
     ```
     https://auth.expo.io/@your-expo-username/pookie4u
     http://localhost:3000
     ```
   - Click "Create"

3. **Get Your Credentials**
   - Copy the **Client ID** (looks like: `123456789-abc123.apps.googleusercontent.com`)
   - Copy the **Client Secret** (looks like: `GOCSPX-abc123xyz`)

### Step 3: Configure Expo App

1. **Update app.json**
   ```json
   {
     "expo": {
       "scheme": "pookie4u",
       "android": {
         "googleServicesFile": "./google-services.json"
       },
       "ios": {
         "googleServicesFile": "./GoogleService-Info.plist"
       }
     }
   }
   ```

2. **Add Environment Variables**
   - Open `/app/frontend/.env`
   - Add your Google credentials:
   ```bash
   EXPO_PUBLIC_GOOGLE_CLIENT_ID=your-client-id-here.apps.googleusercontent.com
   EXPO_PUBLIC_GOOGLE_CLIENT_SECRET=your-client-secret-here
   ```

### Step 4: Test Google OAuth
- Restart your Expo app
- Try "Continue with Google" option
- Should open Google sign-in flow

---

## 🍎 Apple Sign-In Setup

### Step 1: Apple Developer Account Requirements

**Prerequisites:**
- Apple Developer Program membership ($99/year)
- Access to Apple Developer Portal
- iOS device for testing

### Step 2: Configure App ID

1. **Go to Apple Developer Portal**
   - Visit: https://developer.apple.com/account/
   - Sign in with Apple ID

2. **Create App ID**
   - Go to "Certificates, Identifiers & Profiles"
   - Click "Identifiers" → "+" button
   - Choose "App IDs" → "App"
   - Description: `Pookie4u`
   - Bundle ID: `com.yourcompany.pookie4u`
   - **Enable "Sign In with Apple"** capability
   - Click "Continue" → "Register"

### Step 3: Create Service ID

1. **Create Services ID**
   - Go to "Identifiers" → "+" → "Services IDs"
   - Description: `Pookie4u Web Service`
   - Identifier: `com.yourcompany.pookie4u.service`
   - **Enable "Sign In with Apple"**
   - Configure domains and return URLs:
     - Domains: `yourapp.com` (your domain)
     - Return URLs: `https://yourapp.com/auth/apple/callback`

### Step 4: Create Private Key

1. **Generate Key**
   - Go to "Keys" → "+" button
   - Key Name: `Pookie4u Apple Sign In Key`
   - **Enable "Sign In with Apple"**
   - Configure with your App ID
   - Download the `.p8` key file
   - **Save the Key ID** (10-character string)

### Step 5: Implement Apple OAuth

I'll need to implement the Apple OAuth service. Here's what we need:

```typescript
// Apple OAuth Configuration
const appleConfig = {
  clientId: 'com.yourcompany.pookie4u.service',
  teamId: 'YOUR_TEAM_ID', // From Apple Developer Account
  keyId: 'YOUR_KEY_ID', // From the key you created
  privateKey: 'YOUR_PRIVATE_KEY' // Content of .p8 file
};
```

---

## 📱 SMS/OTP Setup (Optional)

### Popular SMS Services:

1. **Twilio** (Recommended)
   - Sign up: https://www.twilio.com/
   - Get Phone Number and Auth Token
   - Cost: ~$1/month + $0.0075 per SMS

2. **AWS SNS**
   - More complex setup but cost-effective
   - Good if already using AWS

3. **Firebase Auth**
   - Google's solution
   - Easy integration with existing Google setup

### Twilio Setup:
```bash
# Backend Environment Variables
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+1234567890
```

---

## 🛠️ Implementation Priority

### Phase 1: Google OAuth (Recommended First)
1. ✅ Create Google Cloud Project
2. ✅ Get OAuth credentials
3. ✅ Add to environment variables
4. ✅ Test authentication flow

### Phase 2: Apple OAuth (If targeting iOS)
1. 🔄 Get Apple Developer Account
2. 🔄 Create App ID and Service ID
3. 🔄 Generate private key
4. 🔄 Implement Apple OAuth service
5. 🔄 Test on iOS device

### Phase 3: SMS/OTP (Optional Enhancement)
1. 🔄 Choose SMS provider
2. 🔄 Get API credentials
3. 🔄 Implement backend SMS sending
4. 🔄 Test OTP flow

---

## 📋 Checklist

### Google OAuth Setup
- [ ] Google Cloud project created
- [ ] OAuth consent screen configured
- [ ] Client ID and Secret obtained
- [ ] Environment variables added
- [ ] Tested sign-in flow

### Apple OAuth Setup
- [ ] Apple Developer account active
- [ ] App ID created with Sign In capability
- [ ] Service ID configured
- [ ] Private key generated and downloaded
- [ ] Apple OAuth service implemented

### SMS Setup (Optional)
- [ ] SMS service provider chosen
- [ ] API credentials obtained
- [ ] Backend SMS integration completed
- [ ] OTP verification tested

---

## 🔧 Need Help?

**Google OAuth Issues:**
- Check redirect URLs match exactly
- Ensure APIs are enabled
- Verify environment variables are loaded

**Apple OAuth Issues:**
- Confirm Apple Developer membership is active
- Check bundle IDs match exactly
- Ensure private key is correctly formatted

**General Issues:**
- Clear app cache: `expo r -c`
- Check network connectivity
- Verify environment variables with `console.log(process.env.EXPO_PUBLIC_GOOGLE_CLIENT_ID)`

---

## 🚀 Quick Start (Google Only)

If you want to get started quickly with just Google OAuth:

1. **Get Google Credentials** (Steps 1-2 from Google OAuth section)
2. **Add to .env file:**
   ```bash
   EXPO_PUBLIC_GOOGLE_CLIENT_ID=your-client-id-here
   ```
3. **Restart app:** `expo r -c`
4. **Test:** Try "Continue with Google" button

This will give you a fully functional authentication system with email/password + Google OAuth!