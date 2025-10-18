"""
Custom exceptions for Enterprise Production Assistant
"""

class DocumentProcessingError(Exception):
    """Raised when document processing fails"""
    pass

class SearchError(Exception):
    """Raised when search operations fail"""  
    pass

class ConfigurationError(Exception):
    """Raised when configuration is invalid"""
    pass