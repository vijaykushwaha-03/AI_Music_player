import chromadb
import os
from config import DATA_DIR

client = chromadb.PersistentClient(path=os.path.join(DATA_DIR, "chroma_db"))
collection = client.get_collection("jukebox_songs")

# Get all items
results = collection.get()
ids = results["ids"]
metadatas = results["metadatas"]
documents = results["documents"]

print(f"Total items in RAG: {len(ids)}")
for i, meta in enumerate(metadatas):
    print(f"ID: {ids[i]}, Title: {meta.get('title')}, Tags: {documents[i]}")
