# ============================================================
#  SMART MONEY RADAR — Main Monitor
#
#  This is the engine that:
#  1. Scans new token listings every minute
#  2. Scores each token across 4 signals
#  3. Flags high-score tokens as "ALPHA"
#  4. Saves results to a JSON file the dashboard reads
# ============================================================

import time
import json
import os
from datetime import datetime
import birdeye
from birdeye import get_trending_tokens, get_token_security, get_token_overview, get_new_listings, call_count
from telegram_bot import send_alert, send_startup_message

from birdeye import (
    get_new_listings,
    get_token_security,
    get_token_overview,
    call_count
)
from smart_money import build_smart_money_list, is_smart_money_buying, get_wallet_hit_count
from config import SCAN_INTERVAL, ALERT_THRESHOLD, NEW_LISTING_LIMIT

# Tokens we've already seen (so we don't re-score them)
seen_tokens = set()

# All scored tokens — written to file so dashboard can read them
all_results = []

RESULTS_FILE = "results.json"


def score_token(address, symbol, smart_buyers):
    """
    Scores a token out of 100 based on 4 signals:
    
    1. Smart Money Signal (40 pts)  — most important
       Are known winning wallets buying this?
    
    2. Security Score (30 pts)
       Is the token safe? No rug pull red flags?
    
    3. Momentum Score (20 pts)
       Is price and volume moving upward?
    
    4. Holder Score (10 pts)
       Are holders distributed? Not whale-concentrated?
    """
    score = 0
    breakdown = {}

    # ── 1. Smart Money Signal ─────────────────────────────
    if smart_buyers:
        sm_score = min(40, len(smart_buyers) * 20)
        # Bonus points if wallets have high hit counts
        for wallet in smart_buyers:
            hits = get_wallet_hit_count(wallet)
            sm_score = min(40, sm_score + hits * 2)
        score += sm_score
        breakdown["smart_money"] = sm_score
    else:
        breakdown["smart_money"] = 0

    # ── 2. Security Score ─────────────────────────────────
    security_data = None  # token_security requires paid plan
    if security_data and "data" in security_data:
        sec = security_data["data"]
        sec_score = 30  # start at full marks, subtract for red flags

        if sec.get("freezeAuthority"):    sec_score -= 10  # can freeze wallets
        if sec.get("mintAuthority"):      sec_score -= 10  # can mint more tokens
        if sec.get("jupiterStrictList") == False: sec_score -= 5
        if sec.get("top10HolderPercent", 0) > 80: sec_score -= 5

        sec_score = max(0, sec_score)
        score += sec_score
        breakdown["security"] = sec_score
    else:
        breakdown["security"] = 15  # neutral if we can't get data

    # ── 3. Momentum Score ─────────────────────────────────
    overview = get_token_overview(address)
    if overview and "data" in overview:
        ov = overview["data"]
        mom_score = 0

        price_change = ov.get("priceChange24hPercent", 0) or 0
        volume_24h   = ov.get("v24hUSD", 0) or 0

        if price_change > 50:  mom_score += 10
        elif price_change > 20: mom_score += 6
        elif price_change > 0:  mom_score += 3

        if volume_24h > 100_000:  mom_score += 10
        elif volume_24h > 10_000: mom_score += 6
        elif volume_24h > 1_000:  mom_score += 3

        score += mom_score
        breakdown["momentum"] = mom_score

        price       = ov.get("price", 0)
        market_cap  = ov.get("mc", 0)
        liquidity   = ov.get("liquidity", 0)
        holders     = ov.get("holder", 0)
    else:
        breakdown["momentum"] = 0
        price = market_cap = liquidity = holders = 0

    # ── 4. Holder Distribution Score ─────────────────────
    # We get this from security data above
    if security_data and "data" in security_data:
        top10 = security_data["data"].get("top10HolderPercent", 100) or 100
        if top10 < 30:   holder_score = 10
        elif top10 < 50: holder_score = 7
        elif top10 < 70: holder_score = 4
        else:            holder_score = 1
        score += holder_score
        breakdown["holder_distribution"] = holder_score
    else:
        breakdown["holder_distribution"] = 5

    return {
        "score": min(100, score),
        "breakdown": breakdown,
        "price": price,
        "market_cap": market_cap,
        "liquidity": liquidity,
        "holders": holders,
        "smart_buyers": [w[:8] + "..." + w[-4:] for w in smart_buyers]
    }


