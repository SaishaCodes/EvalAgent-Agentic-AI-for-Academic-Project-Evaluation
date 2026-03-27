EvalAgent: Agentic AI for Academic Project Evaluation
Overview

EvalAgent is an autonomous agentic AI system designed to assist professors in managing and evaluating student projects across the entire academic lifecycle. It reduces manual workload while ensuring consistency, fairness, and high-quality feedback through structured, rubric-driven evaluation.

The system supports proposal evaluation, milestone feedback, and final grading using a unified AI-driven pipeline powered by large language models.

High-Level Architecture
+----------------------+          +--------------------------+
|  Frontend (React)    |  <---->  |  Backend (FastAPI)       |
|  - Upload ZIP        |          |  - Evaluation pipelines  |
|  - View results      |          |  - LLM wrapper           |
+----------------------+          |  - Rubric engine         |
                                  +--------------------------+
                                            |
                                            v
                                  +--------------------------+
                                  |  LLM Engine              |
                                  |  - llama-cpp             |
                                  |  - HuggingFace API       |
                                  +--------------------------+
                                            |
                                            v
                                  +--------------------------+
                                  |  Database                |
                                  |  (SQLite/PostgreSQL)     |
                                  +--------------------------+
Features
Proposal Evaluation
Validates alignment with course objectives
Assesses feasibility and originality
Provides structured improvement suggestions
Milestone Feedback
Evaluates incremental progress
Generates iterative, context-aware feedback
Supports continuous student improvement
Final Grading
Uses a YAML-defined rubric
Produces dimension-wise scoring
Generates transparent evaluation reports
Tech Stack
Frontend: React, Axios, React Dropzone
Backend: FastAPI, SQLAlchemy, Pydantic
LLM Integration: llama-cpp-python, Hugging Face Inference API
Database: SQLite (default), PostgreSQL (optional)
Other: YAML (rubrics), Markdown parsing
Project Structure
PROJECT/
│── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── crud.py
│   │   ├── llm_provider.py
│   │   ├── rubric_engine.py
│   │   ├── utils.py
│   │   └── rubric.yaml
│   └── requirements.txt
│
│── agentic-ai-frontend/
│   ├── src/
│   ├── public/
│   └── package.json
│
│── .gitignore
│── README.md
Environment Setup
Prerequisites
Python >= 3.10
Node.js >= 18
Git
unzip
Backend Setup
python -m venv .venv-back
.venv-back\Scripts\activate     # Windows
# or
source .venv-back/bin/activate  # Linux/Mac

pip install -U pip
pip install fastapi uvicorn[standard] pydantic[dotenv] python-multipart \
            llama-cpp-python transformers sentencepiece \
            huggingface_hub pyyaml sqlalchemy
Frontend Setup
cd agentic-ai-frontend
npm install
npm install axios react-dropzone react-markdown remark-gfm
LLM Configuration
Option 1: Local Model
Download GGUF model (e.g. Llama-2-7B-Chat)
Place it in:
backend/models/

Set environment variable:

set LLM_BACKEND=local
Option 2: Hugging Face API
set LLM_BACKEND=hf
set HF_TOKEN=your_token_here
Running the System
Start Backend
cd backend
.venv-back\Scripts\activate
uvicorn app.main:app --reload --port 8000
Start Frontend
cd agentic-ai-frontend
npm start

Open:

http://localhost:3000
API Endpoint
Evaluate Project
POST /evaluate/{stage}
Parameters
stage: proposal | milestone_1 | milestone_2 | final
student_id: string
file: ZIP file
Response
{
  "id": 1,
  "student_id": "s123",
  "stage": "final",
  "score": 85.5,
  "detailed_report": {},
  "message": "Evaluation completed successfully."
}
Rubric Engine
Defined in rubric.yaml
Supports weighted scoring
Parses structured LLM output (markdown tables)
Produces normalized score (0–100)
Example Workflow
Upload project ZIP
Backend extracts files
Prompt is constructed based on stage
LLM generates structured evaluation
Rubric engine computes score
Result stored in database
JSON response returned
Future Improvements
Authentication system
Batch evaluation
PDF parsing
Multi-agent workflows
Analytics dashboard
GPU acceleration
Multi-course support
License

This project is intended for academic and research purposes. Modify and extend as needed.
