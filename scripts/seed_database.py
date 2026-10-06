from pathlib import Path
import sys
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.database import Base, engine, SessionLocal
from app.models import Student

Base.metadata.create_all(bind=engine)

csv = ROOT / "data" / "sample_students.csv"
df = pd.read_csv(csv)

db = SessionLocal()
try:
    existing = {x.id for x in db.query(Student).all()}
    for _, r in df.head(80).iterrows():
        sid = str(r.student_id)
        if sid in existing:
            continue
        db.add(Student(
            id=sid, name=r["name"], department=r["department"],
            semester=int(r["semester"]),
            attendance_pct=float(r["attendance_pct"]),
            assignment_completion_pct=float(r["assignment_completion_pct"]),
            avg_assignment_score=float(r["avg_assignment_score"]),
            avg_exam_score=float(r["avg_exam_score"]),
            lms_sessions_per_week=float(r["lms_sessions_per_week"]),
            avg_session_minutes=float(r["avg_session_minutes"]),
            late_submissions=int(r["late_submissions"]),
            quiz_attempts=int(r["quiz_attempts"]),
            forum_posts=int(r["forum_posts"]),
            days_inactive=int(r["days_inactive"]),
            previous_semester_gpa=float(r["previous_semester_gpa"]),
            financial_stress=float(r["financial_stress"]),
            commute_minutes=float(r["commute_minutes"]),
        ))
    db.commit()
    print("Seeded 80 students.")
finally:
    db.close()
