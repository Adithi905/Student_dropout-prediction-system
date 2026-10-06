from app.services.risk_engine import classify_priority

def build_intervention(student, prediction):
    actions = []
    band = prediction["risk_band"]

    if student.attendance_pct < 75:
        actions.append({
            "priority": "High",
            "action": "Attendance recovery plan",
            "reason": f"Attendance is {student.attendance_pct:.1f}%. Set a weekly attendance target and mentor check-in."
        })

    if student.assignment_completion_pct < 70 or student.late_submissions >= 3:
        actions.append({
            "priority": "High",
            "action": "Assignment completion sprint",
            "reason": "Multiple incomplete or late submissions indicate academic execution risk."
        })

    if student.avg_exam_score < 55:
        actions.append({
            "priority": "High",
            "action": "Targeted academic support",
            "reason": "Assessment performance is below the intervention threshold."
        })

    if student.days_inactive >= 5 or student.lms_sessions_per_week < 2:
        actions.append({
            "priority": "High",
            "action": "Re-engagement sequence",
            "reason": "Low recent learning-platform activity suggests disengagement."
        })

    if student.previous_semester_gpa < 6.0:
        actions.append({
            "priority": "Moderate",
            "action": "Academic mentoring",
            "reason": "Previous GPA indicates the student may benefit from structured mentoring."
        })

    if student.financial_stress >= 7:
        actions.append({
            "priority": "Moderate",
            "action": "Student-support referral",
            "reason": "Financial stress indicator is elevated; connect the student with appropriate institutional support."
        })

    if student.commute_minutes >= 90:
        actions.append({
            "priority": "Moderate",
            "action": "Flexible learning support",
            "reason": "Long commute may make consistent attendance and study time harder."
        })

    if not actions:
        actions.append({
            "priority": "Routine",
            "action": "Maintain current engagement",
            "reason": "No major intervention trigger was detected."
        })

    if band in {"Critical", "High"}:
        actions.insert(0, {
            "priority": "Immediate",
            "action": "Mentor outreach within 48 hours",
            "reason": f"Overall predicted dropout risk is {prediction['risk_probability']*100:.1f}%."
        })

    return {
        "student_id": student.id,
        "priority": classify_priority(band),
        "actions": actions,
    }
