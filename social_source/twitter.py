import os
import tweepy
import requests
import json
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# Environment variables
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
API_BASE_URL = os.getenv("API_BASE_URL", "https://misinformation-collector-322893934340.asia-south1.run.app")

# Validate environment variables
if not TWITTER_BEARER_TOKEN:
    logger.warning("TWITTER_BEARER_TOKEN environment variable not set - Twitter functionality disabled")
    client = None
else:
    try:
        client = tweepy.Client(bearer_token=TWITTER_BEARER_TOKEN)
        logger.info("Twitter client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Twitter client: {e}")
        client = None

def get_tweet(tweet_id):
    """Get tweet data and optionally send to backend"""
    if not client:
        logger.error("Twitter client not initialized - check your TWITTER_BEARER_TOKEN")
        return None
        
    try:
        tweet = client.get_tweet(
            tweet_id, 
            tweet_fields=["author_id", "created_at", "text", "public_metrics", "context_annotations"]
        )
        
        if not tweet.data:
            logger.warning(f"No data found for tweet ID: {tweet_id}")
            return None
            
        tweet_data = {
            "author_id": tweet.data.author_id,
            "text": tweet.data.text,
            "created_at": str(tweet.data.created_at),
            "tweet_id": tweet_id,
            "public_metrics": getattr(tweet.data, 'public_metrics', {}),
            "context_annotations": getattr(tweet.data, 'context_annotations', [])
        }
        
        logger.info(f"Successfully retrieved tweet: {tweet_id}")
        return tweet_data
        
    except tweepy.TooManyRequests:
        logger.error("Twitter API rate limit exceeded")
        raise
    except tweepy.Unauthorized:
        logger.error("Twitter API unauthorized - check your bearer token")
        raise
    except Exception as e:
        logger.error(f"Error retrieving tweet {tweet_id}: {e}")
        raise

def send_tweet_to_backend(tweet_data):
    """Send tweet data to the backend service"""
    try:
        payload = {
            "source": "twitter",
            "type": "tweet",
            "content_text": tweet_data["text"],
            "metadata": json.dumps({
                "tweet_id": tweet_data["tweet_id"],
                "author_id": tweet_data["author_id"],
                "created_at": tweet_data["created_at"],
                "public_metrics": tweet_data.get("public_metrics", {}),
                "context_annotations": tweet_data.get("context_annotations", [])
            })
        }
        
        response = requests.post(
            f"{API_BASE_URL}/collect",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"Tweet sent to backend successfully: {result.get('doc_id')}")
            return result
        else:
            logger.error(f"Failed to send tweet to backend: {response.status_code} - {response.text}")
            return None
            
    except requests.RequestException as e:
        logger.error(f"Error sending tweet to backend: {e}")
        return None

def collect_tweet(tweet_id, send_to_backend=True):
    """Collect tweet data and optionally send to backend"""
    tweet_data = get_tweet(tweet_id)
    
    if tweet_data and send_to_backend:
        backend_result = send_tweet_to_backend(tweet_data)
        if backend_result:
            tweet_data["backend_doc_id"] = backend_result.get("doc_id")
    
    return tweet_data

if __name__ == "__main__":
    # Example usage
    tweet_id = "1234567890123456789"  # Replace with actual tweet ID
    result = collect_tweet(tweet_id)
    print(json.dumps(result, indent=2))
