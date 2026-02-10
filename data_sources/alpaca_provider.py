"""Alpaca data provider for US stocks."""

import asyncio
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
import pandas as pd
from alpaca.data import StockHistoricalDataClient
from alpaca.data.live import StockDataStream
from alpaca.data.requests import StockBarsRequest, StockLatestQuoteRequest
from alpaca.data.timeframe import TimeFrame
import structlog

from .base import BaseDataProvider
from config.settings import settings

logger = structlog.get_logger()


class AlpacaProvider(BaseDataProvider):
    """Alpaca provider for US stocks real-time data."""

    TIMEFRAME_MAPPING = {
        "1m": TimeFrame.Minute,
        "5m": TimeFrame(5, TimeFrame.Minute),
        "15m": TimeFrame(15, TimeFrame.Minute),
        "1h": TimeFrame.Hour,
        "4h": TimeFrame(4, TimeFrame.Hour),
        "1D": TimeFrame.Day,
    }

    def __init__(self, on_message: Optional[Callable] = None):
        """Initialize Alpaca provider."""
        super().__init__("Alpaca")
        self.api_key = settings.api_keys.alpaca_key
        self.secret_key = settings.api_keys.alpaca_secret

        if not self.api_key or not self.secret_key:
            logger.warning("Alpaca API keys not configured")
            raise ValueError("Alpaca API keys are required")

        # Historical data client
        self.hist_client = StockHistoricalDataClient(
            api_key=self.api_key,
            secret_key=self.secret_key
        )

        # WebSocket stream client
        self.stream = StockDataStream(
            api_key=self.api_key,
            secret_key=self.secret_key
        )

        self.on_message = on_message
        self.subscribed_symbols: List[str] = []

    async def connect(self) -> bool:
        """Establish WebSocket connection."""
        try:
            logger.info("Connecting to Alpaca WebSocket...")

            # Register handlers
            async def quote_handler(data):
                """Handle incoming quote data."""
                if self.on_message:
                    message = {
                        "symbol": data.symbol,
                        "price": float(data.bid_price + data.ask_price) / 2,
                        "bid": float(data.bid_price),
                        "ask": float(data.ask_price),
                        "bid_size": data.bid_size,
                        "ask_size": data.ask_size,
                        "timestamp": data.timestamp,
                        "provider": "alpaca"
                    }
                    await self.on_message(message)

            async def trade_handler(data):
                """Handle incoming trade data."""
                if self.on_message:
                    message = {
                        "symbol": data.symbol,
                        "price": float(data.price),
                        "volume": data.size,
                        "timestamp": data.timestamp,
                        "provider": "alpaca"
                    }
                    await self.on_message(message)

            # Subscribe handlers
            self.stream.subscribe_quotes(quote_handler, *self.subscribed_symbols)
            self.stream.subscribe_trades(trade_handler, *self.subscribed_symbols)

            self.is_connected = True
            logger.info("Connected to Alpaca WebSocket")
            return True

        except Exception as e:
            self.last_error = str(e)
            logger.error(f"Failed to connect to Alpaca: {e}")
            return False

    async def disconnect(self):
        """Close WebSocket connection."""
        try:
            if self.stream:
                await self.stream.stop_ws()
                self.is_connected = False
                logger.info("Disconnected from Alpaca")
        except Exception as e:
            logger.error(f"Error disconnecting from Alpaca: {e}")

    async def subscribe(self, symbols: List[str]):
        """Subscribe to real-time data for symbols."""
        try:
            self.subscribed_symbols.extend([s for s in symbols if s not in self.subscribed_symbols])
            logger.info(f"Subscribed to Alpaca symbols: {symbols}")
        except Exception as e:
            logger.error(f"Failed to subscribe to symbols: {e}")

    async def unsubscribe(self, symbols: List[str]):
        """Unsubscribe from symbols."""
        try:
            self.subscribed_symbols = [s for s in self.subscribed_symbols if s not in symbols]
            logger.info(f"Unsubscribed from Alpaca symbols: {symbols}")
        except Exception as e:
            logger.error(f"Failed to unsubscribe from symbols: {e}")

    async def get_latest_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get latest price for a symbol."""
        try:
            request = StockLatestQuoteRequest(symbol_or_symbols=symbol)
            quotes = self.hist_client.get_stock_latest_quote(request)

            if symbol in quotes:
                quote = quotes[symbol]
                return {
                    "symbol": symbol,
                    "price": float(quote.bid_price + quote.ask_price) / 2,
                    "bid": float(quote.bid_price),
                    "ask": float(quote.ask_price),
                    "timestamp": quote.timestamp,
                    "provider": "alpaca"
                }
        except Exception as e:
            logger.error(f"Failed to get latest price for {symbol}: {e}")
            return None

    async def get_historical_data(
        self,
        symbol: str,
        timeframe: str,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        limit: int = 100
    ) -> Optional[pd.DataFrame]:
        """Get historical OHLCV data."""
        try:
            # Default to last 30 days if no start time provided
            if start is None:
                start = datetime.now() - timedelta(days=30)
            if end is None:
                end = datetime.now()

            # Map timeframe
            tf = self.TIMEFRAME_MAPPING.get(timeframe, TimeFrame.Day)

            # Create request
            request = StockBarsRequest(
                symbol_or_symbols=symbol,
                timeframe=tf,
                start=start,
                end=end,
                limit=limit
            )

            # Fetch data
            bars = self.hist_client.get_stock_bars(request)

            if symbol in bars:
                df = bars[symbol].df
                df = df.rename(columns={
                    "open": "Open",
                    "high": "High",
                    "low": "Low",
                    "close": "Close",
                    "volume": "Volume"
                })
                return df

            return None

        except Exception as e:
            logger.error(f"Failed to get historical data for {symbol}: {e}")
            return None

    def get_supported_symbols(self) -> List[str]:
        """Get list of supported US stock symbols."""
        # Common US stocks - in production, fetch from Alpaca API
        return [
            "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "META",
            "BRK.B", "JPM", "V", "UNH", "JNJ", "WMT", "XOM", "PG"
        ]

    async def run_stream(self):
        """Run the WebSocket stream (call this in background task)."""
        try:
            await self.stream.run()
        except Exception as e:
            logger.error(f"Stream error: {e}")
            self.is_connected = False
