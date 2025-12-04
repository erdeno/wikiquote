import os
import sys

# Get the backend directory path (parent of services directory)
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from neo4j import GraphDatabase
from services.rag.embeddings import EmbeddingService
import time
from tqdm import tqdm  # Progress bar

from dotenv import load_dotenv
# Load credentials
load_dotenv()
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

def generate_embeddings(limit=None, batch_size=50):
    """Generate embeddings for all quotes"""
    
    print("🔌 Connecting to Neo4j...")
    driver = GraphDatabase.driver(
        NEO4J_URI,
        auth=(NEO4J_USER, NEO4J_PASSWORD)
    )
    
    print("🤖 Initializing embedding service...")
    embedder = EmbeddingService()
    
    # Get count first
    with driver.session() as session:
        count_result = session.run("""
            MATCH (q:Quote)
            WHERE q.embedding IS NULL
            RETURN count(q) as total
        """)
        total = count_result.single()['total']
    
    print(f"📊 Found {total} quotes without embeddings")
    
    if total == 0:
        print("✅ All quotes already have embeddings!")
        driver.close()
        return
    
    if limit:
        total = min(total, limit)
        print(f"🎯 Processing first {total} quotes")
    
    # Process in batches with progress bar
    processed = 0
    
    with tqdm(total=total, desc="Generating embeddings") as pbar:
        while processed < total:
            # Fetch batch
            with driver.session() as session:
                result = session.run("""
                    MATCH (q:Quote)
                    WHERE q.embedding IS NULL
                    RETURN elementId(q) as id, 
                           coalesce(q.short_text, q.full_text, q.text) as text
                    LIMIT $batch_size
                """, batch_size=batch_size)
                batch = list(result)
            
            if not batch:
                break
            
            # Process batch
            for quote in batch:
                try:
                    text = quote['text']
                    if not text or len(text.strip()) < 5:
                        continue
                    
                    # Generate embedding
                    embedding = embedder.embed_text(text)
                    embedding_list = embedding.tolist()
                    
                    # Store in Neo4j
                    with driver.session() as session:
                        session.run("""
                            MATCH (q:Quote)
                            WHERE elementId(q) = $id
                            SET q.embedding = $embedding
                        """, id=quote['id'], embedding=embedding_list)
                    
                    processed += 1
                    pbar.update(1)
                    
                except Exception as e:
                    print(f"\n⚠️  Error: {e}")
                    continue
            
            time.sleep(0.1)  # Brief pause
    
    print(f"\n✅ Successfully generated embeddings for {processed} quotes!")
    driver.close()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate embeddings for quotes')
    parser.add_argument('--limit', type=int, help='Limit number of quotes to process')
    parser.add_argument('--batch-size', type=int, default=50, help='Batch size')
    
    args = parser.parse_args()
    
    try:
        generate_embeddings(limit=args.limit, batch_size=args.batch_size)
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()