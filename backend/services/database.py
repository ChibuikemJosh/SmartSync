"""
Database configuration and connection management for SmartSync
"""
import os
import uuid
import time
import math
import logging
from datetime import datetime, timezone
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class GraphService:
    def __init__(self):
        self.driver = None
        uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        user = os.getenv("NEO4J_USER", "neo4j")
        password = os.getenv("NEO4J_PASSWORD", "")

        max_retries = int(os.getenv("NEO4J_CONNECT_RETRIES", 5))
        base_delay = float(os.getenv("NEO4J_BASE_DELAY", 1.0))

        # --- Connection Retry Loop ---
        for attempt in range(1, max_retries + 1):
            try:
                temp_driver = GraphDatabase.driver(uri, auth=(user, password))
                temp_driver.verify_connectivity()
                self.driver = temp_driver
                logger.info(f"✅ Neo4j connected successfully on attempt {attempt}")
                break
            except Exception as e:
                logger.warning(f"⚠️ Attempt {attempt} failed to connect to Neo4j: {e}")
                if attempt == max_retries:
                    logger.error("❌ Could not connect to Neo4j after max retries.")
                    self.driver = None
                else:
                    sleep_time = base_delay * (2 ** (attempt - 1))
                    time.sleep(sleep_time)

    def is_available(self):
        return self.driver is not None

    def _session(self):
        if not self.driver:
            raise RuntimeError("Database connection not available")
        return self.driver.session()

    def close(self):
        if self.driver:
            self.driver.close()

    # --- User Management ---

    def create_user_node(self, user_data):
        """Creates a new user with location and base score"""
        with self._session() as session:
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
                email=user_data['email'],
                password=user_data['password'],
                role=user_data['role'],
                city=loc.get('city'),
                state=loc.get('state'),
                country=loc.get('country'),
                trust_score=user_data.get('trust_score', 43),
                skills=user_data.get('skills', []),
                created_at=datetime.now(timezone.utc).isoformat()
            )

    # --- Transaction & Trust Score Logic ---

    def log_transaction(self, user_id, tx_data):
        """Logs a transaction and triggers a Trust Score update."""
        tx_id = str(uuid.uuid4())
        timestamp = tx_data.get('timestamp') or datetime.now(timezone.utc).isoformat()

        with self._session() as session:
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
            RETURN t.id
            """
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
            # Automatically update the user's score after new data
            return self.recalculate_user_score(user_id)

    @staticmethod
    def calculate_decayed_score(transactions, half_life_days=14):
        """Calculates a score that weights recent activity higher."""
        if not transactions:
            return 43 

        total_weighted_points = 0
        lambda_constant = math.log(2) / half_life_days
        now = datetime.now(timezone.utc)

        for tx in transactions:
            try:
                tx_time = datetime.fromisoformat(tx['timestamp'])
                if tx_time.tzinfo is None:
                    tx_time = tx_time.replace(tzinfo=timezone.utc)
                
                days_ago = max(0, (now - tx_time).total_seconds() / 86400)
                weight = math.exp(-lambda_constant * days_ago)

                if tx.get('is_anomaly'):
                    base_points = -20
                else:
                    # Verified transactions are 5x more powerful
                    base_points = 15 if tx.get('verified') else 3

                total_weighted_points += (base_points * weight)
            except Exception as e:
                logger.error(f"Error processing transaction weight: {e}")
                continue

        # Logarithmic Scaling to cap the growth naturally
        safe_points = max(total_weighted_points, 0)
        # 40 is the 'floor' for active users
        log_scaled = 40 + (math.log(safe_points + 1, 1.1))
        return min(100, round(log_scaled))

    def recalculate_user_score(self, user_id):
        """Refreshes the Trust Score on the User node."""
        with self._session() as session:
            history = self.get_history(user_id)
            new_score = self.calculate_decayed_score(history)
            
            session.run(
                "MATCH (u:User {id: $user_id}) SET u.trust_score = $score", 
                user_id=user_id, score=new_score
            )
            return new_score

    # --- Escrow & Gig Management ---

    def create_escrow(self, gig_id, trader_id, worker_id, amount):
        """Creates a Gig node and links Trader and Worker."""
        with self._session() as session:
            query = """
            MATCH (t:User {id: $trader_id}), (w:User {id: $worker_id})
            CREATE (g:Gig {
                id: $gig_id, 
                amount: $amount, 
                status: 'locked', 
                created_at: datetime()
            })
            CREATE (t)-[:FUNDED]->(g)
            CREATE (w)-[:ASSIGNED_TO]->(g)
            """
            session.run(query, gig_id=gig_id, trader_id=trader_id, worker_id=worker_id, amount=amount)

    def get_gig_details(self, gig_id):
        with self._session() as session:
            query = """
            MATCH (w:User)-[:ASSIGNED_TO]->(g:Gig {id: $gig_id})<-[:FUNDED]-(t:User)
            RETURN g.amount as amount, 
                   g.status as status, 
                   w.virtual_account as account_number, 
                   w.id as worker_id, 
                   t.id as trader_id, 
                   w.bank_name as bank_name
            """
            result = session.run(query, gig_id=gig_id).single()
            return result.data() if result else None

    # --- Retrieval & Profile Methods ---

    def get_user_by_email(self, email: str):
        with self._session() as session:
            query = """
            MATCH (u:User {email: $email})
            RETURN u.id as id, u.name as name, u.password as password, 
                   u.role as role, u.trust_score as trust_score
            """
            result = session.run(query, email=email).single()
            return result.data() if result else None

    def get_history(self, user_id):
        with self._session() as session:
            query = """
            MATCH (u:User {id: $user_id})-[:PERFORMED]->(t:Transaction)
            RETURN t.amount as amount, t.timestamp as timestamp, 
                   t.verified as verified, t.is_anomaly as is_anomaly
            """
            result = session.run(query, user_id=user_id)
            return [record.data() for record in result]

    def get_transaction_by_id(self, tx_id: str) -> dict:
        query = """
        MATCH (u:User)-[:PERFORMED]->(t:Transaction {id: $tx_id})
        RETURN t {.*, user_id: u.id} AS transaction
        """
        with self._session() as session:
            result = session.run(query, tx_id=tx_id).single()
            return result["transaction"] if result else None

    def update_transaction_node(self, tx_id: str, data: dict):
        with self._session() as session:
            query = """
            MATCH (t:Transaction {id: $tx_id})
            SET t.item = $item,
                t.amount = $amount,
                t.quantity = $quantity,
                t.unit = $unit,
                t.type = $type,
                t.notes = $notes,
                t.updated_at = $updated_at
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

    def update_user_virtual_account(self, user_id, account_number, bank_name):
        with self._session() as session:
            query = """
            MATCH (u:User {id: $user_id})
            SET u.virtual_account = $account_number,
                u.bank_name = $bank_name
            """
            session.run(query, user_id=user_id, account_number=account_number, bank_name=bank_name)