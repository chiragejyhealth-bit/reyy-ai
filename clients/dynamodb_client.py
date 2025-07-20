import os
from typing import Dict, List, Optional, Any, cast

from clients.aws_base_client import AWSBaseClient

class DynamoDBClient(AWSBaseClient):
    def __init__(self) -> None:
        super().__init__()
        self.table_name = os.environ.get('DYNAMODB_TABLE_NAME', 'reyy-ai')
    
    async def put_item(self, item: Dict[str, Any]) -> bool:
        try:
            async with self.session.resource('dynamodb') as dynamodb:
                table = await dynamodb.Table(self.table_name)
                await table.put_item(Item=item)
                return True
                
        except Exception as e:
            print(f"Error putting item in DynamoDB: {e}")
            return False
    
    async def get_item(self, key: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            async with self.session.resource('dynamodb') as dynamodb:
                table = await dynamodb.Table(self.table_name)
                response = await table.get_item(Key=key)
                return cast(Optional[Dict[str, Any]], response.get('Item'))
                
        except Exception as e:
            print(f"Error getting item from DynamoDB: {e}")
            return None
    
    async def scan(self, limit: int = 100, created_at: Optional[str] = None) -> List[Dict[str, Any]]:
        try:
            async with self.session.resource('dynamodb') as dynamodb:
                table = await dynamodb.Table(self.table_name)
                scan_kwargs = {'Limit': limit}
                
                if created_at:
                    scan_kwargs.update({
                        'FilterExpression': '#created_at = :created_at',
                        'ExpressionAttributeValues': {':created_at': created_at},
                        'ExpressionAttributeNames': {'#created_at': 'created_at'}
                    })
                
                response = await table.scan(**scan_kwargs)
                return cast(List[Dict[str, Any]], response.get('Items', []))
                
        except Exception as e:
            print(f"Error scanning DynamoDB table: {e}")
            return []