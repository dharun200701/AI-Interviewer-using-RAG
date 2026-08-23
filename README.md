
# 🤖 AI Interviewer using RAG

An AI-powered technical interview assistant that uses **Retrieval-Augmented Generation (RAG)**, **FAISS vector search**, **Sentence Transformers**, **Ollama LLM**, **FastAPI**, and **React** to conduct personalized technical interviews and evaluate candidate answers.

The system generates interview questions based on the candidate's:

- Role
- Experience level
- Difficulty level

It then evaluates each answer strictly, calculates scores, provides technical feedback, and generates a final interview result.

---

# 📌 Project Overview

The goal of this project is to build an AI-based interview platform that simulates a technical interview.

Instead of generating completely random questions, the application uses a **RAG pipeline** to retrieve relevant questions from an interview question dataset.

The overall architecture is:


                    ┌──────────────────────┐
                    │      React Frontend  │
                    │                      │
                    │ Role                 │
                    │ Experience           │
                    │ Difficulty           │
                    └──────────┬───────────┘
                               │
                               │ HTTP / Axios
                               ▼
                    ┌──────────────────────┐
                    │    FastAPI Backend   │
                    │                      │
                    │ Interview Sessions   │
                    │ Question Management  │
                    │ Answer Submission    │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │  Interviewer Agent   │
                    │                      │
                    │ Question Selection   │
                    │ Answer Evaluation    │
                    └──────────┬───────────┘
                               │
                ┌──────────────┴──────────────┐
                ▼                             ▼
       ┌─────────────────┐           ┌─────────────────┐
       │   RAG Pipeline  │           │   LLM Evaluator │
       │                 │           │                 │
       │ Sentence        │           │ Ollama          │
       │ Transformers    │           │ Gemma           │
       │ FAISS           │           │ Strict Scoring  │
       └────────┬────────┘           └─────────────────┘
                │
                ▼
       ┌─────────────────────┐
       │ Interview Dataset   │
       │ hr_questions.json   │
       └─────────────────────┘



# ✨ Features

## 🎯 Personalized Interviews

The candidate can select:

* Role
* Experience
* Difficulty

Example:


Role: DevOps Engineer
Experience: 1 year
Difficulty: Medium


The system then generates an interview specifically for those preferences.



## 🧠 Retrieval-Augmented Generation

The project uses a RAG-based question retrieval system.

The question dataset is converted into vector embeddings using:

```text
SentenceTransformer
all-MiniLM-L6-v2
```

These embeddings are stored in a FAISS vector index.

When an interview starts:

```text
Candidate Preferences
        ↓
Semantic Query
        ↓
Sentence Transformer
        ↓
Query Embedding
        ↓
FAISS Search
        ↓
Relevant Questions
        ↓
Role Filtering
        ↓
Experience/Difficulty Matching
        ↓
Question Selection
```

This allows the application to retrieve questions that are semantically relevant rather than relying only on exact keyword matching.

---

# 🔎 RAG Pipeline

The main RAG implementation is located in:

```text
backend/rag_pipeline.py
```

The pipeline performs the following operations:

1. Loads the Sentence Transformer model.
2. Loads the FAISS vector database.
3. Loads the interview question dataset.
4. Converts the candidate's query into an embedding.
5. Searches FAISS for similar questions.
6. Filters questions according to the requested role.
7. Removes duplicate questions.
8. Calculates similarity scores.
9. Returns the most relevant questions.

The embedding model currently used is:

```text
all-MiniLM-L6-v2
```

The embeddings are normalized, allowing FAISS inner-product similarity to behave like cosine similarity.

---

# 🗂️ Dataset

The interview question dataset is stored in:

```text
dataset/hr_questions.json
```

The dataset contains information such as:

```json
{
    "role": "Software Engineer",
    "question": "What is object-oriented programming?",
    "ideal_answer": "Object-oriented programming is...",
    "category": "Programming",
    "difficulty": "Medium",
    "experience": "fresher",
    "keywords": [
        "OOP",
        "classes",
        "objects"
    ]
}
```

