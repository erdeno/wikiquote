import bz2
import xml.etree.ElementTree as ET
from neo4j import GraphDatabase
from dotenv import load_dotenv
import os

# Load credentials
load_dotenv()
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

# Initialize driver
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

# Limit constants
MAX_SHORT_TEXT_LEN = 1000  # For indexing
MAX_FULL_TEXT_LEN = 10000  # Just to be safe with memory

# Path to Wikiquote dump
DUMP_PATH = "data/enwikiquote-latest.xml.bz2"


def create_constraints(tx):
    """Create unique constraints on author name and short_text."""
    tx.run("""
    CREATE CONSTRAINT author_name_unique IF NOT EXISTS
    FOR (a:Author)
    REQUIRE a.name IS UNIQUE;
    """)
    tx.run("""
    CREATE CONSTRAINT quote_short_text_unique IF NOT EXISTS
    FOR (q:Quote)
    REQUIRE q.short_text IS UNIQUE;
    """)


def insert_quote(tx, author, quote):
    """Insert author and quote with MERGE for idempotency."""
    short_text = quote[:MAX_SHORT_TEXT_LEN]
    full_text = quote[:MAX_FULL_TEXT_LEN]
    tx.run("""
        MERGE (a:Author {name: $author})
        MERGE (q:Quote {short_text: $short_text})
        SET q.full_text = $full_text
        MERGE (a)-[:SAID]->(q)
    """, author=author, short_text=short_text, full_text=full_text)


def parse_wikiquote_dump(path):
    """Stream parse Wikiquote XML dump using bz2."""
    with bz2.open(path, "rt", encoding="utf-8") as f:
        for event, elem in ET.iterparse(f, events=("end",)):
            if elem.tag.endswith("page"):
                title = elem.findtext("./{*}title")
                text = elem.findtext(".//{*}text")
                if title and text:
                    yield title, text
                elem.clear()


def extract_quotes(text):
    """Simple heuristic to extract sentences with quotes."""
    quotes = []
    for line in text.split("\n"):
        line = line.strip()
        if len(line) > 10 and not line.startswith("=") and not line.startswith("* [["):
            quotes.append(line)
    return quotes


def build_graph():
    with driver.session() as session:
        session.execute_write(create_constraints)
        print("✅ Constraints ensured.")

        count = 0
        for title, text in parse_wikiquote_dump(DUMP_PATH):
            author = title.strip()
            quotes = extract_quotes(text)
            for quote in quotes:
                try:
                    session.execute_write(insert_quote, author, quote)
                    count += 1
                    if count % 1000 == 0:
                        print(f"Inserted {count} quotes...")
                except Exception as e:
                    print(f"⚠️ Skipped problematic quote: {e}")

        print(f"✅ Finished inserting {count} quotes.")


if __name__ == "__main__":
    print(f"Connecting to Neo4j at {NEO4J_URI}...")
    build_graph()
    driver.close()

