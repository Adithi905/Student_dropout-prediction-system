def test_risk_bands():
    from app.ml.predictor import risk_band
    assert risk_band(0.10) == "Low"
    assert risk_band(0.40) == "Medium"
    assert risk_band(0.70) == "High"
    assert risk_band(0.90) == "Critical"