The exact fields can vary depending on the question.

Important information includes:

* `role`
* `question`
* `ideal_answer`
* `category`
* `difficulty`
* `experience`
* `keywords`

---

# 🗃️ FAISS Vector Database

The generated FAISS index is stored locally in:

```text
vector_db/hr_questions.index
```

Additional generated indexes may also exist, such as:

```text
vector_db/hr_questions_old.index
```

These files are intentionally **not uploaded to GitHub** because the FAISS index can become very large.

The `.gitignore` contains:

```gitignore
vector_db/*.index
```

Therefore generated FAISS indexes remain local.

This keeps the GitHub repository lightweight.

---

# 👨‍💻 Interviewer Agent

The main interview logic is implemented in:

```text
backend/interviewer_agent.py
```

The interviewer agent is responsible for:

* Retrieving interview questions
* Matching questions to role
* Matching experience
* Matching difficulty
* Randomizing question selection
* Evaluating candidate answers

The agent uses the RAG pipeline:

```python
from rag_pipeline import search_questions
```

and the LLM evaluator:

```python
from llm_evaluator import evaluate_with_llama
```

The interviewer agent also supports report generation through:

```python
generate_interview_report
```

---

# 🎲 Question Selection

The application does not always return exactly the same questions.

The system:

1. Retrieves a pool of relevant questions.
2. Scores them according to role, experience, and difficulty.
3. Creates a quality pool.
4. Randomly selects questions from that pool.
5. Randomizes the final question order.

The interview normally contains:

```text
4–5 questions
```

This provides variation between interviews while keeping the questions relevant.

---

# 🧑‍⚖️ Strict Answer Evaluation

The answer evaluation system is implemented in:

```text
backend/llm_evaluator.py
```

The project uses Ollama to run the local LLM.

Current model:

```text
gemma:2b
```

The evaluator compares:

```text
Question
     +
Ideal Answer
     +
Candidate Answer
```

and evaluates the answer using:

1. Correctness
2. Relevance
3. Completeness
4. Technical depth

---

# 📊 Scoring System

Answers are scored from:

```text
0 → 10
```

The scoring rules are intentionally strict.

```text
0     = No answer / completely incorrect
1–2   = Almost no useful knowledge
3–4   = Significant misunderstanding
5     = Partially correct with important missing concepts
6     = Mostly correct but incomplete
7     = Strong and mostly complete
8     = Very strong technical answer
9     = Exceptional answer
10    = Expert-level answer
```

The evaluator is instructed to avoid giving high scores simply because an answer is long.

It also considers:

* Technical accuracy
* Missing concepts
* Incorrect assumptions
* Core concept understanding
* Complexity
* Edge cases
* Security
* Scalability
* Architecture
* Database concepts
* API concepts

depending on the question.

---

# 🚫 No-Answer Detection

The system includes special handling for answers such as:

```text
none
no
no idea
i don't know
i dont know
don't know
not sure
i am not sure
unknown
nothing
nil
n/a
cannot answer
can't answer
cant answer
```

These answers are detected before sending them to the LLM.

They receive:

```text
Score: 0/10
```

This prevents the LLM from accidentally giving a high score to a candidate who did not provide an answer.

---

# 🧠 LLM Evaluation Flow

The evaluation process is:

```text
Candidate Answer
       │
       ▼
No-Answer Detection
       │
       ├── No Answer
       │       ↓
       │     Score 0
       │
       └── Meaningful Answer
               ↓
        Ollama / Gemma
               ↓
        Strict Evaluation
               ↓
        JSON Response
               ↓
          Score + Feedback
```

The expected output is:

```json
{
    "score": 7,
    "feedback": "The answer correctly explains..."
}
```

---

# 🌐 FastAPI Backend

The backend is implemented using:

```text
FastAPI
```

Main backend file:

