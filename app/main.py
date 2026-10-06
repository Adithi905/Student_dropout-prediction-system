from pathlib import Path
import json
import pandas as pd
from fastapi import FastAPI, Depends, HTTPException, Query, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.config import settings
from app.database import Base, engine, get_db
from app.models import Student, Teacher, Prediction, Intervention
from app.schemas import (
    StudentCreate,
    StudentOut,
    TeacherCreate,
    TeacherOut,
    PredictionOut,
    InterventionOut,
)
from app.ml.predictor import explain, reset_model
from app.ml.train import train
from app.services.intervention import build_intervention

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="Explainable student engagement analytics and dropout-risk intervention platform."
)

STATIC = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=STATIC), name="static")

@app.get("/", response_class=HTMLResponse)
def home():
    return (STATIC / "index.html").read_text()

@app.get("/faculty", response_class=HTMLResponse)
def faculty():
    return (STATIC / "faculty.html").read_text()

@app.get("/student", response_class=HTMLResponse)
def student():
    return (STATIC / "student.html").read_text()

@app.get("/api/health")
def health():
    return {"status": "ok", "service": settings.app_name}

@app.get("/api/dashboard/summary")
def dashboard_summary(db: Session = Depends(get_db)):
    students = db.query(Student).all()
    if not students:
        return {"total_students": 0, "high_risk": 0, "critical": 0, "average_engagement": 0}

    bands = {"Low": 0, "Medium": 0, "High": 0, "Critical": 0}
    engagements = []
    for s in students:
        p = explain(s)
        bands[p["risk_band"]] += 1
        engagements.append(p["engagement_score"])

    return {
        "total_students": len(students),
        "high_risk": bands["High"] + bands["Critical"],
        "critical": bands["Critical"],
        "medium_risk": bands["Medium"],
        "low_risk": bands["Low"],
        "average_engagement": round(sum(engagements) / len(engagements), 1),
        "risk_distribution": bands,
    }

@app.get("/api/students", response_model=list[StudentOut])
def students(
    risk: str | None = Query(default=None),
    department: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    records = db.query(Student).all()
    if department:
        records = [s for s in records if s.department.lower() == department.lower()]
    if risk:
        records = [s for s in records if explain(s)["risk_band"].lower() == risk.lower()]
    return records

@app.post("/api/students", response_model=StudentOut, status_code=201)
def create_student(payload: StudentCreate, db: Session = Depends(get_db)):
    if db.get(Student, payload.id):
        raise HTTPException(409, "A student with this ID already exists")
    student = Student(**payload.model_dump())
    db.add(student)
    db.commit()
    db.refresh(student)
    return student

@app.get("/api/teachers", response_model=list[TeacherOut])
def teachers(db: Session = Depends(get_db)):
    return db.query(Teacher).order_by(Teacher.name).all()

@app.post("/api/teachers", response_model=TeacherOut, status_code=201)
def create_teacher(payload: TeacherCreate, db: Session = Depends(get_db)):
    if db.get(Teacher, payload.id):
        raise HTTPException(409, "A teacher with this ID already exists")
    existing_email = db.query(Teacher).filter(
        func.lower(Teacher.email) == payload.email.lower()
    ).first()
    if existing_email:
        raise HTTPException(409, "A teacher with this email already exists")
    teacher = Teacher(**payload.model_dump())
    db.add(teacher)
    db.commit()
    db.refresh(teacher)
    return teacher

@app.get("/api/students/{student_id}", response_model=StudentOut)
def student_detail(student_id: str, db: Session = Depends(get_db)):
    student = db.get(Student, student_id)
    if not student:
        raise HTTPException(404, "Student not found")
    return student

@app.get("/api/students/{student_id}/prediction", response_model=PredictionOut)
def student_prediction(student_id: str, db: Session = Depends(get_db)):
    student = db.get(Student, student_id)
    if not student:
        raise HTTPException(404, "Student not found")

    result = explain(student)
    prediction = Prediction(
        student_id=student.id,
        risk_probability=result["risk_probability"],
        risk_band=result["risk_band"],
        engagement_score=result["engagement_score"],
        top_factors=json.dumps(result["top_factors"]),
    )
    db.add(prediction)
    db.commit()
    return {"student_id": student.id, **result}

@app.post("/api/students/{student_id}/intervention", response_model=InterventionOut)
def intervention(student_id: str, db: Session = Depends(get_db)):
    student = db.get(Student, student_id)
    if not student:
        raise HTTPException(404, "Student not found")

    prediction = explain(student)
    plan = build_intervention(student, prediction)

    for action in plan["actions"]:
        db.add(Intervention(
            student_id=student.id,
            priority=action["priority"],
            action=action["action"],
            reason=action["reason"],
        ))
    db.commit()
    return plan

@app.get("/api/interventions")
def interventions(db: Session = Depends(get_db)):
    rows = db.query(Intervention).order_by(Intervention.created_at.desc()).limit(100).all()
    return [{
        "student_id": x.student_id,
        "priority": x.priority,
        "action": x.action,
        "reason": x.reason,
        "status": x.status,
        "created_at": x.created_at.isoformat(),
    } for x in rows]

@app.get("/api/model/metrics")
def model_metrics():
    path = Path(settings.model_path).with_name("model_metadata.json")
    if not path.exists():
        return {"status": "not_trained"}
    return json.loads(path.read_text())

@app.post("/api/model/train")
def retrain():
    metrics = train()
    reset_model()
    return {"status": "trained", "metrics": metrics}

@app.post("/api/batch/predict")
async def batch_predict(file: UploadFile = File(...)):
    raw = await file.read()
    tmp = Path("data") / "_uploaded_batch.csv"
    tmp.write_bytes(raw)
    df = pd.read_csv(tmp)

    required = [
        "student_id", "name", "department", "semester",
        "attendance_pct", "assignment_completion_pct",
        "avg_assignment_score", "avg_exam_score",
        "lms_sessions_per_week", "avg_session_minutes",
        "late_submissions", "quiz_attempts", "forum_posts",
        "days_inactive", "previous_semester_gpa",
        "financial_stress", "commute_minutes"
    ]
    missing = [x for x in required if x not in df.columns]
    if missing:
        raise HTTPException(400, f"Missing columns: {missing}")

    results = []
    for _, row in df.iterrows():
        class Obj:
            pass
        s = Obj()
        for col in required:
            setattr(s, col if col != "student_id" else "id", row[col])
        result = explain(s)
        results.append({"student_id": str(row["student_id"]), **result})
    return {"count": len(results), "results": results}
