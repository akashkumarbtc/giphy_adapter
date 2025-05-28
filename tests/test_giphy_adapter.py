"""
Test cases for Giphy Adapter modules.
"""

import pytest
import asyncio
import aiohttp
from unittest.mock import Mock, patch, AsyncMock

# Import with error handling for different project structures
try:
    from giphy_adapter import GiphyAdapter, GifService, GiphyError, GiphyTimeout, GiphyValidation
    from giphy_adapter.models import GifData, GifImage, PaginationData, AdapterResponse
    from giphy_adapter.utils import extract_keywords, validate_search_params
except ImportError:
    from giphy_adapter.adapter import GiphyAdapter
    from giphy_adapter.service import GifService
    from giphy_adapter.exceptions import GiphyError, GiphyTimeout, GiphyValidation
    from giphy_adapter.models import GifData, GifImage, PaginationData, AdapterResponse
    from giphy_adapter.utils import extract_keywords, validate_search_params


# Configure pytest for async tests
pytest_plugins = ('pytest_asyncio',)


class TestGiphyAdapter:
    """Test cases for GiphyAdapter class."""

    @pytest.mark.asyncio
    async def test_search_gifs_success(self):
        """Test successful GIF search with mocked API response."""
        adapter = GiphyAdapter("test_api_key", timeout=1.0, retry_attempts=1)

        # Mock response data
        mock_response_data = {
            'data': [
                {
                    "id": "test123",
                    "title": "Test GIF",
                    "url": "https://giphy.com/gifs/test123",
                    "rating": "pg",
                    "import_datetime": "2024-01-01 12:00:00",
                    "tags": ["test", "funny"],
                    "images": {
                        "original": {
                            "url": "https://media.giphy.com/test.gif",
                            "width": "480",
                            "height": "270",
                            "size": "1000000"
                        },
                        "fixed_height_small": {
                            "url": "https://media.giphy.com/test_small.gif",
                            "width": "200",
                            "height": "113"
                        },
                        "fixed_height_small_still": {
                            "url": "https://media.giphy.com/test_thumb.gif",
                            "width": "200",
                            "height": "113"
                        }
                    }
                }
            ],
            'pagination': {
                'total_count': 100,
                'count': 1,
                'offset': 0
            },
            'meta': {'status': 200}
        }

        try:
            # Mock the _make_request method
            with patch.object(adapter, '_make_request', return_value=mock_response_data):
                result = await adapter.search_gifs("funny cats")

                assert result.success is True
                assert len(result.data) == 1
                assert result.data[0].id == "test123"
                assert result.data[0].title == "Test GIF"
                assert result.pagination.total == 100
        finally:
            await adapter.close()

    @pytest.mark.asyncio
    async def test_search_gifs_validation_error(self):
        """Test search with invalid parameters."""
        adapter = GiphyAdapter("test_api_key", timeout=1.0, retry_attempts=1)

        try:
            # Empty query should raise GiphyValidation exception
            with pytest.raises(GiphyValidation, match="Query parameter is required"):
                await adapter.search_gifs("")

            # Non-string query should raise GiphyValidation exception
            with pytest.raises(GiphyValidation, match="Query parameter is required"):
                await adapter.search_gifs(123)

        finally:
            await adapter.close()


