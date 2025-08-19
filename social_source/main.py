from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
import os
from youtube import get_video_details, send_to_backend
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="YouTube Collector Service")

@app.get("/")
async def root():
    return {"message": "YouTube Collector Service", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "youtube-collector"}

@app.post("/collect-video/{video_id}")
async def collect_video(video_id: str):
    """Collect YouTube video data"""
    try:
        video_data = get_video_details(video_id)
        if video_data:
            # Send to backend
            result = send_to_backend(video_data)
            return {"status": "success", "video_id": video_id, "result": result}
        else:
            raise HTTPException(status_code=404, detail="Video not found")
    except Exception as e:
        logger.error(f"Error collecting video {video_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
