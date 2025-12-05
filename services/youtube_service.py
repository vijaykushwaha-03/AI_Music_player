import os
import requests
from config import YOUTUBE_API_KEY
import logging

logger = logging.getLogger(__name__)

YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEOS_URL = "https://www.googleapis.com/youtube/v3/videos"

def search_video(query: str, max_results: int = 5):
    if not YOUTUBE_API_KEY:
        logger.warning("No YOUTUBE_API_KEY set.")
        return []
    
    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "key": YOUTUBE_API_KEY,
        "maxResults": max_results
    }
    
    try:
        response = requests.get(YOUTUBE_SEARCH_URL, params=params)
        response.raise_for_status()
        data = response.json()
        
        results = []
        for item in data.get("items", []):
            results.append({
                "youtube_id": item["id"]["videoId"],
                "title": item["snippet"]["title"],
                "channel": item["snippet"]["channelTitle"],
                "thumbnail": item["snippet"]["thumbnails"]["default"]["url"]
            })
        return results
    except Exception as e:
        logger.error(f"YouTube Search Error: {e}")
        return []

def get_video_details(video_ids: list[str]):
    if not YOUTUBE_API_KEY:
        return {}
        
    params = {
        "part": "contentDetails,snippet",
        "id": ",".join(video_ids),
        "key": YOUTUBE_API_KEY
    }
    
    try:
        response = requests.get(YOUTUBE_VIDEOS_URL, params=params)
        response.raise_for_status()
        data = response.json()
        
        details = {}
        for item in data.get("items", []):
            vid = item["id"]
            details[vid] = {
                "duration": item["contentDetails"]["duration"], # Needs parsing (PT4M13S)
                "title": item["snippet"]["title"],
                "channel": item["snippet"]["channelTitle"]
            }
        return details
    except Exception as e:
        logger.error(f"YouTube Details Error: {e}")
        return {}
