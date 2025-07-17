#!/usr/bin/env python3

import os
from typing import Dict, Any
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv

from container import Container
from config import Config
from services.perplexity_service import PerplexityService

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Perplexity API",
    description="API for fetching Perplexity data and storing in AWS",
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

# Dependency to get PerplexityService
def get_perplexity_service() -> PerplexityService:
    return container.perplexity_service()

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

def start() -> None:
    host: str = os.environ.get('API_HOST', '0.0.0.0')
    port: int = int(os.environ.get('API_PORT', '8000'))
    debug: bool = os.environ.get('API_DEBUG', 'False').lower() == 'true'
    
    uvicorn.run("api:app", host=host, port=port, reload=debug)

if __name__ == "__main__":
    start() 