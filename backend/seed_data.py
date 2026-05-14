from services.database import GraphService
from services.auth_logic import hash_password
import uuid
from datetime import datetime, timedelta, timezone

def seed_everything():
    db = GraphService()
    print("🌱 Seeding database with demo data...")

    # Clear existing data (OPTIONAL - use with caution!)
    # with db.driver.session() as session:
    #     session.run("MATCH (n) DETACH DELETE n")

    demo_users = [
        {
            "id": "user_pro_001",
            "name": "Alhaji Musa",
            "email": "musa@market.com",
            "role": "trader",
            "score": 85,
            "city": "Kano"
        },
        {
            "id": "user_new_002",
            "name": "Blessing Okon",
            "email": "blessing@market.com",
            "role": "trader",
            "score": 43,
            "city": "Lagos"
        },
        {
            "id": "worker_001",
            "name": "Sunday Delivery",
            "email": "sunday@logistic.com",
            "role": "worker",
            "score": 70,
            "city": "Lagos"
        }
    ]

    for u in demo_users:
        db.create_user_node({
            "id": u['id'],
            "name": u['name'],
            "email": u['email'],
            "password": hash_password("password123"),
            "role": u['role'],
            "location": {"city": u['city'], "state": u['city'], "country": "Nigeria"},
            "trust_score": u['score']
        })
        
        # Add a few transactions for Alhaji Musa so his history looks full
        if u['id'] == "user_pro_001":
            for i in range(5):
                # Backdate transactions slightly
                ts = (datetime.now(timezone.utc) - timedelta(days=i*2)).isoformat()
                db.log_transaction(u['id'], {
                    "item": f"Wholesale Supply {i+1}",
                    "amount": 150000 + (i * 10000),
                    "type": "SALE",
                    "verified": True,
                    "timestamp": ts
                })

    print("✅ Seeding complete! Login with password: password123")
    db.close()

if __name__ == "__main__":
    seed_everything()