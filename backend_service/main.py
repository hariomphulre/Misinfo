from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from google.cloud import firestore, storage
import os
from dotenv import load_dotenv
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Google Cloud config
GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")

# Validate required environment variables
if not GCS_BUCKET_NAME:
    logger.error("GCS_BUCKET_NAME environment variable is required")
    raise ValueError("GCS_BUCKET_NAME environment variable is required")

app = FastAPI()

# Enable CORS for testing with frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Initialize clients with error handling
try:
    # Firestore client
    db = firestore.Client()
    logger.info("Firestore client initialized successfully")
    
    # Cloud Storage client
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
        
        # Validate required fields
        if not source or not type:
            raise HTTPException(status_code=400, detail="Source and type are required")
        
        doc_ref = db.collection("content").add({
            "source": source,
            "type": type,
            "content_text": content_text,
            "metadata": metadata_dict,
            "status": "pending",
            "timestamp": firestore.SERVER_TIMESTAMP
        })
        
        logger.info(f"Data collected successfully with doc_id: {doc_ref[1].id}")
        return {"status": "success", "doc_id": str(doc_ref[1].id)}
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in metadata")
    except Exception as e:
        logger.error(f"Error collecting data: {e}")
        raise HTTPException(status_code=500, detail="Failed to collect data")

@app.post("/upload")
async def upload_file(file: UploadFile = File(...), source: str = Form(...)):
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Validate source
        if not source:
            raise HTTPException(status_code=400, detail="Source is required")
        
        blob = bucket.blob(file.filename)
        blob.upload_from_file(file.file)
        
        # Make blob publicly readable (optional - adjust based on security requirements)
        blob.make_public()
        
        doc_ref = db.collection("content").add({
            "source": source,
            "type": "file",
            "file_url": blob.public_url,
            "metadata": {"filename": file.filename, "content_type": file.content_type},
            "status": "pending",
            "timestamp": firestore.SERVER_TIMESTAMP
        })
        
        logger.info(f"File uploaded successfully: {file.filename}")
        return {"status": "success", "file_url": blob.public_url, "doc_id": str(doc_ref[1].id)}
        
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        raise HTTPException(status_code=500, detail="Failed to upload file")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "misinformation-collector"}
