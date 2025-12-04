import sys
import os

# Add to path
sys.path.insert(0, os.path.dirname(__file__))

from llm_providers import LLMFactory

def test_ollama_connection():
    """Test Ollama connection"""
    import requests
    
    print("Testing Ollama connection...")
    try:
        response = requests.get("http://localhost:11434/api/version", timeout=5)
        if response.status_code == 200:
            print("✓ Ollama is running")
            print(f"  Version: {response.json()}")
            return True
        else:
            print(f"✗ Ollama returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to Ollama")
        print("  Start it with: ollama serve")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_ollama_models():
    """Check available models"""
    import requests
    
    print("\nChecking available models...")
    try:
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code == 200:
            models = response.json().get('models', [])
            if models:
                print(f"✓ Found {len(models)} models:")
                for model in models:
                    print(f"  - {model['name']}")
                return True
            else:
                print("✗ No models installed")
                print("  Install one with: ollama pull llama3.2:3b")
                return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_ollama_generation():
    """Test text generation"""
    print("\n" + "="*60)
    print("Testing Ollama Generation")
    print("="*60)
    
    try:
        ollama = LLMFactory.create("ollama", model="llama3.2:3b")
        
        prompt = """Context: "To be or not to be" - Shakespeare

User asks: "What does this mean?"

Respond in 2-3 sentences:"""
        
        print(f"\nPrompt: {prompt}\n")
        print("Generating (this may take a few seconds)...")
        
        response = ollama.generate(prompt, max_tokens=150)
        
        print(f"\n✓ Response:\n{response}\n")
        return True
        
    except Exception as e:
        print(f"\n✗ Generation failed: {e}")
        return False

def test_full_rag():
    """Test full RAG system"""
    print("\n" + "="*60)
    print("Testing Full RAG System")
    print("="*60)
    
    try:
        from rag_chatbot import RAGChatbot
        
        # Update with your Neo4j credentials
        NEO4J_URI = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
        NEO4J_USER = os.getenv('NEO4J_USER', 'neo4j')
        NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD', 'your_password')
        
        print(f"\nConnecting to Neo4j at {NEO4J_URI}...")
        
        chatbot = RAGChatbot(
            neo4j_uri=NEO4J_URI,
            neo4j_user=NEO4J_USER,
            neo4j_password=NEO4J_PASSWORD,
            llm_provider="ollama",
            llm_config={'model': 'llama3.2:3b'}
        )
        
        queries = [
            "Tell me about love",
            "What is wisdom?",
        ]
        
        for query in queries:
            print(f"\n{'─'*60}")
            print(f"Query: {query}")
            print('─'*60)
            
            result = chatbot.query(query, username="Test", accent="american")
            
            print(f"\nResponse: {result['response']}")
            print(f"\nMethod: {result['method']}")
            
            if result['quotes']:
                print(f"\nTop quote:")
                quote = result['quotes'][0]
                print(f"  \"{quote['text'][:100]}...\"")
                print(f"  - {quote['author']} (similarity: {quote['similarity']:.3f})")
        
        chatbot.close()
        print("\n✓ RAG system test complete!")
        return True
        
    except Exception as e:
        print(f"\n✗ RAG test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("="*60)
    print("Ollama + RAG System Test")
    print("="*60)
    
    # Run tests
    if not test_ollama_connection():
        print("\n⚠ Fix Ollama connection before proceeding")
        sys.exit(1)
    
    if not test_ollama_models():
        print("\n⚠ Install a model before proceeding")
        sys.exit(1)
    
    if not test_ollama_generation():
        print("\n⚠ Fix Ollama generation before testing RAG")
        sys.exit(1)
    
    # Only test RAG if basic tests pass
    print("\n" + "="*60)
    print("Basic tests passed! Now testing full RAG system...")
    print("="*60)
    
    test_full_rag()