"""
High-level service layer for GIF operations.
"""

import logging
from typing import Optional, Dict, Any

from .adapter import GiphyAdapter
from .utils import extract_keywords

logger = logging.getLogger(__name__)


class GifService:
    """
    High-level service for GIF operations, designed for bot integration.
    """

    def __init__(self, giphy_api_key: str, **config):
        """
        Initialize GIF service.

        Args:
            giphy_api_key: Giphy API key
            **config: Configuration overrides for adapter
        """
        # Service-specific defaults
        service_config = {
            'limit': 5,
            'rating': 'pg',
            'timeout': 3.0,
            'retry_attempts': 2,
            **config
        }

        self.giphy_adapter = GiphyAdapter(giphy_api_key, **service_config)

    async def get_gif_for_message(self, user_message: str, **options) -> Optional[Dict[str, Any]]:
        """
        Get a GIF based on user message content.

        Args:
            user_message: User's message text
            **options: Additional search options

        Returns:
            Dict with GIF data or None if no suitable GIF found
        """
        if not user_message or not isinstance(user_message, str):
            logger.warning("Invalid user message provided")
            return None

        try:
            # Extract keywords from message for search
            query = extract_keywords(user_message)
            logger.debug(
                f"Extracted keywords: '{query}' from message: '{user_message}'")

            # Get random GIF based on keywords
            result = await self.giphy_adapter.get_random_gif(query, **options)

            if result.success and result.data:
                gif = result.data
                return {
                    'type': 'gif',
                    'id': gif.id,
                    'title': gif.title,
                    'url': gif.original.url,
                    'preview_url': gif.preview.url,
                    'thumbnail_url': gif.thumbnail.url,
                    'width': gif.original.width,
                    'height': gif.original.height,
                    'rating': gif.rating,
                    'query_used': query
                }

            logger.info(f"No GIF found for message: '{user_message}'")
            return None

        except Exception as error:
            logger.error(
                f"GIF service error for message '{user_message}': {error}")
            return None

    async def search_gifs(self, query: str, **options) -> Optional[Dict[str, Any]]:
        """
        Search for multiple GIFs with formatted response.

        Args:
            query: Search query
            **options: Search options

        Returns:
            Dict with search results or None on error
        """
        try:
            result = await self.giphy_adapter.search_gifs(query, **options)

            if result.success and result.data:
                return {
                    'query': query,
                    'total_results': result.pagination.total if result.pagination else 0,
                    'returned_count': len(result.data),
                    'gifs': [
                        {
                            'id': gif.id,
                            'title': gif.title,
                            'url': gif.original.url,
                            'preview_url': gif.preview.url,
                            'thumbnail_url': gif.thumbnail.url,
                            'width': gif.original.width,
                            'height': gif.original.height,
                            'rating': gif.rating
                        }
                        for gif in result.data
                    ]
                }

            return None

        except Exception as error:
            logger.error(f"Search error for query '{query}': {error}")
            return None

    async def health_check(self) -> Dict[str, Any]:
        """
        Check service health status.

        Returns:
            Dict with health status and service info
        """
        adapter_health = await self.giphy_adapter.health_check()

        return {
            'service': 'gif_service',
            'adapter_healthy': adapter_health.get('healthy', False),
            'timestamp': adapter_health.get('timestamp'),
            'details': adapter_health
        }

    async def close(self):
        """Close adapter connections and cleanup resources."""
        await self.giphy_adapter.close()
        logger.info("GIF service closed successfully")