class TestGifService:
    """Test cases for GifService class."""

    @pytest.mark.asyncio
    async def test_get_gif_for_message_success(self):
        """Test getting GIF for user message."""
        service = GifService("test_api_key")

        # Mock adapter response
        mock_gif = GifData(
            id="msg123",
            title="Happy GIF",
            url="https://giphy.com/gifs/msg123",
            rating="pg",
            created_at="2024-01-01",
            tags=["happy"],
            original=GifImage(
                "https://media.giphy.com/happy.gif", 480, 270, 1000000),
            preview=GifImage(
                "https://media.giphy.com/happy_small.gif", 200, 113),
            thumbnail=GifImage(
                "https://media.giphy.com/happy_thumb.gif", 200, 113)
        )

        mock_response = AdapterResponse(
            success=True,
            data=mock_gif,
            message="GIF found"
        )

        try:
            with patch.object(service.giphy_adapter, 'get_random_gif', return_value=mock_response):
                result = await service.get_gif_for_message("I'm so happy today!")

                assert result is not None
                assert result['type'] == 'gif'
                assert result['id'] == 'msg123'
                assert result['title'] == 'Happy GIF'
                assert 'query_used' in result
        finally:
            await service.close()

    @pytest.mark.asyncio
    async def test_get_gif_for_message_no_result(self):
        """Test getting GIF when no results found."""
        service = GifService("test_api_key")

        mock_response = AdapterResponse(
            success=True,
            data=None,
            message="No GIF found"
        )

        try:
            with patch.object(service.giphy_adapter, 'get_random_gif', return_value=mock_response):
                result = await service.get_gif_for_message("obscure random text")
                assert result is None
        finally:
            await service.close()

    @pytest.mark.asyncio
    async def test_get_gif_for_message_invalid_input(self):
        """Test getting GIF with invalid input."""
        service = GifService("test_api_key")

        try:
            # Test with None input
            result = await service.get_gif_for_message(None)
            assert result is None

            # Test with non-string input
            result = await service.get_gif_for_message(123)
            assert result is None

            # Test with empty string
            result = await service.get_gif_for_message("")
            assert result is None
        finally:
            await service.close()

    @pytest.mark.asyncio
    async def test_search_gifs_success(self):
        """Test search GIFs functionality."""
        service = GifService("test_api_key")

        # Mock adapter response
        mock_gifs = [
            GifData(
                id="search123",
                title="Search Result GIF",
                url="https://giphy.com/gifs/search123",
                rating="pg",
                created_at="2024-01-01",
                tags=["search"],
                original=GifImage(
                    "https://media.giphy.com/search.gif", 480, 270, 1000000),
                preview=GifImage(
                    "https://media.giphy.com/search_small.gif", 200, 113),
                thumbnail=GifImage(
                    "https://media.giphy.com/search_thumb.gif", 200, 113)
            )
        ]

        mock_pagination = PaginationData(total=10, count=1, offset=0)
        mock_response = AdapterResponse(
            success=True,
            data=mock_gifs,
            pagination=mock_pagination,
            message="Search successful"
        )

        try:
            with patch.object(service.giphy_adapter, 'search_gifs', return_value=mock_response):
                result = await service.search_gifs("funny cats")

                assert result is not None
                assert result['query'] == "funny cats"
                assert result['total_results'] == 10
                assert result['returned_count'] == 1
                assert len(result['gifs']) == 1
                assert result['gifs'][0]['id'] == 'search123'
        finally:
            await service.close()

    @pytest.mark.asyncio
    async def test_health_check(self):
        """Test service health check."""
        service = GifService("test_api_key")

        mock_adapter_health = {
            'healthy': True,
            'timestamp': 1640995200.0,
            'service': 'giphy'
        }

        try:
            with patch.object(service.giphy_adapter, 'health_check', return_value=mock_adapter_health):
                health = await service.health_check()

                assert health['service'] == 'gif_service'
                assert health['adapter_healthy'] is True
                assert 'timestamp' in health
                assert 'details' in health
        finally:
            await service.close()


class TestUtils:
    """Test cases for utility functions."""

    def test_extract_keywords(self):
        """Test keyword extraction from messages."""
        # Normal message
        result = extract_keywords("I love funny cats and dogs")
        # Should extract meaningful words, filtering out stop words
        assert len(result.split()) <= 3
        assert "love" in result or "funny" in result
        assert "cats" in result or "dogs" in result

        # Message with stop words only
        result = extract_keywords("The quick brown fox jumps")
        expected_words = ["quick", "brown", "fox", "jumps"]
        result_words = result.split()
        assert len(result_words) <= 3
        assert all(word in expected_words for word in result_words)

        # Short message (less than 3 characters)
        result = extract_keywords("hi")
        assert result == "hi"

        # Empty message
        result = extract_keywords("")
        assert result == ""

        # Message with only stop words
        result = extract_keywords("the and or")
        assert result == "the and or"  # Should return original if no keywords found

    def test_validate_search_params(self):
        """Test search parameter validation."""
        # Valid parameters
        validate_search_params(limit=10, offset=0, rating='pg')

        # Invalid limit - too low
        with pytest.raises(ValueError, match="Limit must be"):
            validate_search_params(limit=0)

        # Invalid limit - too high
        with pytest.raises(ValueError, match="Limit must be"):
            validate_search_params(limit=100)

        # Invalid limit - not integer
        with pytest.raises(ValueError, match="Limit must be"):
            validate_search_params(limit="10")

        # Invalid offset
        with pytest.raises(ValueError, match="Offset must be"):
            validate_search_params(offset=-1)

        # Invalid offset - not integer
        with pytest.raises(ValueError, match="Offset must be"):
            validate_search_params(offset="0")

        # Invalid rating
        with pytest.raises(ValueError, match="Rating must be"):
            validate_search_params(rating='invalid')

        # Test edge cases
        # Minimum valid limit
        validate_search_params(limit=1, offset=0, rating='g')
        validate_search_params(limit=50, offset=1000,
                               rating='r')  # Maximum valid limit


