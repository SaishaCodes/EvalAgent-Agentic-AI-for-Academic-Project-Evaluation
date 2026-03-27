# EvalAgent: Agentic AI for Academic Project Evaluation

## Overview
EvalAgent is an autonomous agentic AI system designed to assist professors in managing and evaluating student projects across the entire academic lifecycle. It reduces manual workload while ensuring consistency, fairness, and high-quality feedback through structured, rubric-driven evaluation.

The system supports proposal evaluation, milestone feedback, and final grading using a unified AI-driven pipeline powered by large language models.

---

## High-Level Architecture

```
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
```

---

## Features

### Proposal Evaluation
- Validates alignment with course objectives  
- Assesses feasibility and originality  
- Provides structured improvement suggestions  

### Milestone Feedback
- Evaluates incremental progress  
- Generates iterative, context-aware feedback  
- Supports continuous student improvement  

### Final Grading
- Uses a YAML-defined rubric  
- Produces dimension-wise scoring  
- Generates transparent evaluation reports  

---

## Tech Stack

- Frontend: React, Axios, React Dropzone  
- Backend: FastAPI, SQLAlchemy, Pydantic  
- LLM: llama-cpp-python, Hugging Face API  
- Database: SQLite / PostgreSQL  
- Other: YAML, Markdown parsing  

---

## Project Structure

```
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
```

---

## Environment Setup

### Prerequisites
- Python >= 3.10  
- Node.js >= 18  
- Git  

---

### Backend Setup

```
python -m venv .venv-back
.venv-back\Scripts\activate   # Windows

pip install -U pip
pip install fastapi uvicorn python-multipart pyyaml sqlalchemy
```

---

### Frontend Setup

```
cd agentic-ai-frontend
npm install
```

---

## Running the System

### Backend

```
cd backend
uvicorn app.main:app --reload --port 8000
```

---

### Frontend

```
cd agentic-ai-frontend
npm start
```

Open: http://localhost:3000

---

## API

POST /evaluate/{stage}

Stages:
- proposal
- milestone_1
- milestone_2
- final

---

## Workflow

1. Upload ZIP  
2. Backend extracts files  
3. LLM evaluates  
4. Rubric computes score  
5. Result stored and returned  

---

## License

This project is for academic and research use.
