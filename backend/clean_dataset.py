import json
import os
import re


# ==========================================
# PATHS
# ==========================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

INPUT_PATH = os.path.join(
    BASE_DIR,
    "../dataset/hr_questions.json"
)

OUTPUT_PATH = os.path.join(
    BASE_DIR,
    "../dataset/hr_questions_cleaned.json"
)


# ==========================================
# ROLE NORMALIZATION
# ==========================================

ROLE_NAMES = {
    "softwareengineer": "Software Engineer",
    "devopsengineer": "DevOps Engineer",
    "datascientist": "Data Scientist",
    "productmanager": "Product Manager",
    "marketingassociate": "Marketing Associate",
    "uxdesigner": "UX Designer",
    "qaanalyst": "QA Analyst",
    "hrspecialist": "HR Specialist",
}


def normalize_role(role):

    if not role:
        return ""

    original = str(role).strip()

    key = (
        original
        .lower()
        .replace(" ", "")
        .replace("-", "")
        .replace("_", "")
    )

    return ROLE_NAMES.get(
        key,
        original
    )


# ==========================================
# CLEAN TEXT
# ==========================================

def clean_text(text):

    if text is None:
        return ""

    text = str(text)

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ==========================================
# SAFE IDEAL ANSWER CLEANING
# ==========================================

def clean_ideal_answer(
    question,
    ideal_answer
):

    question = clean_text(
        question
    )

    answer = clean_text(
        ideal_answer
    )

    if not answer:
        return ""


    # Only remove the question if it is
    # clearly appended at the END.

    if answer.lower().endswith(
        question.lower()
    ):

        answer = answer[
            :len(answer) - len(question)
        ].strip()


    return answer


# ==========================================
# START
# ==========================================

print("\n" + "=" * 60)
print("SAFE DATASET CLEANING")
print("=" * 60)

print(
    "Input:",
    INPUT_PATH
)

print(
    "Output:",
    OUTPUT_PATH
)


if not os.path.exists(INPUT_PATH):

    raise FileNotFoundError(
        INPUT_PATH
    )


# ==========================================
# LOAD ORIGINAL DATA
# ==========================================

print(
    "\nLoading dataset..."
)

with open(
    INPUT_PATH,
    "r",
    encoding="utf-8"
) as f:

    data = json.load(f)


print(
    "Original records:",
    len(data)
)


# ==========================================
# COUNTERS
# ==========================================

cleaned_data = []

exact_duplicates = 0
normalized_roles = 0
cleaned_answers = 0


# ==========================================
# EXACT DUPLICATE TRACKING
# ==========================================

seen = set()


# ==========================================
# PROCESS
# ==========================================

for count, item in enumerate(
    data,
    1
):

    question = clean_text(
        item.get(
            "question",
            ""
        )
    )


    if not question:
        continue


    category = clean_text(
        item.get(
            "category",
            ""
        )
    )


    role_original = clean_text(
        item.get(
            "role",
            ""
        )
    )


    role = normalize_role(
        role_original
    )


    if role != role_original:

        normalized_roles += 1


    experience = clean_text(
        item.get(
            "experience",
            ""
        )
    )


    difficulty = clean_text(
        item.get(
            "difficulty",
            ""
        )
    )


    source_type = clean_text(
        item.get(
            "source_type",
            ""
        )
    )


    ideal_answer_original = clean_text(
        item.get(
            "ideal_answer",
            ""
        )
    )


    ideal_answer = clean_ideal_answer(
        question,
        ideal_answer_original
    )


    if (
        ideal_answer
        != ideal_answer_original
    ):

        cleaned_answers += 1


    # ======================================
    # KEYWORDS
    # ======================================

    keywords = item.get(
        "keywords",
        []
    )


    if not isinstance(
        keywords,
        list
    ):

        keywords = []


    cleaned_keywords = []


    for keyword in keywords:

        keyword = clean_text(
            keyword
        )

        if keyword:

            cleaned_keywords.append(
                keyword
            )


    # ======================================
    # TRUE DUPLICATE KEY
    # ======================================

    duplicate_key = (

        question.lower(),

        category.lower(),

        role.lower(),

        experience.lower(),

        difficulty.lower(),

        source_type.lower(),

        ideal_answer.lower(),

        tuple(
            sorted(
                x.lower()
                for x in cleaned_keywords
            )
        )
    )


    if duplicate_key in seen:

        exact_duplicates += 1

        continue


    seen.add(
        duplicate_key
    )


    # ======================================
    # CLEAN RECORD
    # ======================================

    cleaned_item = {

        "question":
            question,

        "category":
            category,

        "role":
            role,

        "experience":
            experience,

        "difficulty":
            difficulty,

        "source_type":
            source_type,

        "ideal_answer":
            ideal_answer,

        "keywords":
            cleaned_keywords
    }


    cleaned_data.append(
        cleaned_item
    )


    # ======================================
    # PROGRESS
    # ======================================

    if count % 100000 == 0:

        print(
            f"Processed "
            f"{count:,} / "
            f"{len(data):,}"
        )


# ==========================================
# SAVE
# ==========================================

print(
    "\nSaving cleaned dataset..."
)


with open(
    OUTPUT_PATH,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        cleaned_data,
        f,
        indent=2,
        ensure_ascii=False
    )


# ==========================================
# SUMMARY
# ==========================================

print("\n" + "=" * 60)
print("CLEANING COMPLETE")
print("=" * 60)

print(
    "Original records:",
    f"{len(data):,}"
)

print(
    "Clean records:",
    f"{len(cleaned_data):,}"
)

print(
    "Exact duplicates removed:",
    f"{exact_duplicates:,}"
)

print(
    "Roles normalized:",
    f"{normalized_roles:,}"
)

print(
    "Answers cleaned:",
    f"{cleaned_answers:,}"
)

print(
    "\nSaved:"
)

print(
    OUTPUT_PATH
)

print(
    "=" * 60
)