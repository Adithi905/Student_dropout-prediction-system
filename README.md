# Intelligent Student Engagement & Dropout Prediction System

A resume-grade end-to-end academic analytics platform that predicts student dropout risk from attendance, academic performance and learning-interaction signals, explains the prediction, and generates personalized intervention recommendations.

## What this project demonstrates

- Machine Learning classification pipeline using scikit-learn
- Feature engineering from attendance, assignments, assessments and LMS interaction data
- Random Forest model with class balancing
- Cross-validation and evaluation metrics
- Explainable predictions using feature contribution analysis
- Risk segmentation: Low / Medium / High / Critical
- Personalized intervention recommendation engine
- Faculty analytics dashboard
- Student self-view dashboard
- REST API using FastAPI
- SQLite persistence using SQLAlchemy
- CSV batch prediction workflow
- Synthetic but realistic training dataset
- Model persistence with joblib
- Health/API documentation through FastAPI
- Responsive dashboard without a frontend build dependency

## Architecture

```text
                    ┌──────────────────────┐
                    │   Student Activity   │
                    │ attendance / marks   │
                    │ LMS / assignments    │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ Feature Engineering  │
                    │ ratios / trends /    │
                    │ engagement score      │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ Random Forest Model  │
                    │ + class balancing    │
                    └──────────┬───────────┘
                               │
                 ┌─────────────┼─────────────┐
                 ▼             ▼             ▼
          Risk Probability  Explanation   Risk Band
                 │             │             │
                 └─────────────┼─────────────┘
                               ▼
                    ┌──────────────────────┐
                    │ Intervention Engine  │
                    │ study plan / mentor  │
                    │ resources / outreach  │
                    └──────────┬───────────┘
                               ▼
              ┌─────────────────────────────────┐
              │ Faculty Dashboard + Student UI │
              └─────────────────────────────────┘
```

## Project structure

```text
app/
  main.py
  config.py
  database.py
  models.py
  schemas.py
  ml/
    features.py
    predictor.py
    train.py
  services/
    risk_engine.py
    intervention.py
  static/
    index.html
    faculty.html
    student.html
    app.js
    styles.css

data/
  sample_students.csv

models/
  dropout_model.joblib
  model_metadata.json

scripts/
  seed_database.py
  generate_dataset.py

tests/
  test_api.py
  test_risk_engine.py

requirements.txt
Dockerfile
docker-compose.yml
.env.example
```

## Run locally

### 1. Create a virtual environment

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Generate the model and sample dataset

```bash
python scripts/generate_dataset.py
python app/ml/train.py
python scripts/seed_database.py
```

### 4. Start the application

```bash
uvicorn app.main:app --reload
```

Open:

- Dashboard: http://127.0.0.1:8000
- Faculty view: http://127.0.0.1:8000/faculty
- Student view: http://127.0.0.1:8000/student
- API docs: http://127.0.0.1:8000/docs

## Docker

```bash
docker compose up --build
```

Then open http://127.0.0.1:8000

## API examples

Get dashboard summary:

```http
GET /api/dashboard/summary
```

List students by risk:

```http
GET /api/students?risk=High
```

Get a student prediction:

```http
GET /api/students/STU1001/prediction
```

Generate an intervention plan:

```http
POST /api/students/STU1001/intervention
```

Retrain model:

```http
POST /api/model/train
```

## CSV format

The batch workflow accepts:

```text
student_id,name,department,semester,attendance_pct,assignment_completion_pct,avg_assignment_score,avg_exam_score,lms_sessions_per_week,avg_session_minutes,late_submissions,quiz_attempts,forum_posts,days_inactive,previous_semester_gpa,financial_stress,commute_minutes
```

## Important project note

The included dataset is synthetic and intended for software demonstration. It must not be presented as a clinically, legally, or institutionally validated dropout predictor.

For a real college deployment, the model should be trained and validated on appropriately consented institutional data, checked for demographic bias, calibrated, monitored for drift, and used to support—not automatically punish or exclude—students.

## Resume bullets

- Developed an end-to-end student analytics platform using FastAPI, SQLAlchemy, SQLite and scikit-learn to predict dropout risk from attendance, assessment and LMS engagement signals.
- Engineered behavioral and academic features, trained a class-balanced Random Forest classifier, and exposed probability-based Low/Medium/High/Critical risk predictions through REST APIs.
- Built an explainable intervention engine that converts risk drivers into personalized study plans, mentor outreach and learning-resource recommendations, with faculty and student dashboards.
