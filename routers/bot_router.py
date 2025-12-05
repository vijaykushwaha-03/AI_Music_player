from fastapi import APIRouter, Request, HTTPException
from services.queue_manager import queue_manager
from services.ai_service import correct_song_name
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/teams")

@router.post("/hook")
async def teams_webhook(request: Request):
    """
    Simple webhook to receive messages from a Teams Bot (e.g. via Power Automate or Bot Framework).
    Expected payload: {"text": "play despacito", "user": "Vijay"}
    """
    try:
        data = await request.json()
        text = data.get("text", "")
        user = data.get("user", "Teams User")
        
        if not text:
            return {"status": "ignored", "reason": "no text"}
            
        # Basic logic: if text starts with "play", treat as suggestion
        if text.lower().startswith("play "):
            query = text[5:].strip()
            song = queue_manager.add_song(query, requested_by=user)
            if song:
                return {"status": "success", "message": f"Queued: {song.title}"}
            else:
                return {"status": "failed", "message": "Could not find song"}
                
        return {"status": "ignored", "reason": "command not recognized"}
        
    except Exception as e:
        logger.error(f"Teams Webhook Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
