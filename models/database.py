from sqlmodel import SQLModel, create_engine, Session
import os
from config import DATA_DIR
from models.db_models import Song, Vote, PlayHistory

sqlite_file_name = "jukebox.db"
sqlite_url = f"sqlite:///{os.path.join(DATA_DIR, sqlite_file_name)}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
