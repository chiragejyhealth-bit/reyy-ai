import os
import json
import uuid
from typing import Dict, List, Any, Optional
from podcastfy.client import generate_podcast

from clients.dynamodb_client import DynamoDBClient
from services.podcast_config_service import PodcastConfigService


class PodcastService:
    """Service for generating podcasts from Perplexity data"""
    
    def __init__(self, dynamodb_client: DynamoDBClient, podcast_config_service: Optional[PodcastConfigService] = None) -> None:
        """
        Initialize the Podcast service
        
        Args:
            dynamodb_client: Client for DynamoDB
            podcast_config_service: Service for generating podcast configurations
        """
        self.dynamodb_client = dynamodb_client
        self.podcast_config_service = podcast_config_service
        self.output_dir = os.path.join(os.getcwd(), "data", "audio")
        os.makedirs(self.output_dir, exist_ok=True)
    
    async def get_perplexity_data(self, table_name: str, item_id: Optional[str] = None, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve Perplexity data from DynamoDB
        
        Args:
            table_name: The DynamoDB table name
            item_id: Optional specific item ID to retrieve
            limit: Maximum number of items to retrieve if no specific ID
            
        Returns:
            List of Perplexity data items
        """
        if item_id:
            item = await self.dynamodb_client.get_item(table_name, {"id": item_id})
            return [item] if item else []
        else:
            items = await self.dynamodb_client.scan(table_name, limit=limit)
            return items
    
    def extract_urls_from_perplexity_data(self, perplexity_items: List[Dict[str, Any]]) -> List[str]:
        """
        Extract URLs from Perplexity data items
        
        Args:
            perplexity_items: List of Perplexity data items
            
        Returns:
            List of URLs from the data
        """
        urls = []
        for item in perplexity_items:
            data = item.get('data', {})
            if 'url' in data:
                urls.append(data['url'])
            elif 'link' in data:
                urls.append(data['link'])
        
        return urls
    
    def extract_topics_from_perplexity_data(self, perplexity_items: List[Dict[str, Any]]) -> List[str]:
        """
        Extract topics from Perplexity data items
        
        Args:
            perplexity_items: List of Perplexity data items
            
        Returns:
            List of topics from the data
        """
        topics = []
        for item in perplexity_items:
            data = item.get('data', {})
            
            # Extract topic if available
            if 'topic' in data and data['topic']:
                topics.append(data['topic'])
                
            # Extract title as a topic
            if 'title' in data and data['title']:
                topics.append(data['title'])
                
            # Extract tags as topics
            if 'tags' in data and isinstance(data['tags'], list):
                topics.extend(data['tags'])
        
        # Remove duplicates and empty strings
        return list(set([topic for topic in topics if topic]))
    
    def extract_content_text_from_perplexity_data(self, perplexity_items: List[Dict[str, Any]]) -> str:
        """
        Extract content text from Perplexity data items for analysis
        
        Args:
            perplexity_items: List of Perplexity data items
            
        Returns:
            Combined content text
        """
        content_texts = []
        
        for item in perplexity_items:
            data = item.get('data', {})
            
            # Extract title
            if 'title' in data and data['title']:
                content_texts.append(data['title'])
                
            # Extract description
            if 'description' in data and data['description']:
                content_texts.append(data['description'])
                
            # Extract content
            if 'content' in data and data['content']:
                content_texts.append(data['content'])
                
            # Extract summary
            if 'summary' in data and data['summary']:
                content_texts.append(data['summary'])
        
        return " ".join(content_texts)
    
    def generate_conversation_config(self, perplexity_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a custom conversation config based on Perplexity data
        
        Args:
            perplexity_items: List of Perplexity data items
            
        Returns:
            Custom conversation configuration
        """
        # Default configuration
        config = {
            "conversation_style": ["engaging", "fast-paced", "enthusiastic"],
            "roles_person1": "main summarizer",
            "roles_person2": "questioner/clarifier",
            "dialogue_structure": ["Introduction", "Main Content Summary", "Conclusion"],
            "podcast_name": "Perplexity Insights",
            "podcast_tagline": "Exploring Today's Top Stories",
            "output_language": "English",
            "engagement_techniques": ["rhetorical questions", "anecdotes", "analogies", "humor"],
            "creativity": 0.8,
            "user_instructions": ""
        }
        
        # Customize based on content if available
        if perplexity_items:
            # Get the first item for basic customization
            first_item = perplexity_items[0].get('data', {})
            
            # Set podcast name based on topic if available
            if 'topic' in first_item:
                topic = first_item['topic']
                config["podcast_name"] = f"{topic.capitalize()} Insights"
                config["podcast_tagline"] = f"Exploring {topic.capitalize()} Topics"
            
            # Analyze content to determine conversation style
            titles = [item.get('data', {}).get('title', '') for item in perplexity_items if 'data' in item]
            combined_text = ' '.join(titles).lower()
            
            # Adjust conversation style based on content
            if any(term in combined_text for term in ['tech', 'technology', 'ai', 'software']):
                config["conversation_style"] = ["analytical", "informative", "educational"]
                config["roles_person1"] = "tech analyst"
                config["roles_person2"] = "tech enthusiast"
            
            elif any(term in combined_text for term in ['science', 'research', 'study']):
                config["conversation_style"] = ["academic", "detailed", "educational"]
                config["roles_person1"] = "science communicator"
                config["roles_person2"] = "curious interviewer"
            
            elif any(term in combined_text for term in ['business', 'finance', 'market', 'economy']):
                config["conversation_style"] = ["professional", "analytical", "insightful"]
                config["roles_person1"] = "market analyst"
                config["roles_person2"] = "business journalist"
            
            elif any(term in combined_text for term in ['politics', 'government', 'policy']):
                config["conversation_style"] = ["balanced", "thoughtful", "analytical"]
                config["roles_person1"] = "political analyst"
                config["roles_person2"] = "policy expert"
            
            elif any(term in combined_text for term in ['entertainment', 'movie', 'music', 'celebrity']):
                config["conversation_style"] = ["casual", "enthusiastic", "entertaining"]
                config["roles_person1"] = "entertainment critic"
                config["roles_person2"] = "pop culture enthusiast"
        
        return config
    
    async def generate_intelligent_config(self, 
                                        perplexity_items: List[Dict[str, Any]], 
                                        tone: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate an intelligent conversation config using Gemini API
        
        Args:
            perplexity_items: List of Perplexity data items
            tone: Optional tone for the podcast
            
        Returns:
            Intelligent conversation configuration
        """
        if not self.podcast_config_service:
            # Fall back to rule-based config if no config service available
            return self.generate_conversation_config(perplexity_items)
        
        try:
            # Extract topics and content text from Perplexity data
            topics = self.extract_topics_from_perplexity_data(perplexity_items)
            content_text = self.extract_content_text_from_perplexity_data(perplexity_items)
            urls = self.extract_urls_from_perplexity_data(perplexity_items)
            
            # Determine audience based on content
            audience = "general audience interested in current topics"
            if topics:
                combined_text = " ".join(topics).lower()
                if any(term in combined_text for term in ['tech', 'technology', 'ai', 'software']):
                    audience = "technology enthusiasts and professionals"
                elif any(term in combined_text for term in ['business', 'finance', 'market', 'economy']):
                    audience = "business professionals and investors"
                elif any(term in combined_text for term in ['science', 'research', 'study']):
                    audience = "science enthusiasts and curious minds"
            
            # Generate config using Gemini and specialized templates
            config = await self.podcast_config_service.generate_podcast_config(
                topics=topics,
                urls=urls,
                audience=audience,
                tone=tone
            )
            
            return config
            
        except Exception as e:
            print(f"Error generating intelligent config: {e}")
            # Fall back to rule-based config
            return self.generate_conversation_config(perplexity_items)
    
    async def generate_podcast_from_perplexity(self, 
                                              table_name: str, 
                                              item_id: Optional[str] = None,
                                              custom_config: Optional[Dict[str, Any]] = None,
                                              tts_model: str = "gemini",
                                              use_intelligent_config: bool = True,
                                              tone: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a podcast from Perplexity data
        
        Args:
            table_name: The DynamoDB table name
            item_id: Optional specific item ID to retrieve
            custom_config: Optional custom conversation configuration
            tts_model: TTS model to use (gemini, geminimulti, openai, elevenlabs, edge)
            use_intelligent_config: Whether to use intelligent config generation
            tone: Optional tone for the podcast
            
        Returns:
            Result of podcast generation
        """
        try:
            # Get Perplexity data
            perplexity_items = await self.get_perplexity_data(table_name, item_id)
            
            if not perplexity_items:
                return {
                    "success": False,
                    "error": "No Perplexity data found",
                    "audio_file": None
                }
            
            # Extract URLs
            urls = self.extract_urls_from_perplexity_data(perplexity_items)
            
            if not urls:
                return {
                    "success": False,
                    "error": "No URLs found in Perplexity data",
                    "audio_file": None
                }
            
            # Generate conversation config
            if use_intelligent_config and self.podcast_config_service:
                conversation_config = await self.generate_intelligent_config(perplexity_items, tone)
            else:
                conversation_config = self.generate_conversation_config(perplexity_items)
            
            # Override with custom config if provided
            if custom_config:
                conversation_config.update(custom_config)
            
            # Generate podcast
            audio_file = generate_podcast(
                urls=urls,
                tts_model=tts_model,
                conversation_config=conversation_config
            )
            
            return {
                "success": True,
                "audio_file": audio_file,
                "urls_used": urls,
                "config_used": conversation_config
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "audio_file": None
            } 