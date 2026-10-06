from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "sample_students.csv"
OUT.parent.mkdir(exist_ok=True)

rng = np.random.default_rng(42)
n = 900

departments = np.array(["CSE", "ISE", "ECE", "ME", "AIML", "MBA"])
rows = []

for i in range(n):
    attendance = np.clip(rng.normal(78, 14), 35, 100)
    assignment = np.clip(rng.normal(76, 17), 20, 100)
    assignment_score = np.clip(rng.normal(70, 16), 25, 100)
    exam_score = np.clip(rng.normal(67, 17), 20, 100)
    lms = np.clip(rng.normal(4.5, 2.0), 0, 12)
    minutes = np.clip(rng.normal(42, 16), 5, 120)
    late = int(np.clip(rng.poisson(1.5), 0, 10))
    quizzes = int(np.clip(rng.poisson(5), 0, 20))
    forum = int(np.clip(rng.poisson(2), 0, 12))
    inactive = int(np.clip(rng.poisson(2.5), 0, 20))
    gpa = np.clip(rng.normal(7.0, 1.1), 4.0, 10.0)
    stress = np.clip(rng.normal(4.0, 2.4), 0, 10)
    commute = np.clip(rng.normal(48, 25), 5, 160)

    risk_signal = (
        -0.045 * (attendance - 70)
        -0.035 * (assignment - 70)
        -0.025 * (assignment_score - 60)
        -0.030 * (exam_score - 60)
        -0.18 * (lms - 3)
        +0.18 * late
        -0.10 * quizzes
        -0.06 * forum
        +0.25 * inactive
        -0.65 * (gpa - 6)
        +0.22 * (stress - 5)
        +0.008 * (commute - 60)
    )
    probability = 1 / (1 + np.exp(-(risk_signal - 1.2)))
    dropout = int(rng.random() < probability)

    rows.append([
        f"STU{1001+i}",
        f"Student {i+1:03d}",
        rng.choice(departments),
        int(rng.integers(1, 9)),
        round(attendance, 1),
        round(assignment, 1),
        round(assignment_score, 1),
        round(exam_score, 1),
        round(lms, 1),
        round(minutes, 1),
        late, quizzes, forum, inactive,
        round(gpa, 2), round(stress, 1), round(commute, 1),
        dropout
    ])

columns = [
    "student_id","name","department","semester","attendance_pct",
    "assignment_completion_pct","avg_assignment_score","avg_exam_score",
    "lms_sessions_per_week","avg_session_minutes","late_submissions",
    "quiz_attempts","forum_posts","days_inactive","previous_semester_gpa",
    "financial_stress","commute_minutes","dropout"
]
pd.DataFrame(rows, columns=columns).to_csv(OUT, index=False)
print(f"Generated {n} rows at {OUT}")
