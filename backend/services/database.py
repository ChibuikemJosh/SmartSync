"""
Database configuration and connection management
"""

from neo4j import GraphDatabase
import os
from dotenv import load_dotenv
from datetime import datetime
import math
from datetime import timezone

load_dotenv()

class GraphService:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            os.getenv("NEO4J_URI", ""), 
            auth=(os.getenv("NEO4J_USER", ""), os.getenv("NEO4J_PASSWORD", ""))
        )

    def close(self):
        self.driver.close()

    def log_transaction(self, user_id, tx_data):
        """Logs the sale, then recalculates the dynamic Trust Score"""
        with self.driver.session() as session:
            # 1. Create the new transaction node
            session.execute_write(self._create_tx_node_only, user_id, tx_data)
            
            # 2. Fetch all transactions to calculate the new decayed score
            history = session.execute_read(self._get_user_history, user_id)
            
            # 3. Calculate the new score in Python
            new_score = self.calculate_decayed_score(history)
            
            # 4. Save the new score back to the User node
            session.execute_write(self._update_user_score, user_id, new_score)
            
            return new_score
        
    @staticmethod
    def _create_tx_node_only(tx, user_id, data):
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
        """
        tx.run(query, 
            user_id=user_id, 
            item=data['item'], 
            amount=data['amount'], 
            type=data['type'],
            timestamp=datetime.now(timezone.utc).isoformat()
        )
    
    @staticmethod
    def _get_user_history(tx, user_id):
        query = """
        MATCH (u:User {id: $user_id})-[:PERFORMED]->(t:Transaction)
        RETURN t.amount as amount, t.timestamp as timestamp, t.verified as verified
        """
        result = tx.run(query, user_id=user_id)
        return [record.data() for record in result]
    
    @staticmethod
    def _update_user_score(tx, user_id, score):
        tx.run("MATCH (u:User {id: $user_id}) SET u.trust_score = $score", 
               user_id=user_id, score=score)

    @staticmethod
    def calculate_decayed_score(transactions, half_life_days=14):
        """The 'Intelligent' part of the economy"""
        if not transactions:
            return 43 # Starting base score

        total_weighted_points = 0
        lambda_constant = math.log(2) / half_life_days
        now = datetime.now(timezone.utc)

        for tx in transactions:
            tx_time = datetime.fromisoformat(tx['timestamp'])
            days_ago = (now - tx_time).total_seconds() / 86400 # Convert to days
            
            # Weight based on time (Exponential Decay)
            weight = math.exp(-lambda_constant * days_ago)
            
            # Points: Verified transactions are 5x more valuable than voice logs alone
            base_points = 15 if tx['verified'] else 3
            
            total_weighted_points += (base_points * weight)

        # Logarithmic Scaling: math.log(x, base)
        # This ensures the score doesn't just grow to 10,000. It curves.
        log_scaled = 40 + (math.log(total_weighted_points + 1, 1.1))
        
        return min(100, round(log_scaled))
    
def get_user_dashboard(self, user_id):
    """
    Fetches the profile, current score, and recent transaction history.
    """
    with self.driver.session() as session:
        query = """
        MATCH (u:User {id: $user_id})
        OPTIONAL MATCH (u)-[:PERFORMED]->(t:Transaction)
        WITH u, t
        ORDER BY t.timestamp DESC
        LIMIT 10
        RETURN u.name as name, 
               u.trust_score as score, 
               u.role as role,
               collect({
                   item: t.item,
                   amount: t.amount,
                   type: t.type,
                   verified: t.verified,
                   timestamp: t.timestamp
               }) as transactions
        """
        result = session.run(query, user_id=user_id).single()
        
        if not result:
            return None
            
        data = result.data()
        # Add Tiering logic
        data['tier'] = self.get_score_tier(data['score'])
        return data

@staticmethod
def get_score_tier(score):
    if score >= 90: return {"name": "Elite", "color": "#FFD700", "next": 100}
    if score >= 75: return {"name": "Established", "color": "#C0C0C0", "next": 90}
    if score >= 60: return {"name": "Trusted", "color": "#CD7F32", "next": 75}
    if score >= 45: return {"name": "Growing", "color": "#4CAF50", "next": 60}
    return {"name": "New", "color": "#2196F3", "next": 45}


def verify_transaction(self, user_id, amount):
    """
    Finds the most recent unverified 'SALE' of a similar amount 
    and marks it as verified.
    """
    with self.driver.session() as session:
        query = """
        MATCH (u:User {id: $user_id})-[:PERFORMED]->(t:Transaction {type: 'SALE', verified: false})
        WHERE t.amount >= $min_amount AND t.amount <= $max_amount
        WITH t
        ORDER BY t.timestamp DESC
        LIMIT 1
        SET t.verified = true, t.verified_at = $v_time
        RETURN t.item as item
        """
        # We allow a small margin (e.g., +/- 10%) in case of fees or rounding
        result = session.run(query, 
            user_id=user_id, 
            min_amount=amount * 0.9, 
            max_amount=amount * 1.1,
            v_time=datetime.now(timezone.utc).isoformat()
        )
        return result.single()