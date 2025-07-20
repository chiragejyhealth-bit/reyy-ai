import asyncio
import cloudscraper
import json
import os
from typing import Dict, Any, List

from models.perplexity import PerplexityFeedItem


class PerplexityClient:
    def __init__(self) -> None:
        self.scraper = cloudscraper.create_scraper(
            browser={'custom': 'ReplitClient/1.0'}
        )
        self.base_url: str = "https://www.perplexity.ai/rest/discover/feed"
        
    async def get_feed(self, limit: int = 100, offset: int = 0, 
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
    
    async def get_feed_items(self, limit: int = 100, offset: int = 0,
                     version: str = "2.18", topic: str = "top",
                     source: str = "default") -> List[PerplexityFeedItem]:
        
        feed_json : Dict[str, Any] = await self.get_feed(limit, offset, version, topic, source)
        return [PerplexityFeedItem.from_json(item) for item in feed_json["items"]]

if __name__ == "__main__":
    client = PerplexityClient()
    feed = asyncio.run(client.get_feed())
    
    # Create response folder if it doesn't exist
    os.makedirs("response", exist_ok=True)
    
    # Save feed to response folder
    with open("response/feed.json", "w") as f:
        json.dump(feed, f, indent=2)