```text
backend/main.py
```

The backend provides API endpoints for:

* Starting an interview
* Submitting answers
* Managing interview sessions
* Returning interview results

---

# 🚀 Start Interview API

Endpoint:

```text
POST /start_interview
```

Request:

```json
{
    "role": "DevOps Engineer",
    "experience": "1 year",
    "difficulty": "Medium"
}
```

The backend:

1. Receives the interview preferences.
2. Calls the interviewer agent.
3. Retrieves relevant questions.
4. Creates an interview session.
5. Generates a unique session ID.
6. Returns the questions to the frontend.

Example response:

```json
{
    "session_id": "unique-session-id",
    "questions": [
        "What is Docker?",
        "What is CI/CD?",
        "What is Kubernetes?"
    ],
    "total_questions": 3,
    "role": "DevOps Engineer",
    "experience": "1 year",
    "difficulty": "Medium"
}
```

---

# 📝 Submit Answer API

Endpoint:

```text
POST /submit_answer
```

Request:

```json
{
    "session_id": "unique-session-id",
    "question": "What is Docker?",
    "answer": "Docker is a containerization platform..."
}
```

The backend:

1. Finds the interview session.
2. Finds the question metadata.
3. Retrieves the ideal answer.
4. Sends the answer to the evaluator.
5. Receives a score and feedback.
6. Stores the result.
7. Moves to the next question.
8. Returns the final report after the last question.

---

# 🔐 Interview Sessions

Each interview receives a unique session ID.

Example:

```text
550e8400-e29b-41d4-a716-446655440000
```

The backend stores:

```text
Role
Experience
Difficulty
Questions
Answers
Scores
Feedback
```

This allows multiple interview sessions to be handled independently.

---

# ⚛️ React Frontend

The frontend is implemented using:

```text
React
```

Main frontend file:

```text
frontend/src/App.jsx
```

Axios is used for communication with the FastAPI backend.

The frontend provides:

* Interview setup screen
* Role selection
* Experience selection
* Difficulty selection
* Interview question display
* Answer input
* Submit answer button
* Loading state
* Progress indicator
* Final score
* Individual question results
* Feedback
* Restart interview

---

# 🎨 Interview Flow

The frontend flow is:

```text
Start Screen
     │
     ▼
Select Role
     │
     ▼
Select Experience
     │
     ▼
Select Difficulty
     │
     ▼
Start Interview
     │
     ▼
Question 1
     │
     ▼
Submit Answer
     │
     ▼
Evaluate Answer
     │
     ▼
Question 2
     │
     ▼
...
     │
     ▼
Final Question
     │
     ▼
Interview Completed
     │
     ▼
Final Results
```

---

# 📊 Current Results Screen

After the interview is completed, the frontend displays:

```text
Interview Completed

Overall Score: X / Y

Average: X / 10
```

For each question, it displays:

```text
Question

Your Answer

Score

Feedback
```

The candidate can then start a new interview.

---

# 🧾 Interview Reports

The project also includes report-generation support.

Reports can be useful for a future dashboard because they can provide structured information such as:

* Overall score
* Average score
* Individual question scores
* Candidate answers
* Feedback
* Strengths
* Weaknesses
* Technical performance
* Interview difficulty
* Role
* Experience
* Recommendations

The report layer is especially useful if the frontend is later expanded into an analytics dashboard.

---

# 📈 Future Dashboard

The current system can be extended into a dashboard containing:

```text
Candidate Dashboard
│
├── Overall Score
├── Average Score
├── Interview History
├── Question-wise Scores
├── Technical Strengths
├── Weak Areas
├── Performance Trends
├── Role-wise Performance
├── Difficulty-wise Performance
└── AI Recommendations
```

Possible visualizations include:

* Score cards
* Progress charts
* Performance graphs
* Category-wise performance
* Difficulty-wise performance
* Interview history
* Skill analysis

---

# 🛠️ Technologies Used

## Frontend

