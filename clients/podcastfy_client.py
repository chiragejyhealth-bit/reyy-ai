import asyncio
from podcastfy.client import generate_podcast
from models.podcast import PodcastConfig, ConversationConfig

class PodcastClient:
    """Client for generating podcasts"""
    
    async def generate_podcast(self, config: PodcastConfig) -> str:
        conversation_config = config.conversation_config.model_dump() if config.conversation_config else None
        
        # Generate podcast using sync function in async context
        audio_file = await asyncio.to_thread(generate_podcast,
            urls=config.urls,
            tts_model=config.tts_model,
            conversation_config=conversation_config
        )
        
        return audio_file

# Example usage
if __name__ == "__main__":
    # Create podcast configuration
    config = PodcastConfig(
        urls=["https://shophorne.com/?srsltid=AfmBOoqvWYVdy3sYWNRn0X6sKavatI-Mnl5oBVNNnYhHfmPC1TLdj6aJ"],
        tts_model="gemini",
        conversation_config=ConversationConfig(
            word_count=125,
            conversation_style=["casual", "humorous"],
            podcast_name="Tech Chuckles",
            creativity=0.7
        )
    )
    
    # Generate podcast
    client = PodcastClient()
    audio_file = asyncio.run(client.generate_podcast(config))
    
    print(f"✅ Podcast generated successfully: {audio_file}") 