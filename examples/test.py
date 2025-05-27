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
