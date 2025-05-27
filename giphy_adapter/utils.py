"""
Utility functions for text processing and validation.
"""

from typing import Set


def extract_keywords(message: str, max_keywords: int = 3) -> str:
    """
    Extract relevant keywords from user message for GIF search.

    Args:
        message: Input text message
        max_keywords: Maximum number of keywords to return

    Returns:
        Space-separated string of keywords
    """
    # Common stop words to filter out
    stop_words: Set[str] = {
        'the', 'is', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at',
        'to', 'for', 'of', 'with', 'by', 'this', 'that', 'these', 'those',
        'i', 'me', 'my', 'you', 'your', 'he', 'she', 'it', 'we', 'they'
    }

    # Clean and tokenize message
    words = message.lower().strip().split()

    # Filter out stop words and short words
    keywords = [
        word for word in words
        if len(word) > 2 and word not in stop_words
    ]

    # Return up to max_keywords or original message if no keywords found
    if keywords:
        return ' '.join(keywords[:max_keywords])

    return message.strip()


def validate_search_params(**params) -> None:
    """
    Validate search parameters for Giphy API.

    Raises:
        ValueError: If parameters are invalid
    """
    limit = params.get('limit', 10)
    offset = params.get('offset', 0)

    if not isinstance(limit, int) or limit < 1 or limit > 50:
        raise ValueError("Limit must be an integer between 1 and 50")

    if not isinstance(offset, int) or offset < 0:
        raise ValueError("Offset must be a non-negative integer")

    rating = params.get('rating', 'pg')
    valid_ratings = {'g', 'pg', 'pg-13', 'r'}
    if rating not in valid_ratings:
        raise ValueError(f"Rating must be one of: {', '.join(valid_ratings)}")