class TestExceptions:
    """Test cases for custom exceptions."""

    def test_giphy_error(self):
        """Test base GiphyError exception."""
        error = GiphyError("Test error", "TEST_TYPE")
        assert str(error) == "Test error"
        assert error.error_type == "TEST_TYPE"
        assert error.message == "Test error"

        # Test default error type
        error_default = GiphyError("Default error")
        assert error_default.error_type == "UNKNOWN_ERROR"

    def test_giphy_timeout(self):
        """Test GiphyTimeout exception."""
        timeout = GiphyTimeout("Custom timeout message")
        assert str(timeout) == "Custom timeout message"
        assert timeout.error_type == "TIMEOUT"

        # Default message
        timeout_default = GiphyTimeout()
        assert str(timeout_default) == "Request timeout"
        assert timeout_default.error_type == "TIMEOUT"

    def test_giphy_validation(self):
        """Test GiphyValidation exception."""
        validation = GiphyValidation("Invalid input")
        assert str(validation) == "Invalid input"
        assert validation.error_type == "VALIDATION_ERROR"


class TestModels:
    """Test cases for data models."""

    def test_gif_image_creation(self):
        """Test GifImage dataclass creation."""
        gif_image = GifImage(
            url="https://example.com/test.gif",
            width=480,
            height=270,
            size=1000000
        )
        assert gif_image.url == "https://example.com/test.gif"
        assert gif_image.width == 480
        assert gif_image.height == 270
        assert gif_image.size == 1000000

        # Test with default size
        gif_image_default = GifImage(
            url="https://example.com/test.gif",
            width=480,
            height=270
        )
        assert gif_image_default.size == 0

    def test_pagination_data_creation(self):
        """Test PaginationData dataclass creation."""
        pagination = PaginationData(total=100, count=10, offset=0)
        assert pagination.total == 100
        assert pagination.count == 10
        assert pagination.offset == 0

    def test_adapter_response_creation(self):
        """Test AdapterResponse dataclass creation."""
        # Success response
        response = AdapterResponse(
            success=True, data=["test"], message="Success")
        assert response.success is True
        assert response.data == ["test"]
        assert response.message == "Success"
        assert response.pagination is None
        assert response.error is None

        # Error response
        error_response = AdapterResponse(
            success=False,
            data=None,
            error={"type": "TEST_ERROR", "message": "Test error"}
        )
        assert error_response.success is False
        assert error_response.data is None
        assert error_response.error["type"] == "TEST_ERROR"


# Integration test
class TestIntegration:
    """Integration test with mocked HTTP responses."""

    @pytest.mark.asyncio
    async def test_end_to_end_gif_search(self):
        """Test complete flow from service to adapter."""
        service = GifService("test_key", limit=1, timeout=1.0)

        # Mock HTTP response
        mock_http_response = {
            'data': [{
                "id": "integration123",
                "title": "Integration Test GIF",
                "url": "https://giphy.com/gifs/integration123",
                "rating": "g",
                "import_datetime": "2024-01-01 00:00:00",
                "tags": ["test"],
                "images": {
                    "original": {
                        "url": "https://media.giphy.com/integration.gif",
                        "width": "400",
                        "height": "300",
                        "size": "500000"
                    },
                    "fixed_height_small": {
                        "url": "https://media.giphy.com/integration_small.gif",
                        "width": "150",
                        "height": "100"
                    },
                    "fixed_height_small_still": {
                        "url": "https://media.giphy.com/integration_thumb.gif",
                        "width": "150",
                        "height": "100"
                    }
                }
            }],
            'pagination': {'total_count': 1, 'count': 1, 'offset': 0},
            'meta': {'status': 200}
        }

        try:
            with patch.object(service.giphy_adapter, '_make_request', return_value=mock_http_response):
                result = await service.get_gif_for_message("testing integration")

                assert result is not None
                assert result['id'] == "integration123"
                assert result['type'] == 'gif'
                assert result['width'] == 400
                assert result['height'] == 300
                assert 'query_used' in result
        finally:
            await service.close()

    @pytest.mark.asyncio
    async def test_error_handling_flow(self):
        """Test error handling throughout the stack."""
        service = GifService("test_key", timeout=0.1, retry_attempts=1)

        try:
            # Mock network error
            with patch.object(service.giphy_adapter, '_make_request', side_effect=aiohttp.ClientError("Network error")):
                result = await service.get_gif_for_message("test message")
                # Service should handle the error gracefully and return None
                assert result is None
        finally:
            await service.close()


# Fixture for cleanup
@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


if __name__ == "__main__":
    # Run tests with: python -m pytest test_giphy_adapter.py -v
    pytest.main([__file__, "-v", "--tb=short"])
