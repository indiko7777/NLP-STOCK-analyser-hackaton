"""Central data orchestration manager."""

import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
import pandas as pd
import structlog

from data_sources import AlpacaProvider, BinanceProvider
from config.symbols import get_market_type

logger = structlog.get_logger()


class DataManager:
    """Orchestrates all data providers and manages unified data cache."""

    def __init__(self):
        """Initialize data manager."""
        self.providers: Dict[str, Any] = {}
        self.price_cache: Dict[str, Dict[str, Any]] = {}
        self.update_callbacks: List = []
        self._running = False

    async def initialize(self):
        """Initialize all data providers."""
        logger.info("Initializing DataManager...")

        try:
            # Initialize Alpaca for US stocks
            try:
                alpaca = AlpacaProvider(on_message=self._handle_price_update)
                await alpaca.connect()
                self.providers["alpaca"] = alpaca
                logger.info("Alpaca provider initialized")
            except Exception as e:
                logger.warning(f"Alpaca provider failed to initialize: {e}")

            # Initialize Binance for crypto
            try:
                binance = BinanceProvider(on_message=self._handle_price_update)
                await binance.connect()
                self.providers["binance"] = binance
                logger.info("Binance provider initialized")
            except Exception as e:
                logger.warning(f"Binance provider failed to initialize: {e}")

            logger.info(f"DataManager initialized with {len(self.providers)} providers")

        except Exception as e:
            logger.error(f"Failed to initialize DataManager: {e}")

    async def shutdown(self):
        """Shutdown all providers."""
        logger.info("Shutting down DataManager...")
        self._running = False

        for name, provider in self.providers.items():
            try:
                await provider.disconnect()
                logger.info(f"Disconnected {name}")
            except Exception as e:
                logger.error(f"Error disconnecting {name}: {e}")

    def register_update_callback(self, callback):
        """Register a callback for price updates."""
        self.update_callbacks.append(callback)

    async def _handle_price_update(self, data: Dict[str, Any]):
        """Handle incoming price update from providers."""
        symbol = data.get("symbol")
        if symbol:
            self.price_cache[symbol] = data

            # Notify callbacks
            for callback in self.update_callbacks:
                try:
                    await callback(data)
                except Exception as e:
                    logger.error(f"Error in update callback: {e}")

    async def subscribe_symbols(self, symbols: List[str]):
        """Subscribe to real-time data for symbols."""
        logger.info(f"Subscribing to symbols: {symbols}")

        # Group symbols by market type
        us_stocks = []
        crypto = []

        for symbol in symbols:
            market_type = get_market_type(symbol)
            if market_type == "US":
                us_stocks.append(symbol)
            elif market_type == "CRYPTO":
                crypto.append(symbol)

        # Subscribe to appropriate providers
        if us_stocks and "alpaca" in self.providers:
            await self.providers["alpaca"].subscribe(us_stocks)

        if crypto and "binance" in self.providers:
            await self.providers["binance"].subscribe(crypto)

    async def unsubscribe_symbols(self, symbols: List[str]):
        """Unsubscribe from symbols."""
        logger.info(f"Unsubscribing from symbols: {symbols}")

        # Group symbols by market type
        us_stocks = []
        crypto = []

        for symbol in symbols:
            market_type = get_market_type(symbol)
            if market_type == "US":
                us_stocks.append(symbol)
            elif market_type == "CRYPTO":
                crypto.append(symbol)

        # Unsubscribe from appropriate providers
        if us_stocks and "alpaca" in self.providers:
            await self.providers["alpaca"].unsubscribe(us_stocks)

        if crypto and "binance" in self.providers:
            await self.providers["binance"].unsubscribe(crypto)

    async def get_latest_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get latest price for a symbol."""
        # Check cache first
        if symbol in self.price_cache:
            return self.price_cache[symbol]

        # Fetch from appropriate provider
        market_type = get_market_type(symbol)

        if market_type == "US" and "alpaca" in self.providers:
            return await self.providers["alpaca"].get_latest_price(symbol)
        elif market_type == "CRYPTO" and "binance" in self.providers:
            return await self.providers["binance"].get_latest_price(symbol)

        return None

    async def get_historical_data(
        self,
        symbol: str,
        timeframe: str,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        limit: int = 100
    ) -> Optional[pd.DataFrame]:
        """Get historical OHLCV data for a symbol."""
        market_type = get_market_type(symbol)

        if market_type == "US" and "alpaca" in self.providers:
            return await self.providers["alpaca"].get_historical_data(
                symbol, timeframe, start, end, limit
            )
        elif market_type == "CRYPTO" and "binance" in self.providers:
            return await self.providers["binance"].get_historical_data(
                symbol, timeframe, start, end, limit
            )

        return None

    def get_all_prices(self) -> Dict[str, Dict[str, Any]]:
        """Get all cached prices."""
        return self.price_cache

    def get_provider_status(self) -> Dict[str, bool]:
        """Get connection status of all providers."""
        return {
            name: provider.is_connected
            for name, provider in self.providers.items()
        }

    async def start_streams(self):
        """Start all WebSocket streams in background."""
        self._running = True
        tasks = []

        if "alpaca" in self.providers:
            tasks.append(asyncio.create_task(self.providers["alpaca"].run_stream()))

        if "binance" in self.providers:
            tasks.append(asyncio.create_task(self.providers["binance"].run_stream()))

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
