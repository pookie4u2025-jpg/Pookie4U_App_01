# 🧪 Pre-Deployment Testing Checklist for Pookie4u

**CRITICAL: Complete ALL tests before deploying to avoid credit loss!**

Each deployment costs **50 credits**. Testing is **FREE** in preview mode.

---

## 📋 Quick Start

### Run Automated Tests
```bash
# Run all tests at once
cd /app
./test_deployment_readiness.sh
```

### Manual Testing Checklist
Follow the sections below in order ⬇️

---

## 1️⃣ **BACKEND HEALTH CHECKS** (CRITICAL)

**Why:** If these fail, deployment will fail immediately.

### Test Commands:
```bash
# Test all health endpoints
curl -s http://localhost:8001/health | python3 -m json.tool
curl -s http://localhost:8001/api/health | python3 -m json.tool
curl -s http://localhost:8001/health/ready | python3 -m json.tool
```

### Expected Results:
```json
✅ /health
{
  "status": "healthy",
  "service": "pookie4u-api",
  "database": "connected",
  "timestamp": "2025-11-21T..."
}

✅ /api/health
{
  "status": "healthy",
  "service": "pookie4u-api",
  "database": "connected",
  "timestamp": "2025-11-21T..."
}

✅ /health/ready
{
  "status": "ready",
  "service": "pookie4u-api",
  "database": "connected",
  "timestamp": "2025-11-21T..."
}
```

**❌ FAIL CRITERIA:**
- Any 500 errors
- "database": "error" or "disconnected"
- No response (timeout)

**✋ STOP if any health check fails!** Fix before proceeding.

---

## 2️⃣ **DATABASE CONNECTION** (CRITICAL)

**Why:** MongoDB Atlas connection issues are the #1 cause of deployment failures.

### Test Commands:
```bash
# Check MongoDB connection
mongosh "$MONGO_URL" --eval "db.runCommand({ ping: 1 })" --quiet

# List databases
mongosh "$MONGO_URL" --eval "show dbs" --quiet

# Count users
mongosh "$MONGO_URL" --eval "db.users.countDocuments()" --quiet
```

### Expected Results:
```
✅ Connection successful
✅ Database "pookie4u" visible
✅ Users collection has documents
```

**❌ FAIL CRITERIA:**
- Connection timeout
- Authentication failed
- Database not accessible

**✋ STOP if MongoDB connection fails!**

---

## 3️⃣ **AUTHENTICATION FLOW** (HIGH PRIORITY)

**Why:** Users can't use the app if auth doesn't work.

### Test Emergent OAuth:
```bash
# Test session-data endpoint (after Google login)
curl -s http://localhost:8001/api/auth/emergent/session-data?session_id=test123
```

### Expected Results:
```json
✅ Returns user data (or proper error for invalid session)
✅ No 500 errors
✅ Response includes: email, name, phone, partner_profile
```

### Test Email/Password Login:
```bash
# Test login endpoint
curl -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"test123"}'
```

**❌ FAIL CRITERIA:**
- 500 Internal Server Error
- Authentication crashes
- No token returned

---

## 4️⃣ **USER PROFILE ENDPOINTS** (HIGH PRIORITY)

**Why:** Core functionality - users need to access their profiles.

### Test Commands:
```bash
# Get user profile (requires auth token)
# Replace TOKEN with actual JWT token from login

TOKEN="your-jwt-token-here"

curl -s http://localhost:8001/api/user/profile \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

### Expected Results:
```json
✅ Returns complete user profile
✅ Includes: name, email, phone, partner_profile
✅ Profile picture included
✅ Gamification data present
```

### Test Update Profile:
```bash
curl -X PUT http://localhost:8001/api/user/profile \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Test User","phone":"+1234567890"}'
```

**❌ FAIL CRITERIA:**
- 401 Unauthorized (token not working)
- 500 errors
- Missing profile data

---

## 5️⃣ **TASK SYSTEM** (MEDIUM PRIORITY)

**Why:** Core app functionality.

### Test Commands:
```bash
# Get daily tasks
curl -s http://localhost:8001/api/tasks/daily \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

# Get weekly tasks
curl -s http://localhost:8001/api/tasks/weekly \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

### Expected Results:
```json
✅ Returns task list
✅ No 500 errors
✅ Tasks are relevant to relationship mode
```

---

## 6️⃣ **GAMIFICATION SYSTEM** (MEDIUM PRIORITY)

### Test Commands:
```bash
# Get gamification stats
curl -s http://localhost:8001/api/gamification/stats \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

### Expected Results:
```json
✅ Returns points, level, streak
✅ No calculation errors
✅ Data matches database
```

---

## 7️⃣ **FRONTEND LOADING** (HIGH PRIORITY)

**Why:** Users need to access the web app.

### Test Commands:
```bash
# Check frontend is serving
curl -I http://localhost:3000

