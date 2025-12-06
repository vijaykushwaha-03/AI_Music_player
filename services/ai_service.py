import os
import logging
import openai
import google.generativeai as genai
from config import (
    OPENAI_API_KEY, 
    GEMINI_API_KEY, 
    OPENROUTER_API_KEY,
    LLM_PROVIDER, 
    LLM_MODEL_NAME
)

logger = logging.getLogger(__name__)

def get_openai_client():
    if not OPENAI_API_KEY:
        logger.error("OPENAI_API_KEY is missing.")
        return None
    return openai.OpenAI(api_key=OPENAI_API_KEY)

def get_openrouter_client():
    if not OPENROUTER_API_KEY:
        logger.error("OPENROUTER_API_KEY is missing.")
        return None
    return openai.OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY,
        default_headers={
             "HTTP-Referer": "https://github.com/your-repo/ai-office-jukebox", # Optional: good practice
             "X-Title": "AI Office Jukebox"
        }
    )

def get_gemini_client():
    if not GEMINI_API_KEY:
        logger.error("GEMINI_API_KEY is missing.")
        return None
    genai.configure(api_key=GEMINI_API_KEY)
    return genai.GenerativeModel(LLM_MODEL_NAME or "gemini-1.5-flash")


def correct_song_name(input_text: str) -> str:
    """
    Uses the configured LLM to parse a messy input string into a clean 'Song - Artist' format.
    Example: 'play that one song by queen about mamas' -> 'Bohemian Rhapsody - Queen'
    """
    system_prompt = "You are a music assistant. Extract the likely Song Title and Artist from the user input. Return ONLY the format: 'Title - Artist'. If unsure, return the original text."
    
    try:
        if LLM_PROVIDER == "openai":
            client = get_openai_client()
            if not client: return input_text
            
            response = client.chat.completions.create(
                model=LLM_MODEL_NAME or "gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": input_text}
                ],
                max_tokens=50
            )
            return response.choices[0].message.content.strip()

        elif LLM_PROVIDER == "openrouter":
            client = get_openrouter_client()
            if not client: return input_text

            response = client.chat.completions.create(
                model=LLM_MODEL_NAME, # User must specify, e.g., 'openai/gpt-3.5-turbo'
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": input_text}
                ],
                max_tokens=50
            )
            return response.choices[0].message.content.strip()

        elif LLM_PROVIDER == "gemini":
            model = get_gemini_client()
            if not model: return input_text
            
            # Gemini doesn't have system prompts in the same way for simple generation, 
            # but we can prepend it or use system_instruction if model supports it.
            # For simplicity across versions, we'll prepend.
            full_prompt = f"{system_prompt}\n\nUser Input: {input_text}"
            
            response = model.generate_content(full_prompt)
            if response.text:
                return response.text.strip()
            return input_text

        else:
            logger.warning(f"Unknown LLM_PROVIDER: {LLM_PROVIDER}. Returning original text.")
            return input_text

    except Exception as e:
        logger.error(f"AI Correction Error ({LLM_PROVIDER}): {e}")
        return input_text
