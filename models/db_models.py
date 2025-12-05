from typing import Optional, List
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship

class Song(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    youtube_id: str = Field(index=True, unique=True)
    title: str
    artist: str
    duration: int
    thumbnail_url: str
    added_at: datetime = Field(default_factory=datetime.utcnow)
    embedding_id: Optional[str] = None # Link to ChromaDB

class Vote(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    song_id: int = Field(foreign_key="song.id")
    vote_type: str # "up", "down", "skip"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
class PlayHistory(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    song_id: int = Field(foreign_key="song.id")
    played_at: datetime = Field(default_factory=datetime.utcnow)
