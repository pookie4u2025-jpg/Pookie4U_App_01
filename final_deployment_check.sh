#!/bin/bash
echo "╔════════════════════════════════════════════════════════╗"
echo "║   POOKIE4U - FINAL DEPLOYMENT READINESS CHECK         ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

READY=true
WARNINGS=()
BLOCKERS=()

# 1. Services Check
echo "1️⃣  SERVICE STATUS"
echo "─────────────────────────────────────────────────────────"
if supervisorctl status backend | grep -q RUNNING; then
    echo "✅ Backend: RUNNING"
else
    echo "❌ Backend: NOT RUNNING"
    READY=false
    BLOCKERS+=("Backend service not running")
fi

if supervisorctl status expo | grep -q RUNNING; then
    echo "✅ Frontend: RUNNING"
else
    echo "❌ Frontend: NOT RUNNING"
    READY=false
    BLOCKERS+=("Frontend service not running")
fi
echo ""

# 2. Health Endpoint Check
echo "2️⃣  HEALTH ENDPOINT"
echo "─────────────────────────────────────────────────────────"
if curl -s http://localhost:8001/health | grep -q "healthy\|unhealthy"; then
    health_status=$(curl -s http://localhost:8001/health | python3 -c "import sys, json; print(json.load(sys.stdin)['status'])")
    if [ "$health_status" = "healthy" ]; then
        echo "✅ Health endpoint: Working & Database Connected"
    else
        echo "⚠️  Health endpoint: Working but Database Disconnected"
        WARNINGS+=("Database not connected - needs MongoDB Atlas")
    fi
else
    echo "❌ Health endpoint: Not responding"
    READY=false
    BLOCKERS+=("Health check endpoint not working")
fi
echo ""

# 3. MongoDB Configuration
echo "3️⃣  MONGODB CONFIGURATION"
echo "─────────────────────────────────────────────────────────"
cd /app/backend
MONGO_URL=$(grep "^MONGO_URL=" .env 2>/dev/null | cut -d'=' -f2- | tr -d '"' | tr -d "'")
if [ -z "$MONGO_URL" ]; then
    echo "❌ MONGO_URL: NOT CONFIGURED"
    READY=false
    BLOCKERS+=("MONGO_URL not set in .env")
elif echo "$MONGO_URL" | grep -q "mongodb+srv://"; then
    echo "✅ MONGO_URL: MongoDB Atlas (Production Ready)"
elif echo "$MONGO_URL" | grep -q "localhost\|127.0.0.1"; then
    echo "⚠️  MONGO_URL: Local MongoDB (NOT DEPLOYMENT READY)"
    READY=false
    BLOCKERS+=("Using local MongoDB - needs Atlas for deployment")
else
    echo "✅ MONGO_URL: Configured (Remote)"
fi
echo ""

# 4. Environment Variables
echo "4️⃣  ENVIRONMENT VARIABLES"
echo "─────────────────────────────────────────────────────────"
cd /app/backend
required_vars=("MONGO_URL" "EMERGENT_LLM_KEY")
optional_vars=("JWT_SECRET" "SMTP_SERVER" "SENDER_EMAIL")

for var in "${required_vars[@]}"; do
    if grep -q "^${var}=" .env 2>/dev/null && [ -n "$(grep "^${var}=" .env | cut -d'=' -f2-)" ]; then
        echo "✅ $var: Configured"
    else
        echo "❌ $var: MISSING"
        READY=false
        BLOCKERS+=("$var not configured")
    fi
done

for var in "${optional_vars[@]}"; do
    if grep -q "^${var}=" .env 2>/dev/null && [ -n "$(grep "^${var}=" .env | cut -d'=' -f2-)" ]; then
        echo "✅ $var: Configured"
    else
        echo "⚠️  $var: Not set (using defaults)"
        WARNINGS+=("$var not configured - using defaults")
    fi
done
echo ""

# 5. Dependencies
echo "5️⃣  DEPENDENCIES"
echo "─────────────────────────────────────────────────────────"
cd /app/backend
if [ -f "requirements.txt" ]; then
    pkg_count=$(wc -l < requirements.txt)
    echo "✅ Backend requirements.txt: $pkg_count packages"
else
    echo "❌ Backend requirements.txt: MISSING"
    READY=false
    BLOCKERS+=("requirements.txt missing")
fi

cd /app/frontend
if [ -d "node_modules" ] && [ -f "package.json" ]; then
    pkg_count=$(cat package.json | grep -c '".*":')
    echo "✅ Frontend dependencies: Installed"
else
    echo "❌ Frontend dependencies: NOT INSTALLED"
    READY=false
    BLOCKERS+=("Frontend node_modules missing")
fi
echo ""

# 6. Critical Files
echo "6️⃣  CRITICAL FILES"
echo "─────────────────────────────────────────────────────────"
critical_files=(
    "/app/backend/server.py"
    "/app/backend/requirements.txt"
    "/app/backend/.env"
    "/app/frontend/package.json"
    "/app/frontend/app.json"
    "/app/eas.json"
)

for file in "${critical_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $(basename $file): Present"
    else
        echo "❌ $(basename $file): MISSING"
        READY=false
        BLOCKERS+=("$(basename $file) missing")
    fi
done
echo ""

# 7. Code Quality
echo "7️⃣  CODE QUALITY"
echo "─────────────────────────────────────────────────────────"
cd /app/frontend
if npx expo-doctor 2>&1 | grep -q "No issues detected\|checks passed"; then
    echo "✅ expo-doctor: All checks passed"
else
    echo "⚠️  expo-doctor: Some warnings present"
    WARNINGS+=("expo-doctor has warnings")
fi
echo ""

# 8. API Endpoints
echo "8️⃣  API ENDPOINTS TEST"
echo "─────────────────────────────────────────────────────────"
endpoints=(
    "/health:GET"
    "/api/auth/register:POST"
    "/api/auth/login:POST"
)

working=0
total=${#endpoints[@]}

for endpoint in "${endpoints[@]}"; do
    path=$(echo $endpoint | cut -d':' -f1)
    if [ "$path" = "/health" ]; then
        if curl -s "http://localhost:8001$path" > /dev/null 2>&1; then
            ((working++))
        fi
    else
        # Check if endpoint exists (will return 422 or 401, not 404)
        status=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:8001$path" -X POST -H "Content-Type: application/json" -d '{}' 2>/dev/null)
        if [ "$status" != "404" ] && [ "$status" != "000" ]; then
            ((working++))
        fi
    fi
done

if [ $working -eq $total ]; then
    echo "✅ API Endpoints: $working/$total responding"
else
    echo "⚠️  API Endpoints: $working/$total responding"
    WARNINGS+=("Some API endpoints not responding")
fi
echo ""

# 9. Deployment Specific
echo "9️⃣  DEPLOYMENT SPECIFIC"
echo "─────────────────────────────────────────────────────────"

# Check if health endpoint returns proper JSON
if curl -s http://localhost:8001/health | python3 -c "import sys, json; json.load(sys.stdin)" > /dev/null 2>&1; then
    echo "✅ Health endpoint: Valid JSON response"
else
    echo "❌ Health endpoint: Invalid response"
    READY=false
    BLOCKERS+=("Health endpoint not returning valid JSON")
fi

# Check for localhost references in code
if grep -r "localhost" /app/backend/*.py 2>/dev/null | grep -v ".pyc" | grep -v "MONGO_URL" | grep -v "#" > /dev/null; then
    echo "⚠️  Localhost references: Found in code"
    WARNINGS+=("Hardcoded localhost found in backend code")
else
    echo "✅ Localhost references: None in backend code"
fi
echo ""

# 10. Summary
echo "╔════════════════════════════════════════════════════════╗"
echo "║                  DEPLOYMENT SUMMARY                    ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

if [ "$READY" = true ] && [ ${#BLOCKERS[@]} -eq 0 ]; then
    echo "🎉 STATUS: ✅ READY FOR DEPLOYMENT"
    echo ""
    echo "Your app is production-ready!"
    echo "All critical checks passed."
    echo ""
    if [ ${#WARNINGS[@]} -gt 0 ]; then
        echo "⚠️  WARNINGS (Non-blocking):"
        for warning in "${WARNINGS[@]}"; do
            echo "   • $warning"
        done
        echo ""
    fi
    echo "Next Steps:"
    echo "  1. Ensure MongoDB Atlas is configured in Emergent secrets"
    echo "  2. Add JWT_SECRET to Emergent secrets (32+ chars)"
    echo "  3. Click Deploy in Emergent dashboard"
    echo "  4. Monitor deployment logs"
    exit 0
else
    echo "❌ STATUS: NOT READY FOR DEPLOYMENT"
    echo ""
    echo "🚫 BLOCKING ISSUES:"
    for blocker in "${BLOCKERS[@]}"; do
        echo "   • $blocker"
    done
    echo ""
    if [ ${#WARNINGS[@]} -gt 0 ]; then
        echo "⚠️  WARNINGS:"
        for warning in "${WARNINGS[@]}"; do
            echo "   • $warning"
        done
        echo ""
    fi
    echo "Action Required:"
    echo "  1. Fix all blocking issues above"
    echo "  2. Setup MongoDB Atlas (critical)"
    echo "  3. Re-run this check"
    exit 1
fi
