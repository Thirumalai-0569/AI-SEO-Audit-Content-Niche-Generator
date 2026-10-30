"""Train and use a simple ML classifier for a defined engagement outcome."""
from pathlib import Path
from typing import Tuple, Dict
import pandas as pd
import numpy as np
import joblib
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, roc_auc_score, brier_score_loss
from config import SAMPLE_POSTS_PATH, MODEL_PATH, FEATURE_COLUMNS_PATH, RANDOM_STATE

CATEGORICAL = ["platform", "topic", "posting_time"]
NUMERIC = ["duration_seconds", "title_keyword_score", "hashtag_relevance", "historical_engagement_rate"]

def load_training_data(path=SAMPLE_POSTS_PATH):
    df = pd.read_csv(path)
    needed = CATEGORICAL + NUMERIC + ["success"]
    missing = [c for c in needed if c not in df.columns]
    if missing:
        raise ValueError(f"Dataset is missing required columns: {missing}")
    return df[needed].copy()

def train_model(path=SAMPLE_POSTS_PATH) -> Tuple[dict, object]:
    df = load_training_data(path)
    df["success"] = pd.to_numeric(df["success"], errors="coerce")
    df = df.dropna(subset=["success"])
    X = df[CATEGORICAL + NUMERIC]
    y = df["success"].astype(int)
    if y.nunique() < 2 or y.value_counts().min() < 2:
        raise ValueError("Need at least two classes and at least two rows in each class to train/test.")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=RANDOM_STATE, stratify=y
    )
    preprocessor = ColumnTransformer([
        ("categorical", Pipeline([
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore"))
        ]), CATEGORICAL),
        ("numeric", Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler())
        ]), NUMERIC)
    ])
    model = Pipeline([
        ("preprocessor", preprocessor),
        ("classifier", LogisticRegression(max_iter=1500, class_weight="balanced"))
    ])
    model.fit(X_train, y_train)
    probs = model.predict_proba(X_test)[:,1]
    pred = (probs >= 0.5).astype(int)
    metrics = {
        "test_rows": int(len(y_test)),
        "accuracy": round(float(accuracy_score(y_test, pred)), 3),
        "precision": round(float(precision_score(y_test, pred, zero_division=0)), 3),
        "recall": round(float(recall_score(y_test, pred, zero_division=0)), 3),
        "roc_auc": round(float(roc_auc_score(y_test, probs)), 3) if y_test.nunique() == 2 else None,
        "brier_score": round(float(brier_score_loss(y_test, probs)), 3),
        "positive_rate": round(float(y.mean()), 3),
        "warning": "Sample dataset is synthetic. These metrics are for software demonstration only."
    }
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    joblib.dump(CATEGORICAL + NUMERIC, FEATURE_COLUMNS_PATH)
    return metrics, model

def load_model():
    if not MODEL_PATH.exists():
        return None
    return joblib.load(MODEL_PATH)

def predict_success_probability(model, platform, topic, posting_time, duration_seconds,
                                title_keyword_score, hashtag_relevance, historical_engagement_rate):
    row = pd.DataFrame([{
        "platform": platform,
        "topic": topic,
        "posting_time": posting_time,
        "duration_seconds": float(duration_seconds),
        "title_keyword_score": float(title_keyword_score),
        "hashtag_relevance": float(hashtag_relevance),
        "historical_engagement_rate": float(historical_engagement_rate),
    }])
    return float(model.predict_proba(row)[0, 1])
