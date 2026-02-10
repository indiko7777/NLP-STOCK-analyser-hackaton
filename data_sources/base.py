"""Base data provider interface."""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import datetime
import pandas as pd


class BaseDataProvider(ABC):
    """Abstract base class for data providers."""

    def __init__(self, name: str):
        """Initialize provider."""
        self.name = name
        self.is_connected = False
        self.last_error: Optional[str] = None

    @abstractmethod
    async def connect(self) -> bool:
        """Establish connection to data source."""
        pass

    @abstractmethod
    async def disconnect(self):
        """Close connection to data source."""
        pass

    @abstractmethod
    async def subscribe(self, symbols: List[str]):
        """Subscribe to real-time data for symbols."""
        pass

    @abstractmethod
    async def unsubscribe(self, symbols: List[str]):
        """Unsubscribe from symbols."""
        pass

    @abstractmethod
    async def get_latest_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get latest price for a symbol."""
        pass

    @abstractmethod
    async def get_historical_data(
        self,
        symbol: str,
        timeframe: str,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        limit: int = 100
    ) -> Optional[pd.DataFrame]:
        """Get historical OHLCV data."""
        pass

    def get_supported_symbols(self) -> List[str]:
        """Get list of supported symbols."""
        return []

    def get_supported_timeframes(self) -> List[str]:
        """Get list of supported timeframes."""
        return ["1m", "5m", "15m", "1h", "4h", "1D"]

    def health_check(self) -> bool:
        """Check if provider is healthy."""
        return self.is_connected and self.last_error is None
