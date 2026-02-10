"""Logging configuration for Stock Analyzer."""

import logging
import structlog
from config.settings import settings


def configure_logging():
    """Configure structured logging."""
    logging.basicConfig(
        format="%(message)s",
        level=getattr(logging, settings.log_level),
    )

    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.stdlib.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


# Configure on import
configure_logging()
