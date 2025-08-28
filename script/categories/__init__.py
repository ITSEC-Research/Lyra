"""
Category management for different types of domain blocklists.
"""

from .base import BaseCategory
from .gambling import GamblingCategory
from .suspicious import SuspiciousCategory
from .malicious import MaliciousCategory
from .adult import AdultCategory

__all__ = ['BaseCategory', 'GamblingCategory', 'SuspiciousCategory', 'MaliciousCategory', 'AdultCategory']
