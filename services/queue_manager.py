import logging
from typing import List, Optional
from models.db_models import Song, Vote, PlayHistory, Playlist, PlaylistSong
from models.database import engine, create_db_and_tables
from sqlmodel import Session, select, func, desc
from services.youtube_service import search_video, get_video_details
from services.rag_service import add_song_to_rag, retrieve_candidates
from services.rl_service import agent
from services.ai_service import correct_song_name

logger = logging.getLogger(__name__)

# In-memory state for "Now Playing" (simple approach)
# Ideally this would be syncing with a real player, but we'll track "what should be playing"
class QueueManager:
    def __init__(self):
        create_db_and_tables()
        self.now_playing: Optional[Song] = None
        self.queue: List[Song] = [] # This is an in-memory cache of the queue, or we fetch from DB every time? 
        # For voting sorting, DB is better. 
        
    def get_queue(self) -> List[dict]:
        """Returns the sorted queue and now playing."""
        with Session(engine) as session:
            # Logic: Get songs that are in "Queue" state. 
            # Simplified: Song is in queue if it hasn't been played yet? 
            # Let's assume we delete from queue when played, or mark as played.
            # We need a status field or just check PlayHistory.
            
            # Better approach for this MVP: 
            # We track queue in-memory for order, but persist the objects in DB.
            return {
                "now_playing": self.now_playing,
                "queue": self.queue
            }

    def add_song(self, query: str, requested_by: str = "User"):
        """Search YouTube, Add to DB, Add to Queue, Add to RAG."""
        # 0. AI Correction
        corrected_query = correct_song_name(query)
        logger.info(f"Original: {query} -> Corrected: {corrected_query}")

        # 1. Search YouTube
        results = search_video(corrected_query, max_results=1)
        if not results:
            return None
        
        video = results[0]
        
        with Session(engine) as session:
            # Check if exists
            existing = session.exec(select(Song).where(Song.youtube_id == video["youtube_id"])).first()
            if existing:
                song = existing
            else:
                # 2. Get Details (Duration, Category, Tags)
                details = get_video_details([video["youtube_id"]])
                video_details = details.get(video["youtube_id"], {})
                duration = video_details.get("duration", "PT3M") 
                category_id = video_details.get("categoryId")
                video_tags = video_details.get("tags", [])
                
                # Determine RAG tags
                if category_id == '10': # Music Category ID
                    if video_tags:
                        rag_tags = ", ".join(video_tags[:5])
                    else:
                        rag_tags = "Music"
                else:
                    rag_tags = "Non-Music"

                # 3. Save to DB
                song = Song(
                    youtube_id=video["youtube_id"],
                    title=video["title"],
                    artist=video["channel"],
                    duration=0, # Simplify duration parsing for now
                    thumbnail_url=video["thumbnail"]
                )
                session.add(song)
                session.commit()
                session.refresh(song)
                
                # 4. Add to RAG
                add_song_to_rag(song.id, song.title, song.artist, tags=rag_tags)
        
        # 5. Add to Queue
        if not self.now_playing:
            self.now_playing = song
        else:
            self.queue.append(song)
            
        return song

    def vote(self, song_id: int, vote_type: str):
        """Register vote and update RL agent."""
        with Session(engine) as session:
            if vote_type == "favorite":
                song = session.get(Song, song_id)
                if song:
                    song.is_favorite = not song.is_favorite
                    session.add(song)
                    session.commit()
                    return {"status": "toggled", "is_favorite": song.is_favorite}
                return {"status": "error", "message": "Song not found"}

            vote = Vote(song_id=song_id, vote_type=vote_type)
            session.add(vote)
            session.commit()
            
            # Simple RL Update immediately (or batch later)
            # If vote is for Now Playing, update immediately?
            # Or if it's for something in queue?
            # Let's update RL only if it's "Now Playing" or recently played?
            # Actually, user feedback on suggestions is valuable.
            if vote_type == "up":
                agent.update(agent.choose_action(), 1.0) # Assumption: User likes the CURRENT vibe?
                # This is tricky without tracking WHICH action produced this song.
                # For MVP: We assume the Agent's *current* context/action is what is being voted on
                # if the song was Auto-Suggested. 
                # If User suggested it, maybe we don't update RL? 
                pass
            elif vote_type == "down":
                agent.update(agent.choose_action(), -1.0)

            # Re-sort queue if in queue
            # (Simplified: logic to sort self.queue based on vote counts)
            # self.sort_queue()
            
    def pop_next(self):
        """Move queue to now playing. If empty, auto-generate."""
        if self.queue:
            self.now_playing = self.queue.pop(0)
        else:
            # AUTO GENERATE
            # Use previous song context if available
            if self.now_playing:
                query = f"Songs similar to {self.now_playing.title} by {self.now_playing.artist}"
                logger.info(f"Queue empty. Auto-generating based on previous: {query}")
            else:
                query = agent.choose_action() # e.g. "Upbeat Pop"
                logger.info(f"Queue empty. Agent chose: {query}")
            
            candidates = retrieve_candidates(query)
            
            if candidates:
                # Pick one random candidate from top 5 that isn't recently played
                # For now just pick first that isn't the one that just finished
                found_new = False
                for cand in candidates:
                    if self.now_playing and str(cand["id"]) == str(self.now_playing.id):
                        continue
                    
                    song_id = cand["id"]
                    with Session(engine) as session:
                        song = session.get(Song, int(song_id))
                        self.now_playing = song
                        found_new = True
                        break
                
                if not found_new and candidates:
                     # Fallback if all candidates were the same (unlikely but possible with small DB)
                     song_id = candidates[0]["id"]
                     with Session(engine) as session:
                        song = session.get(Song, int(song_id))
                        self.now_playing = song
            else:
                self.now_playing = None # Silence if nothing found
                
        # Log PlayHistory
        if self.now_playing:
            with Session(engine) as session:
                ph = PlayHistory(song_id=self.now_playing.id)
                session.add(ph)
                session.commit()
                
        return self.now_playing

    def create_playlist(self, name: str):
        with Session(engine) as session:
            playlist = Playlist(name=name)
            session.add(playlist)
            session.commit()
            session.refresh(playlist)
            return playlist

    def add_to_playlist(self, playlist_id: int, song_id: int):
        with Session(engine) as session:
            link = PlaylistSong(playlist_id=playlist_id, song_id=song_id)
            session.add(link)
            session.commit()
            return link

    def get_playlists(self):
        with Session(engine) as session:
            return session.exec(select(Playlist)).all()

    def get_recommendations(self):
        """Get top 3 recommendations based on recent history or random vibe."""
        # Query RAG with "Similar to [Last Song]" if available
        if self.now_playing:
            query = f"Songs similar to {self.now_playing.title} by {self.now_playing.artist}"
            logger.info(f"Fetching recommendations for: {query}")
        else:
            # Fallback to agent's choice
            query = agent.choose_action()
            logger.info(f"Fetching recommendations for agent action: {query}")

        candidates = retrieve_candidates(query, n_results=3)
        
        recommendations = []
        with Session(engine) as session:
            for cand in candidates:
                # Avoid recommending the exact same song that is playing
                if self.now_playing and str(cand["id"]) == str(self.now_playing.id):
                    continue
                    
                song = session.get(Song, int(cand["id"]))
                if song:
                    recommendations.append(song)
        return recommendations

queue_manager = QueueManager()
