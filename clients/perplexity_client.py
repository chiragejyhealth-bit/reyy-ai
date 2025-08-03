import asyncio
import json
from typing import Any, Dict, List

import undetected_chromedriver as uc
from models.perplexity import PerplexityFeedItem


class PerplexityClient:

    BASE_URL: str = "https://www.perplexity.ai/rest/discover/feed"

    async def get_feed(
        self,
        limit: int = 100,
        offset: int = 0,
        version: str = "2.18",
        topic: str = "top",
        source: str = "default",
    ) -> Dict[str, Any]:
        """Return the raw JSON response from the feed endpoint."""
        url = self._build_url(limit, offset, version, topic, source)
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self._selenium_fetch, url)

    async def get_feed_items(
        self,
        limit: int = 100,
        offset: int = 0,
        version: str = "2.18",
        topic: str = "top",
        source: str = "default",
    ) -> List[PerplexityFeedItem]:
        """Parse the feed into strongly-typed ``PerplexityFeedItem`` objects."""
        feed_json = await self.get_feed(limit, offset, version, topic, source)
        return [PerplexityFeedItem.from_json(json_data=i) for i in feed_json["items"]]

    # ------------------------------------------------------------------
    # Internals – all kept private to avoid leaking Selenium details
    # ------------------------------------------------------------------
    @staticmethod
    def _build_url(limit: int, offset: int, version: str, topic: str, source: str) -> str:
        """Compose the feed URL using the same query parameter scheme."""
        return (
            f"{PerplexityClient.BASE_URL}"
            f"?limit={limit}&offset={offset}&version={version}"
            f"&topic={topic}&source={source}"
        )

    def _create_driver(self) -> "uc.Chrome":
        """Spin up an undetected Chrome instance with sensible defaults."""
        options = uc.ChromeOptions()
        options.headless = False
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        return uc.Chrome(version_main=138, options=options)

    def _selenium_fetch(self, url: str) -> Dict[str, Any]:
        """Run inside a thread pool: launches Chrome, hits the endpoint & returns JSON."""
        driver = self._create_driver()
        try:
            # Initial page load ensures Cloudflare cookies are set.
            driver.get("https://www.perplexity.ai/")
            js = """
                return (async () => {
                    const response = await fetch(arguments[0], { credentials: 'include' });
                    return await response.text();
                })();
            """
            raw_result: str = driver.execute_script(js, url)

            try:
                return json.loads(raw_result)
            except json.JSONDecodeError:
                snippet = raw_result[:300].replace("\n", " ")
                raise RuntimeError(
                    f"Failed to parse Selenium response. First 300 chars: {snippet}"
                ) from None
        finally:
            driver.quit()


if __name__ == "__main__":
    client = PerplexityClient()  # Visible browser for CAPTCHA workaround
    raw_feed = asyncio.run(client.get_feed_items(limit=10))
    print(raw_feed)
