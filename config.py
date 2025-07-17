import os
from typing import Dict, Any, Optional


class Config:
    """Configuration manager for the application"""
    
    @staticmethod
    def get_aws_credentials() -> Dict[str, Optional[str]]:
        """Get AWS credentials from environment variables"""
        return {
            'aws_access_key_id': os.environ.get('AWS_ACCESS_KEY_ID'),
            'aws_secret_access_key': os.environ.get('AWS_SECRET_ACCESS_KEY'),
            'region_name': os.environ.get('AWS_REGION', 'us-east-1')
        }
    
    @staticmethod
    def get_s3_config() -> Dict[str, str]:
        """Get S3 configuration from environment variables"""
        return {
            'bucket_name': os.environ.get('S3_BUCKET_NAME', 'perplexity-audio'),
            'audio_prefix': os.environ.get('S3_AUDIO_PREFIX', 'perplexity_audio/')
        }
    
    @staticmethod
    def get_dynamodb_config() -> Dict[str, Any]:
        """Get DynamoDB configuration from environment variables"""
        return {
            'table_name': os.environ.get('DYNAMODB_TABLE_NAME', 'perplexity_data'),
            'read_capacity_units': int(os.environ.get('DYNAMODB_READ_CAPACITY_UNITS', '5')),
            'write_capacity_units': int(os.environ.get('DYNAMODB_WRITE_CAPACITY_UNITS', '5'))
        }
    
    @staticmethod
    def get_perplexity_config() -> Dict[str, Any]:
        """Get Perplexity API configuration from environment variables"""
        return {
            'default_limit': int(os.environ.get('PERPLEXITY_DEFAULT_LIMIT', '20')),
            'default_version': os.environ.get('PERPLEXITY_API_VERSION', '2.18'),
            'default_topic': os.environ.get('PERPLEXITY_DEFAULT_TOPIC', 'top'),
            'default_source': os.environ.get('PERPLEXITY_DEFAULT_SOURCE', 'default'),
            'json_output_path': os.environ.get('PERPLEXITY_JSON_OUTPUT_PATH', 'response/perplexity_response.json')
        } 