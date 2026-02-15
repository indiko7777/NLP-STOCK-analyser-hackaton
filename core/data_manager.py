"""Central data orchestration manager."""

import asyncio
from typing import Dict, List, Optional, Any, Callable, Awaitable
from datetime import datetime

import pandas as pd
import structlog

from data_sources import AlpacaProvider, BinanceProvider
from config.symbols import get_market_type

logger = structlog.get_logger()

# Mapping from market type to provider key
_MARKET_PROVIDER_MAP = {
    "US": "alpaca",
    "CRYPTO": "binance",
}


class DataManager:
    """Orchestrates all data providers and manages unified data cache."""

    def __init__(self) -> None:
        self.providers: Dict[str, Any] = {}
        self.price_cache: Dict[str, Dict[str, Any]] = {}
        self.update_callbacks: List[Callable[[Dict[str, Any]], Awaitable[None]]] = []
        self._running = False

    # ── Lifecycle ────────────────────────────────────────────────────────

    async def initialize(self) -> None:
        """Initialize all data providers."""
        logger.info("Initializing DataManager...")

        provider_factories = {
            "alpaca": AlpacaProvider,
            "binance": BinanceProvider,
        }

        for name, factory in provider_factories.items():
            try:
                provider = factory(on_message=self._handle_price_update)
                await provider.connect()
                self.providers[name] = provider
                logger.info(f"{name.capitalize()} provider initialized")
            except Exception as e:
                logger.warning(f"{name.capitalize()} provider failed to initialize: {e}")

        logger.info(f"DataManager initialized with {len(self.providers)} providers")

    async def shutdown(self) -> None:
        """Shutdown all providers."""
        logger.info("Shutting down DataManager...")
        self._running = False

        for name, provider in self.providers.items():
            try:
                await provider.disconnect()
                logger.info(f"Disconnected {name}")
            except Exception as e:
                logger.error(f"Error disconnecting {name}: {e}")

    async def start_streams(self) -> None:
        """Start all WebSocket streams in background."""
        self._running = True
        tasks = [
            asyncio.create_task(provider.run_stream())
            for provider in self.providers.values()
        ]
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    # ── Callbacks ────────────────────────────────────────────────────────

    def register_update_callback(self, callback: Callable[[Dict[str, Any]], Awaitable[None]]) -> None:
        """Register a callback for price updates."""
        self.update_callbacks.append(callback)

    async def _handle_price_update(self, data: Dict[str, Any]) -> None:
        """Handle incoming price update from providers."""
        symbol = data.get("symbol")
        if not symbol:
            return

        self.price_cache[symbol] = data

        for callback in self.update_callbacks:
            try:
                await callback(data)
            except Exception as e:
                logger.error(f"Error in update callback: {e}")

    # ── Subscriptions ────────────────────────────────────────────────────

    def _group_by_provider(self, symbols: List[str]) -> Dict[str, List[str]]:
        """Group symbols by their provider key."""
        groups: Dict[str, List[str]] = {}
        for symbol in symbols:
            provider_key = _MARKET_PROVIDER_MAP.get(get_market_type(symbol))
            if provider_key:
                groups.setdefault(provider_key, []).append(symbol)
        return groups

    async def _dispatch_to_providers(self, symbols: List[str], method: str) -> None:
        """Call *method* ('subscribe' or 'unsubscribe') on the right providers."""
        for provider_key, syms in self._group_by_provider(symbols).items():
            if provider_key in self.providers:
                await getattr(self.providers[provider_key], method)(syms)

    async def subscribe_symbols(self, symbols: List[str]) -> None:
        """Subscribe to real-time data for symbols."""
        logger.info(f"Subscribing to symbols: {symbols}")
        await self._dispatch_to_providers(symbols, "subscribe")

    async def unsubscribe_symbols(self, symbols: List[str]) -> None:
        """Unsubscribe from symbols."""
        logger.info(f"Unsubscribing from symbols: {symbols}")
        await self._dispatch_to_providers(symbols, "unsubscribe")

    # ── Data access ──────────────────────────────────────────────────────

    def _provider_for(self, symbol: str) -> Optional[Any]:
        """Return the provider responsible for *symbol*, or None."""
        provider_key = _MARKET_PROVIDER_MAP.get(get_market_type(symbol))
        return self.providers.get(provider_key) if provider_key else None

    async def get_latest_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get latest price for a symbol."""
        if symbol in self.price_cache:
            return self.price_cache[symbol]

        provider = self._provider_for(symbol)
        return await provider.get_latest_price(symbol) if provider else None

    async def get_historical_data(
        self,
        symbol: str,
        timeframe: str,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        limit: int = 100,
    ) -> Optional[pd.DataFrame]:
        """Get historical OHLCV data for a symbol."""
        provider = self._provider_for(symbol)
        if provider is None:
            return None
        return await provider.get_historical_data(symbol, timeframe, start, end, limit)

    def get_all_prices(self) -> Dict[str, Dict[str, Any]]:
        """Get all cached prices."""
        return self.price_cache

    def get_provider_status(self) -> Dict[str, bool]:
        """Get connection status of all providers."""
        return {name: provider.is_connected for name, provider in self.providers.items()}
