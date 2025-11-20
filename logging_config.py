"""
Logging Configuration for FARVS
================================

This module provides centralized logging configuration for debugging.
Can be easily enabled/disabled via environment variable or config.

Usage:
    from logging_config import setup_logging, get_logger
    
    setup_logging(debug=True)
    logger = get_logger(__name__)
    logger.debug("Debug message")
    logger.info("Info message")
"""

import logging
import sys
from typing import Optional


# Global logger instance
_logger: Optional[logging.Logger] = None


def setup_logging(debug: bool = False, log_file: Optional[str] = None):
    """
    Configure logging for the application.
    
    Args:
        debug: If True, enable DEBUG level logging. If False, use INFO level.
        log_file: Optional path to log file. If None, logs only to console.
    """
    global _logger
    
    # Determine log level
    level = logging.DEBUG if debug else logging.INFO
    
    # Create formatter
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Remove existing handlers to avoid duplicates
    root_logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        try:
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
        except Exception as e:
            print(f"Warning: Could not create log file {log_file}: {e}")
    
    _logger = root_logger
    
    if debug:
        root_logger.debug("Debug logging enabled")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for the specified module.
    
    Args:
        name: Logger name (typically __name__ of the calling module)
    
    Returns:
        Logger instance configured with application settings
    """
    return logging.getLogger(name)