# Check if JavaScript loads
curl -s http://localhost:3000 | grep -o "<script" | wc -l
```

### Expected Results:
```
✅ HTTP 200 OK
✅ HTML content returned
✅ JavaScript bundles load
✅ No blank page
```

### Manual Browser Test:
1. Open: http://localhost:3000 or preview URL
2. Check console for errors (F12)
3. Try login flow
4. Verify no "setNativeProps" errors

**❌ FAIL CRITERIA:**
- Blank white screen
- JavaScript errors in console
- Login button doesn't work

---

## 8️⃣ **ENVIRONMENT VARIABLES** (CRITICAL)

**Why:** Missing env vars cause deployment failures.

### Test Commands:
```bash
# Check backend env vars
cd /app/backend
echo "Checking required environment variables..."

[ -n "$MONGO_URL" ] && echo "✅ MONGO_URL set" || echo "❌ MONGO_URL missing"
[ -n "$DB_NAME" ] && echo "✅ DB_NAME set" || echo "❌ DB_NAME missing"
[ -n "$EMERGENT_LLM_KEY" ] && echo "✅ EMERGENT_LLM_KEY set" || echo "❌ EMERGENT_LLM_KEY missing"
[ -n "$GOOGLE_CLIENT_ID" ] && echo "✅ GOOGLE_CLIENT_ID set" || echo "❌ GOOGLE_CLIENT_ID missing"
[ -n "$GOOGLE_CLIENT_SECRET" ] && echo "✅ GOOGLE_CLIENT_SECRET set" || echo "❌ GOOGLE_CLIENT_SECRET missing"
```

### Expected Results:
```
✅ All required env vars present
✅ MONGO_URL points to Atlas
✅ OAuth credentials configured
```

**❌ FAIL CRITERIA:**
- Any required env var missing
- MONGO_URL pointing to localhost
- Invalid credentials

---

## 9️⃣ **STRESS TEST** (OPTIONAL BUT RECOMMENDED)

**Why:** Ensure app handles load in production.

### Test Commands:
```bash
# Send 10 concurrent requests
for i in {1..10}; do
  curl -s http://localhost:8001/health &
done
wait

# Check response times
time curl -s http://localhost:8001/health
```

### Expected Results:
```
✅ All requests succeed
✅ Response time < 2 seconds
✅ No timeout errors
✅ No connection errors
```

---

## 🔟 **ERROR LOG CHECK** (CRITICAL)

**Why:** Hidden errors can cause deployment failures.

### Test Commands:
```bash
# Check backend logs for errors
sudo supervisorctl tail -100 backend | grep -i "error\|exception\|failed" | tail -20

# Check frontend logs for errors
sudo supervisorctl tail -100 expo | grep -i "error\|failed" | tail -20
```

### Expected Results:
```
✅ No critical errors
✅ No unhandled exceptions
✅ Only deprecation warnings (acceptable)
```

**❌ FAIL CRITERIA:**
- Connection errors
- Unhandled exceptions
- Database errors
- Import errors

---

## ✅ **FINAL DEPLOYMENT CHECKLIST**

Before clicking "Deploy" in Emergent:

- [ ] All 3 health endpoints return 200 OK
- [ ] MongoDB Atlas connection working
- [ ] Authentication flow tested and working
- [ ] User profile endpoints functional
- [ ] Frontend loads without errors
- [ ] No critical errors in logs
- [ ] All required env vars present
- [ ] Tested in Preview mode (if available)
- [ ] Waited at least 10 minutes in preview
- [ ] Verified all features work end-to-end

**🎯 ALL BOXES CHECKED?** 
✅ **SAFE TO DEPLOY!**

**❌ ANY BOX UNCHECKED?**
🛑 **FIX ISSUES FIRST!**

---

## 🆘 **TROUBLESHOOTING**

### If Health Checks Fail:
1. Check MongoDB connection string
2. Verify Atlas IP whitelist (allow all: 0.0.0.0/0)
3. Check database credentials
4. Restart backend: `sudo supervisorctl restart backend`

### If Auth Fails:
1. Verify Google OAuth credentials
2. Check redirect URIs in Google Console
3. Test with curl first before frontend

### If Frontend Won't Load:
1. Check for JavaScript errors in console
2. Verify environment variables
3. Restart expo: `sudo supervisorctl restart expo`

### If Database Connection Fails:
1. Test connection string directly with mongosh
2. Verify Atlas cluster is running
3. Check network access settings in Atlas

---

## 📞 **SUPPORT**

If all tests pass but deployment still fails:
- **Discord:** https://discord.gg/VzKfwCXC4A
- **Email:** support@emergent.sh
- Include this test report in your message

---

## 💡 **PRO TIP**

Save this output before deploying:
```bash
# Run all tests and save results
cd /app
./test_deployment_readiness.sh > test_results.txt 2>&1
cat test_results.txt
```

Attach `test_results.txt` to support requests if deployment fails.

---

**🎉 Good luck with your deployment!**
