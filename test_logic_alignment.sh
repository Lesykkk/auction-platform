#!/bin/bash
set -euo pipefail

# Service URLs
GATEWAY="http://127.0.0.1:63221/api/v1"
USER_API="$GATEWAY"
AUCTION_API="$GATEWAY"
BIDDING_API="$GATEWAY"
SUFFIX="$(date +%s)_$$"
ALICE_USERNAME="alice_${SUFFIX}"
ALICE_EMAIL="alice_${SUFFIX}@example.com"
BOB_USERNAME="bob_${SUFFIX}"
BOB_EMAIL="bob_${SUFFIX}@example.com"
CHARLIE_USERNAME="charlie_${SUFFIX}"
CHARLIE_EMAIL="charlie_${SUFFIX}@example.com"

echo "=============================================="
echo "    Testing Real-time Logic Alignment         "
echo "=============================================="

# Helper function to get value from JSON
get_json_val() {
    echo "$1" | grep -o "\"$2\":\"[^\"]*" | cut -d'"' -f4
}

assert_equals() {
    local actual="$1"
    local expected="$2"
    local message="$3"
    if [ "$actual" = "$expected" ]; then
        echo "$message: $actual (OK)"
    else
        echo "$message: $actual (Expected: $expected)"
        exit 1
    fi
}

assert_nonempty() {
    local value="$1"
    local message="$2"
    if [ -n "$value" ]; then
        echo "$message"
    else
        echo "FAILED: $message"
        exit 1
    fi
}

# 1. Register Alice and Bob
echo -n "Registering Alice & Bob... "
ALICE_REG=$(curl -s -X POST "$USER_API/users/register" -H "Content-Type: application/json" -d "{\"username\": \"$ALICE_USERNAME\", \"email\": \"$ALICE_EMAIL\", \"password\": \"password123\"}")
BOB_REG=$(curl -s -X POST "$USER_API/users/register" -H "Content-Type: application/json" -d "{\"username\": \"$BOB_USERNAME\", \"email\": \"$BOB_EMAIL\", \"password\": \"password123\"}")
assert_nonempty "$(get_json_val "$ALICE_REG" "id")" "Alice registration OK"
assert_nonempty "$(get_json_val "$BOB_REG" "id")" "Bob registration OK"
echo "OK"

# 2. Login
echo -n "Logging in... "
ALICE_LOGIN=$(curl -s -X POST "$USER_API/auth/login" -H "Content-Type: application/json" -d "{\"username\": \"$ALICE_USERNAME\", \"password\": \"password123\"}")
BOB_LOGIN=$(curl -s -X POST "$USER_API/auth/login" -H "Content-Type: application/json" -d "{\"username\": \"$BOB_USERNAME\", \"password\": \"password123\"}")
ALICE_TOKEN=$(get_json_val "$ALICE_LOGIN" "access_token")
BOB_TOKEN=$(get_json_val "$BOB_LOGIN" "access_token")
assert_nonempty "$ALICE_TOKEN" "Alice login OK"
assert_nonempty "$BOB_TOKEN" "Bob login OK"
echo "OK"

# 3. Top up balances
echo -n "Topping up Bob (\$1000)... "
curl -s -X POST "$USER_API/users/me/top-up" -H "Authorization: Bearer $BOB_TOKEN" -H "Content-Type: application/json" -d '{"amount": "1000.00"}' > /dev/null
echo -n "Topping up Alice (\$1000)... "
curl -s -X POST "$USER_API/users/me/top-up" -H "Authorization: Bearer $ALICE_TOKEN" -H "Content-Type: application/json" -d '{"amount": "1000.00"}' > /dev/null
echo "OK"