```text
React
Axios
JavaScript
HTML
CSS
```

## Backend

```text
Python
FastAPI
Pydantic
Uvicorn
```

## AI / Machine Learning

```text
Sentence Transformers
all-MiniLM-L6-v2
FAISS
Ollama
Gemma 2B
```

## Data

```text
JSON
```

## Version Control

```text
Git
GitHub
```

---

# 📁 Project Structure

```text
AI-Interviewer-using-RAG/
│
├── backend/
│   │
│   ├── main.py
│   ├── interviewer_agent.py
│   ├── rag_pipeline.py
│   ├── llm_evaluator.py
│   ├── requirements.txt
│   │
│   └── ...
│
├── frontend/
│   │
│   ├── src/
│   │   ├── App.jsx
│   │   └── ...
│   │
│   ├── package.json
│   └── ...
│
├── dataset/
│   │
│   └── hr_questions.json
│
├── vector_db/
│   │
│   └── hr_questions.index
│       (generated locally and ignored by Git)
│
├── .gitignore
│
└── README.md
```

---

# ⚙️ Installation

## 1. Clone the Repository

```bash
git clone https://github.com/dharun200701/AI-Interviewer-using-RAG.git
```

Move into the project:

```bash
cd AI-Interviewer-using-RAG
```

---

# 🐍 Backend Setup

Go to the backend directory:

```bash
cd backend
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate it on Windows:

```powershell
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# 🤖 Ollama Setup

Install Ollama on your system.

After installing Ollama, download the model:

```bash
ollama pull gemma:2b
```

Make sure Ollama is running before starting the backend.

Test the model:

```bash
ollama run gemma:2b
```

The LLM evaluator uses this local model to evaluate candidate answers.

---

# 🧠 FAISS Index

The FAISS vector index is intentionally not included in GitHub because it can be hundreds of megabytes in size.

The expected local file is:

```text
vector_db/hr_questions.index
```

The project uses:

```text
dataset/hr_questions.json
```

as the source dataset.

The FAISS index can be generated from the dataset using the project's indexing script.

If the index does not exist, it should be generated before starting the RAG application.

---

# 🚀 Start the Backend

From the `backend` directory:

```bash
uvicorn main:app --reload
```

The backend should run at:

```text
http://127.0.0.1:8000
```

You can test the API by opening:

```text
http://127.0.0.1:8000
```

Expected response:

```json
{
    "message": "AI Interview Assistant Running 🚀"
}
```

FastAPI documentation is also available at:

```text
http://127.0.0.1:8000/docs
```

---

# ⚛️ Frontend Setup

Open another terminal.

Go to:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start the React development server:

```bash
npm run dev
```

The frontend will normally be available at:

```text
http://localhost:5173
```

---

# 🔗 Frontend ↔ Backend Communication

The React frontend communicates with FastAPI using Axios.

Example:

```javascript
axios.post(
    "http://127.0.0.1:8000/start_interview",
    {
        role,
        experience,
        difficulty
    }
);
```

Answers are submitted through:

```text
POST /submit_answer
```

The backend returns evaluation results to the frontend.

---

# 🔒 Git and Large Files

The FAISS index is intentionally excluded from GitHub.

The root `.gitignore` contains:

```gitignore
vector_db/*.index
```

This prevents files such as:

```text
vector_db/hr_questions.index
vector_db/hr_questions_old.index
```

from being uploaded.

This is important because GitHub has a 100 MB individual file limit, while the generated FAISS index can be much larger.

Generated vector databases should therefore remain local or be stored using an appropriate external artifact/storage solution.

---

# 📦 Requirements

The Python dependencies are stored in:

```text
backend/requirements.txt
```

They can be installed using:

```bash
pip install -r requirements.txt
```

The frontend dependencies are defined in:

```text
frontend/package.json
```

Install them using:

```bash
npm install
```

---

# 🧪 Example Interview

Example configuration:

