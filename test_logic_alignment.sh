#!/bin/bash
set -e

# Base URL (API Gateway)
API="http://localhost:8000/api/v1"

echo "=============================================="
echo "    Testing Real-time Logic Alignment         "
echo "=============================================="

# Helper function to get value from JSON
get_json_val() {
    echo "$1" | grep -o "\"$2\":\"[^\"]*" | cut -d'"' -f4
}

# 1. Register Alice and Bob
echo -n "Registering Alice & Bob... "
curl -s -X POST "$API/users/register/" -H "Content-Type: application/json" -d '{"username": "alice", "email": "alice@example.com", "password": "password123"}' > /dev/null
curl -s -X POST "$API/users/register/" -H "Content-Type: application/json" -d '{"username": "bob", "email": "bob@example.com", "password": "password123"}' > /dev/null
echo "OK"

# 2. Login
echo -n "Logging in... "
ALICE_TOKEN=$(get_json_val "$(curl -s -X POST "$API/auth/login/" -H "Content-Type: application/json" -d '{"username": "alice", "password": "password123"}')" "access_token")
BOB_TOKEN=$(get_json_val "$(curl -s -X POST "$API/auth/login/" -H "Content-Type: application/json" -d '{"username": "bob", "password": "password123"}')" "access_token")
echo "OK"

# 3. Top up balances
echo -n "Topping up Bob (\$1000)... "
curl -s -X POST "$API/users/me/top-up/" -H "Authorization: Bearer $BOB_TOKEN" -H "Content-Type: application/json" -d '{"amount": "1000.00"}' > /dev/null
echo -n "Topping up Alice (\$1000)... "
curl -s -X POST "$API/users/me/top-up/" -H "Authorization: Bearer $ALICE_TOKEN" -H "Content-Type: application/json" -d '{"amount": "1000.00"}' > /dev/null
echo "OK"

# 4. Scenario Setup
echo -n "Alice creating Auction & Lot... "
AUCTION_RES=$(curl -s -X POST "$API/auctions/" -H "Authorization: Bearer $ALICE_TOKEN" -H "Content-Type: application/json" -d '{"title": "Test Auction", "description": "Desc", "closes_at": "2030-01-01T00:00:00Z"}')
AUCTION_ID=$(get_json_val "$AUCTION_RES" "id")
LOT_RES=$(curl -s -X POST "$API/lots/" -H "Authorization: Bearer $ALICE_TOKEN" -H "Content-Type: application/json" -d "{\"auction_id\": \"$AUCTION_ID\", \"title\": \"Test Lot\", \"description\": \"Desc\", \"starting_price\": \"100.00\", \"min_bid_increment\": \"10.00\"}")
LOT_ID=$(get_json_val "$LOT_RES" "id")
curl -s -X POST "$API/auctions/$AUCTION_ID/open/" -H "Authorization: Bearer $ALICE_TOKEN" > /dev/null
echo "OK (Lot ID: $LOT_ID)"

echo "----------------------------------------------"
echo "TEST 1: Bob bids \$150"
curl -s -X POST "$API/bids/" -H "Authorization: Bearer $BOB_TOKEN" -H "Content-Type: application/json" -d "{\"lot_id\": \"$LOT_ID\", \"amount\": \"150.00\"}" > /dev/null
# Check Lot price
LOT_INFO=$(curl -s -X GET "$API/lots/$LOT_ID/")
CURRENT_PRICE=$(get_json_val "$LOT_INFO" "current_price")
echo "Lot Current Price: $CURRENT_PRICE (Expected: 150.00)"
# Check Bob balance
BOB_INFO=$(curl -s -X GET "$API/users/me/" -H "Authorization: Bearer $BOB_TOKEN")
BOB_LOCKED=$(get_json_val "$BOB_INFO" "locked_balance")
echo "Bob Locked Balance: $BOB_LOCKED (Expected: 150.00)"

echo "----------------------------------------------"
echo "TEST 2: Charlie bids \$200 (Bob should be refunded)"
echo -n "Registering Charlie & Topping up (\$1000)... "
curl -s -X POST "$API/users/register/" -H "Content-Type: application/json" -d '{"username": "charlie", "email": "charlie@example.com", "password": "password123"}' > /dev/null
CHARLIE_TOKEN=$(get_json_val "$(curl -s -X POST "$API/auth/login/" -H "Content-Type: application/json" -d '{"username": "charlie", "password": "password123"}')" "access_token")
curl -s -X POST "$API/users/me/top-up/" -H "Authorization: Bearer $CHARLIE_TOKEN" -H "Content-Type: application/json" -d '{"amount": "1000.00"}' > /dev/null
echo "OK"

