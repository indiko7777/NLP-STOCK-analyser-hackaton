"""Configuration module for Stock Analyzer."""

from .settings import Settings
from .symbols import WATCHLIST, SYMBOL_MAPPING

__all__ = ["Settings", "WATCHLIST", "SYMBOL_MAPPING"]
