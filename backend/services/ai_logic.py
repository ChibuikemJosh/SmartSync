import json
import os
import logging
from typing import Optional, Any, Dict
from pathlib import Path
from dotenv import load_dotenv

import httpx
import redis
from groq import Groq
from pydantic import ValidationError

from models.schemas import VoiceTransaction

# Setup configuration
load_dotenv()
logger = logging.getLogger(__name__)

# Constants
SUPPORTED_AUDIO_FORMATS = {'.mp3', '.wav', '.m4a', '.ogg', '.flac', '.mpeg', '.mpga', '.mp4', '.webm'}
DEFAULT_TTL = 3600  # 1 hour

# Global instances
_groq_client: Optional[Groq] = None
http_client = httpx.Client()

# Redis Initialization
try:
    r = redis.Redis(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", 6379)),
        decode_responses=True
    )
    # Test connection
    r.ping()
except redis.ConnectionError:
    logger.error("❌ Redis connection failed. Job tracking will be disabled.")
    r = None


def _get_client() -> Groq:
    """Singleton pattern to manage Groq client instance."""
    global _groq_client
    if _groq_client is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError("GROQ_API_KEY is missing from .env")
        _groq_client = Groq(api_key=api_key, http_client=http_client)
    return _groq_client


# --- Job Management ---

def update_job_status(job_id: str, status: str, data: Optional[Any] = None):
    """Update job state in Redis with automatic expiry."""
    if not r: return
    job_key = f"job:{job_id}"
    try:
        mapping = {"status": status, "data": json.dumps(data) if data else ""}
        r.hset(job_key, mapping=mapping)
        r.expire(job_key, DEFAULT_TTL)
    except Exception as e:
        logger.error(f"Redis update failed: {e}")


def get_job_status(job_id: str) -> Optional[Dict[str, Any]]:
    """Fetch and parse job data from Redis."""
    if not r: return None
    job_key = f"job:{job_id}"
    
    job = r.hgetall(job_key)
    if not job:
        return None

    data_str = job.get("data")
    job["data"] = json.loads(data_str) if data_str else {}
    return job


# --- AI Logic ---

def transcribe_audio(file_path: str) -> str:
    """Uses Groq Whisper-large-v3-turbo for fast English/Pidgin transcription."""
    client = _get_client()
    path_obj = Path(file_path.strip('"'))

    if path_obj.suffix.lower() not in SUPPORTED_AUDIO_FORMATS:
        logger.error(f"Unsupported format: {path_obj.suffix}")
        return ""

    try:
        with open(path_obj, "rb") as audio_file:
            # We pass the filename specifically to help Groq detect the codec
            transcription = client.audio.transcriptions.create(
                file=(path_obj.name, audio_file.read()),
                model="whisper-large-v3-turbo",
                response_format="text",
                language="en"  # "en" works best for Nigerian Pidgin mixed with English
            )
            return str(transcription).strip()
    except Exception as e:
        logger.error(f"Transcription failed: {e}")
        return ""


def parse_voice_to_json(transcription_text: str) -> Optional[Dict[str, Any]]:
    """Extracts structured financial data from informal transcription."""
    if not transcription_text:
        return None

    prompt = f"""
    You are a SmartSync Bookkeeper. Extract data from this Nigerian market talk: "{transcription_text}"
    
    RULES:
    1. 'K' suffix means thousands (e.g., 5k = 5000).
    2. Units: Bag, Paint, Derica, Crate, KG, Piece, Carton. Default: 'item'.
    3. Types: 'SALE' (money in) or 'EXPENSE' (money out).
    4. If the speaker mentions a customer name, add it to 'notes'.
    
    RETURN ONLY RAW JSON:
    {{
      "item": string, 
      "amount": float, 
      "quantity": integer, 
      "unit": string, 
      "type": "SALE" | "EXPENSE", 
      "notes": string
    }}
    """

    client = _get_client()
    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"},
        )
        
        content = response.choices[0].message.content
        raw_json = json.loads(content)
        
        # Pydantic validation for data integrity
        validated_data = VoiceTransaction(**raw_json)
        return validated_data.model_dump()
        
    except (json.JSONDecodeError, ValidationError, Exception) as e:
        logger.error(f"JSON Parsing/Validation Error: {e}")
        return None


def process_voice_entry(audio_file_path: str) -> Optional[Dict[str, Any]]:
    """Complete pipeline: Audio -> Text -> Structured Dict."""
    text = transcribe_audio(audio_file_path)
    if not text:
        return None
    
    return parse_voice_to_json(text)