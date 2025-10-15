# Step-by-Step Guide: Adding Redirect URIs to Google Cloud Console

## 📋 What You Need to Add:

**Authorized redirect URIs:**
```
https://auth.expo.io/@anonymous/frontend
https://relationship-app-4.preview.emergentagent.com
https://relationship-app-4.preview.emergentagent.com/auth/callback
http://localhost:3000
```

**Authorized JavaScript origins:**
```
https://auth.expo.io
https://relationship-app-4.preview.emergentagent.com
http://localhost:3000
```

---

## 🎯 Step-by-Step Instructions:

### Step 1: Go to Google Cloud Console
1. Open your browser
2. Go to: https://console.cloud.google.com/
3. Make sure you're signed in with the same Google account you used to create the OAuth credentials

### Step 2: Select Your Project
1. At the top of the page, you'll see a project dropdown (it might show "Select a project" or your project name)
2. Click on it
3. Find and select your "Pookie4u" project (or whatever you named it)
4. The page will reload with your project selected

### Step 3: Navigate to Credentials
1. On the left sidebar, click on **"APIs & Services"**
2. Then click on **"Credentials"**
3. You'll see a page with all your API credentials

### Step 4: Find Your OAuth Client ID
1. Look for the section titled **"OAuth 2.0 Client IDs"**
2. You should see your client ID listed there (it will show the name you gave it, like "Pookie4u Web" or "Web client 1")
3. The Client ID will be: `235271953596-r0md5vpfm8i7f2lrvrfe6hrsipicgc9o.apps.googleusercontent.com`
4. Click on the **name** of your OAuth client (NOT the edit icon, but the actual name text)

### Step 5: Add Authorized JavaScript Origins
1. Scroll down to the section called **"Authorized JavaScript origins"**
2. Click the **"+ ADD URI"** button
3. Add these URIs one by one (click "+ ADD URI" for each):
   ```
   https://auth.expo.io
   ```
   (Press Enter or click outside)
   
4. Click **"+ ADD URI"** again and add:
   ```
   https://relationship-app-4.preview.emergentagent.com
   ```
   
5. Click **"+ ADD URI"** again and add:
   ```
   http://localhost:3000
   ```

### Step 6: Add Authorized Redirect URIs
1. Scroll down to the section called **"Authorized redirect URIs"**
2. Click the **"+ ADD URI"** button
3. Add these URIs one by one (click "+ ADD URI" for each):
   ```
   https://auth.expo.io/@anonymous/frontend
   ```
   (Press Enter or click outside)
   
4. Click **"+ ADD URI"** again and add:
   ```
   https://relationship-app-4.preview.emergentagent.com
   ```
   
5. Click **"+ ADD URI"** again and add:
   ```
   https://relationship-app-4.preview.emergentagent.com/auth/callback
   ```
   
6. Click **"+ ADD URI"** again and add:
   ```
   http://localhost:3000
   ```

### Step 7: Save Your Changes
1. Scroll to the bottom of the page
2. Click the blue **"SAVE"** button
3. Wait for the confirmation message that says "Client ID updated"

---

## ✅ Verification Checklist

After saving, verify you have:

**Authorized JavaScript origins (3 total):**
- [ ] `https://auth.expo.io`
- [ ] `https://relationship-app-4.preview.emergentagent.com`
- [ ] `http://localhost:3000`

**Authorized redirect URIs (4 total):**
- [ ] `https://auth.expo.io/@anonymous/frontend`
- [ ] `https://relationship-app-4.preview.emergentagent.com`
- [ ] `https://relationship-app-4.preview.emergentagent.com/auth/callback`
- [ ] `http://localhost:3000`

---

## 📸 What You Should See:

### Before Adding URIs:
The sections will likely be empty or have just one or two URIs.

### After Adding URIs:
You should see all the URIs listed in their respective sections.

---

## 🚨 Common Issues:

### Issue 1: "Can't find Credentials page"
**Solution:** 
- Make sure you're on the right project (check the project name at the top)
- Look for the hamburger menu (☰) on the top left
- Navigate to: APIs & Services → Credentials

### Issue 2: "Don't see OAuth 2.0 Client IDs section"
**Solution:**
- Make sure you've already created an OAuth Client ID
- If not, you need to create one first (follow the setup guide)

### Issue 3: "Save button is grayed out"
**Solution:**
- Make sure you pressed Enter or clicked outside after typing each URI
- URIs must be properly formatted (no spaces, correct protocol http/https)

### Issue 4: "Invalid redirect URI format"
**Solution:**
- Make sure there are no spaces before or after the URI
- Make sure you're using the exact URIs provided (copy-paste recommended)
- Check that http/https is correct

---

## 🎯 Quick Copy-Paste Guide

If you prefer to copy-paste, here's a condensed version:

**Authorized JavaScript origins (add 3 URIs):**
```
https://auth.expo.io
https://relationship-app-4.preview.emergentagent.com
http://localhost:3000
```

**Authorized redirect URIs (add 4 URIs):**
```
https://auth.expo.io/@anonymous/frontend
https://relationship-app-4.preview.emergentagent.com
https://relationship-app-4.preview.emergentagent.com/auth/callback
http://localhost:3000
```

---

## ⏱️ How Long Does It Take?

This entire process should take about 2-3 minutes once you're on the Credentials page.

---

## 🎉 After You're Done:

1. Save the changes in Google Console
2. Go back to your Pookie4u app
3. Try the "Sign in with Google" button
4. It should now work and open the Google account picker!

---

## 📞 Need Help?

If you're stuck at any step, let me know:
- Which step you're on
- What you see on the screen
- Any error messages

I can provide more detailed guidance!
