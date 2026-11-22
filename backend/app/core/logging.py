"""
TripSync AI - Structured Application Logging Configuration
"""

import logging
import sys


def setup_logging(level: str = "INFO"):
    """Configures structured console logging for FastAPI backend."""
    log_format = "%(asctime)s [%(levelname)s] [%(name)s]: %(message)s"
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format=log_format,
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True,
    )


logger = logging.getLogger("TripSyncBackend")
