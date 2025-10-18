"""
Logging configuration for Enterprise Production Assistant
"""

import logging
import sys
from ..core.config import settings

def setup_logger(name: str = "enterprise_assistant") -> logging.Logger:
    """Setup and configure logger"""
    
    logger = logging.getLogger(name)
    
    if logger.handlers:
        return logger
    
    # Set level
    level = logging.DEBUG if settings.DEBUG else logging.INFO
    logger.setLevel(level)
    
    # Console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    return logger

# Default logger
logger = setup_logger()