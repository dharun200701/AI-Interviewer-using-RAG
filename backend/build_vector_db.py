import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import os

# -------- SETTINGS --------
DATASET_PATH = "../dataset/hr_questions.json"
VECTOR_PATH = "../vector_db/hr_questions.index"

MAX_ROWS = 25000
BATCH_SIZE = 100
# --------------------------

print("Loading dataset...")

with open(DATASET_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

data = data[:MAX_ROWS]

print("Total questions loaded:", len(data))

print("Loading embedding model...")

model = SentenceTransformer("all-MiniLM-L6-v2")

dimension = 384

index = faiss.IndexFlatL2(dimension)

texts = []


def format_text(item):
    return f"""
Role: {item.get('role')}
Experience: {item.get('experience')}
Category: {item.get('category')}
Difficulty: {item.get('difficulty')}

Question:
{item.get('question')}
"""


print("Starting embedding process...")

for i, item in enumerate(data):

    texts.append(format_text(item))

    if len(texts) == BATCH_SIZE:

        embeddings = model.encode(
            texts,
            normalize_embeddings=True
        )

        index.add(np.asarray(embeddings, dtype="float32"))

        print(f"Processed {i + 1} questions")

        texts = []


# Process remaining questions
if texts:

    embeddings = model.encode(
        texts,
        normalize_embeddings=True
    )

    index.add(np.asarray(embeddings, dtype="float32"))


# Create vector database folder
os.makedirs("../vector_db", exist_ok=True)

# Save FAISS index
faiss.write_index(index, VECTOR_PATH)

print("===================================")
print("✅ Vector database created")
print("Total vectors:", index.ntotal)
print("Saved at:", VECTOR_PATH)
print("===================================")