#!/bin/bash

# Pookie4u Pre-Deployment Automated Testing Script
# Run this before every deployment to avoid credit loss!

set +e  # Don't exit on errors, we want to see all results

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Function to print test header
print_header() {
    echo ""
    echo "========================================="
    echo -e "${BLUE}$1${NC}"
    echo "========================================="
}

# Function to print test result
print_result() {
    local test_name=$1
    local result=$2
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    if [ "$result" = "PASS" ]; then
        echo -e "${GREEN}✅ PASS${NC}: $test_name"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo -e "${RED}❌ FAIL${NC}: $test_name"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
}

# Function to check if service is running
check_service() {
    if sudo supervisorctl status $1 | grep -q "RUNNING"; then
        print_result "$1 service running" "PASS"
        return 0
    else
        print_result "$1 service running" "FAIL"
        return 1
    fi
}

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║  POOKIE4U DEPLOYMENT READINESS TEST      ║"
echo "║  Testing Before Deployment to Save $$$   ║"
echo "╚══════════════════════════════════════════╝"
echo ""
echo "⏰ Started: $(date)"
echo ""

# ============================================
# TEST 1: SERVICE STATUS
# ============================================
print_header "TEST 1: Service Status"

check_service "backend"
check_service "expo"

# ============================================
# TEST 2: BACKEND HEALTH ENDPOINTS
# ============================================
print_header "TEST 2: Backend Health Endpoints (CRITICAL)"

