import os
import json
from typing import Dict, Any, Optional
import aiohttp
from jinja2 import Environment, BaseLoader


class GeminiClient:
    """Client for interacting with Google's Gemini API"""
    
    def __init__(self) -> None:
        """Initialize the Gemini client"""
        self.api_key = os.environ.get('GEMINI_API_KEY')
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"
        self.default_model = "gemini-1.5-pro"
        self.jinja_env = Environment(loader=BaseLoader())
    
    def is_configured(self) -> bool:
        """Check if the client is properly configured"""
        return bool(self.api_key)
    
    async def generate_content(self, prompt: str, model: Optional[str] = None, 
                             temperature: float = 0.7, max_tokens: int = 1024) -> Optional[Dict[str, Any]]:
        """
        Generate content using Gemini API
        
        Args:
            prompt: The prompt to send to the API
            model: The model to use (defaults to gemini-1.5-pro)
            temperature: The temperature for generation
            max_tokens: The maximum number of tokens to generate
            
        Returns:
            The API response as a dictionary, or None if there was an error
        """
        if not self.is_configured():
            raise ValueError("Gemini API key not configured in environment variables")
        
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
    
    def extract_text_from_response(self, response: Dict[str, Any]) -> str:
        """
        Extract text from Gemini API response
        
        Args:
            response: The API response
            
        Returns:
            The extracted text
        """
        if not response or 'candidates' not in response or not response['candidates']:
            return ""
        
        candidate = response['candidates'][0]
        if 'content' not in candidate or 'parts' not in candidate['content']:
            return ""
        
        parts = candidate['content']['parts']
        if not parts or 'text' not in parts[0]:
            return ""
        
        return parts[0]['text']
    
    def extract_json_from_text(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Extract JSON from text response
        
        Args:
            text: Text containing JSON
            
        Returns:
            Parsed JSON as dictionary, or None if parsing failed
        """
        # Find JSON content between triple backticks
        json_start = text.find("```json")
        if json_start == -1:
            json_start = text.find("```")
        
        if json_start != -1:
            # Move past the backticks
            json_start = text.find("{", json_start)
            if json_start == -1:
                return None
            
            # Find the end of the JSON
            json_end = text.rfind("}")
            if json_end == -1:
                return None
            
            json_str = text[json_start:json_end + 1]
            
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                return None
        
        # If no triple backticks, try to find JSON directly
        try:
            # Find the first { and last }
            json_start = text.find("{")
            json_end = text.rfind("}")
            
            if json_start != -1 and json_end != -1 and json_end > json_start:
                json_str = text[json_start:json_end + 1]
                return json.loads(json_str)
            
            return None
        except json.JSONDecodeError:
            return None
    
    def render_template(self, template_str: str, context: Dict[str, Any]) -> str:
        """
        Render a Jinja template with the given context
        
        Args:
            template_str: The template string
            context: The context dictionary
            
        Returns:
            The rendered template
        """
        template = self.jinja_env.from_string(template_str)
        return template.render(**context) 