#!/bin/bash
set -e

# Base URL (API Gateway)
API="http://localhost:8000/api/v1"
INTERNAL_USER_API="http://localhost:8001/api/v1"
INTERNAL_AUCTION_API="http://localhost:8002/api/v1"
INTERNAL_BIDDING_API="http://localhost:8003/api/v1"

echo "=============================================="
echo "    Microservices Auction Platform Tests      "
echo "=============================================="

# 1. Start clean
echo "Starting clean..."
sleep 2

# 2. Register User 1 (Seller)
echo -n "Registering Alice (Seller)... "
RES=$(curl -s -X POST "$API/users/register" -H "Content-Type: application/json" -d '{"username": "alice", "email": "alice@example.com", "password": "password123"}')
if echo "$RES" | grep -q '"id"'; then echo "OK"; else echo "FAILED: $RES"; exit 1; fi

# Login Alice
echo -n "Logging in Alice... "
ALICE_AUTH=$(curl -s -c /tmp/cookies.txt -X POST "$API/auth/login" -H "Content-Type: application/json" -d '{"username": "alice", "password": "password123"}')
ALICE_TOKEN=$(echo "$ALICE_AUTH" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
if [ -n "$ALICE_TOKEN" ]; then echo "OK"; else echo "FAILED"; exit 1; fi

# 3. Register User 2 (Buyer)
echo -n "Registering Bob (Buyer)... "
RES=$(curl -s -X POST "$API/users/register" -H "Content-Type: application/json" -d '{"username": "bob", "email": "bob@example.com", "password": "password123"}')
if echo "$RES" | grep -q '"id"'; then echo "OK"; else echo "FAILED: $RES"; exit 1; fi

# Login Bob
echo -n "Logging in Bob... "
BOB_AUTH=$(curl -s -c /tmp/cookies.txt -X POST "$API/auth/login" -H "Content-Type: application/json" -d '{"username": "bob", "password": "password123"}')
BOB_TOKEN=$(echo "$BOB_AUTH" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
if [ -n "$BOB_TOKEN" ]; then echo "OK"; else echo "FAILED"; exit 1; fi

# 4. Top up Bob's balance
echo -n "Topping up Bob's balance... "
RES=$(curl -s -X POST "$API/users/me/top-up" -H "Authorization: Bearer $BOB_TOKEN" -H "Content-Type: application/json" -d '{"amount": "1000.00"}')
if echo "$RES" | grep -q '"balance":"1000.00"'; then echo "OK"; else echo "FAILED: $RES"; exit 1; fi

# 5. Alice creates an Auction
echo -n "Alice creates an Auction... "
RES=$(curl -s -X POST "$API/auctions" -H "Authorization: Bearer $ALICE_TOKEN" -H "Content-Type: application/json" -d '{"title": "Alice Vintage Collection", "description": "Awesome stuff", "closes_at": "2030-01-01T00:00:00Z"}')
AUCTION_ID=$(echo "$RES" | grep -o '"id":"[^"]*' | cut -d'"' -f4)
if [ -n "$AUCTION_ID" ]; then echo "OK ($AUCTION_ID)"; else echo "FAILED: $RES"; exit 1; fi

# 6. Alice adds a Lot to the Auction
echo -n "Alice adds a Lot... "
RES=$(curl -s -X POST "$API/lots" -H "Authorization: Bearer $ALICE_TOKEN" -H "Content-Type: application/json" -d "{\"auction_id\": \"$AUCTION_ID\", \"title\": \"Old Watch\", \"description\": \"Still ticks\", \"starting_price\": \"100.00\", \"min_bid_increment\": \"10.00\"}")
LOT_ID=$(echo "$RES" | grep -o '"id":"[^"]*' | cut -d'"' -f4)
if [ -n "$LOT_ID" ]; then echo "OK ($LOT_ID)"; else echo "FAILED: $RES"; exit 1; fi

# 7. Alice opens the Auction
echo -n "Alice opens the Auction... "
RES=$(curl -s -X POST "$API/auctions/$AUCTION_ID/open" -H "Authorization: Bearer $ALICE_TOKEN")
if echo "$RES" | grep -q '"status":"ACTIVE"'; then echo "OK"; else echo "FAILED: $RES"; exit 1; fi

# 8. Bob places a Bid
echo -n "Bob places a Bid ($150)... "
RES=$(curl -s -X POST "$API/bids" -H "Authorization: Bearer $BOB_TOKEN" -H "Content-Type: application/json" -d "{\"lot_id\": \"$LOT_ID\", \"amount\": \"150.00\"}")
if echo "$RES" | grep -q '"amount":"150.00"'; then echo "OK"; else echo "FAILED: $RES"; exit 1; fi

# 9. Verify Bob's locked balance
echo -n "Verifying Bob's locked balance ($150)... "
RES=$(curl -s -X GET "$API/users/me" -H "Authorization: Bearer $BOB_TOKEN")
if echo "$RES" | grep -q '"locked_balance":"150.00"'; then echo "OK"; else echo "FAILED: $RES"; exit 1; fi

# 10. Alice closes the Auction
echo -n "Alice closes the Auction... "
RES=$(curl -s -X POST "$API/auctions/$AUCTION_ID/close" -H "Authorization: Bearer $ALICE_TOKEN")
if echo "$RES" | grep -q '"status":"CLOSED"'; then echo "OK"; else echo "FAILED: $RES"; exit 1; fi

# 11. Verify Lot is SOLD
echo -n "Verifying Lot is SOLD... "
sleep 1 # wait for async settle
RES=$(curl -s -X GET "$API/lots/$LOT_ID")
if echo "$RES" | grep -q '"status":"SOLD"'; then echo "OK"; else echo "FAILED: $RES"; exit 1; fi

# 12. Verify Alice got paid
echo -n "Verifying Alice got paid ($150)... "
RES=$(curl -s -X GET "$API/users/me" -H "Authorization: Bearer $ALICE_TOKEN")
if echo "$RES" | grep -q '"balance":"150.00"'; then echo "OK"; else echo "FAILED: $RES"; exit 1; fi

# 13. Verify Bob's balance decreased
echo -n "Verifying Bob's balance decreased to 850... "
RES=$(curl -s -X GET "$API/users/me" -H "Authorization: Bearer $BOB_TOKEN")
if echo "$RES" | grep -q '"balance":"850.00"'; then echo "OK"; else echo "FAILED: $RES"; exit 1; fi

echo ""
echo "ALL TESTS PASSED SUCCESSFULLY!"
