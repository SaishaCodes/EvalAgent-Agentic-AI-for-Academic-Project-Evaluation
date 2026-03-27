# backend/app/schemas.py
from pydantic import BaseModel
from typing import Optional, Dict, Any

class EvaluationResponse(BaseModel):
    id: int
    student_id: str
    stage: str
    score: Optional[float] = None
    detailed_report: Optional[Dict[str, Any]] = None
    message: str