FEATURES = [
    "attendance_pct",
    "assignment_completion_pct",
    "avg_assignment_score",
    "avg_exam_score",
    "lms_sessions_per_week",
    "avg_session_minutes",
    "late_submissions",
    "quiz_attempts",
    "forum_posts",
    "days_inactive",
    "previous_semester_gpa",
    "financial_stress",
    "commute_minutes",
]

DISPLAY_NAMES = {
    "attendance_pct": "Attendance",
    "assignment_completion_pct": "Assignment completion",
    "avg_assignment_score": "Assignment score",
    "avg_exam_score": "Exam score",
    "lms_sessions_per_week": "LMS sessions",
    "avg_session_minutes": "Session duration",
    "late_submissions": "Late submissions",
    "quiz_attempts": "Quiz attempts",
    "forum_posts": "Forum participation",
    "days_inactive": "Inactive days",
    "previous_semester_gpa": "Previous GPA",
    "financial_stress": "Financial stress indicator",
    "commute_minutes": "Commute duration",
}

def to_frame(student):
    import pandas as pd
    row = {f: getattr(student, f) for f in FEATURES}
    return pd.DataFrame([row], columns=FEATURES)

def engagement_score(student):
    attendance = min(max(student.attendance_pct, 0), 100)
    assignments = min(max(student.assignment_completion_pct, 0), 100)
    scores = min(max((student.avg_assignment_score + student.avg_exam_score) / 2, 0), 100)
    lms = min(student.lms_sessions_per_week / 7 * 100, 100)
    inactivity = max(0, 100 - student.days_inactive * 5)
    interaction = min((student.quiz_attempts * 8 + student.forum_posts * 12), 100)
    value = (
        attendance * 0.25 +
        assignments * 0.20 +
        scores * 0.20 +
        lms * 0.15 +
        inactivity * 0.10 +
        interaction * 0.10
    )
    return round(value, 1)
