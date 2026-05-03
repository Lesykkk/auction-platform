#!/bin/bash
set -euo pipefail

# Service URLs
USER_API="http://127.0.0.1:8001/api/v1"
AUCTION_API="http://127.0.0.1:8002/api/v1"
BIDDING_API="http://127.0.0.1:8003/api/v1"
SUFFIX="$(date +%s)_$$"
ALICE_USERNAME="alice_${SUFFIX}"
ALICE_EMAIL="alice_${SUFFIX}@example.com"
BOB_USERNAME="bob_${SUFFIX}"
BOB_EMAIL="bob_${SUFFIX}@example.com"

echo "=============================================="
echo "    Microservices Auction Platform Tests      "
echo "=============================================="

json_field() {
    echo "$1" | grep -o "\"$2\":\"[^\"]*" | cut -d'"' -f4
}

assert_contains() {
    local body="$1"
    local needle="$2"
    local message="$3"
    if echo "$body" | grep -q "$needle"; then
        echo "OK"
    else
        echo "FAILED: $message"
        echo "$body"
        exit 1
    fi
}

# 2. Register User 1 (Seller)
echo -n "Registering Alice (Seller)... "
RES=$(curl -s -X POST "$USER_API/users/register" -H "Content-Type: application/json" -d "{\"username\": \"$ALICE_USERNAME\", \"email\": \"$ALICE_EMAIL\", \"password\": \"password123\"}")
assert_contains "$RES" '"id"' "Alice registration did not return an id"

# Login Alice
echo -n "Logging in Alice... "
ALICE_AUTH=$(curl -s -X POST "$USER_API/auth/login" -H "Content-Type: application/json" -d "{\"username\": \"$ALICE_USERNAME\", \"password\": \"password123\"}")
ALICE_TOKEN=$(json_field "$ALICE_AUTH" "access_token")
if [ -n "$ALICE_TOKEN" ]; then echo "OK"; else echo "FAILED"; echo "$ALICE_AUTH"; exit 1; fi

# 3. Register User 2 (Buyer)
echo -n "Registering Bob (Buyer)... "
RES=$(curl -s -X POST "$USER_API/users/register" -H "Content-Type: application/json" -d "{\"username\": \"$BOB_USERNAME\", \"email\": \"$BOB_EMAIL\", \"password\": \"password123\"}")
assert_contains "$RES" '"id"' "Bob registration did not return an id"

# Login Bob
echo -n "Logging in Bob... "
BOB_AUTH=$(curl -s -X POST "$USER_API/auth/login" -H "Content-Type: application/json" -d "{\"username\": \"$BOB_USERNAME\", \"password\": \"password123\"}")
BOB_TOKEN=$(json_field "$BOB_AUTH" "access_token")
if [ -n "$BOB_TOKEN" ]; then echo "OK"; else echo "FAILED"; echo "$BOB_AUTH"; exit 1; fi

# 4. Top up Bob's balance
echo -n "Topping up Bob's balance... "
RES=$(curl -s -X POST "$USER_API/users/me/top-up" -H "Authorization: Bearer $BOB_TOKEN" -H "Content-Type: application/json" -d '{"amount": "1000.00"}')
assert_contains "$RES" '"balance":"1000.00"' "Bob top-up failed"

# 5. Alice creates an Auction
echo -n "Alice creates an Auction... "
RES=$(curl -s -X POST "$AUCTION_API/auctions" -H "Authorization: Bearer $ALICE_TOKEN" -H "Content-Type: application/json" -d '{"title": "Alice Vintage Collection", "description": "Awesome stuff", "closes_at": "2030-01-01T00:00:00Z"}')
AUCTION_ID=$(json_field "$RES" "id")
if [ -n "$AUCTION_ID" ]; then echo "OK ($AUCTION_ID)"; else echo "FAILED: $RES"; exit 1; fi

# 6. Alice adds a Lot to the Auction
echo -n "Alice adds a Lot... "
RES=$(curl -s -X POST "$AUCTION_API/lots" -H "Authorization: Bearer $ALICE_TOKEN" -H "Content-Type: application/json" -d "{\"auction_id\": \"$AUCTION_ID\", \"title\": \"Old Watch\", \"description\": \"Still ticks\", \"starting_price\": \"100.00\", \"min_bid_increment\": \"10.00\"}")
LOT_ID=$(json_field "$RES" "id")
if [ -n "$LOT_ID" ]; then echo "OK ($LOT_ID)"; else echo "FAILED: $RES"; exit 1; fi

# 7. Alice opens the Auction
echo -n "Alice opens the Auction... "
RES=$(curl -s -X POST "$AUCTION_API/auctions/$AUCTION_ID/open" -H "Authorization: Bearer $ALICE_TOKEN")
assert_contains "$RES" '"status":"ACTIVE"' "Auction was not opened"

# 8. Bob places a Bid
echo -n "Bob places a Bid (\$150)... "
RES=$(curl -s -X POST "$BIDDING_API/bids" -H "Authorization: Bearer $BOB_TOKEN" -H "Content-Type: application/json" -d "{\"lot_id\": \"$LOT_ID\", \"amount\": \"150.00\"}")
assert_contains "$RES" '"amount":"150.00"' "Bid creation failed"

# 9. Verify Bob's locked balance
echo -n "Verifying Bob's locked balance (\$150)... "
RES=$(curl -s -X GET "$USER_API/users/me" -H "Authorization: Bearer $BOB_TOKEN")
assert_contains "$RES" '"locked_balance":"150.00"' "Bob locked balance mismatch after first bid"

# 10. Alice closes the Auction
echo -n "Alice closes the Auction... "
RES=$(curl -s -X POST "$AUCTION_API/auctions/$AUCTION_ID/close" -H "Authorization: Bearer $ALICE_TOKEN")
assert_contains "$RES" '"status":"CLOSED"' "Auction close failed"

# 11. Verify Lot is SOLD
echo -n "Verifying Lot is SOLD... "
sleep 1 # wait for async settle
RES=$(curl -s -X GET "$AUCTION_API/lots/$LOT_ID")
assert_contains "$RES" '"status":"SOLD"' "Lot was not sold after close"

# 12. Verify Alice got paid
echo -n "Verifying Alice got paid (\$150)... "
RES=$(curl -s -X GET "$USER_API/users/me" -H "Authorization: Bearer $ALICE_TOKEN")
assert_contains "$RES" '"balance":"150.00"' "Seller balance mismatch after settlement"

# 13. Verify Bob's balance decreased
echo -n "Verifying Bob's balance decreased to \$850... "
RES=$(curl -s -X GET "$USER_API/users/me" -H "Authorization: Bearer $BOB_TOKEN")
assert_contains "$RES" '"balance":"850.00"' "Buyer balance mismatch after settlement"

echo ""
echo "ALL TESTS PASSED SUCCESSFULLY!"
