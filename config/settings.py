"""Application settings and configuration management."""

import os
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Load environment variables
load_dotenv()


class APIKeys(BaseModel):
    """API keys configuration."""

    openrouter: str = Field(default="", alias="OPENROUTER_API_KEY")
    alpaca_key: str = Field(default="", alias="ALPACA_API_KEY")
    alpaca_secret: str = Field(default="", alias="ALPACA_SECRET_KEY")
    twelve_data: str = Field(default="", alias="TWELVE_DATA_API_KEY")
    alpha_vantage: str = Field(default="", alias="ALPHA_VANTAGE_API_KEY")
    finnhub: str = Field(default="", alias="FINNHUB_API_KEY")


class AlpacaConfig(BaseModel):
    """Alpaca API configuration."""

    base_url: str = Field(
        default="https://paper-api.alpaca.markets",
        alias="ALPACA_BASE_URL"
    )
    api_key: str = ""
    secret_key: str = ""


class Settings(BaseModel):
    """Main application settings."""

    # App settings
    debug: bool = Field(default=False, alias="DEBUG")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    # Paths
    base_dir: Path = Path(__file__).parent.parent
    data_dir: Path = base_dir / "data"
    db_path: Path = data_dir / "stockanalyzer.duckdb"

    # API Configuration
    api_keys: APIKeys = Field(default_factory=APIKeys)
    alpaca_config: AlpacaConfig = Field(default_factory=AlpacaConfig)

    # WebSocket settings
    ws_reconnect_delay: int = 5
    ws_max_reconnect_attempts: int = 10

    # Rate limiting
    alpaca_rate_limit: int = 200  # requests per minute
    twelve_data_rate_limit: int = 8  # concurrent connections
    finnhub_rate_limit: int = 60  # requests per minute

    # Cache settings
    price_cache_ttl: int = 60  # seconds
    fundamentals_cache_ttl: int = 3600  # 1 hour

    # LLM settings
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    default_model: str = "xiaomi/mimo-v2-flash:free"

    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"

    def __init__(self, **data):
        """Initialize settings and create necessary directories."""
        super().__init__(**data)

        # Load API keys from environment
        self.api_keys = APIKeys(
            OPENROUTER_API_KEY=os.getenv("OPENROUTER_API_KEY", ""),
            ALPACA_API_KEY=os.getenv("ALPACA_API_KEY", ""),
            ALPACA_SECRET_KEY=os.getenv("ALPACA_SECRET_KEY", ""),
            TWELVE_DATA_API_KEY=os.getenv("TWELVE_DATA_API_KEY", ""),
            ALPHA_VANTAGE_API_KEY=os.getenv("ALPHA_VANTAGE_API_KEY", ""),
            FINNHUB_API_KEY=os.getenv("FINNHUB_API_KEY", ""),
        )

        # Load Alpaca config
        self.alpaca_config = AlpacaConfig(
            ALPACA_BASE_URL=os.getenv("ALPACA_BASE_URL", "https://paper-api.alpaca.markets"),
            api_key=self.api_keys.alpaca_key,
            secret_key=self.api_keys.alpaca_secret,
        )

        # Create data directory if it doesn't exist
        self.data_dir.mkdir(exist_ok=True)


# Global settings instance
settings = Settings()
