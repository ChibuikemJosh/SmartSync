import easyocr
import numpy as np
import cv2
from PIL import Image
import io
from .ai_logic import parse_voice_to_json
from typing import Optional, Dict, Any

# Initialize the reader once (loading the model into memory)
# We use 'en' for English. EasyOCR supports 80+ languages!
reader = easyocr.Reader(['en'], gpu=False) # Set gpu=True if you have one

def process_ledger_image(file_bytes: bytes) -> Optional[Dict[str, Any]]:
    """
    Extracts text from a photo and converts it to a structured sale.
    """
    try:
        image = Image.open(io.BytesIO(file_bytes))
        image_np = np.array(image)
        
        gray = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)

        # 1. Run EasyOCR on the image
        # detail=0 returns just the text strings
        results = reader.readtext(gray, detail=0, paragraph=True)
        
        # 2. Combine the detected lines into one block of text
        raw_text = " ".join(str(text) for text in results)
        
        if not raw_text.strip():
            print("❌ OCR Error: No text found in image")
            return None

        # 3. Feed the 'messy' OCR text into our existing AI logic
        # The AI is great at cleaning up OCR typos (e.g., '10k' vs 'l0k')
        structured_data = parse_voice_to_json(raw_text)
        
        return structured_data
        
    except Exception as e:
        print(f"❌ OCR Service Error: {e}")
        return None