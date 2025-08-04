import asyncio
from datetime import datetime
import os
from typing import Dict, List, Optional, Any, cast

from clients.aws_base_client import AWSBaseClient
from models.perplexity import PerplexityFeedItem

class DynamoDBClient(AWSBaseClient):
    def __init__(self) -> None:
        super().__init__()
        self.table_name = os.environ.get('DYNAMODB_TABLE_NAME', 'reyy-ai')
    
    async def put_items(self, items: List[Dict[str, Any]]) -> int:
        try:
            async with self.session.resource('dynamodb') as dynamodb:
                table = await dynamodb.Table(self.table_name)
                
                # Filter out items that already exist
                new_items = []
                for item in items:
                    if 'uuid' not in item:
                        new_items.append(item)
                        continue
                        
                    existing_item = await self.get_item({'uuid': item['uuid']})
                    if not existing_item:
                        new_items.append(item)
                
                # Put each item individually since there's no batch put_items method
                for item in new_items:
                    await table.put_item(Item=item)
                return len(new_items)
                
        except Exception as e:
            print(f"Error putting item in DynamoDB: {e}")
            return 0
    
    async def get_item(self, key: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            async with self.session.resource('dynamodb') as dynamodb:
                table = await dynamodb.Table(self.table_name)
                response = await table.get_item(Key=key)
                return cast(Optional[Dict[str, Any]], response.get('Item'))
                
        except Exception as e:
            print(f"Error getting item from DynamoDB: {e}")
            return None

    async def scan(
            self,
            limit: int = 100,
            *,
            blank_s3_only: bool = False,
            last_query_datetime: Optional[datetime] = None,
    ) -> List[PerplexityFeedItem]:

        try:
            async with self.session.resource("dynamodb") as dynamodb:
                table = await dynamodb.Table(self.table_name)

                filters: list[str] = []
                names: dict[str, str] = {}
                values: dict[str, str] = {}

                if last_query_datetime:
                    filters.append("#last_dt > :last_dt")
                    names["#last_dt"] = "last_query_datetime"
                    values[":last_dt"] = last_query_datetime.isoformat()

                if blank_s3_only:
                    filters.append("attribute_not_exists(#s3) OR #s3 = :empty")
                    names["#s3"] = "s3_url"
                    values[":empty"] = ""

                base_kwargs: dict = {}
                if filters:
                    base_kwargs["FilterExpression"] = " AND ".join(filters)
                if names:
                    base_kwargs["ExpressionAttributeNames"] = names
                if values:
                    base_kwargs["ExpressionAttributeValues"] = values

                # ── paginated scan ─────────────────────────────────
                items: list = []
                start_key = None

                while len(items) < limit:
                    page_limit = min(1000, limit - len(items))  # 1 MB ≈ ~1 000 rows
                    kwargs = {"Limit": page_limit, **base_kwargs}
                    if start_key:
                        kwargs["ExclusiveStartKey"] = start_key

                    resp = await table.scan(**kwargs)
                    items.extend(resp.get("Items", []))

                    start_key = resp.get("LastEvaluatedKey")
                    if not start_key:
                        break

                return [PerplexityFeedItem(**item) for item in items[:limit]]

        except Exception:
            raise

    async def update_item(self, key: Dict[str, Any], s3_url: str) -> None:
        try:
            async with self.session.resource('dynamodb') as dynamodb:
                table = await dynamodb.Table(self.table_name)
                await table.update_item(Key=key, UpdateExpression='SET s3_url = :s3_url, last_query_datetime = :last_query_datetime',\
                            ExpressionAttributeValues={':s3_url': s3_url, ':last_query_datetime': datetime.now().isoformat()})
        except Exception as e:
            print(f"Error updating item in DynamoDB: {e}")
            return None

if __name__ == "__main__":
    from container import ServicesContainer
    client = ServicesContainer().dynamodb_client()
    print(len(asyncio.run(client.scan(limit=10,blank_s3_only= True))))