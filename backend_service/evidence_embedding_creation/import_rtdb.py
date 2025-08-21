import json
import firebase_admin
from firebase_admin import credentials, db,firestore

from dotenv import load_dotenv
import os
load_dotenv()

database_url=os.getenv("DATABASE_URL")
# Initialize app
cred = credentials.Certificate("serviceAccountKey.json")


firebase_admin.initialize_app(cred)

db = firestore.client()
# Load JSON file
with open("evidence_embeddings_metadata.json","r") as f:
    data = json.load(f)


collection_ref = db.collection("evidence")  # collection name "articles"
# If JSON is a dict
for item in data:
    doc_id = item["id"]  # use "id" field as document ID
    collection_ref.document(doc_id).set(item)
    print(f"Inserted document {doc_id}")

print("Data imported successfully to Realtime Database!")
