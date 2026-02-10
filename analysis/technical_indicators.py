"""Technical indicators calculation."""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
import pandas_ta as ta


class TechnicalIndicators:
    """Calculate technical indicators for price data."""

    @staticmethod
    def calculate_rsi(df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Relative Strength Index (RSI)."""
        return ta.rsi(df["Close"], length=period)

    @staticmethod
    def calculate_macd(
        df: pd.DataFrame,
        fast: int = 12,
        slow: int = 26,
        signal: int = 9
    ) -> Dict[str, pd.Series]:
        """Calculate MACD (Moving Average Convergence Divergence)."""
        macd = ta.macd(df["Close"], fast=fast, slow=slow, signal=signal)
        return {
            "macd": macd[f"MACD_{fast}_{slow}_{signal}"],
            "signal": macd[f"MACDs_{fast}_{slow}_{signal}"],
            "histogram": macd[f"MACDh_{fast}_{slow}_{signal}"]
        }

    @staticmethod
    def calculate_bollinger_bands(
        df: pd.DataFrame,
        period: int = 20,
        std: float = 2.0
    ) -> Dict[str, pd.Series]:
        """Calculate Bollinger Bands."""
        bbands = ta.bbands(df["Close"], length=period, std=std)
        return {
            "upper": bbands[f"BBU_{period}_{std}"],
            "middle": bbands[f"BBM_{period}_{std}"],
            "lower": bbands[f"BBL_{period}_{std}"]
        }

    @staticmethod
    def calculate_moving_averages(
        df: pd.DataFrame,
        periods: list = [20, 50, 200]
    ) -> Dict[str, pd.Series]:
        """Calculate Simple Moving Averages (SMA)."""
        mas = {}
        for period in periods:
            mas[f"sma_{period}"] = ta.sma(df["Close"], length=period)
        return mas

    @staticmethod
    def calculate_ema(
        df: pd.DataFrame,
        periods: list = [12, 26]
    ) -> Dict[str, pd.Series]:
        """Calculate Exponential Moving Averages (EMA)."""
        emas = {}
        for period in periods:
            emas[f"ema_{period}"] = ta.ema(df["Close"], length=period)
        return emas

    @staticmethod
    def calculate_stochastic(
        df: pd.DataFrame,
        k_period: int = 14,
        d_period: int = 3
    ) -> Dict[str, pd.Series]:
        """Calculate Stochastic Oscillator."""
        stoch = ta.stoch(df["High"], df["Low"], df["Close"], k=k_period, d=d_period)
        return {
            "k": stoch[f"STOCHk_{k_period}_{d_period}_3"],
            "d": stoch[f"STOCHd_{k_period}_{d_period}_3"]
        }

    @staticmethod
    def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Average True Range (ATR)."""
        return ta.atr(df["High"], df["Low"], df["Close"], length=period)

    @staticmethod
    def calculate_all(df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate all technical indicators."""
        if df is None or df.empty:
            return {}

        indicators = {}

        try:
            # RSI
            rsi = TechnicalIndicators.calculate_rsi(df)
            indicators["rsi"] = {
                "value": float(rsi.iloc[-1]) if not rsi.empty else None,
                "series": rsi
            }

            # MACD
            macd = TechnicalIndicators.calculate_macd(df)
            indicators["macd"] = {
                "macd": float(macd["macd"].iloc[-1]) if not macd["macd"].empty else None,
                "signal": float(macd["signal"].iloc[-1]) if not macd["signal"].empty else None,
                "histogram": float(macd["histogram"].iloc[-1]) if not macd["histogram"].empty else None,
                "series": macd
            }

            # Bollinger Bands
            bbands = TechnicalIndicators.calculate_bollinger_bands(df)
            indicators["bollinger"] = {
                "upper": float(bbands["upper"].iloc[-1]) if not bbands["upper"].empty else None,
                "middle": float(bbands["middle"].iloc[-1]) if not bbands["middle"].empty else None,
                "lower": float(bbands["lower"].iloc[-1]) if not bbands["lower"].empty else None,
                "series": bbands
            }

            # Moving Averages
            mas = TechnicalIndicators.calculate_moving_averages(df)
            indicators["sma"] = {
                period: float(ma.iloc[-1]) if not ma.empty else None
                for period, ma in mas.items()
            }

            # EMAs
            emas = TechnicalIndicators.calculate_ema(df)
            indicators["ema"] = {
                period: float(ema.iloc[-1]) if not ema.empty else None
                for period, ema in emas.items()
            }

            # ATR
            atr = TechnicalIndicators.calculate_atr(df)
            indicators["atr"] = {
                "value": float(atr.iloc[-1]) if not atr.empty else None,
                "series": atr
            }

        except Exception as e:
            print(f"Error calculating indicators: {e}")

        return indicators

    @staticmethod
    def generate_signals(indicators: Dict[str, Any]) -> Dict[str, str]:
        """Generate trading signals based on indicators."""
        signals = {}

        try:
            # RSI signals
            if "rsi" in indicators and indicators["rsi"]["value"]:
                rsi_value = indicators["rsi"]["value"]
                if rsi_value > 70:
                    signals["rsi"] = "OVERBOUGHT"
                elif rsi_value < 30:
                    signals["rsi"] = "OVERSOLD"
                else:
                    signals["rsi"] = "NEUTRAL"

            # MACD signals
            if "macd" in indicators:
                macd_val = indicators["macd"].get("macd")
                signal_val = indicators["macd"].get("signal")

                if macd_val and signal_val:
                    if macd_val > signal_val:
                        signals["macd"] = "BULLISH"
                    else:
                        signals["macd"] = "BEARISH"

            # Bollinger Bands signals
            if "bollinger" in indicators:
                # You would need current price here
                # For now, placeholder
                signals["bollinger"] = "NEUTRAL"

        except Exception as e:
            print(f"Error generating signals: {e}")

        return signals
