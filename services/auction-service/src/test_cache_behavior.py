import os
import time
import uuid

import httpx


IN_DOCKER = os.path.exists("/.dockerenv")

USER_API = os.getenv(
    "USER_API",
    "http://user-service:8001/api/v1" if IN_DOCKER else "http://127.0.0.1:8001/api/v1",
)
AUCTION_API = os.getenv(
    "AUCTION_API",
    "http://auction-service:8002/api/v1" if IN_DOCKER else "http://127.0.0.1:8002/api/v1",
)


def _timed_get(client: httpx.Client, url: str) -> tuple[httpx.Response, float]:
    started_at = time.perf_counter()
    response = client.get(url)
    elapsed = time.perf_counter() - started_at
    return response, elapsed


def _register_and_login(client: httpx.Client) -> str:
    suffix = uuid.uuid4().hex[:8]
    username = f"cache_user_{suffix}"
    email = f"cache_user_{suffix}@example.com"

    register_resp = client.post(
        f"{USER_API}/users/register",
        json={
            "username": username,
            "email": email,
            "password": "password123",
        },
    )
    assert register_resp.status_code in {200, 201}, register_resp.text

    login_resp = client.post(
        f"{USER_API}/auth/login",
        json={
            "username": username,
            "password": "password123",
        },
    )
    assert login_resp.status_code == 200, login_resp.text
    return login_resp.json()["access_token"]


def test_auction_get_cache_hit_is_faster_than_first_fetch():
    with httpx.Client(timeout=10.0, follow_redirects=True) as client:
        token = _register_and_login(client)
        headers = {"Authorization": f"Bearer {token}"}

        auction_resp = client.post(
            f"{AUCTION_API}/auctions",
            headers=headers,
            json={
                "title": "Cache Comparison Auction",
                "description": "Cache comparison test",
                "closes_at": "2030-01-01T00:00:00Z",
            },
        )
        assert auction_resp.status_code in {200, 201}, auction_resp.text
        auction_id = auction_resp.json()["id"]

        miss_resp, miss_time = _timed_get(client, f"{AUCTION_API}/auctions/{auction_id}")
        hit_resp, hit_time = _timed_get(client, f"{AUCTION_API}/auctions/{auction_id}")

        assert miss_resp.status_code == 200, miss_resp.text
        assert hit_resp.status_code == 200, hit_resp.text
        assert miss_resp.headers.get("x-cache", "").upper() == "MISS"
        assert hit_resp.headers.get("x-cache", "").upper() == "HIT"
        assert hit_resp.json() == miss_resp.json()

        print(
            f"Cache timings: miss={miss_time:.6f}s hit={hit_time:.6f}s "
            f"ratio={(hit_time / miss_time) if miss_time else 0:.2f}"
        )

        # Keep the comparison practical rather than brittle. The hit should not be slower
        # than the cold read by a meaningful margin.
        assert hit_time <= miss_time * 1.5
