from pathlib import Path
import json
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from app.ml.features import FEATURES

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "sample_students.csv"
MODEL = ROOT / "models" / "dropout_model.joblib"
META = ROOT / "models" / "model_metadata.json"

def train():
    df = pd.read_csv(DATA)
    X = df[FEATURES]
    y = df["dropout"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.22, random_state=42, stratify=y
    )

    model = RandomForestClassifier(
        n_estimators=350,
        max_depth=9,
        min_samples_leaf=3,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)

    pred = model.predict(X_test)
    prob = model.predict_proba(X_test)[:, 1]
    cv = cross_val_score(
        model, X, y,
        cv=StratifiedKFold(n_splits=5, shuffle=True, random_state=42),
        scoring="roc_auc"
    )

    metrics = {
        "accuracy": round(float(accuracy_score(y_test, pred)), 4),
        "precision": round(float(precision_score(y_test, pred)), 4),
        "recall": round(float(recall_score(y_test, pred)), 4),
        "f1": round(float(f1_score(y_test, pred)), 4),
        "roc_auc": round(float(roc_auc_score(y_test, prob)), 4),
        "cv_roc_auc_mean": round(float(cv.mean()), 4),
        "training_rows": len(df),
        "features": FEATURES,
    }

    MODEL.parent.mkdir(exist_ok=True)
    joblib.dump(model, MODEL)
    META.write_text(json.dumps(metrics, indent=2))
    print(json.dumps(metrics, indent=2))
    return metrics

if __name__ == "__main__":
    train()
