import os
from dotenv import load_dotenv

load_dotenv()


# LLM Configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai").lower() # openai, gemini, openrouter
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "gpt-4o") # Default model

# Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") # Used for OpenAI and optional RAG
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
DATA_DIR = os.getenv("DATA_DIR", "./data")

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)
