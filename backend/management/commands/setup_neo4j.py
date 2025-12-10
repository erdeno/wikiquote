from django.core.management.base import BaseCommand
from neomodel import db

class Command(BaseCommand):
    help = 'Setup Neo4j constraints and indexes'
    
    def handle(self, *args, **options):
        # Create unique constraints
        db.cypher_query("""
            CREATE CONSTRAINT user_username IF NOT EXISTS
            FOR (u:NeoUser) REQUIRE u.username IS UNIQUE
        """)
        
        db.cypher_query("""
            CREATE CONSTRAINT user_email IF NOT EXISTS
            FOR (u:NeoUser) REQUIRE u.email IS UNIQUE
        """)
        
        db.cypher_query("""
            CREATE CONSTRAINT token_key IF NOT EXISTS
            FOR (t:NeoAuthToken) REQUIRE t.key IS UNIQUE
        """)
        
        self.stdout.write(self.style.SUCCESS('Neo4j constraints created'))
