import logging
import sys
from pathlib import Path
from typing import Optional

class ProductionLogManager:
    """Configures centralized structured logging for Riva Production runtime."""

    @staticmethod
    def setup_logger(name: str = "riva", level: str = "INFO", log_file: Optional[str] = None) -> logging.Logger:
        logger = logging.getLogger(name)
        
        # Clear existing handlers to prevent duplicate logging
        if logger.hasHandlers():
            logger.handlers.clear()

        numeric_level = getattr(logging, level.upper(), logging.INFO)
        logger.setLevel(numeric_level)

        formatter = logging.Formatter(
            '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}'
        )

        # Console handler
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(numeric_level)
        ch.setFormatter(formatter)
        logger.addHandler(ch)

        # Optional File handler
        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            fh = logging.FileHandler(log_path, encoding="utf-8")
            fh.setLevel(numeric_level)
            fh.setFormatter(formatter)
            logger.addHandler(fh)

        logger.propagate = False
        return logger
