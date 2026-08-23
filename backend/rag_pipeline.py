import json
from pathlib import Path
from threading import Lock

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


# =========================
# Paths
# =========================

BASE_DIR = Path(__file__).resolve().parent.parent

INDEX_PATH = BASE_DIR / "vector_db" / "hr_questions.index"

DATASET_PATH = BASE_DIR / "dataset" / "hr_questions.json"


# =========================
# Lazy-loaded resources
# =========================

_model = None
_index = None
_data = None

_load_lock = Lock()


# =========================
# Load resources
# =========================

def _load_resources():

    global _model
    global _index
    global _data

    if (
        _model is not None
        and _index is not None
        and _data is not None
    ):
        return

    with _load_lock:

        if (
            _model is not None
            and _index is not None
            and _data is not None
        ):
            return

        print("\n" + "=" * 60)
        print("Loading RAG resources...")
        print("=" * 60)

        if not INDEX_PATH.exists():
            raise FileNotFoundError(
                f"Vector index not found at:\n{INDEX_PATH}"
            )

        if not DATASET_PATH.exists():
            raise FileNotFoundError(
                f"Dataset not found at:\n{DATASET_PATH}"
            )

        # =========================
        # Embedding model
        # =========================

        print("Loading embedding model...")

        _model = SentenceTransformer(
            "all-MiniLM-L6-v2"
        )

        print("Embedding model loaded.")

        # =========================
        # FAISS
        # =========================

        print("Loading FAISS index...")

        _index = faiss.read_index(
            str(INDEX_PATH)
        )

        print(
            f"FAISS index loaded: {_index.ntotal} vectors"
        )

        # =========================
        # Dataset
        # =========================

        print("Loading dataset...")

        with DATASET_PATH.open(
            "r",
            encoding="utf-8"
        ) as f:

            _data = json.load(f)

        print(
            f"Dataset loaded: {len(_data)} questions"
        )

        print("=" * 60)
        print("RAG resources loaded successfully.")
        print("=" * 60 + "\n")


# =========================
# Normalize text
# =========================

def _normalize_text(text):

    return (
        str(text)
        .strip()
        .lower()
        .replace("-", " ")
        .replace("_", " ")
    )


# =========================
# Normalize role
# =========================

def _normalize_role(role):

    return _normalize_text(role)


# =========================
# Check role match
# =========================

def _role_matches(
    item_role,
    requested_role
):

    if not requested_role:
        return True

    item_role = _normalize_role(
        item_role
    )

    requested_role = _normalize_role(
        requested_role
    )

    # Exact match
    if item_role == requested_role:
        return True

    # Requested role contained in dataset role
    if requested_role in item_role:
        return True

    # Dataset role contained in requested role
    if item_role in requested_role:
        return True

    # Handle common role variations
    role_aliases = {

        "software engineer": [
            "software developer",
            "software development engineer",
            "sde",
            "developer",
        ],

        "software developer": [
            "software engineer",
            "software development engineer",
            "sde",
            "developer",
        ],

        "data scientist": [
            "data science",
            "machine learning",
            "ml engineer",
        ],

        "machine learning engineer": [
            "machine learning",
            "ml engineer",
            "data scientist",
        ],

        "web developer": [
            "frontend developer",
            "backend developer",
            "full stack developer",
            "fullstack developer",
        ],

        "full stack developer": [
            "fullstack developer",
            "web developer",
            "software engineer",
        ],

    }

    aliases = role_aliases.get(
        requested_role,
        []
    )

    for alias in aliases:

        if alias in item_role:
            return True

    return False


# =========================
# Search Questions
# =========================

def search_questions(
    query,
    top_k=20,
    role=None
):

    _load_resources()

    if not query or not str(query).strip():
        return []

    query = str(query).strip()


    # ==================================================
    # Build role-aware semantic query
    # ==================================================

    if role:

        semantic_query = (
            f"{role} technical interview "
            f"questions {query}"
        )

    else:

        semantic_query = (
            f"technical interview questions {query}"
        )


    print(
        "\nRAG query:",
        semantic_query
    )


    # ==================================================
    # Encode ONLY the query
    # ==================================================

    query_vector = _model.encode(
        [semantic_query],
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    query_vector = np.asarray(
        query_vector,
        dtype=np.float32
    )


    # ==================================================
    # FAISS candidate search
    # ==================================================

    # Search many candidates so that
    # role filtering does not eliminate
    # all useful results.

    search_k = min(
        max(top_k * 50, 1000),
        _index.ntotal
    )


    distances, indices = _index.search(
        query_vector,
        search_k
    )


    print(
        f"FAISS searched {search_k} candidates."
    )


    # ==================================================
    # Collect role-matching candidates
    # ==================================================

    results = []

    seen_questions = set()


    for position, idx in enumerate(
        indices[0]
    ):

        idx = int(idx)


        # Invalid FAISS index
        if idx < 0 or idx >= len(_data):
            continue


        item = _data[idx]


        question = item.get(
            "question"
        )


        if not question:
            continue


        # ==================================================
        # Role filtering
        # ==================================================

        item_role = item.get(
            "role",
            ""
        )


        if role:

            if not _role_matches(
                item_role,
                role
            ):
                continue


        # ==================================================
        # Remove duplicates
        # ==================================================

        normalized_question = (
            _normalize_text(question)
        )


        if normalized_question in seen_questions:
            continue


        seen_questions.add(
            normalized_question
        )


        # ==================================================
        # Calculate retrieval score
        # ==================================================

        distance = float(
            distances[0][position]
        )


        # With normalized embeddings,
        # inner product behaves like cosine similarity.

        similarity = distance


        results.append({

            "role": item.get(
                "role"
            ),

            "question": question,

            "ideal_answer": item.get(
                "ideal_answer"
            ),

            "category": item.get(
                "category"
            ),

            "difficulty": item.get(
                "difficulty"
            ),

            "similarity": round(
                similarity,
                4
            ),

        })


        # We intentionally collect
        # more than top_k results.
        #
        # interviewer_agent.py will
        # randomly choose questions
        # from this pool.

        if len(results) >= max(
            top_k,
            20
        ):

            break


    # ==================================================
    # Sort by semantic similarity
    # ==================================================

    results.sort(
        key=lambda x: x.get(
            "similarity",
            0
        ),
        reverse=True
    )


    # ==================================================
    # Final results
    # ==================================================

    print(
        f"Role-filtered results: "
        f"{len(results)}"
    )


    if results:

        print(
            "\nTop retrieved questions:"
        )

        for i, item in enumerate(
            results[:10],
            1
        ):

            print(
                f"{i}. "
                f"[{item.get('similarity')}] "
                f"{item.get('question')}"
            )


    return results[:top_k]