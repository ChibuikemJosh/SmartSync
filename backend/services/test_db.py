import sys
import os
# Add the current directory to path so it can find services
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import GraphService
import uuid

def test_connection():
    db = GraphService()
    print("--- Testing Neo4j Connection ---")
    try:
        if not db.is_available():
            print("⚠️ Neo4j driver unavailable, skipping database test")
            return

        # 1. Simple Connectivity
        with db._session() as session:
            res = session.run("RETURN 'Connection Successful' as msg").single()
            print(f"✅ {res['msg']}")

        # 2. Test User Creation
        test_id = f"test_{uuid.uuid4().hex[:6]}"
        db.create_user_node({
            "id": test_id,
            "name": "Test Trader",
            "email": f"{test_id}@test.com",
            "password": "hashed_password_here",
            "role": "trader",
            "location": {"city": "Lagos", "state": "Lagos", "country": "Nigeria"},
            "trust_score": 43
        })
        print(f"✅ User node created: {test_id}")

        # 3. Test Score Calculation
        # Log a "Verified" transaction to see if score jumps from 43
        db.log_transaction(test_id, {
            "item": "Test Bags of Rice",
            "amount": 50000,
            "type": "SALE",
            "verified": True
        })
        
        new_score = db.recalculate_user_score(test_id)
        print(f"✅ Trust Score updated: {new_score}")
        
        if new_score > 43:
            print("🚀 SUCCESS: The Trust Score engine is working!")
        else:
            print("⚠️ WARNING: Score didn't increase. Check decay logic.")

    except Exception as e:
        print(f"❌ TEST FAILED: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    test_connection()