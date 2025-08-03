from datetime import datetime, timedelta
import os
import asyncio
from typing import List
from langsmith import traceable
from clients.dynamodb_client import DynamoDBClient
from clients.gemini_client import GeminiClient
from clients.podcastfy_client import PodcastClient
from clients.s3_client import S3Client
from models.perplexity import PerplexityFeedItem
from models.podcast import PodcastConfig
from utils.common import delete_transcripts, delete_audio_files, delete_pdf_responses
from utils.pdf import save_item_as_pdf
import logging
logging.basicConfig(level=logging.INFO)

class PodcastService:
    def __init__(self, podcast_client: PodcastClient, dynamo_db_client: DynamoDBClient, s3_client: S3Client,\
                  gemini_client: GeminiClient):
        
        self.podcast_client = podcast_client
        self.dynamo_db_client = dynamo_db_client
        self.s3_client = s3_client
        self.gemini_client = gemini_client

    #this will get all items from dynamo db and generate a podcast for each item with cutoff date 1 day ago
    @traceable(name="generate_podcast")
    async def generate_podcast(self) -> int:
        try:
            delete_transcripts()
            delete_audio_files()
            delete_pdf_responses()
        except Exception as e:
            raise e
        cutoff_date = datetime.now() - timedelta(days=5)
        items: List[PerplexityFeedItem] = await self.dynamo_db_client.scan(limit=2, last_query_datetime=cutoff_date)

        logging.info(f"Found {len(items)} items to process.")
        # Process items in parallel
        for item in items:
            asyncio.create_task(self._process_item(item))
            logging.info(f"Started processing item: {item.uuid}")
        return len(items)
    
    @traceable(name="process_podcast_item")
    async def _process_item(self, item: PerplexityFeedItem) -> None:
        """Process a single feed item to generate and upload a podcast."""
        pdf_path = audio_path = None
        try:
            # Create PDF from item
            pdf_path = await self._create_pdf(item)

            logging.info(f"Created PDF for item: {item.uuid}")

            # Generate podcast audio
            audio_path = await self._generate_audio(item, pdf_path)

            logging.info(f"Generated audio for item: {item.uuid}")

            # Upload to S3 and get URL
            s3_url = await self._upload_to_s3(audio_path)

            logging.info(f"Uploaded audio to S3 for item: {item.uuid}")

            # Update item in database with S3 URL
            await self._update_item_with_url(item.uuid, s3_url)

            logging.info(f"Updated item in database with S3 URL for item: {item.uuid}")

        except Exception as e:
            raise e
        finally:
            delete_transcripts()
            delete_audio_files()
            delete_pdf_responses()
            await asyncio.sleep(50)
    
    @traceable(name="create_pdf")
    async def _create_pdf(self, item: PerplexityFeedItem) -> str:
        """Create a PDF from the feed item and return the path."""
        pdf_path = f"responses/pdf/{item.uuid}.pdf"
        os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
        save_item_as_pdf(item, pdf_path)
        return pdf_path
    
    @traceable(name="generate_audio")
    async def _generate_audio(self, item: PerplexityFeedItem, pdf_path: str) -> str:
        """Generate podcast audio from the PDF and return the audio path."""
        config = PodcastConfig(urls=[pdf_path], image_paths=item.images)
        audio_path = await self.podcast_client.generate_podcast(config)
        return audio_path
    
    @traceable(name="upload_to_s3") 
    async def _upload_to_s3(self, file_path: str) -> str:
        """Upload a file to S3 and return the S3 URL."""
        with open(file_path, 'rb') as f:
            file_content = f.read()
            s3_url = await self.s3_client.upload_file(file_content=file_content, key=file_path)
        return s3_url
    
    @traceable(name="update_item_with_url")
    async def _update_item_with_url(self, uuid: str, s3_url: str) -> None:
        """Update the item in DynamoDB with the S3 URL."""
        await self.dynamo_db_client.update_item(
            key={'uuid': uuid},
            s3_url=s3_url
        )
