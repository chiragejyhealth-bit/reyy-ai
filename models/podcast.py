from typing import List, Optional
from pydantic import BaseModel, Field

class TTSVoiceConfig(BaseModel):
    question: str = Field(default=None, description="Voice for the questioner")
    answer: str = Field(default=None, description="Voice for the answerer")


class ConversationConfig(BaseModel):
    """Pydantic model for podcast configuration"""

    # Conversation configuration
    word_count: int = Field(
        default=150,
        description="Target word count for the podcast transcript"
    )
    conversation_style: List[str] = Field(
        default_factory=lambda: ["engaging", "fast-paced", "enthusiastic"],
        description="Styles to apply to the conversation"
    )
    roles_person1: str = Field(
        default="main summarizer",
        description="Role of the first speaker"
    )
    roles_person2: str = Field(
        default="questioner/clarifier",
        description="Role of the second speaker"
    )
    dialogue_structure: List[str] = Field(
        default_factory=lambda: ["Introduction", "Main Content Summary", "Conclusion"],
        description="Structure of the dialogue"
    )
    podcast_name: str = Field(
        default="Reyy AI",
        description="Name of the podcast"
    )
    podcast_tagline: str = Field(
        default="Your Personal Generative AI Podcasts",
        description="Tagline for the podcast"
    )
    output_language: str = Field(
        default="English",
        description="Language of the output"
    )
    engagement_techniques: List[str] = Field(
        default_factory=lambda: ["rhetorical questions", "anecdotes", "analogies", "humor"],
        description="Techniques to engage the audience"
    )
    creativity: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Level of creativity/temperature (0-1)"
    )
    user_instructions: str = Field(
        default="",
        description="Custom instructions to guide the conversation focus and topics"
    )
    max_num_chunks: int = Field(
        default=7,
        description="Maximum number of rounds of discussions in longform"
    )
    min_chunk_size: int = Field(
        default=600,
        description="Minimum number of characters to generate a round of discussion in longform"
    )
    
    # TTS voices configuration
    voices: Optional[TTSVoiceConfig] = Field(
        default=None,
        description="Custom voices configuration"
    )
    

class PodcastConfig(BaseModel):
    """Pydantic model for podcast configuration"""
    # Content sources
    urls: List[str] = Field(
        default_factory=list,
        description="List of URLs to generate podcast content from"
    )

    # TTS configuration
    tts_model: Optional[str] = Field(
        default="gemini",
        description="TTS model to use: 'openai', 'elevenlabs', 'gemini', 'geminimulti', or 'edge'"
    )

    conversation_config: Optional[ConversationConfig] = Field(
        default=ConversationConfig(),
        description="Conversation configuration"
    )