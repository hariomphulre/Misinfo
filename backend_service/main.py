from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from google.cloud import storage
import firebase_admin
from firebase_admin import credentials, db
import os
from dotenv import load_dotenv
import json
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME", "misinfo-tool-bucket-1755447699")
FIREBASE_DATABASE_URL = os.getenv("FIREBASE_DATABASE_URL", "https://misinfo-469304-default-rtdb.firebaseio.com/")

logger.info(f"GCS Bucket: {GCS_BUCKET_NAME}")
logger.info(f"Firebase URL: {FIREBASE_DATABASE_URL}")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

try:
    if not firebase_admin._apps:
        cred = credentials.ApplicationDefault()
        firebase_admin.initialize_app(cred, {
            'databaseURL': FIREBASE_DATABASE_URL
        })
    
    database = db.reference()
    logger.info("Firebase Realtime Database initialized successfully")
    
    storage_client = storage.Client()
    bucket = storage_client.bucket(GCS_BUCKET_NAME)
    logger.info(f"Cloud Storage client initialized for bucket: {GCS_BUCKET_NAME}")
except Exception as e:
    logger.error(f"Failed to initialize Google Cloud clients: {e}")
    raise

@app.post("/collect")
async def collect_data(
    source: str = Form(...),
    type: str = Form(...),
    content_text: str = Form(""),
    metadata: str = Form("{}")
):
    try:
        metadata_dict = json.loads(metadata) if isinstance(metadata, str) else metadata
        
        if not source or not type:
            raise HTTPException(status_code=400, detail="Source and type are required")
        
        content_ref = database.child("content").push({
            "source": source,
            "type": type,
            "content_text": content_text,
            "metadata": metadata_dict,
            "status": "pending",
            "timestamp": datetime.utcnow().isoformat()
        })
        
        logger.info(f"Data collected successfully with doc_id: {content_ref.key}")
        return {"status": "success", "doc_id": content_ref.key}
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in metadata")
    except Exception as e:
        logger.error(f"Error collecting data: {e}")
        raise HTTPException(status_code=500, detail="Failed to collect data")

@app.post("/upload")
async def upload_file(file: UploadFile = File(...), source: str = Form(...)):
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        if not source:
            raise HTTPException(status_code=400, detail="Source is required")
        
        blob = bucket.blob(file.filename)
        blob.upload_from_file(file.file)
        
        file_url = f"gs://{GCS_BUCKET_NAME}/{file.filename}"
        
        file_ref = database.child("content").push({
            "source": source,
            "type": "file",
            "file_url": file_url,
            "metadata": {"filename": file.filename, "content_type": file.content_type},
            "status": "pending",
            "timestamp": datetime.utcnow().isoformat()
        })
        
        logger.info(f"File uploaded successfully: {file.filename}")
        return {"status": "success", "file_url": file_url, "doc_id": file_ref.key}
        
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        raise HTTPException(status_code=500, detail="Failed to upload file")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "misinformation-collector"}
