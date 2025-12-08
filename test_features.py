import requests
import time

API_URL = "http://localhost:8000/api"

def test_rag_flow():
    print("Testing RAG Flow...")
    # 1. Suggest a song
    res = requests.post(f"{API_URL}/suggest", json={"query": "Shape of You"})
    if res.status_code == 200:
        song = res.json()
        print(f"✅ Song added: {song['title']}")
        song_id = song['id']
        
        # 2. Toggle Favorite
        res = requests.post(f"{API_URL}/favorite/{song_id}")
        if res.status_code == 200:
            print(f"✅ Favorite toggled: {res.json()}")
            
        # 3. Get Recommendations
        res = requests.get(f"{API_URL}/recommendations")
        if res.status_code == 200:
            recs = res.json()
            print(f"✅ Recommendations fetched: {len(recs)} items")
            
    else:
        print("❌ Failed to suggest song")

def test_playlists():
    print("\nTesting Playlists...")
    # 1. Create Playlist
    res = requests.post(f"{API_URL}/playlists", json={"name": "Test Playlist"})
    if res.status_code == 200:
        pl = res.json()
        print(f"✅ Playlist created: {pl['name']} (ID: {pl['id']})")
        
        # 2. Get Playlists
        res = requests.get(f"{API_URL}/playlists")
        if res.status_code == 200:
            print(f"✅ Playlists fetched: {len(res.json())} items")
    else:
        print("❌ Failed to create playlist")

if __name__ == "__main__":
    try:
        test_rag_flow()
        test_playlists()
    except Exception as e:
        print(f"❌ Test failed: {e}")
