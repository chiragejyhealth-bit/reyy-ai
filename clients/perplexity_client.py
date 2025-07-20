import asyncio
import cloudscraper
from typing import Dict, Any


class PerplexityClient:
    def __init__(self) -> None:
        self.scraper = cloudscraper.create_scraper(
            browser={'custom': 'ReplitClient/1.0'}
        )
        self.base_url: str = "https://www.perplexity.ai/rest/discover/feed"
        
    async def get_feed(self, limit: int = 20, offset: int = 0, 
                version: str = "2.18", topic: str = "top", 
                source: str = "default") -> Dict[str, Any]:
        url: str = (
            f"{self.base_url}"
            f"?limit={limit}&offset={offset}&version={version}"
            f"&topic={topic}&source={source}"
        )
        # Run synchronous request in a thread pool
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, self.scraper.get, url)
        response.raise_for_status()
        return response.json()

if __name__ == "__main__":
    client = PerplexityClient()
    print(asyncio.run(client.get_feed()))