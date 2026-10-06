from uuid import uuid4

from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app.models import Student, Teacher

client = TestClient(app)

def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_docs():
    response = client.get("/docs")
    assert response.status_code == 200

def test_create_student():
    student_id = f"TEST{uuid4().hex[:12]}"
    payload = {
        "id": student_id,
        "name": "Test Student",
        "department": "Engineering",
        "semester": 2,
        "attendance_pct": 80,
        "assignment_completion_pct": 75,
        "avg_assignment_score": 72,
        "avg_exam_score": 78,
        "lms_sessions_per_week": 4,
        "avg_session_minutes": 30,
        "late_submissions": 1,
        "quiz_attempts": 4,
        "forum_posts": 2,
        "days_inactive": 1,
        "previous_semester_gpa": 7.5,
        "financial_stress": 3,
        "commute_minutes": 25,
    }
    try:
        response = client.post("/api/students", json=payload)
        assert response.status_code == 201
        assert response.json()["id"] == student_id
        assert client.post("/api/students", json=payload).status_code == 409
    finally:
        with SessionLocal() as db:
            student = db.get(Student, student_id)
            if student:
                db.delete(student)
                db.commit()

def test_create_teacher():
    teacher_id = f"TEST{uuid4().hex[:12]}"
    payload = {
        "id": teacher_id,
        "name": "Test Faculty",
        "email": f"{teacher_id.lower()}@example.edu",
        "department": "Engineering",
    }
    try:
        response = client.post("/api/teachers", json=payload)
        assert response.status_code == 201
        assert response.json()["email"] == payload["email"]
        assert client.post("/api/teachers", json=payload).status_code == 409
    finally:
        with SessionLocal() as db:
            teacher = db.get(Teacher, teacher_id)
            if teacher:
                db.delete(teacher)
                db.commit()