```text
Role:
DevOps Engineer

Experience:
1 year

Difficulty:
Medium
```

The RAG pipeline retrieves relevant DevOps interview questions.

The candidate answers each question.

Example:

```text
Question:
What is Docker?
```

Candidate:

```text
Docker is a containerization platform that allows applications
and their dependencies to be packaged into containers.
```

The LLM evaluator analyzes the answer and returns:

```json
{
    "score": 8,
    "feedback": "The answer correctly identifies Docker as a containerization platform..."
}
```

The interview continues until all questions are completed.

---

# 🧩 Error Handling

The application includes handling for several common problems.

## Missing Interview Session

If an invalid session ID is submitted:

```text
Interview session not found
```

is returned.

## Empty Answer

The frontend prevents submitting an empty answer.

## No-Answer Response

Responses such as:

```text
none
I don't know
no idea
not sure
```

receive:

```text
0/10
```

## Invalid LLM JSON

If the LLM does not return valid JSON, the evaluator attempts to extract JSON from the response.

If evaluation still fails, the system safely returns:

```text
Score: 0
```

instead of crashing the application.

---

# 🔄 Complete System Flow

The complete application works as follows:

```text
                     CANDIDATE
                         │
                         ▼
                ┌─────────────────┐
                │  React Frontend │
                └────────┬────────┘
                         │
                         │ Start Interview
                         ▼
                ┌─────────────────┐
                │  FastAPI        │
                │  /start_interview
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │ Interviewer     │
                │ Agent           │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │ RAG Pipeline    │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │ Sentence        │
                │ Transformer     │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │ FAISS           │
                │ Vector Search   │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │ Relevant        │
                │ Questions       │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │ React displays  │
                │ question        │
                └────────┬────────┘
                         │
                         ▼
                   Candidate Answer
                         │
                         ▼
                ┌─────────────────┐
                │ FastAPI         │
                │ /submit_answer  │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │ LLM Evaluator   │
                │ Ollama + Gemma  │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │ Score + Feedback│
                └────────┬────────┘
                         │
                         ▼
                Next Question
                         │
                         ▼
                      Repeat
                         │
                         ▼
                ┌─────────────────┐
                │ Final Results   │
                │ + Report        │
                └─────────────────┘
```

---

# 🎯 Current Project Status

The project currently supports:

* [x] React frontend
* [x] FastAPI backend
* [x] Interview setup
* [x] Role selection
* [x] Experience selection
* [x] Difficulty selection
* [x] RAG-based question retrieval
* [x] FAISS semantic search
* [x] Sentence Transformer embeddings
* [x] Role-aware question retrieval
* [x] Experience-aware question selection
* [x] Difficulty-aware question selection
* [x] Randomized interview questions
* [x] Interview sessions
* [x] Candidate answer submission
* [x] Strict LLM evaluation
* [x] No-answer detection
* [x] 0–10 scoring
* [x] Technical feedback
* [x] Final interview score
* [x] Question-wise results
* [x] Interview report support
* [x] GitHub repository setup
* [x] Large FAISS files excluded from Git

---

# 🚧 Future Improvements

The project can be expanded with the following features.

## 👤 User Authentication

Add:

* Login
* Registration
* User profiles
* Authentication
* Candidate history

---

## 💾 Database

Currently interview sessions are maintained in memory.

A production version can use:

```text
PostgreSQL
MySQL
MongoDB
```

This would allow interview history to persist after the backend restarts.

---

## 📊 Candidate Dashboard

A complete dashboard can display:

```text
Overall Performance
Interview History
Average Score
Technical Skills
Weak Areas
Strong Areas
Progress Over Time
```

---

## 📈 Advanced Analytics

Possible analytics:

```text
Role-wise performance
Difficulty-wise performance
Category-wise performance
Question-wise performance
Average score over time
```

---

## 🤖 Adaptive Interviews

Future versions can dynamically change question difficulty based on the candidate's previous answer.

For example:

