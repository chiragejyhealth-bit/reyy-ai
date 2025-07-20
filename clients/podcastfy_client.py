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
            conversation_config=conversation_config,
            transcript_only=config.transcript_only,
            image_paths=config.image_paths
        )
        
        return audio_file

# Example usage
if __name__ == "__main__":
    # Create podcast configuration
    config = PodcastConfig(
        urls=["data/images/chirag_punia.pdf"],
        tts_model="gemini",
        image_paths=["https://pplx-res.cloudinary.com/image/fetch/s--S3X6yNFW--/t_limit/https://www.reuters.com/resizer/v2/X4D24K4LTJP2JGRJ5CKG227UPM.jpg%3Fauth%3D45ec298707d9e4c352e5391f667b2d80294c3620d7316602c39a1aedba5191b2%26width%3D4180%26quality%3D80"],
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