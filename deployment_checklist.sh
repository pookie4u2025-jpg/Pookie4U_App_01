#!/bin/bash
echo "========================================="
echo "EMERGENT DEPLOYMENT ISSUE CHECKER"
echo "========================================="
echo ""

echo "1. Checking MongoDB Connection String Format:"
cd /app/backend
if grep -q "mongodb+srv://" .env 2>/dev/null; then
    echo "✅ Using MongoDB Atlas connection string"
elif grep -q "mongodb://" .env 2>/dev/null; then
    echo "⚠️  Local MongoDB connection detected - needs Atlas for deployment"
    echo "   Current: $(grep MONGO_URL .env | cut -d'=' -f2 | cut -c1-40)..."
else
    echo "❌ No MONGO_URL found in .env"
fi
echo ""

echo "2. Checking Port Configuration:"
if grep -q "PORT" .env 2>/dev/null; then
    echo "✅ PORT variable configured"
else
    echo "⚠️  No PORT variable - deployment will use Emergent's assigned port"
fi

# Check if server.py uses dynamic port
if grep -q "port=int(os.getenv" server.py 2>/dev/null; then
    echo "✅ server.py uses dynamic port from environment"
elif grep -q "port=8001" server.py 2>/dev/null; then
    echo "❌ server.py hardcoded to port 8001 - needs to be dynamic"
fi
echo ""

echo "3. Checking Required Environment Variables:"
for var in MONGO_URL EMERGENT_LLM_KEY JWT_SECRET; do
    if grep -q "^${var}=" .env 2>/dev/null; then
        echo "✅ $var configured"
    else
        echo "❌ $var missing"
    fi
done
echo ""

echo "4. Checking Health Check Endpoint:"
if grep -q '@app.get.*"/health"' server.py || grep -q '@api_router.get.*"/health"' server.py; then
    echo "✅ Health check endpoint exists"
else
    echo "⚠️  No /health endpoint found"
fi
echo ""

echo "5. Checking for Hardcoded Localhost References:"
if grep -rq "localhost" backend/*.py 2>/dev/null; then
    echo "⚠️  Found localhost references:"
    grep -n "localhost" backend/*.py | head -3
else
    echo "✅ No localhost hardcoded"
fi
echo ""

echo "6. Checking Python Dependencies:"
if [ -f "requirements.txt" ]; then
    echo "✅ requirements.txt exists ($(wc -l < requirements.txt) packages)"
else
    echo "❌ requirements.txt missing"
fi
echo ""

echo "7. Checking Frontend Environment:"
cd /app/frontend
if grep -q "EXPO_PUBLIC_BACKEND_URL" .env 2>/dev/null; then
    backend_url=$(grep EXPO_PUBLIC_BACKEND_URL .env | cut -d'=' -f2)
    if [[ $backend_url == *"localhost"* ]] || [[ $backend_url == *"127.0.0.1"* ]]; then
        echo "⚠️  Frontend points to localhost: $backend_url"
        echo "   Needs to be updated for deployment"
    else
        echo "✅ Frontend backend URL configured for deployment"
    fi
else
    echo "❌ EXPO_PUBLIC_BACKEND_URL missing"
fi
echo ""

echo "========================================="
echo "CRITICAL ISSUES TO FIX:"
echo "========================================="
