import logging
import logging.config
from pathlib import Path

from src.config import settings


def setup_logging() -> None:
    logging_config = settings.logger_settings.LOGGING_CONFIG

    if not logging_config:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
        return

    # Create logs directory if it doesn't exist
    for _, handler_config in logging_config.get("handlers", {}).items():
        filename = handler_config.get("filename")
        if filename:
            log_dir = Path(filename).parent
            if log_dir and not log_dir.exists():
                log_dir.mkdir(parents=True, exist_ok=True)

    logging.config.dictConfig(logging_config)


def get_logger(name: str | None = None) -> logging.Logger:
    if name is None:
        name = "app"
    return logging.getLogger(name)
