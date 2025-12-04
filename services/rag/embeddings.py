"""
Embedding service for semantic search - Ollama only
"""
import numpy as np
from typing import List, Union
import requests

class EmbeddingService:
    """Generate embeddings using Ollama"""
    
    def __init__(self, model: str = None):
        """
        Initialize embedding service with Ollama
        
        Args:
            model: Model name (default: nomic-embed-text)
        """
        self.base_url = "http://localhost:11434"
        self.model_name = model or "nomic-embed-text"
        
        try:
            # Test connection
            response = requests.get(f"{self.base_url}/api/tags", timeout=2)
            if response.status_code != 200:
                raise ConnectionError(f"Ollama returned status {response.status_code}")
            
            models_data = response.json()
            models = models_data.get('models', [])
            model_names = [m.get('name', '') for m in models]
            
            # Check for exact match or with :latest suffix
            model_found = (
                self.model_name in model_names or 
                f"{self.model_name}:latest" in model_names
            )
            
            if not model_found:
                print(f"⚠️  Model '{self.model_name}' not found")
                print(f"    Available: {model_names}")
                print(f"    Run: ollama pull {self.model_name}")
                raise ConnectionError(f"Model {self.model_name} not available")
            
            # Use the full name with :latest if that's what exists
            if f"{self.model_name}:latest" in model_names and self.model_name not in model_names:
                self.model_name = f"{self.model_name}:latest"
            
            print(f"✓ Connected to Ollama: {self.model_name}")
            
        except requests.exceptions.RequestException as e:
            raise ConnectionError(
                f"Cannot connect to Ollama at {self.base_url}. "
                f"Make sure Ollama is running with 'ollama serve'. Error: {e}"
            )
    
    def embed_text(self, text: Union[str, List[str]]) -> np.ndarray:
        """
        Generate embeddings for text using Ollama
        
        Args:
            text: Single string or list of strings
            
        Returns:
            numpy array of embeddings
        """
        if isinstance(text, str):
            text = [text]
        
        embeddings = []
        for t in text:
            try:
                response = requests.post(
                    f"{self.base_url}/api/embeddings",
                    json={"model": self.model_name, "prompt": t},
                    timeout=30
                )
                response.raise_for_status()
                data = response.json()
                
                # Handle different possible response formats
                if 'embedding' in data:
                    embeddings.append(data['embedding'])
                elif 'embeddings' in data:
                    embeddings.append(data['embeddings'][0])
                else:
                    raise KeyError(f"Unexpected response format: {list(data.keys())}")
                    
            except Exception as e:
                print(f"Error embedding text '{t[:50]}...': {e}")
                raise
        
        result = np.array(embeddings)
        return result[0] if len(text) == 1 else result
    
    @staticmethod
    def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors"""
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        return float(dot_product / (norm1 * norm2))