# 4. Scenario Setup
echo -n "Alice creating Auction & Lot... "
AUCTION_RES=$(curl -s -X POST "$AUCTION_API/auctions" -H "Authorization: Bearer $ALICE_TOKEN" -H "Content-Type: application/json" -d '{"title": "Test Auction", "description": "Verification of bidding flow", "closes_at": "2030-01-01T00:00:00Z"}')
AUCTION_ID=$(get_json_val "$AUCTION_RES" "id")
assert_nonempty "$AUCTION_ID" "Auction created"
LOT_RES=$(curl -s -X POST "$AUCTION_API/lots" -H "Authorization: Bearer $ALICE_TOKEN" -H "Content-Type: application/json" -d "{\"auction_id\": \"$AUCTION_ID\", \"title\": \"Test Lot\", \"description\": \"Testing price update and refund\", \"starting_price\": \"100.00\", \"min_bid_increment\": \"10.00\"}")
LOT_ID=$(get_json_val "$LOT_RES" "id")
assert_nonempty "$LOT_ID" "Lot created"
curl -s -X POST "$AUCTION_API/auctions/$AUCTION_ID/open" -H "Authorization: Bearer $ALICE_TOKEN" > /dev/null
echo "OK (Lot ID: $LOT_ID)"

echo "----------------------------------------------"
echo "TEST 1: Bob bids \$150"
curl -s -X POST "$BIDDING_API/bids" -H "Authorization: Bearer $BOB_TOKEN" -H "Content-Type: application/json" -d "{\"lot_id\": \"$LOT_ID\", \"amount\": \"150.00\"}" > /dev/null
# Check Lot price
LOT_INFO=$(curl -s -X GET "$AUCTION_API/lots/$LOT_ID")
CURRENT_PRICE=$(get_json_val "$LOT_INFO" "current_price")
assert_equals "$CURRENT_PRICE" "150.00" "Lot Current Price"
# Check Bob balance
BOB_INFO=$(curl -s -X GET "$USER_API/users/me" -H "Authorization: Bearer $BOB_TOKEN")
BOB_LOCKED=$(get_json_val "$BOB_INFO" "locked_balance")
assert_equals "$BOB_LOCKED" "150.00" "Bob Locked Balance"

echo "----------------------------------------------"
echo "TEST 2: Charlie bids \$200 (Bob should be refunded)"
echo -n "Registering Charlie & Topping up (\$1000)... "
CHARLIE_REG=$(curl -s -X POST "$USER_API/users/register" -H "Content-Type: application/json" -d "{\"username\": \"$CHARLIE_USERNAME\", \"email\": \"$CHARLIE_EMAIL\", \"password\": \"password123\"}")
assert_nonempty "$(get_json_val "$CHARLIE_REG" "id")" "Charlie registration OK"
CHARLIE_LOGIN=$(curl -s -X POST "$USER_API/auth/login" -H "Content-Type: application/json" -d "{\"username\": \"$CHARLIE_USERNAME\", \"password\": \"password123\"}")
CHARLIE_TOKEN=$(get_json_val "$CHARLIE_LOGIN" "access_token")
assert_nonempty "$CHARLIE_TOKEN" "Charlie login OK"
curl -s -X POST "$USER_API/users/me/top-up" -H "Authorization: Bearer $CHARLIE_TOKEN" -H "Content-Type: application/json" -d '{"amount": "1000.00"}' > /dev/null
echo "OK"

echo "Charlie bids \$200..."
curl -s -X POST "$BIDDING_API/bids" -H "Authorization: Bearer $CHARLIE_TOKEN" -H "Content-Type: application/json" -d "{\"lot_id\": \"$LOT_ID\", \"amount\": \"200.00\"}" > /dev/null
# Check Lot price
LOT_INFO=$(curl -s -X GET "$AUCTION_API/lots/$LOT_ID")
CURRENT_PRICE=$(get_json_val "$LOT_INFO" "current_price")
assert_equals "$CURRENT_PRICE" "200.00" "Lot Current Price"
# Check Bob balance (should be 0)
BOB_INFO=$(curl -s -X GET "$USER_API/users/me" -H "Authorization: Bearer $BOB_TOKEN")
BOB_LOCKED=$(get_json_val "$BOB_INFO" "locked_balance")
assert_equals "$BOB_LOCKED" "0.00" "Bob Locked Balance"
# Check Charlie balance
CHARLIE_INFO=$(curl -s -X GET "$USER_API/users/me" -H "Authorization: Bearer $CHARLIE_TOKEN")
CHARLIE_LOCKED=$(get_json_val "$CHARLIE_INFO" "locked_balance")
assert_equals "$CHARLIE_LOCKED" "200.00" "Charlie Locked Balance"

