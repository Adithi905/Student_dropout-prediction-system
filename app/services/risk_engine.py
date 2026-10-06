def classify_priority(risk_band: str) -> str:
    return {
        "Critical": "Immediate",
        "High": "High",
        "Medium": "Moderate",
        "Low": "Routine",
    }.get(risk_band, "Routine")
