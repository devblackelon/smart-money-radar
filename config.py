# ============================================================
#  SMART_MONEY_RADAR — Configuration
#  Paste your Birdeye API key below
# ============================================================

API_KEY = "8f8041d4f9814b958ea00c9a4e41678f"   # <-- replace this

BASE_URL = "https://public-api.birdeye.so"

# How many trending tokens to analyze for smart money wallets
TRENDING_LIMIT = 20

# How many new listings to scan per check
NEW_LISTING_LIMIT = 20

# Minimum score for a token to trigger an alert (0–100)
ALERT_THRESHOLD = 60

# How often the radar checks for new tokens (in seconds)
SCAN_INTERVAL = 180

# Minimum times a wallet must have bought early across trending tokens
# to be considered "smart money"
SMART_MONEY_MIN_HITS = 2