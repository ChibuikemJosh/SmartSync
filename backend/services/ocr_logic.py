import logging
import requests
import os
from typing import Optional, Dict, Any
from .ai_logic import parse_voice_to_json

logger = logging.getLogger(__name__)

# 🔐 Debug mode: API Key left here as requested, but logic is ready for os.getenv
OCR_API_KEY = "k81034156488957"
OCR_URL = "https://api.ocr.space/parse/image"

def process_ledger_image(file_bytes: bytes) -> Optional[Dict[str, Any]]:
    """
    Extracts text from a photo using OCR.space API 
    and leverages the existing AI parser to structure the data.
    """
    try:
        # Prepare the OCR.space payload
        # Engine 2 is indeed better for receipts and non-standard text
        payload = {
            "apikey": OCR_API_KEY,
            "language": "eng",
            "isOverlayRequired": False,
            "OCREngine": 2,
            "detectOrientation": True,
            "scale": True,
            "isTable": False # Set to True if processing complex tabular ledgers
        }

        files = {"file": ("ledger.jpg", file_bytes)}

        response = requests.post(
            OCR_URL,
            files=files,
            data=payload,
            timeout=30
        )
        
        response.raise_for_status()
        result = response.json()

        # Handle OCR.space internal errors
        if result.get("IsErroredOnProcessing"):
            err_msg = result.get("ErrorMessage", "Unknown Error")
            logger.error(f"❌ OCR API Error: {err_msg}")
            return None

        parsed_results = result.get("ParsedResults")
        if not parsed_results:
            logger.warning("⚠️ OCR Error: No text could be parsed from this image.")
            return None

        # Extract detected text
        raw_text = parsed_results[0].get("ParsedText", "").strip()

        if not raw_text:
            logger.warning("⚠️ OCR Error: Image was processed but returned empty text.")
            return None

        logger.info(f"✅ OCR Extracted Text: {raw_text[:100]}...")

        # Re-use the market-intelligent AI logic
        # This handles the Pidgin/Market talk detected in the image
        structured_data = parse_voice_to_json(raw_text)

        return structured_data

    except requests.exceptions.Timeout:
        logger.error("❌ OCR Service Timeout: API took too long to respond.")
    except Exception as e:
        logger.error(f"❌ OCR Service Error: {str(e)}")
        
    return None