import json
import os
from pydantic import ValidationError
from models.schemas import VoiceTransaction 
from dotenv import load_dotenv

from groq import Groq
import httpx

load_dotenv()

def _get_client() -> Groq:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not set")
    # Pass an explicit httpx client to avoid incompatible kwargs
    http_client = httpx.Client()
    return Groq(api_key=api_key, http_client=http_client)

def transcribe_audio(file_path: str) -> str:
    """
    Uses Groq's Whisper model to turn audio into text.
    Supports .m4a, .mp3, .wav, etc.
    """
    client = _get_client()
    
    try:
        with open(file_path, "rb") as file:
            transcription = client.audio.transcriptions.create(
                file=(file_path, file.read()),
                model="whisper-large-v3-turbo",  # The fastest/newest Whisper model on Groq
                response_format="text",         # Just get the string back
                language="en"                   # Forces English to avoid translation glitches
            )
            return str(transcription)
    except Exception as e:
        print(f"❌ Transcription Error: {e}")
        return ""

def parse_voice_to_json(transcription_text):
    """Turn informal market talk into structured transaction data."""
    prompt = f"""
You are an expert Nigerian Market Bookkeeper for the SmartSync platform.
Your goal is to turn informal market talk into structured financial data.

EXAMPLES:
User: "I just sold four crates of eggs for 12,000 naira to Mama Ngozi."
Expected JSON: {{"item": "eggs", "amount": 12000, "quantity": 4, "type": "SALE", "notes": "Customer: Mama Ngozi"}}

User: "I spent 5k on transport for the delivery today."
Expected JSON: {{"item": "transport", "amount": 5000, "quantity": 1, "type": "EXPENSE", "notes": "Delivery"}}

INPUT TO PROCESS:
"{transcription_text}"

INSTRUCTIONS:
- Return ONLY valid JSON.
- If the user uses 'k', convert it to thousands (e.g., 5k = 5000).
- Categorize as SALE or EXPENSE.
- Default quantity to 1 if the speaker does not mention one.

Return ONLY JSON in this format:
{{"item": str, "amount": int, "quantity": int, "type": "SALE" | "EXPENSE", "notes": str}}
"""

    client = _get_client()
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile",
        response_format={"type": "json_object"},
    )

    content = chat_completion.choices[0].message.content if chat_completion.choices else ""

    try:
        raw_data = json.loads(content)
        # VALIDATION HAPPENS HERE:
        validated_data = VoiceTransaction(**raw_data)
        return validated_data.model_dump() # Returns a clean, safe dict
    except (json.JSONDecodeError, ValidationError) as e:
        print(f"Validation or JSON Error: {e}")
        # Return a safe default or raise an error for the route to handle
        return None