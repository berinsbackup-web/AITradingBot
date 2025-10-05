import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logger(
    name: str = __name__,
    level=logging.DEBUG,
    log_file: str = 'logs/trading_bot.log',
    max_bytes: int = 10 * 1024 * 1024,
    backup_count: int = 5
):
    """
    Setup a logger with both console and rotating file handlers.
    
    Args:
        name (str): Logger name.
        level (int): Logging level, e.g. logging.DEBUG.
        log_file (str): Path to log file.
        max_bytes (int): Max size per log file in bytes before rotating.
        backup_count (int): Number of rotated log files to keep.
    
    Returns:
        logging.Logger: Configured logger instance.
    """
    # Create directory for log files if it doesn't exist
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.hasHandlers():
        # Console handler with detailed formatter
        ch = logging.StreamHandler()
        ch.setLevel(level)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        ch.setFormatter(console_formatter)
        logger.addHandler(ch)

        # Rotating file handler with simplified formatter
        fh = RotatingFileHandler(
            log_file, maxBytes=max_bytes, backupCount=backup_count, mode='a', encoding='utf-8'
        )
        fh.setLevel(level)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        fh.setFormatter(file_formatter)
        logger.addHandler(fh)

    return logger
