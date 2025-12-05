# AI Office Jukebox

An AI-powered office music jukebox that learns your team's preferences using Reinforcement Learning and RAG.

## Features
- **Smart Queue**: Suggests songs based on office vibes and past votes.
- **RL Brain**: Learns from Upvotes/Downvotes to refine recommendations.
- **Collaborative**: Add songs via Web UI or Teams.
- **Premium UI**: Dark mode visualization for the host screen.

## Setup
1. **Prerequisites**: Python 3.9+, YouTube API Key, OpenAI API Key.
2. **Install**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure**:
   - Rename `.env` (create one based on the template) and fill in your keys.
4. **Run**:
   ```bash
   uvicorn main:app --reload
   ```

## Usage
- **Host**: Open `http://localhost:8000` on the computer connected to speakers.
- **Vote**: Anyone on the network can access the URL to vote/suggest.
- **Teams**: Point your Teams Bot webhook to `YOUR_PUBLIC_URL/api/teams/hook`.

## API Endpoints
- `POST /api/suggest`: {query: "song name"}
- `POST /api/vote`: {song_id: 1, vote_type: "up"}
- `GET /api/state`: Get current queue.
