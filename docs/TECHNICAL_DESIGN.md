# Technical Design

## 1. Problem

Dropout risk is rarely caused by one metric. The system therefore combines:
- attendance
- assignment completion
- assessment performance
- LMS activity
- interaction signals
- inactivity
- prior academic performance
- support-risk indicators

## 2. ML approach

A Random Forest classifier is used because it:
- handles nonlinear interactions
- is robust on mixed behavioral signals
- supports feature importance
- requires little preprocessing for bounded numeric features
- is easy to persist and serve

Class balancing is enabled because the positive dropout class can be smaller than the non-dropout class.

Evaluation includes:
- Accuracy
- Precision
- Recall
- F1
- ROC-AUC
- 5-fold stratified cross-validation

For a real deployment, probability calibration, temporal validation and cohort-based validation should be added.

## 3. Explainability

The prediction endpoint returns:
- dropout probability
- risk band
- engagement score
- top contributing signals
- whether each signal is risk-increasing or protective

This is an application-level explanation layer rather than a claim of causal inference.

## 4. Intervention engine

The intervention engine uses transparent rules on top of the ML output. Examples:
- low attendance → attendance recovery plan
- low assignment completion → completion sprint
- low exam performance → targeted academic support
- inactivity → re-engagement sequence
- elevated support-risk indicator → student-support referral

This separation keeps prediction and intervention logic independently testable.

## 5. Data lifecycle

```text
CSV / SIS / LMS
      ↓
Validation
      ↓
Feature engineering
      ↓
Model inference
      ↓
Risk + explanation
      ↓
Intervention
      ↓
Faculty/student dashboard
```

## 6. Production improvements

For a production deployment:
- PostgreSQL instead of SQLite
- authentication and role-based access
- encrypted student data
- audit logging
- model registry
- scheduled retraining
- drift detection
- probability calibration
- SHAP-based explanations
- temporal validation
- fairness evaluation
- consent and data-retention policies
- LMS/SIS integration
- notification service
