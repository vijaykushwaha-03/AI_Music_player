import chromadb
from chromadb.utils import embedding_functions
import os
from config import DATA_DIR
import logging

logger = logging.getLogger(__name__)

# Initialize Chroma Client
# PersistentClient to save data to disk
chroma_client = chromadb.PersistentClient(path=os.path.join(DATA_DIR, "chroma_db"))

# Embedding Function - Local Sentence Transformer
# This removes dependency on OpenAI API Key for embeddings
try:
    embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
    logger.info("Initialized local SentenceTransformer embedding function.")
except Exception as e:
    logger.error(f"Failed to initialize SentenceTransformer: {e}")
    embedding_func = None

# Collection
collection = chroma_client.get_or_create_collection(
    name="jukebox_songs",
    embedding_function=embedding_func
)

def add_song_to_rag(song_id: str, title: str, artist: str, tags: str = ""):
    """Adds a song to the vector DB."""
    if not embedding_func: 
        logger.warning("Embedding function not available. Skipping RAG addition.")
        return
        
    text_representation = f"{title} by {artist}. {tags}"
    
    try:
        collection.upsert(
            documents=[text_representation],
            metadatas=[{"title": title, "artist": artist, "type": "song"}],
            ids=[str(song_id)]
        )
        logger.info(f"Added {title} to RAG.")
    except Exception as e:
        logger.error(f"Error adding to RAG: {e}")

def retrieve_candidates(query_text: str, n_results: int = 5):
    """Retrieves similar songs based on query text (e.g. 'Upbeat pop')."""
    if not embedding_func:
        return []
        
    try:
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
    except Exception as e:
        logger.error(f"Error retrieving from RAG: {e}")
        return []
