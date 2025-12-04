from neo4j import GraphDatabase
from dotenv import load_dotenv
import os

# Load credentials
load_dotenv()
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

print("="*60)
print("Neo4j Schema Discovery")
print("="*60)

with driver.session() as session:
    # 1. Node labels
    print("\n1. Node Labels:")
    result = session.run("CALL db.labels()")
    labels = [record[0] for record in result]
    print(f"   Found: {labels}")
    
    # 2. Relationship types
    print("\n2. Relationship Types:")
    result = session.run("CALL db.relationshipTypes()")
    rel_types = [record[0] for record in result]
    print(f"   Found: {rel_types}")
    
    # 3. Sample data structure
    print("\n3. Sample Data Structure:")
    result = session.run("""
        MATCH (q:Quote)-[r]->(n)
        RETURN labels(q) as from_label, 
               type(r) as relationship, 
               labels(n) as to_label,
               keys(q) as quote_properties
        LIMIT 5
    """)
    
    for record in result:
        print(f"   {record['from_label']} -[{record['relationship']}]-> {record['to_label']}")
        print(f"   Quote properties: {record['quote_properties']}")
    
    # 4. Count quotes
    print("\n4. Statistics:")
    result = session.run("MATCH (q:Quote) RETURN count(q) as count")
    count = result.single()['count']
    print(f"   Total quotes: {count}")
    
    # 5. Sample quote
    print("\n5. Sample Quote:")
    result = session.run("""
        MATCH (q:Quote)
        RETURN q
        LIMIT 1
    """)
    
    sample = result.single()
    if sample:
        quote = sample['q']
        print(f"   Properties: {dict(quote)}")
    
    # 6. Check for fulltext index
    print("\n6. Fulltext Indexes:")
    try:
        result = session.run("SHOW INDEXES")
        indexes = list(result)
        for idx in indexes:
            if 'fulltext' in str(idx).lower():
                print(f"   {idx}")
    except:
        print("   Could not check indexes")

driver.close()

print("\n" + "="*60)
print("Schema discovery complete!")
print("="*60)