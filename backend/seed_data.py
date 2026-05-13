import uuid
from datetime import datetime, timedelta, timezone
from services.database import GraphService

db = GraphService()

MOCK_USER = {
    "id": "mock_trader_001",
    "name": "Bolaji Test",
    "role": "Trader",
    "location": {"city": "Lagos", "state": "Lagos", "country": "Nigeria"},
    "skills": ["Wholesale", "Logistics"]
}

def seed_database():
    print("🚀 Starting Mock Data Injection...")
    
    # 1. Create the User
    db.create_user_node(MOCK_USER)
    
    # 2. Generate a mix of transactions
    # We'll create some old ones to test the "Decay" logic
    transactions = [
        # Normal sales from 2 weeks ago (should have decayed slightly)
        {"item": "rice", "amount": 1200, "quantity": 1, "unit": "derica", "type": "SALE", "days_ago": 20, "verified": True},
        {"item": "eggs", "amount": 4500, "quantity": 1, "unit": "crate", "type": "SALE", "days_ago": 15, "verified": True},
        
        # Recent sales (high impact on score)
        {"item": "beans", "amount": 1500, "quantity": 1, "unit": "paint", "type": "SALE", "days_ago": 2, "verified": False},
        
        # Anomaly/Potential Fraud (Price too high for a derica)
        {"item": "rice", "amount": 25000, "quantity": 1, "unit": "derica", "type": "SALE", "days_ago": 1, "verified": False},
        
        # Expense
        {"item": "fuel", "amount": 5000, "quantity": 1, "unit": "unit", "type": "EXPENSE", "days_ago": 5, "verified": False},
    ]

    for tx in transactions:
        # Calculate backdated timestamp
        backdated_time = (datetime.now(timezone.utc) - timedelta(days=tx['days_ago'])).isoformat()
        
        # We manually inject these to the graph for testing
        with db.driver.session() as session:
            query = """
            MATCH (u:User {id: $user_id})
            CREATE (t:Transaction {
                item: $item,
                amount: $amount,
                quantity: $quantity,
                unit: $unit,
                type: $type,
                timestamp: $timestamp,
                verified: $verified
            })
            CREATE (u)-[:PERFORMED]->(t)
            """
            session.run(query, 
                user_id=MOCK_USER["id"],
                item=tx["item"],
                amount=tx["amount"],
                quantity=tx["quantity"],
                unit=tx["unit"],
                type=tx["type"],
                timestamp=backdated_time,
                verified=tx["verified"]
            )

    with db.driver.session() as session:
        history = session.execute_read(db._get_user_history, MOCK_USER["id"])
        new_score = db.calculate_decayed_score(history)
        session.execute_write(db._update_user_score, MOCK_USER["id"], new_score)

    print(f"✅ Seeding Complete. Bolaji's Trust Score: {new_score}")

if __name__ == "__main__":
    try:
        seed_database()
    finally:
        db.close()