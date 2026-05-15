import sys
import os
import uuid
import logging
from datetime import datetime, timedelta, timezone

# Ensure the app root is in the python path so it can find 'services'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.database import GraphService
from services.auth_logic import hash_password

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed_everything():
    db = GraphService()
    print("\n🌱 Seeding SmartSync database with demo data...")

    if not db.is_available():
        print("❌ ERROR: Neo4j is unavailable, skipping seed data.")
        return

    # Clear existing data (Uncomment if you want a fresh slate every time)
    # with db._session() as session:
    #     session.run("MATCH (n) DETACH DELETE n")
    #     print("🧹 Cleared old database data.")

    demo_users = [
        {
            "id": "user_pro_001",
            "name": "Alhaji Musa",
            "email": "musa@market.com",
            "role": "Trader",
            "score": 85,
            "city": "Kano"
        },
        {
            "id": "user_new_002",
            "name": "Blessing Okon",
            "email": "blessing@market.com",
            "role": "Trader",
            "score": 43,
            "city": "Lagos"
        },
        {
            "id": "worker_001",
            "name": "Sunday Delivery",
            "email": "sunday@logistic.com",
            "role": "Worker",
            "score": 70,
            "city": "Lagos"
        }
    ]

    for u in demo_users:
        # Create User
        db.create_user_node({
            "id": u['id'],
            "name": u['name'],
            "email": u['email'],
            "password": hash_password("password123"),
            "role": u['role'],
            "location": {"city": u['city'], "state": u['city'], "country": "Nigeria"},
            "trust_score": u['score']
        })
        print(f"👤 Created user: {u['name']} ({u['role']})")

        # Add a few transactions for Alhaji Musa so his dashboard looks alive
        if u['id'] == "user_pro_001":
            print(f"📦 Generating transaction history for {u['name']}...")
            for i in range(5):
                # Backdate transactions slightly
                ts = (datetime.now(timezone.utc) - timedelta(days=i*2)).isoformat()
                db.log_transaction(u['id'], {
                    "item": f"Wholesale Supply {i+1}",
                    "amount": 150000 + (i * 10000),
                    "quantity": 10 + i,
                    "unit": "bag",
                    "type": "SALE",
                    "verified": True,
                    "timestamp": ts,
                    "is_anomaly": False
                })

    print("\n✅ Seeding complete! You can now log in with:")
    print("   Email: musa@market.com")
    print("   Password: password123")
    db.close()

if __name__ == "__main__":
    seed_everything()