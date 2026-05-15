import sys
import os
import uuid
import logging

# Ensure the app root is in the python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.database import GraphService

# Setup minimal logging to see errors if they happen
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_connection():
    db = GraphService()
    print("\n--- 🧩 SmartSync Database Integration Test ---")
    
    try:
        if not db.is_available():
            print("❌ ERROR: Neo4j driver could not connect. Check your .env credentials.")
            return

        # 1. Simple Connectivity Check
        with db._session() as session:
            res = session.run("RETURN 'Neo4j is Online' as msg").single()
            print(f"✅ {res['msg']}")

        # 2. Test User Creation
        test_id = f"test_{uuid.uuid4().hex[:8]}"
        user_payload = {
            "id": test_id,
            "name": "Test Trader",
            "email": f"{test_id}@smartsync.test",
            "password": "argon2_or_bcrypt_hash",
            "role": "trader",
            "location": {"city": "Mushin", "state": "Lagos", "country": "Nigeria"},
            "trust_score": 43
        }
        
        db.create_user_node(user_payload)
        print(f"✅ User node created: {test_id} (Base Score: 43)")

        # 3. Test Score Engine (The Logic Core)
        print("📊 Logging a verified sale to test Trust Score engine...")
        
        # We log a significant sale to trigger a score jump
        updated_score = db.log_transaction(test_id, {
            "item": "Luxury Handbags",
            "amount": 150000.0,
            "quantity": 2,
            "unit": "piece",
            "type": "SALE",
            "verified": True, # Verified tx carry 5x weight
            "is_anomaly": False
        })

        print(f"📈 New Trust Score: {updated_score}")

        if updated_score > 43:
            print(f"🚀 SUCCESS: Trust Score increased by {updated_score - 43} points!")
        else:
            print("⚠️ WARNING: Score stayed at 43. Check your decay/logarithmic math in database.py.")

        # 4. Cleanup (Keep your DB clean during development)
        print(f"🧹 Cleaning up test node {test_id}...")
        with db._session() as session:
            session.run("MATCH (u:User {id: $id}) DETACH DELETE u", id=test_id)
        print("✅ Database clean. Test finished.")

    except Exception as e:
        print(f"❌ CRITICAL TEST FAILURE: {str(e)}")
        logger.exception("Traceback for debugging:")
    finally:
        db.close()

if __name__ == "__main__":
    test_connection()