from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

import uuid
import random


# ============================================================
# IMPORTS
# ============================================================

try:

    from .interviewer_agent import (
        generate_interview_questions,
        evaluate_answer
    )

    from .rag_pipeline import (
        search_questions
    )

    from .llm_evaluator import (
        generate_interview_report
    )

except ImportError:

    from interviewer_agent import (
        generate_interview_questions,
        evaluate_answer
    )

    from rag_pipeline import (
        search_questions
    )

    from llm_evaluator import (
        generate_interview_report
    )


# ============================================================
# FASTAPI
# ============================================================

app = FastAPI(
    title="AI Interview Assistant",
    description="RAG-based AI Interview System",
    version="1.0.0"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)


# ============================================================
# REQUEST MODELS
# ============================================================

class InterviewRequest(BaseModel):

    role: str

    experience: str

    difficulty: str


class AnswerRequest(BaseModel):

    session_id: str

    question: str

    answer: str


# ============================================================
# INTERVIEW SESSIONS
# ============================================================

interview_sessions = {}


# ============================================================
# HOME
# ============================================================

@app.get("/")
def home():

    return {
        "message": "AI Interview Assistant Running 🚀",
        "status": "online"
    }


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize_text(text):

    if text is None:
        return ""

    return (
        str(text)
        .strip()
        .lower()
        .replace("-", " ")
        .replace("_", " ")
    )


# ============================================================
# CHECK DUPLICATE QUESTION
# ============================================================

def question_already_used(
    session,
    question
):

    normalized_question = normalize_text(
        question
    )

    for item in session.get(
        "asked_questions",
        []
    ):

        if normalize_text(item) == normalized_question:

            return True

    return False


# ============================================================
# GET NEXT QUESTION
# ============================================================

def get_next_question(session):

    role = session["role"]

    experience = session["experience"]

    difficulty = session["difficulty"]


    # ========================================================
    # BUILD QUERY
    # ========================================================

    query = (

        f"{role} "

        f"{experience} experience "

        f"{difficulty} difficulty "

        f"technical interview question"

    )


    print("\n" + "-" * 60)

    print("GENERATING NEXT QUESTION")

    print("-" * 60)

    print("Role:", role)

    print("Experience:", experience)

    print("Difficulty:", difficulty)

    print("Query:", query)


    # ========================================================
    # RAG SEARCH
    # ========================================================

    try:

        results = search_questions(

            query=query,

            top_k=100,

            role=role

        )

    except Exception as e:

        print(
            "RAG search error:",
            e
        )

        return None


    if not results:

        print(
            "No RAG results found."
        )

        return None


    # ========================================================
    # FILTER AVAILABLE QUESTIONS
    # ========================================================

    available_questions = []


    for item in results:

        question = item.get(
            "question",
            ""
        )


        if not question:

            continue


        # -----------------------------------------------
        # Avoid previously asked questions
        # -----------------------------------------------

        if question_already_used(
            session,
            question
        ):

            continue


        # -----------------------------------------------
        # Calculate matching score
        # -----------------------------------------------

        score = 0


        item_role = normalize_text(
            item.get(
                "role",
                ""
            )
        )

        item_experience = normalize_text(
            item.get(
                "experience",
                ""
            )
        )

        item_difficulty = normalize_text(
            item.get(
                "difficulty",
                ""
            )
        )


        requested_role = normalize_text(
            role
        )

        requested_experience = normalize_text(
            experience
        )

        requested_difficulty = normalize_text(
            difficulty
        )


        # Role

        if item_role == requested_role:

            score += 10

        elif (
            requested_role
            and requested_role in item_role
        ):

            score += 7


        # Experience

        if (
            item_experience
            == requested_experience
        ):

            score += 6


        # Difficulty

        if (
            item_difficulty
            == requested_difficulty
        ):

            score += 8


        # RAG similarity

        similarity = item.get(
            "similarity",
            0
        )


        try:

            similarity = float(
                similarity
            )

        except Exception:

            similarity = 0


        score += similarity * 5


        # Small randomness prevents
        # exactly the same sequence.

        score += random.uniform(
            0,
            2
        )


        available_questions.append({

            "question":
                question,

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
                    difficulty
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

            "similarity":
                similarity,

            "selection_score":
                score

        })


    # ========================================================
    # NO UNUSED QUESTIONS
    # ========================================================

    if not available_questions:

        print(
            "No unused questions remain."
        )

        return None


    # ========================================================
    # SORT
    # ========================================================

    available_questions.sort(

        key=lambda item:
            item.get(
                "selection_score",
                0
            ),

        reverse=True

    )


    # ========================================================
    # QUALITY POOL
    # ========================================================

    quality_pool = available_questions[
        :min(
            10,
            len(
                available_questions
            )
        )
    ]


    # ========================================================
    # RANDOM PICK FROM QUALITY QUESTIONS
    # ========================================================

    selected = random.choice(
        quality_pool
    )


    print(
        "\nSelected question:"
    )

    print(
        selected["question"]
    )

    print(
        "Category:",
        selected.get(
            "category",
            ""
        )
    )

    print(
        "Difficulty:",
        selected.get(
            "difficulty",
            ""
        )
    )

    print(
        "Similarity:",
        selected.get(
            "similarity",
            0
        )
    )


    return selected


