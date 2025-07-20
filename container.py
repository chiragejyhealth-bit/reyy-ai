from dependency_injector import containers, providers

from clients.perplexity_client import PerplexityClient
from clients.s3_client import S3Client
from clients.dynamodb_client import DynamoDBClient
from clients.gemini_client import GeminiClient
from clients.podcastfy_client import PodcastClient
from services.podcast_service import PodcastService
from services.preplexity_service import PerplexityService

class ServicesContainer(containers.DeclarativeContainer):
    """Dependency Injection Container"""
    
    # Clients
    perplexity_client = providers.Singleton(
        PerplexityClient
    )
    
    s3_client = providers.Singleton(
        S3Client
    )
    
    dynamodb_client = providers.Singleton(
        DynamoDBClient
    )
    
    gemini_client = providers.Singleton(
        GeminiClient
    )
    
    podcast_client = providers.Singleton(
        PodcastClient
    )

    podcast_service = providers.Singleton(
        PodcastService,
        podcast_client=podcast_client,
        dynamo_db_client=dynamodb_client,
        s3_client=s3_client,
        gemini_client=gemini_client,
        perplexity_client=perplexity_client
    )

    perplexity_service = providers.Singleton(
        PerplexityService,
        perplexity_client=perplexity_client,
        dynamo_db_client=dynamodb_client
    )