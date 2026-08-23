import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import os
import gc


# ==========================================
# SETTINGS
# ==========================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

DATASET_PATH = os.path.join(
    BASE_DIR,
    "../dataset/hr_questions_cleaned.json"
)

VECTOR_DIR = os.path.join(
    BASE_DIR,
    "../vector_db"
)

VECTOR_PATH = os.path.join(
    VECTOR_DIR,
    "hr_questions.index"
)

# Keep this small for 8 GB RAM
BATCH_SIZE = 64


# ==========================================
# LOAD DATASET
# ==========================================

print("\n" + "=" * 60)
print("CREATING FAISS VECTOR DATABASE")
print("=" * 60)

print(
    "Dataset:",
    DATASET_PATH
)


if not os.path.exists(DATASET_PATH):

    raise FileNotFoundError(
        f"Dataset not found: {DATASET_PATH}"
    )


print("\nLoading dataset...")


with open(
    DATASET_PATH,
    "r",
    encoding="utf-8"
) as f:

    data = json.load(f)


print(
    "Total questions:",
    f"{len(data):,}"
)


# ==========================================
# LOAD MODEL
# ==========================================

print(
    "\nLoading embedding model..."
)

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


# ==========================================
# FAISS
# ==========================================

dimension = 384

index = faiss.IndexFlatL2(
    dimension
)


# ==========================================
# FORMAT TEXT
# ==========================================

def format_text(item):

    keywords = item.get(
        "keywords",
        []
    )

    if not isinstance(
        keywords,
        list
    ):

        keywords = []


    return (
        f"Role: {item.get('role', '')}\n"
        f"Experience: {item.get('experience', '')}\n"
        f"Category: {item.get('category', '')}\n"
        f"Difficulty: {item.get('difficulty', '')}\n"
        f"Source Type: {item.get('source_type', '')}\n"
        f"Question: {item.get('question', '')}\n"
        f"Ideal Answer: {item.get('ideal_answer', '')}\n"
        f"Keywords: {', '.join(keywords)}"
    )


# ==========================================
# PROCESS BATCHES
# ==========================================

print("\nStarting embedding process...")

total = len(data)

processed = 0


for start in range(
    0,
    total,
    BATCH_SIZE
):

    end = min(
        start + BATCH_SIZE,
        total
    )


    batch_items = data[
        start:end
    ]


    texts = [

        format_text(item)

        for item in batch_items
    ]


    # --------------------------------------
    # Generate embeddings
    # --------------------------------------

    embeddings = model.encode(

        texts,

        batch_size=BATCH_SIZE,

        show_progress_bar=False,

        convert_to_numpy=True
    )


    embeddings = np.asarray(
        embeddings,
        dtype="float32"
    )


    # --------------------------------------
    # Add directly to FAISS
    # --------------------------------------

    index.add(
        embeddings
    )


    processed = end


    if (
        processed % 5000 == 0
        or processed == total
    ):

        percentage = (
            processed / total
        ) * 100


        print(
            f"Processed "
            f"{processed:,}/"
            f"{total:,} "
            f"({percentage:.1f}%)"
        )


    # --------------------------------------
    # Free batch memory
    # --------------------------------------

    del texts
    del batch_items
    del embeddings

    gc.collect()


# ==========================================
# CREATE VECTOR DIRECTORY
# ==========================================

os.makedirs(
    VECTOR_DIR,
    exist_ok=True
)


# ==========================================
# SAVE INDEX
# ==========================================

print(
    "\nSaving FAISS index..."
)

faiss.write_index(
    index,
    VECTOR_PATH
)


# ==========================================
# VERIFY
# ==========================================

print("\n" + "=" * 60)
print("FAISS DATABASE CREATED SUCCESSFULLY")
print("=" * 60)

print(
    "Dataset records:",
    f"{total:,}"
)

print(
    "FAISS vectors:",
    f"{index.ntotal:,}"
)

print(
    "Vector dimension:",
    index.d
)

print(
    "Index:",
    VECTOR_PATH
)

print("=" * 60)