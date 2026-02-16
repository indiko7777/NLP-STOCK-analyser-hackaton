"""Technical indicators calculation."""

from typing import Dict, Any, List, Optional

import pandas as pd
import numpy as np
import pandas_ta as ta
import structlog

logger = structlog.get_logger()


def _safe_last(series: pd.Series) -> Optional[float]:
    """Return the last value of a series as a float, or None if empty/NaN."""
    if series is None or series.empty:
        return None
    val = series.iloc[-1]
    return None if pd.isna(val) else float(val)


class TechnicalIndicators:
    """Calculate technical indicators for price data."""

    # ── Individual indicators ────────────────────────────────────────────

    @staticmethod
    def calculate_rsi(df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Relative Strength Index (RSI)."""
        return ta.rsi(df["Close"], length=period)

    @staticmethod
    def calculate_macd(
        df: pd.DataFrame,
        fast: int = 12,
        slow: int = 26,
        signal: int = 9,
    ) -> Dict[str, pd.Series]:
        """Calculate MACD (Moving Average Convergence Divergence)."""
        macd = ta.macd(df["Close"], fast=fast, slow=slow, signal=signal)
        suffix = f"{fast}_{slow}_{signal}"
        return {
            "macd": macd[f"MACD_{suffix}"],
            "signal": macd[f"MACDs_{suffix}"],
            "histogram": macd[f"MACDh_{suffix}"],
        }

    @staticmethod
    def calculate_bollinger_bands(
        df: pd.DataFrame,
        period: int = 20,
        std: float = 2.0,
    ) -> Dict[str, pd.Series]:
        """Calculate Bollinger Bands."""
        bbands = ta.bbands(df["Close"], length=period, std=std)
        suffix = f"{period}_{std}"
        return {
            "upper": bbands[f"BBU_{suffix}"],
            "middle": bbands[f"BBM_{suffix}"],
            "lower": bbands[f"BBL_{suffix}"],
        }

    @staticmethod
    def calculate_moving_averages(
        df: pd.DataFrame,
        periods: List[int] = None,
    ) -> Dict[str, pd.Series]:
        """Calculate Simple Moving Averages (SMA)."""
        return {
            f"sma_{p}": ta.sma(df["Close"], length=p)
            for p in (periods or [20, 50, 200])
        }

    @staticmethod
    def calculate_ema(
        df: pd.DataFrame,
        periods: List[int] = None,
    ) -> Dict[str, pd.Series]:
        """Calculate Exponential Moving Averages (EMA)."""
        return {
            f"ema_{p}": ta.ema(df["Close"], length=p)
            for p in (periods or [12, 26])
        }

    @staticmethod
    def calculate_stochastic(
        df: pd.DataFrame,
        k_period: int = 14,
        d_period: int = 3,
    ) -> Dict[str, pd.Series]:
        """Calculate Stochastic Oscillator."""
        stoch = ta.stoch(df["High"], df["Low"], df["Close"], k=k_period, d=d_period)
        return {
            "k": stoch[f"STOCHk_{k_period}_{d_period}_3"],
            "d": stoch[f"STOCHd_{k_period}_{d_period}_3"],
        }

    @staticmethod
    def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Average True Range (ATR)."""
        return ta.atr(df["High"], df["Low"], df["Close"], length=period)

    # ── Aggregate helpers ────────────────────────────────────────────────

    @staticmethod
    def calculate_all(df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate all technical indicators."""
        if df is None or df.empty:
            return {}

        indicators: Dict[str, Any] = {}
        calc = TechnicalIndicators

        try:
            # RSI
            rsi = calc.calculate_rsi(df)
            indicators["rsi"] = {"value": _safe_last(rsi), "series": rsi}

            # MACD
            macd = calc.calculate_macd(df)
            indicators["macd"] = {
                key: _safe_last(macd[key]) for key in ("macd", "signal", "histogram")
            }
            indicators["macd"]["series"] = macd

            # Bollinger Bands
            bbands = calc.calculate_bollinger_bands(df)
            indicators["bollinger"] = {
                key: _safe_last(bbands[key]) for key in ("upper", "middle", "lower")
            }
            indicators["bollinger"]["series"] = bbands

            # Moving Averages (SMA & EMA)
            for label, func in (("sma", calc.calculate_moving_averages), ("ema", calc.calculate_ema)):
                series_map = func(df)
                indicators[label] = {
                    name: _safe_last(s) for name, s in series_map.items()
                }

            # ATR
            atr = calc.calculate_atr(df)
            indicators["atr"] = {"value": _safe_last(atr), "series": atr}

        except Exception as e:
            logger.error(f"Error calculating indicators: {e}")

        return indicators

    @staticmethod
    def generate_signals(indicators: Dict[str, Any]) -> Dict[str, str]:
        """Generate trading signals based on indicators."""
        signals: Dict[str, str] = {}

        try:
            # RSI signals
            rsi_value = (indicators.get("rsi") or {}).get("value")
            if rsi_value is not None:
                if rsi_value > 70:
                    signals["rsi"] = "OVERBOUGHT"
                elif rsi_value < 30:
                    signals["rsi"] = "OVERSOLD"
                else:
                    signals["rsi"] = "NEUTRAL"

            # MACD signals
            macd_data = indicators.get("macd") or {}
            macd_val, signal_val = macd_data.get("macd"), macd_data.get("signal")
            if macd_val is not None and signal_val is not None:
                signals["macd"] = "BULLISH" if macd_val > signal_val else "BEARISH"

            # Bollinger Bands signals
            if "bollinger" in indicators:
                signals["bollinger"] = "NEUTRAL"

        except Exception as e:
            logger.error(f"Error generating signals: {e}")

        return signals
