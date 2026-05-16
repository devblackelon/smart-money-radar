# ============================================================
#  SMART MONEY RADAR — Wallet Intelligence Engine
#
#  This is the brain of the project.
#  It figures out WHICH wallets are "smart money" by looking
#  at who bought trending tokens before they blew up.
# ============================================================

import time
import json
from collections import defaultdict
from birdeye import get_trending_tokens, get_token_transactions
from config import TRENDING_LIMIT, SMART_MONEY_MIN_HITS

# This dictionary stores every wallet we've seen and their stats
# Format: { "wallet_address": { "hits": 2, "tokens": [...] } }
wallet_stats = defaultdict(lambda: {"hits": 0, "tokens": []})

# The final list of confirmed smart money wallets
smart_money_wallets = set()


def build_smart_money_list():
    """
    Main function — called once at startup.
    
    Steps:
    1. Get the top trending tokens right now
    2. For each trending token, look at who bought it early
       (first 20 buyers = early buyers)
    3. Any wallet that appears as an early buyer across
       MULTIPLE trending tokens = smart money
    """
    print("\n🔍 Building Smart Money wallet list from trending tokens...")
    print("=" * 55)

    trending_data = get_trending_tokens(TRENDING_LIMIT)
    if not trending_data or "data" not in trending_data:
        print("❌ Could not fetch trending tokens.")
        return

    tokens = trending_data["data"].get("tokens", [])
    print(f"✅ Found {len(tokens)} trending tokens to analyze\n")

    for i, token in enumerate(tokens):
        address = token.get("address")
        symbol = token.get("symbol", "???")
        print(f"  [{i+1}/{len(tokens)}] Analyzing early buyers of ${symbol}...")

        txs_data = get_token_transactions(address, limit=30)
        if not txs_data or "data" not in txs_data:
            continue

        transactions = txs_data["data"].get("items", [])
        
        # The first 10 buyers = "early buyers"
        early_buyers = transactions[:10]

        for tx in early_buyers:
            wallet = tx.get("owner") or tx.get("source")
            if wallet:
                wallet_stats[wallet]["hits"] += 1
                wallet_stats[wallet]["tokens"].append(symbol)

        time.sleep(3)  # small pause to be respectful to the API

    # Now filter: only keep wallets with hits >= threshold
    for wallet, stats in wallet_stats.items():
        if stats["hits"] >= SMART_MONEY_MIN_HITS:
            smart_money_wallets.add(wallet)

    print(f"\n🧠 Smart Money wallets identified: {len(smart_money_wallets)}")
    for wallet in list(smart_money_wallets)[:5]:
        hits = wallet_stats[wallet]["hits"]
        tokens = ", ".join(wallet_stats[wallet]["tokens"])
        print(f"  💼 {wallet[:8]}...{wallet[-4:]} → {hits} early hits ({tokens})")

        # Save wallet stats to disk so dashboard can read them
    with open("wallet_stats.json", "w") as f:
        json.dump(dict(wallet_stats), f)

    # Save wallet stats so the dashboard can read them
    #import json
    with open("wallet_stats.json", "w") as f:
        json.dump(dict(wallet_stats), f, indent=2)
    print(f"  💾 Wallet stats saved to wallet_stats.json")

    return smart_money_wallets


def is_smart_money_buying(token_address):
    """
    Checks if any smart money wallet has bought this token.
    Returns list of smart money wallets found in the buyer list.
    """
    if not smart_money_wallets:
        return []

    txs_data = get_token_transactions(token_address, limit=50)
    if not txs_data or "data" not in txs_data:
        return []

    transactions = txs_data["data"].get("items", [])
    buyers = set()
    for tx in transactions:
        wallet = tx.get("owner") or tx.get("source")
        if wallet:
            buyers.add(wallet)

    # Find overlap between buyers and our smart money list
    smart_buyers = buyers.intersection(smart_money_wallets)
    return list(smart_buyers)


def get_wallet_hit_count(wallet):
    """Returns how many trending tokens this wallet bought early."""
    return wallet_stats.get(wallet, {}).get("hits", 0)