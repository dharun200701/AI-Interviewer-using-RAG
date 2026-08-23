import json
import re
import ollama


# ==========================================================
# ANSWERS THAT CLEARLY MEAN THE CANDIDATE DOES NOT KNOW
# ==========================================================

NO_ANSWER_PHRASES = {
    "none",
    "no",
    "no idea",
    "i don't know",
    "i dont know",
    "don't know",
    "dont know",
    "not sure",
    "i am not sure",
    "i'm not sure",
    "unknown",
    "nothing",
    "nil",
    "n/a",
    "na",
    "cannot answer",
    "can't answer",
    "cant answer",
    "i cannot answer",
    "i can't answer",
    "i dont have an answer",
    "i don't have an answer",
}


# ==========================================================
# NO-ANSWER DETECTION
# ==========================================================

def is_no_answer(answer):

    if answer is None:
        return True

    text = str(answer).strip().lower()

    if not text:
        return True

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    if text in NO_ANSWER_PHRASES:
        return True

    if len(text.split()) <= 4:

        patterns = [

            r"^i\s+(do\s+not|don't|dont)\s+know$",

            r"^i\s+have\s+no\s+idea$",

            r"^no\s+idea$",

            r"^not\s+sure$",

            r"^i\s+am\s+not\s+sure$",

            r"^i'?m\s+not\s+sure$",

            r"^cannot\s+answer$",

            r"^can't\s+answer$",

            r"^cant\s+answer$",

            r"^no\s+answer$",

            r"^none$",

            r"^nil$",

            r"^n/?a$",
        ]

        for pattern in patterns:

            if re.match(
                pattern,
                text
            ):
                return True

    return False


# ==========================================================
# INDIVIDUAL ANSWER EVALUATION
# ==========================================================

