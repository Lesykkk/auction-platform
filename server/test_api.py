"""
Test script for Auction Platform API.
Run: python test_api.py
Requires: pip install httpx
"""

import sys
import httpx

sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://localhost:8000/api/v1"


def print_result(method: str, url: str, status: int, body, expected_status: int):
    ok = "✅" if status == expected_status else "❌"
    print(f"{ok} {method} {url} → {status} (expected {expected_status})")
    if status != expected_status:
        print(f"   Body: {body}")


def run():
    client = httpx.Client(base_url=BASE_URL)
    access_token = None
    seller_token = None
    buyer2_token = None
    auction_id = None
    lot_id = None
    lot2_id = None

    print("\n=== AUTH ===")

    r = client.post("/users/register", json={
        "username": "buyer1",
        "email": "buyer1@example.com",
        "password": "buyer1pass",
    })
    print_result("POST", "/users/register (buyer1)", r.status_code, r.json(), 200)

    r = client.post("/users/register", json={
        "username": "buyer2",
        "email": "buyer2@example.com",
        "password": "buyer2pass",
    })
    print_result("POST", "/users/register (buyer2)", r.status_code, r.json(), 200)

    r = client.post("/users/register", json={
        "username": "seller1",
        "email": "seller1@example.com",
        "password": "seller1pass",
    })
    print_result("POST", "/users/register (seller)", r.status_code, r.json(), 200)

    # Duplicate
    r = client.post("/users/register", json={
        "username": "buyer1",
        "email": "buyer1@example.com",
        "password": "buyer1pass",
    })
    print_result("POST", "/users/register (duplicate, should fail)", r.status_code, r.json(), 409)

    r = client.post("/auth/login", json={"username": "seller1", "password": "seller1pass"})
    print_result("POST", "/auth/login (seller)", r.status_code, r.json(), 200)
    if r.status_code == 200:
        seller_token = r.json()["access_token"]

    r = client.post("/auth/login", json={"username": "buyer1", "password": "buyer1pass"})
    print_result("POST", "/auth/login (buyer1)", r.status_code, r.json(), 200)
    if r.status_code == 200:
        access_token = r.json()["access_token"]

    r = client.post("/auth/login", json={"username": "buyer2", "password": "buyer2pass"})
    print_result("POST", "/auth/login (buyer2)", r.status_code, r.json(), 200)
    if r.status_code == 200:
        buyer2_token = r.json()["access_token"]

    r = client.post("/auth/login", json={"username": "buyer1", "password": "wrongpass"})
    print_result("POST", "/auth/login (wrong password, should fail)", r.status_code, r.json(), 401)

    r = client.post("/auth/refresh")
    print_result("POST", "/auth/refresh (no cookie, should fail)", r.status_code, r.json(), 401)

    buyer_headers = {"Authorization": f"Bearer {access_token}"}
    buyer2_headers = {"Authorization": f"Bearer {buyer2_token}"}
    seller_headers = {"Authorization": f"Bearer {seller_token}"}

    print("\n=== USERS ===")

    r = client.get("/users/me", headers=buyer_headers)
    print_result("GET", "/users/me", r.status_code, r.json(), 200)

    r = client.get("/users/me")
    print_result("GET", "/users/me (no token, should fail)", r.status_code, r.json(), 401)

    r = client.patch("/users/me", json={"username": "buyer1_updated"}, headers=buyer_headers)
    print_result("PATCH", "/users/me", r.status_code, r.json(), 200)

    r = client.post("/users/me/top-up", json={"amount": 5000}, headers=buyer_headers)
    print_result("POST", "/users/me/top-up (buyer1)", r.status_code, r.json(), 200)

    r = client.post("/users/me/top-up", json={"amount": 3000}, headers=buyer2_headers)
    print_result("POST", "/users/me/top-up (buyer2)", r.status_code, r.json(), 200)

    r = client.post("/users/me/top-up", json={"amount": -100}, headers=buyer_headers)
    print_result("POST", "/users/me/top-up (negative, should fail)", r.status_code, r.json(), 400)

    print("\n=== AUCTIONS ===")

    r = client.get("/auctions")
    print_result("GET", "/auctions", r.status_code, r.json(), 200)

    r = client.post("/auctions", json={
        "title": "Spring Collection",
        "description": "Premium art and collectibles.",
        "closes_at": "2027-01-01T00:00:00Z",
    }, headers=seller_headers)
    print_result("POST", "/auctions", r.status_code, r.json(), 200)
    if r.status_code == 200:
        auction_id = r.json()["id"]

    r = client.post("/auctions", json={
        "title": "No auth auction",
        "description": "Should fail.",
        "closes_at": "2027-01-01T00:00:00Z",
    })
    print_result("POST", "/auctions (no auth, should fail)", r.status_code, r.json(), 401)

    if auction_id:
        r = client.get(f"/auctions/{auction_id}")
        print_result("GET", "/auctions/{id}", r.status_code, r.json(), 200)

    # Test Auction Update
    if auction_id:
        r = client.patch(f"/auctions/{auction_id}", json={
            "description": "Updated premium art collection"
        }, headers=seller_headers)
        print_result("PATCH", "/auctions/{id} (owner)", r.status_code, r.json(), 200)

        # Update by non-owner
        r = client.patch(f"/auctions/{auction_id}", json={
            "title": "Hacked Title"
        }, headers=buyer_headers)
        print_result("PATCH", "/auctions/{id} (wrong user, should fail)", r.status_code, r.json(), 403)

    r = client.get("/auctions/00000000-0000-0000-0000-000000000000")
    print_result("GET", "/auctions/{id} (not found, should fail)", r.status_code, r.json(), 404)

    # Test Auction Delete on a separate PENDING auction
    r = client.post("/auctions", json={
        "title": "Auction to delete",
        "description": "Will be deleted soon.",
        "closes_at": "2027-01-01T00:00:00Z",
    }, headers=seller_headers)
    if r.status_code == 200:
        delete_auction_id = r.json()["id"]

        r = client.delete(f"/auctions/{delete_auction_id}", headers=buyer_headers)
        print_result("DELETE", "/auctions/{id} (wrong user, should fail)", r.status_code, r.json() if r.content else {}, 403)

        r = client.delete(f"/auctions/{delete_auction_id}", headers=seller_headers)
        print_result("DELETE", "/auctions/{id} (owner)", r.status_code, r.json() if r.content else {}, 200)

        r = client.delete(f"/auctions/{delete_auction_id}", headers=seller_headers)
        print_result("DELETE", "/auctions/{id} (already deleted, should fail)", r.status_code, r.json() if r.content else {}, 404)

    print("\n=== LOTS ===")

    if auction_id:
        r = client.post("/lots", json={
            "auction_id": auction_id,
            "title": "Vintage Guitar",
            "description": "1960s Fender Stratocaster in mint condition.",
            "starting_price": 2000,
            "min_bid_increment": 100,
        }, headers=seller_headers)
        print_result("POST", "/lots", r.status_code, r.json(), 200)
        if r.status_code == 200:
            lot_id = r.json()["id"]

    if auction_id:
        r = client.post("/lots", json={
            "auction_id": auction_id,
            "title": "Rare Painting",
            "description": "Oil on canvas, 18th century.",
            "starting_price": 5000,
            "min_bid_increment": 500,
        }, headers=seller_headers)
        print_result("POST", "/lots (lot2)", r.status_code, r.json(), 200)
        if r.status_code == 200:
            lot2_id = r.json()["id"]

    # Add lot by non-owner
    if auction_id:
        r = client.post("/lots", json={
            "auction_id": auction_id,
            "title": "Hacked lot",
            "description": "Should fail.",
            "starting_price": 100,
            "min_bid_increment": 10,
        }, headers=buyer_headers)
        print_result("POST", "/lots (wrong user, should fail)", r.status_code, r.json(), 403)

    if auction_id:
        r = client.get(f"/lots?auction_id={auction_id}")
        print_result("GET", "/lots?auction_id={id}", r.status_code, r.json(), 200)

    if lot_id:
        r = client.get(f"/lots/{lot_id}")
        print_result("GET", "/lots/{lot_id}", r.status_code, r.json(), 200)

    if lot_id:
        r = client.patch(f"/lots/{lot_id}", json={"title": "Vintage Guitar - Updated"}, headers=seller_headers)
        print_result("PATCH", "/lots/{lot_id} (owner)", r.status_code, r.json(), 200)

    if lot_id:
        r = client.patch(f"/lots/{lot_id}", json={"title": "Hacked"}, headers=buyer_headers)
        print_result("PATCH", "/lots/{lot_id} (wrong user, should fail)", r.status_code, r.json(), 403)

    print("\n=== OPEN AUCTION ===")

    # Open by non-owner
    if auction_id:
        r = client.post(f"/auctions/{auction_id}/open", headers=buyer_headers)
        print_result("POST", "/auctions/{id}/open (wrong user, should fail)", r.status_code, r.json(), 403)

    # Open by owner
    if auction_id:
        r = client.post(f"/auctions/{auction_id}/open", headers=seller_headers)
        print_result("POST", "/auctions/{id}/open (owner)", r.status_code, r.json(), 200)

    # Open already active auction
    if auction_id:
        r = client.post(f"/auctions/{auction_id}/open", headers=seller_headers)
        print_result("POST", "/auctions/{id}/open (already active, should fail)", r.status_code, r.json(), 400)

    # Add lot to active auction (should fail)
    if auction_id:
        r = client.post("/lots", json={
            "auction_id": auction_id,
            "title": "Late lot",
            "description": "Should fail, auction is active.",
            "starting_price": 100,
            "min_bid_increment": 10,
        }, headers=seller_headers)
        print_result("POST", "/lots (active auction, should fail)", r.status_code, r.json(), 400)

    print("\n=== BIDS ===")

    if lot_id:
        r = client.post("/bids", json={"lot_id": lot_id, "amount": 2100}, headers=buyer_headers)
        print_result("POST", "/bids (buyer1 valid)", r.status_code, r.json(), 200)

    # Organizer bids on own auction
    if lot_id:
        r = client.post("/bids", json={"lot_id": lot_id, "amount": 2200}, headers=seller_headers)
        print_result("POST", "/bids (organizer, should fail)", r.status_code, r.json(), 403)

    # Bid too low increment
    if lot_id:
        r = client.post("/bids", json={"lot_id": lot_id, "amount": 2150}, headers=buyer2_headers)
        print_result("POST", "/bids (too low increment, should fail)", r.status_code, r.json(), 400)

    # Bid without auth
    if lot_id:
        r = client.post("/bids", json={"lot_id": lot_id, "amount": 9999})
        print_result("POST", "/bids (no auth, should fail)", r.status_code, r.json(), 401)

    # buyer2 outbids buyer1
    if lot_id:
        r = client.post("/bids", json={"lot_id": lot_id, "amount": 2200}, headers=buyer2_headers)
        print_result("POST", "/bids (buyer2 outbids buyer1)", r.status_code, r.json(), 200)

    # buyer1 bids on lot2 (no bids = UNSOLD test)
    # intentionally no bids on lot2

    # Get bids for lot
    if lot_id:
        r = client.get(f"/bids?lot_id={lot_id}")
        print_result("GET", "/bids?lot_id={lot_id}", r.status_code, r.json(), 200)

    print("\n=== CLOSE AUCTION ===")

    # Close by non-owner
    if auction_id:
        r = client.post(f"/auctions/{auction_id}/close", headers=buyer_headers)
        print_result("POST", "/auctions/{id}/close (wrong user, should fail)", r.status_code, r.json(), 403)

    # Close by owner
    if auction_id:
        r = client.post(f"/auctions/{auction_id}/close", headers=seller_headers)
        print_result("POST", "/auctions/{id}/close (owner)", r.status_code, r.json(), 200)

    # Close already closed
    if auction_id:
        r = client.post(f"/auctions/{auction_id}/close", headers=seller_headers)
        print_result("POST", "/auctions/{id}/close (already closed, should fail)", r.status_code, r.json(), 400)

    # Check lot statuses after close
    if lot_id:
        r = client.get(f"/lots/{lot_id}")
        body = r.json()
        expected_status_value = "SOLD"
        ok = "✅" if body.get("status") == expected_status_value else "❌"
        print(f"{ok} lot1 status after close → {body.get('status')} (expected SOLD)")

    if lot2_id:
        r = client.get(f"/lots/{lot2_id}")
        body = r.json()
        expected_status_value = "UNSOLD"
        ok = "✅" if body.get("status") == expected_status_value else "❌"
        print(f"{ok} lot2 status after close → {body.get('status')} (expected UNSOLD)")

    print("\n=== PAYMENTS ===")

    r = client.get("/payments", headers=buyer_headers)
    print_result("GET", "/payments (buyer1)", r.status_code, r.json(), 200)
    if r.status_code == 200:
        payments = r.json().get("items", [])
        refunded = [p for p in payments if p["status"] == "REFUNDED"]
        ok = "✅" if len(refunded) >= 1 else "❌"
        print(f"{ok} buyer1 has REFUNDED payment (outbid) → {len(refunded)} found")

    r = client.get("/payments", headers=buyer2_headers)
    print_result("GET", "/payments (buyer2)", r.status_code, r.json(), 200)
    if r.status_code == 200:
        payments = r.json().get("items", [])
        completed = [p for p in payments if p["status"] == "COMPLETED"]
        ok = "✅" if len(completed) >= 1 else "❌"
        print(f"{ok} buyer2 has COMPLETED payment (winner) → {len(completed)} found")

    r = client.get("/payments")
    print_result("GET", "/payments (no auth, should fail)", r.status_code, r.json(), 401)

    print("\n=== DELETE LOT (on new PENDING auction) ===")

    r = client.post("/auctions", json={
        "title": "Auction to test delete",
        "description": "Test.",
        "closes_at": "2027-06-01T00:00:00Z",
    }, headers=seller_headers)
    if r.status_code == 200:
        test_auction_id = r.json()["id"]

        r = client.post("/lots", json={
            "auction_id": test_auction_id,
            "title": "Lot to delete",
            "description": "Will be deleted.",
            "starting_price": 100,
            "min_bid_increment": 10,
        }, headers=seller_headers)
        if r.status_code == 200:
            delete_lot_id = r.json()["id"]

            r = client.delete(f"/lots/{delete_lot_id}", headers=buyer_headers)
            print_result("DELETE", "/lots/{lot_id} (wrong user, should fail)", r.status_code, r.json() if r.content else {}, 403)

            r = client.delete(f"/lots/{delete_lot_id}", headers=seller_headers)
            print_result("DELETE", "/lots/{lot_id} (owner)", r.status_code, r.json() if r.content else {}, 200)

            r = client.delete(f"/lots/{delete_lot_id}", headers=seller_headers)
            print_result("DELETE", "/lots/{lot_id} (already deleted, should fail)", r.status_code, r.json() if r.content else {}, 404)

    print("\n=== LOGOUT ===")

    r = client.post("/auth/logout", headers=buyer_headers)
    print_result("POST", "/auth/logout", r.status_code, r.json(), 200)

    print("\nDone!")
    client.close()


if __name__ == "__main__":
    run()