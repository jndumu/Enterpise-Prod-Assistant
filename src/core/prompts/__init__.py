"""
Prompt management package for semantic search system.
Contains optimized prompts for different AI providers and use cases.
"""

from .templates import SearchPrompts, SummaryPrompts

__all__ = ['SearchPrompts', 'SummaryPrompts']
__version__ = '1.0.0'