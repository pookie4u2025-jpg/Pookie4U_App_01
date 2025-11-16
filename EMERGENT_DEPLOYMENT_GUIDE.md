# 🚀 EMERGENT DEPLOYMENT CONFIGURATION GUIDE

## Deployment Fixes Applied

### ✅ Issues Fixed

1. **Health Check Endpoint Added** ✅
   - Added `/health` endpoint for deployment monitoring
   - Checks database connectivity
   - Returns service status and timestamp

2. **JWT Secret Updated** ✅
   - Default value now 32+ characters
   - Secure fallback if environment variable not set

3. **Dynamic Port Ready** ✅
   - Server respects PORT environment variable from Emergent
   - Fallback to 8001 for local development

### ⚠️ MongoDB Atlas Required

**Current Issue**: Local MongoDB connection detected
- Local: `mongodb://localhost:27017`
- **Needed**: MongoDB Atlas connection string

## Required Environment Variables for Deployment

### 1. MongoDB Atlas Connection (CRITICAL)

```bash
MONGO_URL=mongodb+srv://username:password@cluster.mongodb.net/pookie4u?retryWrites=true&w=majority
```

**How to Get MongoDB Atlas Connection String:**

1. Go to [MongoDB Atlas](https://cloud.mongodb.com/)
2. Sign up/login (free tier available)
3. Create a new cluster (select free tier)
4. Click "Connect" on your cluster
5. Choose "Connect your application"
6. Copy the connection string
7. Replace `<password>` with your database password
8. Replace `<dbname>` with `pookie4u`

**Atlas Setup Checklist:**
- [ ] Create Atlas account
- [ ] Create cluster (free tier: M0)
- [ ] Create database user (username + password)
- [ ] Add IP to whitelist: `0.0.0.0/0` (allows all IPs)
- [ ] Get connection string
- [ ] Add to Emergent secrets

### 2. JWT Secret (CRITICAL)

```bash
JWT_SECRET=your-super-secret-key-min-32-characters-long-change-this
```

**Generate Strong Secret:**
```bash
# Option 1: Using Python
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Option 2: Using OpenSSL
openssl rand -base64 32

# Option 3: Manual
# Use a random string of 32+ characters
```

### 3. Emergent LLM Key (Required for AI Features)

```bash
EMERGENT_LLM_KEY=your-emergent-llm-key
```

Get from: Emergent dashboard → Profile → Universal Key

### 4. Optional Email Configuration

**For Development** (Current):
```bash
EMAIL_CONSOLE_MODE=true
```

**For Production** (Real Emails):
```bash
EMAIL_CONSOLE_MODE=false
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=noreply@pookie4u.com
SENDER_PASSWORD=your-email-app-password
```

### 5. RevenueCat (For Subscriptions)

```bash
EXPO_PUBLIC_REVENUECAT_GOOGLE_API_KEY=your-revenuecat-key
```

Get from: RevenueCat dashboard

## Emergent Deployment Steps

### Step 1: Set Environment Variables in Emergent

1. Go to your Emergent deployment dashboard
2. Click on "Manage Secrets" or "Environment Variables"
3. Add the following secrets:

```
MONGO_URL = mongodb+srv://...your-atlas-connection...
JWT_SECRET = ...your-32-char-secret...
EMERGENT_LLM_KEY = ...your-key...
EMAIL_CONSOLE_MODE = true
EXPO_PUBLIC_REVENUECAT_GOOGLE_API_KEY = ...your-key...
```

### Step 2: Deploy

1. Click "Deploy" button
2. Wait for build process (~5-10 minutes)
3. Check logs:
   - [BUILD] - Should complete successfully
   - [DEPLOY] - Kubernetes deployment
   - [HEALTH_CHECK] - Should return healthy status
   - [MONGODB_MIGRATE] - If applicable

### Step 3: Verify Deployment

Once deployed, test the health endpoint:
```bash
curl https://your-deployment-url.emergentagent.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "pookie4u-api",
  "database": "connected",
  "timestamp": "2025-11-16T12:00:00"
}
```

## Deployment Checklist

### Pre-Deployment

- [ ] MongoDB Atlas cluster created
- [ ] Database user created with password
- [ ] IP whitelist set to 0.0.0.0/0
- [ ] Connection string tested
- [ ] All environment variables ready
- [ ] JWT_SECRET generated (32+ chars)
- [ ] Emergent LLM key obtained

### During Deployment

- [ ] Environment variables added to Emergent
- [ ] Click Deploy
- [ ] Monitor build logs
- [ ] Wait for health check to pass

### Post-Deployment

- [ ] Test /health endpoint
- [ ] Test authentication endpoints
- [ ] Verify database connectivity
- [ ] Check application logs
- [ ] Test frontend connectivity

## Common Deployment Errors & Fixes

### Error: "Database connection failed"

**Cause**: MongoDB Atlas connection issue

**Fix**:
1. Verify connection string format
2. Check database user credentials
3. Ensure IP whitelist includes 0.0.0.0/0
4. Test connection string locally first

### Error: "Health check timeout"

**Cause**: Application not starting properly

**Fix**:
1. Check if PORT environment variable is respected
2. Verify all required environment variables are set
3. Check application logs for startup errors

### Error: "Missing environment variable"

**Cause**: Required variables not set in Emergent

**Fix**:
1. Go to Manage Secrets
2. Add all required variables
3. Redeploy

## MongoDB Atlas Quick Setup

### 1. Create Free Cluster

```
1. Go to cloud.mongodb.com
2. Sign up (free)
3. Click "Build a Database"
4. Choose M0 (Free tier)
5. Select cloud provider & region
6. Cluster name: "Pookie4u"
7. Click "Create"
```

### 2. Create Database User

```
1. Security → Database Access
2. Add New Database User
3. Choose "Password" authentication
4. Username: pookie4u_user
5. Password: (generate strong password)
6. Database User Privileges: "Read and write to any database"
7. Add User
```

### 3. Whitelist IP Address

```
1. Security → Network Access
2. Add IP Address
3. Enter: 0.0.0.0/0 (allows all IPs)
4. Description: "Emergent Deployment"
5. Confirm
```

### 4. Get Connection String

```
1. Databases → Connect
2. Connect your application
3. Driver: Python, Version: 3.12 or later
4. Copy connection string
5. Format:
   mongodb+srv://pookie4u_user:<password>@cluster.mongodb.net/pookie4u
6. Replace <password> with actual password
```

## Testing Before Deployment

### Test MongoDB Atlas Connection Locally

```bash
cd /app/backend

# Create test script
cat > test_atlas.py << 'EOF'
import os
from motor.motor_asyncio import AsyncIOMotorClient

async def test_connection():
    # Replace with your Atlas connection string
    MONGO_URL = "mongodb+srv://username:password@cluster.mongodb.net/pookie4u"
    
    client = AsyncIOMotorClient(MONGO_URL)
    db = client["pookie4u"]
    
    try:
        # Test connection
        await db.users.find_one({})
        print("✅ MongoDB Atlas connection successful!")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
    finally:
        client.close()

import asyncio
asyncio.run(test_connection())
EOF

# Run test
python3 test_atlas.py
```

## Production Environment Variables Template

Save this to use in Emergent secrets:

```env
# Database (REQUIRED - Get from MongoDB Atlas)
MONGO_URL=mongodb+srv://pookie4u_user:YOUR_PASSWORD@cluster.mongodb.net/pookie4u?retryWrites=true&w=majority

# Security (REQUIRED - Generate strong key)
JWT_SECRET=your-super-secret-jwt-key-min-32-characters-long

# AI Service (REQUIRED - Get from Emergent)
EMERGENT_LLM_KEY=your-emergent-llm-key-here

# Email (OPTIONAL - Keep console mode for now)
EMAIL_CONSOLE_MODE=true
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=noreply@pookie4u.com
SENDER_PASSWORD=your-app-password

# Subscriptions (OPTIONAL - Add later)
EXPO_PUBLIC_REVENUECAT_GOOGLE_API_KEY=your-revenuecat-api-key

# Database Name (OPTIONAL - Defaults to pookie4u)
DB_NAME=pookie4u
```

## Health Check Endpoint Details

### Endpoint: `GET /health`

**Response (Healthy)**:
```json
{
  "status": "healthy",
  "service": "pookie4u-api",
  "database": "connected",
  "timestamp": "2025-11-16T12:34:56.789Z"
}
```

**Response (Unhealthy)**:
```json
{
  "status": "unhealthy",
  "service": "pookie4u-api",
  "database": "disconnected",
  "error": "Connection timeout",
  "timestamp": "2025-11-16T12:34:56.789Z"
}
```

## Rollback Plan

If deployment fails:

1. **Check Logs**: Click on specific log tabs ([BUILD], [DEPLOY], etc.)
2. **Verify Secrets**: Ensure all environment variables are correct
3. **Test Connection String**: Verify MongoDB Atlas connection locally
4. **Contact Support**: Emergent Discord with deployment ID

## Support Resources

- **Emergent Discord**: https://discord.gg/VzKfwCXC4A
- **MongoDB Atlas Docs**: https://docs.atlas.mongodb.com/
- **Deployment ID**: d4cqiek (for support reference)

## Summary

**Deployment is BLOCKED by:**
1. ❌ Local MongoDB connection (needs Atlas)

**Deployment is READY after:**
1. ✅ Health check endpoint (DONE)
2. ✅ JWT secret updated (DONE)  
3. ✅ Dynamic port support (DONE)
4. ⏳ MongoDB Atlas setup (REQUIRED)
5. ⏳ Environment variables in Emergent (REQUIRED)

**Next Steps:**
1. Create MongoDB Atlas cluster
2. Get connection string
3. Add all environment variables to Emergent
4. Click Deploy again

---

**Status**: Ready for deployment once MongoDB Atlas is configured
**Last Updated**: November 16, 2025
**Deployment ID**: d4cqiek
