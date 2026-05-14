"""
Database configuration and connection management
"""

from neo4j import GraphDatabase
import os
from dotenv import load_dotenv
from datetime import datetime
import math
from datetime import timezone
import uuid

load_dotenv()

class GraphService:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            os.getenv("NEO4J_URI", ""), 
            auth=(os.getenv("NEO4J_USER", ""), os.getenv("NEO4J_PASSWORD", ""))
        )

    def close(self):
        self.driver.close()

    def create_user_node(self, user_data):
        """Creates a new user with location and base score"""
        with self.driver.session() as session:
            query = """
            MERGE (u:User {id: $id})
            SET u.name = $name,
                u.role = $role,
                u.email = $email,
                u.password = $password,
                u.city = $city,
                u.state = $state,
                u.country = $country,
                u.trust_score = $trust_score,
                u.skills = $skills,
                u.created_at = $created_at
            RETURN u.id
            """

            loc = user_data.get('location', {})

            session.run(query,
                id=user_data['id'],
                name=user_data['name'],
                email=user_data['email'], # Save email
                password=user_data['password'], # Save password
                role=user_data['role'],
                city=loc.get('city'),
                state=loc.get('state'),
                country=loc.get('country'),
                trust_score=user_data.get('trust_score', 43),
                skills=user_data.get('skills', []),
                created_at=datetime.now(timezone.utc).isoformat()
            )

    def log_transaction(self, user_id, tx_data):
        """Logs the sale, then recalculates the dynamic Trust Score"""
        with self.driver.session() as session:
            query = """
            MATCH (u:User {id: $user_id})
            CREATE (t:Transaction {
                id: $tx_id,
                item: $item,
                amount: $amount,
                quantity: $quantity,
                unit: $unit,
                type: $type,
                notes: $notes,
                timestamp: $timestamp,
                verified: $verified,
                is_anomaly: $is_anomaly
            })
            CREATE (u)-[:PERFORMED]->(t)
            RETURN t
            """
            # Ensure we have defaults for missing fields (like from Squad webhooks)
            tx_id = str(uuid.uuid4())
            timestamp = tx_data.get('timestamp') or datetime.now(timezone.utc).isoformat()
        
            session.run(query, 
                user_id=user_id,
                tx_id=tx_id,
                item=tx_data.get('item', 'Unknown'),
                amount=tx_data.get('amount', 0),
                quantity=tx_data.get('quantity', 1),
                unit=tx_data.get('unit', 'unit'),
                type=tx_data.get('type', 'SALE'),
                notes=tx_data.get('notes', ''),
                timestamp=timestamp,
                verified=tx_data.get('verified', False),
                is_anomaly=tx_data.get('is_anomaly', False)
            )

            # 2. Fetch all transactions to calculate the new decayed score
            history = session.execute_read(self.get_user_history, user_id)
            
            # 3. Calculate the new score in Python
            new_score = self.calculate_decayed_score(history)
            
            # 4. Save the new score back to the User node
            session.execute_write(self.update_user_score, user_id, new_score)
            
            return self.recalculate_user_score(user_id) # Return the updated score for frontend display 
        
    @staticmethod
    def _create_tx_node_only(tx, user_id, data):
        query = """
        MATCH (u:User {id: $user_id})
        CREATE (t:Transaction {
            item: $item,
            amount: $amount,
            quantity: $quantity,
            type: $type,
            timestamp: $timestamp,
            is_anomaly: $is_anomaly,
            verified: false
        })
        CREATE (u)-[:PERFORMED]->(t)
        """
        tx.run(query, 
            user_id=user_id, 
            item=data['item'], 
            amount=data.get('amount', 0), 
            quantity=data.get('quantity', 1),
            type=data['type'],
            timestamp=datetime.now(timezone.utc).isoformat(),
            is_anomaly=data.get('is_anomaly', False)
        )

    def create_escrow(self, gig_id, trader_id, worker_id, amount):
        """Creates a Gig node and links Trader and Worker in an Escrow relationship."""
        with self.driver.session() as session:
            query = """
            MATCH (t:User {id: $trader_id}), (w:User {id: $worker_id})
            CREATE (g:Gig {id: $gig_id, amount: $amount, status: 'locked', created_at: datetime()})
            CREATE (t)-[:FUNDED]->(g)
            CREATE (w)-[:ASSIGNED_TO]->(g)
            """
            session.run(query, gig_id=gig_id, trader_id=trader_id, worker_id=worker_id, amount=amount)

    def release_escrow_status(self, gig_id):
        """Updates Gig status to released and timestamps the payout."""
        with self.driver.session() as session:
            query = """
            MATCH (g:Gig {id: $gig_id})
            SET g.status = 'released', 
                g.released_at = datetime()
            RETURN g.id
            """
            session.run(query, gig_id=gig_id)

    def get_gig_details(self, gig_id):
        """Fetches Gig info to replace your teammate's placeholders."""
        with self.driver.session() as session:
            query = """
            MATCH (w:User)-[:ASSIGNED_TO]->(g:Gig {id: $gig_id})<-[:FUNDED]-(t:User)
            RETURN g.amount as amount, g.status as status, w.account_number as worker_acc, 
                   w.id as worker_id, t.id as trader_id, w.bank_code as bank_code
            """
            result = session.run(query, gig_id=gig_id).single()
            return result.data() if result else None

    def refund_escrow_status(self, gig_id, canceled_by="trader"):
        """
        Marks the gig as refunded and records who canceled.
        """
        with self.driver.session() as session:
            query = """
            MATCH (g:Gig {id: $gig_id})
            WHERE g.status = 'locked'
            SET g.status = 'refunded', 
                g.canceled_by = $canceled_by,
                g.refunded_at = datetime()
            RETURN g.id
            """
            result = session.run(query, gig_id=gig_id, canceled_by=canceled_by).single()
            return result is not None

    @staticmethod
    def get_user_history(tx, user_id):
        query = """
        MATCH (u:User {id: $user_id})-[:PERFORMED]->(t:Transaction)
        RETURN t.amount as amount, t.timestamp as timestamp, t.verified as verified, t.is_anomaly as is_anomaly
        """
        result = tx.run(query, user_id=user_id)
        return [record.data() for record in result]
    
    def get_history(self, user_id):
        with self.driver.session() as session:
            return session.execute_read(self._get_user_history, user_id)

    @staticmethod
    def update_user_score(tx, user_id, score):
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

            if tx.get('is_anomaly'):
                      base_points = -20 # Huge penalty for anomalies
            else:
                # Points: Verified transactions are 5x more valuable than voice logs alone
                base_points = 15 if tx['verified'] else 3
            
            total_weighted_points += (base_points * weight)

        # Logarithmic Scaling: math.log(x, base)
        # This ensures the score doesn't just grow to 10,000. It curves.
        log_scaled = 40 + (math.log(total_weighted_points + 1, 1.1))
        
        return min(100, round(log_scaled))
    
    def update_user_virtual_account(self, user_id, account_number, bank_name):
        """Saves the Squad virtual account info to the User node."""
        with self.driver.session() as session:
            query = """
            MATCH (u:User {id: $user_id})
            SET u.virtual_account = $account_number,
                u.bank_name = $bank_name
            RETURN u
            """
            session.run(query, user_id=user_id, account_number=account_number, bank_name=bank_name)

    def recalculate_user_score(self, user_id):
        """Recalculates the user's score based on all their transactions."""
        with self.driver.session() as session:
            history = session.execute_read(self.get_user_history, user_id)
            new_score = self.calculate_decayed_score(history)
            session.execute_write(self.update_user_score, user_id, new_score)
            return new_score
    
    def get_user_by_email(self, email: str):
        """Fetches a user and their hashed password for authentication"""
        with self.driver.session() as session:
            query = """
            MATCH (u:User {email: $email})
            RETURN u.id as id, u.name as name, u.password as password, 
                   u.role as role, u.trust_score as trust_score
            """
            result = session.run(query, email=email).single()
            return result.data() if result else None
    
    def get_user_by_id(self, user_id: str):
        """Fetches a user profile by their ID (used by JWT dependency)"""
        with self.driver.session() as session:
            query = """
            MATCH (u:User {id: $user_id})
            RETURN u.id as id, u.name as name, u.email as email, 
                   u.role as role, u.trust_score as trust_score,
                   u.city as city, u.state as state, u.country as country
            """
            result = session.run(query, user_id=user_id).single()
            return result.data() if result else None

    def get_user_dashboard(self, user_id):
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
                   u.city as city, u.state as state, u.country as country,
                   collect({
                       item: t.item,
                       amount: t.amount,
                       type: t.type,
                       verified: t.verified,
                       timestamp: t.timestamp
                   }) as transactions
            """
            result = session.run(query, user_id=user_id).single()
            if not result: return None
            
            data = result.data()
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
        Looks for the most recent unverified SALE matching the Squad payment amount.
        """
        with self.driver.session() as session:
            # We allow a 1% margin for small fee differences
            query = """
            MATCH (u:User {id: $user_id})-[:PERFORMED]->(t:Transaction {type: 'SALE', verified: false})
            WHERE t.amount >= $min_amount AND t.amount <= $max_amount
            WITH t ORDER BY t.timestamp DESC LIMIT 1
            SET t.verified = true, t.verified_at = datetime().isoformat()
            RETURN t.item as item
            """
            result = session.run(query, 
                user_id=user_id, 
                min_amount=amount * 0.99, 
                max_amount=amount * 1.01
            )
            return result.single()

    def check_if_verified(self, tx_id: str) -> bool:
        """Checks if a specific transaction is already marked as verified."""
        with self.driver.session() as session:
            query = """
            MATCH (t:Transaction {id: $tx_id})
            RETURN t.verified as verified
            """
            result = session.run(query, tx_id=tx_id).single()
            if result:
                # result['verified'] might be None or False, return explicit bool
                return bool(result.get('verified'))
            return False
        
    def update_transaction_node(self, tx_id: str, data: dict):
        """Updates an unverified transaction's details."""
        with self.driver.session() as session:
            query = """
            MATCH (t:Transaction {id: $tx_id})
            SET t.item = $item,
                t.amount = $amount,
                t.quantity = $quantity,
                t.unit = $unit,
                t.type = $type,
                t.notes = $notes,
                t.updated_at = $updated_at
            RETURN t.id
            """
            session.run(query,
                tx_id=tx_id,
                item=data.get('item'),
                amount=data.get('amount'),
                quantity=data.get('quantity'),
                unit=data.get('unit'),
                type=data.get('type'),
                notes=data.get('notes'),
                updated_at=datetime.now(timezone.utc).isoformat()
            )

    def check_price_anomaly(self, item, unit, amount, quantity):
        price_per_unit = amount / quantity
        with self.driver.session() as session:
            query = """
            MATCH (t:Transaction {item: $item, unit: $unit})
            RETURN avg(t.amount / t.quantity) as avg_price, 
                   stDev(t.amount / t.quantity) as std_dev
            """
            result = session.run(query, item=item, unit=unit).single()
        
            if result and result['avg_price']:
                avg = result['avg_price']
                # If price is 3x the average, it's a huge anomaly
                if price_per_unit > (avg * 3):
                    return True, avg
        return False, 0