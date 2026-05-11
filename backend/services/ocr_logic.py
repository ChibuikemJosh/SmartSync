import easyocr
from ai_logic import parse_voice_to_json

# Initialize the reader once (loading the model into memory)
# We use 'en' for English. EasyOCR supports 80+ languages!
reader = easyocr.Reader(['en'], gpu=False) # Set gpu=True if you have one

def process_ledger_image(image_path: str):
    """
    Extracts text from a photo and converts it to a structured sale.
    """
    try:
        # 1. Run EasyOCR on the image
        # detail=0 returns just the text strings
        results = reader.readtext(image_path, detail=0)
        
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