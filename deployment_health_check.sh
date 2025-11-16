#!/bin/bash
echo "=================================="
echo "POOKIE4U DEPLOYMENT HEALTH CHECK"
echo "=================================="
echo ""

# Check Backend Service
echo "1. Backend Service Status:"
supervisorctl status backend | grep RUNNING && echo "✅ Backend Running" || echo "❌ Backend Down"
echo ""

# Check Frontend Service
echo "2. Frontend Service Status:"
supervisorctl status expo | grep RUNNING && echo "✅ Frontend Running" || echo "❌ Frontend Down"
echo ""

# Check MongoDB Connection
echo "3. MongoDB Connection:"
if curl -s http://localhost:8001/api/health > /dev/null 2>&1; then
    echo "✅ Backend API Responding"
else
    echo "⚠️  Backend API Not Responding"
fi
echo ""

# Check Environment Variables
echo "4. Environment Variables Check:"
cd /app/backend
if [ -f .env ]; then
    echo "✅ Backend .env exists"
    grep -q "MONGO_URL" .env && echo "✅ MONGO_URL configured" || echo "❌ MONGO_URL missing"
    grep -q "JWT_SECRET" .env && echo "✅ JWT_SECRET configured" || echo "❌ JWT_SECRET missing"
else
    echo "❌ Backend .env missing"
fi

cd /app/frontend
if [ -f .env ]; then
    echo "✅ Frontend .env exists"
    grep -q "EXPO_PUBLIC_BACKEND_URL" .env && echo "✅ EXPO_PUBLIC_BACKEND_URL configured" || echo "❌ EXPO_PUBLIC_BACKEND_URL missing"
    grep -q "EXPO_PUBLIC_REVENUECAT_GOOGLE_API_KEY" .env && echo "✅ EXPO_PUBLIC_REVENUECAT_GOOGLE_API_KEY configured" || echo "❌ Key missing"
else
    echo "❌ Frontend .env missing"
fi
echo ""

# Check Python Dependencies
echo "5. Backend Dependencies:"
cd /app/backend
pip list | grep -i fastapi > /dev/null && echo "✅ FastAPI installed" || echo "❌ FastAPI missing"
pip list | grep -i pymongo > /dev/null && echo "✅ PyMongo installed" || echo "❌ PyMongo missing"
pip list | grep -i pydantic > /dev/null && echo "✅ Pydantic installed" || echo "❌ Pydantic missing"
echo ""

# Check Node Dependencies
echo "6. Frontend Dependencies:"
cd /app/frontend
if [ -d node_modules ]; then
    echo "✅ node_modules exists"
    [ -d node_modules/expo ] && echo "✅ Expo installed" || echo "❌ Expo missing"
    [ -d node_modules/expo-router ] && echo "✅ expo-router installed" || echo "❌ expo-router missing"
    [ -d node_modules/react-native-purchases ] && echo "✅ RevenueCat SDK installed" || echo "❌ RevenueCat missing"
else
    echo "❌ node_modules missing"
fi
echo ""

# Check File Structure
echo "7. Critical Files Check:"
[ -f /app/backend/server.py ] && echo "✅ server.py exists" || echo "❌ server.py missing"
[ -f /app/backend/requirements.txt ] && echo "✅ requirements.txt exists" || echo "❌ requirements.txt missing"
[ -f /app/frontend/package.json ] && echo "✅ package.json exists" || echo "❌ package.json missing"
[ -f /app/frontend/app.json ] && echo "✅ app.json exists" || echo "❌ app.json missing"
[ -f /app/eas.json ] && echo "✅ eas.json exists (for builds)" || echo "⚠️  eas.json missing"
echo ""

# Check Port Availability
echo "8. Port Check:"
curl -s http://localhost:8001/ > /dev/null && echo "✅ Port 8001 (Backend) accessible" || echo "❌ Port 8001 not accessible"
curl -s http://localhost:3000/ > /dev/null && echo "✅ Port 3000 (Frontend) accessible" || echo "❌ Port 3000 not accessible"
echo ""

echo "=================================="
echo "HEALTH CHECK COMPLETE"
echo "=================================="
