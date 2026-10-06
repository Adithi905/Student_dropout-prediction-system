from pathlib import Path
import json
import joblib
from app.config import settings
from app.ml.features import DISPLAY_NAMES, FEATURES, to_frame, engagement_score

_model = None

def get_model():
    global _model
    if _model is None:
        path = Path(settings.model_path)
        if not path.exists():
            raise FileNotFoundError("Model not found. Run: python app/ml/train.py")
        _model = joblib.load(path)
    return _model

def reset_model():
    global _model
    _model = None

def risk_band(prob):
    if prob >= 0.80:
        return "Critical"
    if prob >= 0.60:
        return "High"
    if prob >= 0.35:
        return "Medium"
    return "Low"

def explain(student):
    model = get_model()
    frame = to_frame(student)
    prob = float(model.predict_proba(frame)[0, 1])
    importances = model.feature_importances_
    raw = frame.iloc[0].to_dict()

    # Directional heuristic combined with model importance.
    risk_direction = {
        "attendance_pct": -raw["attendance_pct"],
        "assignment_completion_pct": -raw["assignment_completion_pct"],
        "avg_assignment_score": -raw["avg_assignment_score"],
        "avg_exam_score": -raw["avg_exam_score"],
        "lms_sessions_per_week": -raw["lms_sessions_per_week"],
        "avg_session_minutes": -raw["avg_session_minutes"],
        "late_submissions": raw["late_submissions"] * 8,
        "quiz_attempts": -raw["quiz_attempts"] * 4,
        "forum_posts": -raw["forum_posts"] * 4,
        "days_inactive": raw["days_inactive"] * 10,
        "previous_semester_gpa": -raw["previous_semester_gpa"] * 12,
        "financial_stress": raw["financial_stress"] * 12,
        "commute_minutes": raw["commute_minutes"] * 0.15,
    }

    contributions = []
    for feature, importance in zip(FEATURES, importances):
        contributions.append({
            "feature": feature,
            "score": round(float(importance * abs(risk_direction[feature])), 4),
            "impact": "Risk increasing" if risk_direction[feature] > 0 else "Protective",
        })

    contributions.sort(key=lambda x: x["score"], reverse=True)
    return {
        "risk_probability": round(prob, 4),
        "risk_band": risk_band(prob),
        "engagement_score": engagement_score(student),
        "top_factors": [
            {
                "feature": DISPLAY_NAMES[x["feature"]],
                "impact": x["impact"],
                "score": x["score"],
            }
            for x in contributions[:5]
        ],
    }
