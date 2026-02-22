from neo4j import GraphDatabase
from .embeddings import EmbeddingService
from .llm_providers import LLMFactory
import numpy as np
from typing import List, Dict
import os

class RAGChatbot:
    """RAG-based chatbot with local LLM support"""
    
    def __init__(self, neo4j_uri, neo4j_user, neo4j_password, 
                 llm_provider="ollama", llm_config=None):
        """
        Initialize RAG chatbot
        
        Args:
            llm_provider: 'ollama', 'openai', or 'anthropic'
            llm_config: Dict with provider-specific config
        """
        self.driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
        self.embedder = EmbeddingService()
        
        # Initialize LLM
        llm_config = llm_config or {}
        
        if llm_provider == "ollama":
            self.llm = LLMFactory.create(
                "ollama",
                model=llm_config.get('model', 'llama3.2:3b'),
                base_url=llm_config.get('base_url', 'http://ollama:11434')
            )
        elif llm_provider == "openai":
            self.llm = LLMFactory.create(
                "openai",
                api_key=llm_config.get('api_key') or os.getenv('OPENAI_API_KEY'),
                model=llm_config.get('model', 'gpt-3.5-turbo')
            )
        elif llm_provider == "anthropic":
            self.llm = LLMFactory.create(
                "anthropic",
                api_key=llm_config.get('api_key') or os.getenv('ANTHROPIC_API_KEY'),
                model=llm_config.get('model', 'claude-3-haiku-20240307')
            )
        else:
            raise ValueError(f"Unknown LLM provider: {llm_provider}")
    
    def close(self):
        self.driver.close()
    
    def retrieve_similar_quotes(self, query: str, top_k: int = 5) -> List[Dict]:
        """Retrieve most similar quotes - undirected relationship"""
        
        query_embedding = self.embedder.embed_text(query)
        
        # Undirected match works both ways
        cypher = """
        MATCH (q:Quote)-[:SAID]-(a:Author)
        OPTIONAL MATCH (q)-[:FROM]->(w:Work)
        WHERE q.embedding IS NOT NULL
        RETURN elementId(q) as id, 
            coalesce(q.short_text, q.full_text, q.text) as text,
            q.full_text as full_text,
            q.embedding as embedding, 
            coalesce(a.name, 'Unknown') as author,
            w.title as work
        LIMIT 500
        """
        
        with self.driver.session() as session:
            result = session.run(cypher)
            quotes = list(result)
        
        similarities = []
        for quote in quotes:
            quote_embedding = np.array(quote['embedding'])
            similarity = self.embedder.cosine_similarity(query_embedding, quote_embedding)
            
            similarities.append({
                'text': quote.get('text') or quote.get('full_text', ''),
                'author': quote.get('author', 'Unknown'),
                'work': quote.get('work'),  # ← Use .get() method to safely handle NULL
                'similarity': similarity
            })
        
        similarities.sort(key=lambda x: x['similarity'], reverse=True)
        return similarities[:top_k]
    
    def generate_response(self, query: str, context_quotes: List[Dict], 
                         username: str = None, accent: str = "american") -> str:
        """Generate response using LLM with retrieved context"""
        
        # Build context
        context = "Relevant quotes:\n\n"
        for i, quote in enumerate(context_quotes, 1):
            context += f"{i}. \"{quote['text']}\" - {quote['author']}"
            if quote['work']:
                context += f" ({quote['work']})"
            context += "\n"
        
        user_greeting = username or "there"
        
        accent_styles = {
            'american': "casual and friendly",
            'uk': "polite and formal",
            'mexican': "warm and expressive",
            'french': "elegant",
            'irish': "cheerful",
            'indian': "respectful",
            'african': "warm",
            'italian': "expressive",
            'german': "precise"
        }
        
        style = accent_styles.get(accent, "friendly")
        
        prompt = f"""You are a wise quote assistant speaking in a {style} manner.

User: "{query}"

{context}

Task: Respond to the user's query using the quotes above.
- Address the user as {user_greeting}
- Reference the most relevant quote
- Keep response to 2-3 sentences
- Be {style}

Response:"""
        
        # Generate with LLM
        response = self.llm.generate(prompt, max_tokens=150, temperature=0.7)
        return response.strip()
    
    def query(self, user_query: str, username: str = None, accent: str = "american") -> Dict:
        """Full RAG pipeline"""
        
        similar_quotes = self.retrieve_similar_quotes(user_query, top_k=3)
        
        if not similar_quotes or similar_quotes[0]['similarity'] < 0.3:
            return {
                'response': f"I couldn't find relevant quotes about that. Try asking about something else!",
                'quotes': [],
                'method': 'fallback'
            }
        
        response = self.generate_response(user_query, similar_quotes, username, accent)
        
        return {
            'response': response,
            'quotes': similar_quotes,
            'method': 'rag'
        }