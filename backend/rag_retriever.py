import json
import faiss
import numpy as np
import os
import random

from sentence_transformers import SentenceTransformer


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

DATASET_PATH = os.path.join(
    BASE_DIR,
    "../dataset/hr_questions_cleaned.json"
)

VECTOR_PATH = os.path.join(
    BASE_DIR,
    "../vector_db/hr_questions.index"
)


# ============================================================
# SETTINGS
# ============================================================

MODEL_NAME = "all-MiniLM-L6-v2"

# Retrieve more candidates first.
# Then filter/rank them before selecting 4 or 5.
TOP_K = 100


# ============================================================
# LOAD DATASET
# ============================================================

print("Loading cleaned dataset...")

with open(
    DATASET_PATH,
    "r",
    encoding="utf-8"
) as f:

    data = json.load(f)


print(
    "Dataset records:",
    len(data)
)


# ============================================================
# LOAD FAISS
# ============================================================

print("Loading FAISS index...")

index = faiss.read_index(
    VECTOR_PATH
)


print(
    "FAISS vectors:",
    index.ntotal
)


# ============================================================
# LOAD EMBEDDING MODEL
# ============================================================

print("Loading embedding model...")

model = SentenceTransformer(
    MODEL_NAME
)


# ============================================================
# NORMALIZATION HELPERS
# ============================================================

def normalize(value):

    if value is None:
        return ""

    return (
        str(value)
        .strip()
        .lower()
    )


def normalize_difficulty(value):

    value = normalize(value)

    if value in [
        "easy",
        "beginner"
    ]:
        return "easy"

    if value in [
        "medium",
        "moderate",
        "intermediate"
    ]:
        return "medium"

    if value in [
        "hard",
        "difficult",
        "advanced"
    ]:
        return "hard"

    return value


# ============================================================
# BUILD SEARCH TEXT
# ============================================================

def build_query(
    role,
    experience,
    difficulty
):

    return (
        f"Role: {role}\n"
        f"Experience: {experience}\n"
        f"Difficulty: {difficulty}\n"
        f"Interview questions for this candidate."
    )


# ============================================================
# RETRIEVE QUESTIONS
# ============================================================

def retrieve_questions(
    role,
    experience,
    difficulty,
    num_questions=5
):

    role_norm = normalize(role)

    experience_norm = normalize(
        experience
    )

    difficulty_norm = normalize_difficulty(
        difficulty
    )


    # ========================================================
    # VALIDATE NUMBER OF QUESTIONS
    # ========================================================

    if num_questions < 4:
        num_questions = 4

    if num_questions > 5:
        num_questions = 5


    # ========================================================
    # RANDOMLY CHOOSE 4 OR 5
    # ========================================================

    target_count = random.choice(
        [4, 5]
    )


    # If caller explicitly asks for
    # 4 or 5, respect it.

    if num_questions in [4, 5]:

        target_count = num_questions


    # ========================================================
    # CREATE QUERY EMBEDDING
    # ========================================================

    query_text = build_query(
        role,
        experience,
        difficulty
    )


    query_embedding = model.encode(
        [query_text],
        convert_to_numpy=True
    )


    query_embedding = np.asarray(
        query_embedding,
        dtype="float32"
    )


    # ========================================================
    # FAISS SEARCH
    # ========================================================

    distances, indices = index.search(
        query_embedding,
        TOP_K
    )


    # ========================================================
    # CANDIDATES
    # ========================================================

    candidates = []


    for distance, idx in zip(
        distances[0],
        indices[0]
    ):

        if idx < 0:
            continue

        if idx >= len(data):
            continue


        item = data[idx]


        item_role = normalize(
            item.get("role")
        )

        item_experience = normalize(
            item.get("experience")
        )

        item_difficulty = normalize_difficulty(
            item.get("difficulty")
        )


        # ====================================================
        # MATCH SCORE
        # ====================================================

        match_score = 0


        # Role match
        if (
            item_role
            == role_norm
        ):

            match_score += 5


        # Difficulty match
        if (
            item_difficulty
            == difficulty_norm
        ):

            match_score += 5


        # Experience match
        if (
            item_experience
            == experience_norm
        ):

            match_score += 3


        # ====================================================
        # SEMANTIC SCORE
        #
        # Smaller FAISS L2 distance = better.
        # Convert it into a positive ranking signal.
        # ====================================================

        semantic_score = 1 / (
            1 + float(distance)
        )


        # ====================================================
        # FINAL RANKING SCORE
        # ====================================================

        final_score = (
            match_score
            + semantic_score
        )


        candidates.append({

            "question":
                item.get(
                    "question",
                    ""
                ),

            "ideal_answer":
                item.get(
                    "ideal_answer",
                    ""
                ),

            "category":
                item.get(
                    "category",
                    ""
                ),

            "difficulty":
                item.get(
                    "difficulty",
                    ""
                ),

            "experience":
                item.get(
                    "experience",
                    ""
                ),

            "role":
                item.get(
                    "role",
                    ""
                ),

            "keywords":
                item.get(
                    "keywords",
                    []
                ),

            "distance":
                float(distance),

            "match_score":
                match_score,

            "final_score":
                final_score
        })


    # ========================================================
    # SORT
    # ========================================================

    candidates.sort(
        key=lambda x: x["final_score"],
        reverse=True
    )


    # ========================================================
    # REMOVE DUPLICATE QUESTIONS
    # ========================================================

    unique_candidates = []

    seen_questions = set()


    for item in candidates:

        question_key = normalize(
            item["question"]
        )


        if not question_key:
            continue


        if question_key in seen_questions:
            continue


        seen_questions.add(
            question_key
        )

        unique_candidates.append(
            item
        )


    # ========================================================
    # SELECT RANDOMLY FROM TOP QUALITY POOL
    # ========================================================

    # Take the best candidates first.
    #
    # We don't simply take the first 4/5 every time,
    # otherwise the interview would always repeat
    # the same questions.

    pool_size = min(
        20,
        len(unique_candidates)
    )


    quality_pool = unique_candidates[
        :pool_size
    ]


    if len(quality_pool) <= target_count:

        selected = quality_pool

    else:

        selected = random.sample(
            quality_pool,
            target_count
        )


    # ========================================================
    # FINAL SORT
    # ========================================================

    # Randomize question order too.

    random.shuffle(
        selected
    )


    # ========================================================
    # DEBUG OUTPUT
    # ========================================================

    print("\n" + "=" * 60)

    print(
        "RAG RETRIEVAL"
    )

    print(
        "Role:",
        role
    )

    print(
        "Experience:",
        experience
    )

    print(
        "Difficulty:",
        difficulty
    )

    print(
        "Requested:",
        target_count
    )

    print(
        "Returned:",
        len(selected)
    )

    print(
        "=" * 60
    )


    for i, item in enumerate(
        selected,
        1
    ):

        print(
            f"{i}. "
            f"{item['question']}"
        )

        print(
            f"   Role: "
            f"{item['role']}"
        )

        print(
            f"   Experience: "
            f"{item['experience']}"
        )

        print(
            f"   Difficulty: "
            f"{item['difficulty']}"
        )

        print(
            f"   Distance: "
            f"{item['distance']}"
        )

        print(
            f"   Match score: "
            f"{item['match_score']}"
        )


    print(
        "=" * 60
    )


    return selected


# ============================================================
# COMPATIBILITY FUNCTION
# ============================================================

def get_questions(
    role,
    experience,
    difficulty,
    num_questions=5
):

    return retrieve_questions(
        role=role,
        experience=experience,
        difficulty=difficulty,
        num_questions=num_questions
    )