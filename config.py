import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
DATA_DIR = os.getenv("DATA_DIR", "./data")

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)
