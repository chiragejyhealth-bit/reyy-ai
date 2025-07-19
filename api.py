#!/usr/bin/env python3

import os
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, Depends, HTTPException, Body, Query
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv
from pydantic import BaseModel

from container import Container
from config import Config
from services.perplexity_service import PerplexityService
from services.podcast_service import PodcastService
from services.podcast_config_service import PodcastConfigService

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Perplexity API",
    description="API for fetching Perplexity data and generating podcasts",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize DI container
container = Container.get_container()

# Pydantic models for request validation
class PodcastConfig(BaseModel):
    conversation_style: Optional[List[str]] = None
    roles_person1: Optional[str] = None
    roles_person2: Optional[str] = None
    dialogue_structure: Optional[List[str]] = None
    podcast_name: Optional[str] = None
    podcast_tagline: Optional[str] = None
    output_language: Optional[str] = None
    engagement_techniques: Optional[List[str]] = None
    creativity: Optional[float] = None
    user_instructions: Optional[str] = None
    word_count: Optional[int] = None

class ConfigRequest(BaseModel):
    topics: Optional[List[str]] = None
    urls: Optional[List[str]] = None
    audience: Optional[str] = None
    tone: Optional[str] = None
    additional_instructions: Optional[str] = None
    template_name: Optional[str] = None
    temperature: Optional[float] = 0.7

class TemplateRequest(BaseModel):
    template_name: str
    template_content: str

# Dependency to get PerplexityService
def get_perplexity_service() -> PerplexityService:
    return container.perplexity_service()

# Dependency to get PodcastService
def get_podcast_service() -> PodcastService:
    return container.podcast_service()

# Dependency to get PodcastConfigService
def get_podcast_config_service() -> PodcastConfigService:
    return container.podcast_config_service()

@app.get("/")
def read_root() -> Dict[str, str]:
    return {"message": "Perplexity API is running"}

@app.post("/process")
async def process_perplexity_data(
    perplexity_service: PerplexityService = Depends(get_perplexity_service)
) -> Dict[str, Any]:
    try:
        # Get configuration
        s3_config: Dict[str, str] = Config.get_s3_config()
        dynamodb_config: Dict[str, Any] = Config.get_dynamodb_config()
        perplexity_config: Dict[str, Any] = Config.get_perplexity_config()
        
        # Process data using service
        result: Dict[str, Any] = await perplexity_service.process_perplexity_data(
            bucket_name=s3_config['bucket_name'],
            table_name=dynamodb_config['table_name'],
            save_locally=True,
            local_filename=perplexity_config['json_output_path']
        )
        
        return result
    
    except ValueError as e:
        raise HTTPException(status_code=500, detail=f"Configuration error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing data: {str(e)}")

@app.post("/generate-podcast")
async def generate_podcast(
    podcast_config: Optional[PodcastConfig] = Body(None),
    item_id: Optional[str] = None,
    tts_model: str = "gemini",
    use_intelligent_config: bool = True,
    tone: Optional[str] = None,
    podcast_service: PodcastService = Depends(get_podcast_service)
) -> Dict[str, Any]:
    try:
        # Get configuration
        dynamodb_config: Dict[str, Any] = Config.get_dynamodb_config()
        
        # Convert podcast_config to dict if provided
        config_dict = podcast_config.dict(exclude_unset=True) if podcast_config else None
        
        # Generate podcast using service
        result: Dict[str, Any] = await podcast_service.generate_podcast_from_perplexity(
            table_name=dynamodb_config['table_name'],
            item_id=item_id,
            custom_config=config_dict,
            tts_model=tts_model,
            use_intelligent_config=use_intelligent_config,
            tone=tone
        )
        
        if not result['success']:
            raise HTTPException(status_code=500, detail=result['error'])
        
        return result
    
    except ValueError as e:
        raise HTTPException(status_code=500, detail=f"Configuration error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating podcast: {str(e)}")

@app.post("/generate-podcast-config")
async def generate_podcast_config(
    config_request: ConfigRequest,
    podcast_config_service: PodcastConfigService = Depends(get_podcast_config_service)
) -> Dict[str, Any]:
    try:
        # Generate podcast configuration
        config = await podcast_config_service.generate_podcast_config(
            topics=config_request.topics,
            urls=config_request.urls,
            audience=config_request.audience,
            tone=config_request.tone,
            additional_instructions=config_request.additional_instructions,
            template_name=config_request.template_name,
            temperature=config_request.temperature or 0.7
        )
        
        return config
    
    except ValueError as e:
        raise HTTPException(status_code=500, detail=f"Configuration error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating podcast configuration: {str(e)}")

@app.post("/save-template")
async def save_template(
    template_request: TemplateRequest,
    podcast_config_service: PodcastConfigService = Depends(get_podcast_config_service)
) -> Dict[str, str]:
    try:
        # Save template
        template_path = podcast_config_service.save_template(
            template_name=template_request.template_name,
            template_content=template_request.template_content
        )
        
        return {
            "message": f"Template saved successfully as {template_request.template_name}",
            "path": template_path
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving template: {str(e)}")

@app.get("/templates/{template_name}")
async def get_template(
    template_name: str,
    podcast_config_service: PodcastConfigService = Depends(get_podcast_config_service)
) -> Dict[str, str]:
    # Load template
    template_content = podcast_config_service.load_template(template_name)
    
    if not template_content:
        raise HTTPException(status_code=404, detail=f"Template {template_name} not found")
    
    return {
        "template_name": template_name,
        "template_content": template_content
    }

@app.get("/podcast/{filename}")
async def get_podcast(filename: str) -> FileResponse:
    """
    Get a generated podcast file by filename
    """
    file_path = os.path.join(os.getcwd(), "data", "audio", filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Podcast file not found")
    
    return FileResponse(
        path=file_path,
        media_type="audio/mpeg",
        filename=filename
    )

def start() -> None:
    host: str = os.environ.get('API_HOST', '0.0.0.0')
    port: int = int(os.environ.get('API_PORT', '8000'))
    debug: bool = os.environ.get('API_DEBUG', 'False').lower() == 'true'
    
    uvicorn.run("api:app", host=host, port=port, reload=debug)

if __name__ == "__main__":
    start() 