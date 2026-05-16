# ============================================================
#  SMART MONEY RADAR — Birdeye API Wrapper
#  Every function here = one API call to Birdeye
# ============================================================

import requests
import time
from config import API_KEY, BASE_URL

# This header goes with every request so Birdeye knows it's you
HEADERS = {
    "X-API-KEY": API_KEY,
    "accept": "application/json",
    "x-chain": "solana"
}

call_count = 0  # tracks total API calls made (for the submission proof)


def _get(endpoint, params=None):
    """Internal helper — makes a GET request and returns JSON data."""
    global call_count
    url = f"{BASE_URL}{endpoint}"
    try:
        response = requests.get(url, headers=HEADERS, params=params, timeout=10)
        call_count += 1
        print(f"  [API Call #{call_count}] {endpoint} → {response.status_code}")
        if response.status_code == 200:
            if not response.text.strip():
                print(f"  ⚠️  Empty response body")
                return None
            data = response.json()
            if "list" in endpoint or "tokenlist" in endpoint:
                print(f"  DEBUG top keys: {list(data.keys())}")
                if "data" in data:
                    print(f"  DEBUG data keys: {list(data['data'].keys())}")
            return data
        else:
            print(f"  ⚠️  Error {response.status_code}: {response.text[:200]}")
            return None
    except Exception as e:
        print(f"  ❌ Request failed: {e}")
        print(f"  Raw response: {response.text[:300]}")
        return None


def get_trending_tokens(limit=20):
    """
    Fetches currently trending tokens on Solana.
    Used to identify which tokens are hot — so we can find
    which wallets bought them early.
    """
    return _get("/defi/token_trending", params={
        "sort_by": "rank",
        "sort_type": "asc",
        "offset": 0,
        "limit": limit
    })


def get_token_transactions(address, limit=50):
    """
    Fetches the most recent BUY transactions for a token.
    We use this to find who bought a token early.
    """
    return _get("/defi/txs/token", params={
        "address": address,
        "tx_type": "swap",
        "limit": limit,
        "sort_type": "asc"   # oldest first → gives us the earliest buyers
    })


def get_new_listings(limit=20):
    """
    Fetches newly launched tokens.
    This is what the radar watches — we check if smart money
    wallets are buying into these new tokens.
    """
    return _get("/defi/tokenlist", params={
        "sort_by": "v24hUSD",
        "sort_type": "desc",
        "offset": 0,
        "limit": limit,
        "min_liquidity": 1000
    })


def get_token_security(address):
    """
    Returns a security/risk report for a token.
    Used to filter out obvious scams and rug pulls.
    """
    return _get("/defi/token_security", params={"address": address})


def get_token_overview(address):
    """
    Returns price, volume, market cap, holder count, etc.
    Used to calculate momentum score.
    """
    return _get("/defi/token_overview", params={"address": address})


def get_wallet_portfolio(wallet_address):
    """
    Returns what tokens a wallet currently holds.
    Used to verify smart money wallets are still active.
    """
    return _get("/v1/wallet/token_list", params={
        "wallet": wallet_address
    })
