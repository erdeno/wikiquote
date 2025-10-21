# index_quotes.py
from neo4j import GraphDatabase
from elasticsearch import Elasticsearch
from dotenv import load_dotenv
import os

load_dotenv()

# Connect to Neo4j
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

# Connect to Elasticsearch
es = Elasticsearch("http://localhost:9200")

INDEX_NAME = "wikiquote"

# Create index (if not exists)
if not es.indices.exists(index=INDEX_NAME):
    es.indices.create(index=INDEX_NAME, body={
        "settings": {"number_of_shards": 1},
        "mappings": {
            "properties": {
                "quote": {"type": "text"},
                "author": {"type": "keyword"}
            }
        }
    })

def fetch_quotes(tx):
    query = """
    MATCH (a:Author)-[:SAID]->(q:Quote)
    RETURN a.name AS author, q.text AS quote
    """
    return list(tx.run(query))

with driver.session() as session:
    results = session.read_transaction(fetch_quotes)
    print(f"Indexing {len(results)} quotes...")

    for record in results:
        doc = {
            "quote": record["quote"],
            "author": record["author"]
        }
        es.index(index=INDEX_NAME, body=doc)

print("✅ Finished indexing quotes.")
driver.close()

