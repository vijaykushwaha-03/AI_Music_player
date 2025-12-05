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
def next_song():
    """Force play next song (Admin/Auto)."""
    # Use queue manager to pop next
    next_track = queue_manager.pop_next()
    return next_track
