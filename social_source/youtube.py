import os
import requests
import json
from googleapiclient.discovery import build
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# Environment variables
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
API_BASE_URL = os.getenv("API_BASE_URL", "https://misinformation-collector-322893934340.asia-south1.run.app")

# Validate environment variables
if not YOUTUBE_API_KEY:
    logger.error("YOUTUBE_API_KEY environment variable is required")
    raise ValueError("YOUTUBE_API_KEY environment variable is required")

try:
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
    logger.info("YouTube client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize YouTube client: {e}")
    raise

def get_video_details(video_id):
    """Get YouTube video details"""
    try:
        response = youtube.videos().list(
            part='snippet,contentDetails,statistics',
            id=video_id
        ).execute()
        
        if not response['items']:
            logger.warning(f"No video found for ID: {video_id}")
            return None
            
        video = response['items'][0]
        
        video_data = {
            "video_id": video_id,
            "title": video['snippet']['title'],
            "description": video['snippet']['description'],
            "publishedAt": video['snippet']['publishedAt'],
            "channel": video['snippet']['channelTitle'],
            "channel_id": video['snippet']['channelId'],
            "url": f"https://www.youtube.com/watch?v={video_id}",
            "duration": video['contentDetails']['duration'],
            "statistics": video.get('statistics', {}),
            "tags": video['snippet'].get('tags', []),
            "category_id": video['snippet'].get('categoryId')
        }
        
        logger.info(f"Successfully retrieved video: {video_id}")
        return video_data
        
    except Exception as e:
        logger.error(f"Error retrieving video {video_id}: {e}")
        raise

def send_video_to_backend(video_data):
    """Send video data to the backend service"""
    try:
        payload = {
            "source": "youtube",
            "type": "video",
            "content_text": f"{video_data['title']}\n\n{video_data['description']}",
            "metadata": json.dumps({
                "video_id": video_data["video_id"],
                "title": video_data["title"],
                "channel": video_data["channel"],
                "channel_id": video_data["channel_id"],
                "url": video_data["url"],
                "publishedAt": video_data["publishedAt"],
                "duration": video_data["duration"],
                "statistics": video_data.get("statistics", {}),
                "tags": video_data.get("tags", []),
                "category_id": video_data.get("category_id")
            })
        }
        
        response = requests.post(
            f"{API_BASE_URL}/collect",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"Video sent to backend successfully: {result.get('doc_id')}")
            return result
        else:
            logger.error(f"Failed to send video to backend: {response.status_code} - {response.text}")
            return None
            
    except requests.RequestException as e:
        logger.error(f"Error sending video to backend: {e}")
        return None

def collect_video(video_id, send_to_backend=True):
    """Collect video data and optionally send to backend"""
    video_data = get_video_details(video_id)
    
    if video_data and send_to_backend:
        backend_result = send_video_to_backend(video_data)
        if backend_result:
            video_data["backend_doc_id"] = backend_result.get("doc_id")
    
    return video_data

def extract_video_id_from_url(url):
    """Extract video ID from YouTube URL"""
    import re
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)',
        r'youtube\.com\/v\/([^&\n?#]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None

if __name__ == "__main__":
    # Example usage
    video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Replace with actual video URL
    video_id = extract_video_id_from_url(video_url)
    
    if video_id:
        result = collect_video(video_id)
        print(json.dumps(result, indent=2))
    else:
        print("Invalid YouTube URL")
