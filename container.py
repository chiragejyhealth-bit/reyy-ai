from dependency_injector import containers, providers

from clients.perplexity_client import PerplexityClient
from clients.s3_client import S3Client
from clients.dynamodb_client import DynamoDBClient
from clients.gemini_client import GeminiClient


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