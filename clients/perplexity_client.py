import cloudscraper
import json
import aiohttp
from typing import Dict, Any, Optional


class PerplexityClient:
    def __init__(self) -> None:
        self.scraper = cloudscraper.create_scraper(
            browser={'custom': 'ReplitClient/1.0'}
        )
        self.base_url: str = "https://www.perplexity.ai/rest/discover/feed"

    def get_feed(self, limit: int = 20, offset: int = 0, 
                version: str = "2.18", topic: str = "top", 
                source: str = "default") -> Dict[str, Any]:
        url: str = (
            f"{self.base_url}"
            f"?limit={limit}&offset={offset}&version={version}"
            f"&topic={topic}&source={source}"
        )
        response = self.scraper.get(url)
        response.raise_for_status()
        return response.json()
        
    async def get_feed_async(self, limit: int = 20, offset: int = 0, 
                            version: str = "2.18", topic: str = "top", 
                            source: str = "default") -> Dict[str, Any]:
        url: str = (
            f"{self.base_url}"
            f"?limit={limit}&offset={offset}&version={version}"
            f"&topic={topic}&source={source}"
        )
        
        # For async operations, we need to use aiohttp
        # But since cloudscraper handles Cloudflare protection, we'll use it first
        # to get cookies and headers, then use those with aiohttp
        initial_response = self.scraper.get(url)
        cookies = initial_response.cookies
        headers = initial_response.headers
        
        # Now use aiohttp with the cookies and headers
        async with aiohttp.ClientSession() as session:
            async with session.get(url, cookies=cookies, headers=headers) as response:
                response.raise_for_status()
                return await response.json() 