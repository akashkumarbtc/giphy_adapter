# Giphy Adapter

A production-ready, async Python adapter for the Giphy API with built-in error handling, retry logic, and connection pooling.

## Features

- **Async/Await Support**: Built with `aiohttp` for high-performance async operations
- **Connection Pooling**: Efficient connection management for scalable applications
- **Retry Logic**: Configurable retry attempts with exponential backoff
- **Error Handling**: Comprehensive error categorization and handling
- **Type Safety**: Full type hints and dataclass models
- **Production Ready**: Logging, health checks, and proper resource cleanup

## Installation

```bash
pip install -r requirements.txt
```

## Install the package in development mode

```bash
pip install -e .
```

## Quick Start

```python
import asyncio
from giphy_adapter import GifService


async def main():
    # Initialize the service with your Giphy API key
    gif_service = GifService(giphy_api_key="key here")

    try:
        # Search for GIFs
        result = await gif_service.search_gifs("happy cat", limit=5)
        print("Raw result:", result)
        print("-" * 50)

        # Check if result has gifs and process them
        if result and 'gifs' in result and result['gifs']:
            print(f"Query: {result['query']}")
            print(f"Total results: {result['total_results']}")
            print(f"Returned count: {result['returned_count']}")
            print("-" * 30)

            for gif in result['gifs']:
                print(f"Title: {gif['title']}")
                print(f"URL: {gif['url']}")
                print(f"Preview: {gif['preview_url']}")
                print(f"Dimensions: {gif['width']}x{gif['height']}")
                print(f"Rating: {gif['rating']}")
                print("-" * 20)
        else:
            print("No GIFs found or invalid result structure")

        # Get a single random GIF
        print("Getting GIF for message...")
        gif = await gif_service.get_gif_for_message("I'm excited!")
        if gif:
            print(f"Found GIF: {gif.get('title', 'No title')}")
            print(f"URL: {gif.get('url', 'No URL')}")
        else:
            print("No GIF found for message")

    except Exception as e:
        print(f"Error occurred: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Always close the service to cleanup resources
        await gif_service.close()

if __name__ == "__main__":
    asyncio.run(main())

```

## Configuration Options

```python
from giphy_adapter import GiphyAdapter

adapter = GiphyAdapter(
    api_key="your_api_key",
    limit=10,                    # Default number of results
    rating='pg',                 # Content rating (g, pg, pg-13, r)
    lang='en',                   # Language
    timeout=5.0,                 # Request timeout in seconds
    retry_attempts=3,            # Number of retry attempts
    retry_delay=1.0,            # Base delay between retries
    max_concurrent_requests=100  # Connection pool size
)
```

## API Reference

### GifService

High-level service for GIF operations.

#### Methods

- `search_gifs(query, **options)` - Search for GIFs by query
- `get_random_gif(query, **options)` - Get a single random GIF
- `get_gif_for_message(message)` - Extract keywords and find relevant GIF
- `health_check()` - Check API connectivity
- `close()` - Cleanup resources

### GiphyAdapter

Low-level adapter for direct Giphy API access.

## Error Handling

The adapter categorizes errors into types:

- `TIMEOUT` - Request timeouts
- `CLIENT_ERROR` - 4xx HTTP errors
- `SERVER_ERROR` - 5xx HTTP errors
- `NETWORK_ERROR` - Connection issues
- `VALIDATION_ERROR` - Invalid parameters
- `UNKNOWN_ERROR` - Unexpected errors

```python
result = await gif_service.search_gifs("cats")
if not result.success:
    error_type = result.error['type']
    error_message = result.error['message']
    print(f"Error ({error_type}): {error_message}")
```

## Environment Variables

Set your Giphy API key as an environment variable:

```bash
export GIPHY_API_KEY="your_api_key_here"
```

## Testing

Run the test suite:

```bash
pytest tests/ -v
```

Run with coverage:

```bash
pytest tests/ --cov=giphy_adapter --cov-report=html
```

## Examples

See the `examples/` directory for more usage examples.

```bash
python -m examples.test
```

## Requirements

- Python 3.7+
- aiohttp
- typing-extensions (for Python < 3.8)

## License

MIT License

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request
