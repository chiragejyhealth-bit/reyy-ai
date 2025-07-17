import os
from typing import Dict, List, Optional, Any, cast

from clients.aws_base_client import AWSBaseClient


class DynamoDBClient(AWSBaseClient):
    def __init__(self) -> None:
        super().__init__()
        self.table_cache: Dict[str, Any] = {}
    
    async def create_table(self, table_name: str, 
                          read_capacity_units: int = 5, 
                          write_capacity_units: int = 5) -> Any:
        if not self.is_configured():
            raise ValueError("AWS DynamoDB credentials not configured in environment variables")
            
        async with self.session.resource('dynamodb') as dynamodb:
            # Check if table exists
            existing_tables: List[str] = await dynamodb.meta.client.list_tables()
            existing_tables = cast(List[str], existing_tables.get('TableNames', []))
            
            if table_name not in existing_tables:
                # Create the table
                table = await dynamodb.create_table(
                    TableName=table_name,
                    KeySchema=[
                        {'AttributeName': 'id', 'KeyType': 'HASH'},  # Partition key
                    ],
                    AttributeDefinitions=[
                        {'AttributeName': 'id', 'AttributeType': 'S'},
                    ],
                    ProvisionedThroughput={
                        'ReadCapacityUnits': read_capacity_units,
                        'WriteCapacityUnits': write_capacity_units
                    }
                )
                # Wait for table creation
                await dynamodb.meta.client.get_waiter('table_exists').wait(TableName=table_name)
                print(f"DynamoDB table '{table_name}' created")
            else:
                table = await dynamodb.Table(table_name)
                print(f"Using existing DynamoDB table '{table_name}'")
                
            return table
    
    async def put_item(self, table_name: str, item: Dict[str, Any]) -> bool:
        if not self.is_configured():
            raise ValueError("AWS DynamoDB credentials not configured in environment variables")
            
        try:
            async with self.session.resource('dynamodb') as dynamodb:
                table = await dynamodb.Table(table_name)
                await table.put_item(Item=item)
                return True
                
        except Exception as e:
            print(f"Error putting item in DynamoDB: {e}")
            return False
    
    async def get_item(self, table_name: str, key: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if not self.is_configured():
            raise ValueError("AWS DynamoDB credentials not configured in environment variables")
            
        try:
            async with self.session.resource('dynamodb') as dynamodb:
                table = await dynamodb.Table(table_name)
                response = await table.get_item(Key=key)
                return cast(Optional[Dict[str, Any]], response.get('Item'))
                
        except Exception as e:
            print(f"Error getting item from DynamoDB: {e}")
            return None
    
    async def scan(self, table_name: str, limit: int = 100) -> List[Dict[str, Any]]:
        if not self.is_configured():
            raise ValueError("AWS DynamoDB credentials not configured in environment variables")
            
        try:
            async with self.session.resource('dynamodb') as dynamodb:
                table = await dynamodb.Table(table_name)
                response = await table.scan(Limit=limit)
                return cast(List[Dict[str, Any]], response.get('Items', []))
                
        except Exception as e:
            print(f"Error scanning DynamoDB table: {e}")
            return [] 