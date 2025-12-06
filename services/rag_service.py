import chromadb
from chromadb.utils import embedding_functions
import os
from config import DATA_DIR, OPENAI_API_KEY
import logging

logger = logging.getLogger(__name__)

# Initialize Chroma Client
# PersistentClient to save data to disk
chroma_client = chromadb.PersistentClient(path=os.path.join(DATA_DIR, "chroma_db"))

# Embedding Function
if OPENAI_API_KEY:
    openai_ef = embedding_functions.OpenAIEmbeddingFunction(
        api_key=OPENAI_API_KEY,
        model_name="text-embedding-3-small"
    )
else:
    logger.warning("OPENAI_API_KEY not found. RAG features will be disabled (Switching to simple queue mode).")
    openai_ef = None


# Collection
collection = chroma_client.get_or_create_collection(
    name="jukebox_songs",
    embedding_function=openai_ef
)

def add_song_to_rag(song_id: str, title: str, artist: str, tags: str = ""):
    """Adds a song to the vector DB."""
    if not openai_ef: 
        return
        
    text_representation = f"{title} by {artist}. {tags}"
    
    collection.upsert(
        documents=[text_representation],
        metadatas=[{"title": title, "artist": artist, "type": "song"}],
        ids=[str(song_id)]
    )
    logger.info(f"Added {title} to RAG.")

def retrieve_candidates(query_text: str, n_results: int = 5):
    """Retrieves similar songs based on query text (e.g. 'Upbeat pop')."""
    if not openai_ef:
        return []
        
    results = collection.query(
        query_texts=[query_text],
        n_results=n_results
    )
    
    # helper to flatten results
    candidates = []
    if results['ids']:
        ids = results['ids'][0]
        metas = results['metadatas'][0]
        for i, song_id in enumerate(ids):
            candidates.append({
                "id": song_id,
                "metadata": metas[i]
            })
            
    return candidates
