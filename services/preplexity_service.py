import logging
from typing import List, Tuple
from langsmith import traceable
from clients.dynamodb_client import DynamoDBClient
from clients.perplexity_client import PerplexityClient
from models.perplexity import PerplexityFeedItem
logging.basicConfig(level=logging.INFO)

class PerplexityService:
    def __init__(self, perplexity_client: PerplexityClient, dynamo_db_client: DynamoDBClient):
        self.perplexity_client = perplexity_client
        self.dynamo_db_client = dynamo_db_client

    @traceable(name="get_and_save_feed")
    async def get_and_save_feed(self, limit: int = 20, offset: int = 0) -> Tuple[int, List[PerplexityFeedItem]]:
        logging.info(f"Getting feed items from Perplexity with limit: {limit}, offset: {offset}")
        feed_items : List[PerplexityFeedItem] = await self.perplexity_client.get_feed_items(limit, offset)
        logging.info(f"Received {len(feed_items)} feed items from Perplexity")
        num_items_saved = await self.dynamo_db_client.put_items([item.model_dump() for item in feed_items])
        logging.info(f"Saved {num_items_saved} feed items to DynamoDB")
        return num_items_saved, feed_items
    
