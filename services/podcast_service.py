from datetime import datetime, timedelta
from clients.dynamodb_client import DynamoDBClient
from clients.gemini_client import GeminiClient
from clients.perplexity_client import PerplexityClient
from clients.podcastfy_client import PodcastClient
from clients.s3_client import S3Client
from models.podcast import PodcastConfig, ConversationConfig, TTSVoiceConfig

class PodcastService:
    def __init__(self, podcast_client: PodcastClient, dynamo_db_client: DynamoDBClient, s3_client: S3Client,\
                  gemini_client: GeminiClient, perplexity_client: PerplexityClient):
        
        self.podcast_client = podcast_client
        self.dynamo_db_client = dynamo_db_client
        self.s3_client = s3_client
        self.gemini_client = gemini_client
        self.perplexity_client = perplexity_client

    #this will get all items from dynamo db and generate a podcast for each item with cutoff date 1 day ago
    #TODO CHECK THIS FUNCTION
    async def generate_podcast(self) -> str:
        cutoff_date = datetime.now() - timedelta(days=1)
        items = await self.dynamo_db_client.scan(limit=100, created_at=cutoff_date)
        for item in items:
            url = item['url']
            config = PodcastConfig(urls=[url])
            audio_path = await self.podcast_client.generate_podcast(config)
            with open(audio_path, 'rb') as f:
                file_content = f.read()
            s3_url = await self.s3_client.upload_file(file_content=file_content, key=audio_path)
            print(s3_url, url)
        