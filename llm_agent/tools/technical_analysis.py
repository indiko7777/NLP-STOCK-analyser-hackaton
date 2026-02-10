"""Technical analysis tool for LLM agent."""

from typing import Dict, Any, List
from datetime import datetime, timedelta
from analysis import TechnicalIndicators


class TechnicalAnalysisTool:
    """Tool for calculating technical indicators."""

    def __init__(self, data_manager):
        """Initialize technical analysis tool."""
        self.data_manager = data_manager
        self.name = "technical_analysis"
        self.description = "Calculate technical indicators (RSI, MACD, Bollinger Bands, Moving Averages) for a symbol"

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
                        "description": "The stock or crypto symbol to analyze"
                    },
                    "timeframe": {
                        "type": "string",
                        "description": "Timeframe for analysis",
                        "enum": ["1m", "5m", "15m", "1h", "4h", "1D"],
                        "default": "1D"
                    },
                    "indicators": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": ["rsi", "macd", "bollinger", "sma", "ema", "atr", "all"]
                        },
                        "description": "List of indicators to calculate",
                        "default": ["all"]
                    }
                },
                "required": ["symbol"]
            }
        }

    async def execute(
        self,
        symbol: str,
        timeframe: str = "1D",
        indicators: List[str] = ["all"]
    ) -> Dict[str, Any]:
        """Execute technical analysis."""
        try:
            # Get historical data
            start_date = datetime.now() - timedelta(days=100)  # Need enough data for indicators
            df = await self.data_manager.get_historical_data(
                symbol=symbol,
                timeframe=timeframe,
                start=start_date,
                limit=100
            )

            if df is None or df.empty:
                return {"error": f"No data available for {symbol}"}

            # Calculate indicators
            if "all" in indicators:
                results = TechnicalIndicators.calculate_all(df)
            else:
                results = {}
                if "rsi" in indicators:
                    rsi = TechnicalIndicators.calculate_rsi(df)
                    results["rsi"] = {"value": float(rsi.iloc[-1]) if not rsi.empty else None}

                if "macd" in indicators:
                    macd = TechnicalIndicators.calculate_macd(df)
                    results["macd"] = {
                        "macd": float(macd["macd"].iloc[-1]) if not macd["macd"].empty else None,
                        "signal": float(macd["signal"].iloc[-1]) if not macd["signal"].empty else None,
                        "histogram": float(macd["histogram"].iloc[-1]) if not macd["histogram"].empty else None
                    }

                if "bollinger" in indicators:
                    bbands = TechnicalIndicators.calculate_bollinger_bands(df)
                    results["bollinger"] = {
                        "upper": float(bbands["upper"].iloc[-1]) if not bbands["upper"].empty else None,
                        "middle": float(bbands["middle"].iloc[-1]) if not bbands["middle"].empty else None,
                        "lower": float(bbands["lower"].iloc[-1]) if not bbands["lower"].empty else None
                    }

                if "sma" in indicators:
                    mas = TechnicalIndicators.calculate_moving_averages(df)
                    results["sma"] = {
                        period: float(ma.iloc[-1]) if not ma.empty else None
                        for period, ma in mas.items()
                    }

            # Generate trading signals
            signals = TechnicalIndicators.generate_signals(results)

            return {
                "symbol": symbol,
                "timeframe": timeframe,
                "indicators": results,
                "signals": signals,
                "current_price": float(df["Close"].iloc[-1])
            }

        except Exception as e:
            return {"error": str(e)}
