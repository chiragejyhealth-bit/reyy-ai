import os
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, ByteString, cast

from clients.perplexity_client import PerplexityClient
from clients.s3_client import S3Client
from clients.dynamodb_client import DynamoDBClient


class PerplexityService:
    """Service for handling Perplexity operations"""
    
    def __init__(self, 
                perplexity_client: PerplexityClient,
                s3_client: S3Client,
                dynamodb_client: DynamoDBClient) -> None:
        """
        Initialize the Perplexity service
        
        Args:
            perplexity_client: Client for Perplexity API
            s3_client: Client for S3
            dynamodb_client: Client for DynamoDB
        """
        self.perplexity_client: PerplexityClient = perplexity_client
        self.s3_client: S3Client = s3_client
        self.dynamodb_client: DynamoDBClient = dynamodb_client
    
    def save_to_json(self, data: Dict[str, Any], 
                    filename: str = "response/perplexity_response.json") -> None:
        """
        Save API response data to a JSON file
        
        Args:
            data: The API response data
            filename: The name of the file to save the data to
        """
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        print(f"Data saved to {os.path.abspath(filename)}")
    
    def extract_audio_urls(self, data: Dict[str, Any]) -> List[str]:
        """
        Extract audio URLs from Perplexity response data
        
        Args:
            data: The Perplexity API response data
            
        Returns:
            List of audio URLs
        """
        audio_urls: List[str] = []
        
        if 'items' in data:
            for item in data['items']:
                if 'audio_url' in item and item['audio_url']:
                    audio_urls.append(item['audio_url'])
        
        return audio_urls
    
    async def upload_audio_files(self, audio_urls: List[str], bucket_name: str) -> Dict[str, str]:
        """
        Download and upload audio files to S3
        
        Args:
            audio_urls: List of audio URLs to download and upload
            bucket_name: The S3 bucket name
            
        Returns:
            Dictionary mapping original URLs to S3 URLs
        """
        url_mapping: Dict[str, str] = {}
        
        for url in audio_urls:
            if url:
                # Download audio file
                audio_content: Optional[ByteString] = await self.s3_client.download_file(url)
                
                if audio_content:
                    # Generate key for S3
                    prefix: str = 'perplexity_audio/'
                    key: str = f"{prefix}{os.path.basename(url)}"
                    
                    # Upload to S3
                    s3_url: Optional[str] = await self.s3_client.upload_file(
                        file_content=audio_content,
                        bucket_name=bucket_name,
                        key=key,
                        content_type='audio/mpeg'
                    )
                    
                    if s3_url:
                        url_mapping[url] = s3_url
                        print(f"Audio uploaded to S3: {s3_url}")
        
        return url_mapping
    
    async def store_in_dynamodb(self, data: Dict[str, Any], 
                               table_name: str, 
                               s3_audio_mapping: Dict[str, str]) -> List[str]:
        """
        Store Perplexity data in DynamoDB
        
        Args:
            data: The Perplexity API response data
            table_name: The DynamoDB table name
            s3_audio_mapping: Mapping of original audio URLs to S3 URLs
            
        Returns:
            List of item IDs stored in DynamoDB
        """
        stored_ids: List[str] = []
        
        if 'items' in data:
            for item in data['items']:
                # Replace audio URLs with S3 URLs if available
                if s3_audio_mapping and 'audio_url' in item and item['audio_url'] in s3_audio_mapping:
                    item['original_audio_url'] = item['audio_url']
                    item['audio_url'] = s3_audio_mapping[item['audio_url']]
                
                # Add metadata
                item_id: str = cast(str, item.get('uuid', str(uuid.uuid4())))
                timestamp: str = datetime.now().isoformat()
                
                # Create DynamoDB item
                db_item: Dict[str, Any] = {
                    'id': item_id,
                    'timestamp': timestamp,
                    'data': item
                }
                
                # Store in DynamoDB
                success: bool = await self.dynamodb_client.put_item(table_name, db_item)
                
                if success:
                    stored_ids.append(item_id)
            
            print(f"Stored {len(stored_ids)} items in DynamoDB table '{table_name}'")
        
        return stored_ids
    
    async def process_perplexity_data(self, bucket_name: str, 
                                     table_name: str = 'perplexity_data',
                                     save_locally: bool = True,
                                     local_filename: str = "response/perplexity_response.json") -> Dict[str, Any]:
        """
        Complete workflow to process Perplexity data
        
        Args:
            bucket_name: The S3 bucket name
            table_name: The DynamoDB table name
            save_locally: Whether to save the response locally
            local_filename: The name of the local file to save the response to
            
        Returns:
            Processing results including replicated audio URLs
        """
        if not self.s3_client.is_configured() or not self.dynamodb_client.is_configured():
            raise ValueError("AWS credentials not properly configured in environment variables")
            
        try:
            # Fetch feed data from Perplexity API
            data: Dict[str, Any] = await self.perplexity_client.get_feed_async()
            
            # Save to local JSON if requested
            if save_locally:
                self.save_to_json(data, local_filename)
            
            # Extract audio URLs
            audio_urls: List[str] = self.extract_audio_urls(data)
            
            # Upload audio files to S3
            s3_audio_mapping: Dict[str, str] = await self.upload_audio_files(audio_urls, bucket_name)
            
            # Store in DynamoDB
            stored_ids: List[str] = await self.store_in_dynamodb(data, table_name, s3_audio_mapping)
            
            # Get list of replicated audio URLs
            replicated_urls: List[str] = list(s3_audio_mapping.values())
            
            return {
                'success': True,
                'items_processed': len(data.get('items', [])),
                'items_stored': len(stored_ids),
                'audio_files_uploaded': len(s3_audio_mapping),
                'replicated_audio_urls': replicated_urls
            }
            
        except Exception as e:
            print(f"Error processing Perplexity data: {e}")
            return {
                'success': False,
                'error': str(e),
                'replicated_audio_urls': []
            } 