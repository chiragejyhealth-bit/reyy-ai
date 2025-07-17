import os
import aiohttp
from typing import Dict, Optional, Any, ByteString

from clients.aws_base_client import AWSBaseClient


class S3Client(AWSBaseClient):
    async def upload_file(self, file_content: ByteString, bucket_name: str, 
                         key: str, content_type: str = 'application/octet-stream') -> Optional[str]:
        if not self.is_configured():
            raise ValueError("AWS S3 credentials not configured in environment variables")
            
        try:
            async with self.session.client('s3') as s3:
                await s3.put_object(
                    Bucket=bucket_name,
                    Key=key,
                    Body=file_content,
                    ContentType=content_type
                )
            
            s3_url: str = f"https://{bucket_name}.s3.amazonaws.com/{key}"
            return s3_url
            
        except Exception as e:
            print(f"Error uploading to S3: {e}")
            return None
    
    async def download_file(self, url: str) -> Optional[ByteString]:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    response.raise_for_status()
                    return await response.read()
        except Exception as e:
            print(f"Error downloading file: {e}")
            return None 