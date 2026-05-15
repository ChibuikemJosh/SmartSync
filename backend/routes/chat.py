import logging
from fastapi import APIRouter, HTTPException, Depends
from services.ai_logic import transcribe_audio, _get_client
from services.database import GraphService
from utils.dependencies import get_current_user
from models.schemas import ChatRequest

router = APIRouter()
logger = logging.getLogger(__name__)
db = GraphService()

@router.post("/")
async def chat_with_records(
    data: ChatRequest, 
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user['id']
    user_query = data.message

    # 1. Handle Voice Input if provided
    if data.voice_path:
        try:
            transcribed_text = transcribe_audio(data.voice_path)
            user_query = transcribed_text if transcribed_text else user_query
        except Exception as e:
            logger.error(f"Transcription Error: {e}")
            raise HTTPException(status_code=500, detail="Failed to process voice note")

    if not user_query:
        raise HTTPException(status_code=400, detail="Oga, provide a message or voice note abeg.")

    # 2. Generate Cypher query
    cypher_query = generate_cypher(user_query, user_id)
    # Clean the markdown code blocks if the LLM includes them
    cypher_query = cypher_query.replace("```cypher", "").replace("```", "").strip()

    # 3. Execute on Neo4j
    try:
        with db._session() as session:
            result = session.run(cypher_query).data()
    except Exception as e:
        logger.error(f"Cypher Execution Error: {e}")
        # We pass an empty list so the summarizer can explain the 'no results' state
        result = []

    # 4. Generate AI response
    answer = summarize_results(user_query, result)

    return {
        "query": user_query, 
        "answer": answer,
        "status": "success"
    }

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
    5. Only query transactions of user with id = '{user_id}'.
    6. MATCH, UPDATE, and RETURN only. NO DELETE.
    7. Time Range Logic:
         - "last month" -> timestamp CONTAINS '2025-12'
         - "this year" -> timestamp STARTS WITH '2026'
         - "last week" -> Calculate based on 2026-05-15

    USER_ID: "{user_id}"
    USER_QUESTION: "{user_query}"
    """
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile"
    )
    return response.choices[0].message.content

def summarize_results(user_query: str, result_data: list):
    client = _get_client()
    prompt = (
        f"User asked: {user_query}. The database returned: {result_data}. "
        "Answer like a helpful, witty Nigerian market assistant. Use a mix of English and Pidgin. "
        "Be concise. If the result is empty, tell them you no see any record for that one. "
        "Always be encouraging about their business growth."
    )
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile"
    )
    return response.choices[0].message.content