"""Custom Exception Handling for Production RAG Application.

This module provides enhanced exception handling with detailed context capture,
structured error reporting, and comprehensive stack trace analysis. Designed
for production environments requiring detailed error diagnostics.

Features:
    - Enhanced error context with file and line information
    - Comprehensive stack trace capture and formatting
    - Support for exception chaining and wrapping
    - Logger-friendly error message formatting
    - Integration with monitoring and alerting systems
    - Thread-safe exception handling

Usage:
    >>> try:
    ...     risky_operation()
    ... except Exception as e:
    ...     raise ResearchAnalystException("Operation failed", e) from e

Author: Production RAG Team
Version: 1.0.0
"""

import sys
import traceback
from typing import Optional, cast

class ResearchAnalystException(Exception):
    """Production-grade custom exception with enhanced error context.
    
    This exception class provides comprehensive error information including
    file location, line numbers, detailed stack traces, and structured
    error messages. Designed for production debugging and monitoring.
    
    The exception automatically captures the most relevant stack frame
    information and provides both human-readable and machine-parseable
    error formats for integration with logging and monitoring systems.
    
    Attributes:
        file_name (str): Source file where the error occurred
        lineno (int): Line number where the error occurred
        error_message (str): Normalized error message
        traceback_str (str): Full formatted traceback string
        
    Example:
        >>> try:
        ...     result = 1 / 0
        ... except ZeroDivisionError as e:
        ...     raise ResearchAnalystException("Division error", e) from e
    """
    
    def __init__(self, error_message, error_details: Optional[object] = None):
        """Initialize the custom exception with enhanced context capture.
        
        Args:
            error_message: Primary error message or exception object.
                         Will be normalized to string representation.
            error_details (Optional[object]): Additional error context.
                                             Can be an Exception, sys module,
                                             or None for current context.
                                             
        Processing:
            1. Normalizes error message to string format
            2. Extracts exception info from various sources
            3. Captures detailed stack trace information
            4. Identifies the most relevant error location
            5. Formats comprehensive error context
            
        Note:
            The exception automatically walks the stack trace to find
            the most relevant error location, providing accurate debugging
            information even in complex call stacks.
        """
        # Normalize message
        if isinstance(error_message, BaseException):
            norm_msg = str(error_message)
        else:
            norm_msg = str(error_message)

        # Resolve exc_info (supports: sys module, Exception object, or current context)
        exc_type = exc_value = exc_tb = None
        if error_details is None:
            exc_type, exc_value, exc_tb = sys.exc_info()
        else:
            if hasattr(error_details, "exc_info"):  # e.g., sys
                exc_info_obj = cast(sys, error_details)
                exc_type, exc_value, exc_tb = exc_info_obj.exc_info()
            elif isinstance(error_details, BaseException):
                exc_type, exc_value, exc_tb = type(error_details), error_details, error_details.__traceback__
            else:
                exc_type, exc_value, exc_tb = sys.exc_info()

        # Walk to the last frame to report the most relevant location
        last_tb = exc_tb
        while last_tb and last_tb.tb_next:
            last_tb = last_tb.tb_next

        self.file_name = last_tb.tb_frame.f_code.co_filename if last_tb else "<unknown>"
        self.lineno = last_tb.tb_lineno if last_tb else -1
        self.error_message = norm_msg

        # Full pretty traceback (if available)
        if exc_type and exc_tb:
            self.traceback_str = ''.join(traceback.format_exception(exc_type, exc_value, exc_tb))
        else:
            self.traceback_str = ""

        super().__init__(self.__str__())

    def __str__(self) -> str:
        """Return human-readable string representation of the exception.
        
        Provides a compact, logger-friendly error message that includes
        file location, line number, error message, and optional stack trace.
        Optimized for both console output and log file storage.
        
        Returns:
            str: Formatted error string with location and context information.
                 Includes full traceback if available.
                 
        Format:
            "Error in [filename] at line [number] | Message: [error_text]"
            Optional: "\nTraceback:\n[full_stack_trace]"
        """
        # Compact, logger-friendly message (no leading spaces)
        base = f"Error in [{self.file_name}] at line [{self.lineno}] | Message: {self.error_message}"
        if self.traceback_str:
            return f"{base}\nTraceback:\n{self.traceback_str}"
        return base

    def __repr__(self) -> str:
        """Return developer-friendly representation of the exception.
        
        Provides a structured representation suitable for debugging,
        logging systems, and development environments. Includes key
        attributes in a parseable format.
        
        Returns:
            str: Structured representation with file, line, and message info.
        """
        return f"ResearchAnalystException(file={self.file_name!r}, line={self.lineno}, message={self.error_message!r})"


# if __name__ == "__main__":
#     # Demo-1: generic exception -> wrap
#     try:
#         a = 1 / 0
#     except Exception as e:
#         raise ResearchAnalystException("Division failed", e) from e

#     # Demo-2: still supports sys (old pattern)
#     # try:
#     #     a = int("abc")
#     # except Exception as e:
#     #     raise ResearchAnalystException(e, sys)