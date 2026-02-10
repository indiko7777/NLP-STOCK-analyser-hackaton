"""Price lookup tool for LLM agent."""

import asyncio
from typing import Dict, Any
from datetime import datetime, timedelta


class PriceLookupTool:
    """Tool for looking up current and historical prices."""

    def __init__(self, data_manager):
        """Initialize price lookup tool."""
        self.data_manager = data_manager
        self.name = "price_lookup"
        self.description = "Get current or historical price data for a stock or cryptocurrency symbol"

    def get_function_schema(self) -> Dict[str, Any]:
        """Get OpenAI function schema for this tool."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "The stock symbol (e.g., AAPL, MSFT) or crypto symbol (e.g., BTC-USD)"
                    },
                    "timeframe": {
                        "type": "string",
                        "description": "Timeframe for historical data",
                        "enum": ["1m", "5m", "15m", "1h", "4h", "1D"],
                        "default": "1D"
                    },
                    "days_back": {
                        "type": "integer",
                        "description": "Number of days of historical data to retrieve",
                        "default": 30
                    }
                },
                "required": ["symbol"]
            }
        }

    async def execute(
        self,
        symbol: str,
        timeframe: str = "1D",
        days_back: int = 30
    ) -> Dict[str, Any]:
        """Execute price lookup."""
        try:
            # Get current price
            current_price = await self.data_manager.get_latest_price(symbol)

            # Get historical data
            start_date = datetime.now() - timedelta(days=days_back)
            historical_data = await self.data_manager.get_historical_data(
                symbol=symbol,
                timeframe=timeframe,
                start=start_date,
                limit=days_back
            )

            result = {
                "symbol": symbol,
                "current_price": current_price,
                "historical_summary": None
            }

            if historical_data is not None and not historical_data.empty:
                result["historical_summary"] = {
                    "latest_close": float(historical_data["Close"].iloc[-1]),
                    "period_high": float(historical_data["High"].max()),
                    "period_low": float(historical_data["Low"].min()),
                    "period_avg": float(historical_data["Close"].mean()),
                    "total_volume": float(historical_data["Volume"].sum()),
                    "data_points": len(historical_data)
                }

            return result

        except Exception as e:
            return {"error": str(e)}