```text
Strong answer
     ↓
Increase difficulty

Weak answer
     ↓
Ask foundational question
```

This would create a more realistic adaptive interview experience.

---

## 🎤 Voice Interview

Future versions can support:

```text
Speech-to-Text
Text-to-Speech
Voice-based interview
```

This would allow the AI interviewer to conduct an interview through voice.

---

## 🧠 Better LLM Models

The evaluator can eventually support larger models such as:

```text
Gemma
Llama
Qwen
Mistral
```

depending on available hardware.

---

## ☁️ Production Deployment

The application can eventually be deployed using:

```text
Frontend:
Vercel / Netlify

Backend:
Render / Railway / AWS / Azure / GCP

Database:
PostgreSQL

Vector Database:
FAISS / Qdrant / Pinecone / Weaviate
```

---

# ⚠️ Current Limitations

The current project is primarily designed as a local development and demonstration system.

Current limitations include:

1. Interview sessions are stored in memory.
2. Sessions are lost when the backend restarts.
3. FAISS indexes are stored locally.
4. Ollama requires a locally running LLM.
5. No authentication system is currently implemented.
6. No persistent candidate database is currently implemented.
7. The frontend is currently focused on the interview experience rather than a complete analytics dashboard.

These can be addressed in future versions.

---

# 🔐 Security Considerations

Before production deployment, the following should be implemented:

* Authentication
* Authorization
* Secure CORS configuration
* Environment variables
* Input validation
* Rate limiting
* Secure API configuration
* Database security
* LLM prompt protection
* Session security

The current application uses permissive CORS for local development.

For production, `allow_origins=["*"]` should be replaced with the actual frontend domain.

---

# 🧑‍💻 Development

This project is being developed as an AI-powered interview platform using modern AI and web technologies.

The main focus areas are:

```text
RAG
+
Semantic Search
+
LLM Evaluation
+
FastAPI
+
React
```

The architecture is designed so that each component can be improved independently.

---

# 📚 Main Components

| Component       | Technology            | Purpose                        |
| --------------- | --------------------- | ------------------------------ |
| Frontend        | React                 | User interface                 |
| API             | FastAPI               | Backend API                    |
| HTTP Client     | Axios                 | Frontend/backend communication |
| Embeddings      | Sentence Transformers | Convert questions into vectors |
| Vector Search   | FAISS                 | Retrieve relevant questions    |
| LLM             | Ollama + Gemma        | Evaluate candidate answers     |
| Dataset         | JSON                  | Interview questions            |
| Language        | Python / JavaScript   | Application development        |
| Version Control | Git / GitHub          | Source code management         |

---

# 🏁 Quick Start

## Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
ollama pull gemma:2b
uvicorn main:app --reload
```

## Frontend

Open another terminal:

```bash
cd frontend
npm install
npm run dev
```

Then open the frontend URL shown by Vite.

---

# 📌 Repository

GitHub:

```text
https://github.com/dharun200701/AI-Interviewer-using-RAG
```

---

# 👨‍💻 Author

**Dharun**

AI Interviewer using RAG is a project focused on combining:

```text
Artificial Intelligence
Retrieval-Augmented Generation
Semantic Search
Large Language Models
Web Development
```

to create an intelligent and personalized technical interview platform.

---

# ⭐ Future Vision

The long-term goal is to transform this project into a complete AI recruitment and interview platform.

The planned system will eventually provide:

```text
Candidate
    │
    ▼
AI Interview
    │
    ├── Technical Questions
    ├── Adaptive Difficulty
    ├── Voice Interview
    ├── AI Evaluation
    └── Detailed Feedback
            │
            ▼
      Performance Report
            │
            ▼
       Candidate Dashboard
            │
            ▼
      Recruiter Dashboard
```

The system can eventually help candidates understand their technical strengths and weaknesses while also helping recruiters evaluate candidates more efficiently.

---

# 📄 License

This project is currently intended for educational, research, and development purposes.

```
```
