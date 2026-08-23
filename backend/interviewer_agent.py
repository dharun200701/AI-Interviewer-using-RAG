import random


# ==========================================================
# IMPORTS
# ==========================================================

try:

    from .rag_pipeline import search_questions

    from .llm_evaluator import (
        evaluate_with_llama,
        generate_interview_report
    )

except ImportError:

    from rag_pipeline import search_questions

    from llm_evaluator import (
        evaluate_with_llama,
        generate_interview_report
    )


# ==========================================================
# GENERATE INTERVIEW QUESTIONS
# ==========================================================

def generate_interview_questions(
    role="general",
    experience="fresher",
    difficulty="Medium",
    num_questions=None
):

    print(
        "\n" + "=" * 60
    )

    print(
        "GENERATING INTERVIEW QUESTIONS"
    )

    print(
        "=" * 60
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


    # ======================================================
    # QUESTION COUNT
    # ======================================================

    if num_questions is None:

        num_questions = random.choice(
            [4, 5]
        )

    else:

        num_questions = max(
            4,
            min(
                5,
                num_questions
            )
        )


    print(
        "Number of questions:",
        num_questions
    )


    # ======================================================
    # RAG QUERY
    # ======================================================

    query = (
        f"{role} interview "
        f"{experience} experience "
        f"{difficulty} difficulty"
    )


    print(
        "\nRAG Query:"
    )

    print(
        query
    )


    # ======================================================
    # RAG SEARCH
    # ======================================================

    results = search_questions(

        query=query,

        top_k=50,

        role=role
    )


    print(
        "\nRAG results:",
        len(results)
    )


    # ======================================================
    # QUESTION POOL
    # ======================================================

    question_pool = []

    seen = set()


    for item in results:

        question = item.get(
            "question"
        )


        if not question:
            continue


        normalized = (
            question
            .strip()
            .lower()
        )


        if normalized in seen:
            continue


        seen.add(
            normalized
        )


        item_role = item.get(
            "role",
            ""
        )

        item_experience = item.get(
            "experience",
            ""
        )

        item_difficulty = item.get(
            "difficulty",
            ""
        )


        # ==================================================
        # MATCH SCORE
        # ==================================================

        match_score = 0


        if (
            str(item_role).strip().lower()
            ==
            str(role).strip().lower()
        ):

            match_score += 5


        if (
            str(item_experience).strip().lower()
            ==
            str(experience).strip().lower()
        ):

            match_score += 3


        if (
            str(item_difficulty).strip().lower()
            ==
            str(difficulty).strip().lower()
        ):

            match_score += 5


        question_pool.append({

            "question":
                question.strip(),

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
                    experience
                ),

            "role":
                item.get(
                    "role",
                    role
                ),

            "keywords":
                item.get(
                    "keywords",
                    []
                ),

            "match_score":
                match_score
        })


    # ======================================================
    # SORT
    # ======================================================

    question_pool.sort(

        key=lambda x:
            x["match_score"],

        reverse=True
    )


    # ======================================================
    # QUALITY POOL
    # ======================================================

    quality_pool = question_pool[
        :min(
            20,
            len(question_pool)
        )
    ]


    # ======================================================
    # RANDOM SELECTION
    # ======================================================

    if len(quality_pool) <= num_questions:

        selected_questions = quality_pool

    else:

        selected_questions = random.sample(

            quality_pool,

            num_questions
        )


    random.shuffle(
        selected_questions
    )


    # ======================================================
    # DISPLAY
    # ======================================================

    print(
        "\nSelected interview questions:"
    )


    for i, item in enumerate(
        selected_questions,
        1
    ):

        print(
            f"{i}. {item['question']}"
        )


    print(
        "\nTotal selected:",
        len(selected_questions)
    )


    print(
        "=" * 60
    )


    return selected_questions


# ==========================================================
# EVALUATE ANSWER
# ==========================================================

def evaluate_answer(
    question,
    answer,
    ideal_answer=""
):

    return evaluate_with_llama(

        question=question,

        answer=answer,

        ideal_answer=ideal_answer
    )


# ==========================================================
# GENERATE FINAL REPORT
# ==========================================================

def generate_final_interview_report(
    role,
    experience,
    difficulty,
    results
):

    return generate_interview_report(

        role=role,

        experience=experience,

        difficulty=difficulty,

        results=results
    )