import asyncio
from typing import Optional, ByteString, List
from clients.aws_base_client import AWSBaseClient

class S3Client(AWSBaseClient):

    async def upload_file(self, file_content: ByteString, 
                         key: str, content_type: str = 'application/octet-stream', bucket_name: str = 'reyy-ai') -> Optional[str]:
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


if __name__ == "__main__":
    client = S3Client()
    audio_path = 'response/feed.json'
    with open(audio_path, 'r') as f:
        file_content = f.read()
    print(asyncio.run(client.upload_file(file_content=file_content, key=audio_path)))