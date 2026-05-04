import httpx
import asyncio
import os
import uuid
from decimal import Decimal

IN_DOCKER = os.path.exists("/.dockerenv")

USER_API = os.getenv(
    "USER_API",
    "http://user-service:8001/api/v1" if IN_DOCKER else "http://127.0.0.1:8001/api/v1",
)
AUCTION_API = os.getenv(
    "AUCTION_API",
    "http://auction-service:8002/api/v1" if IN_DOCKER else "http://127.0.0.1:8002/api/v1",
)
BIDDING_API = os.getenv(
    "BIDDING_API",
    "http://bidding-service:8003/api/v1" if IN_DOCKER else "http://127.0.0.1:8003/api/v1",
)

async def run_test_logic():
    async with httpx.AsyncClient(timeout=10.0) as client:
        print("1. Registering Users...")
        # Alice (Seller), Bob (Buyer 1), Charlie (Buyer 2)
        users = ["alice", "bob", "charlie"]
        tokens = {}
        user_ids = {}
        for u in users:
            reg_resp = await client.post(f"{USER_API}/users/register", json={
                "username": f"{u}_{uuid.uuid4().hex[:4]}",
                "email": f"{u}_{uuid.uuid4().hex[:4]}@example.com",
                "password": "password123"
            })
            assert reg_resp.status_code in {200, 201}, reg_resp.text
            data = reg_resp.json()
            username = data["username"]
            user_ids[u] = data["id"]
            
            login_resp = await client.post(f"{USER_API}/auth/login", json={
                "username": username,
                "password": "password123"
            })
            assert login_resp.status_code == 200, login_resp.text
            tokens[u] = login_resp.json()["access_token"]

        # 2. Top up
        print("2. Topping up balances...")
        for u in ["alice", "bob", "charlie"]:
            top_up_resp = await client.post(
                f"{USER_API}/users/me/top-up",
                headers={"Authorization": f"Bearer {tokens[u]}"},
                json={"amount": "1000.00"},
            )
            assert top_up_resp.status_code == 200, top_up_resp.text

        # 3. Create Auction and Lot
        print("3. Creating Auction and Lot...")
        auction_resp = await client.post(
            f"{AUCTION_API}/auctions",
            headers={"Authorization": f"Bearer {tokens['alice']}"},
            json={
                "title": "Internal Logic Test",
                "description": "Verification",
                "closes_at": "2030-01-01T00:00:00Z"
            },
        )
        assert auction_resp.status_code in {200, 201}, auction_resp.text
        auction_id = auction_resp.json()["id"]

        lot_resp = await client.post(
            f"{AUCTION_API}/lots",
            headers={"Authorization": f"Bearer {tokens['alice']}"},
            json={
                "auction_id": auction_id,
                "title": "Logic Lot",
                "description": "Testing price/refund",
                "starting_price": "100.00",
                "min_bid_increment": "10.00"
            },
        )
        assert lot_resp.status_code in {200, 201}, lot_resp.text
        lot_id = lot_resp.json()["id"]

        # 4. Open Auction
        print("4. Opening Auction...")
        open_resp = await client.post(
            f"{AUCTION_API}/auctions/{auction_id}/open",
            headers={"Authorization": f"Bearer {tokens['alice']}"},
        )
        assert open_resp.status_code == 200, open_resp.text

        # 5. TEST 1: Bob bids $150
        print("5. TEST 1: Bob bids $150...")
        bid_resp = await client.post(
            f"{BIDDING_API}/bids",
            headers={"Authorization": f"Bearer {tokens['bob']}"},
            json={"lot_id": lot_id, "amount": "150.00"},
        )
        assert bid_resp.status_code in {200, 201}, bid_resp.text

        lot_info = (await client.get(f"{AUCTION_API}/lots/{lot_id}")).json()
        print(f"Lot Current Price: {lot_info['current_price']} (Expected: 150.00)")
        assert lot_info["current_price"] == "150.00"
        
        bob_info = (await client.get(f"{USER_API}/users/me", headers={"Authorization": f"Bearer {tokens['bob']}"})).json()
        print(f"Bob Locked Balance: {bob_info['locked_balance']} (Expected: 150.00)")
        assert bob_info["locked_balance"] == "150.00"

        # 6. TEST 2: Charlie bids $200 (Bob should be refunded IMMEDIATELY)
        print("6. TEST 2: Charlie bids $200...")
        bid_resp = await client.post(
            f"{BIDDING_API}/bids",
            headers={"Authorization": f"Bearer {tokens['charlie']}"},
            json={"lot_id": lot_id, "amount": "200.00"},
        )
        assert bid_resp.status_code in {200, 201}, bid_resp.text
        
        lot_info = (await client.get(f"{AUCTION_API}/lots/{lot_id}")).json()
        print(f"Lot Current Price: {lot_info['current_price']} (Expected: 200.00)")
        assert lot_info["current_price"] == "200.00"
        
        bob_info = (await client.get(f"{USER_API}/users/me", headers={"Authorization": f"Bearer {tokens['bob']}"})).json()
        print(f"Bob Locked Balance: {bob_info['locked_balance']} (Expected: 0.00 - REFUNDED)")
        assert bob_info["locked_balance"] == "0.00"
        
        charlie_info = (await client.get(f"{USER_API}/users/me", headers={"Authorization": f"Bearer {tokens['charlie']}"})).json()
        print(f"Charlie Locked Balance: {charlie_info['locked_balance']} (Expected: 200.00)")
        assert charlie_info["locked_balance"] == "200.00"

        # 7. Settlement
        print("7. Closing Auction & Final Settlement...")
        close_resp = await client.post(
            f"{AUCTION_API}/auctions/{auction_id}/close",
            headers={"Authorization": f"Bearer {tokens['alice']}"},
        )
        assert close_resp.status_code == 200, close_resp.text
        
        await asyncio.sleep(2) # wait for async settle

        lot_info = (await client.get(f"{AUCTION_API}/lots/{lot_id}")).json()
        print(f"Lot Status: {lot_info['status']} (Expected: SOLD)")
        assert lot_info["status"] == "SOLD"
        
        alice_final = (await client.get(f"{USER_API}/users/me", headers={"Authorization": f"Bearer {tokens['alice']}"})).json()
        print(f"Alice (Seller) Final Balance: {alice_final['balance']} (Expected: 1200.00)")
        assert alice_final["balance"] == "1200.00"
        
        charlie_final = (await client.get(f"{USER_API}/users/me", headers={"Authorization": f"Bearer {tokens['charlie']}"})).json()
        print(f"Charlie (Winner) Final Balance: {charlie_final['balance']} (Expected: 800.00)")
        print(f"Charlie Final Locked: {charlie_final['locked_balance']} (Expected: 0.00)")
        assert charlie_final["balance"] == "800.00"
        assert charlie_final["locked_balance"] == "0.00"

        print("\nALL LOGIC TESTS PASSED!")

def test_logic():
    asyncio.run(run_test_logic())


if __name__ == "__main__":
    asyncio.run(run_test_logic())