echo "Charlie bids \$200..."
curl -s -X POST "$API/bids/" -H "Authorization: Bearer $CHARLIE_TOKEN" -H "Content-Type: application/json" -d "{\"lot_id\": \"$LOT_ID\", \"amount\": \"200.00\"}" > /dev/null
# Check Lot price
LOT_INFO=$(curl -s -X GET "$API/lots/$LOT_ID/")
CURRENT_PRICE=$(get_json_val "$LOT_INFO" "current_price")
echo "Lot Current Price: $CURRENT_PRICE (Expected: 200.00)"
# Check Bob balance (should be 0)
BOB_INFO=$(curl -s -X GET "$API/users/me/" -H "Authorization: Bearer $BOB_TOKEN")
BOB_LOCKED=$(get_json_val "$BOB_INFO" "locked_balance")
echo "Bob Locked Balance: $BOB_LOCKED (Expected: 0.00)"
# Check Charlie balance
CHARLIE_INFO=$(curl -s -X GET "$API/users/me/" -H "Authorization: Bearer $CHARLIE_TOKEN")
CHARLIE_LOCKED=$(get_json_val "$CHARLIE_INFO" "locked_balance")
echo "Charlie Locked Balance: $CHARLIE_LOCKED (Expected: 200.00)"

echo "----------------------------------------------"
echo "TEST 3: Bob re-bids \$250 (Charlie should be refunded)"
curl -s -X POST "$API/bids/" -H "Authorization: Bearer $BOB_TOKEN" -H "Content-Type: application/json" -d "{\"lot_id\": \"$LOT_ID\", \"amount\": \"250.00\"}" > /dev/null
# Check Lot price
LOT_INFO=$(curl -s -X GET "$API/lots/$LOT_ID/")
CURRENT_PRICE=$(get_json_val "$LOT_INFO" "current_price")
echo "Lot Current Price: $CURRENT_PRICE (Expected: 250.00)"
# Check Charlie balance (should be 0)
CHARLIE_INFO=$(curl -s -X GET "$API/users/me/" -H "Authorization: Bearer $CHARLIE_TOKEN")
CHARLIE_LOCKED=$(get_json_val "$CHARLIE_INFO" "locked_balance")
echo "Charlie Locked Balance: $CHARLIE_LOCKED (Expected: 0.00)"
# Check Bob balance
BOB_INFO=$(curl -s -X GET "$API/users/me/" -H "Authorization: Bearer $BOB_TOKEN")
BOB_LOCKED=$(get_json_val "$BOB_INFO" "locked_balance")
echo "Bob Locked Balance: $BOB_LOCKED (Expected: 250.00)"

echo "----------------------------------------------"
echo "TEST 4: Close Auction & Final Settlement"
curl -s -X POST "$API/auctions/$AUCTION_ID/close/" -H "Authorization: Bearer $ALICE_TOKEN" > /dev/null
sleep 2 # wait for async settle
# Check Lot status
LOT_INFO=$(curl -s -X GET "$API/lots/$LOT_ID/")
LOT_STATUS=$(get_json_val "$LOT_INFO" "status")
echo "Lot Status: $LOT_STATUS (Expected: SOLD)"
# Final Balances
ALICE_INFO=$(curl -s -X GET "$API/users/me/" -H "Authorization: Bearer $ALICE_TOKEN")
ALICE_BAL=$(get_json_val "$ALICE_INFO" "balance")
echo "Alice Final Balance: $ALICE_BAL (Expected: 1250.00)"
BOB_INFO=$(curl -s -X GET "$API/users/me/" -H "Authorization: Bearer $BOB_TOKEN")
BOB_BAL=$(get_json_val "$BOB_INFO" "balance")
BOB_LOCKED=$(get_json_val "$BOB_INFO" "locked_balance")
echo "Bob Final Balance: $BOB_BAL (Expected: 750.00)"
echo "Bob Final Locked: $BOB_LOCKED (Expected: 0.00)"

echo "----------------------------------------------"
echo "LOGIC ALIGNMENT TESTS COMPLETED"
