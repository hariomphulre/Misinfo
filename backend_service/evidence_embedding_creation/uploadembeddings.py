from google.cloud import aiplatform
from dotenv import load_dotenv
import os

load_dotenv()

project_id=os.getenv("PROJECT_ID")
location=os.getenv("LOCATION")
index_name=os.getenv("INDEX")
bucket_uri=os.getenv("BUCKET_URI")

# Initialize Vertex AI
aiplatform.init(project=project_id, location=location)

# Reference your existing index
index = aiplatform.MatchingEngineIndex(
    index_name=index_name
)

# Start the bulk import/update operation using GCS JSONL
op = index.update_embeddings(
    contents_delta_uri=bucket_uri,
    is_complete_overwrite=True  # set True to fully overwrite index
)

# Wait for completion
op.wait()
print("Embeddings have been successfully imported into the index!")