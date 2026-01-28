"""
AI Provider Services
Handles communication with different AI providers (Gemini, OpenAI, Claude, Ollama)
"""

import os
import time
import requests
from typing import Dict, List, Any, Optional
import google.generativeai as genai
from openai import OpenAI
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

# Load API keys
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://192.168.18.8:11434")
OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "300"))  # Default 5 minutes
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Initialize Gemini
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)


def get_model_status() -> Dict[str, Any]:
    """Get availability status of all AI providers."""
    status = {
        "Ollama": {"available": False, "models": []},
        "Gemini": {"available": bool(GOOGLE_API_KEY), "models": ["gemini-2.0-flash", "gemini-1.5-pro"]},
        "OpenAI": {"available": bool(OPENAI_API_KEY), "models": ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"]},
        "Claude": {"available": bool(ANTHROPIC_API_KEY), "models": ["claude-3-5-sonnet-20241022", "claude-3-opus-20240229", "claude-3-haiku-20240307"]}
    }
    
    # Check Ollama availability
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=3)
        if response.status_code == 200:
            ollama_models = [model["name"] for model in response.json().get("models", [])]
            if ollama_models:
                status["Ollama"]["available"] = True
                status["Ollama"]["models"] = ollama_models
    except:
        pass
    
    return status


def get_ollama_response(prompt: str, model: str, max_retries: int = 2) -> str:
    """Get response from Ollama API with extended timeout for large tasks."""
    for attempt in range(max_retries):
        try:
            # Extended timeout for CV enhancement tasks (configurable via env)
            response = requests.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json={"model": model, "prompt": prompt, "stream": False},
                timeout=OLLAMA_TIMEOUT
            )
            if response.status_code == 200:
                return response.json().get("response", "").strip()
            else:
                raise Exception(f"Ollama API returned status {response.status_code}")
        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                print(f"Ollama timeout on attempt {attempt + 1}, retrying...")
                time.sleep(3)
                continue
            else:
                raise Exception(
                    f"Ollama API timed out after {OLLAMA_TIMEOUT}s. The model '{model}' may be too slow for this task. "
                    f"Try using a faster model (e.g., llama3.2, qwen2.5) or switch to Gemini/OpenAI/Claude."
                )
        except requests.exceptions.ConnectionError:
            raise Exception(
                f"Cannot connect to Ollama at {OLLAMA_BASE_URL}. "
                f"Please ensure Ollama is running and accessible."
            )
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            else:
                raise Exception(f"Ollama API error: {str(e)}")


def get_gemini_response(prompt: str, model: str, max_retries: int = 3) -> str:
    """Get response from Gemini API."""
    gemini_model = genai.GenerativeModel(model)
    
    for attempt in range(max_retries):
        try:
            response = gemini_model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            else:
                raise Exception(f"Gemini API call failed: {str(e)}")


def get_openai_response(prompt: str, model: str, max_retries: int = 3) -> str:
    """Get response from OpenAI API."""
    client = OpenAI(api_key=OPENAI_API_KEY)
    
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            else:
                raise Exception(f"OpenAI API call failed: {str(e)}")


def get_claude_response(prompt: str, model: str, max_retries: int = 3) -> str:
    """Get response from Anthropic Claude API."""
    client = Anthropic(api_key=ANTHROPIC_API_KEY)
    
    for attempt in range(max_retries):
        try:
            response = client.messages.create(
                model=model,
                max_tokens=4096,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text.strip()
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            else:
                raise Exception(f"Claude API call failed: {str(e)}")


def get_ai_response(prompt: str, provider: str, model: str) -> str:
    """Unified function to get AI response from any provider."""
    provider_map = {
        "Ollama": get_ollama_response,
        "Gemini": get_gemini_response,
        "OpenAI": get_openai_response,
        "Claude": get_claude_response,
    }
    
    if provider not in provider_map:
        raise Exception(f"Unknown provider: {provider}")
    
    return provider_map[provider](prompt, model)
