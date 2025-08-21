import pandas as pd
from vertexai.language_models import TextEmbeddingInput, TextEmbeddingModel
from tqdm import tqdm
import json



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
df = df.head(1)
texts = df['title'].tolist()

df['embedding'] = embed_texts_in_batches(texts)

with open("evidence_embeddings.json", "w") as f:
    for idx, row in df.iterrows():
        json_line = {
            "id": str(row.get('id', idx)),
            "embedding": row['embedding'],  # embedding as list
            "metadata": {
                "text": row['title'],
                "description": row['description'],
                "source": row.get('link', ''),
                "guid":row.get('guid'),
                "publishedDate":row.get('pubDate')
            }
        }
        f.write(json.dumps(json_line) + "\n")
        
with open("evidence_embeddings_metadata.json", "w") as f:
    for idx, row in df.iterrows():
        json_line = {
            "id": str(row.get('id', idx)),
            "metadata": {
                "text": row['title'],
                "description": row['description'],
                "source": row.get('link', ''),
                "guid":row.get('guid'),
                "publishedDate":row.get('pubDate')
            }
        }
        f.write(json.dumps(json_line) + "\n")


