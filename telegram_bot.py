# ============================================================
#  SMART MONEY RADAR — Telegram Alert Bot
#  Sends a message to your Telegram when an alpha token
#  is detected by the radar.
# ============================================================

import requests

# ── Fill these in ──────────────────────────────────────────
TELEGRAM_TOKEN   = "8915653740:AAGGVZvj3gdRTDaUcdHU50vAyNyMZgRWIzo"
TELEGRAM_CHAT_ID = "2069857650"              
# ──────────────────────────────────────────────────────────

ENABLED = TELEGRAM_TOKEN != "YOUR_TELEGRAM_BOT_TOKEN_HERE"


def send_alert(token_symbol, token_name, score, breakdown, smart_buyers, price, liquidity, address):
    """
    Sends a formatted Telegram message when an alpha token is found.
    Called from radar.py whenever a token scores >= ALERT_THRESHOLD.
    """
    if not ENABLED:
        print("  ℹ️  Telegram not configured — skipping alert")
        return

    sm_wallets = "\n".join([f"  🧠 `{w}`" for w in smart_buyers[:3]])
    if not sm_wallets:
        sm_wallets = "  None detected"

    message = f"""
message = (
        f"🚨 SMART MONEY RADAR ALERT\n\n"
        f"🪙 ${token_symbol} — {token_name}\n"
        f"📊 Score: {score}/100\n\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🧠 Smart Money:  {breakdown['smart_money']}/40\n"
        f"🛡️ Safety:       {breakdown['security']}/30\n"
        f"⚡ Momentum:     {breakdown['momentum']}/20\n"
        f"👥 Holders:      {breakdown['holder_distribution']}/10\n"
        f"━━━━━━━━━━━━━━━━━━\n\n"
        f"💰 Price: ${price:.8f}\n"
        f"💧 Liquidity: ${liquidity:,.0f}\n\n"
        f"🧠 Smart Money Wallets:\n"
        f"{chr(10).join(['  ' + w for w in smart_buyers[:3]])}\n\n"
        f"🔗 https://birdeye.so/token/{address}?chain=solana\n\n"
        f"Powered by Birdeye Data #BirdeyeAPI"
    )
    """.strip()

    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        resp = requests.post(url, json={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "disable_web_page_preview": True
        }, timeout=10)

        if resp.status_code == 200:
            print(f"  📱 Telegram alert sent for ${token_symbol}!")
        else:
            print(f"  ⚠️  Telegram error: {resp.text[:100]}")
    except Exception as e:
        print(f"  ❌ Telegram failed: {e}")


def send_startup_message(wallet_count):
    if not ENABLED:
        return

    message = (
        f"🦅 Smart Money Radar Started\n\n"
        f"✅ Radar is now live on Solana\n"
        f"🧠 Smart money wallets tracked: {wallet_count}\n"
        f"📡 Monitoring new tokens every 3 minutes\n\n"
        f"You will get alerts here when smart money buys a new token.\n\n"
        f"Powered by Birdeye Data #BirdeyeAPI"
    )

    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        resp = requests.post(url, json={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message
        }, timeout=10)

        if resp.status_code == 200:
            print(f"  📱 Telegram startup message sent!")
        else:
            print(f"  ⚠️  Telegram error: {resp.text}")
    except Exception as e:
        print(f"  ❌ Telegram failed: {e}")