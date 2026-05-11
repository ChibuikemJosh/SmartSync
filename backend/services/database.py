"""
Database configuration and connection management
"""

from neo4j import GraphDatabase
import os
from datetime import datetime

class GraphService:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            os.getenv("NEO4J_URI"), 
            auth=(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD"))
        )

    def close(self):
        self.driver.close()

    def log_transaction(self, user_id, tx_data):
        """Saves AI-parsed transaction and boosts Trust Score"""
        with self.driver.session() as session:
            return session.execute_write(self._create_tx_node, user_id, tx_data)

    @staticmethod
    def _create_tx_node(tx, user_id, data):
        # This query: 1. Finds user, 2. Creates transaction, 3. Connects them, 4. Boosts score
        query = """
        MATCH (u:User {id: $user_id})
        CREATE (t:Transaction {
            item: $item,
            amount: $amount,
            type: $type,
            timestamp: $timestamp,
            verified: false
        })
        CREATE (u)-[:PERFORMED]->(t)
        SET u.trust_score = u.trust_score + 2  // Basic boost for logging
        RETURN u.trust_score as new_score
        """
        result = tx.run(query, 
            user_id=user_id, 
            item=data['item'], 
            amount=data['amount'], 
            type=data['type'],
            timestamp=datetime.now().isoformat()
        )
        return result.single()
