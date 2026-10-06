from pydantic import BaseModel, Field
from typing import List

class StudentCreate(BaseModel):
    id: str = Field(min_length=1, max_length=32, pattern=r"^[A-Za-z0-9_-]+$")
    name: str = Field(min_length=1, max_length=120)
    department: str = Field(min_length=1, max_length=80)
    semester: int = Field(ge=1, le=20)
    attendance_pct: float = Field(ge=0, le=100)
    assignment_completion_pct: float = Field(ge=0, le=100)
    avg_assignment_score: float = Field(ge=0, le=100)
    avg_exam_score: float = Field(ge=0, le=100)
    lms_sessions_per_week: float = Field(ge=0, le=7)
    avg_session_minutes: float = Field(ge=0, le=1440)
    late_submissions: int = Field(ge=0)
    quiz_attempts: int = Field(ge=0)
    forum_posts: int = Field(ge=0)
    days_inactive: int = Field(ge=0)
    previous_semester_gpa: float = Field(ge=0, le=10)
    financial_stress: float = Field(ge=0, le=10)
    commute_minutes: float = Field(ge=0, le=1440)

class StudentOut(BaseModel):
    id: str
    name: str
    department: str
    semester: int
    attendance_pct: float
    assignment_completion_pct: float
    avg_assignment_score: float
    avg_exam_score: float
    lms_sessions_per_week: float
    avg_session_minutes: float
    late_submissions: int
    quiz_attempts: int
    forum_posts: int
    days_inactive: int
    previous_semester_gpa: float
    financial_stress: float
    commute_minutes: float

    class Config:
        from_attributes = True

class TeacherCreate(BaseModel):
    id: str = Field(min_length=1, max_length=32, pattern=r"^[A-Za-z0-9_-]+$")
    name: str = Field(min_length=1, max_length=120)
    email: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$", max_length=254)
    department: str = Field(min_length=1, max_length=80)

class TeacherOut(BaseModel):
    id: str
    name: str
    email: str
    department: str

    class Config:
        from_attributes = True

class Factor(BaseModel):
    feature: str
    impact: str
    score: float

class PredictionOut(BaseModel):
    student_id: str
    risk_probability: float
    risk_band: str
    engagement_score: float
    top_factors: List[Factor]

class InterventionOut(BaseModel):
    student_id: str
    priority: str
    actions: List[dict]
