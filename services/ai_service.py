import os
import openai
from config import OPENAI_API_KEY
import logging

logger = logging.getLogger(__name__)

if OPENAI_API_KEY:
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
else:
    client = None

def correct_song_name(input_text: str) -> str:
    """
    Uses GPT-4 to parse a messy input string into a clean 'Song - Artist' format.
    Example: 'play that one song by queen about mamas' -> 'Bohemian Rhapsody - Queen'
    """
    if not client:
        return input_text # Fallback
        
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a music assistant. Extract the likely Song Title and Artist from the user input. Return ONLY the format: 'Title - Artist'. If unsure, return the original text."},
                {"role": "user", "content": input_text}
            ],
            max_tokens=50
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"AI Correction Error: {e}")
        return input_text
