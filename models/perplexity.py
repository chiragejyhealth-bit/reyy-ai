from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

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
    
    def from_json(self, json_data: Dict[str, Any]) -> "PerplexityFeedItem":
        
        images = []
        if json_data.get("featured_images") and len(json_data["featured_images"]) > 0:
            for image in json_data["featured_images"]:
                image_url = image.get("image")
                if image_url:
                    images.append(image_url)
            
        return PerplexityFeedItem(
            uuid=json_data.get("uuid", ""),
            slug=json_data.get("slug", ""),
            title=json_data.get("title", ""),
            summary=json_data.get("summary", ""),
            first_answer=json_data.get("first_answer", ""),
            description=json_data.get("description", ""),
            bullet_summary_preload=json_data.get("bullet_summary_preload", ""),
            images=images
        )
 