"""Streamlit session state management."""

import streamlit as st
from datetime import datetime
from typing import Any, Dict, List, Optional
import pandas as pd


class StateManager:
    """Manages Streamlit session state with type-safe accessors."""

    def __init__(self):
        """Initialize state manager."""
        self._initialize_state()

    def _initialize_state(self):
        """Initialize session state with default values."""
        defaults = {
            # Connection state
            "ws_connected": False,
            "last_update": None,
            "connection_errors": [],

            # Market data (real-time cache)
            "prices": {},

            # Historical data cache
            "ohlcv_cache": {},

            # Technical indicators cache
            "indicators": {},

            # Portfolio state
            "portfolio": {
                "positions": [],
                "total_value": 0.0,
                "daily_pnl": 0.0,
            },

            # LLM chat state
            "chat_history": [],
            "current_research": None,

            # UI state
            "selected_symbol": "AAPL",
            "active_page": "dashboard",
            "watchlist": ["AAPL", "MSFT", "BTC-USD"],
            "selected_timeframe": "1D",

            # Settings
            "auto_refresh": True,
            "refresh_interval": 5,
        }

        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value

    # Connection state
    @property
    def ws_connected(self) -> bool:
        """Get WebSocket connection status."""
        return st.session_state.get("ws_connected", False)

    @ws_connected.setter
    def ws_connected(self, value: bool):
        """Set WebSocket connection status."""
        st.session_state["ws_connected"] = value
        st.session_state["last_update"] = datetime.now()

    # Market data
    def get_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get current price data for a symbol."""
        return st.session_state["prices"].get(symbol)

    def update_price(self, symbol: str, data: Dict[str, Any]):
        """Update price data for a symbol."""
        st.session_state["prices"][symbol] = data
        st.session_state["last_update"] = datetime.now()

    def get_all_prices(self) -> Dict[str, Dict[str, Any]]:
        """Get all price data."""
        return st.session_state["prices"]

    # Historical data
    def get_ohlcv(self, symbol: str, timeframe: str) -> Optional[pd.DataFrame]:
        """Get cached OHLCV data."""
        key = f"{symbol}_{timeframe}"
        return st.session_state["ohlcv_cache"].get(key)

    def cache_ohlcv(self, symbol: str, timeframe: str, data: pd.DataFrame):
        """Cache OHLCV data."""
        key = f"{symbol}_{timeframe}"
        st.session_state["ohlcv_cache"][key] = data

    # Technical indicators
    def get_indicators(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get cached technical indicators."""
        return st.session_state["indicators"].get(symbol)

    def cache_indicators(self, symbol: str, indicators: Dict[str, Any]):
        """Cache technical indicators."""
        st.session_state["indicators"][symbol] = indicators

    # Portfolio
    @property
    def portfolio(self) -> Dict[str, Any]:
        """Get portfolio data."""
        return st.session_state["portfolio"]

    def update_portfolio(self, positions: List[Dict], total_value: float, daily_pnl: float):
        """Update portfolio data."""
        st.session_state["portfolio"] = {
            "positions": positions,
            "total_value": total_value,
            "daily_pnl": daily_pnl,
        }

    # Chat state
    def add_chat_message(self, role: str, content: str):
        """Add a message to chat history."""
        st.session_state["chat_history"].append({
            "role": role,
            "content": content,
            "timestamp": datetime.now(),
        })

    def get_chat_history(self) -> List[Dict[str, Any]]:
        """Get chat history."""
        return st.session_state["chat_history"]

    def clear_chat_history(self):
        """Clear chat history."""
        st.session_state["chat_history"] = []

    # UI state
    @property
    def selected_symbol(self) -> str:
        """Get selected symbol."""
        return st.session_state.get("selected_symbol", "AAPL")

    @selected_symbol.setter
    def selected_symbol(self, value: str):
        """Set selected symbol."""
        st.session_state["selected_symbol"] = value

    @property
    def watchlist(self) -> List[str]:
        """Get watchlist."""
        return st.session_state.get("watchlist", [])

    def add_to_watchlist(self, symbol: str):
        """Add symbol to watchlist."""
        if symbol not in st.session_state["watchlist"]:
            st.session_state["watchlist"].append(symbol)

    def remove_from_watchlist(self, symbol: str):
        """Remove symbol from watchlist."""
        if symbol in st.session_state["watchlist"]:
            st.session_state["watchlist"].remove(symbol)

    @property
    def selected_timeframe(self) -> str:
        """Get selected timeframe."""
        return st.session_state.get("selected_timeframe", "1D")

    @selected_timeframe.setter
    def selected_timeframe(self, value: str):
        """Set selected timeframe."""
        st.session_state["selected_timeframe"] = value

    # Error handling
    def add_error(self, error: str):
        """Add connection error."""
        st.session_state["connection_errors"].append({
            "error": error,
            "timestamp": datetime.now(),
        })

    def clear_errors(self):
        """Clear connection errors."""
        st.session_state["connection_errors"] = []

    def get_errors(self) -> List[Dict[str, Any]]:
        """Get connection errors."""
        return st.session_state["connection_errors"]
