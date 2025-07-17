from dependency_injector import containers, providers
from typing import Dict, Any

from clients.perplexity_client import PerplexityClient
from clients.s3_client import S3Client
from clients.dynamodb_client import DynamoDBClient
from services.perplexity_service import PerplexityService
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
    
    # Services
    perplexity_service = providers.Singleton(
        PerplexityService,
        perplexity_client=perplexity_client,
        s3_client=s3_client,
        dynamodb_client=dynamodb_client
    )
    
    @classmethod
    def get_container(cls) -> 'Container':
        """Get configured container instance"""
        return cls() 