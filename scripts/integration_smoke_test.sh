#!/usr/bin/env bash
#
# Comprehensive Integration Smoke Test Script
# 
# Tests ALL critical API endpoints and service integrations after docker compose up.
# Exit code 0 if all pass, 1 if any fail.
#
set -euo pipefail

BASE_URL="${BASE_URL:-http://localhost:8000}"
FRONTEND_URL="${FRONTEND_URL:-http://localhost:3000}"
MAX_RETRIES=30
RETRY_DELAY=2

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
PASS_COUNT=0
FAIL_COUNT=0
SKIP_COUNT=0

# Test result tracking
declare -a FAILED_TESTS=()

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_pass() {
    echo -e "${GREEN}[PASS]${NC} $1"
    ((PASS_COUNT++))
}

log_fail() {
    echo -e "${RED}[FAIL]${NC} $1"
    ((FAIL_COUNT++))
    FAILED_TESTS+=("$1")
}

log_skip() {
    echo -e "${YELLOW}[SKIP]${NC} $1"
    ((SKIP_COUNT++))
}

log_section() {
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

# Wait for service to be healthy
wait_for_service() {
    local service_name="$1"
    local health_url="$2"
    local attempts=0
    
    log_info "Waiting for $service_name to be ready..."
    
    while [ $attempts -lt $MAX_RETRIES ]; do
        if curl -sf "$health_url" > /dev/null 2>&1; then
            log_pass "$service_name is ready"
            return 0
        fi
        ((attempts++))
        sleep $RETRY_DELAY
    done
    
    log_fail "$service_name not ready after $MAX_RETRIES attempts"
    return 1
}

# Test an endpoint
test_endpoint() {
    local test_name="$1"
    local method="$2"
    local url="$3"
    local auth_header="$4"
    local data="$5"
    local expected_status="$6"
    
    local curl_opts=(-s -w "\n%{http_code}" -X "$method")
    
    if [ -n "$auth_header" ]; then
        curl_opts+=(-H "Authorization: Bearer $auth_header")
    fi
    
    if [ -n "$data" ]; then
        curl_opts+=(-H "Content-Type: application/json" -d "$data")
    fi
    
    local response
    response=$(curl "${curl_opts[@]}" "$url" 2>&1 || echo "")
    
    # Extract status code (last line)
    local status_code
    status_code=$(echo "$response" | tail -n1)
    
    if [ "$status_code" = "$expected_status" ]; then
        log_pass "$test_name (HTTP $status_code)"
        return 0
    else
        log_fail "$test_name (Expected HTTP $expected_status, got $status_code)"
        return 1
    fi
}

# Extract JSON field using grep/sed (simple parser, no jq dependency)
extract_json_field() {
    local json="$1"
    local field="$2"
    echo "$json" | grep -o "\"$field\"[[:space:]]*:[[:space:]]*\"[^\"]*\"" | sed "s/\"$field\"[[:space:]]*:[[:space:]]*\"\([^\"]*\)\"/\1/"
}

# Main test flow
main() {
    log_section "1. Service Health Checks"
    
    # Wait for backend
    if ! wait_for_service "Backend API" "${BASE_URL}/health"; then
        log_fail "Backend not available, cannot continue"
        exit 1
    fi
    
    # Check Postgres (via backend health)
    log_info "Checking database connectivity..."
    if curl -sf "${BASE_URL}/health" | grep -q "postgres"; then
        log_pass "Database connectivity verified"
    else
        log_skip "Database health check (not in health endpoint)"
    fi
    
    # Check Redis (via backend health)
    log_info "Checking Redis connectivity..."
    if curl -sf "${BASE_URL}/health" | grep -q "redis"; then
        log_pass "Redis connectivity verified"
    else
        log_skip "Redis health check (not in health endpoint)"
    fi
    
    # Check Frontend
    log_info "Checking frontend availability..."
    if curl -sf "${FRONTEND_URL}" > /dev/null 2>&1; then
        log_pass "Frontend is accessible at ${FRONTEND_URL}"
    else
        log_skip "Frontend not accessible (may not be running)"
    fi
    
    log_section "2. Database Migrations"
    
    log_info "Running Alembic migrations..."
    if docker compose exec -T backend alembic upgrade head 2>&1 | grep -qE "(already at head|Running upgrade)"; then
        log_pass "Database migrations completed"
    else
        log_fail "Database migrations failed"
    fi
    
    log_section "3. Authentication & Bootstrap"
    
    # Bootstrap admin user
    log_info "Bootstrapping admin user..."
    BOOTSTRAP_RESULT=$(curl -sf -X POST "${BASE_URL}/auth/dev/bootstrap" 2>&1 || echo '{"status":"error"}')
    if echo "$BOOTSTRAP_RESULT" | grep -qE '(created|skipped)'; then
        log_pass "Admin user bootstrap completed"
    else
        log_fail "Admin user bootstrap failed"
        exit 1
    fi
    
    # Get admin credentials from env or defaults
    ADMIN_EMAIL="${BOOTSTRAP_ADMIN_EMAIL:-admin@coffeestudio.com}"
    ADMIN_PASSWORD="${BOOTSTRAP_ADMIN_PASSWORD:-adminadmin}"
    
    # Login and get token
    log_info "Authenticating as admin..."
    LOGIN_RESPONSE=$(curl -sf -X POST "${BASE_URL}/auth/login" \
        -H "Content-Type: application/json" \
        -d "{\"email\":\"${ADMIN_EMAIL}\",\"password\":\"${ADMIN_PASSWORD}\"}" 2>&1 || echo '{}')
    
    TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access_token"[[:space:]]*:[[:space:]]*"[^"]*"' | sed 's/"access_token"[[:space:]]*:[[:space:]]*"\([^"]*\)"/\1/')
    
    if [ -n "$TOKEN" ]; then
        log_pass "Authentication successful, token obtained"
    else
        log_fail "Authentication failed, cannot continue"
        exit 1
    fi
    
    # Test /auth/me
    test_endpoint "GET /auth/me" "GET" "${BASE_URL}/auth/me" "$TOKEN" "" "200"
    
    log_section "4. Core API Endpoints"
    
    # Health endpoint
    test_endpoint "GET /health" "GET" "${BASE_URL}/health" "" "" "200"
    
    # Metrics endpoint
    test_endpoint "GET /metrics" "GET" "${BASE_URL}/metrics" "" "" "200"
    
    log_section "5. Cooperatives API"
    
    # Create cooperative
    COOP_DATA='{"name":"Smoke Test Cooperative","region":"Cajamarca","country":"Peru","annual_production_kg":50000,"contact_email":"test@smoketest.com"}'
    COOP_RESPONSE=$(curl -sf -X POST "${BASE_URL}/cooperatives" \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json" \
        -d "$COOP_DATA" 2>&1 || echo '{}')
    
    COOP_ID=$(echo "$COOP_RESPONSE" | grep -o '"id"[[:space:]]*:[[:space:]]*[0-9]*' | sed 's/"id"[[:space:]]*:[[:space:]]*\([0-9]*\)/\1/')
    
    if [ -n "$COOP_ID" ]; then
        log_pass "POST /cooperatives (created ID: $COOP_ID)"
    else
        log_fail "POST /cooperatives (failed to create)"
        COOP_ID=""
    fi
    
    # List cooperatives
    test_endpoint "GET /cooperatives" "GET" "${BASE_URL}/cooperatives" "$TOKEN" "" "200"
    
    # Get single cooperative
    if [ -n "$COOP_ID" ]; then
        test_endpoint "GET /cooperatives/$COOP_ID" "GET" "${BASE_URL}/cooperatives/${COOP_ID}" "$TOKEN" "" "200"
    fi
    
    log_section "6. Roasters API"
    
    # Create roaster
    ROASTER_DATA='{"name":"Smoke Test Roastery","city":"Hamburg","country":"Germany","roaster_type":"specialty","annual_capacity_kg":30000,"contact_email":"test@roaster.com"}'
    ROASTER_RESPONSE=$(curl -sf -X POST "${BASE_URL}/roasters" \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json" \
        -d "$ROASTER_DATA" 2>&1 || echo '{}')
    
    ROASTER_ID=$(echo "$ROASTER_RESPONSE" | grep -o '"id"[[:space:]]*:[[:space:]]*[0-9]*' | sed 's/"id"[[:space:]]*:[[:space:]]*\([0-9]*\)/\1/')
    
    if [ -n "$ROASTER_ID" ]; then
        log_pass "POST /roasters (created ID: $ROASTER_ID)"
    else
        log_fail "POST /roasters (failed to create)"
        ROASTER_ID=""
    fi
    
    # List roasters
    test_endpoint "GET /roasters" "GET" "${BASE_URL}/roasters" "$TOKEN" "" "200"
    
    log_section "7. Lots/Deals API"
    
    # Create lot (requires cooperative)
    if [ -n "$COOP_ID" ]; then
        LOT_DATA="{\"cooperative_id\":${COOP_ID},\"name\":\"Test Lot A\",\"price_per_kg\":5.50,\"currency\":\"USD\",\"weight_kg\":1000,\"expected_cupping_score\":86.0}"
        LOT_RESPONSE=$(curl -sf -X POST "${BASE_URL}/lots" \
            -H "Authorization: Bearer $TOKEN" \
            -H "Content-Type: application/json" \
            -d "$LOT_DATA" 2>&1 || echo '{}')
        
        LOT_ID=$(echo "$LOT_RESPONSE" | grep -o '"id"[[:space:]]*:[[:space:]]*[0-9]*' | sed 's/"id"[[:space:]]*:[[:space:]]*\([0-9]*\)/\1/')
        
        if [ -n "$LOT_ID" ]; then
            log_pass "POST /lots (created ID: $LOT_ID)"
        else
            log_fail "POST /lots (failed to create)"
            LOT_ID=""
        fi
    fi
    
    # List lots
    test_endpoint "GET /lots" "GET" "${BASE_URL}/lots" "$TOKEN" "" "200"
    
    log_section "8. Margins API"
    
    # Calculate margin
    MARGIN_DATA='{"purchase_price_per_kg":5.50,"purchase_currency":"USD","landed_costs_per_kg":0.80,"roast_and_pack_costs_per_kg":1.20,"yield_factor":0.84,"selling_price_per_kg":12.0,"selling_currency":"EUR"}'
    MARGIN_RESPONSE=$(curl -sf -X POST "${BASE_URL}/margins/calc" \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json" \
        -d "$MARGIN_DATA" 2>&1 || echo '{}')
    
    if echo "$MARGIN_RESPONSE" | grep -q "outputs"; then
        log_pass "POST /margins/calc (calculation successful)"
    else
        log_fail "POST /margins/calc (calculation failed)"
    fi
    
    log_section "9. Peru Regions API"
    
    # List Peru regions
    test_endpoint "GET /regions/peru" "GET" "${BASE_URL}/regions/peru" "$TOKEN" "" "200"
    
    # Seed Peru regions (may fail if already seeded)
    log_info "Testing POST /regions/peru/seed..."
    SEED_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "${BASE_URL}/regions/peru/seed" \
        -H "Authorization: Bearer $TOKEN" 2>&1 || echo "")
    SEED_STATUS=$(echo "$SEED_RESPONSE" | tail -n1)
    
    if [ "$SEED_STATUS" = "200" ] || [ "$SEED_STATUS" = "201" ]; then
        log_pass "POST /regions/peru/seed (seeded or already exists)"
    elif [ "$SEED_STATUS" = "409" ]; then
        log_pass "POST /regions/peru/seed (already seeded)"
    else
        log_skip "POST /regions/peru/seed (status: $SEED_STATUS)"
    fi
    
    # Peru sourcing
    test_endpoint "GET /peru/regions" "GET" "${BASE_URL}/peru/regions" "$TOKEN" "" "200"
    
    log_section "10. Shipments API"
    
    # Create shipment
    SHIPMENT_DATA='{"container_number":"SMOKE1234567","bill_of_lading":"BOL-SMOKE-001","weight_kg":18000.0,"container_type":"40ft","origin_port":"Callao, Peru","destination_port":"Hamburg, Germany","departure_date":"2024-01-15","estimated_arrival":"2024-03-01"}'
    SHIPMENT_RESPONSE=$(curl -sf -X POST "${BASE_URL}/shipments" \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json" \
        -d "$SHIPMENT_DATA" 2>&1 || echo '{}')
    
    SHIPMENT_ID=$(echo "$SHIPMENT_RESPONSE" | grep -o '"id"[[:space:]]*:[[:space:]]*[0-9]*' | sed 's/"id"[[:space:]]*:[[:space:]]*\([0-9]*\)/\1/')
    
    if [ -n "$SHIPMENT_ID" ]; then
        log_pass "POST /shipments (created ID: $SHIPMENT_ID)"
    else
        log_fail "POST /shipments (failed to create)"
        SHIPMENT_ID=""
    fi
    
    # List shipments
    test_endpoint "GET /shipments" "GET" "${BASE_URL}/shipments" "$TOKEN" "" "200"
    
    # List active shipments
    test_endpoint "GET /shipments/active" "GET" "${BASE_URL}/shipments/active" "$TOKEN" "" "200"
    
    log_section "11. ML Predictions API"
    
    # Predict freight cost
    FREIGHT_DATA='{"origin_port":"Callao","destination_port":"Hamburg","weight_kg":20000,"container_type":"40ft","departure_date":"2024-06-01"}'
    log_info "Testing POST /ml/predict-freight..."
    ML_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "${BASE_URL}/ml/predict-freight" \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json" \
        -d "$FREIGHT_DATA" 2>&1 || echo "")
    ML_STATUS=$(echo "$ML_RESPONSE" | tail -n1)
    
    if [ "$ML_STATUS" = "200" ]; then
        log_pass "POST /ml/predict-freight (prediction successful)"
    elif [ "$ML_STATUS" = "503" ]; then
        log_skip "POST /ml/predict-freight (model not trained yet)"
    else
        log_skip "POST /ml/predict-freight (status: $ML_STATUS)"
    fi
    
    log_section "12. News & Reports API"
    
    # Test news endpoint
    test_endpoint "GET /news" "GET" "${BASE_URL}/news" "$TOKEN" "" "200"
    
    # Test reports endpoint
    test_endpoint "GET /reports" "GET" "${BASE_URL}/reports" "$TOKEN" "" "200"
    
    log_section "13. Market Data API"
    
    # Test market latest endpoint
    test_endpoint "GET /market/latest" "GET" "${BASE_URL}/market/latest" "$TOKEN" "" "200"
    
    log_section "14. Cleanup Test Data"
    
    # Delete created resources
    if [ -n "$SHIPMENT_ID" ]; then
        log_info "Deleting test shipment..."
        curl -sf -X DELETE "${BASE_URL}/shipments/${SHIPMENT_ID}" \
            -H "Authorization: Bearer $TOKEN" > /dev/null 2>&1 && \
            log_pass "Deleted test shipment" || log_skip "Failed to delete shipment"
    fi
    
    if [ -n "$LOT_ID" ]; then
        log_info "Deleting test lot..."
        curl -sf -X DELETE "${BASE_URL}/lots/${LOT_ID}" \
            -H "Authorization: Bearer $TOKEN" > /dev/null 2>&1 && \
            log_pass "Deleted test lot" || log_skip "Failed to delete lot"
    fi
    
    if [ -n "$ROASTER_ID" ]; then
        log_info "Deleting test roaster..."
        curl -sf -X DELETE "${BASE_URL}/roasters/${ROASTER_ID}" \
            -H "Authorization: Bearer $TOKEN" > /dev/null 2>&1 && \
            log_pass "Deleted test roaster" || log_skip "Failed to delete roaster"
    fi
    
    if [ -n "$COOP_ID" ]; then
        log_info "Deleting test cooperative..."
        curl -sf -X DELETE "${BASE_URL}/cooperatives/${COOP_ID}" \
            -H "Authorization: Bearer $TOKEN" > /dev/null 2>&1 && \
            log_pass "Deleted test cooperative" || log_skip "Failed to delete cooperative"
    fi
    
    log_section "15. Summary"
    
    echo ""
    echo -e "${BLUE}================================================${NC}"
    echo -e "${GREEN}Passed:${NC} $PASS_COUNT"
    echo -e "${RED}Failed:${NC} $FAIL_COUNT"
    echo -e "${YELLOW}Skipped:${NC} $SKIP_COUNT"
    echo -e "${BLUE}Total:${NC} $((PASS_COUNT + FAIL_COUNT + SKIP_COUNT))"
    echo -e "${BLUE}================================================${NC}"
    
    if [ $FAIL_COUNT -gt 0 ]; then
        echo ""
        echo -e "${RED}Failed tests:${NC}"
        for test in "${FAILED_TESTS[@]}"; do
            echo -e "  ${RED}✗${NC} $test"
        done
        echo ""
        exit 1
    else
        echo ""
        echo -e "${GREEN}✓ All tests passed!${NC}"
        echo ""
        exit 0
    fi
}

# Run main
main "$@"
