"""
Data models and enums for Giphy API responses.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Union, Any


class ErrorType(Enum):
    """Error types for categorizing API failures."""
    TIMEOUT = "TIMEOUT"
    CLIENT_ERROR = "CLIENT_ERROR"
    SERVER_ERROR = "SERVER_ERROR"
    NETWORK_ERROR = "NETWORK_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    UNKNOWN_ERROR = "UNKNOWN_ERROR"


@dataclass
class GifImage:
    """Represents a GIF image with dimensions and URL."""
    url: str
    width: int
    height: int
    size: int = 0


@dataclass
class GifData:
    """Complete GIF data from Giphy API."""
    id: str
    title: str
    url: str
    rating: str
    created_at: str
    tags: List[str]
    original: GifImage
    preview: GifImage
    thumbnail: GifImage


@dataclass
class PaginationData:
    """Pagination information for search results."""
    total: int
    count: int
    offset: int


@dataclass
class AdapterResponse:
    """Standardized response format for all adapter operations."""
    success: bool
    data: Optional[Union[List[GifData], GifData]]
    pagination: Optional[PaginationData] = None
    message: str = ""
    error: Optional[Dict[str, Any]] = None
