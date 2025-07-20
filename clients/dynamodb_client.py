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
    
    async def scan(self, limit: int = 100, last_query_datetime: Optional[datetime] = None) -> List[PerplexityFeedItem]:
        try:
            async with self.session.resource('dynamodb') as dynamodb:
                table = await dynamodb.Table(self.table_name)
                scan_kwargs = {'Limit': limit}
                
                if last_query_datetime:
                    scan_kwargs.update({
                        'FilterExpression': '#last_query_datetime > :last_query_datetime',
                        'ExpressionAttributeValues': {':last_query_datetime': last_query_datetime.isoformat()},
                        'ExpressionAttributeNames': {'#last_query_datetime': 'last_query_datetime'}
                    })
                
                response = await table.scan(**scan_kwargs)
                return cast(List[PerplexityFeedItem], [PerplexityFeedItem.from_json(item) for item in response.get('Items', [])])
                
        except Exception as e:
            print(f"Error scanning DynamoDB table: {e}")
            return []
        
    async def update_item(self, key: Dict[str, Any], s3_url: str) -> None:
        try:
            async with self.session.resource('dynamodb') as dynamodb:
                table = await dynamodb.Table(self.table_name)
                await table.update_item(Key=key, UpdateExpression='SET s3_url = :s3_url, last_query_datetime = :last_query_datetime',\
                            ExpressionAttributeValues={':s3_url': s3_url, ':last_query_datetime': datetime.now().isoformat()})
        except Exception as e:
            print(f"Error updating item in DynamoDB: {e}")
            return None