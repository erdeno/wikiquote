from neo4j import GraphDatabase

class Neo4jQuoteService:
    """Advanced Neo4j operations for quotes"""
    
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def close(self):
        self.driver.close()
    
    def get_similar_authors(self, author_name, limit=5):
        """Get authors with similar themes"""
        query = """
        MATCH (a1:Author {name: $author})-[:SAID_BY]-(q1:Quote)
        MATCH (q2:Quote)-[:SAID_BY]-(a2:Author)
        WHERE a1 <> a2
        WITH a2, count(DISTINCT q2) as quote_count
        RETURN a2.name as name, quote_count
        ORDER BY quote_count DESC
        LIMIT $limit
        """
        
        with self.driver.session() as session:
            result = session.run(query, author=author_name, limit=limit)
            return [record['name'] for record in result]
    
    def get_quotes_by_theme(self, theme, limit=10):
        """Get quotes containing theme keywords"""
        query = """
        MATCH (q:Quote)-[:SAID_BY]->(a:Author)
        WHERE toLower(q.text) CONTAINS toLower($theme)
        RETURN q.text as text, a.name as author
        LIMIT $limit
        """
        
        with self.driver.session() as session:
            result = session.run(query, theme=theme, limit=limit)
            return [{'text': r['text'], 'author': r['author']} for r in result]
    
    def get_random_quote(self):
        """Get a random quote"""
        query = """
        MATCH (q:Quote)-[:SAID_BY]->(a:Author)
        WITH q, a, rand() as random
        ORDER BY random
        LIMIT 1
        RETURN q.text as text, a.name as author
        """
        
        with self.driver.session() as session:
            result = session.run(query)
            record = result.single()
            if record:
                return {'text': record['text'], 'author': record['author']}
        return None