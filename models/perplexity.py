from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

class PerplexityFeedItem(BaseModel):
    """Model for a Perplexity feed item"""
    uuid: str = Field(description="Unique identifier for the feed item")
    slug: str = Field(description="URL slug for the feed item")
    title: str = Field(description="Title of the feed item")
    summary: str = Field(description="Summary of the feed item")
    first_answer: str = Field(description="First answer snippet from the feed item")
    description: str = Field(description="Description of the feed item")
    bullet_summary_preload: str = Field(description="Bullet point summary of the feed item")
    images: Optional[List[str]] = Field(default=None, description="List of images from featured images")
    last_query_datetime: Optional[str] = Field(default=None, description="Last query datetime")
    
    @classmethod
    def from_json(cls, json_data: Dict[str, Any]) -> "PerplexityFeedItem":
        
        images = []
        last_query_datetime = json_data.get("last_query_datetime")
        if json_data.get("featured_images") and len(json_data["featured_images"]) > 0:
            for image in json_data["featured_images"]:
                image_url = image.get("image")
                if image_url:
                    images.append(image_url)
            
        return cls(
            uuid=json_data.get("uuid", ""),
            slug=json_data.get("slug", ""),
            title=json_data.get("title", ""),
            summary=json_data.get("summary", ""),
            first_answer=json_data.get("first_answer", ""),
            description=json_data.get("description", ""),
            bullet_summary_preload=json_data.get("bullet_summary_preload", ""),
            images=images,
            last_query_datetime=last_query_datetime
        )
 