import os
from typing import Dict, Any, Optional
from jinja2 import Environment, BaseLoader
import aiohttp  
import asyncio

class GeminiClient:
    def __init__(self) -> None:
        self.api_key = os.environ.get('GEMINI_API_KEY')
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"
        self.default_model = "gemini-1.5-pro"
        self.jinja_env = Environment(loader=BaseLoader())
    
    async def generate_content(self, prompt: str, model: Optional[str] = None, 
                             temperature: float = 0.7, max_tokens: int = 1024) -> Optional[Dict[str, Any]]:
        model_name = model or self.default_model
        url = f"{self.base_url}/{model_name}:generateContent?key={self.api_key}"
        
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
                "topP": 0.95,
                "topK": 40
            }
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    response.raise_for_status()
                    return await response.json()
        except Exception as e:
            print(f"Error calling Gemini API: {e}")
            return None
    
if __name__ == "__main__":
    client = GeminiClient()
    print(asyncio.run(client.generate_content("Hello, how are you?")))