# services/etl/build_graph.py
import os
from neo4j import GraphDatabase
from bs4 import BeautifulSoup
from tqdm import tqdm
import requests
import bz2

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

class WikiquoteGraphBuilder:
    def __init__(self):
        print(f"Connecting to Neo4j Aura at {NEO4J_URI} ...")
        self.driver = GraphDatabase.driver(
                NEO4J_URI, 
                auth=(NEO4J_USER, NEO4J_PASSWORD)
        )

    def close(self):
        self.driver.close()

    def create_constraints(self):
        with self.driver.session() as session:
            session.run("CREATE CONSTRAINT author_name IF NOT EXISTS FOR (a:Author) REQUIRE a.name IS UNIQUE")
            session.run("CREATE CONSTRAINT quote_text IF NOT EXISTS FOR (q:Quote) REQUIRE q.text IS UNIQUE")

    def add_quote(self, author, quote, source=None):
        with self.driver.session() as session:
            session.run(
                """
                MERGE (a:Author {name: $author})
                MERGE (q:Quote {text: $quote})
                MERGE (a)-[:SAID]->(q)
                """,
                {"author": author, "quote": quote}
            )

    def build_from_dump(self, dump_path):
        with bz2.open(dump_path, 'rt', encoding='utf-8', errors='ignore') as f:
            soup = BeautifulSoup(f, 'xml')
            pages = soup.find_all('page')

            for p in tqdm(pages):
                title = p.find('title').text
                text = p.find('text')
                if text and "==Quotes==" in text.text:
                    quotes = [line.strip("* ").strip() for line in text.text.split('\n') if line.startswith('*')]
                    for q in quotes:
                        if len(q.split()) > 3:
                            self.add_quote(title, q)

if __name__ == "__main__":
    builder = WikiquoteGraphBuilder()
    builder.create_constraints()

    dump_url = "https://dumps.wikimedia.org/enwikiquote/20251001/enwikiquote-20251001-pages-articles.xml.bz2"
    dump_file = "data/enwikiquote-latest.xml.bz2"

    if not os.path.exists(dump_file):
        print("Downloading Wikiquote dump...")
        r = requests.get(dump_url, stream=True)
        with open(dump_file, "wb") as f:
            for chunk in tqdm(r.iter_content(chunk_size=8192)):
                if chunk:
                    f.write(chunk)

    builder.build_from_dump(dump_file)
    builder.close()

