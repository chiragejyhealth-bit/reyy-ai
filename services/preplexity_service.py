from typing import List, Dict, Any, Tuple
from clients.dynamodb_client import DynamoDBClient
from clients.perplexity_client import PerplexityClient
from models.perplexity import PerplexityFeedItem


class PerplexityService:
    def __init__(self, perplexity_client: PerplexityClient, dynamo_db_client: DynamoDBClient):
        self.perplexity_client = perplexity_client
        self.dynamo_db_client = dynamo_db_client

    async def get_and_save_feed(self, limit: int = 20, offset: int = 0) -> Tuple[int, List[PerplexityFeedItem]]:
        feed_items : List[PerplexityFeedItem] = await self.perplexity_client.get_feed_items(limit, offset)
        num_items_saved = await self.dynamo_db_client.put_items([item.model_dump() for item in feed_items])
        return num_items_saved, feed_items
    