# ============================================================
# START INTERVIEW
# ============================================================

@app.post("/start_interview")
def start_interview(
    request: InterviewRequest
):

    print("\n" + "=" * 60)

    print(
        "STARTING INTERVIEW"
    )

    print("=" * 60)


    role = request.role.strip()

    experience = request.experience.strip()

    difficulty = request.difficulty.strip()


    if not role:

        return {
            "error":
                "Role is required."
        }


    if not experience:

        return {
            "error":
                "Experience is required."
        }


    if not difficulty:

        return {
            "error":
                "Difficulty is required."
        }


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


    # ========================================================
    # CREATE SESSION
    # ========================================================

    session_id = str(
        uuid.uuid4()
    )


    session = {

        "session_id":
            session_id,

        "role":
            role,

        "experience":
            experience,

        "difficulty":
            difficulty,

        "questions":
            [],

        "asked_questions":
            [],

        "answers":
            [],

        "scores":
            [],

        "completed":
            False

    }


    interview_sessions[
        session_id
    ] = session


    # ========================================================
    # FIRST QUESTION
    # ========================================================

    first_question = get_next_question(
        session
    )


    # ========================================================
    # FALLBACK
    # ========================================================

    if first_question is None:

        print(
            "Dynamic RAG failed."
        )

        print(
            "Using interviewer_agent question generation."
        )


        try:

            generated = (
                generate_interview_questions(

                    role=role,

                    experience=experience,

                    difficulty=difficulty,

                    num_questions=5

                )
            )

        except Exception as e:

            print(
                "Question generation error:",
                e
            )

            del interview_sessions[
                session_id
            ]

            return {

                "error":
                    "Unable to generate interview questions.",

                "details":
                    str(e)

            }


        if not generated:

            del interview_sessions[
                session_id
            ]

            return {

                "error":
                    "No interview questions found."

            }


        first_question = generated[0]


    # ========================================================
    # STORE FIRST QUESTION
    # ========================================================

    session["questions"].append(
        first_question
    )

    session["asked_questions"].append(
        first_question["question"]
    )


    print(
        "\nFirst question:"
    )

    print(
        first_question["question"]
    )

    print(
        "\nSession ID:",
        session_id
    )

    print("=" * 60)


    # ========================================================
    # RESPONSE
    # ========================================================

    return {

        "session_id":
            session_id,

        "questions": [

            first_question[
                "question"
            ]

        ],

        "current_question":
            first_question[
                "question"
            ],

        "question_number":
            1,

        "total_questions":
            5,

        "role":
            role,

        "experience":
            experience,

        "difficulty":
            difficulty,

        "completed":
            False

    }


# ============================================================
# SUBMIT ANSWER
# ============================================================