def evaluate_with_llama(
    question,
    answer,
    ideal_answer=""
):

    # ======================================================
    # HARD RULE
    # ======================================================

    if is_no_answer(answer):

        return {

            "score": 0,

            "feedback":
                "No meaningful answer was provided. "
                "The response does not demonstrate "
                "understanding of the question."
        }


    # ======================================================
    # EVALUATION PROMPT
    # ======================================================

    prompt = f"""
You are a STRICT technical interview evaluator.

Evaluate the candidate's answer against the expected answer.

QUESTION:

{question}


EXPECTED / IDEAL ANSWER:

{ideal_answer}


CANDIDATE ANSWER:

{answer}


Evaluate using these four dimensions:

1. Correctness
2. Relevance
3. Completeness
4. Technical depth


STRICT SCORING:

0 = No answer, completely irrelevant, or completely incorrect.

1-2 = Almost no useful knowledge demonstrated.

3-4 = Significant misunderstanding or major missing concepts.

5 = Partially correct but several important issues or missing concepts.

6 = Mostly correct but incomplete or has noticeable weaknesses.

7 = Strong and mostly complete answer.

8 = Very strong answer with good technical depth.

9 = Exceptional answer with excellent technical understanding.

10 = Expert-level answer, highly accurate, complete, and technically deep.


IMPORTANT RULES:

- Be STRICT.
- Do NOT give high scores just because the answer is long.
- Do NOT reward confidence, repetition, or generic statements.
- A technically incorrect answer must receive a low score.
- Missing important concepts must reduce the score.
- A partially correct answer must not receive 7 or higher.
- If the candidate misunderstands the core concept, score 4 or below.
- If the answer contains a major technical error, score 4 or below.
- Short but correct answers may score well when appropriate.
- For programming questions, consider correctness, reasoning,
  edge cases, and complexity when relevant.
- For system design questions, consider architecture,
  scalability, reliability, trade-offs, and bottlenecks.
- For database questions, consider correctness, indexing,
  transactions, normalization, and query behavior.
- For API/backend questions, consider HTTP concepts,
  authentication, validation, error handling, scalability,
  and security.
- When uncertain between two scores, ALWAYS choose the LOWER score.
- Scores of 8, 9, or 10 should be uncommon.

Return ONLY valid JSON:

{{
    "score": 0,
    "feedback": "Specific technical feedback explaining what was correct, what was missing or wrong, and how the answer could be improved."
}}
"""


    # ======================================================
    # CALL OLLAMA
    # ======================================================

    try:

        response = ollama.chat(

            model="gemma:2b",

            messages=[

                {
                    "role": "user",
                    "content": prompt
                }

            ]
        )


        content = (
            response["message"]["content"]
            .strip()
        )


        print(
            "\nLLM evaluation response:"
        )

        print(content)


        # ==================================================
        # PARSE JSON
        # ==================================================

        try:

            result = json.loads(
                content
            )

        except json.JSONDecodeError:

            match = re.search(
                r"\{.*\}",
                content,
                re.DOTALL
            )

            if match:

                result = json.loads(
                    match.group()
                )

            else:

                raise ValueError(
                    "Could not find JSON in LLM response."
                )


        # ==================================================
        # SCORE
        # ==================================================

        score = result.get(
            "score",
            0
        )

        feedback = result.get(
            "feedback",
            "No feedback provided."
        )


        try:

            score = int(
                float(score)
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


        return {

            "score":
                score,

            "feedback":
                str(feedback)
        }


    except Exception as e:

        print(
            "Evaluation error:",
            e
        )


        return {

            "score":
                0,

            "feedback":
                "Unable to evaluate the answer."
        }


# ==========================================================
# FINAL INTERVIEW REPORT
# ==========================================================

def generate_interview_report(
    role,
    experience,
    difficulty,
    results
):

    print(
        "\n" + "=" * 60
    )

    print(
        "GENERATING FINAL INTERVIEW REPORT"
    )

    print(
        "=" * 60
    )


    # ======================================================
    # SAFETY CHECK
    # ======================================================

    if not results:

        return {

            "overall_score": 0,

            "average_score": 0,

            "performance_level":
                "No Data",

            "strengths": [],

            "weaknesses": [],

            "areas_for_improvement": [],

            "recommendation":
                "Reject",

            "summary":
                "No interview answers were provided."
        }


    # ======================================================
    # CALCULATE REAL SCORE
    # ======================================================

    scores = []

    for item in results:

        try:

            score = float(
                item.get(
                    "score",
                    0
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

        scores.append(
            score
        )


    average_score = (

        sum(scores) / len(scores)

        if scores

        else 0
    )


    average_score = round(
        average_score,
        2
    )


    # ======================================================
    # BUILD INTERVIEW DATA
    # ======================================================

    interview_data = []

    for index, item in enumerate(
        results,
        1
    ):

        interview_data.append(

            f"""
Question {index}:
{item.get("question", "")}

Candidate Answer:
{item.get("answer", "")}

Score:
{item.get("score", 0)}/10

Feedback:
{item.get("feedback", "")}

Category:
{item.get("category", "")}

Difficulty:
{item.get("difficulty", "")}
"""
        )


    combined_data = "\n".join(
        interview_data
    )


    # ======================================================
    # REPORT PROMPT
    # ======================================================

    prompt = f"""
You are a STRICT professional technical interview
assessment system.

Generate a final interview performance report.

CANDIDATE INFORMATION:

Role:
{role}

Experience:
{experience}

Difficulty:
{difficulty}


INTERVIEW RESULTS:

{combined_data}


CALCULATED AVERAGE SCORE:

{average_score}/10


Evaluate the candidate based ONLY on the interview
answers and evaluation results.

Analyze:

1. Overall performance
2. Technical strengths
3. Technical weaknesses
4. Areas for improvement
5. Hiring recommendation
6. Professional summary


STRICT RULES:

- Do not invent skills.
- Do not assume knowledge that was not demonstrated.
- Do not reward long answers automatically.
- Do not reward generic statements.
- Weak answers must affect the assessment.
- No-answer responses must be treated as failures.
- The recommendation must match the actual performance.
- Be honest and critical.
- Keep strengths and weaknesses technically specific.


PERFORMANCE LEVEL:

0-2 = Very Poor

3-4 = Poor

5 = Average

6 = Fair

7 = Good

8 = Very Good

9 = Excellent

10 = Exceptional


RECOMMENDATION:

Use exactly one of:

"Strong Hire"

"Hire"

"Consider"

"Reject"


Return ONLY valid JSON.

Required format:

{{
    "overall_score": 0,
    "average_score": 0,
    "performance_level": "Good",
    "strengths": [
        "strength 1",
        "strength 2"
    ],
    "weaknesses": [
        "weakness 1",
        "weakness 2"
    ],
    "areas_for_improvement": [
        "area 1",
        "area 2"
    ],
    "recommendation": "Consider",
    "summary": "Professional summary of the candidate's performance."
}}
"""


    # ======================================================
    # CALL OLLAMA
    # ======================================================

    try:

        response = ollama.chat(

            model="gemma:2b",

            messages=[

                {
                    "role": "user",
                    "content": prompt
                }

            ]
        )


        content = (
            response["message"]["content"]
            .strip()
        )


        print(
            "\nFinal report LLM response:"
        )

        print(content)


        # ==================================================
        # PARSE JSON
        # ==================================================

        try:

            report = json.loads(
                content
            )

        except json.JSONDecodeError:

            match = re.search(
                r"\{.*\}",
                content,
                re.DOTALL
            )

            if match:

                report = json.loads(
                    match.group()
                )

            else:

                raise ValueError(
                    "Could not find JSON in final report."
                )


        # ==================================================
        # KEEP SCORE CONSISTENT
        # ==================================================

        # We use the actual calculated average
        # instead of allowing the LLM to invent
        # another score.

        overall_score = average_score


        performance_level = str(
            report.get(
                "performance_level",
                "Unknown"
            )
        )


        strengths = report.get(
            "strengths",
            []
        )


        weaknesses = report.get(
            "weaknesses",
            []
        )


        areas_for_improvement = report.get(
            "areas_for_improvement",
            []
        )


        recommendation = str(
            report.get(
                "recommendation",
                "Consider"
            )
        )


        summary = str(
            report.get(
                "summary",
                "No summary available."
            )
        )


        # ==================================================
        # SAFETY
        # ==================================================

        if not isinstance(
            strengths,
            list
        ):

            strengths = [
                str(strengths)
            ]


        if not isinstance(
            weaknesses,
            list
        ):

            weaknesses = [
                str(weaknesses)
            ]


        if not isinstance(
            areas_for_improvement,
            list
        ):

            areas_for_improvement = [
                str(areas_for_improvement)
            ]


        # ==================================================
        # FINAL REPORT
        # ==================================================

        final_report = {

            "overall_score":
                overall_score,

            "average_score":
                average_score,

            "performance_level":
                performance_level,

            "strengths":
                strengths,

            "weaknesses":
                weaknesses,

            "areas_for_improvement":
                areas_for_improvement,

            "recommendation":
                recommendation,

            "summary":
                summary
        }


        print(
            "\nFinal report:"
        )

        print(
            json.dumps(
                final_report,
                indent=4
            )
        )


        return final_report


    except Exception as e:

        print(
            "Final report generation error:",
            e
        )


        # ==================================================
        # FALLBACK
        # ==================================================

        if average_score >= 8:

            performance_level = "Very Good"

            recommendation = "Strong Hire"

        elif average_score >= 7:

            performance_level = "Good"

            recommendation = "Hire"

        elif average_score >= 5:

            performance_level = "Average"

            recommendation = "Consider"

        else:

            performance_level = "Poor"

            recommendation = "Reject"


        return {

            "overall_score":
                average_score,

            "average_score":
                average_score,

            "performance_level":
                performance_level,

            "strengths": [],

            "weaknesses": [],

            "areas_for_improvement": [],

            "recommendation":
                recommendation,

            "summary":
                "The interview was completed, but the detailed AI report could not be generated."
        }