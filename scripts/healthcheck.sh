#!/usr/bin/env bash
# MiniPay health check — exits 0 healthy, 1 degraded, 2 unhealthy
set -uo pipefail

API_URL="${API_URL:-http://localhost:8081}"
UI_URL="${UI_URL:-http://localhost:8080}"
WARNS=0
FAILS=0

pass() { echo "[ OK ] $1"; }
warn() { echo "[WARN] $1"; WARNS=$((WARNS+1)); }
fail() { echo "[FAIL] $1"; FAILS=$((FAILS+1)); }

echo "=== MiniPay Health Check — $(date) ==="

# CPU load
cores=$(nproc)
load=$(awk '{print $1}' /proc/loadavg)
if awk -v l="$load" -v c="$cores" 'BEGIN{exit !(l > c)}'; then
    warn "CPU load $load exceeds $cores cores"
else
    pass "CPU load $load on $cores cores"
fi

# Memory
read total avail < <(awk '/MemTotal/{t=$2}/MemAvailable/{a=$2}END{print t,a}' /proc/meminfo)
pct=$(( (total - avail) * 100 / total ))
[ "$pct" -ge 90 ] && warn "Memory ${pct}% used" || pass "Memory ${pct}% used"

# Disk
df -P / | awk 'NR==2{pct=$5+0; if(pct>=90) print "[FAIL] Disk "pct"% full"; else if(pct>=80) print "[WARN] Disk "pct"% full"; else print "[ OK ] Disk "pct"% used"}'

# Listening ports
for port in 8080 8081 5432; do
    ss -tln | grep -q ":${port}\b" \
        && pass "Port $port listening" \
        || warn "Port $port NOT listening"
done

# API health endpoint
code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 5 "$API_URL/health" 2>/dev/null || echo 000)
[ "$code" = "200" ] && pass "API health $code" || fail "API health returned $code"

# Database reachable from API
body=$(curl -s --max-time 5 "$API_URL/health" 2>/dev/null || echo '{}')
echo "$body" | grep -q '"database":"ok"' \
    && pass "Database reachable from API" \
    || fail "Database NOT ok: $body"

# UI reachable
uicode=$(curl -s -o /dev/null -w '%{http_code}' --max-time 5 "$UI_URL/" 2>/dev/null || echo 000)
[ "$uicode" = "200" ] && pass "UI returned $uicode" || fail "UI returned $uicode"

# Container status
if command -v docker &>/dev/null; then
    unhealthy=$(docker ps --filter health=unhealthy --format '{{.Names}}' 2>/dev/null)
    [ -n "$unhealthy" ] && fail "Unhealthy containers: $unhealthy" || pass "No unhealthy containers"
fi

echo ""
echo "Summary: $FAILS FAIL, $WARNS WARN"
[ "$FAILS" -gt 0 ] && exit 2
[ "$WARNS" -gt 0 ] && exit 1
exit 0
