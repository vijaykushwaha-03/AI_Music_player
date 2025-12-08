from fastapi import APIRouter, HTTPException, BackgroundTasks
from services.queue_manager import queue_manager
from services.rl_service import agent
from typing import Optional
from pydantic import BaseModel

router = APIRouter(prefix="/api")

class SuggestionRequest(BaseModel):
    query: str
    requested_by: str = "User"

class VoteRequest(BaseModel):
    song_id: int
    vote_type: str # "up", "down", "skip"

@router.get("/state")
def get_state():
    """Get current playing song and queue."""
    return queue_manager.get_queue()

@router.post("/suggest")
def suggest_song(request: SuggestionRequest):
    """Search and add a song to the queue."""
    song = queue_manager.add_song(request.query, request.requested_by)
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    return song

@router.post("/vote")
def vote(request: VoteRequest):
    """Vote on a song."""
    queue_manager.vote(request.song_id, request.vote_type)
    return {"status": "voted", "type": request.vote_type}

@router.post("/next")
def play_next():
    """Force play next song (Admin/Auto)."""
    # Use queue manager to pop next
    next_track = queue_manager.pop_next()
    return next_track

@router.post("/favorite/{song_id}")
def toggle_favorite(song_id: int):
    """Toggle favorite status of a song."""
    return queue_manager.vote(song_id, "favorite")

class PlaylistRequest(BaseModel):
    name: str

@router.post("/playlists")
def create_playlist(request: PlaylistRequest):
    return queue_manager.create_playlist(request.name)

@router.get("/playlists")
def get_playlists():
    return queue_manager.get_playlists()

@router.post("/playlists/{playlist_id}/add/{song_id}")
def add_to_playlist(playlist_id: int, song_id: int):
    return queue_manager.add_to_playlist(playlist_id, song_id)

@router.get("/recommendations")
def get_recommendations():
    return queue_manager.get_recommendations()
