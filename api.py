#!/usr/bin/env python3

import os
from typing import Dict
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv

from container import ServicesContainer

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

@app.get("/")
def read_root() -> Dict[str, str]:
    return {"message": "Reyy AI API is running"}

def start() -> None:
    host: str = os.environ.get('API_HOST', '0.0.0.0')
    port: int = int(os.environ.get('API_PORT', '8000'))
    debug: bool = os.environ.get('API_DEBUG', 'False').lower() == 'true'
    
    uvicorn.run("api:app", host=host, port=port, reload=debug)

if __name__ == "__main__":
    start() 