@app.post("/submit_answer")
def submit_answer(
    request: AnswerRequest
):

    print("\n" + "=" * 60)

    print(
        "ANSWER RECEIVED"
    )

    print("=" * 60)


    # ========================================================
    # FIND SESSION
    # ========================================================

    session = interview_sessions.get(
        request.session_id
    )


    if session is None:

        print(
            "ERROR: Session not found."
        )

        return {

            "error":
                "Interview session not found."

        }


    if session.get(
        "completed",
        False
    ):

        return {

            "error":
                "This interview has already been completed."

        }


    question = (
        request.question
        or ""
    ).strip()


    answer = (
        request.answer
        or ""
    ).strip()


    print(
        "Question:",
        question
    )

    print(
        "\nCandidate answer:",
        answer
    )


    # ========================================================
    # VALIDATE QUESTION
    # ========================================================

    question_data = None


    normalized_question = normalize_text(
        question
    )


    for item in session["questions"]:

        stored_question = normalize_text(
            item.get(
                "question",
                ""
            )
        )


        if (
            stored_question
            == normalized_question
        ):

            question_data = item

            break


    # ========================================================
    # QUESTION NOT FOUND
    # ========================================================

    if question_data is None:

        print(
            "WARNING: Question metadata not found."
        )

        question_data = {

            "question":
                question,

            "ideal_answer":
                "",

            "category":
                "",

            "difficulty":
                session["difficulty"],

            "experience":
                session["experience"],

            "role":
                session["role"],

            "keywords":
                []

        }


    # ========================================================
    # IDEAL ANSWER
    # ========================================================

    ideal_answer = question_data.get(
        "ideal_answer",
        ""
    )


    # ========================================================
    # EVALUATE
    # ========================================================

    print(
        "\nEvaluating answer..."
    )


    try:

        evaluation = evaluate_answer(

            question=question,

            answer=answer,

            ideal_answer=ideal_answer

        )

    except Exception as e:

        print(
            "Evaluation error:",
            e
        )

        evaluation = {

            "score":
                0,

            "feedback":
                "Unable to evaluate this answer."

        }


    print(
        "\nEvaluation:"
    )

    print(
        evaluation
    )


    # ========================================================
    # EXTRACT SCORE
    # ========================================================

    if isinstance(
        evaluation,
        dict
    ):

        score = evaluation.get(
            "score",
            0
        )

        feedback = evaluation.get(
            "feedback",
            "No feedback provided."
        )

    else:

        score = 0

        feedback = str(
            evaluation
        )


    # ========================================================
    # VALIDATE SCORE
    # ========================================================

    try:

        score = int(
            float(
                score
            )
        )

    except (
        ValueError,
        TypeError
    ):

        score = 0


    score = max(
        0,
        min(
            10,
            score
        )
    )


    # ========================================================
    # STORE ANSWER
    # ========================================================

    answer_record = {

        "question":
            question,

        "answer":
            answer,

        "score":
            score,

        "feedback":
            str(
                feedback
            ),

        "ideal_answer":
            ideal_answer,

        "category":
            question_data.get(
                "category",
                ""
            ),

        "difficulty":
            question_data.get(
                "difficulty",
                session["difficulty"]
            )

    }


    session["answers"].append(
        answer_record
    )

    session["scores"].append(
        score
    )


    answered = len(
        session["answers"]
    )


    # ========================================================
    # TOTAL QUESTIONS
    # ========================================================

    total_questions = 5


    print(
        f"\nProgress: "
        f"{answered}/{total_questions}"
    )


    # ========================================================
    # INTERVIEW COMPLETE
    # ========================================================

    if answered >= total_questions:

        session["completed"] = True


        total_score = sum(
            session["scores"]
        )


        average_score = (

            total_score
            / answered

            if answered > 0

            else 0

        )


        print("\n" + "=" * 60)

        print(
            "INTERVIEW COMPLETED"
        )

        print("=" * 60)

        print(
            "Total score:",
            total_score
        )

        print(
            "Average:",
            round(
                average_score,
                2
            )
        )


        # ====================================================
        # GENERATE FINAL REPORT
        # ====================================================

        report = None


        try:

            report = generate_interview_report(

                role=session["role"],

                experience=session["experience"],

                difficulty=session["difficulty"],

                results=session["answers"],

                total_score=total_score,

                average_score=average_score

            )

        except TypeError:

            # Support alternative function signatures

            try:

                report = generate_interview_report(
                    session
                )

            except Exception as e:

                print(
                    "Report generation error:",
                    e
                )

        except Exception as e:

            print(
                "Report generation error:",
                e
            )


        # ====================================================
        # FALLBACK REPORT
        # ====================================================

        if report is None:

            report = {

                "summary":
                    "Interview completed successfully.",

                "strengths":
                    [],

                "weaknesses":
                    [],

                "recommendations":
                    []

            }


        print(
            "Report generated."
        )

        print("=" * 60)


        # ====================================================
        # FINAL RESPONSE
        # ====================================================

        return {

            "completed":
                True,

            "question_number":
                answered,

            "total_questions":
                answered,

            "score":
                score,

            "feedback":
                feedback,

            "total_score":
                total_score,

            "average_score":
                round(
                    average_score,
                    2
                ),

            "max_score":
                answered * 10,

            "role":
                session["role"],

            "experience":
                session["experience"],

            "difficulty":
                session["difficulty"],

            "results":
                session["answers"],

            "report":
                report

        }


    # ========================================================
    # GET NEXT QUESTION
    # ========================================================

    next_question = get_next_question(
        session
    )


    # ========================================================
    # FALLBACK IF RAG HAS NO UNUSED QUESTION
    # ========================================================

    if next_question is None:

        print(
            "No unused RAG question available."
        )


        # Try generated questions

        try:

            generated = (
                generate_interview_questions(

                    role=session["role"],

                    experience=session["experience"],

                    difficulty=session["difficulty"],

                    num_questions=5

                )
            )

        except Exception as e:

            print(
                "Fallback generation error:",
                e
            )

            generated = []


        for item in generated:

            candidate_question = item.get(
                "question",
                ""
            )


            if not candidate_question:

                continue


            if question_already_used(
                session,
                candidate_question
            ):

                continue


            next_question = item

            break


    # ========================================================
    # STILL NO QUESTION
    # ========================================================

    if next_question is None:

        print(
            "ERROR: Unable to generate next question."
        )


        return {

            "completed":
                False,

            "error":
                "Unable to generate the next interview question.",

            "score":
                score,

            "feedback":
                feedback,

            "question_number":
                answered,

            "total_questions":
                total_questions

        }


    # ========================================================
    # STORE NEXT QUESTION
    # ========================================================

    session["questions"].append(
        next_question
    )

    session["asked_questions"].append(
        next_question["question"]
    )


    next_number = answered + 1


    print(
        "\nNext question:"
    )

    print(
        next_question["question"]
    )


    # ========================================================
    # RESPONSE
    # ========================================================

    return {

        "completed":
            False,

        "score":
            score,

        "feedback":
            feedback,

        "question_number":
            next_number,

        "total_questions":
            total_questions,

        "current_question":
            next_question[
                "question"
            ],

        "next_question":
            next_question[
                "question"
            ],

        "message":
            "Answer evaluated successfully. Next question generated."

    }


# ============================================================
# GET SESSION
# ============================================================

@app.get("/session/{session_id}")
def get_session(
    session_id: str
):

    session = interview_sessions.get(
        session_id
    )


    if session is None:

        return {

            "error":
                "Interview session not found."

        }


    return {

        "session_id":
            session["session_id"],

        "role":
            session["role"],

        "experience":
            session["experience"],

        "difficulty":
            session["difficulty"],

        "completed":
            session["completed"],

        "question_count":
            len(
                session["questions"]
            ),

        "answered_count":
            len(
                session["answers"]
            ),

        "scores":
            session["scores"]

    }