#!/usr/bin/env python3

import os
# Add gRPC fork safety configuration
os.environ["GRPC_ENABLE_FORK_SUPPORT"] = "true"
os.environ["GRPC_POLL_STRATEGY"] = "poll"
from typing import Dict, Any
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv

from container import ServicesContainer
from services.podcast_service import PodcastService
from services.preplexity_service import PerplexityService

# Initialize LangSmith
from langsmith import Client
langsmith_client = Client()

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Reyy AI API",
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
container = ServicesContainer()
perplexity_service : PerplexityService = container.perplexity_service()
podcast_service : PodcastService = container.podcast_service()
@app.get("/")
def read_root() -> Dict[str, str]:
    return {"message": "Reyy AI API is running"}

@app.post("/get-and-save-feed")
async def get_and_save_feed() -> Dict[str, Any]:
    num_items_saved, feed_items = await perplexity_service.get_and_save_feed(limit=20, offset=0)
    return {"message": "Feed saved successfully", "num_items_saved": num_items_saved, "feed_items": feed_items}

@app.post("/generate-podcast")
async def generate_podcast() -> Dict[str, Any]:
    success = await podcast_service.generate_podcast()
    return {"message": "Podcast generated successfully" if success else "Podcast generation failed"}

def start() -> None:
    host: str = os.environ.get('API_HOST', '0.0.0.0')
    port: int = int(os.environ.get('API_PORT', '8000'))
    
    uvicorn.run("main:app", host=host, port=port, reload=True)

if __name__ == "__main__":
    start()