def save_results():
    """Writes all results to a JSON file so the dashboard can display them."""
    with open(RESULTS_FILE, "w") as f:
        json.dump({
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "next_scan_at": (datetime.now().timestamp() + SCAN_INTERVAL),
            "total_api_calls": birdeye.call_count,
            "tokens_scanned": len(seen_tokens),
            "alpha_signals": [r for r in all_results if r["score"] >= ALERT_THRESHOLD],
            "all_tokens": all_results[-50:]  # keep last 50
        }, f, indent=2)


def scan_new_listings():
    print(f"\n{'='*55}")
    print(f"🔄 Scanning trending tokens... [{datetime.now().strftime('%H:%M:%S')}]")

    listings_data = get_trending_tokens(NEW_LISTING_LIMIT)
    if not listings_data or "data" not in listings_data:
        print("  ⚠️  Could not fetch trending tokens")
        return

    tokens = listings_data["data"].get("tokens", [])
    new_tokens = [t for t in tokens if t.get("address") not in seen_tokens]
    print(f"  📋 {len(new_tokens)} tokens to score")

    for token in new_tokens:
        address = token.get("address")
        symbol  = token.get("symbol", "???")
        name    = token.get("name", "Unknown")

        if not address:
            continue

        seen_tokens.add(address)
        print(f"\n  🪙 Scoring ${symbol} ({name[:20]})...")

        smart_buyers = is_smart_money_buying(address)
        if smart_buyers:
            print(f"    🧠 SMART MONEY DETECTED! {len(smart_buyers)} wallet(s)")

        result = score_token(address, symbol, smart_buyers)
        result.update({
            "address": address,
            "symbol": symbol,
            "name": name,
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "date": datetime.now().strftime("%Y-%m-%d")
        })

        all_results.append(result)

        score = result["score"]
        label = "🚨 ALPHA" if score >= ALERT_THRESHOLD else ("👀 Watch" if score >= 40 else "⬜ Low")
        print(f"    {label} Score: {score}/100 | SM:{result['breakdown']['smart_money']} "
              f"SEC:{result['breakdown']['security']} MOM:{result['breakdown']['momentum']}")

        if score >= ALERT_THRESHOLD:
            print(f"\n    🚨 HIGH SCORE ALERT: ${symbol} — Score: {score}/100\n")
            send_alert(symbol, name, score,       
                result["breakdown"], result["smart_buyers"],
                result["price"], result["liquidity"], address)

        time.sleep(1.5)

    # Clear seen tokens periodically so trending list refreshes
    if len(seen_tokens) > 50:
        seen_tokens.clear()

    save_results()
    print(f"\n  💾 Results saved. Total API calls: {birdeye.call_count}")


def run():
    """Entry point — runs the full radar."""
    print("""
╔══════════════════════════════════════════╗
║       🦅 SMART MONEY RADAR v1.0          ║
║       Built with Birdeye Data API        ║
╚══════════════════════════════════════════╝
    """)

    # Phase 1: Build our smart money wallet database
    build_smart_money_list()
    send_startup_message(len(smart_money_wallets))

    # Phase 2: Continuous monitoring loop
    print(f"\n\n🚀 Starting live monitoring (every {SCAN_INTERVAL}s)...")
    print("   Press Ctrl+C to stop\n")

    try:
        while True:
            scan_new_listings()
            print(f"\n⏳ Next scan in {SCAN_INTERVAL} seconds...")
            time.sleep(SCAN_INTERVAL)
    except KeyboardInterrupt:
        print("\n\n👋 Radar stopped.")
        print(f"📊 Total API calls made: {call_count}")
        print(f"🪙 Total tokens scanned: {len(seen_tokens)}")
        save_results()


if __name__ == "__main__":
    run()