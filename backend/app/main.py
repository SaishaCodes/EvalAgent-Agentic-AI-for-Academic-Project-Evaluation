# backend/app/main.py
import os, json, shutil
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from . import models, crud, schemas, llm_provider, rubric_engine, utils

# ---------- DB ----------
SQLALCHEMY_DATABASE_URL = "sqlite:///./evaluations.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
models.Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------- FastAPI ----------
app = FastAPI(
    title="Agentic AI Project Evaluator",
    version="0.1.0"
)

# allow the React dev server (localhost:3000) to talk to the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Global objects ----------
llm = llm_provider.LLMProvider()
rubric = rubric_engine.RubricEngine()

# ---------- Helper: read syllabus & course metadata ----------
COURSE_METADATA = {
    "course_name": "Advanced Software Engineering",
    "learning_outcomes": [
        "Design scalable software systems",
        "Apply empirical evaluation methods",
        "Communicate technical results effectively"
    ],
    "description": """Students must propose a software project that solves a real-world problem,
    implements a prototype, and writes a short research‑style report."""
}
# You could also load this from a YAML/JSON file.

# ---------- Endpoints ----------
@app.post("/evaluate/{stage}", response_model=schemas.EvaluationResponse)
async def evaluate_project(
    stage: str,                       # "proposal", "milestone_1", "final"
    student_id: str,                  # e.g. "s12345"
    file: UploadFile = File(...),    # zip of the whole project folder
    db: Session = Depends(get_db)
):
    # 1️⃣ sanity checks
    if stage not in {"proposal", "milestone_1", "milestone_2", "final"}:
        raise HTTPException(status_code=400, detail="Invalid stage")

    # 2️⃣ read the uploaded zip into memory
    zip_bytes = await file.read()

    # 3️⃣ extract to a temporary directory
    temp_dir, project_root = utils.unzip_to_temp(zip_bytes)

    try:
        # --------------------------------------------------------------
        #   A. Build the system prompt (static, same for all stages)
        # --------------------------------------------------------------
        system_prompt = f"""You are an academic assistant for the course
        \"{COURSE_METADATA['course_name']}\".
        The learning outcomes are:
        {"; ".join(COURSE_METADATA['learning_outcomes'])}
        Follow the rubric strictly and output **only** a markdown table as described.
        """

        # --------------------------------------------------------------
        #   B. Build the user prompt based on the stage
        # --------------------------------------------------------------
        if stage == "proposal":
            # Look for a file called proposal.txt or README.md
            proposal_text = utils.read_file(project_root, "proposal.txt") or \
                            utils.read_file(project_root, "README.md")
            if not proposal_text:
                raise HTTPException(400, "No proposal.txt / README.md found in the zip.")
            user_prompt = f"""Student proposal:\n```\n{proposal_text[:4000]}\n```"""
            # The LLM will be asked to grade three dimensions 0‑5.
            system_prompt += """\nAssess the proposal on:
            1. Alignment with learning outcomes
            2. Feasibility (resources, time, technical risk)
            3. Novelty / originality
            Return a markdown table with columns: Dimension | Score (0‑5) | Suggested Improvements."""
        elif stage.startswith("milestone"):
            # Find the folder named exactly as the stage (e.g., milestone_1/)
            milestone_folder = os.path.join(project_root, stage)
            if not os.path.isdir(milestone_folder):
                raise HTTPException(400, f"Folder {stage}/ not found.")
            # Concatenate all .py, .ipynb, .md, .txt files (max 4k chars)
            collected = ""
            for root, _, files in os.walk(milestone_folder):
                for f in files:
                    if f.endswith(('.py', '.ipynb', '.md', '.txt')):
                        txt = utils.read_file(root, f)
                        collected += f"\n--- {f} ---\n{txt[:2000]}\n"
                        if len(collected) > 3500:
                            break
            user_prompt = f"""Milestone {stage} submission (selected files shown):
            {collected}
            """
            system_prompt += """\nAssess progress against the following checklist:
            - Does the submission meet the stated milestone goals?
            - Code quality / readability
            - Preliminary results / evidence of working prototype
            Return a markdown table with columns: Dimension | Score (0‑10) | Comments."""
        else:   # final
            # Read the main report (report.pdf → we cannot read PDF without extra deps,
            # so we ask the student to also include a markdown version)
            report_md = utils.read_file(project_root, "report.md")
            if not report_md:
                # fallback: read README
                report_md = utils.read_file(project_root, "README.md")
            # Grab a short excerpt of source code (first 200 lines of each .py)
            src_excerpt = ""
            src_root = os.path.join(project_root, "src")
            if os.path.isdir(src_root):
                for py_file in pathlib.Path(src_root).rglob("*.py"):
                    src_excerpt += f"\n--- {py_file.relative_to(project_root)} ---\n"
                    src_excerpt += "\n".join(open(py_file, "r", encoding="utf8",
                                                errors="ignore").read().splitlines()[:200])
            user_prompt = f"""Final project report (markdown):
            ```markdown
            {report_md[:4000]}
            ```

            Source code excerpt (if any):
            ```python
            {src_excerpt[:4000]}
            ```
            """
            system_prompt += """\nGrade the final project according to the rubric in rubric.yaml.
            Return a markdown table where each row contains:
            Dimension | Score (0‑max) | Comments
            After the table, write a short 2‑sentence overall summary."""

        # --------------------------------------------------------------
        #   C. Call the LLM
        # --------------------------------------------------------------
        llm_output = llm.chat(system=system_prompt, user=user_prompt,
                              temperature=0.2, max_tokens=1024)

        # --------------------------------------------------------------
        #   D. Post‑process (only final uses rubric engine)
        # --------------------------------------------------------------
        numeric_score = None
        detailed_report = None
        if stage == "final":
            numeric_score, detailed_report = rubric.evaluate(llm_output)

        # --------------------------------------------------------------
        #   E. Persist the evaluation
        # --------------------------------------------------------------
        db_obj = crud.create_evaluation(
            db,
            student_id=student_id,
            stage=stage,
            raw_llm_output=llm_output,
            score=numeric_score,
            detailed_report=detailed_report,
        )

        # --------------------------------------------------------------
        #   F. Build the response
        # --------------------------------------------------------------
        response = schemas.EvaluationResponse(
            id=db_obj.id,
            student_id=student_id,
            stage=stage,
            score=numeric_score,
            detailed_report=detailed_report,
            message="Evaluation completed successfully."
        )
        return response

    finally:
        # Clean up the temporary directory
        shutil.rmtree(temp_dir, ignore_errors=True)