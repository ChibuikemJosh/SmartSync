from fastapi import APIRouter, HTTPException, logger, Depends
from services.ai_logic import transcribe_audio, _get_client
from services.database import GraphService
from utils.dependencies import get_current_user
import json

router = APIRouter()
db = GraphService()

@router.post("/chat")
async def chat_with_records(message: str = None, voice_path: str = None, current_user: dict = Depends(get_current_user)):
    user_id = current_user['id']
    # 1. If it's voice, transcribe it first
    user_query = message
    if voice_path:
        user_query = transcribe_audio(voice_path)
    
    if not user_query:
        raise HTTPException(status_code=400, detail="No message or voice provided")

    # 2. Use Groq to turn the question into a Neo4j Cypher query
    cypher_query = generate_cypher(user_query, user_id)
    cypher_query = cypher_query.replace("```cypher", "").replace("```", "").strip()
    
    try:# 3. Run the query on Neo4j
        with db.driver.session() as session:
            result = session.run(cypher_query).data()
    except Exception as e:
        logger.error(f"Cypher Error: {e}")
        result = [] # Return empty list so summarize_results can handle it
    
    # 4. Use Groq to explain the result to the user
    answer = summarize_results(user_query, result)
    
    return {"query": user_query, "answer": answer}

def generate_cypher(user_query: str, user_id: str) -> str:
    client = _get_client()
    prompt = f"""
    You are a Neo4j Cypher expert. Convert the user's question into a Cypher query.
    The Graph has nodes (:User {{id}}) and (:Transaction {{amount, type, item, timestamp, verified}}).
    The relationship is (:User)-[:PERFORMED]->(:Transaction).
    
    STRICT RULES:
    1. Only return the Cypher string. No preamble.
    2. The current year is 2026.
    3. 'SALE' increases money, 'EXPENSE' decreases it.
    4. Handle Nigerian Pidgin: 
       - "How much I get" or "wetin be my balance" means sum of SALE minus sum of EXPENSE.
       - "Wetin I sell" means List items where type='SALE'.
       - "I don pay" means check verified=true.
    5. You are only allowed to query the transactions of the user with id = {user_id}. Do not attempt to query other users.
    6. You can only match, update and return do not delete data.
    7. If the user asks for a time range, use the 'timestamp' field
         - "last month" means transactions from 2025-12
         - "this year" means transactions from 2026-01-01 to 2026-12-31
         - "last week" means transactions from the last 7 days

    USER_ID: "{user_id}"
    USER_QUESTION: "{user_query}"
    
    Return ONLY the Cypher string. Do not explain.
    Example: "How much did I make in Dec?" -> MATCH (u:User {{id: '{user_id}'}})-[:PERFORMED]->(t:Transaction) WHERE t.type = 'SALE' AND t.timestamp CONTAINS '2025-12' RETURN sum(t.amount) as total
    """
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile"
    )
    return response.choices[0].message.content

def summarize_results(user_query, result_data):
    client = _get_client()
    prompt = f"User asked: {user_query}. The database returned: {result_data}. Answer the user like a helpful, witty Nigerian market assistant. Use a mix of professional English and light Nigerian Pidgin where appropriate. Be concise but informative. If the result is empty, say you couldn't fing any record of that. Be encouraging about their business growth"
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile"
    )
    return response.choices[0].message.content