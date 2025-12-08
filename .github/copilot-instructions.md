# AI Office Jukebox - Copilot Instructions

## Project Overview
This is an AI-powered collaborative music jukebox for office environments. It uses Reinforcement Learning (RL) to learn team preferences and Retrieval-Augmented Generation (RAG) to suggest songs based on "vibes".

## Architecture
- **Backend**: FastAPI (`main.py`) with modular routers (`routers/`).
- **Core Logic**: `services/queue_manager.py` is the central orchestrator managing the "Now Playing" state, queue, and interactions with other services.
- **AI Services**:
  - `services/ai_service.py`: LLM integration (OpenAI/Gemini) for correcting song queries (e.g., "play that queen song" -> "Bohemian Rhapsody").
  - `services/rl_service.py`: Q-Learning agent (`JukeboxAgent`) that learns optimal genres/vibes based on day/time context.
  - `services/rag_service.py`: ChromaDB vector store for semantic song retrieval.
- **Data Layer**: SQLite (via SQLModel) for structured data (`models/db_models.py`) and ChromaDB for embeddings.
- **Frontend**: Vanilla JS + HTML (`templates/index.html`) interacting with the backend via REST API.

## Key Workflows & Commands
- **Run Server**: `uvicorn main:app --reload` (Runs on port 8000).
- **Environment**: Requires `.env` with `OPENAI_API_KEY`, `YOUTUBE_API_KEY`, etc. (See `config.py`).
- **Database**: Tables are auto-created on startup via `create_db_and_tables()` in `queue_manager.py`.

## Coding Conventions
- **Queue Management**: The queue is tracked in-memory (`self.queue` in `QueueManager`) for ordering but persisted in SQLite. Always update both or ensure synchronization.
- **Service Injection**: Services (`agent`, `queue_manager`) are typically singletons instantiated in their respective modules and imported.
- **Async/Sync**: FastAPI routes are async, but some service methods are synchronous. Be mindful of blocking operations.
- **Error Handling**: Use `logger.error` for service failures but ensure the app doesn't crash. Fallback to simple search if AI/RAG fails.

## Specific Patterns
- **Song Addition Flow**: User Input -> `correct_song_name` (LLM) -> `search_video` (YouTube) -> DB Save -> RAG Index -> Queue.
- **RL Context**: The RL agent uses `Day-TimeBlock` (e.g., "Monday-Morning") as the state key for Q-learning.
- **Frontend Updates**: The frontend polls `/api/state` every 5 seconds to sync the player UI.

## UI/UX
- **Player Controls**: Located in `templates/index.html`. Includes Shuffle, Prev, Play/Pause, Next, Repeat.
- **Styling**: `static/css/styles.css` uses a "modern" dark theme with CSS variables.

## Integration
- **Teams Bot**: `routers/bot_router.py` handles webhooks from Microsoft Teams to add songs via chat.
