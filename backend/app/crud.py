# backend/app/crud.py
from sqlalchemy.orm import Session
from . import models

def create_evaluation(db: Session, *, student_id: str, stage: str,
                      raw_llm_output: str,
                      score: float | None = None,
                      detailed_report: dict | None = None):
    db_obj = models.Evaluation(
        student_id=student_id,
        stage=stage,
        raw_llm_output=raw_llm_output,
        score=score,
        detailed_report=None if detailed_report is None else json.dumps(detailed_report)
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj