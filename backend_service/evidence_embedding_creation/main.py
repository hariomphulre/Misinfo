import pandas as pd
from vertexai.language_models import TextEmbeddingInput, TextEmbeddingModel
from tqdm import tqdm
import json
from google.cloud import storage
from dotenv import load_dotenv
import os

load_dotenv()

bucket_name=os.getenv("BUCKET_NAME")

def upload_blob(source_file_name, destination_blob_name):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)


    blob.upload_from_filename(source_file_name)

    print(
        f"File {source_file_name} uploaded to {destination_blob_name}."
    )


# Load embedding model
model = TextEmbeddingModel.from_pretrained("gemini-embedding-001")

BATCH_SIZE=20


def embed_texts_in_batches(texts, batch_size=BATCH_SIZE):
    embeddings = []
    for i in tqdm(range(0, len(texts), batch_size)):
        batch_texts = texts
        for text in batch_texts:
            text_input = TextEmbeddingInput(text)
            embedding = model.get_embeddings([text_input])
            embeddings.append(embedding[0].values)
    print(len(embeddings[0]))
    return embeddings



df = pd.read_csv("bbc_news.csv")
df = df.head(2)
texts = df['title'].tolist()

df['embedding'] = embed_texts_in_batches(texts)

# Prepare full embeddings JSON
embeddings_data = []
for idx, row in df.iterrows():
    json_line = {
        "id": str(row.get('id', idx)),
        "embedding": row['embedding'],
        "metadata": {
            "text": row['title'],
            "description": row['description'],
            "source": row.get('link', ''),
            "guid": row.get('guid'),
            "publishedDate": row.get('pubDate')
        }
    }
    embeddings_data.append(json_line)

with open("evidence_embeddings.json", "w") as f:
    json.dump(embeddings_data, f, indent=4)

upload_blob("evidence_embeddings.json","evidence_embeddings.json")
# Prepare metadata-only JSON
metadata_data = []
for idx, row in df.iterrows():
    json_line = {
        "id": str(row.get('id', idx)),
        "metadata": {
            "text": row['title'],
            "description": row['description'],
            "source": row.get('link', ''),
            "guid": row.get('guid'),
            "publishedDate": row.get('pubDate')
        }
    }
    metadata_data.append(json_line)

with open("evidence_embeddings_metadata.json", "w") as f:
    json.dump(metadata_data, f, indent=4)

upload_blob("evidence_embeddings_metadata.json","evidence_embeddings_metadata.json")