echo "----------------------------------------------"
echo "TEST 3: Bob re-bids \$250 (after refund)"
curl -s -X POST "$BIDDING_API/bids" -H "Authorization: Bearer $BOB_TOKEN" -H "Content-Type: application/json" -d "{\"lot_id\": \"$LOT_ID\", \"amount\": \"250.00\"}" > /dev/null
LOT_INFO=$(curl -s -X GET "$AUCTION_API/lots/$LOT_ID")
CURRENT_PRICE=$(get_json_val "$LOT_INFO" "current_price")
assert_equals "$CURRENT_PRICE" "250.00" "Lot Current Price"
CHARLIE_INFO=$(curl -s -X GET "$USER_API/users/me" -H "Authorization: Bearer $CHARLIE_TOKEN")
CHARLIE_LOCKED=$(get_json_val "$CHARLIE_INFO" "locked_balance")
assert_equals "$CHARLIE_LOCKED" "0.00" "Charlie Locked Balance"
BOB_INFO=$(curl -s -X GET "$USER_API/users/me" -H "Authorization: Bearer $BOB_TOKEN")
BOB_LOCKED=$(get_json_val "$BOB_INFO" "locked_balance")
assert_equals "$BOB_LOCKED" "250.00" "Bob Locked Balance"

echo "----------------------------------------------"
echo "TEST 4: Close Auction & Final Settlement"
curl -s -X POST "$AUCTION_API/auctions/$AUCTION_ID/close" -H "Authorization: Bearer $ALICE_TOKEN" > /dev/null
sleep 2 # wait for async settle
# Check Lot status
LOT_INFO=$(curl -s -X GET "$AUCTION_API/lots/$LOT_ID")
LOT_STATUS=$(get_json_val "$LOT_INFO" "status")
assert_equals "$LOT_STATUS" "SOLD" "Lot Status"
# Final Balances
ALICE_INFO=$(curl -s -X GET "$USER_API/users/me" -H "Authorization: Bearer $ALICE_TOKEN")
ALICE_BAL=$(get_json_val "$ALICE_INFO" "balance")
assert_equals "$ALICE_BAL" "1250.00" "Alice Final Balance"
BOB_INFO=$(curl -s -X GET "$USER_API/users/me" -H "Authorization: Bearer $BOB_TOKEN")
BOB_BAL=$(get_json_val "$BOB_INFO" "balance")
BOB_LOCKED=$(get_json_val "$BOB_INFO" "locked_balance")
assert_equals "$BOB_BAL" "750.00" "Bob Final Balance"
assert_equals "$BOB_LOCKED" "0.00" "Bob Final Locked"
CHARLIE_INFO=$(curl -s -X GET "$USER_API/users/me" -H "Authorization: Bearer $CHARLIE_TOKEN")
CHARLIE_BAL=$(get_json_val "$CHARLIE_INFO" "balance")
CHARLIE_LOCKED=$(get_json_val "$CHARLIE_INFO" "locked_balance")
assert_equals "$CHARLIE_BAL" "1000.00" "Charlie Final Balance"
assert_equals "$CHARLIE_LOCKED" "0.00" "Charlie Final Locked"

echo "----------------------------------------------"
echo "LOGIC ALIGNMENT TESTS COMPLETED"