# Test /health endpoint
echo "Testing /health endpoint..."
HEALTH_RESPONSE=$(curl -s -w "\n%{http_code}" http://localhost:8001/health)
HTTP_CODE=$(echo "$HEALTH_RESPONSE" | tail -1)
RESPONSE_BODY=$(echo "$HEALTH_RESPONSE" | head -n -1)

if [ "$HTTP_CODE" = "200" ]; then
    if echo "$RESPONSE_BODY" | grep -q '"status":"healthy"'; then
        if echo "$RESPONSE_BODY" | grep -q '"database":"connected"'; then
            print_result "/health endpoint (200 OK + DB connected)" "PASS"
        else
            print_result "/health endpoint (DB not connected)" "FAIL"
            echo "  Response: $RESPONSE_BODY"
        fi
    else
        print_result "/health endpoint (not healthy)" "FAIL"
        echo "  Response: $RESPONSE_BODY"
    fi
else
    print_result "/health endpoint (HTTP $HTTP_CODE)" "FAIL"
    echo "  Response: $RESPONSE_BODY"
fi

# Test /api/health endpoint
echo "Testing /api/health endpoint..."
API_HEALTH_RESPONSE=$(curl -s -w "\n%{http_code}" http://localhost:8001/api/health)
API_HTTP_CODE=$(echo "$API_HEALTH_RESPONSE" | tail -1)
API_RESPONSE_BODY=$(echo "$API_HEALTH_RESPONSE" | head -n -1)

if [ "$API_HTTP_CODE" = "200" ]; then
    if echo "$API_RESPONSE_BODY" | grep -q '"status":"healthy"'; then
        print_result "/api/health endpoint (200 OK)" "PASS"
    else
        print_result "/api/health endpoint (not healthy)" "FAIL"
    fi
else
    print_result "/api/health endpoint (HTTP $API_HTTP_CODE)" "FAIL"
fi

# Test /health/ready endpoint
echo "Testing /health/ready endpoint..."
READY_RESPONSE=$(curl -s -w "\n%{http_code}" http://localhost:8001/health/ready)
READY_HTTP_CODE=$(echo "$READY_RESPONSE" | tail -1)
READY_RESPONSE_BODY=$(echo "$READY_RESPONSE" | head -n -1)

if [ "$READY_HTTP_CODE" = "200" ]; then
    if echo "$READY_RESPONSE_BODY" | grep -q '"status":"ready"'; then
        print_result "/health/ready endpoint (200 OK)" "PASS"
    else
        print_result "/health/ready endpoint (not ready)" "FAIL"
    fi
else
    print_result "/health/ready endpoint (HTTP $READY_HTTP_CODE)" "FAIL"
fi

# ============================================
# TEST 3: MONGODB CONNECTION
# ============================================
print_header "TEST 3: MongoDB Connection (CRITICAL)"

cd /app/backend
if [ -f .env ]; then
    source .env
    
    # Test MongoDB ping
    echo "Testing MongoDB connection..."
    MONGO_PING=$(mongosh "$MONGO_URL" --eval "db.runCommand({ ping: 1 })" --quiet 2>&1)
    if echo "$MONGO_PING" | grep -q '"ok" : 1'; then
        print_result "MongoDB connection (ping successful)" "PASS"
    else
        print_result "MongoDB connection (ping failed)" "FAIL"
        echo "  Error: $MONGO_PING"
    fi
    
    # Test user count
    echo "Checking users collection..."
    USER_COUNT=$(mongosh "$MONGO_URL" --eval "db.users.countDocuments()" --quiet 2>&1 | tail -1)
    if [[ "$USER_COUNT" =~ ^[0-9]+$ ]]; then
        print_result "Users collection accessible ($USER_COUNT users)" "PASS"
    else
        print_result "Users collection not accessible" "FAIL"
    fi
else
    print_result ".env file exists" "FAIL"
fi

# ============================================
# TEST 4: ENVIRONMENT VARIABLES
# ============================================
print_header "TEST 4: Environment Variables (CRITICAL)"

cd /app/backend
if [ -f .env ]; then
    source .env
    
    [ -n "$MONGO_URL" ] && print_result "MONGO_URL configured" "PASS" || print_result "MONGO_URL missing" "FAIL"
    [ -n "$DB_NAME" ] && print_result "DB_NAME configured" "PASS" || print_result "DB_NAME missing" "FAIL"
    [ -n "$EMERGENT_LLM_KEY" ] && print_result "EMERGENT_LLM_KEY configured" "PASS" || print_result "EMERGENT_LLM_KEY missing" "FAIL"
    [ -n "$GOOGLE_CLIENT_ID" ] && print_result "GOOGLE_CLIENT_ID configured" "PASS" || print_result "GOOGLE_CLIENT_ID missing" "FAIL"
    [ -n "$GOOGLE_CLIENT_SECRET" ] && print_result "GOOGLE_CLIENT_SECRET configured" "PASS" || print_result "GOOGLE_CLIENT_SECRET missing" "FAIL"
    
    # Check if MONGO_URL points to Atlas (not localhost)
    if echo "$MONGO_URL" | grep -q "mongodb+srv://"; then
        print_result "MONGO_URL points to Atlas (production)" "PASS"
    else
        print_result "MONGO_URL should use Atlas connection string" "FAIL"
        echo "  Current: $MONGO_URL"
    fi
else
    print_result ".env file exists" "FAIL"
fi

# ============================================
# TEST 5: FRONTEND STATUS
# ============================================
print_header "TEST 5: Frontend Availability"

# Test frontend HTTP status
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000)
if [ "$FRONTEND_STATUS" = "200" ]; then
    print_result "Frontend HTTP response (200 OK)" "PASS"
else
    print_result "Frontend HTTP response (HTTP $FRONTEND_STATUS)" "FAIL"
fi

# Check if JavaScript bundles are present
SCRIPT_COUNT=$(curl -s http://localhost:3000 | grep -o "<script" | wc -l)
if [ "$SCRIPT_COUNT" -gt 0 ]; then
    print_result "Frontend JavaScript bundles ($SCRIPT_COUNT found)" "PASS"
else
    print_result "Frontend JavaScript bundles not found" "FAIL"
fi

# ============================================
# TEST 6: BACKEND ERROR LOG CHECK
# ============================================
print_header "TEST 6: Error Log Analysis"

# Check for critical errors in backend logs
echo "Checking backend logs for critical errors..."
BACKEND_ERRORS=$(sudo supervisorctl tail -100 backend 2>&1 | grep -i "exception\|traceback\|critical" | wc -l)
if [ "$BACKEND_ERRORS" -eq 0 ]; then
    print_result "No critical errors in backend logs" "PASS"
else
    print_result "$BACKEND_ERRORS critical errors found in logs" "FAIL"
    echo "  Run: sudo supervisorctl tail backend"
fi

# Check for errors in frontend logs
echo "Checking frontend logs for critical errors..."
FRONTEND_ERRORS=$(sudo supervisorctl tail -100 expo 2>&1 | grep -i "error.*failed\|exception" | wc -l)
if [ "$FRONTEND_ERRORS" -eq 0 ]; then
    print_result "No critical errors in frontend logs" "PASS"
else
    print_result "$FRONTEND_ERRORS errors found in frontend logs" "FAIL"
    echo "  Note: Some deprecation warnings are acceptable"
fi

# ============================================
# TEST 7: API ENDPOINT SPOT CHECK
# ============================================
print_header "TEST 7: API Endpoint Availability"

# Test a few key endpoints (without auth for basic check)
API_ENDPOINTS=(
    "/health"
    "/api/health"
    "/health/ready"
)

for endpoint in "${API_ENDPOINTS[@]}"; do
    ENDPOINT_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8001$endpoint)
    if [ "$ENDPOINT_STATUS" = "200" ]; then
        print_result "API endpoint $endpoint (200 OK)" "PASS"
    else
        print_result "API endpoint $endpoint (HTTP $ENDPOINT_STATUS)" "FAIL"
    fi
done

# ============================================
# TEST 8: RESPONSE TIME CHECK
# ============================================
print_header "TEST 8: Performance Check"

# Test response time
echo "Testing health endpoint response time..."
START_TIME=$(date +%s%N)
curl -s http://localhost:8001/health > /dev/null
END_TIME=$(date +%s%N)
RESPONSE_TIME=$(( (END_TIME - START_TIME) / 1000000 ))  # Convert to milliseconds

if [ "$RESPONSE_TIME" -lt 2000 ]; then
    print_result "Response time under 2 seconds (${RESPONSE_TIME}ms)" "PASS"
else
    print_result "Response time over 2 seconds (${RESPONSE_TIME}ms)" "FAIL"
    echo "  Warning: Slow responses may cause health check timeouts"
fi

# ============================================
# FINAL REPORT
# ============================================
echo ""
echo "========================================="
echo "           TEST SUMMARY                  "
echo "========================================="
echo ""
echo "⏰ Completed: $(date)"
echo ""
echo "📊 Results:"
echo "  Total Tests:  $TOTAL_TESTS"
echo -e "  ${GREEN}Passed:       $PASSED_TESTS${NC}"
echo -e "  ${RED}Failed:       $FAILED_TESTS${NC}"
echo ""

# Calculate pass rate
if [ "$TOTAL_TESTS" -gt 0 ]; then
    PASS_RATE=$(( PASSED_TESTS * 100 / TOTAL_TESTS ))
    echo "📈 Pass Rate: $PASS_RATE%"
    echo ""
fi

# Final verdict
if [ "$FAILED_TESTS" -eq 0 ]; then
    echo "╔══════════════════════════════════════════╗"
    echo -e "║  ${GREEN}✅ ALL TESTS PASSED - READY TO DEPLOY!${NC}   ║"
    echo "╚══════════════════════════════════════════╝"
    echo ""
    echo "🚀 Your app is deployment-ready!"
    echo "💡 Test in Preview mode first, then deploy with confidence!"
    exit 0
else
    echo "╔══════════════════════════════════════════╗"
    echo -e "║  ${RED}❌ TESTS FAILED - DO NOT DEPLOY!${NC}        ║"
    echo "╚══════════════════════════════════════════╝"
    echo ""
    echo "🛑 Fix the failed tests before deploying!"
    echo "💸 Deploying now will waste 50 credits!"
    echo ""
    echo "📋 Action Items:"
    echo "  1. Review failed tests above"
    echo "  2. Fix the issues"
    echo "  3. Run this script again"
    echo "  4. Only deploy when all tests pass"
    echo ""
    exit 1
fi
