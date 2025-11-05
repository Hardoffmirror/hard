"""
Configuration file for PoE Currency Exchange Helper
"""

# API Configuration
POE_TRADE_API = "https://www.pathofexile.com/api/trade/exchange"
POE_NINJA_API = "https://poe.ninja/api/data/currencyoverview"
REQUEST_TIMEOUT = 10
UPDATE_INTERVAL = 60  # seconds

# Database Configuration
DB_NAME = "poe_currency_history.db"

# UI Configuration
OVERLAY_OPACITY = 0.9
OVERLAY_WIDTH = 400
OVERLAY_HEIGHT = 600
OVERLAY_X = 10
OVERLAY_Y = 10

# Currency Types
CURRENCIES = [
    "chaos", "divine", "exalted", "mirror",
    "orb-of-alteration", "orb-of-alchemy", "orb-of-fusing",
    "orb-of-scouring", "chromatic-orb", "jewellers-orb",
    "vaal-orb", "regal-orb", "blessed-orb", "gemcutters-prism",
    "cartographers-chisel", "orb-of-regret", "orb-of-annulment"
]

# League (update this to current league)
CURRENT_LEAGUE = "Standard"

# Profit calculation threshold (minimum profit percentage to show)
MIN_PROFIT_PERCENTAGE = 5.0

# History settings
MAX_HISTORY_DAYS = 30
