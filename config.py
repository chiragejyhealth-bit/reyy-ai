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
    
    @staticmethod
    def get_podcast_config() -> Dict[str, Any]:
        """Get podcast generation configuration from environment variables"""
        return {
            'default_tts_model': os.environ.get('PODCAST_DEFAULT_TTS_MODEL', 'gemini'),
            'default_word_count': int(os.environ.get('PODCAST_DEFAULT_WORD_COUNT', '100')),
            'default_creativity': float(os.environ.get('PODCAST_DEFAULT_CREATIVITY', '0.8')),
            'default_podcast_name': os.environ.get('PODCAST_DEFAULT_NAME', 'Reyy Podcast'),
            'default_output_language': os.environ.get('PODCAST_DEFAULT_LANGUAGE', 'English')
        }
    
    @staticmethod
    def get_gemini_config() -> Dict[str, Any]:
        """Get Gemini API configuration from environment variables"""
        return {
            'api_key': os.environ.get('GEMINI_API_KEY'),
            'default_model': os.environ.get('GEMINI_DEFAULT_MODEL', 'gemini-1.5-pro'),
            'default_temperature': float(os.environ.get('GEMINI_DEFAULT_TEMPERATURE', '0.7')),
            'default_max_tokens': int(os.environ.get('GEMINI_DEFAULT_MAX_TOKENS', '1024'))
        } 