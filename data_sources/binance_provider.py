"""Binance data provider for cryptocurrency."""

import asyncio
import json
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
import pandas as pd
import websockets
import structlog
from binance.client import Client
from binance.enums import KLINE_INTERVAL_1MINUTE, KLINE_INTERVAL_5MINUTE, KLINE_INTERVAL_15MINUTE, KLINE_INTERVAL_1HOUR, KLINE_INTERVAL_4HOUR, KLINE_INTERVAL_1DAY

from .base import BaseDataProvider

logger = structlog.get_logger()


class BinanceProvider(BaseDataProvider):
    """Binance provider for cryptocurrency real-time data."""

    TIMEFRAME_MAPPING = {
        "1m": KLINE_INTERVAL_1MINUTE,
        "5m": KLINE_INTERVAL_5MINUTE,
        "15m": KLINE_INTERVAL_15MINUTE,
        "1h": KLINE_INTERVAL_1HOUR,
        "4h": KLINE_INTERVAL_4HOUR,
        "1D": KLINE_INTERVAL_1DAY,
    }

    # Binance WebSocket base URL
    WS_BASE_URL = "wss://stream.binance.com:9443/ws"

    def __init__(self, on_message: Optional[Callable] = None):
        """Initialize Binance provider."""
        super().__init__("Binance")

        # No API key needed for public data
        self.client = Client("", "")

        self.on_message = on_message
        self.subscribed_symbols: List[str] = []
        self.ws_connection = None
        self._running = False

    async def connect(self) -> bool:
        """Establish WebSocket connection."""
        try:
            logger.info("Connecting to Binance WebSocket...")
            self.is_connected = True
            self._running = True
            logger.info("Connected to Binance WebSocket")
            return True
        except Exception as e:
            self.last_error = str(e)
            logger.error(f"Failed to connect to Binance: {e}")
            return False

    async def disconnect(self):
        """Close WebSocket connection."""
        try:
            self._running = False
            if self.ws_connection:
                await self.ws_connection.close()
            self.is_connected = False
            logger.info("Disconnected from Binance")
        except Exception as e:
            logger.error(f"Error disconnecting from Binance: {e}")

    async def subscribe(self, symbols: List[str]):
        """Subscribe to real-time data for symbols."""
        try:
            # Convert symbols to Binance format (e.g., BTC-USD -> btcusdt)
            for symbol in symbols:
                binance_symbol = self._convert_symbol_to_binance(symbol)
                if binance_symbol and binance_symbol not in self.subscribed_symbols:
                    self.subscribed_symbols.append(binance_symbol)

            logger.info(f"Subscribed to Binance symbols: {self.subscribed_symbols}")
        except Exception as e:
            logger.error(f"Failed to subscribe to symbols: {e}")

    async def unsubscribe(self, symbols: List[str]):
        """Unsubscribe from symbols."""
        try:
            binance_symbols = [self._convert_symbol_to_binance(s) for s in symbols]
            self.subscribed_symbols = [
                s for s in self.subscribed_symbols if s not in binance_symbols
            ]
            logger.info(f"Unsubscribed from Binance symbols: {symbols}")
        except Exception as e:
            logger.error(f"Failed to unsubscribe from symbols: {e}")

    async def get_latest_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get latest price for a symbol."""
        try:
            binance_symbol = self._convert_symbol_to_binance(symbol)
            if not binance_symbol:
                return None

            ticker = self.client.get_symbol_ticker(symbol=binance_symbol.upper())
            return {
                "symbol": symbol,
                "price": float(ticker["price"]),
                "timestamp": datetime.now(),
                "provider": "binance"
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
            binance_symbol = self._convert_symbol_to_binance(symbol)
            if not binance_symbol:
                return None

            interval = self.TIMEFRAME_MAPPING.get(timeframe, KLINE_INTERVAL_1DAY)

            # Prepare parameters
            params = {
                "symbol": binance_symbol.upper(),
                "interval": interval,
                "limit": limit
            }

            if start:
                params["startTime"] = int(start.timestamp() * 1000)
            if end:
                params["endTime"] = int(end.timestamp() * 1000)

            # Fetch klines
            klines = self.client.get_klines(**params)

            # Convert to DataFrame
            df = pd.DataFrame(klines, columns=[
                "timestamp", "Open", "High", "Low", "Close", "Volume",
                "close_time", "quote_volume", "trades", "taker_buy_base",
                "taker_buy_quote", "ignore"
            ])

            # Convert types
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
            df.set_index("timestamp", inplace=True)

            for col in ["Open", "High", "Low", "Close", "Volume"]:
                df[col] = df[col].astype(float)

            # Keep only OHLCV columns
            df = df[["Open", "High", "Low", "Close", "Volume"]]

            return df

        except Exception as e:
            logger.error(f"Failed to get historical data for {symbol}: {e}")
            return None

    async def run_stream(self):
        """Run the WebSocket stream."""
        if not self.subscribed_symbols:
            logger.warning("No symbols subscribed for Binance stream")
            return

        # Create stream URLs
        streams = [f"{symbol.lower()}@ticker" for symbol in self.subscribed_symbols]
        stream_url = f"{self.WS_BASE_URL}/{'/'.join(streams)}"

        while self._running:
            try:
                async with websockets.connect(stream_url) as websocket:
                    self.ws_connection = websocket
                    logger.info(f"Binance WebSocket connected: {stream_url}")

                    while self._running:
                        message = await websocket.recv()
                        data = json.loads(message)

                        if "s" in data and "c" in data:  # Ticker data
                            if self.on_message:
                                symbol = self._convert_symbol_from_binance(data["s"])
                                msg = {
                                    "symbol": symbol,
                                    "price": float(data["c"]),
                                    "volume": float(data["v"]),
                                    "change_24h": float(data["P"]),
                                    "timestamp": datetime.fromtimestamp(data["E"] / 1000),
                                    "provider": "binance"
                                }
                                await self.on_message(msg)

            except websockets.exceptions.ConnectionClosed:
                logger.warning("Binance WebSocket connection closed, reconnecting...")
                await asyncio.sleep(5)
            except Exception as e:
                logger.error(f"Binance WebSocket error: {e}")
                await asyncio.sleep(5)

    def _convert_symbol_to_binance(self, symbol: str) -> Optional[str]:
        """Convert standard symbol format to Binance format."""
        # BTC-USD -> btcusdt
        # ETH-USD -> ethusdt
        if "-" in symbol:
            base, quote = symbol.split("-")
            if quote == "USD":
                return f"{base.lower()}usdt"
        return None

    def _convert_symbol_from_binance(self, binance_symbol: str) -> str:
        """Convert Binance symbol to standard format."""
        # BTCUSDT -> BTC-USD
        if binance_symbol.endswith("USDT"):
            base = binance_symbol[:-4]
            return f"{base}-USD"
        return binance_symbol

    def get_supported_symbols(self) -> List[str]:
        """Get list of supported crypto symbols."""
        return [
            "BTC-USD", "ETH-USD", "BNB-USD", "SOL-USD", "ADA-USD",
            "XRP-USD", "DOT-USD", "DOGE-USD", "AVAX-USD", "MATIC-USD"
        ]
