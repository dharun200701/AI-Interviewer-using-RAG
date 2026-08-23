import { useState } from "react";
import axios from "axios";

function App() {
  const [role, setRole] = useState("");
  const [experience, setExperience] = useState("");
  const [difficulty, setDifficulty] = useState("");

  const [questions, setQuestions] = useState([]);
  const [currentQuestion, setCurrentQuestion] = useState(0);

  const [answer, setAnswer] = useState("");
  const [results, setResults] = useState([]);

  const [sessionId, setSessionId] = useState("");

  const [started, setStarted] = useState(false);
  const [completed, setCompleted] = useState(false);

  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");


  // =====================================================
  // START INTERVIEW
  // =====================================================

  const startInterview = async () => {
    if (!role || !experience || !difficulty) {
      setMessage(
        "Please select Role, Experience and Difficulty."
      );
      return;
    }

    setLoading(true);
    setMessage("");

    try {
      const response = await axios.post(
        "http://127.0.0.1:8000/start_interview",
        {
          role: role,
          experience: experience,
          difficulty: difficulty,
        }
      );

      console.log(
        "START INTERVIEW RESPONSE:",
        response.data
      );


      // =================================================
      // CHECK BACKEND RESPONSE
      // =================================================

      if (
        !response.data ||
        !response.data.session_id
      ) {
        setMessage(
          response.data?.error ||
            "Invalid response from server."
        );

        setLoading(false);
        return;
      }


      // =================================================
      // GET QUESTIONS
      // =================================================

      let receivedQuestions =
        response.data.questions || [];


      // =================================================
      // SAFELY CONVERT QUESTIONS
      //
      // Backend normally sends:
      //
      // [
      //   "Question 1",
      //   "Question 2"
      // ]
      //
      // But if an object is returned, this also
      // handles:
      //
      // {
      //   question: "Question 1"
      // }
      // =================================================

      receivedQuestions =
        receivedQuestions
          .map((item) => {

            if (
              typeof item === "string"
            ) {
              return item.trim();
            }

            if (
              item &&
              typeof item === "object"
            ) {
              return (
                item.question || ""
              ).trim();
            }

            return "";
          })
          .filter(
            (question) =>
              question.length > 0
          );


      console.log(
        "QUESTIONS RECEIVED:",
        receivedQuestions
      );


      // =================================================
      // NO QUESTIONS
      // =================================================

      if (
        receivedQuestions.length === 0
      ) {
        setMessage(
          "The server did not return any interview questions."
        );

        setLoading(false);
        return;
      }


      // =================================================
      // SET INTERVIEW STATE
      // =================================================

      setQuestions(
        receivedQuestions
      );

      setSessionId(
        response.data.session_id
      );

      setCurrentQuestion(0);

      setAnswer("");

      setResults([]);

      setStarted(true);

      setCompleted(false);

      setMessage(
        `Interview started with ${receivedQuestions.length} questions.`
      );

    } catch (error) {

      console.error(
        "START INTERVIEW ERROR:",
        error
      );

      setMessage(
        error.response?.data?.error ||
          "Failed to start interview."
      );

    } finally {

      setLoading(false);

    }
  };


  // =====================================================
  // SUBMIT ANSWER
  // =====================================================

  const submitAnswer = async () => {

    // ================================================
    // SAFETY CHECK
    // ================================================

    if (
      !questions ||
      questions.length === 0
    ) {
      setMessage(
        "No interview question is available."
      );

      return;
    }


    // ================================================
    // CURRENT QUESTION
    // ================================================

    const currentQuestionText =
      questions[currentQuestion];


    console.log(
      "CURRENT QUESTION:",
      currentQuestionText
    );


    if (
      !currentQuestionText ||
      !currentQuestionText.trim()
    ) {
      setMessage(
        "Question is empty. Please restart the interview."
      );

      return;
    }


    // ================================================
    // ANSWER VALIDATION
    // ================================================

    if (!answer.trim()) {
      setMessage(
        "Please enter an answer before submitting."
      );

      return;
    }


    // ================================================
    // SESSION VALIDATION
    // ================================================

    if (!sessionId) {
      setMessage(
        "Interview session is missing. Please restart."
      );

      return;
    }


    setLoading(true);
    setMessage("");


    try {

      const response = await axios.post(
        "http://127.0.0.1:8000/submit_answer",
        {
          session_id: sessionId,

          question:
            currentQuestionText,

          answer: answer.trim(),
        }
      );


      console.log(
        "SUBMIT ANSWER RESPONSE:",
        response.data
      );


      // =================================================
      // BACKEND ERROR
      // =================================================

      if (
        response.data?.error
      ) {
        setMessage(
          response.data.error
        );

        setLoading(false);

        return;
      }


      // =================================================
      // INTERVIEW COMPLETED
      // =================================================

      if (
        response.data?.completed === true
      ) {

        console.log(
          "INTERVIEW COMPLETED:",
          response.data
        );


        setResults(
          response.data.results || []
        );

        setCompleted(true);

        setStarted(false);

        setMessage(
          "Interview completed successfully."
        );

        setLoading(false);

        return;
      }


      // =================================================
      // NEXT QUESTION FROM BACKEND
      // =================================================
      //
      // New backend can return:
      //
      // next_question: "..."
      //
      // OR
      //
      // next_question: {
      //    question: "..."
      // }
      //
      // We support both.
      // =================================================

      let nextQuestion =
        response.data?.next_question;


      if (
        nextQuestion &&
        typeof nextQuestion === "object"
      ) {
        nextQuestion =
          nextQuestion.question || "";
      }


      if (
        typeof nextQuestion === "string"
      ) {
        nextQuestion =
          nextQuestion.trim();
      }


      console.log(
        "NEXT QUESTION FROM BACKEND:",
        nextQuestion
      );


      // =================================================
      // IF BACKEND PROVIDED NEXT QUESTION
      // =================================================

      if (
        nextQuestion
      ) {

        setQuestions(
          (previousQuestions) => {

            const updatedQuestions = [
              ...previousQuestions
            ];

            const nextIndex =
              currentQuestion + 1;

            updatedQuestions[
              nextIndex
            ] = nextQuestion;

            return updatedQuestions;
          }
        );

        setCurrentQuestion(
          (previous) =>
            previous + 1
        );

        setAnswer("");

        setMessage(
          "Answer submitted successfully."
        );

        setLoading(false);

        return;
      }


      // =================================================
      // FALLBACK
      //
      // If backend doesn't send next_question,
      // use the original question list.
      // =================================================

      const nextIndex =
        currentQuestion + 1;


      if (
        nextIndex <
        questions.length
      ) {

        setCurrentQuestion(
          nextIndex
        );

        setAnswer("");

        setMessage(
          "Answer submitted successfully."
        );

      } else {

        setMessage(
          "Interview completed, but the server did not return the final result."
        );

      }

    } catch (error) {

      console.error(
        "SUBMIT ANSWER ERROR:",
        error
      );

      setMessage(
        error.response?.data?.error ||
          "Failed to submit answer."
      );

    } finally {

      setLoading(false);

    }
  };


  // =====================================================
  // RESTART INTERVIEW
  // =====================================================

  const restartInterview = () => {

    setRole("");

    setExperience("");

    setDifficulty("");

    setQuestions([]);

    setCurrentQuestion(0);

    setAnswer("");

    setResults([]);

    setSessionId("");

    setStarted(false);

    setCompleted(false);

    setLoading(false);

    setMessage("");
  };


  // =====================================================
  // START SCREEN
  // =====================================================

  if (
    !started &&
    !completed
  ) {

    return (
      <div
        style={{
          maxWidth: "700px",
          margin: "50px auto",
          padding: "30px",
          fontFamily: "Arial",
        }}
      >

        <h1>
          AI Interview Assistant
        </h1>

        <p>
          Select your interview preferences.
        </p>


        {/* ==========================================
            ROLE
        =========================================== */}

        <label>
          <strong>
            Role
          </strong>
        </label>

        <select
          value={role}
          onChange={(e) =>
            setRole(
              e.target.value
            )
          }
          style={{
            width: "100%",
            padding: "12px",
            marginTop: "8px",
            marginBottom: "20px",
          }}
        >

          <option value="">
            Select Role
          </option>

          <option value="Software Engineer">
            Software Engineer
          </option>

          <option value="DevOps Engineer">
            DevOps Engineer
          </option>

          <option value="Data Scientist">
            Data Scientist
          </option>

          <option value="QA Analyst">
            QA Analyst
          </option>

          <option value="Product Manager">
            Product Manager
          </option>

          <option value="UX Designer">
            UX Designer
          </option>

          <option value="Marketing Associate">
            Marketing Associate
          </option>

          <option value="HR Specialist">
            HR Specialist
          </option>

        </select>


        {/* ==========================================
            EXPERIENCE
        =========================================== */}

        <label>
          <strong>
            Experience
          </strong>
        </label>

        <select
          value={experience}
          onChange={(e) =>
            setExperience(
              e.target.value
            )
          }
          style={{
            width: "100%",
            padding: "12px",
            marginTop: "8px",
            marginBottom: "20px",
          }}
        >

          <option value="">
            Select Experience
          </option>

          <option value="fresher">
            Fresher
          </option>

          <option value="intern">
            Intern
          </option>

          <option value="1 year">
            1 year
          </option>

          <option value="2 years">
            2 years
          </option>

          <option value="3 years">
            3 years
          </option>

          <option value="4 years">
            4 years
          </option>

          <option value="5 years">
            5 years
          </option>

          <option value="6 years">
            6 years
          </option>

          <option value="7+ years">
            7+ years
          </option>

        </select>


        {/* ==========================================
            DIFFICULTY
        =========================================== */}

        <label>
          <strong>
            Difficulty
          </strong>
        </label>

        <select
          value={difficulty}
          onChange={(e) =>
            setDifficulty(
              e.target.value
            )
          }
          style={{
            width: "100%",
            padding: "12px",
            marginTop: "8px",
            marginBottom: "20px",
          }}
        >

          <option value="">
            Select Difficulty
          </option>

          <option value="Easy">
            Easy
          </option>

          <option value="Medium">
            Medium
          </option>

          <option value="Hard">
            Hard
          </option>

        </select>


        {/* ==========================================
            START BUTTON
        =========================================== */}

        <button
          onClick={startInterview}
          disabled={loading}
          style={{
            width: "100%",
            padding: "14px",
            fontSize: "16px",
            cursor: loading
              ? "not-allowed"
              : "pointer",
          }}
        >

          {loading
            ? "Starting Interview..."
            : "Start Interview"}

        </button>


        {/* ==========================================
            MESSAGE
        =========================================== */}

        {message && (

          <p
            style={{
              marginTop: "20px",
            }}
          >
            {message}
          </p>

        )}

      </div>
    );
  }


  // =====================================================
  // INTERVIEW SCREEN
  // =====================================================

  if (started) {

    const question =
      questions[currentQuestion] || "";


    return (
      <div
        style={{
          maxWidth: "800px",
          margin: "50px auto",
          padding: "30px",
          fontFamily: "Arial",
        }}
      >

        <h1>
          AI Interview
        </h1>


        {/* ==========================================
            INTERVIEW INFORMATION
        =========================================== */}

        <div
          style={{
            marginBottom: "20px",
          }}
        >

          <strong>
            Role:
          </strong>{" "}
          {role}

          <br />

          <strong>
            Experience:
          </strong>{" "}
          {experience}

          <br />

          <strong>
            Difficulty:
          </strong>{" "}
          {difficulty}

        </div>


        <hr />


        {/* ==========================================
            QUESTION NUMBER
        =========================================== */}

        <h3>
          Question{" "}
          {currentQuestion + 1}{" "}
          of{" "}
          {questions.length}
        </h3>


        {/* ==========================================
            QUESTION
        =========================================== */}

        <div
          style={{
            minHeight: "80px",
            marginTop: "15px",
            marginBottom: "20px",
            padding: "20px",
            border: "1px solid #ddd",
            borderRadius: "8px",
            backgroundColor: "#f8f8f8",
          }}
        >

          {question ? (

            <h2
              style={{
                margin: 0,
                color: "#111",
                lineHeight: "1.5",
              }}
            >
              {question}
            </h2>

          ) : (

            <h2
              style={{
                margin: 0,
                color: "#666",
              }}
            >
              Loading question...
            </h2>

          )}

        </div>


        {/* ==========================================
            ANSWER
        =========================================== */}

        <textarea
          value={answer}
          onChange={(e) =>
            setAnswer(
              e.target.value
            )
          }
          placeholder="Type your answer here..."
          rows="8"
          disabled={loading}
          style={{
            width: "100%",
            padding: "12px",
            marginTop: "10px",
            fontSize: "16px",
            boxSizing: "border-box",
          }}
        />


        {/* ==========================================
            SUBMIT BUTTON
        =========================================== */}

        <button
          onClick={submitAnswer}
          disabled={
            loading ||
            !question
          }
          style={{
            width: "100%",
            padding: "14px",
            marginTop: "15px",
            fontSize: "16px",
            cursor:
              loading || !question
                ? "not-allowed"
                : "pointer",
          }}
        >

          {loading
            ? "Evaluating..."
            : currentQuestion ===
                questions.length - 1
              ? "Submit Final Answer"
              : "Submit Answer"}

        </button>


        {/* ==========================================
            MESSAGE
        =========================================== */}

        {message && (

          <p
            style={{
              marginTop: "20px",
            }}
          >
            {message}
          </p>

        )}

      </div>
    );
  }


  // =====================================================
  // RESULTS SCREEN
  // =====================================================

  if (completed) {

    const totalScore =
      results.reduce(
        (sum, item) =>
          sum +
          Number(
            item.score || 0
          ),
        0
      );


    const maxScore =
      results.length * 10;


    const average =
      results.length > 0
        ? totalScore /
          results.length
        : 0;


    return (
      <div
        style={{
          maxWidth: "800px",
          margin: "50px auto",
          padding: "30px",
          fontFamily: "Arial",
        }}
      >

        <h1>
          Interview Completed
        </h1>


        {/* ==========================================
            OVERALL SCORE
        =========================================== */}

        <h2>
          Overall Score:{" "}
          {totalScore} /{" "}
          {maxScore}
        </h2>


        <h3>
          Average:{" "}
          {average.toFixed(2)} / 10
        </h3>


        <hr />


        {/* ==========================================
            INDIVIDUAL RESULTS
        =========================================== */}

        {results.length === 0 ? (

          <p>
            No evaluation results available.
          </p>

        ) : (

          results.map(
            (result, index) => (

              <div
                key={index}
                style={{
                  marginBottom: "30px",
                  padding: "20px",
                  border:
                    "1px solid #ddd",
                  borderRadius: "8px",
                }}
              >

                <h3>
                  Question{" "}
                  {index + 1}
                </h3>


                <p>
                  <strong>
                    {result.question}
                  </strong>
                </p>


                <p>
                  <strong>
                    Your Answer:
                  </strong>
                </p>


                <p>
                  {result.answer ||
                    "No answer provided."}
                </p>


                <p>
                  <strong>
                    Score:
                  </strong>{" "}
                  {result.score} / 10
                </p>


                <p>
                  <strong>
                    Feedback:
                  </strong>{" "}
                  {result.feedback ||
                    "No feedback provided."}
                </p>

              </div>

            )
          )

        )}


        {/* ==========================================
            NEW INTERVIEW
        =========================================== */}

        <button
          onClick={
            restartInterview
          }
          style={{
            width: "100%",
            padding: "14px",
            fontSize: "16px",
          }}
        >
          Start New Interview
        </button>

      </div>
    );
  }


  // =====================================================
  // FALLBACK
  // =====================================================

  return null;
}

export default App;