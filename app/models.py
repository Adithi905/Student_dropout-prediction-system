from datetime import datetime
from sqlalchemy import String, Float, Integer, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

class Student(Base):
    __tablename__ = "students"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    department: Mapped[str] = mapped_column(String(80))
    semester: Mapped[int] = mapped_column(Integer)
    attendance_pct: Mapped[float] = mapped_column(Float)
    assignment_completion_pct: Mapped[float] = mapped_column(Float)
    avg_assignment_score: Mapped[float] = mapped_column(Float)
    avg_exam_score: Mapped[float] = mapped_column(Float)
    lms_sessions_per_week: Mapped[float] = mapped_column(Float)
    avg_session_minutes: Mapped[float] = mapped_column(Float)
    late_submissions: Mapped[int] = mapped_column(Integer)
    quiz_attempts: Mapped[int] = mapped_column(Integer)
    forum_posts: Mapped[int] = mapped_column(Integer)
    days_inactive: Mapped[int] = mapped_column(Integer)
    previous_semester_gpa: Mapped[float] = mapped_column(Float)
    financial_stress: Mapped[float] = mapped_column(Float)
    commute_minutes: Mapped[float] = mapped_column(Float)

class Teacher(Base):
    __tablename__ = "teachers"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(254), unique=True)
    department: Mapped[str] = mapped_column(String(80))

class Prediction(Base):
    __tablename__ = "predictions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    student_id: Mapped[str] = mapped_column(String(32), index=True)
    risk_probability: Mapped[float] = mapped_column(Float)
    risk_band: Mapped[str] = mapped_column(String(20))
    engagement_score: Mapped[float] = mapped_column(Float)
    top_factors: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class Intervention(Base):
    __tablename__ = "interventions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    student_id: Mapped[str] = mapped_column(String(32), index=True)
    priority: Mapped[str] = mapped_column(String(20))
    action: Mapped[str] = mapped_column(String(160))
    reason: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="Pending")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
