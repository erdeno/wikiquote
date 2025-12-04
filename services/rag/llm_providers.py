import requests
import json
from typing import Optional, Dict, List
from abc import ABC, abstractmethod

class LLMProvider(ABC):
    """Base class for LLM providers"""
    
    @abstractmethod
    def generate(self, prompt: str, max_tokens: int = 200, temperature: float = 0.7) -> str:
        pass


class OllamaProvider(LLMProvider):
    """Local LLM using Ollama"""
    
    def __init__(self, model: str = "llama3.2:3b", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url
        
        # Check if Ollama is available
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                available_models = [m['name'] for m in response.json().get('models', [])]
                print(f"✓ Ollama available. Models: {available_models}")
                
                if self.model not in available_models:
                    print(f"⚠ Model {self.model} not found. Available: {available_models}")
                    print(f"  Run: ollama pull {self.model}")
            else:
                print(f"⚠ Ollama responded with status {response.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"✗ Cannot connect to Ollama at {self.base_url}")
            print(f"  Make sure Ollama is running: 'ollama serve'")
        except Exception as e:
            print(f"⚠ Error checking Ollama: {e}")
        
        print(f"Ollama provider initialized (model: {model})")
    
    def generate(self, prompt: str, max_tokens: int = 200, temperature: float = 0.7) -> str:
        """Generate text using Ollama"""
        
        # Updated API endpoint - use /api/generate
        url = f"{self.base_url}/api/generate"
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
                "stop": ["\n\n", "User:", "Assistant:"]  # Stop tokens
            }
        }
        
        try:
            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            return result.get('response', '').strip()
            
        except requests.exceptions.ConnectionError:
            raise Exception(
                "Cannot connect to Ollama. "
                "Make sure it's running with: 'ollama serve'\n"
                f"Tried to connect to: {self.base_url}"
            )
        except requests.exceptions.Timeout:
            raise Exception("Ollama request timed out. Model might be loading.")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise Exception(
                    f"Model '{self.model}' not found. "
                    f"Install it with: 'ollama pull {self.model}'"
                )
            raise Exception(f"Ollama HTTP error: {e}")
        except Exception as e:
            raise Exception(f"Ollama generation failed: {e}")


class LLMFactory:
    """Factory to create LLM providers"""
    
    @staticmethod
    def create(provider: str, **kwargs) -> LLMProvider:
        """
        Create LLM provider
        
        Args:
            provider: 'ollama', 'openai', or 'anthropic'
            **kwargs: Provider-specific arguments
        """
        
        if provider == "ollama":
            return OllamaProvider(
                model=kwargs.get('model', 'llama3.2:3b'),
                base_url=kwargs.get('base_url', 'http://localhost:11434')
            )
        else:
            raise ValueError(f"Unknown provider: {provider}")