# backend/app/models.py
from sqlalchemy import Column, Integer, String, Float, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Evaluation(Base):
    __tablename__ = "evaluations"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String, index=True)          # e.g., "s12345"
    stage = Column(String)                           # "proposal", "milestone_1", "final"
    timestamp = Column(DateTime, default=datetime.utcnow)
    raw_llm_output = Column(Text)                    # full LLM answer
    score = Column(Float, nullable=True)             # numeric grade (final only)
    detailed_report = Column(Text)                   # JSON string of rubric details