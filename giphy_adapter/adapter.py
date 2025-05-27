"""
Core Giphy API adapter with async HTTP client and error handling.
"""

import asyncio
import aiohttp
import logging
import time
from typing import Dict, Optional, Any

from .models import GifData, GifImage, PaginationData, AdapterResponse, ErrorType
from .exceptions import GiphyError, GiphyTimeout, GiphyValidation
from .utils import validate_search_params

logger = logging.getLogger(__name__)


class GiphyAdapter:
    """
    Async adapter for Giphy API with connection pooling and retry logic.
    """

    def __init__(self, api_key: str, **options):
        """
        Initialize Giphy adapter.

        Args:
            api_key: Giphy API key
            **options: Configuration overrides
        """
        if not api_key:
            raise GiphyValidation("API key is required")

        self.api_key = api_key
        self.base_url = "https://api.giphy.com/v1/gifs"

        # Default configuration
        self.config = {
            'limit': 10,
            'rating': 'pg',
            'lang': 'en',
            'timeout': 5.0,
            'retry_attempts': 3,
            'retry_delay': 1.0,
            'max_concurrent_requests': 100,
            **options
        }

        # HTTP client setup
        self.connector = aiohttp.TCPConnector(
            limit=self.config['max_concurrent_requests'],
            limit_per_host=20,
            ttl_dns_cache=300,
            use_dns_cache=True
        )
        self._session = None

    async def search_gifs(self, query: str, **options) -> AdapterResponse:
        """
        Search for GIFs based on text query.

        Args:
            query: Search text
            **options: Search parameters (limit, offset, rating, lang)

        Returns:
            AdapterResponse with list of GifData objects
        """
        if not query or not isinstance(query, str):
            raise GiphyValidation(
                "Query parameter is required and must be a string")

        # Prepare search parameters
        search_params = {
            'q': query.strip(),
            'limit': min(options.get('limit', self.config['limit']), 50),
            'offset': options.get('offset', 0),
            'rating': options.get('rating', self.config['rating']),
            'lang': options.get('lang', self.config['lang'])
        }

        # Validate parameters
        validate_search_params(**search_params)

        try:
            response_data = await self._make_request('/search', search_params)
            return self._transform_response(response_data)
        except Exception as error:
            return self._handle_error(error, 'search_gifs')

    async def get_random_gif(self, query: str, **options) -> AdapterResponse:
        """
        Get a single random GIF based on text query.

        Args:
            query: Search text
            **options: Search options

        Returns:
            AdapterResponse with single GifData object
        """
        search_options = {**options, 'limit': 1, 'offset': 0}
        result = await self.search_gifs(query, **search_options)

        if result.success and result.data:
            return AdapterResponse(
                success=True,
                data=result.data[0] if isinstance(
                    result.data, list) else result.data,
                message='GIF found'
            )

        return AdapterResponse(
            success=True,
            data=None,
            message='No GIF found for query'
        )

    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on Giphy API connection.

        Returns:
            Dict with health status and metadata
        """
        try:
            await self._make_request('/search', {'q': 'test', 'limit': 1})
            return {
                'healthy': True,
                'timestamp': time.time(),
                'service': 'giphy'
            }
        except Exception as error:
            return {
                'healthy': False,
                'error': str(error),
                'timestamp': time.time(),
                'service': 'giphy'
            }

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session with proper configuration."""
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=self.config['timeout'])
            headers = {
                'Accept': 'application/json',
                'User-Agent': 'Luzia-Bot/1.0'
            }
            self._session = aiohttp.ClientSession(
                connector=self.connector,
                timeout=timeout,
                headers=headers
            )
        return self._session

    async def _make_request(self, endpoint: str, params: Dict) -> Dict:
        """
        Make HTTP request to Giphy API with retry logic.

        Args:
            endpoint: API endpoint path
            params: Request parameters

        Returns:
            JSON response data

        Raises:
            GiphyError: On API or network errors
        """
        url = f"{self.base_url}{endpoint}"
        params['api_key'] = self.api_key

        last_error = None

        for attempt in range(1, self.config['retry_attempts'] + 1):
            try:
                session = await self._get_session()

                async with session.get(url, params=params) as response:
                    if response.status != 200:
                        raise aiohttp.ClientResponseError(
                            request_info=response.request_info,
                            history=response.history,
                            status=response.status,
                            message=f"HTTP {response.status}: {response.reason}"
                        )

                    data = await response.json()

                    # Check Giphy API status
                    if data.get('meta', {}).get('status') != 200:
                        raise GiphyError(
                            f"Giphy API Error: {data.get('meta', {}).get('msg', 'Unknown error')}"
                        )

                    return data

            except asyncio.TimeoutError:
                last_error = GiphyTimeout("Request timeout")
                logger.warning(
                    f"Timeout on attempt {attempt}/{self.config['retry_attempts']}")

            except aiohttp.ClientError as error:
                last_error = GiphyError(f"Client error: {error}")
                logger.warning(f"Client error on attempt {attempt}: {error}")

            except Exception as error:
                last_error = error
                logger.error(f"Unexpected error on attempt {attempt}: {error}")

            # Wait before retry (exponential backoff)
            if attempt < self.config['retry_attempts']:
                await asyncio.sleep(self.config['retry_delay'] * attempt)

        raise last_error

    def _transform_response(self, giphy_response: Dict) -> AdapterResponse:
        """
        Transform Giphy API response to standardized format.

        Args:
            giphy_response: Raw Giphy API response

        Returns:
            AdapterResponse with transformed data
        """
        gifs = []

        for gif_data in giphy_response.get('data', []):
            try:
                images = gif_data.get('images', {})

                gif = GifData(
                    id=gif_data.get('id', ''),
                    title=gif_data.get('title', ''),
                    url=gif_data.get('url', ''),
                    rating=gif_data.get('rating', ''),
                    created_at=gif_data.get('import_datetime', ''),
                    tags=gif_data.get('tags', []),
                    original=GifImage(
                        url=images.get('original', {}).get('url', ''),
                        width=int(images.get('original', {}).get('width', 0)),
                        height=int(images.get(
                            'original', {}).get('height', 0)),
                        size=int(images.get('original', {}).get('size', 0))
                    ),
                    preview=GifImage(
                        url=images.get('fixed_height_small',
                                       {}).get('url', ''),
                        width=int(images.get(
                            'fixed_height_small', {}).get('width', 0)),
                        height=int(images.get(
                            'fixed_height_small', {}).get('height', 0))
                    ),
                    thumbnail=GifImage(
                        url=images.get(
                            'fixed_height_small_still', {}).get('url', ''),
                        width=int(images.get(
                            'fixed_height_small_still', {}).get('width', 0)),
                        height=int(images.get(
                            'fixed_height_small_still', {}).get('height', 0))
                    )
                )
                gifs.append(gif)

            except (ValueError, KeyError) as e:
                logger.warning(f"Error parsing GIF data: {e}")
                continue

        # Extract pagination info
        pagination_data = giphy_response.get('pagination', {})
        pagination = PaginationData(
            total=pagination_data.get('total_count', 0),
            count=pagination_data.get('count', 0),
            offset=pagination_data.get('offset', 0)
        )

        return AdapterResponse(
            success=True,
            data=gifs,
            pagination=pagination,
            message=f"Found {len(gifs)} GIFs"
        )

    def _handle_error(self, error: Exception, method: str) -> AdapterResponse:
        """
        Handle and categorize errors for consistent error responses.

        Args:
            error: The exception that occurred
            method: Method name where error occurred

        Returns:
            AdapterResponse with error details
        """
        error_type = ErrorType.UNKNOWN_ERROR
        error_message = str(error)

        if isinstance(error, GiphyTimeout):
            error_type = ErrorType.TIMEOUT
        elif isinstance(error, GiphyValidation):
            error_type = ErrorType.VALIDATION_ERROR
        elif isinstance(error, aiohttp.ClientResponseError):
            if 400 <= error.status < 500:
                error_type = ErrorType.CLIENT_ERROR
            elif 500 <= error.status < 600:
                error_type = ErrorType.SERVER_ERROR
        elif isinstance(error, aiohttp.ClientError):
            error_type = ErrorType.NETWORK_ERROR

        logger.error(f"Error in {method}: {error_message}")

        return AdapterResponse(
            success=False,
            data=None,
            error={
                'type': error_type.value,
                'message': error_message,
                'method': method,
                'timestamp': time.time()
            }
        )

    async def close(self):
        """Close HTTP session and connector."""
        if self._session and not self._session.closed:
            await self._session.close()
        if self.connector:
            await self.connector.close()
