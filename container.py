from dependency_injector import containers, providers
from typing import Dict, Any

from clients.perplexity_client import PerplexityClient
from clients.s3_client import S3Client
from clients.dynamodb_client import DynamoDBClient
from clients.gemini_client import GeminiClient
from services.perplexity_service import PerplexityService
from services.podcast_service import PodcastService
from services.podcast_config_service import PodcastConfigService
from config import Config


class Container(containers.DeclarativeContainer):
    """Dependency Injection Container"""
    
    # Configuration
    config = providers.Factory(
        Config
    )
    
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
    
    # Services
    perplexity_service = providers.Singleton(
        PerplexityService,
        perplexity_client=perplexity_client,
        s3_client=s3_client,
        dynamodb_client=dynamodb_client
    )
    
    podcast_config_service = providers.Singleton(
        PodcastConfigService,
        gemini_client=gemini_client
    )
    
    podcast_service = providers.Singleton(
        PodcastService,
        dynamodb_client=dynamodb_client,
        podcast_config_service=podcast_config_service
    )
    
    @classmethod
    def get_container(cls) -> 'Container':
        """Get configured container instance"""
        return cls() 