"""Custom Logging System for Production RAG Application.

This module provides a production-grade logging infrastructure with structured
JSON logging, file persistence, and console output. Built on top of Python's
logging module and structlog for enhanced observability and debugging.

Features:
    - Structured JSON logging for better parsing and analysis
    - Dual output: console and timestamped file logging
    - ISO 8601 timestamps with UTC timezone
    - Configurable log directories and levels
    - Integration with monitoring and alerting systems
    - Thread-safe operations for concurrent environments

Usage:
    >>> logger = CustomLogger(log_dir="logs").get_logger(__name__)
    >>> logger.info("User action", user_id=123, action="upload", filename="doc.pdf")
    >>> logger.error("Processing failed", error="timeout", duration_ms=5000)

Author: Production RAG Team
Version: 1.0.0
"""

import os
import logging
from datetime import datetime
import structlog

class CustomLogger:
    """Production-grade structured logging system.
    
    This class provides centralized logging configuration with support for
    both structured JSON logs and human-readable console output. Designed
    for production environments requiring detailed observability.
    
    The logger automatically creates timestamped log files, ensures thread
    safety, and provides consistent formatting across the application.
    
    Attributes:
        logs_dir (str): Directory path for log file storage
        log_file_path (str): Full path to current log file
        
    Example:
        >>> custom_logger = CustomLogger(log_dir="app_logs")
        >>> logger = custom_logger.get_logger("my_module")
        >>> logger.info("Application started", version="1.0.0", env="production")
    """
    
    def __init__(self, log_dir: str = "logs"):
        """Initialize the custom logger with specified configuration.
        
        Args:
            log_dir (str): Directory name for storing log files.
                         Will be created if it doesn't exist.
                         Defaults to "logs" in the current working directory.
                         
        Side Effects:
            - Creates log directory if it doesn't exist
            - Generates timestamped log file for this session
            - Sets up directory permissions for log writing
            
        Note:
            Each logger instance creates a unique timestamped log file.
            Multiple instances will create separate log files.
        """
        # Ensure logs directory exists
        self.logs_dir = os.path.join(os.getcwd(), log_dir)
        os.makedirs(self.logs_dir, exist_ok=True)

        # Timestamped log file (for persistence)
        log_file = f"{datetime.now().strftime('%m_%d_%Y_%H_%M_%S')}.log"
        self.log_file_path = os.path.join(self.logs_dir, log_file)

    def get_logger(self, name: str = __file__):
        """Create and configure a structured logger instance.
        
        This method sets up a complete logging pipeline with both console
        and file output, structured JSON formatting, and production-ready
        configuration. Each logger is optimized for performance and observability.
        
        Args:
            name (str): Logger name, typically __name__ or __file__.
                       Will be processed to extract basename for cleaner logs.
                       Defaults to current file if not specified.
                       
        Returns:
            structlog.BoundLogger: Configured logger instance with JSON formatting,
                                 timestamp injection, and dual output handlers.
                                 
        Features:
            - JSON structured logging for machine parsing
            - ISO 8601 UTC timestamps
            - Log level injection
            - Event field renaming for consistency
            - Both console and file output
            - Thread-safe operation
            
        Example:
            >>> logger = CustomLogger().get_logger(__name__)
            >>> logger.info("Process started", pid=os.getpid(), memory_mb=256)
            >>> logger.warning("High latency detected", response_time_ms=1500)
            
        Note:
            The returned logger supports both positional messages and
            keyword arguments for structured data. All logs are automatically
            timestamped and formatted consistently.
        """
        logger_name = os.path.basename(name)

        # Configure logging for console + file (both JSON)
        file_handler = logging.FileHandler(self.log_file_path)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter("%(message)s"))  # Raw JSON lines

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(logging.Formatter("%(message)s"))

        logging.basicConfig(
            level=logging.INFO,
            format="%(message)s",  # Structlog will handle JSON rendering
            handlers=[console_handler, file_handler]
        )

        # Configure structlog for JSON structured logging
        structlog.configure(
            processors=[
                structlog.processors.TimeStamper(fmt="iso", utc=True, key="timestamp"),
                structlog.processors.add_log_level,
                structlog.processors.EventRenamer(to="event"),
                structlog.processors.JSONRenderer()
            ],
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )

        return structlog.get_logger(logger_name)


# # --- Usage Example ---
# if __name__ == "__main__":
#     logger = CustomLogger().get_logger(__file__)
#     logger.info("User uploaded a file", user_id=123, filename="report.pdf")
#     logger.error("Failed to process PDF", error="File not found", user_id=123)