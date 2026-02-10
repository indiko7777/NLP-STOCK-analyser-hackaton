"""Symbol definitions and watchlists."""

from typing import Dict, List

# Default watchlist
WATCHLIST: List[str] = [
    # US Tech Giants
    "AAPL",
    "MSFT",
    "GOOGL",
    "AMZN",
    "NVDA",
    "TSLA",
    "META",

    # European Stocks (AEX)
    "ASML.AS",
    "SHELL.AS",
    "INGA.AS",

    # Crypto
    "BTC-USD",
    "ETH-USD",
    "SOL-USD",
]

# Symbol mapping for different exchanges
SYMBOL_MAPPING: Dict[str, Dict[str, str]] = {
    # European stocks mapping
    "ASML": {
        "yahoo": "ASML.AS",
        "twelve_data": "ASML:AMS",
        "display": "ASML (AEX)"
    },
    "SHELL": {
        "yahoo": "SHELL.AS",
        "twelve_data": "SHEL:AMS",
        "display": "Shell (AEX)"
    },
    "ING": {
        "yahoo": "INGA.AS",
        "twelve_data": "INGA:AMS",
        "display": "ING Group (AEX)"
    },

    # Crypto mapping
    "BTC": {
        "binance": "BTCUSDT",
        "yahoo": "BTC-USD",
        "display": "Bitcoin"
    },
    "ETH": {
        "binance": "ETHUSDT",
        "yahoo": "ETH-USD",
        "display": "Ethereum"
    },
    "SOL": {
        "binance": "SOLUSDT",
        "yahoo": "SOL-USD",
        "display": "Solana"
    },
}

# Market classifications
MARKET_CLASSIFICATION: Dict[str, str] = {
    # US Stocks
    "AAPL": "US",
    "MSFT": "US",
    "GOOGL": "US",
    "AMZN": "US",
    "NVDA": "US",
    "TSLA": "US",
    "META": "US",

    # European
    "ASML.AS": "EU",
    "SHELL.AS": "EU",
    "INGA.AS": "EU",

    # Crypto
    "BTC-USD": "CRYPTO",
    "ETH-USD": "CRYPTO",
    "SOL-USD": "CRYPTO",
}


def get_display_name(symbol: str) -> str:
    """Get display name for a symbol."""
    base_symbol = symbol.split(".")[0].split("-")[0]
    if base_symbol in SYMBOL_MAPPING:
        return SYMBOL_MAPPING[base_symbol].get("display", symbol)
    return symbol


def get_market_type(symbol: str) -> str:
    """Get market type for a symbol."""
    return MARKET_CLASSIFICATION.get(symbol, "UNKNOWN")
